#!/usr/bin/env python3
"""Release gate regression tests; mutations occur only in temporary clones."""

import hashlib
import json
from pathlib import Path
import runpy
import shutil
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SYNC = runpy.run_path(str(ROOT / "scripts/sync-release.py"))
run = SYNC["run"]
ReleaseError = SYNC["ReleaseError"]


def tree_state(root):
    return {p.relative_to(root).as_posix(): (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns)
            for p in root.rglob("*") if p.is_file() and not p.is_symlink()}


class ReleaseSyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="starfall-release-test-")
        self.root = Path(self.temp.name)
        for name in ("project", "assets", "plugins", "campaign", "artwork", "release", "launch-page", "docs"):
            shutil.copytree(ROOT / name, self.root / name, ignore=shutil.ignore_patterns(".openai", "output", "__pycache__"))
        shutil.copy2(ROOT / "project.gbsproj", self.root / "project.gbsproj")
        shutil.copy2(ROOT / "README.md", self.root / "README.md")
        shutil.copy2(ROOT / "CREDITS.md", self.root / "CREDITS.md")
        manifest = json.loads((self.root / "release/release-manifest.json").read_text())
        self.player_dir = manifest["player"]["directory"]
        self.browser_dir = manifest["browser"]["directory"]
        self.rom_filename = manifest["rom"]["filename"]

    def tearDown(self):
        self.temp.cleanup()

    def mutate(self, name):
        with (self.root / name).open("ab") as handle:
            handle.write(b"\nMUTATED FOR NEGATIVE TEST\n")

    def mutate_manifest(self, change):
        path = self.root / "release/release-manifest.json"
        manifest = json.loads(path.read_text())
        change(manifest)
        path.write_text(json.dumps(manifest))

    def assert_rejected_without_writes(self, message, sync=False):
        before = tree_state(self.root)
        with self.assertRaisesRegex(ReleaseError, message):
            run(self.root, sync=sync)
        self.assertEqual(tree_state(self.root), before)

    def test_checked_in_release_and_idempotent_sync(self):
        before = tree_state(self.root)
        self.assertEqual(run(self.root)["status"], "verified")
        self.assertEqual(run(self.root, sync=True)["changedFiles"], [])
        self.assertEqual(tree_state(self.root), before)

    def test_checked_archive_does_not_require_recompression(self):
        # A different zlib version must not invalidate the exact checked-in ZIP.
        with mock.patch.dict(run.__globals__, {"make_zip": mock.Mock(side_effect=AssertionError("Unexpected recompression"))}):
            self.assertEqual(run(self.root)["status"], "verified")

    def test_supported_publication_states_are_preserved_without_writes(self):
        for publication in ("private-draft", "public-release"):
            with self.subTest(publication=publication):
                self.mutate_manifest(lambda m: m.update(publication=publication))
                before = tree_state(self.root)
                for sync in (False, True):
                    result = run(self.root, sync=sync)
                    self.assertEqual(result["publication"], publication)
                    self.assertEqual(result["changedFiles"], [])
                self.assertEqual(tree_state(self.root), before)

    def test_unknown_publication_state_is_rejected_without_writes(self):
        for publication in ("public", "unlisted", "", None, [], {}):
            with self.subTest(publication=publication):
                self.mutate_manifest(lambda m: m.update(publication=publication))
                for sync in (False, True):
                    self.assert_rejected_without_writes("Publication must be private-draft or public-release", sync=sync)

    def test_public_release_does_not_bypass_player_review(self):
        self.mutate_manifest(lambda m: m.update(publication="public-release"))
        self.mutate(f"{self.player_dir}/{self.rom_filename}")
        self.assert_rejected_without_writes("Unreviewed player input", sync=True)

    def test_mutated_rom_cannot_be_promoted(self):
        self.mutate(f"{self.player_dir}/{self.rom_filename}")
        self.assert_rejected_without_writes("Unreviewed player input", sync=True)

    def test_mutated_browser_rom_cannot_be_promoted(self):
        self.mutate(f"{self.browser_dir}/rom/starfall-salvage.gbc")
        self.assert_rejected_without_writes("Unreviewed browser input", sync=True)

    def test_browser_rom_input_hash_cannot_replace_gameplay_qualification(self):
        name = "rom/starfall-salvage.gbc"
        path = f"{self.browser_dir}/{name}"
        self.mutate(path)
        self.mutate_manifest(lambda m: m["browser"]["files"].update({
            name: hashlib.sha256((self.root / path).read_bytes()).hexdigest()
        }))
        self.assert_rejected_without_writes("Browser ROM identity differs", sync=True)

    def test_browser_runtime_input_hash_cannot_replace_gameplay_qualification(self):
        name = "js/binjgb.wasm"
        path = f"{self.browser_dir}/{name}"
        self.mutate(path)
        self.mutate_manifest(lambda m: m["browser"]["files"].update({
            name: hashlib.sha256((self.root / path).read_bytes()).hexdigest()
        }))
        self.assert_rejected_without_writes("Browser runtime identity differs", sync=True)

    def test_browser_script_input_hash_cannot_replace_gameplay_qualification(self):
        name = "js/script.js"
        path = f"{self.browser_dir}/{name}"
        self.mutate(path)
        self.mutate_manifest(lambda m: m["browser"]["files"].update({
            name: hashlib.sha256((self.root / path).read_bytes()).hexdigest()
        }))
        self.assert_rejected_without_writes("Browser script identity differs", sync=True)

    def test_extra_browser_save_is_rejected_without_copying(self):
        (self.root / self.browser_dir / "progress.sav").write_bytes(b"private save")
        self.assert_rejected_without_writes("Unexpected browser file outside the allowlist", sync=True)

    def test_browser_source_symlink_is_rejected(self):
        target = self.root / self.browser_dir / "js/script.js"
        data = target.read_bytes()
        target.unlink()
        replacement = self.root / "same-script.js"
        replacement.write_bytes(data)
        target.symlink_to(replacement)
        self.assert_rejected_without_writes("Symlinks are not accepted", sync=True)

    def test_stale_browser_copy_is_repaired_from_reviewed_export(self):
        name = "launch-page/dist/play/js/script.js"
        self.mutate(name)
        self.assert_rejected_without_writes("Derived release files are stale")
        result = run(self.root, sync=True)
        self.assertEqual(result["changedFiles"], [name])
        self.assertEqual((self.root / name).read_bytes(), (self.root / self.browser_dir / "js/script.js").read_bytes())
        self.assertEqual(run(self.root)["status"], "verified")

    def test_game_source_change_invalidates_snapshot(self):
        self.mutate("plugins/starfall/engine/src/starfall_encounter.c")
        self.assert_rejected_without_writes("Game source snapshot changed", sync=True)

    def test_new_source_file_is_not_ignored(self):
        (self.root / "assets/unreviewed.txt").write_text("New compiler input")
        self.assert_rejected_without_writes("Game source snapshot changed")

    def test_manual_input_change_requires_review(self):
        self.mutate("campaign/full-length-packaging-stage/generate_manual.py")
        self.assert_rejected_without_writes("Manual inputs", sync=True)

    def test_canonical_screenshot_change_requires_review(self):
        self.mutate("campaign/full-length-packaging-stage/assets/screenshots/escort-flight.png")
        self.assert_rejected_without_writes("Manual inputs", sync=True)

    def test_verification_text_change_requires_reconciliation(self):
        self.mutate("docs/VERIFICATION.md")
        self.assert_rejected_without_writes("Reviewed documentation changed", sync=True)

    def test_unexpected_player_file_is_rejected(self):
        (self.root / self.player_dir / "private-save.sav").write_bytes(b"private")
        self.assert_rejected_without_writes("eight-file allowlist", sync=True)

    def test_unexpected_site_download_is_rejected_without_deleting(self):
        (self.root / "launch-page/dist/downloads/old-release.gbc").write_bytes(b"stale")
        self.assert_rejected_without_writes("Unexpected site file")
        self.assert_rejected_without_writes("Unexpected site file", sync=True)

    def test_changed_campaign_fact_does_not_relabel_release(self):
        self.mutate_manifest(lambda m: m["game"].update(storyMissions=19))
        self.assert_rejected_without_writes("Release fact storyMissions", sync=True)

    def test_changed_timing_claim_requires_review(self):
        self.mutate_manifest(lambda m: m["qualification"].update(guidedClearTime="10:00"))
        self.assert_rejected_without_writes("Reviewed release facts changed", sync=True)

    def test_title_must_use_selected_canonical_capture(self):
        self.mutate_manifest(lambda m: m["site"].update(titleScreenshot="style.css"))
        self.assert_rejected_without_writes("Title screenshot must be selected", sync=True)

    def test_dirty_site_check_is_read_only_then_sync_repairs(self):
        dirty = ["launch-page/dist/assets/escort-flight.png", "launch-page/dist/downloads/INSTRUCTIONS.pdf",
                 "launch-page/dist/index.html", f"{self.player_dir}/SHA256SUMS.txt"]
        for name in dirty:
            self.mutate(name)
        self.assert_rejected_without_writes("Derived release files are stale")
        result = run(self.root, sync=True)
        self.assertEqual(set(result["changedFiles"]), set(dirty))
        self.assertEqual(run(self.root)["status"], "verified")
        for name in dirty:
            self.assertEqual((self.root / name).read_bytes(), (ROOT / name).read_bytes())

    def test_broken_template_link_stops_sync_before_copying(self):
        template = self.root / "launch-page/index.template.html"
        original = template.read_text()
        broken = original.replace('href="style.css', 'href="missing.css')
        self.assertNotEqual(original, broken)
        template.write_text(broken)
        # Pass the editorial guard in this fixture to exercise link validation.
        self.mutate_manifest(lambda m: m["editorialReview"]["files"].update({
            "launch-page/index.template.html": hashlib.sha256(template.read_bytes()).hexdigest()
        }))
        self.mutate("launch-page/dist/downloads/INSTRUCTIONS.pdf")
        self.assert_rejected_without_writes("Missing local site link", sync=True)

    def test_symlink_destination_is_never_followed(self):
        target = self.root / "launch-page/dist/assets/escort-flight.png"
        target.unlink()
        target.symlink_to(self.root / "artwork/box-art.png")
        self.assert_rejected_without_writes("Symlinks are not accepted", sync=True)

    def test_manifest_traversal_is_rejected(self):
        path = self.root / "release/release-manifest.json"
        manifest = json.loads(path.read_text())
        manifest["site"]["directory"] = "../outside"
        path.write_text(json.dumps(manifest))
        self.assert_rejected_without_writes("Unsafe or noncanonical path", sync=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)

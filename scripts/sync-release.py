#!/usr/bin/env python3
"""Check or synchronize reviewed local release copies. Never approves or publishes.

python3 scripts/sync-release.py check  # read-only; also used by CI
python3 scripts/sync-release.py sync   # rebuild derived files after input checks

The manifest is a deliberate review record. This script has no command to accept
new hashes, qualify a build, regenerate a manual, or change publication status.
It validates both private-draft and explicitly recorded public-release inputs;
neither mode publishes files or changes repository or site access.
"""

import argparse
import hashlib
import html
from html.parser import HTMLParser
import io
import json
from pathlib import Path, PurePosixPath
import re
import struct
import sys
import tempfile
from urllib.parse import unquote, urlsplit
import zipfile


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "release/release-manifest.json"


class ReleaseError(Exception):
    pass


def require(condition, message):
    if not condition:
        raise ReleaseError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def path_at(root, name):
    """Accept only plain relative paths, including for not-yet-written outputs."""
    require(isinstance(name, str) and bool(name), "Missing relative file path.")
    p = PurePosixPath(name)
    require(not p.is_absolute() and ".." not in p.parts and str(p) == name,
            f"Unsafe or noncanonical path: {name!r}")
    require("\\" not in name and not any(ord(c) < 32 for c in name), f"Unsafe path: {name!r}")
    target = root
    for part in p.parts:
        target = target / part
        require(not target.is_symlink(), f"Symlinks are not accepted: {name}")
    return target


def read(root, name):
    target = path_at(root, name)
    require(target.is_file(), f"Required file is missing: {name}")
    return target.read_bytes()


def snapshot(root, roots):
    """Digest sorted relative names and file hashes, including added/removed files."""
    entries = {}
    for name in roots:
        target = path_at(root, name)
        require(target.exists(), f"Snapshot input missing: {name}")
        paths = sorted(target.rglob("*")) if target.is_dir() else [target]
        for item in paths:
            rel = item.relative_to(root).as_posix()
            path_at(root, rel)
            if item.is_dir():
                continue
            require(item.is_file(), f"Non-file snapshot input: {rel}")
            entries[rel] = digest(item.read_bytes())
    encoded = "".join(f"{name}\0{sha}\n" for name, sha in sorted(entries.items())).encode()
    return {"sha256": digest(encoded), "fileCount": len(entries)}


def check_snapshot(root, record, label):
    actual = snapshot(root, record["paths"])
    require(actual["sha256"] == record["sha256"] and actual["fileCount"] == record["fileCount"],
            f"{label} changed. Review the current inputs and their evidence; sync cannot approve them.")


def checksums(files):
    return "".join(f"{digest(data)}  {name}\n" for name, data in files.items()).encode("ascii")


def release_facts(manifest):
    facts = {key: manifest[key] for key in ("version", "documentationRevision", "rom", "game", "qualification")}
    facts["manualPages"] = manifest["manualReview"]["pages"]
    return digest(json.dumps(facts, sort_keys=True, separators=(",", ":")).encode())


def check_release_facts(root, manifest):
    missions = [json.loads(read(root, p.relative_to(root).as_posix()))
                for p in sorted((root / "campaign").glob("mission-[0-9][0-9].json"))]
    rooms = [room for mission in missions for room in mission["rooms"]]
    expected = {"storyMissions": len(missions), "storyRooms": len(rooms),
                "zones": len({room["zone"] for room in rooms}),
                "arcadeMaps": len(json.loads(read(root, "campaign/rooms.json")))}
    for key, count in expected.items():
        require(manifest["game"][key] == count, f"Release fact {key} differs from campaign manifests.")
    require(release_facts(manifest) == manifest["editorialReview"]["releaseFactsSha256"],
            "Reviewed release facts changed. Reconcile the site, manual and documentation before accepting new metadata.")


def make_zip(payload, player):
    require(PurePosixPath(player["archiveRoot"]).name == player["archiveRoot"] and player["archiveRoot"] not in (".", ".."),
            "ZIP folder must be a plain release directory name.")
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(payload.items()):
            info = zipfile.ZipInfo(player["archiveRoot"] + "/" + name, date_time=tuple(player["zipTimestamp"]))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    data = buffer.getvalue()
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        require(archive.testzip() is None, "Generated player ZIP failed its CRC check.")
        require(archive.namelist() == [player["archiveRoot"] + "/" + name for name in sorted(payload)],
                "Generated player ZIP has unexpected entries.")
        for name, contents in payload.items():
            require(archive.read(player["archiveRoot"] + "/" + name) == contents,
                    f"Generated ZIP payload mismatch: {name}")
    require(digest(data) == player["archiveSha256"] and len(data) == player["archiveBytes"],
            "Player ZIP differs from the reviewed archive. Review payload and Python/zlib version; no output replaced.")
    return data


def approved_zip(root, payload, player):
    """Reuse the reviewed archive across Python/zlib versions when it is intact."""
    archive_path = path_at(root, player["archive"])
    if archive_path.is_file():
        data = archive_path.read_bytes()
        if digest(data) == player["archiveSha256"] and len(data) == player["archiveBytes"]:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                require(archive.testzip() is None, "Reviewed ZIP failed CRC validation.")
                require(archive.namelist() == [player["archiveRoot"] + "/" + name for name in sorted(payload)],
                        "Reviewed ZIP has an unexpected file list.")
                for name, contents in payload.items():
                    require(archive.read(player["archiveRoot"] + "/" + name) == contents,
                            f"Reviewed ZIP payload mismatch: {name}")
            return data
    return make_zip(payload, player)


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        for key in ("href", "src"):
            if key in attrs:
                self.links.append(attrs[key])


def check_links(root, html_bytes, site_root, outputs):
    parser = Links()
    parser.feed(html_bytes.decode("utf-8"))
    for link in parser.links:
        url = urlsplit(link)
        if url.scheme or url.netloc:
            require(url.scheme in ("http", "https", "mailto"), f"Unexpected link scheme: {link}")
            continue
        if not url.path:
            require(not url.fragment or url.fragment in parser.ids, f"Broken page anchor: {link}")
            continue
        rel = site_root + "/" + unquote(url.path)
        target = path_at(root, rel)
        require(rel in outputs or target.is_file(), f"Missing local site link: {link}")


def prepare(root):
    manifest = json.loads(read(root, MANIFEST))
    require(manifest["schemaVersion"] == 1, "Unsupported release manifest schema.")
    require(manifest.get("publication") in ("private-draft", "public-release"),
            "Publication must be private-draft or public-release.")
    check_snapshot(root, manifest["gameSourceSnapshot"], "Game source snapshot")
    check_snapshot(root, manifest["manualReview"]["inputs"], "Manual inputs; render and visual-review qualification")
    check_release_facts(root, manifest)
    for name, sha in manifest["editorialReview"]["files"].items():
        require(digest(read(root, name)) == sha,
                f"Reviewed documentation changed: {name}. Reconcile instructions, claims and review before updating its hash.")

    player = manifest["player"]
    payload_dir = path_at(root, player["directory"])
    expected_names = set(player["files"]) | {"SHA256SUMS.txt"}
    require(payload_dir.is_dir() and {p.name for p in payload_dir.iterdir()} == expected_names,
            "Player directory must match the exact reviewed eight-file allowlist.")
    payload = {}
    for name, sha in sorted(player["files"].items()):
        require(PurePosixPath(name).name == name, f"Invalid player filename: {name}")
        data = read(root, player["directory"] + "/" + name)
        require(digest(data) == sha, f"Unreviewed player input: {name}; no output replaced.")
        payload[name] = data
    require(len(expected_names) == 8, "Player payload must remain the reviewed eight-file format.")
    rom = manifest["rom"]
    require(digest(payload[rom["filename"]]) == rom["sha256"], "ROM identity differs from release qualification.")
    require(len(payload[rom["filename"]]) == rom["bytes"], "ROM size differs from release qualification.")
    require(digest(payload["INSTRUCTIONS.pdf"]) == manifest["manualReview"]["pdfSha256"],
            "Player PDF differs from the visually reviewed manual.")
    require(manifest["qualification"]["romSha256"] == rom["sha256"], "Gameplay qualification belongs to a different ROM.")
    payload["SHA256SUMS.txt"] = checksums(payload)
    outputs = {player["directory"] + "/SHA256SUMS.txt": payload["SHA256SUMS.txt"]}
    outputs[player["archive"]] = approved_zip(root, payload, player)

    shot_manifest = json.loads(read(root, manifest["screenshots"]["manifest"]))
    require(shot_manifest["version"] == manifest["version"] and shot_manifest["nativeRomSha256"] == rom["sha256"],
            "Screenshot provenance is from another game version or ROM; capture/review the new release.")
    shots = {}
    shot_dir = str(PurePosixPath(manifest["screenshots"]["manifest"]).parent)
    for shot in shot_manifest["screenshots"]:
        name = shot["file"]
        require(PurePosixPath(name).name == name and name not in shots, f"Invalid or duplicate screenshot: {name}")
        data = read(root, shot_dir + "/" + name)
        require(digest(data) == shot["sha256"], f"Screenshot pixels/file changed: {name}")
        require(data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR", f"Invalid PNG: {name}")
        require(struct.unpack(">II", data[16:24]) == (160, 144) and (shot["width"], shot["height"]) == (160, 144),
                f"Screenshot must preserve native 160x144 dimensions: {name}")
        require(shot["nativeRomSha256"] == rom["sha256"] and shot["version"] == manifest["version"] and shot["pixelsAltered"] is False,
                f"Screenshot provenance differs: {name}")
        shots[name] = (shot, data)

    site = manifest["site"]
    outputs[site["directory"] + "/assets/social-preview-v1.2.jpg"] = read(root, "artwork/social-preview-v1.2.jpg")
    require(site["titleScreenshot"] in site["screenshots"] and site["titleScreenshot"] in shots,
            "Title screenshot must be selected from current canonical captures.")
    selected = []
    for name in site["screenshots"]:
        require(name in shots, f"Site screenshot missing from canonical manifest: {name}")
        shot, data = shots[name]
        selected.append({key: shot[key] for key in ("file", "sha256", "width", "height", "pixelsAltered", "frame", "caption")})
        outputs[site["directory"] + "/assets/" + name] = data
    site_shots = {"version": manifest["version"], "source": "Unaltered native PyBoy emulator captures; not physical hardware or browser captures.",
                  "nativeRomSha256": rom["sha256"], "screenshots": selected}
    outputs[site["directory"] + "/assets/screenshots.json"] = (json.dumps(site_shots, indent=2) + "\n").encode()
    downloads = {PurePosixPath(player["archive"]).name: outputs[player["archive"]]}
    downloads.update({name: payload[name] for name in ("INSTRUCTIONS.pdf", "RELEASE-NOTES.txt", "CREDITS.txt")})
    for name, data in downloads.items():
        outputs[site["directory"] + "/downloads/" + name] = data
    outputs[site["directory"] + "/downloads/SHA256SUMS.txt"] = checksums(downloads)

    browser = manifest["browser"]
    browser_names = {"index.html", "gbstudio.json", "css/style.css", "js/README.md", "js/binjgb.js",
                     "js/binjgb.wasm", "js/debugger.js", "js/script.js", "rom/starfall-salvage.gbc"}
    require(set(browser["files"]) == browser_names, "Browser manifest must match the reviewed nine-file allowlist.")
    browser_dir = path_at(root, browser["directory"])
    require(browser_dir.is_dir(), "Reviewed browser directory is missing.")
    found_browser_files = set()
    for entry in browser_dir.rglob("*"):
        name = entry.relative_to(browser_dir).as_posix()
        path_at(root, entry.relative_to(root).as_posix())
        if entry.is_dir():
            require(any(expected.startswith(name + "/") for expected in browser_names),
                    f"Unexpected browser directory outside the allowlist: {name}")
        else:
            require(entry.is_file() and name in browser_names,
                    f"Unexpected browser file outside the allowlist: {name}")
            found_browser_files.add(name)
    require(found_browser_files == browser_names, "Browser directory must match the reviewed nine-file allowlist.")
    browser_payload = {}
    for name, sha in sorted(browser["files"].items()):
        data = read(root, browser["directory"] + "/" + name)
        require(digest(data) == sha, f"Unreviewed browser input: {name}; no output replaced.")
        browser_payload[name] = data
        outputs[site["directory"] + "/play/" + name] = data
    require(digest(browser_payload["rom/starfall-salvage.gbc"]) == manifest["qualification"]["browser"]["romSha256"],
            "Browser ROM identity differs from browser gameplay qualification.")
    require(digest(browser_payload["js/binjgb.wasm"]) == manifest["qualification"]["browser"]["runtimeWasmSha256"],
            "Browser runtime identity differs from browser gameplay qualification.")
    require(digest(browser_payload["js/script.js"]) == manifest["qualification"]["browser"]["runtimeScriptSha256"],
            "Browser script identity differs from browser gameplay qualification.")
    check_links(root, browser_payload["index.html"], site["directory"] + "/play", outputs)

    game = manifest["game"]
    values = {"VERSION": manifest["version"], "ROM_FILENAME": rom["filename"], "ROM_SHA256": rom["sha256"],
              "ROM_BYTES": f'{rom["bytes"]:,}', "MANUAL_PAGES": manifest["manualReview"]["pages"],
              "ZIP_FILENAME": PurePosixPath(player["archive"]).name, "ZIP_SIZE_MB": f'{player["archiveBytes"] / 1_000_000:.2f}',
              "STORY_MISSIONS": game["storyMissions"], "STORY_ROOMS": game["storyRooms"],
              "ZONES": game["zones"], "ZONES_PADDED": f'{game["zones"]:02}', "RIGS": game["rigs"],
              "ARCADE_MAPS": game["arcadeMaps"], "CLEAR_TIME": manifest["qualification"]["guidedClearTime"],
              "NATIVE_EMULATOR": manifest["qualification"]["nativeEmulator"], "TITLE_SCREENSHOT": site["titleScreenshot"]}
    template = read(root, site["template"]).decode("utf-8")
    tokens = set(re.findall(r"{{([A-Z][A-Z0-9_]*)}}", template))
    require(tokens <= values.keys(), "Unknown site template metadata: " + ", ".join(sorted(tokens - values.keys())))
    rendered = re.sub(r"{{([A-Z][A-Z0-9_]*)}}", lambda m: html.escape(str(values[m[1]])), template).encode()
    require(b"{{" not in rendered, "Unresolved site template token.")
    outputs[site["directory"] + "/index.html"] = rendered
    check_links(root, rendered, site["directory"], outputs)
    for name in outputs:
        path_at(root, name)
    allowed_site = {name for name in outputs if name.startswith(site["directory"] + "/")}
    allowed_site.update(site["directory"] + "/" + name for name in ("style.css", "page.js"))
    site_dir = path_at(root, site["directory"])
    for entry in site_dir.rglob("*"):
        name = entry.relative_to(root).as_posix()
        path_at(root, name)
        if entry.is_dir():
            require(any(expected.startswith(name + "/") for expected in allowed_site), f"Unexpected site directory: {name}")
        else:
            require(entry.is_file() and name in allowed_site, f"Unexpected site file: {name}")
    for name in ("style.css", "page.js"):
        read(root, site["directory"] + "/" + name)
    return manifest, outputs


def run(root, sync=False):
    manifest, outputs = prepare(root)
    changed = [name for name, data in outputs.items() if not path_at(root, name).is_file() or path_at(root, name).read_bytes() != data]
    if not sync:
        require(not changed, "Derived release files are stale; run sync after reviewing inputs:\n" + "\n".join(changed))
    elif changed:
        # Stage every output before replacing any file. Recheck inputs immediately
        # before promotion; a copy failure never intentionally removes old files.
        with tempfile.TemporaryDirectory(prefix=".release-sync-", dir=root) as temporary:
            staged = []
            for index, name in enumerate(changed):
                temp = Path(temporary) / str(index)
                temp.write_bytes(outputs[name])
                temp.chmod(0o644)
                staged.append((temp, path_at(root, name)))
            current_manifest, current_outputs = prepare(root)
            require(manifest == current_manifest and outputs == current_outputs,
                    "Inputs changed during sync; no derived files replaced.")
            for temp, destination in staged:
                destination.parent.mkdir(parents=True, exist_ok=True)
                temp.replace(destination)
    return {"status": "synchronized" if sync else "verified", "version": manifest["version"],
            "derivedFiles": len(outputs), "changedFiles": changed, "publication": manifest["publication"],
            "newGameplayOrVisualReviewPerformed": False,
            "remainingPublicReleaseChecks": manifest["qualification"]["pending"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("check", "sync"))
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in ("--check", "--sync"):
        argv[0] = argv[0][2:]
    args = parser.parse_args(argv)
    try:
        print(json.dumps(run(ROOT, sync=args.mode == "sync"), indent=2))
    except (ReleaseError, KeyError, ValueError, OSError) as error:
        parser.exit(1, f"Release check failed: {error}\n")


if __name__ == "__main__":
    main()

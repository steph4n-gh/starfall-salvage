# Working on Starfall Salvage

## Keep the implementation simple

Use the smallest change that satisfies the demonstrated requirement. Reuse or consolidate existing code before adding abstractions, dependencies, configuration, or infrastructure. Do not add extension points for hypothetical future features.

## Keep every release surface in sync

This repository is the canonical editable project. The older local development archive is evidence, not a second release source.

For every game, manual, documentation, screenshot, or site update:

1. Read `docs/RELEASE-WORKFLOW.md` and `release/release-manifest.json`.
2. Edit canonical sources, not generated copies in `launch-page/dist/`.
3. Review all affected player-facing material together: controls, objectives, compatibility, saves, version, filenames, screenshots, quick start, manual, release notes and website.
4. Run `python3 scripts/sync-release.py sync`, then `python3 scripts/sync-release.py check` and `python3 scripts/test-release-sync.py`.
5. Do not bypass a failed review, ROM, source-snapshot, screenshot or manual check by merely replacing expected hashes. Establish the new evidence first and record the deliberate review.

A new ROM does not inherit old playtest results or screenshot provenance. Capture real frames from the exact new ROM and repeat appropriate functional checks. Keep native-emulator, browser, audio, physical-hardware and save-persistence evidence separate.

The manual generator is the content source. Changes to its inputs require regenerated documents and a rendered visual review before promoting the PDF. Never mark a manual reviewed because generation succeeded. AI-generated art may be used as labeled illustration, never as a claimed gameplay screenshot.

The sync command copies and validates artifacts. It does not perform a playthrough, judge fun, review PDF layout, grant a license, or authorize publication.

## Publication and repositories

The user authorized public release of the existing Sites website and GitHub repository on 2026-10-14, superseding the earlier owner-only publication limit. Use the existing site and repository identities, and verify their actual public visibility after publishing. Public source visibility does not assign a new license to original contributions; preserve the licensing scope in `docs/LICENSING.md` and the retained third-party notices. Do not add automatic deployment or upload credentials to GitHub Actions.

Sites identity is in `launch-page/.openai/hosting.json`; reuse it. Stage only the validated site for the Sites source helper. Never send game saves, internal recordings, hardware firmware, license keys or machine-specific diagnostic receipts to either repository.

Use the repository-local `steph4n-gh` Git identity, not a global fallback. Verify `git var GIT_AUTHOR_IDENT` before committing. Do not change global Git settings.

## Cursor Cloud specific instructions

The environment start script already serves `launch-page/dist` at `http://127.0.0.1:8080/`. Use that server for the site and browser edition; do not start a second one on port 8080. Release checks are `python3 scripts/sync-release.py check` and `python3 scripts/test-release-sync.py`. Host mechanics checks are `python3 scripts/test-ui-flow.py`; `cc` is Clang 18 and the test links its UBSan runtime. Manual generation uses the installed Pillow and ReportLab packages with `STARFALL_MANUAL_FONT_DIR=/usr/share/fonts/truetype/dejavu`. GB Studio CLI is not installed here; ROM and web export commands remain in `docs/BUILDING.md`.

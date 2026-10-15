# One release, consistent everywhere

The game repository is the source of truth. The website is a generated distribution of the same reviewed release. A successful sync means the declared files agree; it does not mean new gameplay, hardware, audio, licensing or visual review has passed.

Version 1.2 is published on the public site and [GitHub release](https://github.com/steph4n-gh/starfall-salvage/releases/tag/v1.2). Sites version 6 passed anonymous landing-page, Play 1.2 and exact ZIP/PDF download checks in a fresh Chrome Incognito session; the [delivery receipt](SITES-DRAFT.json) and [hosted receipt](HOSTED-VERIFICATION.json) record the completed publication. Its frozen native/browser artifacts are identified in [VERIFICATION.md](VERIFICATION.md). Native Story passed all 72 rooms at 31:26 and Rank B, including one M17 failed attempt and ordinary retry. All 12 native Arcade sectors passed without retry and banked 22,500; subsequent Continue restored the Story ending. The manifest binds these receipts, eleven reviewed captures, the fourteen-page manual and the player package. Future changes require the evidence and review steps below before accepting new hashes.

## Daily commands

From the repository root, with Python 3:

```sh
python3 scripts/sync-release.py sync
python3 scripts/sync-release.py check
python3 scripts/test-release-sync.py
```

The check command is read-only. Sync validates the canonical inputs before updating derived site copies. It never approves changed review hashes automatically and never uploads or deploys anything. The focused tests use temporary copies and deliberately introduce stale or altered artifacts to verify the checks fail.

GitHub Actions runs the read-only check and failure tests on pushes and pull requests. It has read-only repository permissions and no publishing credentials. A failing check identifies a release mismatch; it does not publish partial work.

## What to edit

| Material | Canonical source | Generated or copied destination |
| --- | --- | --- |
| Game | `project.gbsproj`, `project/`, `assets/`, `plugins/` | Newly built and separately qualified ROM |
| Release identity and reviewed artifacts | `release/release-manifest.json` | Website metadata and validation expectations |
| Manual content | `campaign/full-length-packaging-stage/generate_manual.py` and its inputs | Manual Markdown, HTML and reviewed PDF |
| Gameplay screenshots | Manual `assets/screenshots/SCREENSHOTS.json` and the recorded PNGs beside it | Selected website screenshots and their public provenance |
| Browser player | Frozen official export selected by manifest `browser.directory` and `browser.files`; currently `release/browser-v1.2` | `launch-page/dist/play/` |
| Player instructions and notes | Current `release/player-v*/` text files | Player archive and matching website downloads |
| Website copy | `launch-page/index.template.html`, plus site CSS/JS | `launch-page/dist/index.html` |
| Compatibility and qualification summary | Release manifest, `docs/VERIFICATION.md`, and reviewed player-facing copy | Site and release summaries with the same evidence limits |

Do not edit a screenshot hash to disguise a different frame. Do not change the version field alone and call an old screenshot current. Keep old release evidence identified by its original version and ROM hash.

## When game code or assets change

1. Build a new ROM from the intended source and inspect its header/hash. A changed source snapshot invalidates the old release check even if the old ROM is still present.
2. Play the affected behavior and required release route on that exact ROM. Keep receipts for failures as well as successes. Record completed coverage and pending coverage explicitly; no 1.2 build inherits the old 1.1 native 35:27 or browser 42:41 clear result. Keep source/host tests separate from emulator play, and register/APU traces separate from actual audio listening.
3. Capture genuine screenshots for the new ROM. Review the screenshots and their captions; add exact ROM/frame/file identities to the canonical manifest. Old screenshots may be retained only when clearly labeled as historical, not relabeled as new captures.
4. Update controls, objectives, unlocks, compatibility, save behavior, timing statements and version references wherever the change affects them. Check the manual, quick start, release notes, verification summary and website together.
5. Regenerate and visually review the manual if its inputs changed. Record the reviewed PDF, current manual-input snapshot and page count. Generation alone is insufficient.
6. Deliberately update the release manifest to bind the new source snapshot, qualified ROM, reviewed manual, screenshots and editorial review. Review that manifest diff alongside the actual evidence. Preserve historical receipts under their original version/hash before replacing a current receipt; add the new portable receipts to editorial review. Never replace a pending result with a pass merely to make synchronization succeed.
7. Sync, check and run the failure tests. Inspect the generated site and download contents. Commit the coherent release to the game repository.

The manifest source fingerprint identifies its reviewed portable snapshot, not every later working-tree edit. The existing [clean-clone comparison](CLEAN-BUILD.json) passed for 1.1 native/browser exports on macOS arm64. Only GB Studio's built-in save signature and global checksum varied; all other compared ROM bytes and all eight non-ROM browser files matched the frozen counterparts. Timestamp and inode metadata make ordinary builds non-identical. Two deeper-path builds failed at linking, while a fresh short `/tmp` directory passed; follow the [build instructions](BUILDING.md). A new 1.2 clean-clone comparison remains pending, and signature offsets must be read from the new symbol map. Neither a fingerprint nor a build comparison establishes gameplay, cross-machine reproducibility or save persistence.

## When only documentation or the site changes

Keep the ROM and its qualification unchanged. Edit the canonical text/template. If manual inputs changed, regenerate and review the PDF before updating its review record. Review any changed instructions or claims, then sync and check all copied downloads. A wording correction does not automatically require another full gameplay clear, but a new gameplay claim requires supporting evidence.

The website uses release metadata for repeated fields such as version, native ROM identity and manual page count. Prose still needs editorial review: a checksum cannot decide whether an explanation is accurate or a game is enjoyable.

The Play in Browser button uses the exact reviewed nine-file export. Keep the ROM, runtime and retained license notice together; the browser allowlist excludes saves and private preview metadata. Recheck initial load, controls and checkpoint recovery on the site origin after changing delivery.

Keep native and browser qualification separate. The [native 1.2 receipt](NATIVE-VERIFICATION.json) records Story at 31:26, Rank B and a complete 12-sector Arcade cycle with 22,500 banked; the earlier browser 42:41 and native 35:27 results belong to 1.1. These are successful-room timers, not human wall time. Current [1.2 browser evidence](BROWSER-VERIFICATION.json) covers targeted Story/menu/Arcade and save checks; it must not be described as a complete campaign. Record ordinary reload, fresh-emulator SRAM Continue and same-session Title → Continue separately. The current native harness does not qualify cold-boot SRAM persistence. A same-origin 1.1-to-1.2 checkpoint upgrade does not prove every old save, cartridge or host. Preserve final-host, hardware, audio and human-play limits in all summaries.

The later [owner hardware report](HARDWARE-REPORT-v1.2.json) confirms 1.2 play on a Chromatic with an SD flash cartridge. Keep this confirmation separate from the frozen emulator receipts and from independent hardware checks. Associate the current release hash only as the referenced release: the report does not identify an exact cartridge model or establish a physical readback hash. Do not expand it into a full power-off-save, audio-listening, exhaustive-play or additional-device claim. A later owner report can update compatibility copy without rewriting the scope of the original emulator runs.

## Updating the Sites version

1. Pass all local checks and commit the game repository changes.
2. Use the Sites skill and the existing `project_id` in `launch-page/.openai/hosting.json`. Do not create a second site.
3. Copy the validated site files to the separate Sites checkout, preserving its `.git` and `.openai/hosting.json`. Check that its `dist/` bytes equal the canonical generated site. Never copy the entire game repository into the site.
4. Use the supported Sites source helper to push and package that exact site source. Keep short-lived credentials in session memory and pass them through stdin, never files or command arguments.
5. Save the archive-backed version and record its source commit and saved version. A reserved URL is not evidence of a live website.
6. Deploy the reviewed update to the existing public site. Verify the actual audience and anonymous page/download access after each deployment; update the delivery record with the tested version and artifacts. Keep historical owner-only checks labeled by their original scope. Update compatibility or persistence claims only after the hosted environment is tested. Browser saves remain local to each browser and site address; they do not sync across devices.

The GitHub repository and the Sites source repository serve different purposes. GitHub retains the editable game and release workflow. Sites receives only the matching web distribution. Automatic deployment remains disabled; a Git push or green consistency check is not a publication receipt. Public source visibility does not assign a new license to original contributions; preserve [licensing scope](LICENSING.md) and all retained component notices.

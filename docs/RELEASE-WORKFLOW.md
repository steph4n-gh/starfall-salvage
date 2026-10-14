# One release, consistent everywhere

The game repository is the source of truth. The website is a generated distribution of the same reviewed release. A successful sync means the declared files agree; it does not mean new gameplay, hardware, audio, licensing or visual review has passed.

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
| Browser player | Frozen official export in `release/browser-v1.1`, bound by manifest `browser.files` and browser qualification hashes | `launch-page/dist/play/` |
| Player instructions and notes | Current `release/player-v*/` text files | Player archive and matching website downloads |
| Website copy | `launch-page/index.template.html`, plus site CSS/JS | `launch-page/dist/index.html` |
| Compatibility and qualification summary | Release manifest, `docs/VERIFICATION.md`, and reviewed player-facing copy | Site and release summaries with the same evidence limits |

Do not edit a screenshot hash to disguise a different frame. Do not change the version field alone and call an old screenshot current. Keep old release evidence identified by its original version and ROM hash.

## When game code or assets change

1. Build a new ROM from the intended source and inspect its header/hash. A changed source snapshot invalidates the old release check even if the old ROM is still present.
2. Play the affected behavior and required release route on that exact ROM. Keep receipts for failures as well as successes. A new build does not inherit the old 35:27 clear result.
3. Capture genuine screenshots for the new ROM. Review the screenshots and their captions; add exact ROM/frame/file identities to the canonical manifest. Old screenshots may be retained only when clearly labeled as historical, not relabeled as new captures.
4. Update controls, objectives, unlocks, compatibility, save behavior, timing statements and version references wherever the change affects them. Check the manual, quick start, release notes, verification summary and website together.
5. Regenerate and visually review the manual if its inputs changed. Record the reviewed PDF, current manual-input snapshot and page count. Generation alone is insufficient.
6. Deliberately update the release manifest to bind the new source snapshot, qualified ROM, reviewed manual, screenshots and editorial review. Review that manifest diff alongside the actual evidence.
7. Sync, check and run the failure tests. Inspect the generated site and download contents. Commit the coherent release to the private repository.

The current source fingerprint identifies the reviewed portable snapshot. A [clean-clone build comparison](CLEAN-BUILD.json) passed for native and browser exports on macOS arm64. Only GB Studio's built-in save signature and global checksum varied; all other ROM bytes and all eight non-ROM browser files matched the frozen counterparts. Timestamp and inode metadata make ordinary builds non-identical. Two deeper-path builds failed at linking, while a fresh short `/tmp` directory passed; follow the [build instructions](BUILDING.md) for isolated short temporary paths. Neither the fingerprint nor this local comparison establishes cross-machine reproducibility, save persistence or a complete browser playthrough.

## When only documentation or the site changes

Keep the ROM and its qualification unchanged. Edit the canonical text/template. If manual inputs changed, regenerate and review the PDF before updating its review record. Review any changed instructions or claims, then sync and check all copied downloads. A wording correction does not automatically require another full gameplay clear, but a new gameplay claim requires supporting evidence.

The website uses release metadata for repeated fields such as version, native ROM identity and manual page count. Prose still needs editorial review: a checksum cannot decide whether an explanation is accurate or a game is enjoyable.

The Play in Browser button uses the exact reviewed nine-file export. Keep the ROM, runtime and retained license notice together; the browser allowlist excludes saves and private preview metadata. Recheck initial load, controls and checkpoint recovery on the site origin after changing delivery.

Keep native and browser qualification separate. [The browser receipt](BROWSER-VERIFICATION.json) binds its 42:41 campaign result to the exact tested browser ROM/runtime; the native 35:27 result belongs to its own release ROM. A wrapper snapshot recovery and a fresh-emulator SRAM Continue test establish different save behaviors. Update their outcomes separately and retain final-host, hardware and human-play limits.

## Updating the Sites version

1. Pass all local checks and commit the game repository changes.
2. Use the Sites skill and the existing `project_id` in `launch-page/.openai/hosting.json`. Do not create a second site.
3. Copy the validated site files to the separate Sites checkout, preserving its `.git` and `.openai/hosting.json`. Check that its `dist/` bytes equal the canonical generated site. Never copy the entire game repository into the site.
4. Use the supported Sites source helper to push and package that exact site source. Keep short-lived credentials in session memory and pass them through stdin, never files or command arguments.
5. Save the archive-backed version without deployment while the current no-publishing instruction remains in force. Record its source commit and saved version. A reserved URL is not evidence of a live website.
6. Deploy only after explicit publication authorization; preserve the intended audience and verify the resulting deployment. Update compatibility or persistence claims only after the final hosted environment is tested.

The GitHub repository and the Sites source repository serve different purposes. GitHub retains the editable game and release workflow. Sites receives only the matching web distribution. Neither a Git push nor a green consistency check authorizes a deployment.

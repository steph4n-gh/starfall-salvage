# Starfall Salvage 1.2 launch page

Canonical website copy, the fourteen-page manual and exact-ROM screenshots are reviewed for version 1.2. The private custom domain is [starfall.steph4n.dev](https://starfall.steph4n.dev). The deployed version remains the one identified in the hosting receipt until the new reviewed payload is deployed. Preserve owner-only hosting access. The private-draft banner and `noindex, nofollow` are not access control.

Edit `index.template.html` for page copy. Repeated release metadata comes from `../release/release-manifest.json`. After the final evidence is accepted, run `python3 scripts/sync-release.py sync` from the repository root, followed by the checks/tests in [the release workflow](../docs/RELEASE-WORKFLOW.md). Do not edit generated HTML or copied downloads/screenshots directly.

The generated `dist/` folder is self-contained. From this directory, serve it locally:

```sh
python3 -m http.server 8080 --bind 127.0.0.1 --directory dist
```

Open the local URL printed by the server. The static landing page needs no dependency installation, analytics, remote fonts or remotely loaded scripts. Its JavaScript enlarges screenshots in an accessible dialog. The separate `play/` route contains the frozen Binjgb JavaScript/WebAssembly player and ROM. Downloads are local files under `dist/downloads/`.

## Contents and evidence

- One native player ZIP with the reviewed manual, quick start, release notes, credits and checksums. The manual and canonical player text are reviewed; final manifest/package synchronization is the next promotion step.
- Eight site images from the exact 1.2 native ROM: seven displayed frames and one additional Flight Deck asset. All eleven canonical captures, including the manual-only frames, have been visually reviewed and checked against recorded PNG/RGBA hashes. Sync copies the selected frames and portable provenance into `dist/assets/screenshots.json`.
- After manifest promotion, browser files will be copied from the frozen `../release/browser-v1.2` payload declared there. Keep native and browser ROM identities separate. Browser files remain outside the native player ZIP; do not embed ephemeral preview URLs or private saves.
- The exact native 1.2 ROM completed 18 Story missions, 72 rooms, 18 guardians and seven rescues; the ending showed 31:26, Rank B. One M17 escort failure recovered through ordinary Retry. The timer excludes menus, pauses and failed attempts and is not a first-time human duration. All 12 native Arcade sectors passed without retry, banked 22,500, and retained the completed Story ending through same-session Title/Continue.
- The exact browser 1.2 ROM `19d4488b34ee87d329aa72400e8e7cdb5322ecd07b3759add818809f36f92eeb` completed targeted M01/M02 gameplay, all eight rooms, with guardian failure and checkpoint Continue recovery. One Arcade sector was cleared after retry; Change Rig then Back kept the rig, and Bank Haul saved 300.
- Ordinary reload retained BEST 00300 and Continue restored M03 Bay 1, Debris Halo, with H3. Earlier reloads checked 1.1-to-1.2 continuation, earned M01 route choice and completed M02. Direct launch and Pause/Retry were also exercised. [The browser receipt](../docs/BROWSER-VERIFICATION.json) records the exact runtime/origin and bounded coverage.
- These browser checks are not a full 72-room campaign, a complete 12-map Arcade cycle or a browser clear-time measurement. Same-session SRAM Continue, persisted page reload, native cold-start and full browser-process shutdown are different checks. Browser progress stays in its browser and site address and does not sync across devices.
- References: [GB Studio web build](https://www.gbstudio.dev/docs/build/) and [SameBoy capabilities](https://sameboy.github.io/features/).

## Before promotion and public release

The fourteen-page rendered manual, exact native Story/Arcade receipts and eleven-frame capture manifest have been checked. Finish release-manifest/package synchronization, then verify the exact delivered files on the private host. The current native harness does not qualify cold-start save persistence. Actual speaker/headphone listening, physical 1.2 handheld/cartridge behavior, power-off saves, full browser-process shutdown and other browser/origin combinations remain separate checks. The owner's informal successful 1.1 Chromatic report stays scoped to 1.1. Do not describe generated audio or a waveform check as heard-audio approval.

Recheck delivery and persistence on the final private domain after deploying the exact reviewed 1.2 files. Resolve original-work licensing and retained-asset provenance before any public release. Run uncoached player tests and choose a support channel before launch. No typical first-time completion duration is advertised.

Sites identity is recorded in `.openai/hosting.json`; reuse that project. GitHub Actions checks consistency only. Use the Sites skill to package the validated site, save a version and perform the authorized owner-only deployment. Preserve the private domain and owner-only access. Removing the draft banner/noindex or publishing publicly requires separate authorization.

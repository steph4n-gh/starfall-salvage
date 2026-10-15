# Starfall Salvage 1.2 launch page

Canonical website copy, the fourteen-page manual and exact-ROM screenshots are reviewed for version 1.2. Sites version 6 is publicly deployed at [starfall.steph4n.dev](https://starfall.steph4n.dev), and the [GitHub v1.2 release](https://github.com/steph4n-gh/starfall-salvage/releases/tag/v1.2) is published in the public repository. A fresh Chrome Incognito session verified anonymous landing-page, Play 1.2 and ZIP/PDF access. The [hosted receipt](../docs/HOSTED-VERIFICATION.json) records the tested delivery; the [earlier owner-only version 5 check](../docs/HOSTED-VERIFICATION-v1.2-private.json) remains historical.

Edit `index.template.html` for page copy. Repeated release metadata comes from `../release/release-manifest.json`. After the final evidence is accepted, run `python3 scripts/sync-release.py sync` from the repository root, followed by the checks/tests in [the release workflow](../docs/RELEASE-WORKFLOW.md). Do not edit generated HTML or copied downloads/screenshots directly.

The generated `dist/` folder is self-contained. From this directory, serve it locally:

```sh
python3 -m http.server 8080 --bind 127.0.0.1 --directory dist
```

Open the local URL printed by the server. The static landing page needs no dependency installation, analytics, remote fonts or remotely loaded scripts. Its JavaScript enlarges screenshots in an accessible dialog. The separate `play/` route contains the frozen Binjgb JavaScript/WebAssembly player and ROM. Downloads are local files under `dist/downloads/`.

## Contents and evidence

- One native player ZIP with the reviewed manual, quick start, release notes, credits and checksums. The release manifest binds the synchronized package. The live ZIP and PDF downloads match the canonical files byte for byte; all eight ZIP entries passed the archive CRC check.
- Eight site images from the exact 1.2 native ROM: seven displayed frames and one additional Flight Deck asset. All eleven canonical captures, including the manual-only frames, have been visually reviewed and checked against recorded PNG/RGBA hashes. Sync copies the selected frames and portable provenance into `dist/assets/screenshots.json`.
- Browser files are copied unchanged from the frozen `../release/browser-v1.2` payload selected by the release manifest. Keep native and browser ROM identities separate. Browser files remain outside the native player ZIP; do not embed ephemeral preview URLs or private saves.
- The exact native 1.2 ROM completed 18 Story missions, 72 rooms, 18 guardians and seven rescues; the ending showed 31:26, Rank B. One M17 escort failure recovered through ordinary Retry. The timer excludes menus, pauses and failed attempts and is not a first-time human duration. All 12 native Arcade sectors passed without retry, banked 22,500, and retained the completed Story ending through same-session Title/Continue.
- The exact browser 1.2 ROM `19d4488b34ee87d329aa72400e8e7cdb5322ecd07b3759add818809f36f92eeb` completed targeted M01/M02 gameplay, all eight rooms, with guardian failure and checkpoint Continue recovery. One Arcade sector was cleared after retry; Change Rig then Back kept the rig, and Bank Haul saved 300.
- Ordinary reload retained BEST 00300 and Continue restored M03 Bay 1, Debris Halo, with H3. Earlier reloads checked 1.1-to-1.2 continuation, earned M01 route choice and completed M02. Direct launch and Pause/Retry were also exercised. [The browser receipt](../docs/BROWSER-VERIFICATION.json) records the exact runtime/origin and bounded coverage.
- These browser checks are not a full 72-room campaign, a complete 12-map Arcade cycle or a browser clear-time measurement. Same-session SRAM Continue, persisted page reload, native cold-start and full browser-process shutdown are different checks. Browser progress stays in its browser and site address and does not sync across devices.
- References: [GB Studio web build](https://www.gbstudio.dev/docs/build/) and [SameBoy capabilities](https://sameboy.github.io/features/).

## Delivery and remaining checks

The fourteen-page rendered manual, exact native Story/Arcade receipts and eleven-frame capture manifest have been checked and synchronized. Anonymous version 6 downloads matched the canonical player ZIP and manual PDF, and all eight ZIP entries passed CRC. The [hosted receipt](../docs/HOSTED-VERIFICATION.json) records public landing-page and Play access plus those file identities. The earlier owner-only custom-origin check separately confirmed preservation of the existing 1.1 M01 Bay 1 checkpoint with H3, movement, brake, pulse, pause and ordinary reload/Continue. This adds no full-browser campaign or Arcade-cycle qualification.

The owner confirmed 1.2 play on a physical Chromatic through an SD flash cartridge; the [hardware report](../docs/HARDWARE-REPORT-v1.2.json) preserves the exact statement. The cartridge model and physical ROM readback were not independently identified. Additional hardware combinations, full power-off saves, speaker/headphone listening, full browser-process shutdown and other browser/origin combinations remain separate checks. The current native harness does not qualify cold-start save persistence. Do not describe generated audio or a waveform check as heard-audio approval. Recheck delivery and persistence after future deployments. Original-contribution reuse terms remain described in [licensing status](../docs/LICENSING.md). [Third-party notices](../docs/THIRD-PARTY-NOTICES.md) records the six verified starter files and the applicable component notices. Continue uncoached player tests and collect bug reports and feedback through [GitHub Issues](https://github.com/steph4n-gh/starfall-salvage/issues). No typical first-time completion duration is advertised.

Sites identity is recorded in `.openai/hosting.json`; reuse that project and the existing custom domain for future updates. GitHub Actions checks consistency only. Use the Sites skill to package the validated site, save a version and deploy it. Recheck the resulting audience and anonymous page/download access after each deployment, and retain the new delivery receipt.

# Before public release

This is a private review repository. The site uses authorized owner-only access. No public site, repository, release or player download has been launched. The current release manifest selects the reviewed 1.2 source, ROMs, screenshots, manual and player package.

## Current version 1.2 release

- Native and browser release artifacts are frozen at the hashes in [VERIFICATION.md](VERIFICATION.md). The [native receipt](NATIVE-VERIFICATION.json) accepts all 18 Story missions/72 rooms, 18 guardians and seven crew rescues: **31:26, Rank B**, with one M17 pilot-hull failure followed by ordinary retry. All 12 Arcade sectors then cleared with zero failed Arcade attempts; Bank Haul saved **22,500**, and same-session Continue restored the Story ending afterward. The Story timer counts successful-room gameplay, not first-time human duration.
- The targeted browser check completed M01/M02, all eight rooms, with a failed guardian attempt followed by checkpoint Continue and a full-hull victory. The same-origin 1.1-to-1.2 checkpoint upgrade and ordinary-reload route/completed-mission recovery passed. Optional rigs, held-input direct launch, Pause, Retry and exits were exercised. Browser Arcade S01 passed after an initial failure and retry; Back from Change Rig left the rig unchanged, banking saved 300, and ordinary reload retained BEST 00300 plus the Story M03 checkpoint. These checks do not establish a full 1.2 browser campaign or complete Arcade cycle.
- Source/host checks cover the revised menu flow, legacy checkpoint stages and unchanged gameplay audio traces. Actual title/six-zone music and effect listening remains unverified.
- Updated player text, eleven exact-native-ROM captures and the fourteen-page manual have been reviewed. All nine embedded gameplay images match their canonical capture pixels. The player archive and generated site are bound by the release manifest.
- The manifest, sync/check commands, failure tests and check-only CI provide the existing consistency workflow. The earlier reviewed 1.1 artifacts and receipts remain historical; they cannot be relabeled as 1.2 evidence.

## Private delivery

The accepted, synchronized 1.2 distribution is deployed as Sites version 5 at the existing custom origin. The [hosted receipt](HOSTED-VERIFICATION.json) records movement, brake, pulse and pause checks; preservation of the existing 1.1 M01 Bay 1 H3 checkpoint; and ordinary reload/Continue. The live ZIP and PDF downloads match their canonical bytes, and all eight ZIP entries passed the archive CRC check. Owner-only access was reverified with one owner, no groups and no external visitors. This delivery check does not expand the targeted browser gameplay coverage above.

Keep the earlier binaries and the [historical 1.1 hosted receipt](HOSTED-VERIFICATION-v1.1.json) unchanged. Future deployments require their own delivery and persistence checks at the intended origin. A new source snapshot or passing consistency check does not inherit gameplay results from another artifact.

## Gates before broader claims or public release

1. **Blind player tests:** watch 3–5 new players without coaching. Track first dock, brake/pulse/menu understanding, crew proximity, guardian windows, difficulty spikes and reasons for stopping. Measure real human completion times before advertising them.
2. **Hardware, audio and saves:** qualify the exact 1.2 Chromatic/cartridge combination, crowded scenes, display readability, title/zone/effect balance on speakers and headphones, and save → complete power off → Continue. The owner's informal successful 1.1 Chromatic report is historical and does not qualify these 1.2 behaviors. Native cold-boot SRAM testing is unsupported by the current harness; same-session Continue is a narrower check.
3. **Browser scope:** qualify additional supported browsers and the eventual public host. Full browser-process termination, storage eviction, cross-origin behavior and cross-device persistence are not established. Browser saves do not sync across devices. Complete a 1.2 browser campaign or full Arcade cycle before claiming those results; the accepted targeted checks may be described with their limits.
4. **Licensing and asset provenance:** choose the original work's terms and confirm retained resources' origins/notices. See [licensing status](LICENSING.md). Private preparation assigns no new terms.
5. **Launch/support:** select a feedback channel, prepare a genuine gameplay clip, recheck all links and publish only claims supported by completed tests. The native 1.2 guided Story clear is 31:26. The older native 35:27 and browser 42:41 results belong to 1.1. None of these successful-room timers measures typical-player duration.
6. **Build qualification:** the [clean-clone comparison](CLEAN-BUILD.json) covers 1.1 on the recorded macOS arm64 toolchain. Repeat the appropriate comparison for 1.2 and qualify additional host/toolchain combinations before claiming support. Preserve the documented signature nondeterminism and the short-temporary-path workaround.
7. **Explicit public-release decision:** keep GitHub private, GitHub Pages off and the Sites website owner-only until public release is authorized. Remove draft banners/noindex only in that release step.

Documentation-only changes do not create a newly qualified game build. Keep native gameplay, browser gameplay, source/APU traces, heard audio, physical hardware, persistence and human feedback as separately supported claims.

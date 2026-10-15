# Version 1.2 verification status

Version 1.2 is the current private review release. The frozen native ROM completed all 18 Story missions/72 rooms and one full 12-sector Arcade cycle. Eleven native captures and all fourteen rendered manual pages have been reviewed. The release manifest binds the exact source, player package, browser export and review records. Results below belong to the identified artifacts.

| Version 1.2 artifact | SHA-256 |
| --- | --- |
| Native `Starfall-Salvage-1.2.gbc` | `da88897984d4ead183a8e14aa9c7dcea91592445e27a9cd62517cba432f83a78` |
| Browser `rom/starfall-salvage.gbc` | `19d4488b34ee87d329aa72400e8e7cdb5322ecd07b3759add818809f36f92eeb` |

The inspected native image is 1 MiB, GBC-only, and uses header cartridge type `0x1E` (MBC5 + rumble + RAM + battery), with 32 KiB save RAM. Its build exited successfully and its header checksum is valid. Cartridge and emulator support must match this actual image; a physically fitting cartridge is not sufficient evidence of compatibility.

## Completed 1.2 checks

- **Native Story:** all 18 missions and 72 distinct rooms, 18 guardians and seven crew rescues in PyBoy 2.7.0. The ending at frame 126152 showed **31:26, Rank B**. One M17 escort attempt failed when the pilot's hull depleted; ordinary in-game retry then rescued the crew with two crew HP. The [native receipt](NATIVE-VERIFICATION.json) retains all 72 room-clear records and the source receipt's identity. This was a guided ordinary-input run with frame inspection and read-only diagnostics, without emulator save-state loading or direct progress writes. The displayed timer counts successful-room gameplay and excludes menus, pauses and failed attempts; it is not first-time human duration or a difficulty measurement.
- **Native pause and Continue:** same-session Title → Continue checks covered the launch, route-choice, result, mission-complete, flight-deck and ending stages. Continue at frame 126324 restored the same ending. At the flight deck, Continue returned to the last completed mission rather than retaining an unlaunched mission selection. Pause froze the sampled gameplay state for 120 emulator frames.
- **Native Arcade:** all 12 distinct sectors cleared with zero failed Arcade attempts, followed by an ordinary Bank Haul action that saved **22,500**, also shown as the best banked score. Title → Continue after banking restored STARFALL SAVED, **31:26, Rank B**, at frame 136625. The [native receipt](NATIVE-VERIFICATION.json) preserves all 12 clear records, the bank result and this same-session Story recovery. A wrong-order relay check also left progress at zero as expected. Later loops and every rig combination are outside this run's scope; Story's separate M17 failure remains part of the record.
- **Targeted browser Story play:** M01 and M02, all eight rooms, using ordinary controls. The first M02 guardian attempt failed; checkpoint Continue restored the room and the next attempt completed with full hull (H3). This establishes two missions, not a complete 18-mission browser campaign or a browser clear time.
- **Browser menu and input regression:** optional rig selection at M03, direct launch with A and Right held, Pause objective/help, Retry and exit choices were exercised.
- **Browser Arcade:** S01 initially failed during ordinary play; a fresh retry cleared S01 with full hull (H3). Back from optional Change Rig left the rig unchanged. Bank Haul saved 300, and an ordinary reload showed BEST 00300 plus CONTINUE M03; Continue restored M03 Bay 1, Debris Halo, with H3. This covers one sector and the bank/save transitions, not the complete 12-map browser cycle.
- **Browser save upgrade:** a real checkpoint earned with the frozen 1.1 browser ROM was restored by 1.2 after replacing only the ROM at the same local browser origin. The eight non-ROM export files were unchanged. Normal page reload and Continue also recovered the earned route-choice and completed-mission stages. No browser-storage or emulator-memory injection was used. This covers the tested checkpoints and origin, not every save or host.
- **Host checks of production C:** 155 flow assertions, 57 preservation checks and three negative controls passed with undefined-behavior and bounds sanitizers. Coverage includes launch edges, held movement/brake/pause, both Story route orders, optional Arcade rigs, banking, reward replay protection and six valid legacy checkpoint stages. Rendering, room transitions, geometry and audio are mocked in this harness; it complements runtime play.
- **Audio source/APU-register checks:** the six-zone gameplay sequence, all nine cues and periodic pauses produced byte-identical register, waveform and sequencer traces against the prior source over 72,000 updates. The new title score completed two loops from each zone with transition and cue-priority checks. These are source and register tests; no speaker or headphone listening result is claimed.

The [browser receipt](BROWSER-VERIFICATION.json) records the bounded browser outcomes and identifies its [24 selected captures](browser-evidence-v1.2/SCREENSHOTS.json). Native save checks use same-session Title → Continue reading the committed checkpoint. The current native harness does not support a qualified cold-boot SRAM test. Continue is not a promise to restore a mid-room position.

## Release artifacts and private delivery

The [manual review](MANUAL-REVIEW.json) records all fourteen rendered pages and nine embedded native images whose pixels match the canonical captures. The [release manifest](../release/release-manifest.json) identifies the reviewed eight-file native player package and nine-file official browser export. Synchronization checks compare exact source, document, screenshot, archive and website identities; they do not add gameplay qualification.

The private 1.2 deployment still requires its hosted delivery check. The [historical hosted receipt](HOSTED-VERIFICATION-v1.1.json) describes 1.1 and does not establish 1.2 behavior. Detailed local recordings stay private; portable summaries retain artifact identities and evidence limits without copying saves or machine-specific diagnostics.

## Historical 1.1 evidence

These results remain tied to their original binaries. They are not 1.2 results.

| Version 1.1 artifact | SHA-256 |
| --- | --- |
| Native `Starfall-Salvage-1.1.gbc` | `105e410008ceb8dd2d6c83aebb033972b8cfcfeb41a714fcc7f260966ba193db` |
| Browser ROM used for the full campaign | `3d47ad53fc3fd75e80092df7f7ac1f45f6a6275d89d5c67794d862aecfda29da` |
| Earlier browser export, preview observation only | `cc5a3714c27f32f2a17d1e9a2cef2f465187212d4315c668ff41ea0b277ba177` |

- **Native:** all 18 missions and 72 rooms, 18 guardians with three separate CORE OPEN hits each, seven crew routes, all four rigs and both middle-route orders. The ending showed 35:27 and Rank B. Pause freeze, mid-campaign Continue and Title → Continue restoring the ending passed. A separate controls run completed the 12-room Arcade cycle plus sector 13 and banked 25,500, with rig choices, retry, loss and menu/save transitions.
- **Browser:** all 18 missions, 72 rooms, 18 guardians and seven escorts; the ending showed STARFALL SAVED, 42:41 and Rank B. This run used standard pulse initially and Wide Coil later, with both middle-route orders. It did not repeat the native all-four-rig or complete Arcade qualification. The [historical browser receipt](BROWSER-VERIFICATION-v1.1.json) identifies the ROM and official Binjgb runtime, including WASM SHA-256 `69aa17be45fec5fde585af4f39ed850b5d64107ec094a6482f316fef2fe7c945`.
- **Browser persistence:** Title → Continue and the preview's Restart game → Continue restored the ending. The inspected restart wrapper flushed external RAM and suppressed automatic emulator-state recovery, so that check exercised browser-stored SRAM in a fresh emulator. Ordinary page reload separately recovered an emulator snapshot. The [historical hosted check](HOSTED-VERIFICATION-v1.1.json) records a narrower launch/control/reload test on the private site.
- **Build and manual:** a fresh clone of commit `9c5c727ad55454be5737c3f066d873e970188970` compiled native and browser exports on macOS arm64 with GB Studio CLI 4.3.2, engine 4.3.0-e1 and GBDK 4.5.0. Only the built-in save-signature and global-checksum fields differed from the corresponding frozen images; all eight non-ROM export files matched. Two deeper-path linker failures and a successful short `/tmp` workaround are retained in the [clean-build receipt](CLEAN-BUILD.json). The earlier manual and its nine gameplay captures were reviewed for the native 1.1 image.
- **Owner report:** the owner reported successful 1.1 Chromatic play on October 14. This informal report does not establish 1.2 hardware qualification, independently reproduced cartridge behavior, complete power-cycle persistence or audio listening.

The native 1.1 campaign used ordinary controls without injecting progress, positions or saves. The browser campaign included pauses, failed attempts and retries; once, after an accidental mission relaunch, the visible Saved states menu restored an already-earned M03 completion and granted no new progress. Both clear timers count successful-room gameplay and exclude menus, pauses and failed attempts. Neither measures first-time human play duration or difficulty.

## Remaining independent checks

- Uncoached human feedback on onboarding, clarity, challenge, pacing and enjoyment.
- Actual title and six-zone audio listening on speakers and headphones, including music/effect balance and transitions.
- Physical 1.2 play on each precise handheld/cartridge configuration being recommended, followed by save → full power-off → Continue.
- Native emulator cold-start saves; full browser-process termination, storage eviction, cross-origin behavior and other browser/runtime combinations. Browser saves are local to the browser and site address and do not sync across devices.
- Final public-host qualification if public delivery is later authorized.
- Fresh-clone 1.2 and cross-machine build comparisons. The existing [clean-build receipt](CLEAN-BUILD.json) belongs to 1.1 on the recorded macOS arm64 toolchain.

Every route combination, later indefinite Arcade loops and all optional interaction boundaries have not been exhausted. These software checks do not load hardware firmware or write an SD card.

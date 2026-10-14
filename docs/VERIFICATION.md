# Version 1.1 verification scope

These are results for the qualified release binaries, not a claim that every future build of this source has been tested.

| Artifact | SHA-256 |
| --- | --- |
| Native `Starfall-Salvage-1.1.gbc` | `105e410008ceb8dd2d6c83aebb033972b8cfcfeb41a714fcc7f260966ba193db` |
| Browser ROM used for the full campaign | `3d47ad53fc3fd75e80092df7f7ac1f45f6a6275d89d5c67794d862aecfda29da` |
| Earlier browser export, preview observation only | `cc5a3714c27f32f2a17d1e9a2cef2f465187212d4315c668ff41ea0b277ba177` |

The native image is 1 MiB, GBC-only, and uses header cartridge type `0x1E` (MBC5 + rumble + RAM + battery), with 32 KiB save RAM. Cartridge and emulator support must match the actual image; a physically fitting cartridge is not sufficient evidence of compatibility.

## Completed

- Fresh native emulator run through all 18 Story missions and 72 rooms, reaching Rank B with a displayed clear time of 35:27.
- Native: all 18 guardians with three separate CORE OPEN hits each; seven crew routes; all four rigs; both middle-route orders across the run.
- Native: pause freeze, mid-campaign Continue and Title → Continue restoring the completed ending.
- Separate native 1.1 controls regression: a complete Story mission, the 12-room Arcade cycle plus sector 13, banking 25,500, upgrade choices, retry, loss and menu/save transitions.
- Full campaign in the separately identified browser export: all 18 missions, 72 rooms, 18 guardians and seven escorts, with **STARFALL SAVED**, **00:42:41**, **RANK B - GOT HOME** observed at the ending. The run used standard pulse initially and Wide Coil for the later missions; both middle-route orders occurred, including the reversed order in mission 13. It does not repeat the native all-four-rig or complete Arcade qualification. See [the browser receipt](BROWSER-VERIFICATION.json).
- Browser saves: in-game Title → Continue restored the ending; the preview's **Restart game** control then produced a fresh title with **CONTINUE M18**, and Continue restored the same 42:41/Rank B ending. The inspected wrapper flushes external RAM and suppresses automatic emulator-state restore on that restart, so this checks browser-stored SRAM and fresh-emulator Continue. A normal page reload separately restored the ending paused through the plugin's full-state recovery. These results apply to the exact local export/runtime/origin, not another host or a full browser-process shutdown.
- Current manual screenshot pixels come from the exact native 1.1 image. They are emulator captures, not physical-device photographs. The cover is separately identified as illustration.
- Fresh-clone native and browser compilation on macOS arm64 with GB Studio CLI 4.3.2, engine 4.3.0-e1 and GBDK 4.5.0. The successful ROMs matched the corresponding frozen exports everywhere except the four-byte built-in save signature and two-byte global checksum. All eight non-ROM browser-export files matched exactly. See [the clean-build receipt](CLEAN-BUILD.json).

The native campaign used ordinary emulator controls without injecting game progress, actor positions or saves. The browser campaign likewise earned its progress through ordinary controls, with frequent observation pauses, failed attempts and retries. Once, after an accidental mission relaunch, the visible Saved states menu restored an already-earned mission 3 completion; it granted no new progress. No game-code change was needed for the browser clear. The measured clear timers count successful-room gameplay and exclude menus, pauses and failed attempts. Neither result measures first-time human play duration or difficulty.

The browser ran the official Binjgb export in Codex's in-app browser using runtime WASM SHA-256 `69aa17be45fec5fde585af4f39ed850b5d64107ec094a6482f316fef2fe7c945`. Its eight non-ROM export files match the earlier and clean-clone exports exactly. All 904 source/asset files still match the reviewed source snapshot. Only the built-in signature/checksum fields described below distinguish its ROM from the frozen native and earlier browser images. This establishes the identity of the tested browser export without assigning its results to every build or host.

Detailed recordings, receipts and independently reviewed evidence remain in the private local development archive. This portable repository retains summaries and artifact identities without copying save files, diagnostic logs or local machine paths.

## Clean-build limits

The fresh clone was commit `9c5c727ad55454be5737c3f066d873e970188970`. GB Studio derives its built-in save signature from loaded project data containing generated timestamps and filesystem inode values, so the successful builds are not byte-for-byte reproducible. The signature comparison is diagnostic only: the frozen release ROMs were not replaced or patched, and new builds do not inherit their gameplay or screenshot qualification.

Two repeat builds using deeper temporary paths failed after linking because no ROM was produced. The failed link command terminated with `SIGTRAP`; an unchanged-source cold build using a fresh short `/tmp` directory passed. [Build instructions](BUILDING.md) document that verified workaround. The upstream linker cause and cross-machine behavior remain unverified.

## Still required before public-release claims

- Uncoached human feedback on onboarding, clarity, challenge, pacing and enjoyment.
- Actual six-zone audio listening on speakers and headphones.
- Physical Chromatic play using the precise cartridge configuration being recommended.
- Save, full power-off, restart and Continue on that hardware; native emulator cold saves; full browser-process termination, storage eviction and cross-origin save behavior.
- Qualification of the final public browser host and any other browser/runtime combination; the complete local in-app-browser campaign is verified.
- Cross-machine build qualification; the completed clean-clone comparison covers the recorded macOS arm64 toolchain only.

Every possible route combination, later indefinite Arcade loops and all optional interaction boundaries have not been exhausted. This preparation does not load firmware or write an SD card.

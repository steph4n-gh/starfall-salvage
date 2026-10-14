# Version 1.1 verification scope

These are results for the qualified release binaries, not a claim that every future build of this source has been tested.

| Artifact | SHA-256 |
| --- | --- |
| Native `Starfall-Salvage-1.1.gbc` | `105e410008ceb8dd2d6c83aebb033972b8cfcfeb41a714fcc7f260966ba193db` |
| Official browser-export ROM | `cc5a3714c27f32f2a17d1e9a2cef2f465187212d4315c668ff41ea0b277ba177` |

The native image is 1 MiB, GBC-only, and uses header cartridge type `0x1E` (MBC5 + rumble + RAM + battery), with 32 KiB save RAM. Cartridge and emulator support must match the actual image; a physically fitting cartridge is not sufficient evidence of compatibility.

## Completed

- Fresh native emulator run through all 18 Story missions and 72 rooms, reaching Rank B with a displayed clear time of 35:27.
- All 18 guardians with three separate CORE OPEN hits each; seven crew routes; all four rigs; both middle-route orders across the run.
- Pause freeze, mid-campaign Continue and Title → Continue restoring the completed ending.
- Separate native 1.1 controls regression: a complete Story mission, the 12-room Arcade cycle plus sector 13, banking 25,500, upgrade choices, retry, loss and menu/save transitions.
- The official browser preview opened and was observed running; the browser ROM's identity was checked.
- Current manual screenshot pixels come from the exact native 1.1 image. They are emulator captures, not physical-device photographs. The cover is separately identified as illustration.

The full campaign used ordinary emulator controls. No game progress, actor positions or saves were injected. The measured clear timer counts successful-room gameplay and excludes menus, pauses and failed attempts. It is a guided functional clear, not a measured human first-play duration or difficulty rating.

Detailed recordings, receipts and independently reviewed evidence remain in the private local development archive. This portable repository retains summaries and artifact identities without copying save files, diagnostic logs or local machine paths.

## Still required before public-release claims

- Uncoached human feedback on onboarding, clarity, challenge, pacing and enjoyment.
- Actual six-zone audio listening on speakers and headphones.
- Physical Chromatic play using the precise cartridge configuration being recommended.
- Save, full power-off, restart and Continue on that hardware; browser reload/save persistence.
- Complete campaign in the final browser edition and host environment.
- Clean-clone build qualification and comparison with the tested artifact.

Every possible route combination, later indefinite Arcade loops and all optional interaction boundaries have not been exhausted. This preparation does not load firmware or write an SD card.

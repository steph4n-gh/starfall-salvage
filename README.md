# Starfall Salvage 1.2

An original Game Boy Color adventure by Stephan Arrington, created with OpenAI Codex assistance. Thrust, drift and brake through a damaged station, restore its systems, escort the crew and recover guardian cores.

**Private 1.2 review release.** Native Story and Arcade, targeted browser checks, the eleven-frame capture set and the fourteen-page illustrated manual have been reviewed. The synchronized package is deployed as Sites version 5, with [live delivery checks passed](docs/HOSTED-VERIFICATION.json). Keep GitHub private and the existing site owner-only. This repository does not deploy or publish automatically.

Story contains 18 missions across six zones and 72 large scrolling rooms. Arcade repeats 12 compact room templates with changing hazard pressure and replacement pulse rigs. The native game is GBC-only; its cartridge requirements are a 1 MiB MBC5 ROM and 32 KiB battery-backed save RAM.

## What changes in 1.2

- Filled cyan selections, a pointer, centered headings and visible A/B button badges.
- Arcade **Fly On** is selected by default and launches the next sector with the current rig. **Change Rig** is optional; **Bank Haul** secures the score and ends the sortie.
- Story route choices and ordinary **Bay Secured** cards continue directly with A. After **Mission Complete**, A opens **Flight Deck** on an available unfinished job; choose a mission and A launches.
- Flight Deck and next-bay/dock cards show the upcoming objective. Pause repeats the current objective. Initial Arcade, retry and restored launch checkpoints retain **Ready to Fly** briefings.
- Ship, stars and exhaust animate with the title theme. There is no intro to wait through.

Movement, combat, objective rules, scoring and rig effects retain their existing design. The update changes presentation and menu flow.

## Player materials and private site

- [1.2 quick start](release/player-v1.2/QUICK-START.txt) and [release notes](release/player-v1.2/RELEASE-NOTES.txt).
- The reviewed player package is `release/starfall-salvage-1.2-player.zip`, containing `Starfall-Salvage-1.2.gbc` and its documentation. The live ZIP and PDF downloads match the canonical files byte for byte; all eight ZIP entries passed the archive CRC check.
- [Private owner-only site](https://starfall.steph4n.dev) and [local launch-page workflow](launch-page/README.md). Sites version 5 serves 1.2. The [hosted receipt](docs/HOSTED-VERIFICATION.json) records controls, the preserved 1.1 M01 checkpoint, ordinary reload/Continue and download checks at the custom origin.
- [Remaining public-release work](docs/PUBLIC-RELEASE-PLAN.md).

To view the currently generated site locally:

```sh
python3 -m http.server 8080 --bind 127.0.0.1 --directory launch-page/dist
```

Open `http://127.0.0.1:8080/`. Use a local server for browser play. The Play in Browser button opens the official export under `play/`; browser files remain separate from the native player ZIP. Progress stays in each browser at its site address and does not sync across devices. The generated site must be refreshed only after the release review gates pass.

## Controls and saves

| Action | Handheld | Browser edition defaults |
| --- | --- | --- |
| Thrust; release to drift | D-pad | Arrow keys |
| Pulse a nearby enemy; confirm a menu choice | A | Z |
| Brake/interact; back or cancel in menus | B | X |
| Pause/resume | Start | Enter |
| Open exit options during play | Select | P or Shift |

Use Up/Down to highlight choices and A to confirm. At the flight deck, Up/Down selects a mission and Left/Right chooses an unlocked rig. After confirming a launch, release and press A again when you want to pulse. B has no action at the title; in Pause it resumes, from Change Rig it returns to the dock, and at the Arcade dock it opens exit options without banking.

Finish the room objective, then return beside the actual dock terminal. Guardians require three separate pulses during CORE OPEN, collection of their released cores and docking. Both Story middle bays are required: power first disables the other bay's hazard; supply first speeds pulse recharge there.

Before upgrading, **back up the existing ROM and battery save**. Use your emulator or cartridge's normal save import/export or association process to connect a copy with `Starfall-Salvage-1.2.gbc`. Some setups match saves by ROM basename; a new filename does not automatically migrate progress. Keep the original backup until Continue restores the expected checkpoint and a new save/reopen check succeeds. Continue restores a saved stage or room-entry briefing, not a mid-room position. An unfinished Arcade sortie has no persistent resume point.

## Keep updates synchronized

The [release manifest](release/release-manifest.json) binds the reviewed ROM, source snapshot, manual, player documents and genuine screenshots. Edit canonical sources and run the release checks after the new evidence is accepted:

```sh
python3 scripts/package-player-release.py
python3 scripts/sync-release.py sync
python3 scripts/sync-release.py check
python3 scripts/test-release-sync.py
```

Packaging reproduces the declared player payload; it does not compile or qualify the game. Changed review inputs stop preparation until the required review is recorded. Sync never approves a new ROM, manual or screenshot automatically. GitHub Actions runs checks only. See [the update workflow](docs/RELEASE-WORKFLOW.md) and [project instructions](AGENTS.md).

Reuse the existing Sites identity in [the hosting manifest](launch-page/.openai/hosting.json) for saved versions and authorized owner-only deployments. [The Sites receipt](docs/SITES-DRAFT.json) records the separately delivered version. Preserve owner-only access and GitHub privacy; public release and GitHub Pages remain unauthorized.

## Edit and build

Open `project.gbsproj` in GB Studio with `project/`, `assets/` and `plugins/` together. The snapshot includes the project resources and custom native engine. See [build notes](docs/BUILDING.md) before regenerating assets or changing toolchains. Project metadata retains format 4.2.0/release 10 without migration.

The earlier 1.1 clean-clone comparison compiled native and browser exports on macOS arm64. Generated save-signature and checksum bytes varied; all other compared ROM/runtime bytes matched. A short `/tmp` build directory worked around failures with deeper paths. [The receipt](docs/CLEAN-BUILD.json) retains that version's results. Separate 1.2 clean-clone and cross-machine reproducibility have not been established.

The [manual generator](campaign/full-length-packaging-stage/generate_manual.py) is the content source. Its [instructions](campaign/full-length-packaging-stage/README.md) describe the final-hash, screenshot and review gates. The 1.2 PDF, HTML and Markdown are generated from the accepted receipts and captures; [all fourteen PDF pages were visually reviewed](docs/MANUAL-REVIEW.json). The illustrated cover in `artwork/box-art.png` is artwork, not a gameplay screenshot.

## Qualification scope

The exact native 1.2 ROM completed all 18 Story missions, 72 rooms, 18 guardians and seven rescues, with **31:26, Rank B** on the ending screen. One M17 escort attempt failed and recovered through ordinary Retry. The timer counts successful-room gameplay, excluding menus, pauses and failed attempts; it is not a first-time human completion estimate. All 12 native Arcade sectors passed without retry, banking **22,500**. Same-session Title/Continue restored the Story ending after banking. All eleven canonical captures and the fourteen-page illustrated manual passed visual and identity checks. Native cold-start saves, heard audio, physical 1.2 hardware and power-off-save behavior remain unverified.

The exact browser 1.2 build completed targeted M01/M02 gameplay: eight Story rooms, including guardian failure and checkpoint Continue recovery. One Arcade sector was cleared after retry; Change Rig then Back kept the rig, and Bank Haul saved 300. Ordinary reload retained BEST 00300 and Continue restored M03 Bay 1 with full hull. Earlier reloads checked 1.1-to-1.2 continuation and earned route/mission checkpoints. Direct launch and Pause/Retry were also exercised. This is bounded browser gameplay and persistence evidence; no full browser campaign, complete Arcade cycle or browser clear-time claim is made. Same-session SRAM Continue and persisted browser reload are distinct from native cold-start or full browser-process shutdown tests.

Earlier evidence remains tied to 1.1: its guided native clear showed **35:27, Rank B**, and the separately identified browser clear showed **42:41, Rank B**. These timers count successful-room gameplay, excluding menus, pauses and failed attempts. The owner also reported successful 1.1 Chromatic play on October 14; that informal report does not qualify 1.2 or establish independent cartridge, audio or power-cycle tests.

[Verification scope](docs/VERIFICATION.md), [the native receipt](docs/NATIVE-VERIFICATION.json) and [the browser receipt](docs/BROWSER-VERIFICATION.json) identify accepted artifacts and limits. Uncoached human enjoyment, 1.2 physical hardware/audio/power-off behavior, full browser-process termination, other browsers/origins and cross-machine builds remain separate checks.

## Credits and licensing

See [credits](CREDITS.md), [the retained GB Studio notice](LICENSE) and [licensing status](docs/LICENSING.md). The original game's public licensing and distribution terms remain undecided. Preparing this private repository does not assign new license terms to the game or its assets.

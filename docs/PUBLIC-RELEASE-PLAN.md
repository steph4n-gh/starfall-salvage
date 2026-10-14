# Before public release

This is a private preparation repository. The site is deployed with authorized owner-only access. No public site, repository, release, or player download has been launched.

## Ready for review

- The exact native 1.1 ROM, a clean eight-file player ZIP, quick start, release notes and reviewed 14-page manual.
- An owner-only Sites website draft with seven displayed genuine native 1.1 captures, a private Play in Browser route, download links, installation routes, controls and compatibility scope. The site is deployed for private use; browser saves do not sync across devices.
- A shared release manifest, synchronization/check commands, durable update instructions and check-only CI to detect mismatched release artifacts.
- Editable game source, native art/data generators, and a portable manual generator.
- Matching player archive rebuild and screenshot provenance without private test-session records.
- Fresh-clone native and browser builds on macOS arm64, with exact artifact comparisons in [the clean-build receipt](CLEAN-BUILD.json). ROM differences were confined to GB Studio's built-in save signature and global checksum; all eight other browser-export files matched. Two deeper-path linker failures are retained, along with the verified short `/tmp` workaround.
- A complete local browser campaign: 18 missions, 72 rooms, 18 guardians and seven escorts; ending time 42:41, Rank B. Fresh-emulator Restart → Continue restored browser-stored SRAM, and ordinary page reload separately recovered an emulator snapshot. [The browser receipt](BROWSER-VERIFICATION.json) identifies the exact export and retains retries, recovery and timing limits.

## Next gates

1. **Blind player tests:** watch 3–5 new players without coaching. Track first dock, brake/pulse/menu understanding, crew proximity, guardian windows, difficulty spikes and reasons for stopping. Measure real human completion times before advertising them.
2. **Hardware, audio and saves:** qualify the exact Chromatic/cartridge combination, crowded scenes, display readability, speaker/headphone balance, and save → complete power off → Continue.
3. **Browser delivery:** the local in-app-browser campaign, Restart → Continue and page reload checks are complete. Qualify focus, controls, sound activation and persistence on the final hosting setup and any other supported browser. Full process termination, storage eviction and cross-origin behavior are not established. A new ROM/runtime requires appropriate repeat gameplay testing. Add a stable play URL only after it exists and is verified.
4. **Licensing and asset provenance:** choose the original work's terms and confirm retained resources' origins/notices. See [licensing status](LICENSING.md). Private preparation assigns no new terms.
5. **Launch/support:** select a feedback channel, prepare a genuine gameplay clip, recheck all links, and update only claims supported by completed tests. The 35:27 native and 42:41 browser guided clears are separate functional measurements, not typical-player durations.
6. **Cross-machine builds:** the recorded macOS arm64 clean-clone comparison is complete. Qualify any additional supported host/toolchain combination before claiming it works; preserve the documented signature nondeterminism and short-temporary-path workaround. Ordinary builds are not byte-for-byte reproducible.
7. **Explicit public-release decision:** keep GitHub private, GitHub Pages off and the deployed Sites website owner-only until public release is authorized. Remove draft banners/noindex only in that release step.

The existing 1.1 binary stays frozen. Gameplay or save changes require a new identified build and appropriate repeat verification; documentation-only work does not create a newly verified game build.

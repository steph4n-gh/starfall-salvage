# Editing and building

## Native game

The retained 1.1 build record identifies GB Studio CLI **4.3.2**, engine **4.3.0-e1**, and GBDK **4.5.0**. The project header retains its original GB Studio resource-format metadata, **4.2.0 / release 10**; that field is not the CLI version.

1. Install the versions above when comparing with the tested release. The toolchain is not vendored here. `GB_STUDIO_CLI` below must point to that installation's `gb-studio-cli.js`.
2. Clone this repository into a new directory, then work from its root. Keep `project.gbsproj`, `project/`, `assets/` and `plugins/` together. Do not copy generated build output or compiler caches from a previous checkout.
3. Keep the custom engine plugin at `plugins/starfall/engine`. It implements movement, encounters, menus, objectives, audio, saves and scrolling worlds. Omitting it produces a different game.
4. Build with separate, initially empty, short temporary paths. GB Studio uses `TMPDIR` for both its generated build tree and object cache on macOS/Linux; separate directories also avoid colliding with an interactive preview build. Long nested paths triggered a linker failure in this qualification; the fresh short path below passed.

   ```sh
   mkdir -p build
   sf_native_tmp="$(mktemp -d /tmp/starfall-native.XXXXXX)"
   sf_web_tmp="$(mktemp -d /tmp/starfall-web.XXXXXX)"
   TMPDIR="$sf_native_tmp" node "$GB_STUDIO_CLI" make:rom "$PWD/project.gbsproj" "$PWD/build/Starfall-Salvage-1.1.gbc" --verbose
   TMPDIR="$sf_web_tmp" node "$GB_STUDIO_CLI" make:web "$PWD/project.gbsproj" "$PWD/build/web" --verbose
   ```

   Use fresh temporary-directory names on a repeat qualification run. Preserve compiler output and exit codes. These command examples describe the qualified macOS invocation; Windows requires its own host-appropriate temporary-directory setup and qualification.

5. Check the new ROM's header and exact SHA-256, then test it before distributing it. The frozen release binary is identified in [VERIFICATION.md](VERIFICATION.md). A successful build is not a playthrough.

The project resources, PNGs and generated C tables are committed, so no Python asset-generation step is required to build the game. A fresh clone of commit `9c5c727ad55454be5737c3f066d873e970188970` compiled successfully on macOS arm64 on 2026-10-14: native and web builds both exited 0 with fresh output and cache directories. A further cold native build passed with a fresh short temporary path after two deeper-path attempts failed. See the [clean-build receipt](CLEAN-BUILD.json) for exact tool and artifact identities, including those failures.

### Linker path failure and verified workaround

Two attempts using longer nested temporary paths completed compilation but exited 1 because the generated ROM was missing after linking. Running the same failed link command directly showed signal 5 (`SIGTRAP`) with no linker diagnostic. An unchanged-source cold build using a fresh short `/tmp` directory exited 0 and produced a valid ROM. Keep temporary paths short and isolated; do not treat the CLI's final “Linking...” message as success. The upstream linker cause has not been established or patched. The known Node `DEP0190` warning appeared in successful builds too and is separate from these failures.

### Reproducibility limit

These official CLI builds are **not byte-for-byte reproducible**. Comparing the first clean native build with the frozen native release found only six changed bytes: the four-byte built-in GB Studio `save_signature` at ROM offsets `0x0481`–`0x0484`, and the two-byte global ROM checksum at `0x014E`–`0x014F`. The clean web ROM differed from its frozen browser ROM only within those same fields. All eight non-ROM web-export files matched the retained official export byte for byte. No ROM was patched or normalized for distribution.

GB Studio CLI 4.3.2 computes this signature from the loaded project data, whose asset records include generated timestamps and filesystem inode values. Rebuilding unchanged sources can therefore change the signature and checksum. The successful short-path repeat confirmed this variation without any source changes. The generated symbol map identifies the field; comparison after excluding only those six identified bytes is recorded as a diagnostic, not a claim that the binaries have the same identity.

Starfall's own checkpoints use a separate versioned, CRC-checked record in SRAM bank 3 (`plugins/starfall/engine/src/starfall_save.c`). That distinction explains why the built-in signature change is not evidence of a changed Starfall checkpoint schema. It does not replace save-persistence testing. Keep exact-ROM playthrough and screenshot provenance attached to the binary actually tested, including when this is the only observed build difference. No cross-machine deterministic-build claim is made.

## Game data and optional generators

- `campaign/active-missions.json` lists the 18 Story manifests; each has four rooms.
- `campaign/rooms.json` describes the 12 Arcade templates.
- `generate_room_runtime.py` reads those manifests and writes `starfall_rooms.h` and `starfall_rooms.c` in the engine plugin. It requires Python 3's standard library.
- The `*_art.py` and `encounter_effects.py` scripts require Pillow. They retain the original authoring implementations and use existing project scenes, sprite metadata and palettes. Several write active assets, manifests or generated C files; others write staging folders. Read each script's docstring and review changes before using its output.
- `campaign/zones-04-05-assets/zones_04_05_art.py` authors the two later zone groups. Its relative location is significant to its imports.

These authoring scripts are not a single incremental build pipeline. They preserve the development sources and should be run selectively in a clean working tree. In particular, do not rerun the early screen generator and assume it incorporates all subsequent six-zone code edits. The committed engine files are the current implementation.

## Browser edition

The command above produces the official web export. Serve that export directory through a web server. Keep the export's JavaScript, WASM and ROM together. Use the full-campaign browser-export hash in [VERIFICATION.md](VERIFICATION.md) only for that actual export, not for the native `.gbc` file or an earlier browser build. [The browser receipt](BROWSER-VERIFICATION.json) identifies the tested ROM/runtime; the successful clean-clone build is a separate artifact.

The private launch website includes the frozen official export at `play/index.html`, opened by its Play in Browser button. The nine canonical files in `release/browser-v1.1/` are copied unchanged by `scripts/sync-release.py`; serving this retained release does not require rebuilding it. The native player ZIP remains a separate download. The Site is saved without deployment, and no browser edition has been published. Browser focus, sound and persistent saves still require testing in any future hosted environment.

## Manual

See [the manual generator README](../campaign/full-length-packaging-stage/README.md). The generator is the content source and uses an explicit font directory. The reviewed manual separates native and browser campaign results, records the bounded local restart/reload tests, and clarifies that the browser edition is separate from the native player ZIP. Its nine native gameplay screenshots are unchanged. Generated documents require rendered visual review after a content or typography change.

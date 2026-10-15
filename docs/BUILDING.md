# Editing and building

## Native game

The recorded toolchain is GB Studio CLI **4.3.2**, engine **4.3.0-e1**, and GBDK **4.5.0**. The project header retains its original GB Studio resource-format metadata, **4.2.0 / release 10**; that field is not the CLI version. The frozen 1.2 native candidate has built successfully, passed header inspection and completed its 72-room Story run plus all 12 Arcade sectors. The [native receipt](NATIVE-VERIFICATION.json) records Story at 31:26, Rank B with one failed M17 attempt followed by ordinary retry, and Arcade banking 22,500 with zero failed Arcade attempts. The Story time is a successful-room timer, not human wall time. The existing fresh-clone build receipt is historical 1.1 evidence, not a clean-clone qualification of the changed 1.2 source.

1. Install the versions above when comparing with the tested release. The toolchain is not vendored here. `GB_STUDIO_CLI` below must point to that installation's `gb-studio-cli.js`.
2. Clone this repository into a new directory, then work from its root. Keep `project.gbsproj`, `project/`, `assets/` and `plugins/` together. Do not copy generated build output or compiler caches from a previous checkout.
3. Keep the custom engine plugin at `plugins/starfall/engine`. It implements movement, encounters, menus, objectives, audio, saves and scrolling worlds. Omitting it produces a different game.
4. Build with separate, initially empty, short temporary paths. GB Studio uses `TMPDIR` for both its generated build tree and object cache on macOS/Linux; separate directories also avoid colliding with an interactive preview build. In the 1.1 qualification, linker failures occurred with deeper paths and an unchanged-source build with a fresh short path passed. The underlying cause remains unverified.

   ```sh
   mkdir -p build
   sf_native_tmp="$(mktemp -d /tmp/starfall-native.XXXXXX)"
   sf_web_tmp="$(mktemp -d /tmp/starfall-web.XXXXXX)"
   TMPDIR="$sf_native_tmp" node "$GB_STUDIO_CLI" make:rom "$PWD/project.gbsproj" "$PWD/build/Starfall-Salvage-1.2.gbc" --verbose
   TMPDIR="$sf_web_tmp" node "$GB_STUDIO_CLI" make:web "$PWD/project.gbsproj" "$PWD/build/web" --verbose
   ```

   Use fresh temporary-directory names on a repeat qualification run. Preserve compiler output and exit codes. These command examples describe the qualified macOS invocation; Windows requires its own host-appropriate temporary-directory setup and qualification.

5. Check the new ROM's header and exact SHA-256, then test it before distributing it. Keep the new output separate from the frozen candidates identified in [VERIFICATION.md](VERIFICATION.md). A successful build is not a playthrough, and a rebuilt ROM does not inherit another binary's screenshots or qualification.

The project resources, PNGs and generated C tables are retained in the source tree, so no Python asset-generation step is required to build the game. For 1.1, a fresh clone of commit `9c5c727ad55454be5737c3f066d873e970188970` compiled successfully on macOS arm64 on 2026-10-14: native and web builds both exited 0 with fresh output and cache directories. A further cold native build passed with a fresh short temporary path after two deeper-path attempts failed. See the historical [clean-build receipt](CLEAN-BUILD.json) for exact identities and failures. A separate 1.2 clean-clone comparison remains pending.

### Linker path failure and verified workaround

During 1.1 qualification, two attempts using longer nested temporary paths completed compilation but exited 1 because the generated ROM was missing after linking. Running the same failed link command directly showed signal 5 (`SIGTRAP`) with no linker diagnostic. An unchanged-source cold build using a fresh short `/tmp` directory exited 0 and produced a valid ROM. Keep temporary paths short and isolated; do not treat the CLI's final “Linking...” message as success. The upstream linker cause has not been established or patched. The known Node `DEP0190` warning appeared in successful builds too and is separate from these failures.

### Reproducibility limit

The recorded 1.1 official CLI builds were **not byte-for-byte reproducible**. Comparing the first clean native build with the frozen 1.1 native release found only six changed bytes: the four-byte built-in GB Studio `save_signature` at ROM offsets `0x0481`–`0x0484`, and the two-byte global ROM checksum at `0x014E`–`0x014F`. The clean 1.1 web ROM differed from its frozen counterpart only within those same fields. All eight non-ROM web-export files matched the retained official export byte for byte. No ROM was patched or normalized for distribution.

GB Studio CLI 4.3.2 computes this signature from the loaded project data, whose asset records include generated timestamps and filesystem inode values. Rebuilding unchanged sources can therefore change the signature and checksum. The successful 1.1 short-path repeat confirmed this variation without source changes. Locate the field in each new build's generated symbol map; the frozen 1.2 native image places `_save_signature` at `0x04C1`, so the old offsets must not be reused blindly. Comparing the frozen 1.2 native/browser pair found differences only at `0x04C1`–`0x04C4` and `0x014E`–`0x014F`. That pairwise comparison is not a fresh-clone rebuild test and does not give the binaries the same identity.

Starfall's own checkpoints use a separate versioned, CRC-checked record in SRAM bank 3 (`plugins/starfall/engine/src/starfall_save.c`). That distinction explains why the built-in signature change is not evidence of a changed Starfall checkpoint schema. It does not replace save-persistence testing. Keep exact-ROM playthrough and screenshot provenance attached to the binary actually tested, including when this is the only observed build difference. No cross-machine deterministic-build claim is made.

## Game data and optional generators

- `campaign/active-missions.json` lists the 18 Story manifests; each has four rooms.
- `campaign/rooms.json` describes the 12 Arcade templates.
- `generate_room_runtime.py` reads those manifests and writes `starfall_rooms.h` and `starfall_rooms.c` in the engine plugin. It requires Python 3's standard library.
- The `*_art.py` and `encounter_effects.py` scripts require Pillow. They retain the original authoring implementations and use existing project scenes, sprite metadata and palettes. Several write active assets, manifests or generated C files; others write staging folders. Read each script's docstring and review changes before using its output.
- `campaign/zones-04-05-assets/zones_04_05_art.py` authors the two later zone groups. Its relative location is significant to its imports.
- `title_art_v12.py` retains the 1.2 title-art authoring process and animation data. Its preview is authored artwork; use exact-ROM emulator captures for gameplay screenshot provenance.

These authoring scripts are not a single incremental build pipeline. They preserve the development sources and should be run selectively in a clean working tree. In particular, do not rerun the early screen generator and assume it incorporates all subsequent six-zone code edits. The committed engine files are the current implementation.

## Browser edition

The command above produces the official web export. Serve that export directory through a web server. Keep its JavaScript, WASM, ROM and license notice together. The native and browser candidate hashes in [VERIFICATION.md](VERIFICATION.md) identify separate 1.2 artifacts. Current browser play covers M01/M02, one Arcade sector and targeted menu/save checks; no complete 1.2 browser campaign is claimed. [BROWSER-VERIFICATION.json](BROWSER-VERIFICATION.json) records current browser qualification; the complete 1.1 campaign remains in the [historical receipt](BROWSER-VERIFICATION-v1.1.json).

The private launch website serves the manifest-selected official export at `play/index.html`, opened by its Play in Browser button. The manifest selects the nine reviewed files in `release/browser-v1.2/`. `scripts/sync-release.py` copies that export unchanged, so serving a frozen release does not require rebuilding it. The native player ZIP remains a separate download. Preserve owner-only site access. The [historical hosted check](HOSTED-VERIFICATION-v1.1.json) covers 1.1; the 1.2 deployment requires its own delivery check. Sound, other devices and full browser-process termination remain separate checks. Browser saves do not sync across devices.

## Manual

See [the manual generator README](../campaign/full-length-packaging-stage/README.md). The generator is the content source and uses an explicit font directory. The current fourteen-page manual binds the accepted native/browser receipts and eleven canonical exact-ROM captures; nine of those images appear in the booklet. The [manual review](MANUAL-REVIEW.json) records the rendered-page, image-pixel and text-boundary checks. After future edits, review every rendered page again before accepting the PDF and input hashes. Generation alone is not visual review.

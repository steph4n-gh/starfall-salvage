# Editing and building

## Native game

The retained 1.1 build record identifies GB Studio CLI **4.3.2**, engine **4.3.0-e1**, and GBDK **4.5.0**. The project header retains its original GB Studio resource-format metadata, **4.2.0 / release 10**; that field is not the CLI version.

1. Install a compatible GB Studio toolchain, preferably the versions above when comparing with the tested release.
2. Open `project.gbsproj` with the adjacent `project/`, `assets/` and `plugins/` directories intact.
3. Keep the custom engine plugin at `plugins/starfall/engine`. It implements movement, encounters, menus, objectives, audio, saves and scrolling worlds. Omitting it produces a different game.
4. Export the Game Boy ROM using GB Studio. For the CLI, the recorded native build used the following invocation shape; substitute the location of your installed CLI:

   ```sh
   mkdir -p build
   node "$GB_STUDIO_CLI" make:rom project.gbsproj build/Starfall-Salvage-1.1.gbc --verbose
   ```

   `GB_STUDIO_CLI` must point to that installation's `gb-studio-cli.js`. The toolchain itself is not vendored in this repository. The command shape is taken from the retained successful build; a fresh build of this portable checkout has not yet been qualified.

5. Check the ROM header and test the resulting ROM before distributing it. The qualified native binary is identified in [VERIFICATION.md](VERIFICATION.md). Do not apply that binary's playthrough result automatically to a new build, even if the source changes appear small.

The current project resources, PNGs and generated C tables are committed, so no Python asset-generation step is required merely to open or build the game. The input files were copied byte-for-byte from the current editable source package. A clean-clone build and byte-for-byte reproducibility check remain to be performed; no cross-machine deterministic-build claim is made.

## Game data and optional generators

- `campaign/active-missions.json` lists the 18 Story manifests; each has four rooms.
- `campaign/rooms.json` describes the 12 Arcade templates.
- `generate_room_runtime.py` reads those manifests and writes `starfall_rooms.h` and `starfall_rooms.c` in the engine plugin. It requires Python 3's standard library.
- The `*_art.py` and `encounter_effects.py` scripts require Pillow. They retain the original authoring implementations and use existing project scenes, sprite metadata and palettes. Several write active assets, manifests or generated C files; others write staging folders. Read each script's docstring and review changes before using its output.
- `campaign/zones-04-05-assets/zones_04_05_art.py` authors the two later zone groups. Its relative location is significant to its imports.

These authoring scripts are not a single incremental build pipeline. They preserve the development sources and should be run selectively in a clean working tree. In particular, do not rerun the early screen generator and assume it incorporates all subsequent six-zone code edits. The committed engine files are the current implementation.

## Browser edition

Export the web build through the same GB Studio toolchain, then serve the export directory through a web server. Keep the export's JavaScript, WASM and ROM together. Use the tested browser-export hash in [VERIFICATION.md](VERIFICATION.md) only for that actual export, not for the native `.gbc` file: the two qualified ROM hashes differ.

No web host, Pages deployment or release-upload workflow is configured here. Browser focus, sound and persistent saves need testing in the final host environment.

## Manual

See [the manual generator README](../campaign/full-length-packaging-stage/README.md). The portable copy changes only font discovery in the generator; manual content and screenshot pixels are retained. Generated documents still require visual review after a content or typography change.

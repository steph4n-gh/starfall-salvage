# Editable 1.1 manual

`generate_manual.py` is the content source for `INSTRUCTIONS.md`, `INSTRUCTIONS.html` and the illustrated PDF. All 11 screenshot PNGs are genuine, unchanged 160 × 144 captures from the qualified native 1.1 ROM. Nine are embedded in the manual. `assets/screenshots/SCREENSHOTS.json` retains their hashes, captions and frame identifiers without private filesystem paths.

The portable generator preserves the reviewed booklet's content. Its only code adjustment replaces a machine-specific font directory with the `STARFALL_MANUAL_FONT_DIR` environment variable and an explicit missing-font message. Fonts are not bundled. Use **DejaVuSans.ttf** and **DejaVuSans-Bold.ttf** from your own DejaVu Sans installation.

From the repository root, with Python 3, Pillow and ReportLab installed:

```sh
export STARFALL_MANUAL_FONT_DIR=/path/to/dejavu-font-directory
python3 campaign/full-length-packaging-stage/generate_manual.py
```

The generated PDF is `output/pdf/Starfall-Salvage-Full-Campaign-Manual.pdf` beneath this directory. Markdown and HTML are updated here. The PDF output and per-run receipt are ignored by Git; review and explicitly promote final player artifacts separately. Do not replace a previously reviewed player PDF merely because generation succeeds.

The generator reads the 18 campaign manifests, artwork, screenshot manifest and selected source hashes. `assets/source-provenance.json` retains hash-only references from the original manual build, including verification files that are intentionally not included in this repository. Those retained hashes identify prior evidence; generation does not rerun gameplay tests.

After changing content, fonts or screenshots, render and inspect every page for clipping, overlap and legibility. Confirm screenshot hashes and captions, check image/link paths, and update the launch/download material consistently. The reviewed source booklet has 14 pages; a new font version can change pagination.

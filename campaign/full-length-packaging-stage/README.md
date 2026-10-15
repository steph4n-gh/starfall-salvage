# Editable 1.2 manual

`generate_manual.py` is the content source for `INSTRUCTIONS.md`, `INSTRUCTIONS.html` and the illustrated PDF. Version 1.2 covers filled choices, direct room continuation, optional Arcade rigs, objective reminders in Pause, the animated title and native-save upgrade steps. The current PDF has fourteen pages including its cover and nine genuine native gameplay screenshots. [The manual review](../../docs/MANUAL-REVIEW.json) records visual, pixel and structural checks.

The public edition links [browser play](https://starfall.steph4n.dev) and the [source project](https://github.com/steph4n-gh/starfall-salvage), and records the owner's confirmed Chromatic play. Pages 12-14 were updated and reviewed; pages 1-11 are unchanged from the earlier reviewed 1.2 manual.

## Accepted evidence

Native ROM SHA-256:

```text
da88897984d4ead183a8e14aa9c7dcea91592445e27a9cd62517cba432f83a78
```

The [native receipt](../../docs/NATIVE-VERIFICATION.json) records 18 missions, 72 rooms, 18 guardians and seven rescues, with 31:26 and Rank B at the ending. One M17 escort failure recovered through ordinary Retry. All twelve Arcade sectors passed without retry and banked 22,500; same-session Title/Continue restored the Story ending after banking. The clear timer excludes menus, pauses and failed attempts and is not a first-time human completion estimate.

The separate [browser receipt](../../docs/BROWSER-VERIFICATION.json) covers M01/M02, eight Story rooms, plus one Arcade sector and 300 banked. Ordinary reload retained the best score and restored M03 Bay 1 at full hull. Earned route/mission checkpoints and one same-origin 1.1-to-1.2 launch checkpoint were also recovered. This is bounded browser coverage; no full browser campaign, full Arcade cycle or browser clear time is claimed.

The [owner report](../../docs/HARDWARE-REPORT-v1.2.json) confirms successful version 1.2 play on a Chromatic using an SD flash cartridge. This is owner confirmation for that setup; the report does not identify the cartridge model or establish independent hardware validation, other setups, power-off save persistence or speaker/headphone listening. Native cold-start persistence is unsupported by the current native harness and remains unqualified. Full browser-process shutdown is also a separate unverified check.

## Exact-ROM screenshots

All eleven canonical PNGs in `assets/screenshots/` are unchanged 160 x 144 frames from the exact native ROM above. `SCREENSHOTS.json` preserves each PNG hash, decoded RGBA hash, frame/run identifiers and original capture-manifest hash. The generator checks image hashes, dimensions and ROM identity. The PDF review additionally checks decoded embedded pixels against these captures. Authored artwork and older captures cannot be relabeled as new gameplay evidence.

| Canonical capture | Use |
| --- | --- |
| `title-1.2.png` | Page 2 - title and mode selection |
| `escort-flight.png` | Page 5 - physical crew escort |
| `guardian-core-open.png` | Page 5 - guardian vulnerability |
| `route-choice.png` | Page 7 - direct route choice |
| `pause-menu.png` | Page 9 - Pause and current objective |
| `arcade-bank-choice.png` | Page 10 - Bank Haul selected on the dock card |
| `workbench.png` | Page 10 - optional rig picker, Keep Current selected |
| `arcade-bank-result.png` | Page 11 - 22,500 banked after twelve sectors |
| `story-ending-1.2.png` | Page 11 - 31:26, Rank B Story ending |
| `mission-board.png` | Additional website Flight Deck asset |
| `ion-hazard-active.png` | Additional website hazard frame |

The original 1.1 receipt is retained as [MANUAL-REVIEW-v1.1.json](../../docs/MANUAL-REVIEW-v1.1.json). Its player PDF remains unchanged. Earlier screenshot/manuscript files and receipts are also retained in the ignored local review archive. The pre-publication 1.2 PDF, generator, manuscripts and review receipt are retained in a separate hashed local backup; the current review records their identifiers.

## Generate and review again

The generator reads `STARFALL_MANUAL_FONT_DIR` and requires **DejaVuSans.ttf** plus **DejaVuSans-Bold.ttf**. Fonts are not bundled. With Python 3, Pillow and ReportLab, run from the repository root:

```sh
export STARFALL_MANUAL_FONT_DIR=/path/to/dejavu-font-directory
python3 campaign/full-length-packaging-stage/generate_manual.py
```

Output PDF: `output/pdf/Starfall-Salvage-Full-Campaign-Manual.pdf`. The generator also writes the Markdown, HTML, `MANUAL-RECEIPTS.json` and `assets/source-provenance.json`. It hashes the immutable native/browser receipts, accepted owner hardware report, source code, campaign data, box art and canonical captures. Mutable delivery-status summaries are excluded so packaging/hosting updates do not invalidate the authoring evidence. A pending identity or qualification placeholder stops generation.

Every regeneration requires fresh page rendering and visual inspection before promotion. Verify fourteen-page pagination, all text/tables/captions, nine embedded screenshot pixel matches, links, the resulting PDF hash and current source provenance. Record the review, copy the accepted PDF into the player folder, then synchronize the manifest, ZIP and site. Generation alone is not review approval.

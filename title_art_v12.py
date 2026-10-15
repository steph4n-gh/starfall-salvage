"""Author the native animated title, without touching the legacy screen pack.

Exact 2bpp pixels and CGB tile attributes, rather than a browser animation.
The image/GIF are authoring previews; ROM captures are qualified separately.
"""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageDraw
from screen_art import Canvas, SHADES, BASE_PALETTES, native_tiles, c_array

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "assets/interface/title-v1.2"
SRC = ROOT / "plugins/starfall/engine/src"
INC = ROOT / "plugins/starfall/engine/include"
PATCH = (8, 40, 120, 72)
PATCH_TILES = 56
PALETTES = [list(p) for p in BASE_PALETTES[:6]]
PALETTES[4] = [PALETTES[0][0], (14, 11, 6), (31, 25, 12), (31, 31, 31)]
FAR_CELLS = [(1, 0), (18, 1), (2, 3), (0, 6)]
NEAR_CELLS = [(18, 0), (0, 2), (19, 3)]


def tile_bytes(image, box):
    x0, y0, x1, y1 = box
    data = bytearray()
    for ty in range(y0, y1, 8):
        for tx in range(x0, x1, 8):
            for y in range(8):
                lo = hi = 0
                for x in range(8):
                    p = image.getpixel((tx + x, ty + y))
                    lo |= (p & 1) << (7 - x)
                    hi |= (p >> 1) << (7 - x)
                data.extend([lo, hi])
    return bytes(data)


def skiff(image, x, y, phase):
    """A long service skiff: twin nacelles, glass cockpit and cargo spine."""
    d = ImageDraw.Draw(image)
    def poly(points, color):
        d.polygon([(x + a, y + b) for a, b in points], fill=color)
    def line(points, color):
        d.line([(x + a, y + b) for a, b in points], fill=color)
    # Two uneven plasma tongues, rendered in a separate cyan tile palette.
    reach = [26, 30, 24, 29, 27, 23, 31, 25][phase]
    poly([(2, 10), (-reach, 12), (-reach + 7, 15), (3, 15)], 1)
    poly([(3, 11), (-reach + 5, 12), (-reach + 10, 14), (3, 14)], 2)
    poly([(3, 12), (-reach + 13, 12), (-reach + 9, 13), (3, 13)], 3)
    poly([(4, 18), (-reach + 9, 20), (-reach + 14, 22), (7, 22)], 1)
    poly([(4, 19), (-reach + 14, 20), (-reach + 11, 21), (7, 21)], 3)
    # Strong outer silhouette and a distinct raised cargo/engine assembly.
    poly([(2, 10), (17, 7), (26, 0), (34, 0), (35, 6), (56, 6),
          (76, 13), (72, 17), (55, 19), (36, 27), (23, 27),
          (25, 21), (7, 23), (0, 19)], 1)
    poly([(5, 11), (18, 9), (28, 2), (32, 2), (33, 8), (55, 8),
          (69, 13), (62, 16), (34, 17), (25, 21), (8, 20)], 2)
    line([(7, 11), (19, 10), (29, 3), (32, 3)], 3)
    line([(35, 9), (54, 9), (67, 13)], 3)
    line([(62, 17), (55, 17), (35, 25), (27, 25)], 2)
    poly([(35, 8), (42, 2), (52, 3), (60, 8)], 1)
    poly([(40, 7), (44, 4), (51, 4), (56, 7)], 3)
    line([(47, 4), (49, 7)], 2)
    poly([(12, 12), (22, 12), (22, 18), (12, 18)], 1)
    line([(13, 12), (13, 17), (20, 17), (20, 12)], 3)
    line([(16, 13), (16, 16)], 2)
    poly([(24, 10), (31, 10), (31, 16), (24, 16)], 1)
    line([(25, 11), (29, 11), (29, 14)], 3)
    poly([(29, 19), (36, 19), (43, 22), (33, 25)], 3)
    line([(9, 20), (20, 20)], 3)
    line([(4, 12), (7, 12), (7, 16), (3, 16)], 3)
    d.point((x + 63, y + 14), fill=3)
    d.point((x + 59, y + 14), fill=1)


def star_frame(phase, near, variant):
    im = Image.new("P", (8, 8), 0)
    d = ImageDraw.Draw(im)
    speed = 2 if near else 1
    x = (6 - phase * speed + variant * 3) & 7
    y = (1 + phase * speed + variant * 5) & 7
    if near:
        d.point(((x + 1) & 7, (y - 1) & 7), fill=1)
        d.point((x, y), fill=3)
        if variant:
            d.point(((x - 1) & 7, y), fill=2)
            d.point((x, (y + 1) & 7), fill=2)
    else:
        d.point((x, y), fill=1 + variant)
    return im


def base_canvas():
    c = Canvas()
    d = c.d
    # Purple crescent and block-edged crater scars, separate from the logo.
    c.planet(148, 56, 22)
    d.ellipse((139, 36, 169, 76), fill=0)
    d.arc((126, 34, 170, 78), 192, 286, fill=3)
    c.palette_rect((120, 32, 159, 71), 3)
    # Pale wreck fragments in the quiet left margin give the drift a scale.
    d.line((2, 32, 11, 30, 17, 32, 27, 29), fill=1)
    d.line((3, 34, 11, 32, 17, 34), fill=2)
    c.logo("STARFALL", 32, 3)
    c.logo("SALVAGE", 38, 22)
    c.palette_rect((32, 0, 127, 39), 1)
    # The fixed upload rectangle has no moving map attributes or UI overlap.
    c.d.rectangle((8, 40, 119, 71), fill=0)
    c.palette_rect((8, 40, 39, 71), 2)
    c.palette_rect((40, 40, 119, 71), 5)
    for x, y in FAR_CELLS:
        c.attrs[y * 20 + x] = 8
    for x, y in NEAR_CELLS:
        c.attrs[y * 20 + x] = 10
    # Everything at/below row9 remains a dark, strictly separate menu zone.
    c.d.rectangle((0, 72, 159, 143), fill=0)
    for y in range(9, 18):
        c.attrs[y * 20:(y + 1) * 20] = [8] * 20
    return c


def frame_image(base, ship_frame, near_phase, far_phase):
    c = Canvas()
    c.image = base.image.copy()
    c.attrs = list(base.attrs)
    c.image.paste(ship_frame.crop(PATCH), PATCH[:2])
    for cells, near, phase in [(FAR_CELLS, False, far_phase),
                               (NEAR_CELLS, True, near_phase)]:
        for i, (x, y) in enumerate(cells):
            c.image.paste(star_frame(phase, near, i & 1), (x * 8, y * 8))
    return c


def color_preview(c, shimmer=None):
    out = Image.new("RGB", (160, 144))
    for y in range(144):
        for x in range(160):
            p = c.attrs[y // 8 * 20 + x // 8] & 7
            if shimmer is not None and x // 8 == shimmer and y < 40:
                p = 4
            rgb = PALETTES[p][c.image.getpixel((x, y))]
            out.putpixel((x, y), tuple((v << 3) | (v >> 2) for v in rgb))
    return out


def decode(data, tilemap):
    out = Image.new("P", (160, 144), 0)
    for y in range(144):
        for x in range(160):
            off = tilemap[y // 8 * 20 + x // 8] * 16 + y % 8 * 2
            bit = 7 - x % 8
            out.putpixel((x, y), ((data[off] >> bit) & 1) |
                         (((data[off + 1] >> bit) & 1) << 1))
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    base = base_canvas()
    entrance = []
    idle = []
    for i, x in enumerate([-32, -12, 7, 21, 31, 37, 39, 40]):
        im = Image.new("P", (160, 144), 0)
        skiff(im, x, 42, i)
        entrance.append(im)
    for i, (dx, dy) in enumerate([(0, 0), (0, 0), (0, -1), (0, -1),
                                  (0, 0), (0, 1), (0, 1), (0, 0)]):
        im = Image.new("P", (160, 144), 0)
        skiff(im, 40 + dx, 42 + dy, i)
        idle.append(im)

    # Deduplicate the still image, then explicitly allocate the animated tiles.
    # A full rectangle is intentionally unique in VRAM so frames never alter
    # another repeated background tile or the native menu/font area.
    initial = frame_image(base, entrance[0], 0, 0)
    static = base.image.copy()
    static.paste(0, PATCH)
    for x, y in FAR_CELLS + NEAR_CELLS:
        static.paste(0, (x * 8, y * 8, x * 8 + 8, y * 8 + 8))
    tiles, tilemap, static_count = native_tiles(static)
    tilemap = bytearray(tilemap)
    first_ship = static_count
    tiles += tile_bytes(entrance[0], PATCH)
    for y in range(4):
        for x in range(14):
            tilemap[(y + 5) * 20 + x + 1] = first_ship + y * 14 + x
    first_far = static_count + PATCH_TILES
    first_near = first_far + 2
    for near, cells, start in [(False, FAR_CELLS, first_far),
                                (True, NEAR_CELLS, first_near)]:
        for variant in range(2):
            tiles += tile_bytes(star_frame(0, near, variant), (0, 0, 8, 8))
        for i, (x, y) in enumerate(cells):
            tilemap[y * 20 + x] = start + (i & 1)
    count = len(tiles) // 16
    assert count <= 176, (static_count, count)
    assert decode(tiles, tilemap).tobytes() == initial.image.tobytes()
    assert all((a & 7) <= 5 and (a & 8) for a in base.attrs)
    assert all(initial.image.getpixel((x, y)) == 0
               for y in range(72, 144) for x in range(160))

    ship_data = b"".join(tile_bytes(im, PATCH) for im in entrance + idle)
    far_data = b"".join(tile_bytes(star_frame(f, False, v), (0, 0, 8, 8))
                        for f in range(8) for v in range(2))
    near_data = b"".join(tile_bytes(star_frame(f, True, v), (0, 0, 8, 8))
                         for f in range(8) for v in range(2))
    assert len(ship_data) + len(far_data) + len(near_data) < 16384
    # Round-trip every moving tile in every frame, not just the first still.
    for f, im in enumerate(entrance + idle):
        live = bytearray(tiles)
        live[first_ship * 16:(first_ship + PATCH_TILES) * 16] = ship_data[f * 896:(f + 1) * 896]
        expected = frame_image(base, im, 0, 0)
        assert decode(live, tilemap).tobytes() == expected.image.tobytes()

    sym = "sf_screen_title"
    (INC / f"{sym}.h").write_text(
        "/* Generated by title_art_v12.py; exact native animated window art. */\n"
        "#ifndef SF_SCREEN_TITLE_H\n#define SF_SCREEN_TITLE_H\n"
        '#include <gbdk/platform.h>\n#include "bankdata.h"\n'
        f"BANKREF_EXTERN({sym})\n#define SF_SCREEN_TITLE_COUNT {count}u\n"
        f"#define SF_TITLE_SHIP_FIRST {first_ship}u\n#define SF_TITLE_SHIP_COUNT 56u\n"
        f"#define SF_TITLE_FAR_FIRST {first_far}u\n#define SF_TITLE_NEAR_FIRST {first_near}u\n"
        f"extern const UBYTE {sym}_tiles[{len(tiles)}];\n"
        f"extern const UBYTE {sym}_map[360];\nextern const UBYTE {sym}_attrs[360];\n#endif\n")
    (SRC / f"{sym}.c").write_text(
        '/* Generated by title_art_v12.py. */\n#pragma bank 255\n#include "sf_screen_title.h"\n'
        f"BANKREF({sym})\n" + c_array(sym + "_tiles", tiles) +
        c_array(sym + "_map", tilemap) + c_array(sym + "_attrs", base.attrs))
    (INC / "sf_title_motion.h").write_text(
        "/* Generated by title_art_v12.py. */\n#ifndef SF_TITLE_MOTION_H\n#define SF_TITLE_MOTION_H\n"
        '#include <gbdk/platform.h>\n#include "bankdata.h"\nBANKREF_EXTERN(sf_title_motion)\n'
        'extern const UBYTE sf_title_ship_frames[14336];\n'
        'extern const UBYTE sf_title_far_frames[256];\n'
        'extern const UBYTE sf_title_near_frames[256];\n#endif\n')
    (SRC / "sf_title_motion.c").write_text(
        '/* Generated by title_art_v12.py; one independently autobanked motion payload. */\n'
        '#pragma bank 255\n#include "sf_title_motion.h"\nBANKREF(sf_title_motion)\n' +
        c_array("sf_title_ship_frames", ship_data) +
        c_array("sf_title_far_frames", far_data) + c_array("sf_title_near_frames", near_data))

    initial.image.convert("RGB").save(OUT / "title-source.png")
    still = frame_image(base, idle[0], 2, 1)
    color_preview(still, 10).save(OUT / "title-color.png")
    frames = []
    for tick in range(144):
        ship = entrance[min(7, tick // 6)] if tick < 48 else idle[((tick - 48) // 6) & 7]
        c = frame_image(base, ship, (tick // 4) & 7, (tick // 16) & 7)
        frames.append(color_preview(c, 4 + ((tick // 8) % 12)))
    # Sample every other native frame to keep the illustration compact.
    frames[0].save(OUT / "title-motion.gif", save_all=True,
                   append_images=frames[2::2], duration=34, loop=0, disposal=2)
    receipt = {
        "format": "native-animated-title-v1.2", "dimensions": [160, 144],
        "source_shades": ["#071821", "#306850", "#86c06c", "#e0f8cf"],
        "art_rows": [0, 8], "quiet_menu_rows": [9, 17],
        "vram_bank": 1, "static_deduplicated_tiles": static_count,
        "fixed_ship_tiles": PATCH_TILES, "moving_star_tiles": 4,
        "live_tile_count": count, "highest_live_tile": count - 1,
        "reserved_ui_tiles": [176, 191], "reserved_font_tiles": [192, 233],
        "art_palettes": [0, 1, 2, 3, 4, 5], "untouched_ui_palettes": [6, 7],
        "motion_translation_unit_bytes": len(ship_data) + len(far_data) + len(near_data),
        "static_translation_unit_bytes": len(tiles) + 720,
        "ship_upload": {"first_tile": first_ship, "tiles": PATCH_TILES, "bytes": 896,
                        "frames": 16, "update_interval_native_frames": 6},
        "star_upload": {"near_interval": 4, "far_interval": 16, "bytes_each": 32},
        "round_trip": "Every initial screen pixel and all 16 ship frame patches match exact 2bpp decode",
        "banking": "GBVM restoring bankdata helpers only; motion and static art independently autobanked",
        "input": "Animation adds no wait beyond the existing menu transition guard; menu draws separately on rows9..17",
        "preview_scope": "Authored pixel preview, not a native ROM screenshot or measured performance proof",
        "native_rom": "Awaiting root build and emulator motion review",
        "sources": {},
    }
    for path in [OUT / "title-source.png", OUT / "title-color.png", OUT / "title-motion.gif",
                 SRC / "sf_screen_title.c", SRC / "sf_title_motion.c",
                 SRC / "starfall_screens.c", INC / "starfall_screens.h"]:
        receipt["sources"][str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    (OUT / "TITLE-RECEIPTS.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"tiles": count, "static": static_count,
                      "motion_bytes": receipt["motion_translation_unit_bytes"],
                      "preview": str((OUT / "title-color.png").relative_to(ROOT))}))


if __name__ == "__main__":
    main()

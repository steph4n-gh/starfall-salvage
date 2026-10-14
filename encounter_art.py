#!/usr/bin/env python3
"""Exact native source art for Starfall Salvage's reactor encounter.

No antialiasing, resampling, external images, or nondeterministic pixels. Run from
any directory; output is restricted to the two project-owned encounter PNGs.
Scene collisions are deliberately maintained by the game implementation.
"""
from pathlib import Path
from hashlib import sha256
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
DARK, STEEL, GLOW, WHITE = '#071821', '#306850', '#86c06c', '#e0f8cf'
TRANSPARENT = '#65ff00'


def room():
    im = Image.new('RGB', (160, 144), DARK)
    d = ImageDraw.Draw(im)

    # A small set of floor patterns carries the arena. Keep floor quiet and
    # darker than silhouettes, pickups, and the hard edged cover blocks.
    for ty in range(3, 16):
        for tx in range(1, 19):
            x, y = tx * 8, ty * 8
            d.rectangle((x, y, x + 7, y + 7), fill=STEEL)
            d.line((x, y + 7, x + 7, y + 7), fill=DARK)
            if (tx + ty) % 3 == 0:
                d.point((x + 1, y + 1), fill=GLOW)
            if tx % 4 == 0:
                d.line((x + 7, y + 1, x + 7, y + 6), fill=DARK)

    # Structural perimeter, beginning below the HUD. Thin white leading edges
    # and a dark four-pixel face read as solid, rather than floor decoration.
    for y in range(16, 128, 8):
        for x in (0, 152):
            d.rectangle((x, y, x + 7, y + 7), fill=DARK)
            d.rectangle((x + 1, y + 1, x + 6, y + 6), fill=STEEL)
            d.line((x + 1, y + 1, x + 6, y + 1), fill=GLOW)
            d.point((x + 3, y + 4), fill=DARK)
    for x in range(8, 152, 8):
        for y in (16, 128):
            d.rectangle((x, y, x + 7, y + 7), fill=DARK)
            d.rectangle((x, y + 1, x + 6, y + 5), fill=STEEL)
            d.line((x, y + 1, x + 6, y + 1), fill=GLOW)
            d.point((x + 3, y + 3), fill=DARK)
    d.line((8, 127, 151, 127), fill=GLOW)
    d.line((8, 24, 151, 24), fill=DARK)

    # The top windows sit on the arena's far wall. They stay within y16..31
    # and their black frames never suggest a navigable doorway.
    def window(x):
        d.rectangle((x, 16, x + 23, 31), fill=DARK)
        d.rectangle((x + 1, 17, x + 22, 30), outline=GLOW)
        d.line((x + 12, 18, x + 12, 29), fill=STEEL)
        for px, py, c in ((4, 21, WHITE), (17, 25, GLOW), (8, 27, GLOW), (20, 19, WHITE)):
            d.point((x + px, py), fill=c)
        d.line((x + 3, 30, x + 20, 30), fill=STEEL)
    window(16)
    window(120)

    # Passable central floor reactor: luminous concentric lines, but no wall
    # face. This is an animated-palette target, not another collision island.
    d.rectangle((64, 56, 95, 87), fill=DARK)
    d.rectangle((65, 57, 94, 86), fill=STEEL)
    d.line((68, 57, 91, 57), fill=GLOW)
    d.line((68, 86, 91, 86), fill=GLOW)
    d.line((65, 60, 65, 83), fill=GLOW)
    d.line((94, 60, 94, 83), fill=GLOW)
    # Octagonal center makes the room instantly recognizable in screenshots.
    ring = [(75, 62), (84, 62), (89, 67), (89, 76), (84, 81), (75, 81), (70, 76), (70, 67), (75, 62)]
    d.line(ring, fill=GLOW, width=1)
    d.line([(77, 66), (82, 66), (85, 69), (85, 74), (82, 77), (77, 77), (74, 74), (74, 69), (77, 66)], fill=DARK)
    d.rectangle((78, 69, 81, 74), fill=GLOW)
    d.line((76, 71, 83, 71), fill=WHITE)
    for x, y in ((67, 59), (92, 59), (67, 84), (92, 84)):
        d.point((x, y), fill=WHITE)

    # Repeated conduits are floor inlays, thin enough to preserve player contrast.
    for points in ([(24, 32), (24, 40), (32, 40)], [(128, 32), (128, 40), (120, 40)],
                   [(96, 72), (120, 72), (120, 104), (128, 104)],
                   [(80, 88), (80, 110)]):
        d.line(points, fill=DARK, width=2)
        d.line(points, fill=GLOW, width=1)

    # Exactly the two solid tile rectangles specified by game collisions.
    def cover(x, y):
        d.rectangle((x, y, x + 15, y + 15), fill=DARK)
        d.rectangle((x + 1, y + 1, x + 14, y + 10), fill=GLOW)
        d.line((x + 2, y + 1, x + 13, y + 1), fill=WHITE)
        d.rectangle((x + 2, y + 3, x + 13, y + 9), fill=STEEL)
        d.line((x + 7, y + 3, x + 7, y + 9), fill=DARK)
        d.line((x + 2, y + 5, x + 13, y + 5), fill=DARK)
        d.rectangle((x + 2, y + 12, x + 13, y + 13), fill=STEEL)
        d.point((x + 3, y + 12), fill=GLOW)
        d.point((x + 12, y + 12), fill=GLOW)
    cover(40, 56)
    cover(96, 80)

    # All three pickup stations have the same sharp bracket language. The
    # actual cell sprite sits over the center and disappears on collection.
    def pad(cx, cy):
        x, y = cx - 8, cy - 8
        d.rectangle((x, y, x + 15, y + 15), fill=DARK)
        d.rectangle((x + 2, y + 2, x + 13, y + 13), fill=STEEL)
        for xa, ya, xb, yb in ((x, y, x + 4, y), (x, y, x, y + 4),
                               (x + 11, y, x + 15, y), (x + 15, y, x + 15, y + 4),
                               (x, y + 15, x + 4, y + 15), (x, y + 11, x, y + 15),
                               (x + 11, y + 15, x + 15, y + 15), (x + 15, y + 11, x + 15, y + 15)):
            d.line((xa, ya, xb, yb), fill=GLOW)
        d.rectangle((cx - 2, cy - 2, cx + 1, cy + 1), outline=WHITE)
    pad(32, 48)
    pad(120, 40)
    pad(128, 104)

    # Discreet, asymmetric wall machinery never intrudes into movement paths.
    d.rectangle((48, 17, 63, 22), fill=DARK)
    for x in (50, 54, 58):
        d.line((x, 19, x + 1, 19), fill=WHITE)
    d.rectangle((80, 17, 103, 22), fill=DARK)
    for x in range(82, 102, 4):
        d.line((x, 18, x, 21), fill=GLOW)
    d.rectangle((145, 48, 151, 63), fill=DARK)
    for y in range(50, 62, 3):
        d.line((147, y, 150, y), fill=GLOW)
    d.rectangle((8, 88, 14, 103), fill=DARK)
    d.line((10, 90, 10, 99), fill=GLOW)
    d.rectangle((12, 92, 13, 94), fill=WHITE)

    # Dock/extraction is fixed to x64..95,y112..127. A bright entrance edge,
    # three aligned arrows, and inset bay distinguish it from a pickup station.
    d.rectangle((64, 112, 95, 127), fill=DARK)
    d.line((64, 112, 95, 112), fill=GLOW)
    d.line((64, 112, 64, 127), fill=WHITE)
    d.line((95, 112, 95, 127), fill=WHITE)
    d.rectangle((68, 115, 91, 126), fill=STEEL)
    for x in (71, 79, 87):
        d.line((x - 2, 119, x, 121, x + 2, 119), fill=GLOW)
        d.line((x - 2, 122, x, 124, x + 2, 122), fill=WHITE)
    d.line((68, 127, 91, 127), fill=GLOW)

    # Dark HUD reserve. The tiny lower separator keeps the screen composed
    # when the engine's window overlay is briefly hidden.
    d.rectangle((0, 0, 159, 15), fill=DARK)
    d.line((0, 15, 159, 15), fill=STEEL)
    for x in (4, 154):
        d.rectangle((x, 5, x + 1, 10), fill=GLOW)
    return im


def drone():
    # Chroma-key source convention is kept opaque, matching the existing PNGs.
    im = Image.new('RGB', (16, 16), TRANSPARENT)
    d = ImageDraw.Draw(im)
    # Horizontal stabilizers define a recognizably different silhouette from
    # the astronaut. There are no tiny dangling transparent interior pixels.
    d.rectangle((0, 6, 3, 10), fill=DARK)
    d.rectangle((12, 6, 15, 10), fill=DARK)
    d.line((0, 6, 3, 6), fill=WHITE)
    d.line((12, 6, 15, 6), fill=WHITE)
    d.line((1, 8, 3, 8), fill=GLOW)
    d.line((12, 8, 14, 8), fill=GLOW)
    d.polygon([(5, 2), (10, 2), (12, 4), (12, 11), (10, 13), (5, 13), (3, 11), (3, 4)], fill=DARK)
    d.line((5, 3, 10, 3), fill=WHITE)
    d.line((4, 4, 4, 10), fill=GLOW)
    d.line((11, 4, 11, 10), fill=GLOW)
    d.ellipse((5, 5, 10, 10), fill=GLOW)
    d.rectangle((7, 6, 8, 9), fill=DARK)
    d.point((6, 6), fill=WHITE)
    d.line((6, 12, 9, 12), fill=WHITE)
    d.line((5, 14, 6, 14), fill=GLOW)
    d.line((9, 14, 10, 14), fill=GLOW)
    return im


def write_checked(im, relative, allowed):
    pixels = set(im.getdata())
    expected = {tuple(bytes.fromhex(c[1:])) for c in allowed}
    assert pixels <= expected, (relative, pixels - expected)
    assert len(pixels) == len(expected), (relative, 'missing palette color')
    counts = []
    for y in range(0, im.height, 8):
        for x in range(0, im.width, 8):
            tile = im.crop((x, y, x + 8, y + 8))
            assert len(set(tile.getdata())) <= 4
            counts.append(tile.tobytes())
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, optimize=False)
    print(f'{relative}: {im.width}x{im.height}, {len(pixels)} exact colors, '
          f'{len(set(counts))} unique 8x8 tiles, SHA256={sha256(path.read_bytes()).hexdigest()}')


if __name__ == '__main__':
    write_checked(room(), 'assets/backgrounds/reactor_room.png', (DARK, STEEL, GLOW, WHITE))
    write_checked(drone(), 'assets/sprites/security_drone.png', (TRANSPARENT, DARK, GLOW, WHITE))

#!/usr/bin/env python3
"""Deterministic native room artwork and editable GB Studio scene resources.

Authoring uses four exact importer shades; tile attributes carry actual color.
The manifest owns gameplay geometry. Artwork never invents blocking scenery.
Run with the project's Pillow-enabled Python. No compiler, browser, or hardware
operation is performed by this generator.
"""
from collections import deque
from copy import deepcopy
from hashlib import sha256
from itertools import groupby
from pathlib import Path
from uuid import UUID, uuid5
import json
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
NAMESPACE = UUID('aa392071-34bf-5cdf-bbb4-d7f100ed8cb2')
SHADES = ['#071821', '#306850', '#86c06c', '#e0f8cf']
C = [tuple(bytes.fromhex(v[1:])) for v in SHADES]
ZONE_NAMES = ['WRECK HULL', 'COOLANT WORKS', 'STAR ENGINE']
ZONE_COLORS = [
    ['FFE4B4', 'DDA166', '6F5142', '191B2C'],
    ['DDFFFF', '79DCDD', '325E73', '101B35'],
    ['F8E3FF', 'C292E8', '58446F', '18162F'],
]
# Slot six is reserved for runtime hazards; slot seven for the UI.
PALETTE_IDS = ['default-bg-3', 'default-bg-3', 'default-bg-4', 'default-bg-5', 'default-bg-6']
PALETTE_COLORS = []
for pid in PALETTE_IDS:
    PALETTE_COLORS.append(json.loads((ROOT / f'project/palettes/{pid.replace("-", "_")}.gbsres').read_text())['colors'])


def ident(label):
    return str(uuid5(NAMESPACE, label))


def compressed(values):
    # Exact native GB Studio compress8bitNumberArray representation.
    return ''.join(f'{v:02x}' + ('!' if len(run) == 1 else f'{len(run):x}+')
                   for v, group in groupby(values) for run in [list(group)])


def expanded(data):
    out, i = [], 0
    while i < len(data):
        v = int(data[i:i + 2], 16); i += 2
        if data[i] == '!':
            count = 1; i += 1
        else:
            end = data.index('+', i); count = int(data[i:end], 16); i = end + 1
        out.extend([v] * count)
    return out


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def collision_grid(room):
    grid = [0] * 360
    for ty in range(18):
        for tx in range(20):
            if ty < 3 or ty >= 16 or tx == 0 or tx == 19:
                grid[ty * 20 + tx] = 15
    for x, y, w, h in room['covers']:
        for ty in range(y, y + h):
            for tx in range(x, x + w):
                grid[ty * 20 + tx] = 15
    return grid


def route_check(room, grid):
    # A conservative 16 x 16 body fits (the astronaut's real feet are 16 x 8).
    def free(cx, cy):
        return all(grid[(y // 8) * 20 + (x // 8)] == 0
                   for y in range(cy - 8, cy + 8)
                   for x in range(cx - 8, cx + 8))
    start = (80, 112)
    assert free(*start)
    seen, queue = {start}, deque([start])
    while queue:
        x, y = queue.popleft()
        for point in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 16 <= point[0] <= 144 and 32 <= point[1] <= 120 and point not in seen and free(*point):
                seen.add(point); queue.append(point)
    assert all(tuple(p) in seen for p in room['cells']), (room['name'], 'unreachable objective')
    dx, dy = room['drone']
    assert all(grid[(y // 8) * 20 + (x // 8)] == 0 for x in range(dx - 6, dx + 6) for y in range(dy - 6, dy + 6))
    hx, hy, hw, hh = room['hazard_rect']
    assert all(grid[y * 20 + x] == 0 for y in range(hy, hy + hh) for x in range(hx, hx + hw))
    assert all(grid[y * 20 + x] == 0 for y in (14, 15) for x in range(8, 12))
    return {'body': 'conservative 16x16', 'reachable_centers': len(seen),
            'all_three_objectives_reachable': True, 'drone_spawn_clear': True,
            'hazard_on_clear_floor': True, 'dock_clear': True}


class RoomCanvas:
    def __init__(self, room):
        self.room = room
        self.image = Image.new('RGB', (160, 144), C[0])
        self.draw = ImageDraw.Draw(self.image)
        self.attributes = [0] * 360

    def region(self, x, y, w, h, palette):
        for ty in range(y, y + h):
            for tx in range(x, x + w):
                if 0 <= tx < 20 and 0 <= ty < 18:
                    self.attributes[ty * 20 + tx] = palette

    def rect(self, xy, fill=None, outline=None, width=1):
        self.draw.rectangle(xy, fill=None if fill is None else C[fill],
                            outline=None if outline is None else C[outline], width=width)

    def line(self, xy, fill, width=1):
        self.draw.line(xy, fill=C[fill], width=width)

    def point(self, xy, fill):
        self.draw.point(xy, fill=C[fill])

    def pipe(self, points, palette=1):
        # Flush floor conduits use narrow lines, never a raised block silhouette.
        self.line(points, 0, 3)
        self.line(points, 2, 1)
        for x, y in points:
            self.region(x // 8, y // 8, 1, 1, palette)

    def pad(self, cx, cy, relay=False, order=0):
        x, y = cx - 8, cy - 8
        self.region(x // 8, y // 8, 2, 2, 2)
        self.rect((x, y, x + 15, y + 15), 0)
        self.rect((x + 2, y + 2, x + 13, y + 13), 1)
        self.rect((x + 4, y + 4, x + 11, y + 11), outline=2)
        for ax, ay, bx, by in [(0, 0, 4, 0), (0, 0, 0, 4), (11, 0, 15, 0), (15, 0, 15, 4),
                               (0, 15, 4, 15), (0, 11, 0, 15), (11, 15, 15, 15), (15, 11, 15, 15)]:
            self.line((x + ax, y + ay, x + bx, y + by), 2)
        if relay:
            # One/two/three bright indicator bars give the ordered nodes a
            # visible identity even before runtime highlighting is applied.
            for n in range(order + 1):
                self.line((x + 4 + n * 3, y + 11, x + 4 + n * 3, y + 13), 3)
        else:
            self.point((x + 2, y + 2), 3); self.point((x + 13, y + 13), 3)

    def cover(self, tx, ty, tw, th):
        x, y, w, h = tx * 8, ty * 8, tw * 8, th * 8
        self.region(tx, ty, tw, th, 3)
        self.rect((x, y, x + w - 1, y + h - 1), 0)
        self.rect((x + 1, y + 1, x + w - 2, y + h - 6), 2)
        self.line((x + 2, y + 1, x + w - 3, y + 1), 3)
        self.rect((x + 2, y + 3, x + w - 3, y + h - 7), 1)
        self.line((x + w // 2, y + 3, x + w // 2, y + h - 7), 0)
        self.line((x + 2, y + 5, x + w - 3, y + 5), 0)
        self.rect((x + 2, y + h - 4, x + w - 3, y + h - 3), 1)
        self.point((x + 3, y + h - 4), 2); self.point((x + w - 4, y + h - 4), 2)

    def perimeter(self):
        z = self.room['zone']
        # Quiet repeated steel flooring leaves object silhouettes dominant.
        for ty in range(3, 16):
            for tx in range(1, 19):
                x, y = tx * 8, ty * 8
                self.rect((x, y, x + 7, y + 7), 1)
                self.line((x, y + 7, x + 7, y + 7), 0)
                if (tx + ty) % 4 == 0:
                    self.point((x + 1, y + 1), 2)
                if tx % 4 == 0:
                    self.line((x + 7, y + 2, x + 7, y + 5), 0)
        for y in range(16, 136, 8):
            for x in (0, 152):
                self.rect((x, y, x + 7, y + 7), 0)
                self.rect((x + 1, y + 1, x + 6, y + 6), 1)
                self.line((x + 1, y + 1, x + 6, y + 1), 2)
                self.point((x + 3, y + 4), 0)
        for y in (16, 128):
            for x in range(8, 152, 8):
                self.rect((x, y, x + 7, y + 7), 0)
                self.rect((x, y + 1, x + 6, y + 5), 1)
                self.line((x, y + 1, x + 6, y + 1), 2)
                self.point((x + 3, y + 3), 0)
        self.line((8, 127, 151, 127), 2)
        self.line((8, 24, 151, 24), 0)
        # Palette-independent repeated slats make each zone's architecture
        # distinct before colored light is applied.
        for x in (8, 144):
            for y in (48, 80, 104):
                self.rect((x, y, x + 7, y + 15), 0)
                if z == 0:
                    for yy in range(y + 2, y + 14, 4): self.line((x + 1, yy, x + 5, yy), 2)
                elif z == 1:
                    self.rect((x + 2, y + 1, x + 5, y + 13), 1)
                    self.line((x + 2, y + 2, x + 2, y + 12), 3)
                    self.line((x + 3, y + 10, x + 4, y + 10), 2)
                else:
                    self.line([(x + 2, y + 2), (x + 5, y + 5), (x + 2, y + 8), (x + 5, y + 11)], 2)
                    self.point((x + 2, y + 2), 3)
                self.region(x // 8, y // 8, 1, 2, 1)
        for x in (16, 120):
            self.window(x, z)
        # Actual physical floor remains safe and visibly clear at extraction.
        self.dock()
        self.rect((0, 0, 159, 15), 0)
        self.line((0, 15, 159, 15), 1)

    def window(self, x, zone):
        self.region(x // 8, 2, 3, 2, 2)
        self.rect((x, 16, x + 23, 31), 0)
        self.rect((x + 1, 17, x + 22, 30), outline=2)
        self.line((x + 12, 18, x + 12, 29), 1)
        for px, py, color in ((4, 21, 3), (17, 25, 2), (8, 27, 2), (20, 19, 3)):
            self.point((x + px, py), color)
        if zone == 1:
            self.line((x + 3, 22, x + 9, 28), 1)
            self.line((x + 15, 20, x + 20, 25), 1)
        elif zone == 2:
            self.draw.arc((x + 7, 20, x + 22, 35), 180, 300, fill=C[2])
        self.line((x + 3, 30, x + 20, 30), 1)

    def dock(self):
        self.region(8, 14, 4, 2, 3)
        self.rect((64, 112, 95, 127), 0)
        self.line((64, 112, 95, 112), 2)
        self.line((64, 112, 64, 127), 3); self.line((95, 112, 95, 127), 3)
        self.rect((68, 115, 91, 126), 1)
        for x in (71, 79, 87):
            self.line([(x - 2, 119), (x, 121), (x + 2, 119)], 2)
            self.line([(x - 2, 122), (x, 124), (x + 2, 122)], 3)
        self.line((68, 127, 91, 127), 2)

    def room_plate(self):
        # A native 3x5 room plaque labels the far bulkhead. It occupies only
        # already-solid wall tiles and remains legible at the 160x144 scale.
        alphabet = {
            'A': ['010','101','111','101','101'], 'B': ['110','101','110','101','110'],
            'C': ['011','100','100','100','011'], 'D': ['110','101','101','101','110'],
            'E': ['111','100','110','100','111'], 'F': ['111','100','110','100','100'],
            'G': ['011','100','101','101','011'], 'H': ['101','101','111','101','101'],
            'I': ['111','010','010','010','111'], 'J': ['001','001','001','101','010'],
            'K': ['101','101','110','101','101'], 'L': ['100','100','100','100','111'],
            'M': ['101','111','111','101','101'], 'N': ['101','111','111','111','101'],
            'O': ['010','101','101','101','010'], 'P': ['110','101','110','100','100'],
            'Q': ['010','101','101','111','011'], 'R': ['110','101','110','101','101'],
            'S': ['011','100','010','001','110'], 'T': ['111','010','010','010','010'],
            'U': ['101','101','101','101','111'], 'V': ['101','101','101','101','010'],
            'W': ['101','101','111','111','101'], 'X': ['101','101','010','101','101'],
            'Y': ['101','101','010','010','010'], 'Z': ['111','001','010','100','111'],
            ' ': ['000']*5,
        }
        label = self.room['name']
        start = 80 - (len(label) * 4 - 1) // 2
        self.rect((48, 16, 111, 23), 0)
        self.region(6, 2, 8, 1, 3)
        for index, char in enumerate(label):
            for dy, row in enumerate(alphabet[char]):
                for dx, value in enumerate(row):
                    if value == '1': self.point((start + index * 4 + dx, 18 + dy), 2)
        # Bottom service rail: repeating units rather than another walk surface.
        for x in range(0, 160, 8):
            self.rect((x, 136, x + 7, 143), 0)
            self.line((x + 1, 137, x + 6, 137), 1)
            if x % 32 == 0:
                self.line((x + 2, 140, x + 4, 140), 2)

    def landmark(self):
        r = self.room['room']
        # All large landmarks are flush floor motifs. Bright cover faces are
        # drawn later so the collision islands remain unambiguous.
        if r == 0:  # Airlock iris set into the floor.
            self.region(8, 6, 4, 4, 4)
            self.rect((64, 48, 95, 79), 0)
            self.draw.ellipse((66, 50, 93, 77), outline=C[2])
            self.draw.ellipse((70, 54, 89, 73), outline=C[1])
            self.line([(73, 50), (78, 61), (93, 63)], 2)
            self.line([(90, 73), (81, 64), (69, 73)], 2)
            self.line([(66, 59), (77, 65), (75, 77)], 2)
            self.rect((77, 61, 82, 66), 1, 3)
        elif r == 1:  # Cargo spine: central inlaid freight rail.
            for y in range(32, 112, 8):
                self.rect((87, y, 103, y + 7), 0)
                self.line((89, y, 89, y + 7), 2); self.line((101, y, 101, y + 7), 2)
                self.line((92, y + 3, 98, y + 3), 1)
            self.region(10, 4, 3, 10, 3)
            for x, y in ((24, 56), (112, 80)):
                self.rect((x, y, x + 15, y + 15), 0, 1)
                self.line((x + 2, y + 12, x + 12, y + 2), 1)
        elif r == 2:  # Signal board: three circular induction rings.
            for cx, cy in self.room['cells']:
                self.pipe([(80, 48), (cx, 48), (cx, cy)])
            self.region(8, 6, 4, 3, 4)
            self.rect((64, 48, 95, 71), 0)
            for x in (67, 77, 87):
                self.rect((x, 51, x + 5, 65), 1, 2)
                self.line((x + 2, 54, x + 2, 62), 3)
            self.line((66, 68, 93, 68), 1)
        elif r == 3:  # Dock lock: wide floor gate and long latch indicator.
            self.region(3, 10, 14, 1, 3)
            self.rect((24, 80, 135, 87), 0)
            for x in range(24, 136, 8):
                self.line((x + 1, 81, x + 5, 85), 2)
                self.point((x + 1, 86), 1)
            for y in (32, 96):
                self.rect((64, y, 95, y + 7), 0, 1)
                for x in range(67, 94, 4): self.line((x, y + 2, x, y + 5), 2)
                self.region(8, y // 8, 4, 1, 4)
        elif r == 4:  # Pump garden: inset blue fluid channels.
            for y in (40, 88):
                self.rect((32, y, 127, y + 7), 0)
                for x in range(32, 128, 8):
                    self.line((x + 1, y + 2, x + 4, y + 2), 1)
                    self.line((x + 3, y + 5, x + 6, y + 5), 2)
                self.region(4, y // 8, 12, 1, 2)
            for x in (64, 104):
                self.rect((x, 64, x + 15, 79), 0, 2)
                self.draw.ellipse((x + 3, 67, x + 12, 76), outline=C[1])
                self.line((x + 8, 68, x + 8, 75), 3)
                self.region(x // 8, 8, 2, 2, 4)
        elif r == 5:  # Heat exchanger: inset radiator array.
            self.region(8, 6, 4, 3, 4)
            self.rect((64, 48, 95, 71), 0)
            for x in range(67, 94, 4):
                self.line((x, 51, x, 67), 2)
                self.line((x + 1, 53, x + 1, 65), 1)
            self.line((66, 69, 93, 69), 3)
            for cx, cy in self.room['cells']: self.pipe([(80, 64), (cx, 64), (cx, cy)])
        elif r == 6:  # Prism bridge: crystalline field etched into the floor.
            self.region(8, 8, 4, 4, 2)
            self.rect((64, 64, 95, 95), 0)
            self.draw.polygon([(80, 66), (93, 78), (80, 93), (66, 78)], outline=C[2])
            self.line([(80, 66), (75, 80), (80, 93), (84, 78), (80, 66)], 1)
            self.line((67, 78, 92, 78), 3)
            for x in range(24, 144, 8):
                self.line((x, 104, x + 3, 104), 1)
        elif r == 7:  # Manifold: routed valve lines linking ordered relays.
            for cx, cy in self.room['cells']:
                self.pipe([(112, 88), (cx, 88), (cx, cy)], 2)
            self.region(13, 9, 3, 3, 4)
            self.rect((104, 72, 127, 95), 0)
            self.draw.ellipse((107, 75, 124, 92), outline=C[2])
            self.line((109, 83, 122, 83), 3); self.line((115, 77, 115, 90), 1)
        elif r == 8:  # Outer array: six inlaid stellar receivers.
            for x, y in ((56, 32), (96, 32), (24, 64), (120, 64), (56, 96), (96, 96)):
                self.region(x // 8, y // 8, 2, 2, 4)
                self.rect((x, y, x + 15, y + 15), 0)
                self.line([(x + 1, y + 2), (x + 7, y + 7), (x + 13, y + 2)], 2)
                self.line([(x + 1, y + 13), (x + 7, y + 8), (x + 13, y + 13)], 2)
                self.line((x + 7, y + 3, x + 7, y + 12), 3)
        elif r == 9:  # Ion gallery: repeated recessed conduit channels.
            for x in (32, 96, 120):
                self.region(x // 8, 6, 2, 7, 4)
                self.rect((x, 48, x + 15, 103), 0)
                for y in range(50, 102, 8):
                    self.line([(x + 3, y), (x + 11, y + 3), (x + 3, y + 6)], 2)
                    self.point((x + 11, y + 3), 3)
            for cx, cy in self.room['cells']: self.pipe([(88, 88), (cx, 88), (cx, cy)], 2)
        elif r == 10:  # Capacitor hall: glowing parallel energy reservoirs.
            for x in (64, 88):
                self.region(x // 8, 6, 2, 3, 4)
                self.rect((x, 48, x + 15, 71), 0)
                self.rect((x + 2, 50, x + 13, 68), outline=2)
                for y in range(53, 67, 4): self.line((x + 4, y, x + 11, y), 1)
                self.line((x + 7, 52, x + 7, 66), 3)
                self.line((x + 4, 70, x + 11, 70), 2)
            self.pipe([(80, 72), (80, 88), (120, 88), (120, 104)])
        else:  # Warden core: nested octagonal field around the guardian.
            self.region(6, 8, 8, 3, 4)
            self.rect((48, 64, 111, 87), 0)
            for inset in (0, 5, 10):
                x, y, w, h = 50 + inset, 65 + inset // 2, 60 - 2 * inset, 21 - inset
                points = [(x + 8, y), (x + w - 8, y), (x + w, y + 5), (x + w, y + h - 5),
                          (x + w - 8, y + h), (x + 8, y + h), (x, y + h - 5), (x, y + 5), (x + 8, y)]
                self.line(points, 2 if inset != 5 else 1)
            self.line((72, 80, 87, 80), 3)
            # Recessed containment pylons terminate in crisp luminous teeth;
            # their low-value outlines stay visually separate from solid crates.
            for x in (48, 104):
                self.rect((x, 64, x + 7, 87), 0, 1)
                for yy in (67, 73, 79, 85):
                    self.line((x + 2, yy, x + 5, yy), 2)
                    self.point((x + 3, yy - 1), 3)
            for x in (56, 96):
                self.line((x, 68, x + 6, 68), 3)
                self.line((x, 84, x + 6, 84), 3)
            self.line((80, 72, 80, 85), 3)
            for points in ([(48, 72), (32, 72), (32, 40)], [(111, 72), (120, 72), (120, 40)],
                           [(111, 80), (120, 80), (120, 104)]): self.pipe(points, 4)

    def hazard_floor(self):
        # Authored hazard fixtures occupy exactly the runtime replacement area.
        x, y, w, h = self.room['hazard_rect']
        if not w or not h: return
        self.region(x, y, w, h, 0)
        for ty in range(y, y + h):
            for tx in range(x, x + w):
                px, py = tx * 8, ty * 8
                self.rect((px, py, px + 7, py + 7), 1)
                if self.room['hazard'] == 'vent':
                    self.rect((px + 1, py + 1, px + 6, py + 6), 0)
                    for yy in (py + 2, py + 4): self.line((px + 2, yy, px + 5, yy), 1)
                else:
                    self.line((px, py + 3, px + 7, py + 3), 0)
                    self.line((px, py + 4, px + 7, py + 4), 2)

    def finish(self):
        self.perimeter(); self.landmark(); self.room_plate()
        self.hazard_floor()
        for cover in self.room['covers']: self.cover(*cover)
        for order, (cx, cy) in enumerate(self.room['cells']):
            self.pad(cx, cy, self.room['objective'] == 'relay', order)
        # Repaint the safe extraction fixture after any long conduit.
        self.dock()
        return self.image, self.attributes


def native_color(image, attributes, zone):
    palettes = [ZONE_COLORS[zone]] + PALETTE_COLORS
    out = Image.new('RGB', image.size)
    for y in range(144):
        for x in range(160):
            source = C.index(image.getpixel((x, y)))
            color = palettes[attributes[(y // 8) * 20 + (x // 8)]][3 - source]
            rgb = tuple(bytes.fromhex(color))
            out.putpixel((x, y), tuple(round((value >> 3) * 255 / 31) for value in rgb))
    return out


def resources(room, attributes, grid):
    n = room['room'] + 1
    bgid, sid = ident(f'background-{n:02d}'), ident(f'scene-{n:02d}')
    paletteid = ident(f'zone-palette-{room["zone"]}')
    write_json(ROOT / f'assets/backgrounds/room_{n:02d}.png.gbsres', {
        '_resourceType': 'background', 'id': bgid, 'name': room['name'].title(),
        'symbol': f'bg_room_{n:02d}', 'filename': f'room_{n:02d}.png',
        'width': 20, 'height': 18, 'imageWidth': 160, 'imageHeight': 144,
        'autoColor': False, 'tileColors': compressed(attributes),
    })
    original = ROOT / 'project/scenes/start'
    scene = json.loads((original / 'scene.gbsres').read_text())
    scene.update(id=sid, _index=n, name=f'{n:02d} {room["name"].title()}',
                 symbol=room['scene_symbol'], x=(n - 1) % 4 * 240, y=room['zone'] * 220,
                 backgroundId=bgid, paletteIds=[paletteid] + PALETTE_IDS + [paletteid, 'default-ui'],
                 collisions=compressed(grid), script=[])
    dest = ROOT / f'project/scenes/room_{n:02d}'
    write_json(dest / 'scene.gbsres', scene)
    originals = sorted((json.loads(p.read_text()) for p in (original / 'actors').glob('*.gbsres')),
                       key=lambda actor: actor['_index'])
    centers = room['cells'] + [[80, 112], room['drone'], [80, 104]]
    for actor, (cx, cy) in zip(originals, centers):
        index = actor['_index']
        actor.update(id=ident(f'room-{n:02d}-actor-{index}'), symbol=f'actor_r{n:02d}_{index}',
                     x=(cx - 8) // 8, y=cy // 8)
        write_json(dest / 'actors' / f'actor_{index}.gbsres', actor)
    return sid, bgid


def main():
    rooms = json.loads((ROOT / 'campaign/rooms.json').read_text())
    assert len(rooms) == 12 and [r['room'] for r in rooms] == list(range(12))
    for zone, colors in enumerate(ZONE_COLORS):
        write_json(ROOT / f'project/palettes/zone_{zone + 1}.gbsres', {
            '_resourceType': 'palette', 'id': ident(f'zone-palette-{zone}'),
            'name': ZONE_NAMES[zone].title(), 'colors': colors,
        })
    receipt = {'source': 'Original authored pixels; no external artwork or antialiasing',
               'source_shades': SHADES, 'zones': [], 'manifest_sha256': sha256((ROOT / 'campaign/rooms.json').read_bytes()).hexdigest(),
               'geometry': 'Manifest covers plus outer walls; art does not add collision',
               'runtime_review': 'Source preview only; actual built-ROM review is separate', 'rooms': []}
    for z, colors in enumerate(ZONE_COLORS):
        receipt['zones'].append({'name': ZONE_NAMES[z], 'palette_id': ident(f'zone-palette-{z}'), 'rgb888': colors,
                                 'rgb555': [sum(((int(color[k:k+2], 16) >> 3) << ((k // 2) * 5)) for k in (0, 2, 4)) for color in colors]})
    montage = Image.new('RGB', (4 * 320, 3 * 320), '#10131F')
    md = ImageDraw.Draw(montage)
    for room in rooms:
        n = room['room'] + 1
        image, attributes = RoomCanvas(room).finish()
        grid = collision_grid(room)
        route = route_check(room, grid)
        assert set(image.getdata()) <= set(C)
        tile_count = len({image.crop((x, y, x + 8, y + 8)).tobytes() for y in range(0, 144, 8) for x in range(0, 160, 8)})
        assert tile_count < 192, (room['name'], tile_count)
        assert len(attributes) == 360 and set(attributes) <= set(range(6))
        assert expanded(compressed(attributes)) == attributes
        assert expanded(compressed(grid)) == grid
        path = ROOT / f'assets/backgrounds/room_{n:02d}.png'
        image.save(path, optimize=False)
        sid, bgid = resources(room, attributes, grid)
        shown = native_color(image, attributes, room['zone'])
        bx, by = (n - 1) % 4 * 320, (n - 1) // 4 * 320
        montage.paste(shown.resize((320, 288), Image.Resampling.NEAREST), (bx, by + 24))
        md.text((bx + 8, by + 6), f'{n:02d} {room["name"]} / {room["objective"].upper()}', fill='#F3EEDC')
        item = {'room': n, 'name': room['name'], 'scene_id': sid, 'background_id': bgid,
                'scene_symbol': room['scene_symbol'], 'unique_tiles': tile_count, 'palette_slots': sorted(set(attributes)),
                'png_sha256': sha256(path.read_bytes()).hexdigest(), 'collision_sha256': sha256(bytes(grid)).hexdigest(),
                'attributes_sha256': sha256(bytes(attributes)).hexdigest(), 'route_check': route}
        receipt['rooms'].append(item)
        print(f'{n:02d} {room["name"]}: {tile_count} tiles, routes clear, scene={sid}')
    montage.save(ROOT / 'campaign/room-montage.png', optimize=False)
    receipt['montage_sha256'] = sha256((ROOT / 'campaign/room-montage.png').read_bytes()).hexdigest()
    write_json(ROOT / 'campaign/ART-RECEIPTS.json', receipt)


if __name__ == '__main__':
    main()

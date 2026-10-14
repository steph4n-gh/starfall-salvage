#!/usr/bin/env python3
"""Stage one native scrolling room without mutating active assets/resources.

Original deterministic four-shade pixels, GB Studio-native resource schema and
explicit collision geometry. Coordinates in the manifest are actual integer
actor centers; anchors are derived from the compiler's subpixel bounds math.
No imports into the active project, compiler, browser or hardware operation.
"""
from collections import deque
from copy import deepcopy
from hashlib import sha256
from itertools import groupby
from pathlib import Path
from uuid import UUID, uuid5
import json
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
STAGE = ROOT / 'campaign/scrolling-proof-assets'
MANIFEST = ROOT / 'campaign/scrolling-proof.json'
NAMESPACE = UUID('6aa66586-d5c6-5e08-99b8-4ab16d8907c6')
SHADES = ['071821', '306850', '86c06c', 'E0F8CF']
C = [tuple(bytes.fromhex(v)) for v in SHADES]
PALETTE_IDS = ['c8ef798d-bf6d-5079-8ce3-5901844534d7', 'default-bg-3', 'default-bg-3',
               'default-bg-4', 'default-bg-5', 'default-bg-6', 'default-bg-1', 'default-ui']


def ident(label):
    return str(uuid5(NAMESPACE, label))


def compressed(values):
    return ''.join(f'{v:02x}' + ('!' if len(run) == 1 else f'{len(run):x}+')
                   for v, group in groupby(values) for run in [list(group)])


def expanded(data):
    out, i = [], 0
    while i < len(data):
        v = int(data[i:i+2], 16); i += 2
        if data[i] == '!':
            count = 1; i += 1
        else:
            end = data.index('+', i); count = int(data[i:end], 16); i = end + 1
        out.extend([v] * count)
    return out


def write_json(relative, value):
    path = STAGE / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')
    return path


def sprite_bounds(sprite):
    # Matches generateGBVMData.ts compileBounds() exactly.
    return {
        'left': sprite['boundsX'] * 32,
        'right': (sprite['boundsX'] + sprite['boundsWidth']) * 32 - 1,
        'top': sprite['boundsY'] * 32,
        'bottom': (sprite['boundsY'] + sprite['boundsHeight']) * 32 - 1,
    }


def anchor_for_center(center, sprite):
    b = sprite_bounds(sprite)
    offsets = ((b['left'] + b['right']) >> 1, (b['top'] + b['bottom']) >> 1)
    # Each desired integer center is the floor of (anchor*32 + offset)/32.
    anchors = [center[i] - (offsets[i] // 32) for i in (0, 1)]
    actual = [(anchors[i] * 32 + offsets[i]) >> 5 for i in (0, 1)]
    assert actual == center, (anchors, actual, center)
    return anchors, b


def collision_grid(room):
    w, h = room['width'], room['height']
    grid = [0] * (w * h)
    for y in range(h):
        for x in range(w):
            if x in (0, w - 1) or y < 3 or y == h - 1:
                grid[y * w + x] = 15
    for x, y, tw, th in room['covers']:
        assert 1 <= x < x + tw <= w - 1 and 3 <= y < y + th <= h - 1
        assert tw >= 2 and th >= 2
        for ty in range(y, y + th):
            for tx in range(x, x + tw):
                grid[ty * w + tx] = 15
    return grid


def routes(room, grid, astronaut):
    w, h = room['width'], room['height']
    b = sprite_bounds(astronaut)
    _, bounds = anchor_for_center(room['spawn'], astronaut)
    offset_x = ((bounds['left'] + bounds['right']) >> 1) // 32
    offset_y = ((bounds['top'] + bounds['bottom']) >> 1) // 32
    footprints = {
        'actual16x8': (b['left'] // 32 - offset_x, b['top'] // 32 - offset_y,
                        b['right'] // 32 - offset_x, b['bottom'] // 32 - offset_y),
        'conservative16x16': (-7, -7, 8, 8),
        'visual16x16': (-7, -11, 8, 4),
    }
    def allowed(center, footprint):
        x, y = center
        left, top, right, bottom = x + footprint[0], y + footprint[1], x + footprint[2], y + footprint[3]
        if left < 0 or top < 0 or right >= w * 8 or bottom >= h * 8: return False
        return all(grid[ty * w + tx] == 0 for ty in range(top // 8, bottom // 8 + 1)
                   for tx in range(left // 8, right // 8 + 1))
    # All proof routes fit all three footprints, so the actual feet can never
    # require a visually tight/head-clipping route to satisfy the objective.
    def free(center):
        return all(allowed(center, footprint) for footprint in footprints.values())
    all_centers = [room['spawn']] + room['cells'] + [room['terminal']]
    for center in all_centers: assert free(tuple(center)), ('blocked center', center)
    queue, parents = deque([tuple(room['spawn'])]), {tuple(room['spawn']): None}
    while queue:
        x, y = queue.popleft()
        for point in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if point not in parents and free(point):
                parents[point] = (x, y); queue.append(point)
    assert all(tuple(p) in parents for p in all_centers)
    def bfs_path(start, goal):
        queue, previous = deque([tuple(start)]), {tuple(start): None}
        dest = tuple(goal)
        while dest not in previous:
            assert queue, ('unreachable route', start, goal)
            x, y = queue.popleft()
            for point in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if point not in previous and free(point):
                    previous[point] = (x, y); queue.append(point)
        path, cursor = [], dest
        while cursor is not None:
            path.append(cursor); cursor = previous[cursor]
        path.reverse()
        turns = [path[0]]
        for i in range(1, len(path) - 1):
            before = (path[i][0] - path[i-1][0], path[i][1] - path[i-1][1])
            after = (path[i+1][0] - path[i][0], path[i+1][1] - path[i][1])
            if before != after: turns.append(path[i])
        if path[-1] != turns[-1]: turns.append(path[-1])
        return {'from': list(start), 'to': list(goal), 'length_pixels': len(path) - 1,
                'waypoints': [list(p) for p in turns]}, path
    output, display_paths = [], []
    for start, goal in zip(all_centers, all_centers[1:]):
        item, path = bfs_path(start, goal); output.append(item); display_paths.append(path)
    dx, dy, dw, dh = room['dock_rect']
    assert all(grid[y * w + x] == 0 for y in range(dy // 8, (dy + dh - 1) // 8 + 1)
               for x in range(dx // 8, (dx + dw - 1) // 8 + 1))
    for goal in room['cells']:
        gx, gy = goal
        assert all(grid[y * w + x] == 0 for y in range((gy - 8) // 8, (gy + 7) // 8 + 1)
                   for x in range((gx - 8) // 8, (gx + 7) // 8 + 1)), ('pad over cover', goal)
    nx, ny = room['drone']
    assert all(grid[y * w + x] == 0 for y in range((ny - 6) // 8, (ny + 6) // 8 + 1)
               for x in range((nx - 6) // 8, (nx + 6) // 8 + 1))
    centered_routes, centered_paths = [], []
    for i, waypoints in enumerate(room['route_waypoints']):
        assert waypoints[0] == all_centers[i] and waypoints[-1] == all_centers[i + 1]
        path = [tuple(waypoints[0])]
        for a, b in zip(waypoints, waypoints[1:]):
            assert a[0] == b[0] or a[1] == b[1], ('non-axis route', a, b)
            dx = (b[0] > a[0]) - (b[0] < a[0]); dy = (b[1] > a[1]) - (b[1] < a[1])
            cursor = tuple(a)
            while cursor != tuple(b):
                cursor = (cursor[0] + dx, cursor[1] + dy)
                assert free(cursor), ('centerline route blocked', cursor)
                path.append(cursor)
        centered_routes.append({'from': waypoints[0], 'to': waypoints[-1], 'waypoints': waypoints,
                                'length_pixels': len(path) - 1})
        centered_paths.append(path)
    return {'footprints': footprints, 'reachable_centers': len(parents), 'all_objectives_reachable': True,
            'dock_clear': True, 'drone_spawn_clear': True, 'hazard': 'none', 'ordered_routes': output,
            'total_ordered_route_pixels': sum(r['length_pixels'] for r in output),
            'centerline_playtest_routes': centered_routes,
            'total_centerline_route_pixels': sum(r['length_pixels'] for r in centered_routes)}, centered_paths


class Art:
    def __init__(self, room):
        self.room = room
        self.w, self.h = room['width'], room['height']
        self.image = Image.new('RGB', (self.w * 8, self.h * 8), C[0])
        self.draw = ImageDraw.Draw(self.image)
        self.attributes = [0] * (self.w * self.h)

    def rect(self, xy, fill=None, outline=None):
        self.draw.rectangle(xy, fill=C[fill] if fill is not None else None,
                            outline=C[outline] if outline is not None else None)
    def line(self, xy, c, width=1): self.draw.line(xy, fill=C[c], width=width)
    def point(self, xy, c): self.draw.point(xy, fill=C[c])
    def region(self, x, y, w, h, palette):
        for ty in range(y, y + h):
            for tx in range(x, x + w):
                assert 0 <= tx < self.w and 0 <= ty < self.h
                self.attributes[ty * self.w + tx] = palette

    def base(self):
        for ty in range(3, self.h - 1):
            for tx in range(1, self.w - 1):
                x, y = tx * 8, ty * 8
                self.rect((x, y, x + 7, y + 7), 1)
                self.line((x, y + 7, x + 7, y + 7), 0)
                if (tx + ty) % 5 == 0: self.point((x + 1, y + 1), 2)
                if tx % 4 == 0: self.line((x + 7, y + 2, x + 7, y + 5), 0)
        # Repeated load-bearing ribs, never visually painted into walkable floor.
        for ty in range(3, self.h):
            for tx in (0, self.w - 1):
                x, y = tx * 8, ty * 8
                self.rect((x, y, x + 7, y + 7), 0)
                self.rect((x + 1, y + 1, x + 6, y + 6), 1)
                self.line((x + 1, y + 1, x + 6, y + 1), 2)
                self.point((x + 3, y + 4), 0)
        for ty in (0, 1, 2, self.h - 1):
            for tx in range(1, self.w - 1):
                x, y = tx * 8, ty * 8
                self.rect((x, y, x + 7, y + 7), 0)
                self.rect((x + 1, y + 1, x + 6, y + 5), 1)
                self.line((x + 1, y + 1, x + 6, y + 1), 2)
                self.point((x + 3, y + 3), 0)
        for x in range(16, self.w * 8 - 24, 32):
            self.rect((x, 8, x + 23, 23), 0, 2)
            self.line((x + 12, 10, x + 12, 21), 1)
            for px, py, color in ((4, 12, 3), (17, 17, 2), (8, 20, 2), (20, 10, 3)):
                self.point((x + px, py), color)
            self.region(x // 8, 1, 3, 2, 2)

    def cover(self, tx, ty, tw, th):
        # Tiled face units keep even large machines below the tile budget.
        self.region(tx, ty, tw, th, 3)
        for oy in range(th):
            for ox in range(tw):
                x, y = (tx + ox) * 8, (ty + oy) * 8
                self.rect((x, y, x + 7, y + 7), 1)
                if oy == 0:
                    self.line((x, y, x + 7, y), 0)
                    self.line((x, y + 1, x + 7, y + 1), 3)
                    self.line((x, y + 2, x + 7, y + 2), 2)
                if ox == 0: self.line((x, y, x, y + 7), 0)
                if ox == tw - 1: self.line((x + 7, y, x + 7, y + 7), 0)
                if oy == th - 1:
                    self.rect((x, y + 4, x + 7, y + 7), 0)
                    self.line((x + 1, y + 5, x + 6, y + 5), 1)
                    self.point((x + 2, y + 5), 2)
                else:
                    self.line((x + 2, y + 4, x + 5, y + 4), 0)
                    self.point((x + 2, y + 3), 2)

    def channel(self, points):
        # Flush cable traces deliberately lack a raised face/contact shadow.
        self.line(points, 0, 3); self.line(points, 2, 1)

    def pad(self, cx, cy):
        x, y = cx - 8, cy - 8
        self.region(x // 8, y // 8, 2, 2, 2)
        self.rect((x, y, x + 15, y + 15), 0)
        self.rect((x + 2, y + 2, x + 13, y + 13), 1)
        self.rect((x + 4, y + 4, x + 11, y + 11), outline=2)
        for ax, ay, bx, by in [(0,0,4,0),(0,0,0,4),(11,0,15,0),(15,0,15,4),
                               (0,15,4,15),(0,11,0,15),(11,15,15,15),(15,11,15,15)]:
            self.line((x + ax, y + ay, x + bx, y + by), 2)
        self.point((x + 2, y + 2), 3); self.point((x + 13, y + 13), 3)

    def landmarks(self):
        # Three readable chamber identities; no solid-looking unattached props.
        # Far east: recessed telemetry comb under the collectible bracket.
        self.region(36, 4, 9, 6, 4)
        for x in range(288, 360, 8):
            self.rect((x, 32, x + 7, 47), 0)
            self.line((x + 2, 35, x + 2, 44), 2)
            self.line((x + 3, 38, x + 5, 38), 1)
            self.point((x + 2, 35), 3)
        self.rect((296, 64, 351, 79), 0, 1)
        for x in range(300, 350, 8): self.line((x, 68, x + 3, 68), 2)
        # Central induction junction is thin floor inlay, not a cover island.
        self.region(23, 15, 4, 5, 4)
        self.rect((184, 120, 215, 159), 0)
        self.draw.ellipse((186, 122, 213, 157), outline=C[2])
        self.draw.ellipse((191, 129, 208, 152), outline=C[1])
        self.line((188, 140, 211, 140), 3)
        self.channel([(216, 144), (232, 144), (232, 200)])
        # Lower east freight turntable and repeated docking arrows.
        self.region(38, 29, 6, 6, 4)
        self.rect((304, 232, 351, 279), 0)
        ring = [(314,234),(341,234),(349,242),(349,268),(341,277),(314,277),(306,268),(306,242),(314,234)]
        self.line(ring, 2)
        self.line((308, 244, 347, 244), 1); self.line((308, 267, 347, 267), 1)
        for x in range(312, 345, 8): self.line([(x-2,272),(x,274),(x+2,272)], 2)
        # Repeat recessed direction plaques; they are low-value floor marks.
        for x, y in ((40,184),(112,136),(176,208),(320,112),(320,200)):
            self.rect((x, y, x + 15, y + 7), 0)
            self.line([(x+3,y+2),(x+7,y+4),(x+3,y+6)], 1)
            self.line((x+9,y+4,x+12,y+4), 2)
        # Left return wing has a quiet freight rail, giving camera travel texture.
        for y in range(32, 264, 8):
            self.rect((24, y, 31, y + 7), 0)
            self.line((25, y, 25, y + 7), 1)
            self.line((29, y, 29, y + 7), 1)
            self.line((26, y + 3, 28, y + 3), 2)

    def dock(self):
        x, y, w, h = self.room['dock_rect']
        self.region(x // 8, y // 8, w // 8, h // 8, 3)
        self.rect((x, y, x + w - 1, y + h - 1), 0)
        self.rect((x + 1, y + 1, x + w - 2, y + h - 2), outline=2)
        self.rect((x + 4, y + 4, x + w - 5, y + h - 4), 1)
        self.line((x + 4, y + 4, x + w - 5, y + 4), 3)
        for xx in range(x + 8, x + w - 6, 8):
            for yy in (y + 8, y + 32):
                self.line([(xx-2,yy),(xx,yy+2),(xx+2,yy)], 2)
        self.line((x + 8, y + h - 2, x + w - 9, y + h - 2), 3)

    def finish(self):
        self.base(); self.landmarks()
        for cover in self.room['covers']: self.cover(*cover)
        for center in self.room['cells']: self.pad(*center)
        self.dock()
        return self.image, self.attributes


def resources(room, attributes, grid, sprites):
    original = ROOT / 'project/scenes/start'
    sid, bgid = ident('scene-proof-room-01'), ident('background-proof-room-01')
    write_json('assets/backgrounds/proof_room_01.png.gbsres', {
        '_resourceType': 'background', 'id': bgid, 'name': 'Freight Spine Proof',
        'symbol': 'bg_proof_room_01', 'filename': 'proof_room_01.png',
        'width': room['width'], 'height': room['height'],
        'imageWidth': room['width'] * 8, 'imageHeight': room['height'] * 8,
        'autoColor': False, 'tileColors': compressed(attributes),
    })
    scene = json.loads((original / 'scene.gbsres').read_text())
    scene.update(id=sid, _index=100, name='Freight Spine Proof', symbol=room['scene_symbol'],
                 x=1200, y=0, width=room['width'], height=room['height'], backgroundId=bgid,
                 paletteIds=PALETTE_IDS, collisions=compressed(grid), script=[])
    write_json('project/scenes/proof_room_01/scene.gbsres', scene)
    originals = sorted((json.loads(p.read_text()) for p in (original/'actors').glob('*.gbsres')),
                       key=lambda actor: actor['_index'])
    centers = room['cells'] + [room['terminal'], room['drone'], room['spawn']]
    actor_receipts = []
    for actor, center in zip(originals, centers):
        sprite = sprites[actor['spriteSheetId']]
        anchor, bounds = anchor_for_center(center, sprite)
        index = actor['_index']
        actor.update(id=ident(f'actor-proof-{index}'), symbol=f'actor_proof_01_{index}',
                     coordinateType='pixels', x=anchor[0], y=anchor[1])
        write_json(f'project/scenes/proof_room_01/actors/actor_{index}.gbsres', actor)
        actor_receipts.append({'runtime_index': index + 1, 'id': actor['id'], 'sprite_id': sprite['id'],
                               'center_pixels': center, 'anchor_pixels': anchor, 'bounds_subpixels': bounds,
                               'palette_id': actor['paletteId']})
    spawn_anchor, player_bounds = anchor_for_center(room['spawn'], sprites['player'])
    return {'scene_id': sid, 'background_id': bgid, 'scene_symbol': room['scene_symbol'],
            'player_center_pixels': room['spawn'], 'player_anchor_pixels': spawn_anchor,
            'player_bounds_subpixels': player_bounds, 'actors': actor_receipts}


def main():
    room = json.loads(MANIFEST.read_text())
    assert room['width'] == 48 and room['height'] == 40 and room['hazard'] == 'none'
    sprites = {resource['id']: resource for resource in
               (json.loads(p.read_text()) for p in (ROOT/'assets/sprites').glob('*.gbsres'))}
    sprites['player'] = json.loads((ROOT/'assets/sprites/astronaut.png.gbsres').read_text())
    grid = collision_grid(room)
    route_receipt, paths = routes(room, grid, sprites['player'])
    image, attrs = Art(room).finish()
    assert set(image.get_flattened_data()) <= set(C)
    tile_count = len({image.crop((x,y,x+8,y+8)).tobytes() for y in range(0,image.height,8) for x in range(0,image.width,8)})
    assert tile_count < 192, tile_count
    assert len(grid) == len(attrs) == 1920 and set(attrs) <= set(range(6))
    assert expanded(compressed(grid)) == grid and expanded(compressed(attrs)) == attrs
    path = STAGE/'assets/backgrounds/proof_room_01.png'
    path.parent.mkdir(parents=True,exist_ok=True); image.save(path, optimize=False)
    resource_receipt = resources(room, attrs, grid, sprites)
    palettes = {p['id']:p['colors'] for p in
                (json.loads(path.read_text()) for path in (ROOT/'project/palettes').glob('*.gbsres'))}
    color = Image.new('RGB',image.size)
    for y in range(image.height):
        for x in range(image.width):
            shade = C.index(image.getpixel((x,y)))
            rgb = tuple(bytes.fromhex(palettes[PALETTE_IDS[attrs[(y//8)*room['width']+x//8]]][3-shade]))
            color.putpixel((x,y),tuple(round((v>>3)*255/31) for v in rgb))
    color.save(STAGE/'color-preview.png', optimize=False)
    overlay = color.copy(); draw = ImageDraw.Draw(overlay)
    for x,y,w,h in room['covers']:
        draw.rectangle((x*8,y*8,(x+w)*8-1,(y+h)*8-1), outline='#EF6159')
    for i, path in enumerate(paths):
        draw.line(path, fill=['#FFD767','#60FFD1','#95B9FF','#FF9FE5'][i], width=1)
    overlay.save(STAGE/'collision-routes.png', optimize=False)
    receipt = {
        'scope':'Staged source assets only; not imported, built, emulated, or hardware tested',
        'manifest_sha256':sha256(MANIFEST.read_bytes()).hexdigest(),
        'generator_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
        'source_shades':['#'+s.lower() for s in SHADES], 'dimensions_pixels':[384,320],
        'dimensions_tiles':[48,40], 'unique_tiles':tile_count, 'palette_slots':sorted(set(attrs)),
        'reserved_palette_slots':[6,7], 'palette_ids':PALETTE_IDS,
        'png_sha256':sha256((STAGE/'assets/backgrounds/proof_room_01.png').read_bytes()).hexdigest(),
        'collision_sha256':sha256(bytes(grid)).hexdigest(), 'attributes_sha256':sha256(bytes(attrs)).hexdigest(),
        'native_rle_round_trip':True, 'geometry_matches_manifest':True,
        'resources':resource_receipt,'routes':route_receipt,
    }
    write_json('PROOF-ART-RECEIPTS.json',receipt)
    print(json.dumps({'unique_tiles':tile_count,'scene_id':resource_receipt['scene_id'],
                      'player_anchor':resource_receipt['player_anchor_pixels'],
                      'route_pixels':route_receipt['total_ordered_route_pixels'],
                      'routes':route_receipt['centerline_playtest_routes']},indent=2))


if __name__=='__main__': main()

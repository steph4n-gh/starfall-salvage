#!/usr/bin/env python3
"""Author twelve staged Star Engine rooms, preserving the active game.

Only mission-16..18 manifests and campaign/zone-06-assets are written. Exact
native source shades, resource bounds, RLE and reachability reuse the qualified
local helpers; new geometry, palettes and floor machinery are authored here.
"""
from hashlib import sha256
from pathlib import Path
from uuid import UUID, uuid5
import json
from PIL import Image, ImageDraw
import scrolling_proof_art as proof
import mission_art as common
import zone_art as resources

ROOT = Path(__file__).resolve().parent
STAGE = ROOT / 'campaign/zone-06-assets'
NS = UUID('ee8fe3aa-a741-5bc5-a059-419098eaef14')
C = proof.C
PALETTE_IDS = [str(uuid5(NS,f'background-slot-{i}')) for i in range(7)] + ['default-ui']
# Ordered lightest to darkest, as the native palette resource expects.
COLORS = [
    ['D8E8F8','586888','182030','080810'],
    ['C0D0F0','485068','202838','080810'],
    ['F8F0C8','C89040','584028','101018'],
    ['F8D8A8','987048','403028','100C18'],
    ['F0D0F0','A070B8','483060','100C20'],
    ['D0F8F0','58A0A0','204048','080C18'],
    ['102038','407888','184050','000000'],
]


def room(name, objective, enemy, covers, cells, drone, kind, brief1, brief2,
         hazard='none', hazard_rect=(0,0,0,0), dash=20, warning=48,
         recovery=100, speed=60, cache=None, **details):
    result = dict(name=name,width=48,height=40,zone=5,objective=objective,
        enemy=enemy,hazard=hazard,hazard_rect=list(hazard_rect),spawn=[48,296],
        terminal=[48,296],dock_rect=[24,272,48,40],covers=covers,cells=cells,
        drone=drone,art_kind=kind,brief1=brief1,brief2=brief2,
        warning_frames=warning,dash_frames=dash,recover_frames=recovery,
        speed=speed,hold_ticks=45,optional_cache_marker=cache,
        coordinate_convention={
            'spawn_terminal_cells_drone':'Integer native actor_x/actor_y pixel centers',
            'escort_route':'Integer crew centers; generator derives native anchors',
            'covers_hazard_rect':'Tile x,y,width,height rectangles',
            'dock_rect_enemy_bounds':'Pixel x,y,width,height rectangles'},
        enemy_bounds=[80,48,272,232])
    result.update(details)
    return result


def manifests():
    missions = {
      16: ('IGNITION TRAIL', [
        room('FUSION APPROACH','salvage','charger',
            [[9,7,4,17],[21,5,4,10],[21,20,4,11],[33,9,5,17],
             [3,31,8,2],[13,29,4,6],[39,30,5,5]],
            [[152,64],[296,56],[336,224]],[232,160],'fusion_approach',
            'THREE IGNITION CELLS','WEAVE THE HEAT FINS',
            hazard='vent',hazard_rect=[26,25,2,2],dash=18,
            tactical_goal='Choose the left service loop or the two breaks in the long heat-fin walls; the final cell requires crossing into the far-right return aisle.'),
        room('LENS GALLERY','repair','sweeper',
            [[15,8,17,3],[9,16,3,10],[20,17,11,3],[34,18,3,13],
             [17,28,11,3],[5,5,3,3],[39,5,4,5]],
            [[80,64],[304,128],[208,272]],[248,120],'lens_gallery',
            'REPAIR THREE LENSES','BRAKE BEHIND THE FIN',
            hazard='laser',hazard_rect=[16,24,12,1],dash=24,cache=[360,56],
            tactical_goal='Any-order repair around the central optical bench. The low laser splits the lower return route while the sweeper commits to one axis.'),
        room('COOLANT THROAT','relay','hunter',
            [[7,8,23,3],[19,16,23,3],[7,24,23,3],[19,32,21,3],
             [5,13,3,6],[39,22,4,5]],
            [[328,64],[96,176],[328,240]],[288,176],'coolant_throat',
            'HOLD B AT LIT VALVE','BRAKE AT BAFFLE ENDS',
            hazard='vent',hazard_rect=[15,19,2,2],dash=18,warning=50,
            tactical_goal='Ordered valves alternate sides of three offset cooling baffles, making each turn and safe braking pocket matter.'),
        room('IGNITION WARDEN','core','charger',
            [[16,9,5,8],[30,9,5,8],[22,19,7,4],[8,22,4,9],
             [37,23,5,9],[18,32,12,3],[5,5,4,3]],
            [[264,56],[112,176],[336,280]],[248,152],'ignition_warden',
            'THREE OPENING HITS','BAIT THE WARDEN WIDE',
            hazard='laser',hazard_rect=[22,27,12,1],dash=20,
            warning=52,recovery=108,speed=62,
            tactical_goal='The guardian can be approached through either of two wide lens gaps. Leave its amber line, turn back during cyan recovery, then extract released cores.'),
      ]),
      17: ('LAST SIGNAL', [
        room('ANTENNA ROOT','relay','sweeper',
            [[12,6,3,14],[24,5,3,8],[24,19,3,13],[36,9,3,17],
             [5,25,12,3],[30,31,10,3]],
            [[72,64],[328,96],[168,256]],[328,176],'antenna_root',
            'LINK THREE BEACONS','CUT ACROSS THE RIBS',
            hazard='laser',hazard_rect=[16,22,8,1],dash=24,warning=48,
            tactical_goal='Three beacon links pull the pilot from the outer rim into the center. Tall aerial ribs stop sweeper dashes and offer deliberate turning shelter.'),
        room('HELIOS CONTROL','repair','charger',
            [[9,9,11,3],[27,7,3,12],[14,18,11,3],[34,24,8,3],
             [17,29,3,7],[4,19,3,7],[37,6,5,4]],
            [[96,56],[320,168],[240,272]],[256,128],'helios_control',
            'RESTORE THE STAR BUS','B45 REPAIR ANY ORDER',
            hazard='vent',hazard_rect=[27,25,2,2],dash=18,warning=50,
            cache=[352,56],
            tactical_goal='Repair points occupy three different branches of the control bus, so choosing the first station changes which cover line the charger can use.'),
        room('LIFELINE GANTRY','escort','hunter',
            [[15,28,7,3],[30,16,5,7],[17,8,7,3],[7,13,8,3],
             [21,20,10,3],[18,37,6,2],[37,31,8,4],[2,19,4,6]],
            [[208,224],[304,104],[336,56]],[304,152],'lifeline_gantry',
            'STAY NEAR THE CREW','ESCORT TO THE DOCK',
            hazard='laser',hazard_rect=[28,14,10,1],dash=22,warning=54,
            escort_start=[96,280],
            escort_route=[[96,280],[208,280],[208,224],[304,224],[304,104],
                          [336,104],[336,56],[224,56],[224,144],[144,144],
                          [144,208],[80,208],[80,264],[48,264],[48,296]],
            tactical_goal='Keep within 24 pixels of the real crew while guiding them around the three physical catwalk banks. Step away to stop them before an active beam, then regroup.',
            hazard_route_note='The crew crosses the narrow beam twice. Moving more than 24px from the crew stops them, so its 120-safe/45-warning cycle can be waited out. Repair-first disables this beam.'),
        room('CORONA SENTINEL','core','sweeper',
            [[13,7,3,10],[21,13,12,3],[8,23,16,3],[32,24,3,11],
             [37,8,4,9],[17,32,8,3],[4,11,4,5]],
            [[248,64],[112,160],[328,272]],[264,176],'corona_sentinel',
            'READ THE AXIS LOCK','THREE CYAN PULSES',
            hazard='vent',hazard_rect=[27,25,2,2],dash=24,
            warning=54,recovery=112,speed=64,
            tactical_goal='A long horizontal conductor and offset vertical shields create two broad escape routes; the guardian commits to a horizontal or vertical charge before each opening.'),
      ]),
      18: ('STARFALL HEART', [
        room('EVENT SPINE','salvage','hunter',
            [[7,7,12,3],[25,7,14,3],[16,15,5,11],[31,17,5,7],
             [5,28,12,3],[24,31,15,3],[40,13,3,14]],
            [[80,40],[280,120],[328,288]],[280,208],'event_spine',
            'RECOVER THREE KEYS','HUNTER USES THE GAPS',
            hazard='laser',hazard_rect=[23,23,8,1],dash=20,warning=50,
            tactical_goal='A broad center route branches into three salvage pockets. The hunter follows around baffle corners during recovery, so staying behind one cover is insufficient.'),
        room('ENGINE BALANCE','repair','charger',
            [[12,5,4,14],[26,10,3,16],[34,27,8,3],[8,27,14,3],
             [34,5,6,4],[5,14,3,8],[17,21,5,3]],
            [[80,64],[304,168],[184,272]],[248,128],'engine_balance',
            'BALANCE THREE COILS','REPAIR IN YOUR ORDER',
            hazard='vent',hazard_rect=[20,16,2,2],dash=22,warning=54,
            cache=[344,72],
            tactical_goal='Three coil banks provide separate turning refuges. Repairing in any order makes the central vent an optional shortcut rather than a compulsory damage gate.'),
        room('CROWN NETWORK','relay','sweeper',
            [[9,8,5,12],[20,5,17,3],[24,14,4,13],[7,25,13,3],
             [33,21,9,3],[20,32,15,3],[39,9,4,5]],
            [[72,48],[312,136],[168,240]],[312,208],'crown_network',
            'LINK THE CROWN NODES','USE THE AXIS SHELTER',
            hazard='laser',hazard_rect=[15,18,9,1],dash=24,warning=52,
            tactical_goal='Ordered links sweep from the top-left service bay through the east gallery into a low center pocket. The beam crosses one direct route, with a wide bypass below.'),
        room('STAR ENGINE HEART','core','charger',
            [[15,8,4,8],[30,8,4,8],[22,19,5,7],[6,24,9,3],
             [34,25,8,3],[18,32,13,3],[4,10,4,8],[39,11,4,8]],
            [[240,48],[104,176],[320,280]],[232,144],'star_engine_heart',
            'PULSE THREE OPENINGS','BRING THE HEART HOME',
            hazard='laser',hazard_rect=[19,28,14,1],dash=24,
            warning=56,recovery=120,speed=64,
            tactical_goal='The final guardian sits between a split crown and a central keel. Wide outer loops leave room to drift, evade its committed line, and brake for one precise opening hit.'),
      ]),
    }
    result = {}
    for number,(name,rooms) in missions.items():
        for index,item in enumerate(rooms):
            item['room']=index;item['scene_symbol']=f'scene_mission_{number:02d}_room_{index:02d}'
        result[number]={'mission':number-1,'name':name,'zone':5,'room_count':4,
            'graph':{'entry':0,'middle_choices':[1,2], 'middle_rule':'Visit both in either order','final':3},
            'implementation_scope':'Authored native geometry and existing salvage/relay/repair/escort/core mechanics only; staged assets, not native gameplay verification.',
            'rooms':rooms}
    return result


class EngineArt(common.MissionArt):
    def base(self):
        proof.Art.base(self)
        role=self.room['room']; mission=self.room['mission_number']
        for ty in range(3,self.h-1):
            for tx in range(1,self.w-1):
                x,y=tx*8,ty*8;self.rect((x,y,x+7,y+7),1)
                if role==0:
                    if tx%4==3:self.line((x+7,y,x+7,y+7),0)
                    if ty%4==3:self.line((x,y+7,x+7,y+7),0)
                    if (tx+ty)%4==0:self.line((x+2,y+2,x+3,y+2),2)
                elif role==1:
                    if ty%3==2:self.line((x,y+7,x+7,y+7),0)
                    if tx%3==2:self.line((x+7,y,x+7,y+7),0)
                    if tx%3==0 and ty%3==0:self.point((x+1,y+1),2)
                elif role==2:
                    if ty%2:self.line((x,y+7,x+7,y+7),0)
                    if tx%4==0:self.line((x+7,y+2,x+7,y+5),0)
                    if tx%4==2 and ty%2==0:self.point((x+5,y+2),2)
                else:
                    if tx%4==3:self.line((x+7,y,x+7,y+7),0)
                    if ty%4==3:self.line((x,y+7,x+7,y+7),0)
                    if ty%4==0:self.line((x+2,y+2,x+5,y+2),0)
                if mission==17 and tx%8==0 and ty%4==0:
                    self.point((x+2,y+5),2)

    def instrument(self,cx,cy,style=0):
        x,y=cx-24,cy-8
        self.region(x//8,y//8,6,2,4);self.rect((x,y,x+47,y+15),0)
        for xx in range(x+2,x+45,8):
            self.rect((xx,y+2,xx+5,y+12),outline=1)
            self.line((xx+2,y+4,xx+2,y+9),2)
            self.point((xx+2,y+4+style%3),3)

    def star(self,cx,cy,size=64):
        # A flush eight-point field glyph, with no raised blocker face.
        x,y=cx-size//2,cy-size//2
        self.region(x//8,y//8,size//8,size//8,4);self.rect((x,y,x+size-1,y+size-1),0)
        for radius,color in ((size//2-4,2),(size//2-12,1)):
            points=[(cx,cy-radius),(cx+8,cy-8),(cx+radius,cy),
                    (cx+8,cy+8),(cx,cy+radius),(cx-8,cy+8),
                    (cx-radius,cy),(cx-8,cy-8),(cx,cy-radius)]
            self.line(points,color)
        self.rect((cx-3,cy-3,cx+3,cy+3),outline=3)

    def rail(self,points):
        self.channel(points)
        for x,y in points:
            self.rect((x-2,y-2,x+2,y+2),0,2)

    def landmarks(self):
        kind=self.room['art_kind']
        if kind=='fusion_approach':
            for x in (120,256):
                for y in range(32,288,8):
                    self.rect((x,y,x+7,y+7),0);self.line((x+2,y,x+2,y+7),2)
                    self.line((x+5,y,x+5,y+7),1)
            self.instrument(152,40);self.instrument(296,40,1)
        elif kind=='lens_gallery':
            self.star(216,136,64)
            for cx,cy in self.room['cells']:self.rail([(cx,cy),(cx,cy-24)])
            self.instrument(80,40);self.instrument(304,112,1)
        elif kind=='coolant_throat':
            for x,y,w,h in self.room['covers'][:4]:
                self.rail([(x*8-8,y*8-8),((x+w)*8+8,y*8-8)])
            self.instrument(96,152);self.instrument(328,216,2)
        elif kind=='antenna_root':
            for cx,cy in self.room['cells']:
                self.rail([(cx,cy),(cx+16,cy),(cx+16,cy+24)])
            self.star(280,112,48)
        elif kind=='helios_control':
            for cx,cy in self.room['cells']:self.instrument(cx,cy-24,1)
            self.rail([(96,56),(120,56),(120,128),(224,128),(224,272),(240,272)])
        elif kind=='lifeline_gantry':
            for x,y in ((160,264),(288,200),(312,80),(208,120),(128,184),(64,240)):
                self.region(x//8,y//8,3,1,5);self.rect((x,y,x+23,y+7),0)
                for xx in (x+5,x+13):self.line([(xx-2,y+2),(xx,y+4),(xx-2,y+6)],2)
            self.instrument(304,80,2)
        elif kind=='event_spine':
            self.star(256,176,80)
            self.rail([(80,56),(104,56),(104,120),(144,120)])
            self.rail([(280,128),(368,128),(368,288),(328,288)])
        elif kind=='engine_balance':
            self.star(248,128,48)
            for cx,cy in self.room['cells']:self.instrument(cx,cy-24,2)
            self.rail([(80,64),(80,96),(184,96)])
        elif kind=='crown_network':
            self.rail([(72,56),(72,32),(184,32),(184,112),(312,112),(312,136)])
            self.rail([(168,240),(224,240),(224,288),(296,288)])
            self.instrument(312,112)
        else:
            cx,cy=self.room['drone'];cx=cx//8*8;cy=cy//8*8
            self.star(cx,cy,64 if kind!='star_engine_heart' else 80)
            for px,py in self.room['cells']:
                self.rail([(px,py),(px,py-24)])
            for x in (cx-24,cx+24):
                self.rect((x-4,cy-4,x+3,cy+3),0,2)
        # Gold recesses identify optional B20 cache locations; collision and
        # reward remain existing runtime behavior, not newly invented machinery.

    def pad(self,cx,cy):
        super().pad(cx,cy)
        if self.room['objective']=='relay':
            for n in range(self.room['cells'].index([cx,cy])+1):
                self.line((cx-4+n*3,cy+3,cx-4+n*3,cy+6),3)


def write_json(relative,value):
    path=STAGE/relative;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2)+'\n');return path


def main():
    authored=manifests()
    for number,manifest in authored.items():
        (ROOT/f'campaign/mission-{number:02d}.json').write_text(json.dumps(manifest,indent=2)+'\n')
    common.PALETTE_IDS=PALETTE_IDS
    resources.STAGE=STAGE;resources.PALETTE_IDS=PALETTE_IDS
    resources.NS={n:uuid5(NS,f'mission-{n}') for n in authored}
    sprites={r['id']:r for r in (json.loads(p.read_text()) for p in (ROOT/'assets/sprites').glob('*.gbsres'))}
    sprites['player']=json.loads((ROOT/'assets/sprites/astronaut.png.gbsres').read_text())
    palettes={}
    for slot,colors in enumerate(COLORS):
        ident=PALETTE_IDS[slot];palettes[ident]=colors
        write_json(f'project/palettes/zone06_slot_{slot}.gbsres',{'_resourceType':'palette',
            'id':ident,'name':f'Star Engine {slot+1}','colors':colors})
    receipts={'scope':'Twelve staged native Star Engine rooms; no active import/build/emulation/hardware.',
        'zone':5,'new_room_count':12,'source_shades_rgba':[list(c)+[255] for c in C],
        'generator_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
        'reused_helpers_sha256':{name:sha256((ROOT/name).read_bytes()).hexdigest() for name in
            ('mission_art.py','scrolling_proof_art.py','zone_art.py')},'palettes':COLORS,
        'hazard_phase_rgb555':common.HAZARD_RGB555,'missions':[]}
    fingerprints={}
    for path in sorted((ROOT/'campaign').glob('mission-*.json')):
        if path.stem in [f'mission-{n:02d}' for n in authored]:continue
        manifest=json.loads(path.read_text())
        for r in manifest.get('rooms',[]):
            key=resources.normalized_collision(proof.collision_grid(r))
            fingerprints.setdefault(key,[]).append(f'{path.name}:{r["room"]}')
    for number,manifest in authored.items():
        montage=Image.new('RGB',(768,680),'#0D0A1B');md=ImageDraw.Draw(montage)
        mission_receipt={'mission':number,'name':manifest['name'],'graph':manifest['graph'],
            'manifest_sha256':sha256((ROOT/f'campaign/mission-{number:02d}.json').read_bytes()).hexdigest(),'rooms':[]}
        for room in manifest['rooms']:
            room=dict(room,mission_number=number)
            n=room['room'];strings=common.verify_strings(room);grid=proof.collision_grid(room)
            assert room['warning_frames']>=42 and room['recover_frames']>=96 and room['speed']<=64
            assert 18<=room['dash_frames']<=24
            fingerprint=resources.normalized_collision(grid)
            assert fingerprint not in fingerprints,(room['name'],'mirrored/duplicate geometry',fingerprints.get(fingerprint))
            fingerprints[fingerprint]=[f'mission-{number:02d}.json:{n}']
            checks,paths=common.route_validation(room,grid,sprites['player'])
            image,attributes=EngineArt(room).finish()
            assert set(image.get_flattened_data())<=set(C)
            count=len({image.crop((x,y,x+8,y+8)).tobytes() for y in range(0,320,8) for x in range(0,384,8)})
            assert count<192,(room['name'],'tile budget',count)
            assert len(grid)==len(attributes)==1920 and set(attributes)<=set(range(7))
            assert proof.expanded(proof.compressed(grid))==grid and proof.expanded(proof.compressed(attributes))==attributes
            hx,hy,hw,hh=room['hazard_rect'];expected={y*48+x for y in range(hy,hy+hh) for x in range(hx,hx+hw)}
            assert hw*hh<=16 and {i for i,a in enumerate(attributes) if a==6}==expected
            png=STAGE/f'assets/backgrounds/mission_{number:02d}_room_{n:02d}.png'
            png.parent.mkdir(parents=True,exist_ok=True);rgba=image.convert('RGBA')
            assert set(rgba.get_flattened_data())<={c+(255,) for c in C};rgba.save(png,optimize=False)
            native=resources.native_resources(number,room,attributes,grid,sprites)
            assert native['native_index']==170+(number-16)*4+n
            previews={}
            for state in ('SAFE','AMBER','RED'):
                color=common.color_preview(image,attributes,palettes,state)
                path=STAGE/f'mission_{number:02d}_room_{n:02d}-{state.lower()}.png';color.save(path,optimize=False)
                previews[state]={'path':str(path.relative_to(ROOT)),'sha256':sha256(path.read_bytes()).hexdigest()}
                if state=='SAFE':
                    bx,by=(n%2)*384,(n//2)*340;montage.paste(color,(bx,by+20))
                    md.text((bx+8,by+4),f'{n+1} {room["name"]} / {room["objective"].upper()}',fill='#F0D8B0')
                    overlay=color.copy();draw=ImageDraw.Draw(overlay)
                    for x,y,w,h in room['covers']:draw.rectangle((x*8,y*8,(x+w)*8-1,(y+h)*8-1),outline='#F06570')
                    for i,path in enumerate(paths):draw.line(path,fill=['#FFE276','#70FFBE','#86BFFF','#E5A5FF'][i%4],width=1)
                    overlay.save(STAGE/f'mission_{number:02d}_room_{n:02d}-routes.png',optimize=False)
            checks['optional_cache']['implemented_gameplay']='Existing runtime B20 within12px; not native-playtested here.'
            mission_receipt['rooms'].append({'room':n,'name':room['name'],'objective':room['objective'],
                'enemy':room['enemy'],'dimensions_pixels':[384,320],'dimensions_tiles':[48,40],
                'mode':'RGBA','alpha':255,'unique_tiles':count,'palette_ids':PALETTE_IDS,
                'palette_slots':sorted(set(attributes)),'native_rle_roundtrip':True,
                'png_sha256':sha256(png.read_bytes()).hexdigest(),'collision_sha256':sha256(bytes(grid)).hexdigest(),
                'attribute_sha256':sha256(bytes(attributes)).hexdigest(),
                'mirror_normalized_collision_sha256':sha256(fingerprint).hexdigest(),
                'strings':strings,'resources':native,'static_checks':checks,'previews':previews,
                'tactical_goal':room['tactical_goal']})
            print(f'M{number:02d}R{n:02d} {room["name"]}: {count} tiles, {native["native_actor_count"]} actors, routes clear',flush=True)
        path=STAGE/f'mission-{number:02d}-montage.png';montage.save(path,optimize=False)
        mission_receipt['montage_sha256']=sha256(path.read_bytes()).hexdigest();receipts['missions'].append(mission_receipt)
    receipts['mirror_or_half_turn_duplicate_layouts']=False
    receipts['total_distinct_collision_fingerprints_compared']=len(fingerprints)
    write_json('ZONE-06-ART-RECEIPTS.json',receipts)


if __name__=='__main__':main()

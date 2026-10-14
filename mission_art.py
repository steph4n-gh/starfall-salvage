#!/usr/bin/env python3
"""Stage the first four-room native mission, preserving qualified active files.

Uses the verified source shades, compression and compiler-bound helpers from
scrolling_proof_art.py. Source PNGs are exact RGBA pixels with alpha255. The
six original actor slots are preserved; only Rescue Concourse adds actor7.
No active project import, compiler, emulator, browser or hardware operation.
"""
from collections import deque
from copy import deepcopy
from hashlib import sha256
from itertools import permutations
from pathlib import Path
from uuid import UUID, uuid5
import json
from PIL import Image, ImageDraw
import scrolling_proof_art as proof

ROOT = Path(__file__).resolve().parent
STAGE = ROOT / 'campaign/mission-01-assets'
MANIFEST = ROOT / 'campaign/mission-01.json'
NAMESPACE = UUID('316c486b-efec-575e-9f57-f573f0c58c25')
C = proof.C
HAZARD_ID = str(uuid5(NAMESPACE, 'palette-hazard'))
PALETTE_IDS = list(proof.PALETTE_IDS)
PALETTE_IDS[6] = HAZARD_ID
HAZARD_RGB555 = {
    'SAFE': [(2,4,7),(8,15,17),(3,8,10),(0,0,0)],
    'AMBER': [(2,4,7),(31,23,5),(3,8,10),(0,0,0)],
    'RED': [(2,4,7),(31,5,3),(3,8,10),(0,0,0)],
}
FONT_CHARS = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 :/-!.')


def ident(name): return str(uuid5(NAMESPACE,name))
def write_json(relative,value):
    path=STAGE/relative; path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2)+'\n'); return path


def verify_strings(room):
    result={}
    for field in ('name','brief1','brief2'):
        text=room[field]
        assert len(text)<=20 and set(text)<=FONT_CHARS,(field,text,len(text))
        result[field]={'text':text,'glyphs':len(text),'limit':20}
    return result


class MissionArt(proof.Art):
    def base(self):
        super().base()
        # Distinct floor construction in each working bay, still low contrast.
        kind=self.room['art_kind']
        for ty in range(3,self.h-1):
            for tx in range(1,self.w-1):
                x,y=tx*8,ty*8
                self.rect((x,y,x+7,y+7),1)
                if kind=='signal_works':
                    self.line((x,y+7,x+7,y+7),0)
                    if tx%4==0:self.line((x+7,y,x+7,y+7),0)
                    if (tx+ty)%4==0:self.point((x+1,y+1),2)
                elif kind=='rescue_concourse':
                    if ty%2==1:self.line((x,y+7,x+7,y+7),0)
                    if tx%4==0:self.line((x+7,y+1,x+7,y+6),0)
                    if tx%4==0 and ty%2==1:
                        self.point((x+5,y+5),2);self.point((x+5,y+3),0)
                else:
                    if ty%4==3:self.line((x,y+7,x+7,y+7),0)
                    if tx%4==3:self.line((x+7,y,x+7,y+7),0)
                    if tx%4==0 and ty%4==0:
                        self.line((x+1,y+1,x+3,y+1),2);self.line((x+1,y+1,x+1,y+3),2)

    def landmarks(self):
        kind=self.room['art_kind']
        if kind=='signal_works':
            # Recessed circuit trunks link the three instruments. Cable traces
            # never add collision or masquerade as raised crates.
            for points in (
                [(80,72),(112,72),(112,192),(208,192),(208,240)],
                [(304,128),(320,128),(320,208),(208,208),(208,240)],
                [(128,32),(128,88),(176,88)],
            ):self.channel(points)
            for x,y,tw,th in ((48,48,7,2),(288,104,7,2),(176,216,7,2)):
                self.region(x//8,y//8,tw,th,4)
                self.rect((x,y,x+tw*8-1,y+th*8-1),0)
                for xx in range(x+3,x+tw*8-3,8):
                    self.rect((xx,y+3,xx+4,y+11),1,2)
                    self.line((xx+2,y+5,xx+2,y+9),3)
            # Central switching field carries the palette6 vent separately.
            self.region(24,15,6,5,4)
            self.rect((192,120,239,159),0)
            for y in (124,156):self.line((196,y,235,y),1)
            for x in (196,232):self.line((x,124,x,156),2)
            self.line((200,128,227,128),3)
        elif kind=='rescue_concourse':
            # Quiet medbay floor guidance and inset bed brackets. Each actual
            # blocking bed bank is drawn later from the collision rectangles.
            for x,y in ((88,264),(320,216),(248,200),(192,88),(88,40),(96,248)):
                self.rect((x,y,x+23,y+7),0)
                for xx in (x+5,x+13):
                    self.line([(xx-2,y+2),(xx,y+4),(xx-2,y+6)],2)
            for x,y in ((304,232),(184,96),(72,48)):
                self.region(x//8,y//8,5,3,4)
                self.rect((x,y,x+39,y+23),0)
                self.rect((x+2,y+2,x+37,y+21),outline=1)
                self.line((x+8,y+11,x+31,y+11),2)
                self.line((x+20,y+5,x+20,y+17),2)
            self.region(10,33,3,3,2)
            self.rect((80,264,103,287),0)
            self.rect((82,266,101,285),outline=1)
            self.line((87,271,96,271),2);self.line((91,267,91,276),3)
        else:
            # Large floor containment glyph surrounds the guardian. Its thin
            # nested lines have no raised face or obstacle contact shadow.
            self.region(26,13,10,10,4)
            self.rect((208,104,287,183),0)
            for inset,color in ((0,2),(6,1),(12,2)):
                x,y,w,h=212+inset,108+inset,72-2*inset,72-2*inset
                octagon=[(x+12,y),(x+w-12,y),(x+w,y+12),(x+w,y+h-12),
                         (x+w-12,y+h),(x+12,y+h),(x,y+h-12),(x,y+12),(x+12,y)]
                self.line(octagon,color)
            self.line((236,144,259,144),3);self.line((248,132,248,155),3)
            for x,y in ((216,112),(272,112),(216,168),(272,168)):
                self.rect((x,y,x+7,y+7),0,1)
                self.line((x+2,y+2,x+5,y+2),2)
            for points in ([(248,104),(248,80),(328,80)],[(208,144),(128,144),(128,136),(88,136)],
                           [(248,184),(248,208),(328,208),(328,264)]):self.channel(points)

    def hazard(self):
        tx,ty,tw,th=self.room['hazard_rect']
        if not tw or not th:return
        self.region(tx,ty,tw,th,6)
        for oy in range(th):
            for ox in range(tw):
                x,y=(tx+ox)*8,(ty+oy)*8
                self.rect((x,y,x+7,y+7),0)
                if self.room['hazard']=='vent':
                    self.rect((x+1,y+1,x+6,y+6),outline=1)
                    for yy in (y+2,y+4):self.line((x+2,yy,x+5,yy),2)
                    self.point((x+1,y+1),3)
                else:
                    self.line((x,y+3,x+7,y+3),2)
                    self.line((x,y+4,x+7,y+4),2)
                    self.line((x,y+1,x,y+6),1);self.line((x+7,y+1,x+7,y+6),1)
                    self.point((x+1,y+2),3)

    def cache(self):
        center=self.room.get('optional_cache_marker')
        if not center:return
        cx,cy=center;x,y=cx-8,cy-8
        self.region(x//8,y//8,2,2,3)
        self.rect((x,y,x+15,y+15),1)
        self.draw.polygon([(cx,cy-6),(cx+6,cy),(cx,cy+6),(cx-6,cy)],outline=C[2])
        self.rect((cx-2,cy-2,cx+2,cy+2),outline=3)
        # This is only a floor marker. No cache actor or reward is authored.

    def finish(self):
        self.base();self.landmarks()
        for cover in self.room['covers']:self.cover(*cover)
        for center in self.room['cells']:self.pad(*center)
        self.hazard();self.cache();self.dock()
        return self.image,self.attributes


def route_validation(room,grid,astronaut):
    w,h=room['width'],room['height'];width,height=w*8,h*8
    bounds=proof.sprite_bounds(astronaut)
    ox=((bounds['left']+bounds['right'])>>1)//32
    oy=((bounds['top']+bounds['bottom'])>>1)//32
    footprints={
        'actual16x8':(bounds['left']//32-ox,bounds['top']//32-oy,
                      bounds['right']//32-ox,bounds['bottom']//32-oy),
        'conservative16x16':(-7,-7,8,8),'visual16x16':(-7,-11,8,4),
    }
    def footprint_free(x,y,fp):
        left,top,right,bottom=x+fp[0],y+fp[1],x+fp[2],y+fp[3]
        if left<0 or top<0 or right>=width or bottom>=height:return False
        return all(not grid[ty*w+tx] for ty in range(top//8,bottom//8+1)
                   for tx in range(left//8,right//8+1))
    # Precomputed center occupancy makes full reachability and order audits cheap.
    free={(x,y) for y in range(24,height-8) for x in range(8,width-8)
          if all(footprint_free(x,y,fp) for fp in footprints.values())}
    centers=[tuple(room['spawn'])]+[tuple(p) for p in room['cells']]+[tuple(room['terminal'])]
    assert all(p in free for p in centers),(room['name'],'blocked objective/spawn')
    parents={};
    def bfs(start):
        if start in parents:return parents[start]
        previous={start:None};queue=deque([start])
        while queue:
            x,y=queue.popleft()
            for p in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                if p in free and p not in previous:previous[p]=(x,y);queue.append(p)
        parents[start]=previous;return previous
    origin=bfs(centers[0]);assert all(p in origin for p in centers)
    def shortest(start,end):
        previous=bfs(start);assert end in previous
        path=[];cursor=end
        while cursor is not None:path.append(cursor);cursor=previous[cursor]
        path.reverse();turns=[path[0]]
        for i in range(1,len(path)-1):
            if (path[i][0]-path[i-1][0],path[i][1]-path[i-1][1])!=(path[i+1][0]-path[i][0],path[i+1][1]-path[i][1]):turns.append(path[i])
        if path[-1]!=turns[-1]:turns.append(path[-1])
        return {'from':list(start),'to':list(end),'length_pixels':len(path)-1,'waypoints':[list(p) for p in turns]},path
    routes=[];paths=[]
    for a,b in zip(centers,centers[1:]):
        item,path=shortest(a,b);routes.append(item);paths.append(path)
    repair_orders=[]
    if room['objective']=='repair':
        for ordering in permutations(centers[1:4]):
            chain=[centers[0]]+list(ordering)+[centers[-1]]
            lengths=[shortest(a,b)[0]['length_pixels'] for a,b in zip(chain,chain[1:])]
            repair_orders.append({'order':[list(p) for p in ordering],'length_pixels':sum(lengths),'reachable':True})
    x,y,rw,rh=room['dock_rect']
    assert all(not grid[ty*w+tx] for ty in range(y//8,(y+rh-1)//8+1) for tx in range(x//8,(x+rw-1)//8+1))
    for p in room['cells']+[room['drone']]:
        px,py=p
        assert all(not grid[ty*w+tx] for ty in range((py-8)//8,(py+7)//8+1)
                   for tx in range((px-8)//8,(px+7)//8+1)),(room['name'],'pad/drone overlaps cover',p)
    hx,hy,hw,hh=room['hazard_rect']
    assert hw*hh<=16
    assert all(not grid[ty*w+tx] for ty in range(hy,hy+hh) for tx in range(hx,hx+hw))
    for cx,cy in room['cells']:
        assert not(hw and hh and cx+7>=hx*8 and cx-8<(hx+hw)*8 and cy+7>=hy*8 and cy-8<(hy+hh)*8)
    cache=room.get('optional_cache_marker')
    if cache:
        assert tuple(cache) in free
        cx,cy=cache
        assert all(not grid[ty*w+tx] for ty in range((cy-8)//8,(cy+7)//8+1)
                   for tx in range((cx-8)//8,(cx+7)//8+1))
    escort=None
    if room['objective']=='escort':
        waypoints=room['escort_route'];assert waypoints[0]==room['escort_start'] and waypoints[-1]==room['terminal']
        assert all(p in waypoints for p in room['cells'])
        path=[tuple(waypoints[0])]
        for a,b in zip(waypoints,waypoints[1:]):
            assert a[0]==b[0] or a[1]==b[1],('escort not axis-aligned',a,b)
            dx=(b[0]>a[0])-(b[0]<a[0]);dy=(b[1]>a[1])-(b[1]<a[1]);cursor=tuple(a)
            while cursor!=tuple(b):
                cursor=(cursor[0]+dx,cursor[1]+dy);assert cursor in free,('escort route blocked',cursor);path.append(cursor)
        assert all(((path[min(i+20,len(path)-1)][0]-p[0])**2+(path[min(i+20,len(path)-1)][1]-p[1])**2)<=24**2 for i,p in enumerate(path))
        escort_anchors=[proof.anchor_for_center(p,astronaut)[0] for p in waypoints]
        escort_subpixels=[[x*32,y*32] for x,y in escort_anchors]
        assert all(a[0]==b[0] or a[1]==b[1] for a,b in zip(escort_subpixels,escort_subpixels[1:]))
        escort={'npc_sprite_id':astronaut['id'],'start':waypoints[0],'waypoints':waypoints,
                'route_actor_anchors_pixels':escort_anchors,'route_actor_anchors_subpixels':escort_subpixels,
                'subpixels_per_pixel':32,'axis_alignment_preserved_after_anchor_conversion':True,
                'length_pixels':len(path)-1,'all_axis_segments_clear':True,
                'actual_16x8_and_both_16x16_checks':True,'leader_20_path_pixels_ahead_within_24px':True,
                'runtime_behavior':'Not tested; static feasible route only'}
        paths=[path]
    return {'footprints':footprints,'reachable_centers':len(origin),'all_objectives_reachable':True,
            'dock_clear':True,'hazard_floor_clear':True,'drone_clear':True,'ordered_routes':routes,
            'ordered_route_pixels':sum(r['length_pixels'] for r in routes),'repair_orders':repair_orders,
            'escort':escort,'optional_cache':{'center':cache,'implemented_gameplay':False}},paths


def native_resources(room,attributes,grid,sprites):
    n=room['room'];folder=f'mission_01_room_{n:02d}';filename=f'{folder}.png'
    sid,bgid=ident(f'scene-{n}'),ident(f'background-{n}')
    write_json(f'assets/backgrounds/{filename}.gbsres',{
        '_resourceType':'background','id':bgid,'name':room['name'].title(),
        'symbol':f'bg_{folder}','filename':filename,'width':48,'height':40,
        'imageWidth':384,'imageHeight':320,'autoColor':False,'tileColors':proof.compressed(attributes),
    })
    original=ROOT/'project/scenes/start'
    scene=json.loads((original/'scene.gbsres').read_text())
    scene.update(id=sid,_index=110+n,name=room['name'].title(),symbol=room['scene_symbol'],
                 x=1200+n*440,y=420,width=48,height=40,backgroundId=bgid,
                 paletteIds=PALETTE_IDS,collisions=proof.compressed(grid),script=[])
    write_json(f'project/scenes/{folder}/scene.gbsres',scene)
    actors=sorted([json.loads(p.read_text()) for p in (original/'actors').glob('*.gbsres')],key=lambda a:a['_index'])
    centers=room['cells']+[room['terminal'],room['drone'],room['spawn']]
    receipt=[]
    for actor,center in zip(actors,centers):
        sprite=sprites[actor['spriteSheetId']];anchor,bounds=proof.anchor_for_center(center,sprite);i=actor['_index']
        actor.update(id=ident(f'actor-{n}-{i}'),symbol=f'actor_m01_r{n:02d}_{i}',coordinateType='pixels',x=anchor[0],y=anchor[1])
        write_json(f'project/scenes/{folder}/actors/actor_{i}.gbsres',actor)
        receipt.append({'runtime_index':i+1,'center_pixels':center,'anchor_pixels':anchor,'sprite_id':sprite['id'],
                        'bounds_subpixels':bounds,'actor_id':actor['id']})
    if room['objective']=='escort':
        actor=deepcopy(actors[0]);sprite=sprites['player'];anchor,bounds=proof.anchor_for_center(room['escort_start'],sprite)
        actor.update(id=ident('escort-room-2'),_index=6,name='Rescued Crew',symbol='actor_m01_r02_escort',
                     spriteSheetId=sprite['id'],paletteId='default-sprite',coordinateType='pixels',x=anchor[0],y=anchor[1],direction='up')
        write_json(f'project/scenes/{folder}/actors/actor_6.gbsres',actor)
        receipt.append({'runtime_index':7,'center_pixels':room['escort_start'],'anchor_pixels':anchor,
                        'sprite_id':sprite['id'],'bounds_subpixels':bounds,'actor_id':actor['id']})
    anchor,bounds=proof.anchor_for_center(room['spawn'],sprites['player'])
    return {'scene_id':sid,'background_id':bgid,'scene_symbol':room['scene_symbol'],
            'player_center_pixels':room['spawn'],'player_anchor_pixels':anchor,'player_bounds_subpixels':bounds,
            'native_actor_count':len(receipt),'actors':receipt}


def color_preview(image,attributes,palettes,state='SAFE'):
    output=Image.new('RGB',image.size)
    for y in range(image.height):
        for x in range(image.width):
            shade=C.index(image.getpixel((x,y)))
            slot=attributes[(y//8)*48+x//8]
            if slot==6:rgb=HAZARD_RGB555[state][3-shade]
            else:rgb=tuple(v>>3 for v in bytes.fromhex(palettes[PALETTE_IDS[slot]][3-shade]))
            output.putpixel((x,y),tuple(round(v*255/31) for v in rgb))
    return output


def main():
    mission=json.loads(MANIFEST.read_text());rooms=mission['rooms']
    assert len(rooms)==4 and [r['room'] for r in rooms]==list(range(4))
    sprites={r['id']:r for r in (json.loads(p.read_text()) for p in (ROOT/'assets/sprites').glob('*.gbsres'))}
    sprites['player']=json.loads((ROOT/'assets/sprites/astronaut.png.gbsres').read_text())
    palettes={p['id']:p['colors'] for p in (json.loads(path.read_text()) for path in (ROOT/'project/palettes').glob('*.gbsres'))}
    safe_colors=[''.join(f'{v<<3:02X}' for v in rgb) for rgb in HAZARD_RGB555['SAFE']]
    write_json('project/palettes/mission_hazard.gbsres',{'_resourceType':'palette','id':HAZARD_ID,
                'name':'Mission Hazard Safe','colors':safe_colors})
    palettes[HAZARD_ID]=safe_colors
    receipt={'scope':'Four staged native rooms; no active import/build/emulation/hardware',
             'room_count':4,'later_72_rooms':'Plan only; not implemented',
             'manifest_sha256':sha256(MANIFEST.read_bytes()).hexdigest(),
             'generator_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
             'reused_helper_sha256':sha256((ROOT/'scrolling_proof_art.py').read_bytes()).hexdigest(),
             'source_shades_rgba':[list(c)+( [255]) for c in C],
             'hazard_palette_id':HAZARD_ID,'hazard_phase_rgb555':HAZARD_RGB555,
             'graph':mission['graph'],'rooms':[]}
    montage=Image.new('RGB',(768,680),'#111522');md=ImageDraw.Draw(montage)
    for room in rooms:
        n=room['room'];strings=verify_strings(room)
        assert room['width']==48 and room['height']==40
        grid=proof.collision_grid(room)
        checks,paths=route_validation(room,grid,sprites['player'])
        if n==0:
            source=ROOT/'assets/backgrounds/proof_room_01.png'
            sidecar=json.loads((ROOT/'assets/backgrounds/proof_room_01.png.gbsres').read_text())
            image=Image.open(source).convert('RGB');attributes=proof.expanded(sidecar['tileColors'])
            reused={'qualified_background_path':str(source),'png_sha256':sha256(source.read_bytes()).hexdigest()}
        else:image,attributes=MissionArt(room).finish();reused=None
        assert set(image.get_flattened_data())<=set(C)
        unique_tiles=len({image.crop((x,y,x+8,y+8)).tobytes() for y in range(0,320,8) for x in range(0,384,8)})
        assert unique_tiles<192,(room['name'],unique_tiles)
        assert len(grid)==len(attributes)==1920 and set(attributes)<=set(range(7))
        assert proof.expanded(proof.compressed(grid))==grid and proof.expanded(proof.compressed(attributes))==attributes
        # Only authored hazard cells may consume palette6.
        hx,hy,hw,hh=room['hazard_rect']
        expected={y*48+x for y in range(hy,hy+hh) for x in range(hx,hx+hw)}
        assert {i for i,a in enumerate(attributes) if a==6}==expected
        png=STAGE/f'assets/backgrounds/mission_01_room_{n:02d}.png';png.parent.mkdir(parents=True,exist_ok=True)
        rgba=image.convert('RGBA');assert set(rgba.get_flattened_data())<={c+(255,) for c in C}
        rgba.save(png,optimize=False)
        resources=native_resources(room,attributes,grid,sprites)
        previews={}
        for state in ('SAFE','AMBER','RED'):
            color=color_preview(image,attributes,palettes,state)
            output=STAGE/f'room_{n:02d}-{state.lower()}.png';color.save(output,optimize=False)
            previews[state]={'path':str(output.relative_to(ROOT)),'sha256':sha256(output.read_bytes()).hexdigest()}
            if state=='SAFE':
                bx,by=(n%2)*384,(n//2)*340
                montage.paste(color,(bx,by+20));md.text((bx+8,by+4),f'{n+1:02d} {room["name"]} / {room["objective"].upper()}',fill='#EDECE2')
                overlay=color.copy();draw=ImageDraw.Draw(overlay)
                for x,y,w,h in room['covers']:draw.rectangle((x*8,y*8,(x+w)*8-1,(y+h)*8-1),outline='#EF6159')
                for i,path in enumerate(paths):draw.line(path,fill=['#FFE276','#70FFBE','#86BFFF','#E5A5FF'][i%4],width=1)
                overlay.save(STAGE/f'room_{n:02d}-routes.png',optimize=False)
        signature=sha256(bytes(grid)+json.dumps(room['cells']).encode()).hexdigest()
        receipt['rooms'].append({'room':n,'name':room['name'],'objective':room['objective'],
            'dimensions_pixels':[384,320],'dimensions_tiles':[48,40],'mode':'RGBA','alpha':255,
            'unique_tiles':unique_tiles,'palette_slots':sorted(set(attributes)),'palette_ids':PALETTE_IDS,
            'png_sha256':sha256(png.read_bytes()).hexdigest(),'collision_sha256':sha256(bytes(grid)).hexdigest(),
            'attribute_sha256':sha256(bytes(attributes)).hexdigest(),'tactical_signature':signature,
            'native_rle_roundtrip':True,'strings':strings,'resources':resources,'static_checks':checks,
            'previews':previews,'reused_art':reused})
        print(f'{n:02d} {room["name"]}: {unique_tiles} tiles, {resources["native_actor_count"]} actors, routes clear')
    assert len({r['tactical_signature'] for r in receipt['rooms']})==4
    normalized=[]
    for room in rooms:
        grid=proof.collision_grid(room)
        transforms=[bytes(grid[y*48+x] for y in (range(40) if vy==0 else range(39,-1,-1))
                          for x in (range(48) if hx==0 else range(47,-1,-1)))
                    for hx,vy in ((0,0),(1,0),(0,1),(1,1))]
        normalized.append(min(transforms))
    assert len(set(normalized))==4
    receipt['distinct_collision_layouts']=4
    receipt['mirror_or_half_turn_duplicate_layouts']=False
    montage.save(STAGE/'mission-montage.png',optimize=False)
    receipt['montage_sha256']=sha256((STAGE/'mission-montage.png').read_bytes()).hexdigest()
    write_json('MISSION-ART-RECEIPTS.json',receipt)


if __name__=='__main__':main()

#!/usr/bin/env python3
"""Stage missions02/03 as eight distinct native Wreck Hull spaces.

Reuses qualified source-palette, collision, resource-bound, route and hazard
operations without changing mission_art.py, legacy rooms or active resources.
Only campaign/zone-01-assets is written; input manifests remain authored JSON.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from uuid import UUID, uuid5
import json
from PIL import Image, ImageDraw
import scrolling_proof_art as proof
import mission_art as common

ROOT=Path(__file__).resolve().parent
STAGE=ROOT/'campaign/zone-01-assets'
NS={2:UUID('7195db39-c73c-5d8d-a99c-d2f8ba69a650'),3:UUID('6f5cf5c9-d0a8-52f2-8c1c-5e338559c3d7')}
HAZARD_ID=str(uuid5(UUID('c385f838-17b9-58b8-92d6-67c1ee7de118'),'zone01-authored-hazard'))
PALETTE_IDS=list(proof.PALETTE_IDS);PALETTE_IDS[6]=HAZARD_ID
C=proof.C
# Runtime module globals are confined to this generator process. No source file
# or previously generated resource is changed by selecting these palettes.
common.PALETTE_IDS=PALETTE_IDS


def ident(mission,label):return str(uuid5(NS[mission],label))
def write_json(relative,value):
    path=STAGE/relative;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2)+'\n');return path


class ZoneArt(common.MissionArt):
    def base(self):
        proof.Art.base(self)
        kind=self.room['art_kind']
        for ty in range(3,self.h-1):
            for tx in range(1,self.w-1):
                x,y=tx*8,ty*8;self.rect((x,y,x+7,y+7),1)
                if kind in ('cargo_fork','patch_deck'):
                    if ty%2:self.line((x,y+7,x+7,y+7),0)
                    if tx%4==0:self.line((x+7,y+2,x+7,y+5),0)
                    if (tx+ty)%5==0:self.point((x+1,y+1),2)
                elif kind in ('relay_ladder','triage_hub'):
                    if ty%3==2:self.line((x,y+7,x+7,y+7),0)
                    if tx%3==2:self.line((x+7,y,x+7,y+7),0)
                    if tx%3==0 and ty%3==0:self.point((x+1,y+1),2)
                elif kind in ('circuit_sentinel','pod_warden'):
                    if ty%4==3:self.line((x,y+7,x+7,y+7),0)
                    if tx%4==3:self.line((x+7,y,x+7,y+7),0)
                    if ty%4==0:self.line((x+2,y+1,x+4,y+1),0)
                elif kind=='debris_halo':
                    if ty%3==2:self.line((x,y+7,x+7,y+7),0)
                    if (tx+ty)%4==0:self.line((x+2,y+3,x+4,y+5),0)
                    if tx%4==1:self.point((x+6,y+1),2)
                else:
                    if ty%2==1:self.line((x,y+7,x+7,y+7),0)
                    if tx%4==0:self.line((x+7,y,x+7,y+7),0)
                    if ty%2==0 and tx%2==0:self.point((x+2,y+5),2)

    def plate(self,x,y,w,h,style):
        assert x%8==y%8==w%8==h%8==0
        self.region(x//8,y//8,w//8,h//8,4)
        self.rect((x,y,x+w-1,y+h-1),0)
        if style=='instrument':
            self.rect((x+2,y+2,x+w-3,y+h-3),outline=1)
            for xx in range(x+5,x+w-4,8):
                self.line((xx,y+5,xx,y+h-6),2)
                self.point((xx,y+5),3)
        elif style=='medical':
            self.rect((x+2,y+2,x+w-3,y+h-3),outline=1)
            self.line((x+w//2-7,y+h//2,x+w//2+7,y+h//2),2)
            self.line((x+w//2,y+h//2-6,x+w//2,y+h//2+6),3)
        elif style=='freight':
            for yy in range(y+3,y+h-2,8):
                self.line((x+3,yy,x+w-4,yy),1)
                for xx in range(x+5,x+w-4,8):self.point((xx,yy),2)

    def glyph(self,cx,cy,w,h,kind):
        # Thin flush field lines deliberately omit a raised obstacle face.
        x,y=cx-w//2,cy-h//2
        assert x%8==0 and y%8==0
        self.region(x//8,y//8,w//8,h//8,4);self.rect((x,y,x+w-1,y+h-1),0)
        if kind=='axis':
            self.line((x+4,cy,x+w-5,cy),2);self.line((cx,y+4,cx,y+h-5),1)
            for px,d in ((x+7,-1),(x+w-8,1)):
                self.line([(px-d*3,cy-3),(px,cy),(px-d*3,cy+3)],3)
            self.rect((cx-9,cy-9,cx+8,cy+8),outline=2)
        elif kind=='halo':
            self.draw.ellipse((x+3,y+3,x+w-4,y+h-4),outline=C[2])
            self.draw.ellipse((x+10,y+10,x+w-11,y+h-11),outline=C[1])
            for px,py in ((x+7,cy),(x+w-8,cy),(cx,y+7),(cx,y+h-8)):
                self.line((px-2,py,px+2,py),2)
        else:
            self.line([(x+8,y+4),(x+w-9,y+4),(x+w-4,y+h//2),(cx,y+h-5),(x+4,y+h//2),(x+8,y+4)],2)
            self.line([(x+15,y+12),(x+w-16,y+12),(x+w-12,cy),(cx,y+h-13),(x+12,cy),(x+15,y+12)],1)
            self.line((cx-6,cy,cx+5,cy),3);self.line((cx,cy-6,cx,cy+5),3)

    def landmarks(self):
        kind=self.room['art_kind']
        if kind=='cargo_fork':
            # Two recessed freight rails flank the long physical bulkhead.
            for x in (152,216):
                for y in range(32,280,8):
                    self.rect((x,y,x+7,y+7),0)
                    self.line((x+1,y,x+1,y+7),1);self.line((x+5,y,x+5,y+7),1)
                    self.line((x+2,y+3,x+4,y+3),2)
            self.plate(48,32,56,16,'freight');self.plate(288,80,56,16,'freight')
            self.plate(304,240,48,40,'freight')
        elif kind=='relay_ladder':
            for cx,cy in self.room['cells']:
                self.channel([(cx,cy),(152,cy),(152,208),(216,208)])
            self.plate(40,40,40,16,'instrument');self.plate(304,104,48,16,'instrument')
            self.plate(88,224,48,16,'instrument')
            self.glyph(224,168,48,48,'axis')
        elif kind=='patch_deck':
            self.plate(128,32,48,16,'instrument');self.plate(304,128,48,16,'instrument')
            self.plate(176,248,48,32,'instrument')
            self.channel([(152,56),(160,56),(160,136),(232,136),(232,184)])
            self.channel([(328,152),(352,152),(352,208)])
            self.glyph(152,192,48,32,'halo')
        elif kind=='circuit_sentinel':
            self.glyph(224,144,80,64,'axis')
            self.channel([(224,112),(224,88),(224,72)])
            self.channel([(184,144),(88,144),(88,152)])
            self.channel([(264,144),(328,144),(328,256)])
            self.plate(304,232,48,40,'freight')
        elif kind=='debris_halo':
            self.glyph(192,160,128,112,'halo')
            # Repeated shallow etched fragments; none has a raised cover face.
            for x,y in ((40,128),(136,112),(232,112),(304,176),(304,280)):
                self.rect((x,y,x+15,y+7),0)
                self.line((x+3,y+2,x+11,y+5),1);self.point((x+3,y+2),2)
        elif kind=='triage_hub':
            self.plate(56,32,48,16,'medical');self.plate(304,144,48,16,'medical')
            self.plate(232,248,48,32,'medical')
            self.channel([(80,56),(152,56),(152,128),(256,128),(256,208)])
            self.channel([(328,168),(336,168),(336,280),(256,280)])
            self.glyph(144,176,48,32,'halo')
        elif kind=='pod_causeway':
            for x,y in ((64,264),(304,248),(160,80),(40,128)):
                self.plate(x,y,48,32,'medical')
            # Native floor arrows give the crew's long route readable landmarks.
            for x,y in ((344,192),(264,160),(256,32),(168,32),(88,120),(24,224)):
                self.rect((x,y,x+23,y+7),0)
                for xx in (x+5,x+13):self.line([(xx-2,y+2),(xx,y+4),(xx-2,y+6)],2)
        else:
            self.glyph(200,144,80,64,'warden')
            for points in ([(200,112),(176,112),(176,48)],[(160,144),(56,144),(56,152)],
                           [(240,144),(352,144),(352,256),(344,256)]):self.channel(points)
            self.plate(152,32,48,16,'instrument');self.plate(32,128,48,16,'medical')

    def pad(self,cx,cy):
        super().pad(cx,cy)
        if self.room['objective']=='relay':
            index=self.room['cells'].index([cx,cy])
            for n in range(index+1):self.line((cx-4+n*3,cy+3,cx-4+n*3,cy+6),3)


def native_resources(number,room,attributes,grid,sprites):
    n=room['room'];folder=f'mission_{number:02d}_room_{n:02d}';filename=f'{folder}.png'
    sid,bgid=ident(number,f'scene-{n}'),ident(number,f'background-{n}')
    write_json(f'assets/backgrounds/{filename}.gbsres',{
        '_resourceType':'background','id':bgid,'name':room['name'].title(),
        'symbol':f'bg_{folder}','filename':filename,'width':48,'height':40,
        'imageWidth':384,'imageHeight':320,'autoColor':False,'tileColors':proof.compressed(attributes),
    })
    original=ROOT/'project/scenes/start';scene=json.loads((original/'scene.gbsres').read_text())
    native_index=114+(number-2)*4+n
    scene.update(id=sid,_index=native_index,name=room['name'].title(),symbol=room['scene_symbol'],
                 x=1200+n*440,y=860+(number-2)*440,width=48,height=40,backgroundId=bgid,
                 paletteIds=PALETTE_IDS,collisions=proof.compressed(grid),script=[])
    write_json(f'project/scenes/{folder}/scene.gbsres',scene)
    actors=sorted([json.loads(p.read_text()) for p in (original/'actors').glob('*.gbsres')],key=lambda a:a['_index'])
    centers=room['cells']+[room['terminal'],room['drone'],room['spawn']];receipts=[]
    for actor,center in zip(actors,centers):
        sprite=sprites[actor['spriteSheetId']];anchor,bounds=proof.anchor_for_center(center,sprite);i=actor['_index']
        actor.update(id=ident(number,f'actor-{n}-{i}'),symbol=f'actor_m{number:02d}_r{n:02d}_{i}',
                     coordinateType='pixels',x=anchor[0],y=anchor[1])
        write_json(f'project/scenes/{folder}/actors/actor_{i}.gbsres',actor)
        receipts.append({'runtime_index':i+1,'center_pixels':center,'anchor_pixels':anchor,'sprite_id':sprite['id'],
                         'bounds_subpixels':bounds,'actor_id':actor['id']})
    if room['objective']=='escort':
        actor=deepcopy(actors[0]);sprite=sprites['player'];anchor,bounds=proof.anchor_for_center(room['escort_start'],sprite)
        actor.update(id=ident(number,f'escort-room-{n}'),_index=6,name='Rescued Crew',symbol=f'actor_m{number:02d}_r{n:02d}_escort',
                     spriteSheetId=sprite['id'],paletteId='default-sprite',coordinateType='pixels',x=anchor[0],y=anchor[1],direction='up')
        write_json(f'project/scenes/{folder}/actors/actor_6.gbsres',actor)
        receipts.append({'runtime_index':7,'center_pixels':room['escort_start'],'anchor_pixels':anchor,'sprite_id':sprite['id'],
                         'bounds_subpixels':bounds,'actor_id':actor['id']})
    anchor,bounds=proof.anchor_for_center(room['spawn'],sprites['player'])
    return {'scene_id':sid,'background_id':bgid,'scene_symbol':room['scene_symbol'],'native_index':native_index,
            'player_center_pixels':room['spawn'],'player_anchor_pixels':anchor,'player_bounds_subpixels':bounds,
            'native_actor_count':len(receipts),'actors':receipts}


def normalized_collision(grid):
    transforms=[bytes(grid[y*48+x] for y in (range(40) if vy==0 else range(39,-1,-1))
                      for x in (range(48) if hx==0 else range(47,-1,-1)))
                for hx,vy in ((0,0),(1,0),(0,1),(1,1))]
    return min(transforms)


def main():
    missions={n:json.loads((ROOT/f'campaign/mission-{n:02d}.json').read_text()) for n in (2,3)}
    sprites={r['id']:r for r in (json.loads(p.read_text()) for p in (ROOT/'assets/sprites').glob('*.gbsres'))}
    sprites['player']=json.loads((ROOT/'assets/sprites/astronaut.png.gbsres').read_text())
    palettes={p['id']:p['colors'] for p in (json.loads(path.read_text()) for path in (ROOT/'project/palettes').glob('*.gbsres'))}
    safe_colors=[''.join(f'{v<<3:02X}' for v in rgb) for rgb in common.HAZARD_RGB555['SAFE']]
    write_json('project/palettes/zone01_mission_hazard.gbsres',{'_resourceType':'palette','id':HAZARD_ID,
                'name':'Wreck Hull Hazard Safe','colors':safe_colors});palettes[HAZARD_ID]=safe_colors
    receipt={'scope':'Eight new staged native rooms; no active import/build/emulation/hardware',
             'new_room_count':8,'zone01_room_count_including_frozen_mission01':12,
             'later_72_rooms':'Plan only; no claim of implementation',
             'generator_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
             'reused_helpers_sha256':{name:sha256((ROOT/name).read_bytes()).hexdigest() for name in ('mission_art.py','scrolling_proof_art.py')},
             'source_shades_rgba':[list(c)+[255] for c in C],
             'hazard_palette_id':HAZARD_ID,'hazard_phase_rgb555':common.HAZARD_RGB555,'missions':[]}
    frozen=json.loads((ROOT/'campaign/mission-01.json').read_text())['rooms']
    fingerprints=[normalized_collision(proof.collision_grid(r)) for r in frozen]
    for number,mission in missions.items():
        rooms=mission['rooms'];assert len(rooms)==4 and [r['room'] for r in rooms]==list(range(4))
        montage=Image.new('RGB',(768,680),'#111522');md=ImageDraw.Draw(montage)
        mr={'mission':number,'name':mission['name'],'graph':mission['graph'],
            'manifest_sha256':sha256((ROOT/f'campaign/mission-{number:02d}.json').read_bytes()).hexdigest(),'rooms':[]}
        for room in rooms:
            n=room['room'];assert room['width']==48 and room['height']==40
            assert room['warning_frames']>=42 and room['recover_frames']>=96
            strings=common.verify_strings(room);grid=proof.collision_grid(room)
            checks,paths=common.route_validation(room,grid,sprites['player'])
            image,attributes=ZoneArt(room).finish()
            assert set(image.get_flattened_data())<=set(C)
            count=len({image.crop((x,y,x+8,y+8)).tobytes() for y in range(0,320,8) for x in range(0,384,8)})
            assert count<192,(room['name'],count)
            assert len(grid)==len(attributes)==1920 and set(attributes)<=set(range(7))
            assert proof.expanded(proof.compressed(grid))==grid and proof.expanded(proof.compressed(attributes))==attributes
            hx,hy,hw,hh=room['hazard_rect'];expected={y*48+x for y in range(hy,hy+hh) for x in range(hx,hx+hw)}
            assert {i for i,a in enumerate(attributes) if a==6}==expected
            fingerprint=normalized_collision(grid);assert fingerprint not in fingerprints,(room['name'],'mirrored/duplicate geometry');fingerprints.append(fingerprint)
            filename=f'mission_{number:02d}_room_{n:02d}.png';png=STAGE/'assets/backgrounds'/filename
            png.parent.mkdir(parents=True,exist_ok=True);rgba=image.convert('RGBA')
            assert set(rgba.get_flattened_data())<={c+(255,) for c in C};rgba.save(png,optimize=False)
            resources=native_resources(number,room,attributes,grid,sprites)
            previews={}
            for state in ('SAFE','AMBER','RED'):
                color=common.color_preview(image,attributes,palettes,state)
                output=STAGE/f'mission_{number:02d}_room_{n:02d}-{state.lower()}.png';color.save(output,optimize=False)
                previews[state]={'path':str(output.relative_to(ROOT)),'sha256':sha256(output.read_bytes()).hexdigest()}
                if state=='SAFE':
                    bx,by=(n%2)*384,(n//2)*340;montage.paste(color,(bx,by+20))
                    md.text((bx+8,by+4),f'{n+1:02d} {room["name"]} / {room["objective"].upper()}',fill='#EDECE2')
                    overlay=color.copy();draw=ImageDraw.Draw(overlay)
                    for x,y,w,h in room['covers']:draw.rectangle((x*8,y*8,(x+w)*8-1,(y+h)*8-1),outline='#EF6159')
                    for i,path in enumerate(paths):draw.line(path,fill=['#FFE276','#70FFBE','#86BFFF','#E5A5FF'][i%4],width=1)
                    overlay.save(STAGE/f'mission_{number:02d}_room_{n:02d}-routes.png',optimize=False)
            mr['rooms'].append({'room':n,'name':room['name'],'objective':room['objective'],'enemy':room['enemy'],
                'dimensions_pixels':[384,320],'dimensions_tiles':[48,40],'mode':'RGBA','alpha':255,
                'unique_tiles':count,'palette_slots':sorted(set(attributes)),'palette_ids':PALETTE_IDS,
                'png_sha256':sha256(png.read_bytes()).hexdigest(),'collision_sha256':sha256(bytes(grid)).hexdigest(),
                'attribute_sha256':sha256(bytes(attributes)).hexdigest(),'native_rle_roundtrip':True,
                'mirror_normalized_collision_sha256':sha256(fingerprint).hexdigest(),
                'strings':strings,'resources':resources,'static_checks':checks,'previews':previews})
            print(f'M{number:02d}R{n:02d} {room["name"]}: {count} tiles, {resources["native_actor_count"]} actors, routes clear')
        montage_path=STAGE/f'mission-{number:02d}-montage.png';montage.save(montage_path,optimize=False)
        mr['montage_sha256']=sha256(montage_path.read_bytes()).hexdigest();receipt['missions'].append(mr)
    assert len(set(fingerprints))==12
    receipt['distinct_collision_layouts_including_mission01']=12
    receipt['mirror_or_half_turn_duplicate_layouts']=False
    write_json('ZONE-01-ART-RECEIPTS.json',receipt)


if __name__=='__main__':main()

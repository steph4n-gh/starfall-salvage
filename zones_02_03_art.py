#!/usr/bin/env python3
"""Stage24 authored native rooms for Coolant Works and Solar Foundry.

Reads mission04..09 manifests and preserves all earlier active/staged files.
Original exact four-shade RGBA source pixels; eight consumed BG slots; static
route/hazard/actor checks reuse the qualified native helpers. No builds, imports,
emulator/browser/device operations. Cache markers remain background art only.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from uuid import UUID,uuid5
import json
from PIL import Image,ImageDraw
import scrolling_proof_art as proof
import mission_art as common
import zone_art as previous

ROOT=Path(__file__).resolve().parent
STAGE=ROOT/'campaign/zones-02-03-assets'
MASTER=UUID('cd2a8e90-bc48-5777-9bf7-78bb4e60767c')
C=proof.C
NAMES={1:'COOLANT WORKS',2:'SOLAR FOUNDRY'}
COLORS={
 1:{'floor':['D9FFFF','7ADDE2','365C70','0E1C30'],
    'cover':['D6FFFF','8BCBD4','426C88','142A44'],
    'field':['E8FFFF','79ECB6','347F86','102A42']},
 2:{'floor':['C9D3D8','859595','465159','161E29'],
    'cover':['FFE7C0','DD8454','784044','261A2B'],
    'field':['FFE1A9','E7AF56','995C45','321A27']},
}
HAZARD_ID=str(uuid5(MASTER,'hazard-palette'))


def ident(mission,label):return str(uuid5(uuid5(MASTER,f'mission-{mission:02d}'),label))
def palette_id(zone,material):return str(uuid5(MASTER,f'zone-{zone}-{material}'))
def palette_ids(zone):
    return [palette_id(zone,'floor'),palette_id(zone,'floor'),'default-bg-3',
            palette_id(zone,'cover'),palette_id(zone,'field'),'default-bg-4',HAZARD_ID,'default-ui']
def write_json(relative,value):
    path=STAGE/relative;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2)+'\n');return path


class EnvironmentArt(previous.ZoneArt):
    def base(self):
        # Keep the exact collision perimeter, but author different architecture.
        proof.Art.base(self)
        z=self.room['zone'];n=self.room['room'];m=self.room['mission_number']
        for ty in range(3,self.h-1):
            for tx in range(1,self.w-1):
                x,y=tx*8,ty*8;self.rect((x,y,x+7,y+7),1)
                if z==1:
                    if ty%3==2:self.line((x,y+7,x+7,y+7),0)
                    if tx%4==3:self.line((x+7,y+1,x+7,y+6),0)
                    if (tx+ty+n)%5==0:self.point((x+2,y+2),2)
                    if m==5 and ty%3==0 and tx%4==0:self.line((x+2,y+5,x+4,y+5),0)
                else:
                    if ty%2==1:self.line((x,y+7,x+7,y+7),0)
                    if tx%3==2:self.line((x+7,y,x+7,y+7),0)
                    if m==7 and ty%4==0:self.line((x+2,y+2,x+5,y+2),0)
                    elif m==8 and tx%4==0:self.point((x+3,y+4),2)
                    elif m==9 and (tx+ty)%4==0:self.line((x+2,y+3,x+4,y+5),0)
        for ty in range(3,self.h):
            for tx in (0,self.w-1):
                x,y=tx*8,ty*8;self.rect((x,y,x+7,y+7),0)
                if z==1:
                    self.rect((x+2,y,x+5,y+7),1)
                    self.line((x+2,y+1,x+2,y+6),3)
                    self.line((x+1,y,x+6,y),2)
                    self.line((x+1,y+7,x+6,y+7),2)
                else:
                    self.rect((x+1,y+1,x+6,y+6),1)
                    for yy in (y+2,y+4):self.line((x+2,yy,x+5,yy),2)
                    self.point((x+1,y+1),3)
                self.region(tx,ty,1,1,3)
        # The far wall is fully solid; glazed lab meters/foundry vent grilles
        # replace the Wreck Hull star ports without adding walkable scenery.
        for tx in range(1,self.w-1):
            for ty in range(3):
                x,y=tx*8,ty*8;self.rect((x,y,x+7,y+7),0)
                self.region(tx,ty,1,1,3)
                if z==1:
                    self.rect((x+1,y+1,x+6,y+6),1)
                    self.line((x+2,y+1,x+2,y+5),2)
                    if ty==2:self.line((x+1,y+6,x+6,y+6),3)
                else:
                    for yy in (y+2,y+5):self.line((x+1,yy,x+6,yy),1)
                    self.point((x+1,y+1),2);self.point((x+6,y+6),2)

    def cover(self,tx,ty,tw,th):
        self.region(tx,ty,tw,th,3)
        z=self.room['zone']
        for oy in range(th):
            for ox in range(tw):
                x,y=(tx+ox)*8,(ty+oy)*8;self.rect((x,y,x+7,y+7),1)
                if z==1:
                    self.line((x+2,y+1,x+2,y+6),2)
                    self.line((x+5,y+2,x+5,y+5),0)
                    if oy==0:
                        self.line((x,y,x+7,y),0);self.line((x+1,y+1,x+6,y+1),3)
                    if ox==0:self.line((x,y,x,y+7),0)
                    if ox==tw-1:self.line((x+7,y,x+7,y+7),0)
                    if oy==th-1:
                        self.rect((x,y+5,x+7,y+7),0);self.line((x+1,y+5,x+6,y+5),2)
                else:
                    self.line((x+1,y+3,x+6,y+3),0);self.line((x+2,y+4,x+5,y+4),2)
                    if oy==0:
                        self.line((x,y,x+7,y),0);self.line((x+1,y+1,x+6,y+1),3)
                        self.line((x+1,y+2,x+6,y+2),2)
                    if ox==0:self.line((x,y,x,y+7),0)
                    if ox==tw-1:self.line((x+7,y,x+7,y+7),0)
                    if oy==th-1:
                        self.rect((x,y+5,x+7,y+7),0);self.point((x+2,y+5),2)

    def dock(self):
        super().dock()
        # Extraction keeps the established amber identity across both zones.
        x,y,w,h=self.room['dock_rect']
        self.region(x//8,y//8,w//8,h//8,5)

    def station(self,cx,cy,index):
        # Flush instruments reinforce the implemented repair/relay objectives.
        # Cover is drawn later, so instruments never hide collision geometry.
        x,y=cx-16,cy-24
        if y<24:y=cy+16
        if x<8:x=8
        if x+32>376:x=344
        self.region(x//8,y//8,4,2,4);self.rect((x,y,x+31,y+15),0)
        self.rect((x+1,y+1,x+30,y+14),outline=1)
        if self.room['zone']==1:
            for xx in range(x+4,x+28,8):
                self.draw.ellipse((xx,y+4,xx+5,y+10),outline=C[2])
                self.line((xx+2,y+5,xx+2,y+9),3)
        else:
            for xx in range(x+4,x+29,6):
                self.line((xx,y+4,xx,y+11),2);self.point((xx,y+4),3)

    def containment(self,cx,cy):
        # A floor glyph shows existing charger/axis/hunter behavior; it does
        # not introduce force fields, reflectors or collision of its own.
        x,y=cx-40,cy-32
        self.region(x//8,y//8,10,8,4);self.rect((x,y,x+79,y+63),0)
        enemy=self.room['enemy']
        if enemy=='charger':
            for inset,col in ((3,2),(10,1),(17,2)):
                a,b,c,d=x+inset,y+inset,x+79-inset,y+63-inset
                self.line([(a+8,b),(c-8,b),(c,b+8),(c,d-8),(c-8,d),(a+8,d),(a,d-8),(a,b+8),(a+8,b)],col)
            self.line((cx-6,cy,cx+5,cy),3);self.line((cx,cy-6,cx,cy+5),3)
        elif enemy=='sweeper':
            self.line((x+4,cy,x+75,cy),2)
            for px,d in ((x+7,-1),(x+72,1)):
                self.line([(px-d*4,cy-4),(px,cy),(px-d*4,cy+4)],3)
            self.rect((cx-12,cy-12,cx+11,cy+11),outline=1)
            self.rect((cx-7,cy-7,cx+6,cy+6),outline=2)
        else:
            self.line([(x+10,y+7),(x+69,y+7),(x+75,y+32),(cx,y+57),(x+4,y+32),(x+10,y+7)],2)
            self.line([(x+20,y+15),(x+59,y+15),(x+63,y+32),(cx,y+47),(x+16,y+32),(x+20,y+15)],1)
            self.line((cx-5,cy,cx+4,cy),3)
        if self.room['zone']==1:
            for xx in (x+4,x+68):
                self.rect((xx,y+20,xx+7,y+43),outline=1)
                for yy in (y+23,y+31,y+39):self.line((xx+2,yy,xx+5,yy),2)
        else:
            for xx in (x+4,x+68):
                for yy in (y+5,y+53):self.line((xx,yy,xx+7,yy),2)

    def landmarks(self):
        obj=self.room['objective'];m=self.room['mission_number'];n=self.room['room']
        for i,(cx,cy) in enumerate(self.room['cells']):self.station(cx,cy,i)
        if obj=='core':
            self.containment(*self.room['drone'])
        elif self.room['zone']==1:
            # Authored coolant capillaries differ by physical room goals;
            # they are quiet floor inlays rather than a new simulation system.
            for i,(cx,cy) in enumerate(self.room['cells']):
                cross_x=(144,216,288)[(i+n)%3]
                self.channel([(cx,cy),(cross_x,cy),(cross_x,208-i*24)])
            dx,dy=self.room['drone']
            if m==4:
                self.region((dx-16)//8,(dy-16)//8,4,4,4)
                self.rect((dx-16,dy-16,dx+15,dy+15),0)
                self.draw.ellipse((dx-13,dy-13,dx+12,dy+12),outline=C[2])
                self.line((dx-7,dy,dx+6,dy),1)
            elif m==5:
                self.plate(dx-24,dy-16,48,32,'medical' if obj=='escort' else 'instrument')
            else:
                self.plate(dx-24,dy-16,48,32,'instrument')
                self.line((dx-16,dy+8,dx+15,dy+8),2)
        else:
            # Foundry machines use different large recessed constructions.
            dx,dy=self.room['drone'];self.plate(dx-24,dy-16,48,32,'freight')
            for i,(cx,cy) in enumerate(self.room['cells']):
                line_y=(104,176,280)[(i+n)%3]
                self.channel([(cx,cy),(cx,line_y),(192+i*24,line_y)])
            if m==7:
                for xx in (dx-15,dx-7,dx+1,dx+9):self.line((xx,dy-10,xx,dy+8),2)
            elif m==8:
                self.line((dx-16,dy,dx+15,dy),2);self.line((dx,dy-11,dx,dy+10),3)
            else:
                self.draw.ellipse((dx-18,dy-10,dx+17,dy+9),outline=C[2])
        if obj=='escort':
            # Direction ticks use the authored route's actual turns. These
            # are visual guidance for the existing escort job, not new goals.
            for i,(cx,cy) in enumerate(self.room['escort_route'][1:-1]):
                if i%2:continue
                x,y=(cx//8)*8,(cy//8)*8
                if 8<=x<=352 and 24<=y<=296:
                    self.line([(x+2,y+2),(x+5,y+4),(x+2,y+6)],2)


def resources(number,room,attrs,grid,sprites,ids):
    n=room['room'];folder=f'mission_{number:02d}_room_{n:02d}';filename=f'{folder}.png'
    sid,bgid=ident(number,f'scene-{n}'),ident(number,f'background-{n}')
    write_json(f'assets/backgrounds/{filename}.gbsres',{'_resourceType':'background','id':bgid,
        'name':room['name'].title(),'symbol':f'bg_{folder}','filename':filename,'width':48,'height':40,
        'imageWidth':384,'imageHeight':320,'autoColor':False,'tileColors':proof.compressed(attrs)})
    original=ROOT/'project/scenes/start';scene=json.loads((original/'scene.gbsres').read_text())
    index=122+(number-4)*4+n
    scene.update(id=sid,_index=index,name=room['name'].title(),symbol=room['scene_symbol'],x=1200+n*440,
                 y=1740+(number-4)*440,width=48,height=40,backgroundId=bgid,paletteIds=ids,
                 collisions=proof.compressed(grid),script=[])
    write_json(f'project/scenes/{folder}/scene.gbsres',scene)
    actors=sorted([json.loads(p.read_text()) for p in (original/'actors').glob('*.gbsres')],key=lambda a:a['_index'])
    centers=room['cells']+[room['terminal'],room['drone'],room['spawn']];receipt=[]
    for actor,center in zip(actors,centers):
        i=actor['_index'];sprite=sprites[actor['spriteSheetId']];anchor,bounds=proof.anchor_for_center(center,sprite)
        actor.update(id=ident(number,f'actor-{n}-{i}'),symbol=f'actor_m{number:02d}_r{n:02d}_{i}',
                     coordinateType='pixels',x=anchor[0],y=anchor[1])
        write_json(f'project/scenes/{folder}/actors/actor_{i}.gbsres',actor)
        receipt.append({'runtime_index':i+1,'center_pixels':center,'anchor_pixels':anchor,'sprite_id':sprite['id'],
                        'bounds_subpixels':bounds,'actor_id':actor['id']})
    if room['objective']=='escort':
        actor=deepcopy(actors[0]);sprite=sprites['player'];anchor,bounds=proof.anchor_for_center(room['escort_start'],sprite)
        actor.update(id=ident(number,f'escort-room-{n}'),_index=6,name='Rescued Crew',symbol=f'actor_m{number:02d}_r{n:02d}_escort',
                     spriteSheetId=sprite['id'],paletteId='default-sprite',coordinateType='pixels',x=anchor[0],y=anchor[1],direction='up')
        write_json(f'project/scenes/{folder}/actors/actor_6.gbsres',actor)
        receipt.append({'runtime_index':7,'center_pixels':room['escort_start'],'anchor_pixels':anchor,'sprite_id':sprite['id'],
                        'bounds_subpixels':bounds,'actor_id':actor['id']})
    anchor,bounds=proof.anchor_for_center(room['spawn'],sprites['player'])
    return {'scene_id':sid,'background_id':bgid,'scene_symbol':room['scene_symbol'],'native_index':index,
            'player_center_pixels':room['spawn'],'player_anchor_pixels':anchor,'player_bounds_subpixels':bounds,
            'native_actor_count':len(receipt),'actors':receipt}


def main():
    sprites={r['id']:r for r in (json.loads(p.read_text()) for p in (ROOT/'assets/sprites').glob('*.gbsres'))}
    sprites['player']=json.loads((ROOT/'assets/sprites/astronaut.png.gbsres').read_text())
    palettes={p['id']:p['colors'] for p in (json.loads(path.read_text()) for path in (ROOT/'project/palettes').glob('*.gbsres'))}
    pal_receipts=[]
    for z,materials in COLORS.items():
        for material,colors in materials.items():
            pid=palette_id(z,material);palettes[pid]=colors
            write_json(f'project/palettes/zone_{z+1:02d}_{material}.gbsres',{'_resourceType':'palette','id':pid,
                       'name':NAMES[z].title()+' '+material.title(),'colors':colors})
            pal_receipts.append({'zone':z,'material':material,'id':pid,'colors_rgb888':colors,
                                 'colors_rgb555':[[v>>3 for v in bytes.fromhex(c)] for c in colors]})
    safe=[''.join(f'{v<<3:02X}' for v in rgb) for rgb in common.HAZARD_RGB555['SAFE']]
    palettes[HAZARD_ID]=safe
    write_json('project/palettes/zones_02_03_hazard.gbsres',{'_resourceType':'palette','id':HAZARD_ID,'name':'Zones Hazard Safe','colors':safe})
    fingerprints=[]
    for number in range(1,4):
        for r in json.loads((ROOT/f'campaign/mission-{number:02d}.json').read_text())['rooms']:
            fingerprints.append(previous.normalized_collision(proof.collision_grid(r)))
    receipt={'scope':'24 new staged native rooms; no active import/build/emulation/browser/hardware',
      'new_room_count':24,'earlier_missions_preserved':[1,2,3],'later_72_rooms':'Not claimed implemented',
      'generator_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
      'helpers_sha256':{name:sha256((ROOT/name).read_bytes()).hexdigest() for name in ('mission_art.py','scrolling_proof_art.py','zone_art.py')},
      'source_shades_rgba':[list(c)+[255] for c in C],'palettes':pal_receipts,
      'hazard_palette_id':HAZARD_ID,'hazard_phase_rgb555':common.HAZARD_RGB555,'missions':[]}
    for number in range(4,10):
        manifest=ROOT/f'campaign/mission-{number:02d}.json';mission=json.loads(manifest.read_text())
        rooms=mission['rooms'];assert len(rooms)==4 and [r['room'] for r in rooms]==list(range(4))
        z=mission['zone'];ids=palette_ids(z);common.PALETTE_IDS=ids
        montage=Image.new('RGB',(768,680),'#111522');md=ImageDraw.Draw(montage)
        mr={'mission':number,'name':mission['name'],'zone':z,'zone_name':NAMES[z],'graph':mission['graph'],
            'manifest_sha256':sha256(manifest.read_bytes()).hexdigest(),'rooms':[]}
        for room in rooms:
            room=dict(room,mission_number=number);n=room['room']
            assert room['width']==48 and room['height']==40 and room['warning_frames']>=42
            assert room['recover_frames']>=96 and room['speed']<=64 and 18<=room['dash_frames']<=24
            strings=common.verify_strings(room);grid=proof.collision_grid(room)
            checks,paths=common.route_validation(room,grid,sprites['player'])
            image,attrs=EnvironmentArt(room).finish();assert set(image.get_flattened_data())<=set(C)
            count=len({image.crop((x,y,x+8,y+8)).tobytes() for y in range(0,320,8) for x in range(0,384,8)})
            assert count<192,(number,n,room['name'],count)
            assert len(grid)==len(attrs)==1920 and set(attrs)<=set(range(7))
            assert proof.expanded(proof.compressed(grid))==grid and proof.expanded(proof.compressed(attrs))==attrs
            hx,hy,hw,hh=room['hazard_rect'];expected={y*48+x for y in range(hy,hy+hh) for x in range(hx,hx+hw)}
            assert {i for i,a in enumerate(attrs) if a==6}==expected
            fingerprint=previous.normalized_collision(grid)
            assert fingerprint not in fingerprints,(number,n,'duplicate/mirrored collision');fingerprints.append(fingerprint)
            png=STAGE/f'assets/backgrounds/mission_{number:02d}_room_{n:02d}.png';png.parent.mkdir(parents=True,exist_ok=True)
            rgba=image.convert('RGBA');assert set(rgba.get_flattened_data())<={c+(255,) for c in C};rgba.save(png,optimize=False)
            native=resources(number,room,attrs,grid,sprites,ids);previews={}
            for state in ('SAFE','AMBER','RED'):
                color=common.color_preview(image,attrs,palettes,state)
                out=STAGE/f'mission_{number:02d}_room_{n:02d}-{state.lower()}.png';color.save(out,optimize=False)
                previews[state]={'path':str(out.relative_to(ROOT)),'sha256':sha256(out.read_bytes()).hexdigest()}
                if state=='SAFE':
                    bx,by=(n%2)*384,(n//2)*340;montage.paste(color,(bx,by+20))
                    md.text((bx+8,by+4),f'{n+1:02d} {room["name"]} / {room["objective"].upper()}',fill='#EDECE2')
                    overlay=color.copy();draw=ImageDraw.Draw(overlay)
                    for x,y,w,h in room['covers']:draw.rectangle((x*8,y*8,(x+w)*8-1,(y+h)*8-1),outline='#EF6159')
                    for i,path in enumerate(paths):draw.line(path,fill=['#FFE276','#70FFBE','#86BFFF','#E5A5FF'][i%4],width=1)
                    overlay.save(STAGE/f'mission_{number:02d}_room_{n:02d}-routes.png',optimize=False)
            mr['rooms'].append({'room':n,'name':room['name'],'objective':room['objective'],'enemy':room['enemy'],
                'dimensions_pixels':[384,320],'dimensions_tiles':[48,40],'mode':'RGBA','alpha':255,'unique_tiles':count,
                'palette_slots':sorted(set(attrs)),'palette_ids':ids,'png_sha256':sha256(png.read_bytes()).hexdigest(),
                'collision_sha256':sha256(bytes(grid)).hexdigest(),'attribute_sha256':sha256(bytes(attrs)).hexdigest(),
                'native_rle_roundtrip':True,'mirror_normalized_collision_sha256':sha256(fingerprint).hexdigest(),
                'strings':strings,'resources':native,'static_checks':checks,'previews':previews})
            print(f'M{number:02d}R{n:02d} {room["name"]}: {count} tiles, {native["native_actor_count"]} actors, routes clear',flush=True)
        montage_path=STAGE/f'mission-{number:02d}-montage.png';montage.save(montage_path,optimize=False)
        mr['montage_sha256']=sha256(montage_path.read_bytes()).hexdigest();receipt['missions'].append(mr)
    assert len(set(fingerprints))==36
    assert sum(r['objective']=='escort' for m in receipt['missions'] if m['zone']==1 for r in m['rooms'])==1
    assert sum(r['objective']=='escort' for m in receipt['missions'] if m['zone']==2 for r in m['rooms'])==1
    receipt['distinct_collision_layouts_including_first12']=36;receipt['mirror_or_half_turn_duplicate_layouts']=False
    write_json('ZONES-02-03-ART-RECEIPTS.json',receipt)


if __name__=='__main__':main()

#!/usr/bin/env python3
"""Author 24 staged native rooms in Signal Archive and Outer Array.

Only campaign/mission-10..15.json and campaign/zones-04-05-assets are written.
Uses original exact native pixels and existing mission/zone helpers. Does not
import active resources, run compilers/emulators/browsers or touch hardware.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from uuid import UUID, uuid5
import json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from PIL import Image,ImageDraw
import scrolling_proof_art as proof
import mission_art as common
import zone_art as zone
STAGE=ROOT/'campaign/zones-04-05-assets'
NAMESPACE=UUID('ae5ae49d-c9c7-5dc0-9cfb-38c27c924f51')
NS={n:uuid5(NAMESPACE,f'mission-{n:02d}') for n in range(10,16)}
ZONE_NAMES={3:'SIGNAL ARCHIVE',4:'OUTER ARRAY'}
C=proof.C

def write_json(relative,value):
 p=STAGE/relative;p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(value,indent=2)+'\n');return p

def item(name,obj,enemy,covers,cells,drone,bounds,hazard=(0,0,0,0),kind='vent',cache=None,escort=None,landmark=''):
 return dict(name=name,objective=obj,enemy=enemy,covers=covers,cells=cells,drone=drone,enemy_bounds=bounds,
             hazard_rect=list(hazard),hazard='none' if not hazard[2] else kind,cache=cache,escort=escort,landmark=landmark)

SPECS={
10:('ARCHIVE UPLINK',[
 item('RECEIVER GALLERY','salvage','charger',[[14,6,3,20],[26,12,3,20],[36,6,3,12],[5,14,6,3],[30,27,12,3],[17,5,8,3],[7,29,6,3]],[[72,72],[192,160],[344,264]],[328,176],[240,144,112,88],(22,27,2,2),landmark='receiver'),
 item('DECODER STACK','repair','hunter',[[6,7,10,3],[21,6,3,11],[34,9,8,3],[8,22,3,11],[18,26,12,3],[34,25,3,9],[28,17,11,3]],[[72,152],[256,56],[328,192]],[264,184],[208,160,136,88],(15,20,12,1),'laser',cache=[352,56],landmark='decoder'),
 item('MEMORY SWITCH','relay','sweeper',[[10,8,16,3],[29,6,3,12],[5,18,11,3],[19,17,3,13],[29,24,14,3],[7,30,8,3],[38,11,4,7]],[[64,56],[344,168],[248,280]],[264,160],[216,112,144,136],(34,32,2,2),landmark='memory'),
 item('ARCHIVE GUARDIAN','core','sweeper',[[16,6,3,10],[34,6,3,10],[16,23,3,10],[34,23,3,10],[5,15,8,3],[26,31,6,3],[40,15,3,9],[8,29,5,3]],[[80,72],[312,104],[192,280]],[224,152],[168,104,144,112],(21,25,10,1),'laser',landmark='archive_guard'),]),
11:('SIGNAL RESCUE',[
 item('PACKET CONCOURSE','salvage','hunter',[[7,8,12,3],[23,6,3,10],[32,14,10,3],[13,18,3,14],[23,25,13,3],[36,29,3,6],[5,24,5,3]],[[64,40],[304,88],[248,288]],[304,152],[224,136,128,112],(23,18,2,2),landmark='packet'),
 item('CARRIER REPAIR','repair','charger',[[5,7,5,8],[17,6,14,3],[35,6,3,17],[12,19,12,3],[6,27,8,3],[25,28,11,3],[24,12,3,8]],[[96,56],[328,184],[176,264]],[256,160],[224,96,112,144],(17,24,12,1),'laser',cache=[344,56],landmark='carrier'),
 item('CREW TRANSIT','escort','hunter',[[17,14,12,7],[5,11,6,4],[38,11,5,7],[6,25,6,2],[18,30,14,2],[38,29,4,2]],[[344,248],[200,96],[80,56]],[328,176],[288,144,64,96],(16,24,12,1),'laser',escort=[[88,280],[344,280],[344,248],[344,216],[272,216],[272,96],[200,96],[120,96],[120,56],[80,56],[120,56],[120,240],[88,240],[88,264],[48,264],[48,296]],landmark='crew'),
 item('SIGNAL WARDEN','core','charger',[[12,7,5,10],[28,5,12,3],[35,13,3,11],[8,23,12,3],[23,28,4,7],[33,30,9,3],[5,10,3,6],[23,8,4,4]],[[72,64],[328,88],[344,272]],[200,168],[144,128,176,104],(28,25,2,2),landmark='signal_guard'),]),
12:('LENS ALIGNMENT',[
 item('LENS STACK','salvage','charger',[[6,8,9,3],[18,13,3,18],[31,8,3,16],[37,25,6,3],[5,25,10,3],[24,5,13,3],[24,22,3,9]],[[72,40],[296,136],[344,264]],[208,112],[176,80,144,136],(34,27,2,2),landmark='lenses'),
 item('RELAY PRISM','relay','sweeper',[[8,8,6,3],[19,7,3,9],[29,10,7,3],[13,19,3,13],[23,25,12,3],[39,21,3,9],[6,31,5,3]],[[48,56],[328,152],[192,240]],[232,168],[168,136,160,112],(18,18,14,1),'laser',cache=[344,64],landmark='prism'),
 item('SHIELD FEED','repair','hunter',[[5,9,10,3],[22,6,3,21],[31,8,10,3],[9,20,3,10],[32,22,3,11],[16,29,11,3],[38,29,4,5]],[[88,56],[304,160],[152,280]],[304,112],[216,96,136,128],(35,17,2,2),landmark='shield_feed'),
 item('LENS SENTINEL','core','hunter',[[18,6,3,12],[33,5,3,10],[7,15,8,3],[38,18,5,3],[18,26,3,9],[29,29,13,3],[8,30,7,3],[27,8,3,4]],[[72,56],[312,128],[200,248]],[224,168],[168,104,176,128],(24,24,12,1),'laser',landmark='lens_guard'),]),
13:('BEACON ARRAY',[
 item('ARRAY FOOT','salvage','sweeper',[[8,6,3,14],[18,8,13,3],[34,7,3,19],[14,24,3,10],[23,21,11,3],[5,29,7,3],[39,28,5,4]],[[48,64],[248,128],[328,280]],[232,144],[152,112,136,144],(23,31,2,2),landmark='array'),
 item('BEACON REPAIR','repair','hunter',[[12,6,3,15],[26,5,11,3],[32,13,3,12],[5,24,11,3],[20,22,7,3],[37,27,5,8],[18,31,9,3]],[[72,72],[296,104],[224,280]],[232,136],[176,104,160,136],(16,19,12,1),'laser',cache=[352,72],landmark='beacon'),
 item('NAV RELAYS','relay','charger',[[6,7,12,3],[22,7,3,14],[34,9,7,3],[10,18,3,15],[23,26,13,3],[37,22,3,10],[5,29,4,3]],[[80,104],[328,144],[192,288]],[272,176],[208,136,144,128],(26,21,2,2),landmark='navigation'),
 item('ARRAY GUARDIAN','core','charger',[[17,7,3,11],[30,7,3,11],[7,22,12,3],[36,14,6,3],[22,29,11,3],[8,29,5,3],[39,26,3,8],[10,6,4,3]],[[64,72],[336,80],[272,264]],[224,168],[144,112,144,120],(23,25,12,1),'laser',landmark='array_guard'),]),
14:('NAVIGATION RESCUE',[
 item('ANTENNA WALK','salvage','hunter',[[6,7,3,20],[17,7,17,3],[27,15,3,13],[36,9,3,8],[11,26,10,3],[34,31,9,3],[18,16,3,6]],[[112,56],[336,152],[200,264]],[256,128],[216,96,136,144],(19,23,2,2),landmark='antenna'),
 item('RETURN BUS','repair','sweeper',[[11,5,3,13],[22,12,14,3],[36,6,4,8],[6,23,10,3],[26,24,3,11],[36,29,6,3],[17,31,6,3]],[[72,72],[192,160],[328,200]],[288,176],[208,136,144,120],(30,20,12,1),'laser',cache=[344,64],landmark='return_bus'),
 item('SURVEYOR ROUTE','escort','sweeper',[[6,14,10,3],[21,9,13,3],[22,20,7,5],[36,17,5,10],[9,26,13,2],[27,29,5,3],[41,5,3,5]],[[88,248],[296,56],[280,248]],[344,184],[272,144,80,88],(19,15,14,1),'laser',escort=[[88,280],[88,248],[24,248],[24,176],[152,176],[152,56],[296,56],[296,112],[360,112],[360,248],[280,248],[280,280],[48,280],[48,296]],landmark='surveyor'),
 item('SKY WARDEN','core','sweeper',[[14,5,3,14],[33,9,3,15],[6,18,8,3],[21,7,9,3],[22,27,4,7],[34,29,9,3],[5,29,9,3],[38,6,4,3]],[[72,56],[328,104],[152,264]],[224,152],[144,96,176,136],(27,25,2,2),landmark='sky_guard'),]),
15:('GROUND THE JAMMER',[
 item('STATIC RIDGE','salvage','charger',[[6,7,17,3],[27,12,15,3],[10,18,16,3],[31,24,10,3],[6,29,13,3],[23,30,3,6],[38,5,3,4]],[[72,104],[344,176],[248,256]],[232,152],[184,128,160,120],(26,29,12,1),'laser',landmark='static'),
 item('GROUND RELAYS','relay','hunter',[[7,6,3,12],[18,5,3,18],[30,11,10,3],[8,23,12,3],[29,24,3,10],[38,28,5,4],[23,31,4,3]],[[112,56],[328,152],[200,288]],[256,168],[200,128,144,144],(14,16,2,2),cache=[344,56],landmark='ground'),
 item('EMITTER REPAIR','repair','sweeper',[[5,9,7,3],[17,7,12,3],[34,5,3,15],[12,18,3,14],[23,20,10,3],[32,28,11,3],[4,30,4,3]],[[72,56],[256,128],[328,264]],[232,136],[168,104,152,144],(17,25,12,1),'laser',landmark='emitter'),
 item('JAMMER CORE','core','hunter',[[16,5,3,12],[31,5,3,12],[7,19,8,3],[38,18,5,9],[18,28,4,7],[28,29,9,3],[7,30,6,3],[24,7,4,4]],[[72,64],[344,128],[312,280]],[216,168],[160,112,168,128],(26,24,2,2),landmark='jammer_guard'),]),
}

PALETTE_COLORS={
3:[['D9F3FF','9CC7EB','35485B','0B102A'],['E4F0FF','7AAABF','294866','080E28'],['FFFBD9','A5DFF1','315577','0B1730'],['FDEAB2','DAAB71','614C62','12142A'],['DEF8EF','6BDDC5','37586B','081728'],['E8DCFF','AB9BCD','494568','13132D']],
4:[['FFE7E8','A89BCC','313C58','080F24'],['FFF0CD','C7AA73','4A5566','0C1831'],['DCF6FF','80CEE7','1F4B6B','051728'],['FFDEA7','C1A168','594B53','151324'],['FFDFFE','BC95D5','59446C','130F25'],['E4F8EE','96C2BD','35546B','101829']],
}

def palette_ids(z):return [str(uuid5(NAMESPACE,f'zone-{z}-palette-{s}')) for s in range(7)]+['default-ui']

class RoomsArt(zone.ZoneArt):
 def base(self):
  proof.Art.base(self)
  k=self.room['room'];z=self.room['zone']
  for ty in range(3,self.h-1):
   for tx in range(1,self.w-1):
    x,y=tx*8,ty*8;self.rect((x,y,x+7,y+7),1)
    if z==3:
     if ty%(3 if k%2 else 4)==0:self.line((x,y+7,x+7,y+7),0)
     if tx%(4 if k%2 else 3)==0:self.line((x+7,y+2,x+7,y+5),0)
     if (tx+2*ty)%7==0:self.point((x+2,y+2),2)
    else:
     if ty%3==2:self.line((x,y+7,x+7,y+7),0)
     if tx%5==0:self.line((x+7,y,x+7,y+7),0)
     if (tx+ty+k)%9==0:self.point((x+3,y+2),2)

 def lens(self,cx,cy,tw=6,th=6):
  x,y=cx-tw*4,cy-th*4;self.region(x//8,y//8,tw,th,4);self.rect((x,y,x+tw*8-1,y+th*8-1),0)
  self.draw.ellipse((x+3,y+3,x+tw*8-4,y+th*8-4),outline=C[1])
  inset=min(9,tw*2,th*2)
  self.draw.ellipse((x+inset,y+inset,x+tw*8-inset-1,y+th*8-inset-1),outline=C[2])
  self.line((cx-6,cy,cx+5,cy),2);self.line((cx,cy-6,cx,cy+5),2)

 def comb(self,x,y,tw,th=2):
  self.plate(x,y,tw*8,th*8,'instrument')

 def stars(self,x,y,tw,th):
  self.region(x//8,y//8,tw,th,1);self.rect((x,y,x+tw*8-1,y+th*8-1),0)
  for oy in range(th):
   for ox in range(tw):
    px,py=x+ox*8,y+oy*8
    if (ox+oy)%3==0:self.point((px+3,py+3),2)
    if (ox*2+oy)%5==0:self.line((px+2,py+4,px+4,py+4),1)

 def route_arrows(self):
  route=self.room['escort_route']
  for a,b in zip(route,route[1:]):
   if a[0]==b[0]:
    direction=1 if b[1]>a[1] else -1
    for cy in range(min(a[1],b[1])+16,max(a[1],b[1])-8,32):
     cx=a[0];self.line([(cx-2,cy-direction*2),(cx,cy),(cx+2,cy-direction*2)],2)
   else:
    direction=1 if b[0]>a[0] else -1
    for cx in range(min(a[0],b[0])+16,max(a[0],b[0])-8,32):
     cy=a[1];self.line([(cx-direction*2,cy-2),(cx,cy),(cx-direction*2,cy+2)],2)

 def landmarks(self):
  kind=self.room['art_kind'];cells=self.room['cells'];dx,dy=self.room['drone']
  if kind=='receiver':
   self.comb(40,40,7);self.comb(288,216,8);self.glyph(192,144,64,48,'axis')
   self.channel([(72,72),(96,72),(96,160),(192,160)]);self.channel([(344,264),(352,264),(352,200)])
  elif kind=='decoder':
   for x,y in [(40,120),(232,32),(304,160)]:self.comb(x,y,5)
   for x in (128,144,160):self.channel([(x,88),(x,216)])
   self.glyph(256,232,48,32,'axis')
  elif kind=='memory':
   self.comb(48,32,7);self.comb(320,136,4);self.comb(224,248,6)
   self.channel([(72,56),(88,56),(88,128),(248,128),(248,280)]);self.channel([(248,128),(344,128),(344,168)])
  elif kind=='archive_guard':
   self.glyph(224,152,80,64,'warden');self.comb(48,40,7);self.comb(288,72,7)
   for x in (184,264):self.channel([(x,104),(x,208)])
  elif kind=='packet':
   for x,y in [(48,32),(280,56),(224,256)]:self.comb(x,y,6)
   for x in (144,160):self.channel([(x,96),(x,248),(248,248)])
   self.glyph(256,152,48,32,'axis')
  elif kind=='carrier':
   for cx,cy in cells:self.lens(cx,cy-24,4,2)
   self.channel([(96,56),(128,56),(128,184),(328,184)]);self.glyph(256,232,48,32,'halo')
  elif kind=='crew':
   self.plate(48,32,48,16,'medical');self.comb(176,64,6);self.plate(312,224,48,16,'medical')
   self.route_arrows();self.glyph(184,192,48,32,'axis')
  elif kind=='signal_guard':
   self.glyph(200,168,64,64,'axis');self.comb(48,32,7);self.comb(304,56,7)
   for y in (112,128):self.channel([(152,y),(248,y),(248,216)])
  elif kind=='lenses':
   for cx,cy in [(72,56),(200,96),(328,232)]:self.lens(cx,cy,6,4)
   self.channel([(200,112),(216,112),(216,216),(328,216)])
  elif kind=='prism':
   self.glyph(232,168,64,48,'warden');self.comb(32,32,6);self.comb(304,120,6)
   for cx,cy in cells:self.channel([(cx,cy),(184,cy),(184,216)])
  elif kind=='shield_feed':
   self.comb(64,32,6);self.comb(280,128,7);self.comb(128,248,6)
   self.glyph(304,216,48,48,'axis');self.channel([(88,56),(136,56),(136,192)])
  elif kind=='lens_guard':
   self.lens(224,168,10,8);self.comb(48,32,7);self.comb(288,96,7)
   self.channel([(224,128),(224,104),(312,104)])
  elif kind=='array':
   self.stars(144,96,9,7);self.stars(296,248,8,5);self.comb(24,40,6)
   self.glyph(248,128,48,32,'axis')
  elif kind=='beacon':
   for cx,cy in cells:self.lens(cx,cy-24,4,2)
   self.stars(176,120,7,6);self.channel([(72,72),(88,72),(88,200),(224,200),(224,280)])
  elif kind=='navigation':
   self.comb(56,72,6);self.comb(304,112,6);self.comb(168,256,6)
   self.glyph(248,176,64,48,'axis');self.stars(120,40,5,5)
  elif kind=='array_guard':
   self.glyph(224,168,80,64,'halo');self.stars(48,40,6,4);self.stars(312,56,6,4)
   self.channel([(224,128),(224,88),(336,88)])
  elif kind=='antenna':
   for x in (128,144,160):self.channel([(x,88),(x,200)])
   self.comb(88,32,8);self.comb(312,120,6);self.stars(168,232,8,6)
  elif kind=='return_bus':
   self.channel([(72,72),(152,72),(152,160),(192,160)]);self.channel([(192,160),(192,232),(328,232),(328,200)])
   self.comb(48,40,6);self.comb(168,136,6);self.comb(304,168,7);self.stars(304,32,6,4)
  elif kind=='surveyor':
   self.stars(48,224,8,4);self.stars(272,32,8,3);self.comb(256,216,6)
   self.route_arrows();self.plate(64,256,40,16,'medical')
  elif kind=='sky_guard':
   self.glyph(224,152,80,64,'axis');self.stars(40,32,6,3);self.stars(304,72,6,3)
   for x in (184,264):self.channel([(x,104),(x,192)])
  elif kind=='static':
   self.comb(48,72,7);self.comb(320,144,5);self.comb(224,232,6)
   for y in (112,128):self.channel([(104,y),(248,y),(248,y+40)])
  elif kind=='ground':
   self.glyph(232,168,48,48,'halo');self.comb(88,32,6);self.comb(304,120,6)
   for cx,cy in cells:self.channel([(cx,cy),(216,cy),(216,176)])
  elif kind=='emitter':
   for cx,cy in cells:self.lens(cx,cy-24,4,2)
   self.stars(200,104,7,5);self.channel([(72,56),(112,56),(112,136),(256,136)])
  else:
   self.glyph(216,168,80,64,'warden');self.stars(48,40,6,4);self.stars(320,104,6,4)
   self.comb(288,248,7);self.channel([(216,128),(216,104),(344,104)])

 def pad(self,cx,cy):
  proof.Art.pad(self,cx,cy)
  if self.room['objective'] in ('relay','escort'):
   index=self.room['cells'].index([cx,cy])
   for i in range(index+1):self.line((cx-4+i*3,cy+2,cx-4+i*3,cy+5),3)

 def finish(self):
  self.base();self.landmarks()
  for cover in self.room['covers']:self.cover(*cover)
  for center in self.room['cells']:self.pad(*center)
  self.hazard();self.cache();self.dock()
  return self.image,self.attributes


def make_manifest(number,name,configs):
 z=3 if number<=12 else 4
 rooms=[]
 for i,config in enumerate(configs):
  r=deepcopy(config);cache=r.pop('cache');escort=r.pop('escort');r['art_kind']=r.pop('landmark')
  r.update(room=i,width=48,height=40,zone=z,spawn=[48,296],terminal=[48,296],dock_rect=[24,272,48,40],
           coordinate_convention={'spawn_terminal_cells_drone_escort':'Native integer actor centers; player offset7,3',
           'dock_rect_enemy_bounds':'Pixel x,y,width,height rectangles','covers_hazard_rect':'Tile x,y,width,height rectangles'},
           scene_symbol=f'scene_mission_{number:02d}_room_{i:02d}',warning_frames=48 if r['objective']=='core' else 44,
           dash_frames=24 if r['enemy']=='sweeper' else (20 if number%2 else 18),recover_frames=120 if r['objective']=='core' else 112,
           speed=60 if z==3 else 64)
  if r['objective']=='salvage':r.update(brief1='GRAB THREE CELLS',brief2='FIND THE COVER GAPS')
  elif r['objective']=='repair':r.update(brief1='HOLD B AT EACH PANEL',brief2='POWER THE NEXT PATH',hold_ticks=45)
  elif r['objective']=='relay':r.update(brief1='HOLD B AT LIT RELAY',brief2='ACTIVATE IN ORDER',hold_ticks=30)
  elif r['objective']=='escort':r.update(brief1='STAY CLOSE TO CREW',brief2='THREE MARKERS THEN DOCK',escort_start=escort[0],escort_route=escort)
  else:r.update(brief1='PULSE WHEN CORE OPEN',brief2='THREE HITS THEN DOCK',core_hp=3)
  # Text row uses20glyphs; escort briefing shortened without changing the goal.
  if len(r['brief2'])>20:r['brief2']='MARKERS THEN DOCK'
  if cache:r.update(optional_cache_marker=cache,optional_cache={'hold_ticks':20,'reward':'persistent mission badge','floor_marker':'gold diamond','runtime_support':'Existing B20 native trigger; stage only, not gameplay-qualified'})
  rooms.append(r)
 return dict(mission=number-1,name=name,zone=z,zone_name=ZONE_NAMES[z],room_count=4,
             graph={'entry':0,'middle_choices':[1,2],'middle_rule':'Visit both in either order','final':3},
             implementation_scope='Four new staged native rooms. Existing objectives only; no reflector, forcefield or paired-enemy claims.',rooms=rooms)


def main():
 STAGE.mkdir(exist_ok=True)
 manifests={n:make_manifest(n,*SPECS[n]) for n in range(10,16)}
 for n,m in manifests.items():(ROOT/f'campaign/mission-{n:02d}.json').write_text(json.dumps(m,indent=2)+'\n')
 sprites={r['id']:r for r in (json.loads(p.read_text()) for p in (ROOT/'assets/sprites').glob('*.gbsres'))}
 sprites['player']=json.loads((ROOT/'assets/sprites/astronaut.png.gbsres').read_text())
 palettes={r['id']:r['colors'] for r in (json.loads(p.read_text()) for p in (ROOT/'project/palettes').glob('*.gbsres'))}
 for z in (3,4):
  ids=palette_ids(z)
  colors=PALETTE_COLORS[z]+[[''.join(f'{v<<3:02X}' for v in rgb) for rgb in common.HAZARD_RGB555['SAFE']]]
  for slot,col in enumerate(colors):
   write_json(f'project/palettes/zone{z+1:02d}_slot{slot}.gbsres',{'_resourceType':'palette','id':ids[slot],'name':f'{ZONE_NAMES[z].title()} Slot {slot}','colors':col})
   palettes[ids[slot]]=col
 fingerprints={}
 for p in sorted((ROOT/'campaign').glob('mission-*.json')):
  number=int(p.stem.split('-')[-1])
  if number in range(10,16):continue
  for room in json.loads(p.read_text())['rooms']:
   if room.get('width')==48 and room.get('height')==40:
    fingerprints[zone.normalized_collision(proof.collision_grid(room))]=f'{number:02d}/{room["room"]}'
 previous_count=len(fingerprints)
 zone.STAGE=STAGE;zone.NS=NS
 receipt={'scope':'24newstagednative rooms; no active project changes/build/emulation/browser/device',
          'new_room_count':24,'zones':{str(z):ZONE_NAMES[z] for z in (3,4)},
          'source_shades_rgba':[list(c)+[255] for c in C],'generator_path':str(Path(__file__).relative_to(ROOT)),
          'generator_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
          'helpers_sha256':{name:sha256((ROOT/name).read_bytes()).hexdigest() for name in ('mission_art.py','zone_art.py','scrolling_proof_art.py')},
          'prior_collision_layouts_compared':previous_count,'hazard_phase_rgb555':common.HAZARD_RGB555,'missions':[]}
 ids=[]
 for number,mission in manifests.items():
  common.PALETTE_IDS=zone.PALETTE_IDS=palette_ids(mission['zone'])
  assert sum(r['objective']=='escort' for r in mission['rooms'])<=1
  assert sum('optional_cache_marker' in r for r in mission['rooms'])==1
  montage=Image.new('RGB',(768,680),'#111522');md=ImageDraw.Draw(montage)
  mr={'mission':number,'name':mission['name'],'graph':mission['graph'],'zone':mission['zone'],
      'manifest_sha256':sha256((ROOT/f'campaign/mission-{number:02d}.json').read_bytes()).hexdigest(),'rooms':[]}
  for room in mission['rooms']:
   n=room['room'];strings=common.verify_strings(room);grid=proof.collision_grid(room)
   print(f'Check M{number:02d}R{n:02d} {room["name"]}',flush=True)
   checks,paths=common.route_validation(room,grid,sprites['player'])
   image,attrs=RoomsArt(room).finish()
   count=len({image.crop((x,y,x+8,y+8)).tobytes() for y in range(0,320,8) for x in range(0,384,8)})
   assert count<192,(room['name'],count)
   assert len(grid)==len(attrs)==1920 and set(attrs)<=set(range(7))
   assert proof.expanded(proof.compressed(grid))==grid and proof.expanded(proof.compressed(attrs))==attrs
   hx,hy,hw,hh=room['hazard_rect'];expected={y*48+x for y in range(hy,hy+hh) for x in range(hx,hx+hw)}
   assert {i for i,a in enumerate(attrs) if a==6}==expected
   norm=zone.normalized_collision(grid);assert norm not in fingerprints,(room['name'],'duplicate/mirror',fingerprints.get(norm));fingerprints[norm]=f'{number:02d}/{n}'
   png=STAGE/f'assets/backgrounds/mission_{number:02d}_room_{n:02d}.png';png.parent.mkdir(parents=True,exist_ok=True)
   rgba=image.convert('RGBA');assert set(rgba.get_flattened_data())<={c+(255,) for c in C};rgba.save(png,optimize=False)
   resources=zone.native_resources(number,room,attrs,grid,sprites)
   assert resources['native_index']==146+(number-10)*4+n and resources['player_anchor_pixels']==[41,293]
   # New resource scripts belong to the encounter hook; no legacy events leak.
   for actor_path in (STAGE/f'project/scenes/mission_{number:02d}_room_{n:02d}/actors').glob('*.gbsres'):
    actor=json.loads(actor_path.read_text())
    for key in ('script','startScript','updateScript','hit1Script','hit2Script','hit3Script'):actor[key]=[]
    actor_path.write_text(json.dumps(actor,indent=2)+'\n')
   previews={}
   for state in ('SAFE','AMBER','RED'):
    color=common.color_preview(image,attrs,palettes,state);output=STAGE/f'mission_{number:02d}_room_{n:02d}-{state.lower()}.png';color.save(output,optimize=False)
    previews[state]={'path':str(output.relative_to(ROOT)),'sha256':sha256(output.read_bytes()).hexdigest()}
    if state=='SAFE':
     bx,by=(n%2)*384,(n//2)*340;montage.paste(color,(bx,by+20));md.text((bx+8,by+4),f'{number:02d}-{n+1} {room["name"]} / {room["objective"].upper()}',fill='#EDF2F1')
     overlay=color.copy();draw=ImageDraw.Draw(overlay)
     for x,y,w,h in room['covers']:draw.rectangle((x*8,y*8,(x+w)*8-1,(y+h)*8-1),outline='#F5696D')
     for i,path in enumerate(paths):draw.line(path,fill=['#FFE276','#70FFBE','#86BFFF','#E5A5FF'][i%4],width=1)
     overlay.save(STAGE/f'mission_{number:02d}_room_{n:02d}-routes.png',optimize=False)
   if room.get('optional_cache_marker'):
    cx,cy=room['optional_cache_marker'];near=min(((px-cx)**2+(py-cy)**2)**.5 for path in paths for px,py in path)
    checks['optional_cache'].update(runtime_support='B20badge exists; staged art only',minimum_distance_to_reference_route_pixels=round(near,1))
   mr['rooms'].append({'room':n,'name':room['name'],'objective':room['objective'],'enemy':room['enemy'],
      'dimensions_pixels':[384,320],'dimensions_tiles':[48,40],'mode':'RGBA','alpha':255,'unique_tiles':count,
      'palette_slots':sorted(set(attrs)),'palette_ids':common.PALETTE_IDS,'png_sha256':sha256(png.read_bytes()).hexdigest(),
      'collision_sha256':sha256(bytes(grid)).hexdigest(),'attribute_sha256':sha256(bytes(attrs)).hexdigest(),
      'mirror_normalized_collision_sha256':sha256(norm).hexdigest(),'native_rle_roundtrip':True,
      'strings':strings,'resources':resources,'static_checks':checks,'previews':previews})
   ids.append({'mission':number,'room':n,**{k:resources[k] for k in ('scene_id','background_id','scene_symbol','native_index')}})
   print(f'  -> {count}tiles, {resources["native_actor_count"]}actors, collision-clear routes',flush=True)
  montage_path=STAGE/f'mission-{number:02d}-montage.png';montage.save(montage_path,optimize=False)
  mr['montage_sha256']=sha256(montage_path.read_bytes()).hexdigest();receipt['missions'].append(mr)
 for z in (3,4):assert sum(r['objective']=='escort' for m in manifests.values() if m['zone']==z for r in m['rooms'])==1
 receipt.update(distinct_new_collision_layouts=24,distinct_total_collision_layouts=len(fingerprints),mirror_or_half_turn_duplicate_layouts=False)
 write_json('ZONES-04-05-ART-RECEIPTS.json',receipt);write_json('IDS.json',ids)
 print('Frozen24roomstaging receipts complete.',flush=True)

if __name__=='__main__':main()

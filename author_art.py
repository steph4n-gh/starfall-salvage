from PIL import Image, ImageDraw
from pathlib import Path
root=Path(__file__).parent
C=['#071821','#306850','#86c06c','#e0f8cf']
bg=Image.new('RGB',(160,144),C[0]);d=ImageDraw.Draw(bg)
# star field and moon perimeter
for x,y in [(4,4),(25,9),(51,3),(85,10),(114,5),(146,11),(134,2),(68,13)]:d.point((x,y),fill=C[3])
for y in range(3,17):
 for x in range(1,19):
  d.rectangle((x*8,y*8,x*8+7,y*8+7),fill=C[1]);d.point((x*8+2,y*8+5),fill=C[2])
# rock walls
for x,y,w,h in [(0,2,20,1),(0,3,1,15),(19,3,1,15),(0,17,20,1),(6,5,3,3),(6,10,3,2),(11,7,3,2)]:
 for ty in range(y,y+h):
  for tx in range(x,x+w):
   a,b=tx*8,ty*8
   d.rectangle((a,b,a+7,b+7),fill=C[0]);d.polygon([(a,b+2),(a+3,b),(a+7,b+2),(a+7,b+6),(a+2,b+7)],fill=C[2]);d.line((a+1,b+3,a+4,b+1,a+6,b+3),fill=C[3]);d.line((a+2,b+6,a+6,b+5),fill=C[1])
# panel banks at north and beacon pads for cells
for x,y in [(2,4),(14,4),(14,10)]:
 d.rectangle((x*8,y*8,x*8+23,y*8+15),fill=C[0]);d.rectangle((x*8+1,y*8+1,x*8+22,y*8+14),outline=C[2]);d.line((x*8+4,y*8+12,x*8+19,y*8+12),fill=C[3])
for x in [6,10]:
 d.rectangle((x*8,24,x*8+23,31),fill=C[0]);d.rectangle((x*8+1,25,x*8+22,30),outline=C[3]);d.line((x*8+8,25,x*8+8,30),fill=C[2]);d.line((x*8+15,25,x*8+15,30),fill=C[2])
# parked ship, body, twin engines, canopy
ox,oy=56,104
d.polygon([(ox+8,oy+24),(ox+4,oy+18),(ox,oy+20),(ox+4,oy+8),(ox+12,oy+8),(ox+16,oy),(ox+24,oy),(ox+28,oy+8),(ox+36,oy+8),(ox+40,oy+20),(ox+36,oy+18),(ox+32,oy+24)],fill=C[0])
d.polygon([(ox+7,oy+17),(ox+12,oy+10),(ox+16,oy+3),(ox+23,oy+3),(ox+28,oy+10),(ox+33,oy+17),(ox+28,oy+20),(ox+12,oy+20)],fill=C[3])
d.rectangle((ox+15,oy+6,ox+24,oy+13),fill=C[0]);d.rectangle((ox+17,oy+7,ox+22,oy+11),fill=C[2]);d.rectangle((ox+9,oy+20,ox+13,oy+25),fill=C[2]);d.rectangle((ox+27,oy+20,ox+31,oy+25),fill=C[2])
bg.save(root/'assets/backgrounds/moonbase.png')
# exact 16x16 pixel astronaut frames: down, down step, up, up step, right, right step
T='#65ff00';S=[C[0],C[2],C[3]]
rows=[
['................','.....000000.....','....02222220....','...0222222220...','...0200000020...','...0201111020...','...0201111020...','....02222220....','...0022222200...','..02021112020...','..02021112020...','...002222200....','....0222220.....','....0220220.....','....000.000.....','................'],
['................','.....000000.....','....02222220....','...0222222220...','...0222222220...','...0211111120...','...0211111120...','....02222220....','...0022222200...','..02021112020...','..02021112020...','...002222200....','....0222220.....','....0220220.....','....000.000.....','................'],
['................','.....00000......','....0222220.....','...022222220....','...022000000....','...022011110....','...022011110....','....0222220.....','...00222220.....','..0102222220....','..0102220020....','...00222000.....','....022220......','....022020......','....000.00......','................']]
out=Image.new('RGB',(96,16),T)
for direction,grid in enumerate(rows):
 for step in range(2):
  for y,row in enumerate(grid):
   for x,v in enumerate(row):
    if v!='.':out.putpixel((direction*32+step*16+x,y),tuple(bytes.fromhex(S[int(v)][1:])))
  if step:
   dr=ImageDraw.Draw(out);base=direction*32+16;dr.rectangle((base+4,14,base+6,14),fill=T);dr.line((base+4,15,base+6,15),fill=S[0])
out.save(root/'assets/sprites/astronaut.png')
cell=Image.new('RGB',(16,16),T);q=ImageDraw.Draw(cell)
q.polygon([(5,2),(10,2),(12,4),(12,12),(10,14),(5,14),(3,12),(3,4)],fill=S[0]);q.rectangle((5,4,10,11),fill=S[2]);q.rectangle((6,5,9,10),fill=S[1]);q.line((7,5,7,10),fill=S[2]);q.rectangle((6,1,9,2),fill=S[0]);cell.save(root/'assets/sprites/power_cell.png')
terminal=Image.new('RGB',(16,16),T);q=ImageDraw.Draw(terminal);q.rectangle((3,3,12,12),fill=S[0]);q.rectangle((4,4,11,9),fill=S[2]);q.line((6,7,7,8,10,5),fill=S[0]);q.rectangle((6,13,9,14),fill=S[0]);terminal.save(root/'assets/sprites/ship_terminal.png')
print('Authored moonbase, astronaut, power cell and terminal PNGs.')

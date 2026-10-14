"""Author exact native 160x144 window artwork and its banked 2bpp payloads.

This source is deliberately pixel based. PNGs use GB Studio's four manual
source shades; per-tile palette attributes provide the displayed GBC colors.
Run with Pillow; no ROM, project, scene, sprite, or device mutations are made.
"""
from pathlib import Path
import hashlib
import json
import random
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
SHADES = [(7, 24, 33), (48, 104, 80), (134, 192, 108), (224, 248, 207)]
KINDS = ("title", "launch", "pause", "result", "ending", "failure", "upgrade")
QUIET = {"title": 12, "launch": 6, "pause": 5, "result": 6,
         "ending": 8, "failure": 5, "upgrade": 4}

# Hardware RGB555 triples. Every palette shares the text panel's dark backdrop.
DARK = (2, 4, 7)
BASE_PALETTES = [
    [DARK, (4, 8, 13), (10, 16, 23), (24, 29, 31)],
    [DARK, (11, 9, 8), (25, 18, 10), (31, 29, 22)],
    [DARK, (3, 11, 14), (9, 24, 25), (25, 31, 31)],
    [DARK, (10, 8, 17), (21, 15, 27), (31, 27, 31)],
    [DARK, (13, 7, 7), (27, 14, 8), (31, 27, 15)],
    [DARK, (7, 12, 17), (16, 23, 26), (28, 31, 31)],
    [DARK, (12, 5, 7), (29, 9, 9), (31, 25, 10)],
]
ZONE_HULL = [BASE_PALETTES[1],
             [DARK, (4, 11, 16), (9, 23, 27), (26, 31, 31)],
             [DARK, (10, 7, 18), (22, 14, 29), (31, 28, 31)]]

FONT = {
    "A": [14,17,17,31,17,17,17], "F": [31,16,16,30,16,16,16],
    "E": [31,16,16,30,16,16,31],
    "G": [14,17,16,23,17,17,15], "L": [16,16,16,16,16,16,31],
    "R": [30,17,17,30,20,18,17], "S": [15,16,16,14,1,1,30],
    "T": [31,4,4,4,4,4,4], "V": [17,17,17,17,17,10,4],
}


class Canvas:
    def __init__(self):
        self.image = Image.new("P", (160, 144), 0)
        self.image.putpalette([v for rgb in SHADES for v in rgb] + [0] * (768 - 12))
        self.d = ImageDraw.Draw(self.image)
        self.attrs = [8] * 360  # CGB VRAM bank 1, BG palette zero.

    def palette_rect(self, rect, palette):
        x0,y0,x1,y1 = rect
        for ty in range(max(0,y0//8), min(18,y1//8+1)):
            for tx in range(max(0,x0//8), min(20,x1//8+1)):
                self.attrs[ty*20+tx] = 8 | palette

    def stars(self, bottom, seed, amount=24):
        rng = random.Random(seed)
        for _ in range(amount):
            x = rng.randrange(3,157); y = rng.randrange(2,bottom)
            self.d.point((x,y), fill=2 if rng.randrange(3) else 3)
        for x,y in [(9,8),(145,12),(121,75)]:
            if y < bottom:
                self.d.line((x-1,y,x+1,y), fill=2)
                self.d.line((x,y-1,x,y+1), fill=2)
                self.d.point((x,y), fill=3)

    def logo(self, text, x, y, scale=2):
        # Hard edged block letters with a one pixel cast shadow.
        for shade, dx, dy in [(1,1,2),(3,0,0)]:
            for i, ch in enumerate(text):
                for yy, row in enumerate(FONT[ch]):
                    for xx in range(5):
                        if row & (1 << (4-xx)):
                            sx=x+i*6*scale+xx*scale+dx; sy=y+yy*scale+dy
                            self.d.rectangle((sx,sy,sx+scale-1,sy+scale-1), fill=shade)

    def divider(self, y, palette=2):
        self.d.line((0,y,159,y), fill=1)
        self.d.line((8,y-1,43,y-1), fill=2)
        self.d.line((116,y-1,151,y-1), fill=2)
        for x in [2,5,154,157]: self.d.point((x,y-1), fill=3)
        self.palette_rect((0,y-1,159,y), palette)

    def planet(self, x, y, r):
        d=self.d
        d.ellipse((x-r,y-r,x+r,y+r), fill=1)
        d.ellipse((x-r,y-r,x+r-3,y+r-3), fill=2)
        d.arc((x-r,y-r,x+r,y+r), 192, 295, fill=3, width=1)
        # Deliberate blocks of craters and land, no smooth raster gradients.
        d.ellipse((x-7,y-5,x+4,y+4), fill=1)
        d.ellipse((x-8,y-6,x+2,y+2), outline=3)
        d.rectangle((x+5,y-12,x+9,y-9), fill=1)
        d.line((x-11,y+9,x-5,y+11,x+1,y+9), fill=3)
        d.line((x+10,y+4,x+12,y+10), fill=1)

    def ship(self, x, y, scale=1, exhaust=True):
        """Salvage skiff profile: swept fins, glass canopy, cargo and twin jets."""
        d=self.d
        def pts(p): return [(x+xx*scale,y+yy*scale) for xx,yy in p]
        def poly(p,c): d.polygon(pts(p),fill=c)
        def line(p,c): d.line(pts(p),fill=c,width=scale)
        poly([(5,12),(15,8),(23,1),(30,1),(31,7),(45,7),(58,12),(54,15),
              (43,16),(30,22),(22,22),(22,17),(8,18),(1,15)],1)
        poly([(8,12),(18,10),(24,3),(28,3),(29,9),(44,9),(52,12),
              (48,14),(29,14),(23,17),(9,16)],2)
        line([(14,11),(20,11),(26,4),(28,4)],3)
        line([(31,10),(42,10),(48,12)],3)
        poly([(29,9),(32,5),(40,5),(44,9)],1)
        poly([(32,8),(34,6),(39,6),(41,8)],3)
        poly([(26,16),(29,16),(34,19),(25,20)],3)
        poly([(16,9),(19,5),(23,5),(21,9)],2)
        line([(20,9),(22,6)],3)
        # Cargo crates and small service hatch.
        poly([(12,13),(19,13),(19,15),(12,15)],1)
        line([(13,13),(13,15)],3); line([(18,13),(18,15)],3)
        d.point((x+45*scale,y+13*scale),fill=3)
        if exhaust:
            poly([(8,12),(2,12),(0,13),(6,14)],3)
            poly([(8,15),(1,15),(3,16),(7,16)],2)

    def console(self, broken=False):
        d=self.d
        # Window to space, twin monitors, curved instrument rim.
        self.stars(27, 731, 13)
        d.polygon([(0,0),(15,0),(28,30),(132,30),(145,0),(159,0),(159,38),(0,38)],fill=1)
        d.line((12,0,25,31,134,31,147,0), fill=3)
        for x in [3,134]:
            d.rectangle((x,17,x+22,32),fill=0)
            d.rectangle((x+1,18,x+21,31),outline=2)
            d.line((x+4,27,x+7,23,x+10,26,x+15,21,x+18,25),fill=3)
        d.rectangle((56,24,103,34),fill=0)
        d.rectangle((57,25,102,33),outline=2)
        for x in range(60,101,5): d.rectangle((x,28,x+1,30),fill=3 if x<90 else 1)
        d.line((28,36,131,36),fill=2)
        d.rectangle((39,35,43,38),fill=3)
        d.rectangle((116,35,120,38),fill=3)
        self.palette_rect((0,0,159,39),5)
        self.palette_rect((48,24,111,39),2)
        if broken:
            # Two readable cracks, bright alert lamps, intact recovery monitor.
            d.line((66,0,70,6,64,11,73,15,69,23),fill=3)
            d.line((70,6,80,7,85,3),fill=2)
            d.line((73,15,87,18,89,23),fill=2)
            d.line((111,3,105,10,108,15,102,23),fill=3)
            for x in [28,126]:
                d.rectangle((x,28,x+5,33),fill=3)
                d.point((x+1,29),fill=0)
            self.palette_rect((24,24,39,39),6)
            self.palette_rect((120,24,135,39),6)
        self.divider(39,6 if broken else 2)


def title():
    c=Canvas(); d=c.d
    c.stars(92, 4248, 32)
    # Distant wreck arc and a sunset planet behind the launch silhouette.
    c.planet(128,60,25)
    c.palette_rect((104,32,159,87),4)
    d.line((1,54,20,49,28,52,38,49),fill=1)
    d.line((2,55,19,51,29,54),fill=2)
    c.logo("STARFALL", 33, 6)
    c.logo("SALVAGE", 39, 25)
    c.palette_rect((32,0,127,47),1)
    # One large craft fills the lower third of the artwork.
    c.ship(16,49,2)
    c.palette_rect((16,48,135,95),5)
    # Engine light, independent of the cold grey hull.
    c.palette_rect((16,72,31,87),2)
    # A small inset panel suggests the three-cell cargo.
    for x in [66,78,90]:
        d.rectangle((x,89,x+7,92),fill=1)
        d.line((x+1,90,x+5,90),fill=3)
    c.divider(95,1)
    return c


def launch():
    c=Canvas();d=c.d
    c.stars(46,948,14)
    # Chart occupies the left two-thirds. Twelve nodes form a single route.
    d.rectangle((7,5,110,39),fill=0)
    d.rectangle((7,5,110,39),outline=1)
    for y in [12,28]: d.line((24,y,88,y),fill=1)
    d.line((88,12,104,12,104,28,88,28),fill=1)
    for i in range(12):
        # Index runs clockwise: first six left->right, next six right->left.
        x=(3+i*2) if i<6 else (3+(11-i)*2)
        y=1 if i<6 else 3
        d.rectangle((x*8+2,y*8+2,x*8+5,y*8+5),fill=2)
        d.point((x*8+3,y*8+3),fill=3)
    # Three little station groups make the three zones legible visually.
    d.line((20,20,43,20),fill=2);d.line((48,20,71,20),fill=2);d.line((76,20,99,20),fill=2)
    c.palette_rect((16,8,47,31),1)
    c.palette_rect((48,8,79,31),2)
    c.palette_rect((80,8,111,31),3)
    c.ship(113,10,1)
    # Clip ship at the 160px native screen edge, deliberately cropped bow.
    c.palette_rect((112,8,159,39),5)
    c.divider(47)
    return c


def pause():
    c=Canvas();c.console();return c


def result():
    c=Canvas();d=c.d
    c.stars(44,921,16)
    # Safe berth: ribbed ceiling, docking mast, skiff with cargo bank lamps.
    d.polygon([(0,0),(31,0),(41,5),(119,5),(129,0),(159,0),(159,9),(0,9)],fill=1)
    d.line((0,8,159,8),fill=2)
    for x in range(8,153,16):
        d.rectangle((x,1,x+5,4),fill=2);d.point((x+1,1),fill=3)
    c.ship(20,0,2,False)
    d.rectangle((0,41,159,47),fill=1)
    d.line((0,41,159,41),fill=3)
    for x in range(8,155,16): d.line((x,44,x+4,44),fill=2)
    c.palette_rect((0,0,159,47),1)
    c.palette_rect((56,16,103,31),2)
    c.divider(47,1)
    return c


def ending():
    c=Canvas();d=c.d
    c.stars(61,12701,25)
    c.planet(134,28,26)
    c.palette_rect((104,0,159,55),4)
    # Splintered station in the far distance, survivor escaping in foreground.
    d.line((7,6,24,11,28,9,49,18,48,21,58,25),fill=1)
    d.rectangle((28,11,36,17),fill=2)
    d.line((19,14,16,21,29,20),fill=1)
    for x,y in [(53,12),(41,26),(9,24),(62,20)]:d.rectangle((x,y,x+1,y+1),fill=2)
    c.ship(16,34,1)
    c.palette_rect((16,32,79,63),5)
    c.palette_rect((16,40,31,55),2)
    # Three cargo lights complete the visual motif from the title card.
    for x in [87,97,107]:
        d.rectangle((x,57,x+5,60),fill=1);d.rectangle((x+1,58,x+4,59),fill=3)
    c.palette_rect((80,56,111,63),2)
    c.divider(63,2)
    return c


def failure():
    c=Canvas();c.console(True);return c


def upgrade():
    c=Canvas();d=c.d
    # A native workbench with four distinct module silhouettes.
    d.rectangle((0,0,159,31),fill=1)
    d.rectangle((3,2,156,28),fill=0)
    d.line((3,2,156,2),fill=2)
    d.line((3,28,156,28),fill=2)
    for x in [16,48,80,112]:
        d.rectangle((x,5,x+23,25),fill=1)
        d.rectangle((x+1,6,x+22,24),outline=2)
    # Standard cell, fast capacitor, wide coil and charged module.
    d.rectangle((24,9,30,21),fill=2);d.rectangle((26,7,28,8),fill=3)
    d.line((25,11,29,11),fill=3);d.line((25,19,29,19),fill=3)
    d.polygon([(61,8),(53,17),(60,17),(57,23),(66,13),(60,13)],fill=3)
    for x in [86,90,94]:d.rectangle((x,9,x+2,21),outline=3)
    d.line((84,16,99,16),fill=2)
    d.ellipse((118,9,130,21),outline=3)
    d.ellipse((121,12,127,18),fill=2)
    d.point((124,15),fill=3)
    c.palette_rect((16,0,39,31),1)
    c.palette_rect((48,0,71,31),2)
    c.palette_rect((80,0,103,31),3)
    c.palette_rect((112,0,135,31),6)
    c.divider(31,5)
    return c


def native_tiles(image):
    """Exact 2bpp patterns; retain orientation, no implicit flipping."""
    tiles=[]; index={}; tilemap=[]
    for ty in range(18):
        for tx in range(20):
            b=[]
            for y in range(8):
                lo=hi=0
                for x in range(8):
                    p=image.getpixel((tx*8+x,ty*8+y)); bit=1<<(7-x)
                    if p&1:lo|=bit
                    if p&2:hi|=bit
                b.extend([lo,hi])
            raw=bytes(b)
            if raw not in index:index[raw]=len(tiles);tiles.append(raw)
            tilemap.append(index[raw])
    return b"".join(tiles),bytes(tilemap),len(tiles)


def verify_roundtrip(c, data, tilemap):
    for y in range(144):
        for x in range(160):
            tile=tilemap[(y//8)*20+x//8];off=tile*16+(y%8)*2;bit=7-x%8
            decoded=((data[off]>>bit)&1)|(((data[off+1]>>bit)&1)<<1)
            assert decoded==c.image.getpixel((x,y)), (x,y)
    assert all(8<=a<=14 for a in c.attrs)


def c_array(name, data):
    rows=["    "+",".join(f"0x{x:02X}" for x in data[i:i+16])+"," for i in range(0,len(data),16)]
    return f"const UBYTE {name}[{len(data)}] = {{\n"+"\n".join(rows)+"\n};\n"


def color_preview(c, zone=0):
    pal=[list(x) for x in BASE_PALETTES];pal[1]=ZONE_HULL[zone]
    out=Image.new("RGB",(160,144))
    for y in range(144):
        for x in range(160):
            rgb=pal[c.attrs[(y//8)*20+x//8]&7][c.image.getpixel((x,y))]
            out.putpixel((x,y),tuple((v<<3)|(v>>2) for v in rgb))
    return out


def main():
    pngdir=ROOT/"assets/interface";pngdir.mkdir(parents=True,exist_ok=True)
    include=ROOT/"plugins/starfall/engine/include";src=ROOT/"plugins/starfall/engine/src"
    camp=ROOT/"campaign";camp.mkdir(exist_ok=True)
    receipt={"format":"native-cgb-window-art-v1","dimensions":[160,144],
             "source_shades":["#071821","#306850","#86c06c","#e0f8cf"],
             "vram_bank":1,"tile_range":[0,191],"reserved_untouched":[[192,233],[234,238]],
             "banked_reads":"GBVM SetBankedBkgData / SetBankedWinTiles / MemcpyBanked; all restore ROM bank",
             "screens":[]}
    canvases=[]
    for name in KINDS:
        c=globals()[name]();canvases.append(c)
        assert not any(c.image.getpixel((x,y)) for y in range(QUIET[name]*8,144) for x in range(160))
        tiles,tilemap,count=native_tiles(c.image);assert count<=192,(name,count)
        verify_roundtrip(c,tiles,tilemap)
        path=pngdir/f"{name}.png";c.image.convert("RGB").save(path)
        color_preview(c).save(pngdir/f"{name}-color.png")
        sym=f"sf_screen_{name}"
        (include/f"{sym}.h").write_text(
            "/* Generated by screen_art.py; exact native 2bpp window payload. */\n"
            "#include <gbdk/platform.h>\n#include \"bankdata.h\"\n"
            f"BANKREF_EXTERN({sym})\n#define {sym.upper()}_COUNT {count}u\n"
            f"extern const UBYTE {sym}_tiles[{len(tiles)}];\n"
            f"extern const UBYTE {sym}_map[360];\nextern const UBYTE {sym}_attrs[360];\n")
        (src/f"{sym}.c").write_text(
            "/* Generated by screen_art.py. Each screen is independently autobanked. */\n"
            f"#pragma bank 255\n#include \"{sym}.h\"\nBANKREF({sym})\n"
            +c_array(sym+"_tiles",tiles)+c_array(sym+"_map",tilemap)+c_array(sym+"_attrs",c.attrs))
        receipt["screens"].append({"kind":name,"source":str(path.relative_to(ROOT)),
            "source_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"unique_tiles":count,
            "tile_payload_bytes":len(tiles),"map_attribute_bytes":720,"quiet_from_row":QUIET[name],
            "single_translation_unit_bytes":len(tiles)+720})
    # Montage is a review asset, never a substitute for native ROM screenshots.
    montage=Image.new("RGB",(960,648),(12,18,28));md=ImageDraw.Draw(montage)
    for i,(name,c) in enumerate(zip(KINDS,canvases)):
        x=(i%3)*320;y=(i//3)*216
        md.text((x+5,y+2),f"{name.upper()} / TEXT FROM ROW {QUIET[name]}",fill=(225,242,250))
        # Crop only the illustrated region for this review montage. The exact
        # full-screen PNGs above retain every blank native text row.
        crop=color_preview(c).crop((0,0,160,QUIET[name]*8))
        montage.paste(crop.resize((320,crop.height*2),Image.Resampling.NEAREST),(x,y+16))
    montage.save(camp/"screen-montage.png")
    receipt["verification"]={
        "native_2bpp_roundtrip":"all 161280 screen pixels match authored indices",
        "native_palette_indices":"all attributes select bank1 and palettes0..6",
        "source_colors":"all source PNGs use only four exact manual shades",
        "quiet_text_rows":"all seven quiet regions blank index0",
        "tile_budget":"all seven screens <=192 unique tiles",
        "single_bank_payload":"each individual data translation unit <16384 bytes",
        "banking_source_review":"GBVM NONBANKED bankdata helpers restore ROM bank before return",
        "in_rom":"not yet built or emulator checked"}
    (camp/"SCREEN-RECEIPTS.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps({"screens":receipt["screens"],"montage":"campaign/screen-montage.png"},indent=2))


if __name__=="__main__":main()

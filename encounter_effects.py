"""Author the native 16x16 pulse spark for Starfall Salvage."""
from pathlib import Path
from PIL import Image, ImageDraw

root = Path(__file__).parent
image = Image.new("RGB", (16, 16), "#65ff00")
draw = ImageDraw.Draw(image)
draw.ellipse((1, 1, 14, 14), outline="#071821")
draw.ellipse((2, 2, 13, 13), outline="#e0f8cf")
draw.ellipse((3, 3, 12, 12), outline="#86c06c")
for line in [(7, 0, 7, 4), (7, 11, 7, 15), (0, 7, 4, 7), (11, 7, 15, 7)]:
    draw.line(line, fill="#e0f8cf")
image.save(root / "assets/sprites/pulse_ring.png")

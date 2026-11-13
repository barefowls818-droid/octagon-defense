"""favicon.ico (16/32/48) from the octagon. Needs Pillow."""
from pathlib import Path
from PIL import Image, ImageDraw
import math
S = 256
img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
t = math.tan(math.radians(22.5)); a = S / 2; s = a * t; c = S / 2
pts = [(c-s, 0), (c+s, 0), (S, c-s), (S, c+s), (c+s, S), (c-s, S), (0, c+s), (0, c-s)]
ImageDraw.Draw(img).polygon(pts, fill=(200, 16, 46, 255))
out = Path(__file__).resolve().parent.parent / "src" / "static" / "favicon.ico"
img.save(out, sizes=[(16, 16), (32, 32), (48, 48)])
print(out)

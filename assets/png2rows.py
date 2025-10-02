# png2rows.py
from PIL import Image
import sys

WIDTH = int(sys.argv[2])
HEIGHT = int(sys.argv[3])


path = sys.argv[1]
im = Image.open(path).convert("RGBA").resize((WIDTH, HEIGHT), Image.NEAREST)

L = im.convert("L")
A = im.getchannel("A")
rows = []
for y in range(HEIGHT):
    val = 0
    for x in range(WIDTH):
        on = (A.getpixel((x,y)) > 0) and (L.getpixel((x,y)) < WIDTH//2)
        val = (val << 1) | (1 if on else 0)
    rows.append(val)

print("ICON = [")
for r in rows:
    print(f"  0b{r:0{WIDTH}b},")
print("]")

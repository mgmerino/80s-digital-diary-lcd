# png2rows.py
from PIL import Image
import sys

path = sys.argv[1]
im = Image.open(path).convert("RGBA").resize((16, 16), Image.NEAREST)

# "Encendido" = píxel oscuro (L<128) y con alfa > 0
L = im.convert("L")
A = im.getchannel("A")
rows = []
for y in range(16):
    val = 0
    for x in range(16):
        on = (A.getpixel((x,y)) > 0) and (L.getpixel((x,y)) < 64)
        val = (val << 1) | (1 if on else 0)
    rows.append(val)

print("ICONO_16_ = [")
for r in rows:
    print(f"  0b{r:016b},")
print("]")

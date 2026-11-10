import sys
from PIL import Image
src, out = sys.argv[1], sys.argv[2]
im = Image.open(src); w, h = im.size
for i, (a, b) in enumerate([(0, 0.52), (0.48, 1.0)]):
    c = im.crop((0, int(h * a), w, int(h * b)))
    c = c.resize((1100, int(c.height * 1100 / w)))
    c.save(f'{out}_{"top" if i == 0 else "bot"}.png')

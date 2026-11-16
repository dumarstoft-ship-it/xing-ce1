"""Show original vs render(with voxel) vs render(without voxel), cropped to where the
two renders differ, to settle weakly-determined voxels by eye."""
import sys
sys.path.insert(0, '.')
import numpy as np
from PIL import Image
from q50_render import render, full
SRC = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s17_p13_i00.png'
src = Image.open(SRC).convert('L')

def probe(X0, YB, off, miss, voxels, out, S=14):
    tiles = []
    for v in voxels:
        with_v = full() - (miss - {v})
        without = full() - (miss | {v})
        r1 = render(with_v, X0, YB, size=(80, 75), off=off)
        r0 = render(without, X0, YB, size=(80, 75), off=off)
        d = np.abs(np.array(r1).astype(int) - np.array(r0).astype(int)) > 40
        ys, xs = np.nonzero(d)
        if len(xs) == 0:
            continue
        x0, x1 = max(xs.min() - 4, 0), min(xs.max() + 5, 80)
        y0, y1 = max(ys.min() - 4, 0), min(ys.max() + 5, 75)
        o = src.crop((off[0] + x0, off[1] + y0, off[0] + x1, off[1] + y1))
        row = [o, r1.crop((x0, y0, x1, y1)), r0.crop((x0, y0, x1, y1))]
        tiles.append(row)
    W = max(sum(t.width for t in row) * S + 40 for row in tiles)
    H = sum(row[0].height * S + 12 for row in tiles)
    c = Image.new('L', (W, H), 255)
    y = 0
    for row in tiles:
        x = 0
        for t in row:
            c.paste(t.resize((t.width * S, t.height * S), Image.NEAREST), (x, y))
            x += t.width * S + 20
        y += row[0].height * S + 12
    c.save(out)

if __name__ == '__main__':
    import ast
    X0, YB = float(sys.argv[1]), float(sys.argv[2])
    off = ast.literal_eval(sys.argv[3]); miss = set(ast.literal_eval(sys.argv[4])); vox = ast.literal_eval(sys.argv[5])
    probe(X0, YB, off, miss, vox, sys.argv[6])

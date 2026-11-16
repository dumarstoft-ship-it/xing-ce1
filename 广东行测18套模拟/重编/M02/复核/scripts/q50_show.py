import sys
sys.path.insert(0, '.')
from q50_render import render, full
from PIL import Image
SRC = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s17_p13_i00.png'
src = Image.open(SRC).convert('L')
out = sys.argv[1]
cfg = {
 'A': (33, 209.5, (25, 140), {(0,0,0),(0,1,0),(2,0,0),(2,1,0),(2,1,1),(2,2,1)}),
 'B': (157, 209.0, (148, 140), {(1,0,0),(2,0,2),(2,1,0),(2,2,0),(2,2,1),(2,2,2)}),
 'C': (267, 208.0, (262, 140), {(0,0,0),(0,1,0),(0,2,0),(0,2,1),(1,0,0),(1,1,0)}),
 'D': (395, 209.0, (387, 140), {(1,0,0),(1,2,0),(2,0,0),(2,0,2),(2,1,2),(2,2,0)}),
}
S = 6
canvas = Image.new('L', (2 * 80 * S + 20, 4 * 75 * S + 30), 255)
for i, (k, (X0, YB, off, miss)) in enumerate(cfg.items()):
    r = render(full() - miss, X0, YB, size=(80, 75), off=off)
    o = src.crop((off[0], off[1], off[0] + 80, off[1] + 75))
    canvas.paste(o.resize((80 * S, 75 * S), Image.NEAREST), (0, i * (75 * S + 10)))
    canvas.paste(r.resize((80 * S, 75 * S), Image.NEAREST), (80 * S + 20, i * (75 * S + 10)))
canvas.save(out)

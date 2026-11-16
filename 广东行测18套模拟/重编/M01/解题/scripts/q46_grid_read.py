# 第46题：读取每个4x4方格中黑格的位置，并检验“黑块沿外圈顺时针每次前移1格、同时增加1格”的规律
from PIL import Image
import numpy as np

IMG = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s16_p11_i00.png'
im = np.array(Image.open(IMG).convert('L'))
dark = im < 128

def runs(arr):
    r = []; s = None
    for i, v in enumerate(arr):
        if v and s is None: s = i
        if not v and s is not None: r.append((s, i - 1)); s = None
    if s is not None: r.append((s, len(arr) - 1))
    return r

def read_panel(x0, x1, y0, y1):
    """在面板内部找4x4方格外框，再取16个格子中心的灰度"""
    sub = dark[y0:y1, x0:x1]
    ys, xs = np.nonzero(sub)
    gx0, gx1, gy0, gy1 = xs.min(), xs.max(), ys.min(), ys.max()
    cw = (gx1 - gx0) / 4.0
    ch = (gy1 - gy0) / 4.0
    grid = []
    for r in range(4):
        row = []
        for c in range(4):
            cx = int(gx0 + (c + 0.5) * cw) + x0
            cy = int(gy0 + (r + 0.5) * ch) + y0
            patch = im[cy - 3:cy + 4, cx - 3:cx + 4]
            row.append(1 if patch.mean() < 128 else 0)
        grid.append(row)
    return grid

# 题干面板：竖线在 4,102,200,298,397,495,593；横线 4..112
top_x = [6, 102, 200, 298, 397, 495]
panels = []
for i in range(5):
    panels.append(read_panel(top_x[i] + 4, top_x[i + 1] - 2, 9, 108))
# 选项面板：竖线 104,202,300,399,497；横线 141..248
bot_x = [106, 202, 300, 399, 497]
opts = {}
for i, k in enumerate('ABCD'):
    opts[k] = read_panel(bot_x[i] + 4, bot_x[i + 1] - 2, 146, 244)

# 外圈12格顺时针编号：p0=(0,0) 左上角，沿上边向右，沿右边向下，沿下边向左，沿左边向上
ring = [(0,0),(0,1),(0,2),(0,3),(1,3),(2,3),(3,3),(3,2),(3,1),(3,0),(2,0),(1,0)]

def describe(g):
    cells = [(r, c) for r in range(4) for c in range(4) if g[r][c]]
    inner = [rc for rc in cells if rc not in ring]
    idx = sorted(ring.index(rc) for rc in cells if rc in ring)
    return cells, idx, inner

def show(g):
    return '\n'.join(''.join('#' if v else '.' for v in row) for row in g)

for i, g in enumerate(panels):
    cells, idx, inner = describe(g)
    print(f'题干第{i+1}图  黑格数={len(cells)}  外圈编号={idx}  内部黑格={inner}')
    print(show(g)); print()
for k, g in opts.items():
    cells, idx, inner = describe(g)
    print(f'选项{k}  黑格数={len(cells)}  外圈编号={idx}  内部黑格={inner}')
    print(show(g)); print()

# 规律：第n图（n=1..）黑块为外圈上从 tail(n) 起顺时针连续 n 格，tail(n)= (11 + (n-1)) mod 12
def expected(n):
    tail = (11 + (n - 1)) % 12
    return sorted((tail + j) % 12 for j in range(n))

for n in range(1, 6):
    ok = describe(panels[n - 1])[1] == expected(n) and not describe(panels[n - 1])[2]
    print(f'第{n}图 符合规律: {ok}  预期外圈编号={expected(n)}')
exp6 = expected(6)
print('第6图预期外圈编号:', exp6)
for k, g in opts.items():
    cells, idx, inner = describe(g)
    print(f'选项{k} 是否符合: {idx == exp6 and not inner}')

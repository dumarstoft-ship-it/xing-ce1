# 第47题：九宫格，每行“图1、图2叠加：同黑为黑，其余为白”得到图3。
# 读取每格各小区域的黑白，验证前两行规律，并逐一检验四个选项。
from PIL import Image
import numpy as np, math

IMG = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s16_p11_i01.png'
im = np.array(Image.open(IMG).convert('L')).astype(float)
dark = im < 128
H, W = im.shape

def lines(mask_slice, axis, thr):
    frac = mask_slice.mean(axis=axis)
    idx = [i for i, v in enumerate(frac) if v > thr]
    # 合并相邻
    groups = []
    for i in idx:
        if groups and i - groups[-1][-1] <= 1: groups[-1].append(i)
        else: groups.append([i])
    return [(g[0], g[-1]) for g in groups]

# 九宫格外框
vl = lines(dark[0:305], 0, 0.8)
hl = lines(dark[:, 50:350], 1, 0.8)
print('竖线', vl); print('横线', hl)

def bbox(x0, x1, y0, y1):
    sub = dark[y0:y1, x0:x1]
    ys, xs = np.nonzero(sub)
    return xs.min() + x0, xs.max() + x0, ys.min() + y0, ys.max() + y0

def val(x, y, r=2):
    p = im[int(y) - r:int(y) + r + 1, int(x) - r:int(x) + r + 1]
    return 'B' if p.mean() < 128 else 'W'

def tri_regions(x0, x1, y0, y1):
    bx0, bx1, by0, by1 = bbox(x0 + 4, x1 - 4, y0 + 4, y1 - 4)
    w = bx1 - bx0; h = by1 - by0
    # 正三角形四等分：上、左下、右下、中心（倒三角）
    pts = {'上': (bx0 + w / 2, by0 + h * 0.3), '左下': (bx0 + w * 0.22, by0 + h * 0.82),
           '右下': (bx0 + w * 0.78, by0 + h * 0.82), '中': (bx0 + w / 2, by0 + h * 0.62)}
    return {k: val(*v) for k, v in pts.items()}

def sq_regions(x0, x1, y0, y1):
    bx0, bx1, by0, by1 = bbox(x0 + 4, x1 - 4, y0 + 4, y1 - 4)
    w = bx1 - bx0; h = by1 - by0
    out = {}
    for r in range(3):
        for c in range(3):
            out[(r + 1, c + 1)] = val(bx0 + w * (c + 0.5) / 3, by0 + h * (r + 0.5) / 3)
    return out

def pent_regions(x0, x1, y0, y1):
    bx0, bx1, by0, by1 = bbox(x0 + 4, x1 - 4, y0 + 4, y1 - 4)
    cx = (bx0 + bx1) / 2; cy = by0 + (by1 - by0) * 0.52
    R = (bx1 - bx0) * 0.33
    names = ['上', '右上', '右下', '左下', '左上']
    angs = [90, 18, -54, -126, 162]
    out = {}
    for n, a in zip(names, angs):
        out[n] = val(cx + R * math.cos(math.radians(a)), cy - R * math.sin(math.radians(a)))
    out['中心'] = val(cx, cy)
    return out

xs = [vl[i][1] for i in range(len(vl))]
ys = [hl[i][1] for i in range(len(hl))]
cells = {}
readers = [tri_regions, sq_regions, pent_regions]
for r in range(3):
    for c in range(3):
        if r == 2 and c == 2: continue
        cells[(r, c)] = readers[r](xs[c], xs[c + 1], ys[r], ys[r + 1])

def overlay(a, b):
    return {k: ('B' if a[k] == 'B' and b[k] == 'B' else 'W') for k in a}

for r in range(2):
    a, b, c = cells[(r, 0)], cells[(r, 1)], cells[(r, 2)]
    print(f'第{r+1}行：图1={a}\n        图2={b}\n        图3={c}')
    print('   同黑为黑叠加结果 == 图3 ?', overlay(a, b) == c)
a, b = cells[(2, 0)], cells[(2, 1)]
print('第3行：图1=', a); print('       图2=', b)
exp = overlay(a, b)
print('第3行应为：', exp)

# 选项行
ovl = lines(dark[325:440], 0, 0.8)
ohl = lines(dark[320:465, 10:390], 1, 0.6)
print('选项竖线', ovl, '选项横线', [(p[0] + 320, p[1] + 320) for p in ohl])
oxs = [p[1] for p in ovl]
oy0, oy1 = ohl[0][1] + 320, ohl[1][0] + 320
for i, k in enumerate('ABCD'):
    o = pent_regions(oxs[i], oxs[i + 1], oy0, oy1)
    print(f'选项{k}: {o}  符合: {o == exp}')

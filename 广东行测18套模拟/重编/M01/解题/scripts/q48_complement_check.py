# 第48题：平面拼合。求左侧图形在其外接正方形中的“补形”，
# 与四个选项分别做旋转（及翻转，仅作参考）比对，按重合度(IoU)判断哪一项能拼成正方形。
from PIL import Image
import numpy as np
from collections import deque

IMG = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s16_p11_i02.png'
im = np.array(Image.open(IMG).convert('L'))
dark = im < 160
H, W = im.shape

def lines(mask, axis, thr):
    frac = mask.mean(axis=axis)
    idx = [i for i, v in enumerate(frac) if v > thr]
    g = []
    for i in idx:
        if g and i - g[-1][-1] <= 1: g[-1].append(i)
        else: g.append([i])
    return [(a[0], a[-1]) for a in g]

def shape_mask(x0, x1, y0, y1):
    """在矩形区域内从边界做外部填充，返回多边形（含轮廓线）的掩码"""
    sub = dark[y0:y1, x0:x1]
    h, w = sub.shape
    ext = np.zeros_like(sub, dtype=bool)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if not sub[y, x] and not ext[y, x]: ext[y, x] = True; q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if not sub[y, x] and not ext[y, x]: ext[y, x] = True; q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and not ext[ny, nx] and not sub[ny, nx]:
                ext[ny, nx] = True; q.append((ny, nx))
    m = ~ext
    ys, xs = np.nonzero(m)
    return m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]

# 选项面板外框
vl = lines(dark[5:140], 0, 0.8)
hl = lines(dark[:, 125:595], 1, 0.8)
print('竖线', vl, '横线', hl)
left_x1 = vl[0][0] - 2
top, bot = hl[0][1] + 1, hl[1][0] - 1

L = shape_mask(0, left_x1, 0, H)
print('左图外接矩形 高x宽 =', L.shape)
side = max(L.shape)
# 左图贴着正方形的左边和下边（左边整条竖线、下边整条横线），据此放进 side x side 正方形
sq = np.zeros((side, side), dtype=bool)
sq[side - L.shape[0]:, :L.shape[1]] = L
comp = ~sq
# 去掉补形中贴着左图轮廓的细缝（线宽约2px）：做一次开运算近似
def erode(m):
    p = np.pad(m, 1)
    return p[1:-1,1:-1] & p[:-2,1:-1] & p[2:,1:-1] & p[1:-1,:-2] & p[1:-1,2:]
def dilate(m):
    p = np.pad(m, 1)
    return p[1:-1,1:-1] | p[:-2,1:-1] | p[2:,1:-1] | p[1:-1,:-2] | p[1:-1,2:]
comp = dilate(dilate(erode(erode(comp))))
print('补形面积占正方形比例 = %.3f' % (comp.sum() / side / side))

def resize(m, shape):
    img = Image.fromarray((m * 255).astype(np.uint8)).resize((shape[1], shape[0]), Image.NEAREST)
    return np.array(img) > 127

def iou(a, b):
    return (a & b).sum() / (a | b).sum()

def show(m, step=3):
    return '\n'.join(''.join('#' if m[y, x] else '.' for x in range(0, m.shape[1], step)) for y in range(0, m.shape[0], step))

print('补形（缩略）:'); print(show(comp, 4))
results = {}
for i, k in enumerate('ABCD'):
    x0, x1 = vl[i][1] + 2, vl[i + 1][0] - 2
    M = shape_mask(x0, x1, top, bot)
    best = []
    for flip in (False, True):
        base = M[:, ::-1] if flip else M
        for rot in range(4):
            R = np.rot90(base, rot)
            Rr = resize(R, comp.shape)
            best.append((iou(Rr, comp), '翻转' if flip else '不翻转', rot * 90, R.shape))
    best.sort(reverse=True)
    results[k] = best
    print(f'选项{k} 原始外接矩形 {M.shape}; 最佳匹配:', [(round(b[0], 3), b[1], b[2]) for b in best[:3]])
    print('  仅旋转时最大IoU = %.3f' % max(b[0] for b in best if b[1] == '不翻转'))

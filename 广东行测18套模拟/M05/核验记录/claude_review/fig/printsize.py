# Print-size estimates: bbox_pt (图片清单.json) -> mm; measure key details in px and convert. Read-only on repo.
import json
import numpy as np
from PIL import Image
from collections import deque
REPO = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/'
man = {r['id']: r for r in json.load(open(REPO + '图片清单.json', encoding='utf-8'))}
PT = 25.4 / 72
ids = {46: 's19_p12_i00', 47: 's27_p12_i00', 48: 's31_p12_i00', 49: 's20_p13_i00', 50: 's23_p13_i00'}
scale = {}
print('题号 asset  bbox_pt(w x h)  印刷尺寸mm(w x h)  像素  mm/px  等效ppi')
for n, i in ids.items():
    r = man[i]; x0, y0, x1, y1 = r['bbox_pt']
    wmm, hmm = (x1 - x0) * PT, (y1 - y0) * PT
    s = wmm / r['width_px']; scale[n] = s
    print('%d %s  %.1f x %.1f pt  %.1f x %.1f mm  %dx%d  %.4f  %.0f' % (n, i, x1-x0, y1-y0, wmm, hmm, r['width_px'], r['height_px'], s, 25.4/s))
def load(i):
    return np.array(Image.open(REPO + 'assets/%s.png' % i).convert('L')).astype(int)
def comps(mask, conn8=True):
    H, W = mask.shape; lab = np.zeros((H, W), int); out = []; n = 0
    nb = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)] if conn8 else [(-1,0),(1,0),(0,-1),(0,1)]
    for y in range(H):
        for x in range(W):
            if mask[y, x] and not lab[y, x]:
                n += 1; q = deque([(y, x)]); lab[y, x] = n; pts = []
                while q:
                    cy, cx = q.popleft(); pts.append((cy, cx))
                    for dy, dx in nb:
                        ny, nx = cy+dy, cx+dx
                        if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not lab[ny, nx]:
                            lab[ny, nx] = n; q.append((ny, nx))
                out.append(np.array(pts))
    return out, lab
def dist_to_dark(dark):
    # exact-ish Euclidean distance via brute force on dark pixel list (small images)
    H, W = dark.shape
    dy, dx = np.nonzero(dark)
    D = np.full((H, W), 1e9)
    pts = np.stack([dy, dx], 1)
    yy, xx = np.mgrid[0:H, 0:W]
    for k in range(0, len(pts), 400):
        P = pts[k:k+400]
        d = np.sqrt((yy[..., None] - P[:, 0])**2 + (xx[..., None] - P[:, 1])**2).min(-1)
        D = np.minimum(D, d)
    return D
def mm(n, px): return px * scale[n]
# ---------- Q46
im = load(ids[46]); dark = im < 128
print('\n[46] 六边形宽≈80px=%.1fmm；圆直径≈16px=%.1fmm；短线长≈14-15px=%.1fmm；三角形边长≈20px=%.1fmm；C/D差别=三角形沿边平移半条边≈20px=%.1fmm；线宽≈2.5px=%.2fmm' % (
    mm(46, 80), mm(46, 16), mm(46, 14.5), mm(46, 20), mm(46, 20), mm(46, 2.5)))
lab_rows = dark[240:274]
ys = [y + 240 for y in range(lab_rows.shape[0]) if lab_rows[y].any()]
print('[46] 选项字母行高度: y %d..%d -> %d px = %.1f mm' % (ys[0], ys[-1], ys[-1]-ys[0]+1, mm(46, ys[-1]-ys[0]+1)))
# ---------- Q47 smallest enclosed regions (inscribed circle diameter)
im = load(ids[47]); dark = im < 128
xs = [51, 150, 250, 350]; yb = [6, 100, 200, 300]
cells = {}
for r in range(3):
    for c in range(3):
        if (r, c) != (2, 2): cells['r%dc%d' % (r+1, c+1)] = (xs[c]+4, yb[r]+4, xs[c+1]-3, yb[r+1]-3)
bx = [6, 103, 200, 297, 394]
for k, L in enumerate('ABCD'): cells[L] = (bx[k]+4, 333, bx[k+1]-3, 425)
print('\n[47] 各图最小封闭区（按内切圆直径计）：')
for name, (x0, y0, x1, y1) in cells.items():
    sub = im[y0:y1, x0:x1]; dk = sub < 160; wh = ~dk
    cs, lab = comps(wh, conn8=False)
    D = dist_to_dark(dk)
    regs = []
    for c in cs:
        if c[:, 0].min() == 0 or c[:, 1].min() == 0 or c[:, 0].max() == sub.shape[0]-1 or c[:, 1].max() == sub.shape[1]-1: continue
        if len(c) < 8: continue
        dmax = D[c[:, 0], c[:, 1]].max()
        regs.append((2 * dmax, len(c), (int(c[:, 1].mean()) + x0, int(c[:, 0].mean()) + y0)))
    regs.sort()
    r0 = regs[0]
    print('   %-5s 面数%d  最小区: 内切直径%.1fpx=%.2fmm, 面积%dpx=%.2fmm², 位置%s' % (name, len(regs), r0[0], mm(47, r0[0]), r0[1], r0[1]*scale[47]**2, r0[2]))
print('[47] 线宽≈2.5px=%.2fmm；单格≈99px=%.1fmm' % (mm(47, 2.5), mm(47, 99)))
# ---------- Q48
print('\n[48] 字符外框≈34x35px=%.1fx%.1fmm；同一字符内平行笔画间距(中心)≈16px=%.1fmm；笔画宽≈2px=%.2fmm；字符间距≈20px=%.1fmm' % (
    mm(48, 34), mm(48, 35), mm(48, 16), mm(48, 2), mm(48, 20)))
im = load(ids[48]); dark = im < 128
# option letters A-D at x<30
for (a, b), L in zip([(106, 140), (163, 197), (221, 255), (278, 312)], 'ABCD'):
    sub = dark[a:b, 0:30]; yy = [y for y in range(sub.shape[0]) if sub[y].any()]
    print('   选项字母%s 高%dpx=%.1fmm' % (L, yy[-1]-yy[0]+1, mm(48, yy[-1]-yy[0]+1)), end='')
print()
# ---------- Q49 labels
im = load(ids[49]); dark = im < 128
labels = {'4': (6, 14, 96, 107), '3': (122, 129, 121, 132), '8': (304, 311, 42, 53), '5': (366, 373, 98, 109), '7': (405, 412, 60, 71), '6': (425, 432, 160, 171)}
print('\n[49] 数字标号（独立连通块）字高/字宽：')
for k, (x0, x1, y0, y1) in labels.items():
    print('   "%s": %dx%dpx = %.2fx%.2fmm' % (k, y1-y0+1, x1-x0+1, mm(49, y1-y0+1), mm(49, x1-x0+1)))
print('   "1"与上后棱相接、"2"压在上右棱线上（非独立连通块），字高同为≈12px=%.2fmm' % mm(49, 12))
print('[49] 小方框边长≈25px=%.1fmm；展开图小正方形≈58.5px=%.1fmm；立方体正面≈78px=%.1fmm' % (mm(49, 25), mm(49, 58.5), mm(49, 78)))
# distance from digit '2' centre to the edge line (99,60)-(138,21)
cx, cy = 119, 43
d = abs((cx - 99) + (cy - 60)) / np.sqrt(2)
print('[49] "2"中心到上右棱线距离≈%.1fpx=%.2fmm（即压线）' % (d, mm(49, d)))
# ---------- Q50
im = load(ids[50]); dark = im < 128
print('\n[50] 立体图主体约112x93px=%.1fx%.1fmm；一个深度单位在图上=7px右移+7px上移=%.2fmm（斜向长%.2fmm）' % (mm(50, 112), mm(50, 93), mm(50, 7), mm(50, 7*np.sqrt(2))))
row = dark[88, 60:100]
runs = []; s = None
for x in range(len(row)):
    if row[x] and s is None: s = x
    if not row[x] and s is not None: runs.append((s+60, x-1+60)); s = None
print('[50] y=88 行的黑线段:', runs)
gap = runs[1][0] - runs[0][1] - 1
print('[50] 前块右侧面可见宽(两竖线间白隙)=%dpx=%.2fmm；两线中心距≈%dpx=%.2fmm —— 判断右侧高块“后缩一格”的唯一线索' % (gap, mm(50, gap), (runs[1][0]+runs[1][1])//2 - (runs[0][0]+runs[0][1])//2, mm(50, (runs[1][0]+runs[1][1])/2 - (runs[0][0]+runs[0][1])/2)))
for L, (x0, x1, y0, y1) in {'P': (73, 80, 16, 26)}.items():
    sub = dark[y0-2:y1+3, x0-1:x1+2]; yy = [y for y in range(sub.shape[0]) if sub[y].any()]
    print('[50] 字母P高≈%dpx=%.2fmm' % (len(yy), mm(50, len(yy))))
print('[50] 斜坡右侧三角面竖边≈19px=%.1fmm；小立方体正面≈22x20px=%.1fx%.1fmm；选项图形格宽≈20px/格=%.1fmm' % (mm(50, 19), mm(50, 22), mm(50, 20), mm(50, 20)))

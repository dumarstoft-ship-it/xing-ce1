"""第48题：读出各图的小方块位置，检验“图1能否由图2、图3拼成”。
小方块坐标由像素读出（灰色填充格），再穷举图3（或选项）的旋转/翻转与平移。"""
from PIL import Image
import numpy as np
from scipy import ndimage

PATH = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s21_p11_i02.png'
im = np.array(Image.open(PATH).convert('L')).astype(int)

def cells_in(x0, x1, y0, y1):
    sub = im[y0:y1, x0:x1]
    gray = (sub > 90) & (sub < 180)
    lab, n = ndimage.label(gray)
    cents = []
    for k in range(1, n + 1):
        m = lab == k
        if m.sum() < 60:   # 去掉线条边缘的抗锯齿碎块（真方格约120~145像素）
            continue
        ys, xs = np.nonzero(m)
        if np.ptp(ys) < 8 or np.ptp(xs) < 8:   # 去掉细长的框线灰边
            continue
        cy, cx = ndimage.center_of_mass(m)
        cents.append((cy, cx, m.sum()))
    if not cents:
        return set()
    # 估计格子边长：取相邻质心最小间距
    pts = np.array([(c[0], c[1]) for c in cents])
    d = [np.hypot(*(pts[i] - pts[j])) for i in range(len(pts)) for j in range(i + 1, len(pts))]
    step = min(d) if d else 15
    y0c, x0c = pts[:, 0].min(), pts[:, 1].min()
    return {(int(round((cy - y0c) / step)), int(round((cx - x0c) / step))) for cy, cx, _ in cents}

def show(s):
    R = max(r for r, c in s) + 1
    C = max(c for r, c in s) + 1
    return '\n'.join(''.join('■' if (r, c) in s else '·' for c in range(C)) for r in range(R))

def norm(s):
    mr = min(r for r, c in s); mc = min(c for r, c in s)
    return frozenset((r - mr, c - mc) for r, c in s)

def orientations(s, reflect=True):
    out = set()
    cur = list(s)
    for flip in ([False, True] if reflect else [False]):
        pts = [(r, -c) for r, c in cur] if flip else cur
        for k in range(4):
            out.add(norm(pts))
            pts = [(c, -r) for r, c in pts]
    return out

def tilings(target, a, b, reflect=True):
    """target 能否恰好分成 a、b 两块（各自可旋转/翻转、平移）。返回解的列表。"""
    target = frozenset(target)
    sols = []
    for oa in orientations(a, reflect):
        for ob in orientations(b, reflect):
            for (tr, tc) in target:
                for (ar, ac) in oa:
                    pa = frozenset((r - ar + tr, c - ac + tc) for r, c in oa)
                    if not pa <= target:
                        continue
                    rest = target - pa
                    if norm(rest) == ob:
                        sols.append((pa, rest))
    return list({(s[0], s[1]) for s in sols})

# 题干与选项方框（按竖线分）
def boxes(y0, y1):
    prof = (im[y0:y1] < 60).sum(axis=0)
    xs = [x for x in range(im.shape[1]) if prof[x] > (y1 - y0) * 0.8]
    g = []
    for x in xs:
        if g and x - g[-1][-1] <= 1:
            g[-1].append(x)
        else:
            g.append([x])
    return [(g[i][-1] + 1, g[i + 1][0]) for i in range(len(g) - 1)]

if __name__ == '__main__':
    top = [b for b in boxes(8, 95) if b[1] - b[0] > 50]
    opt = [b for b in boxes(128, 200) if b[1] - b[0] > 50]
    figs = [cells_in(a, b, 8, 95) for a, b in top]
    opts = {k: cells_in(a, b, 128, 200) for k, (a, b) in zip('ABCD', opt)}
    names = ['组1图1', '组1图2', '组1图3', '组2图1', '组2图2']
    for n, f in zip(names, [f for f in figs if f]):
        print(n, len(f), '格'); print(show(f))
    for k, f in opts.items():
        print('选项', k, len(f), '格'); print(show(f))
    g = [f for f in figs if f]
    print('\n组1：图1能否由图2、图3拼成（只旋转不翻转）:', len(tilings(g[0], g[1], g[2], reflect=False)) > 0)
    for pa, rest in tilings(g[0], g[1], g[2], reflect=False):
        print('  图2占', sorted(pa), ' 图3占', sorted(rest))
    print('组1：允许翻转时解数:', len(tilings(g[0], g[1], g[2], reflect=True)))
    for k, f in opts.items():
        s1 = tilings(g[3], g[4], f, reflect=False)
        s2 = tilings(g[3], g[4], f, reflect=True)
        print(f'组2 选项{k}: 只旋转可拼={len(s1)>0}，允许翻转可拼={len(s2)>0}')
        for pa, rest in s2:
            print('    十字占', sorted(pa), ' 选项占', sorted(rest))

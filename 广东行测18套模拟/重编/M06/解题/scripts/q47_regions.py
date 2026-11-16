"""第47题：把每幅图的线条（深色像素）当作边界，对其余像素做连通区域标记，
得到每个封闭区域的位置（质心）和填充色（灰/白），再检验规律。"""
from PIL import Image
import numpy as np
from scipy import ndimage

PATH = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s21_p11_i01.png'
im = np.array(Image.open(PATH).convert('L')).astype(int)

# 九宫格外框线：行 10-11,102-103,200-201,298-300；列 52-53,150-151,247-248,345-347
rows = [(12, 101), (104, 199), (202, 297)]
cols = [(54, 149), (152, 246), (249, 344)]
# 选项框：行 330-424；列按竖线分
opt_dark = (im[330:424, :] < 100).sum(axis=0)
opt_lines = [x for x in range(im.shape[1]) if opt_dark[x] > 80]

def groups(xs):
    out = []
    for x in xs:
        if out and x - out[-1][-1] <= 1:
            out[-1].append(x)
        else:
            out.append([x])
    return [(g[0], g[-1]) for g in out]

ol = groups(opt_lines)
opt_cols = [(ol[i][1] + 1, ol[i + 1][0] - 1) for i in range(len(ol) - 1)]

def regions(y0, y1, x0, x1):
    sub = im[y0:y1 + 1, x0:x1 + 1]
    line = sub < 70           # 线条
    free = ~line
    lab, n = ndimage.label(free)
    res = []
    # 背景（与子图边缘相连的区域）去掉
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
    for k in range(1, n + 1):
        if k in border:
            continue
        mask = lab == k
        area = mask.sum()
        if area < 15:
            continue
        cy, cx = ndimage.center_of_mass(mask)
        mean = sub[mask].mean()
        res.append({'cx': round(cx, 1), 'cy': round(cy, 1), 'area': int(area),
                    'color': 'G' if mean < 200 else 'W', 'mean': round(mean, 1)})
    return res, sub.shape

if __name__ == '__main__':
    for r, (y0, y1) in enumerate(rows):
        for c, (x0, x1) in enumerate(cols):
            if r == 2 and c == 2:
                continue
            res, shp = regions(y0, y1, x0, x1)
            print(f'第{r+1}行第{c+1}幅 (区域数{len(res)}, 灰{sum(1 for z in res if z["color"]=="G")}):')
            for z in sorted(res, key=lambda z: (z['cy'], z['cx'])):
                print('   ', z)
    for k, (x0, x1) in enumerate(opt_cols):
        res, shp = regions(330, 424, x0, x1)
        print(f'选项{"ABCD"[k]} (区域数{len(res)}, 灰{sum(1 for z in res if z["color"]=="G")}):')
        for z in sorted(res, key=lambda z: (z['cy'], z['cx'])):
            print('   ', z)

# ---------- 规律检验 ----------
CANON = {
    1: {'外左上': (32, 29), '外右上': (64, 29), '内左上': (42, 37), '内右上': (55, 37),
        '内左下': (42, 55.5), '内右下': (55, 55.5), '外左下': (32, 63), '外右下': (64, 63)},
    2: {'外上L': (38, 25), '内上': (48, 35.5), '外右': (68.5, 35.5), '内中L': (46, 53),
        '内小方': (55, 62), '外左下': (31.4, 66), '外右下L': (64, 71)},
    3: {'外上': (47, 21.5), '内上': (47, 38.5), '外左': (21, 47), '内左': (38, 47),
        '内右': (55, 47), '外右': (72, 47), '内下': (47, 55.5), '外下': (47, 72.8)},
}

def named(res, row):
    out = {}
    for z in res:
        key = min(CANON[row], key=lambda k: (CANON[row][k][0] - z['cx']) ** 2 + (CANON[row][k][1] - z['cy']) ** 2)
        assert key not in out
        out[key] = z['color']
    assert len(out) == len(CANON[row])
    return out

if __name__ == '__main__':
    print('\n===== 规律检验 =====')
    figs = {}
    for r, (y0, y1) in enumerate(rows):
        for c, (x0, x1) in enumerate(cols):
            if r == 2 and c == 2:
                continue
            figs[(r + 1, c + 1)] = named(regions(y0, y1, x0, x1)[0], r + 1)
    opts = {}
    for k, (x0, x1) in enumerate(opt_cols):
        opts['ABCD'[k]] = named(regions(330, 424, x0, x1)[0], 3)

    combo = {}
    for r in (1, 2):
        f1, f2, f3 = figs[(r, 1)], figs[(r, 2)], figs[(r, 3)]
        print(f'第{r}行 逐区域(图1,图2→图3):')
        for key in CANON[r]:
            print('   ', key, f1[key], f2[key], '→', f3[key])
            combo.setdefault((f1[key], f2[key]), set()).add(f3[key])
        inv = all(f3[k] != f2[k] for k in CANON[r])
        print(f'  第{r}行 图3是否恰为图2黑白互换:', inv)
    print('前两行归纳的叠加对应:', {k: sorted(v) for k, v in combo.items()})
    assert all(len(v) == 1 for v in combo.values())
    rule = {k: next(iter(v)) for k, v in combo.items()}
    f1, f2 = figs[(3, 1)], figs[(3, 2)]
    pred = {k: rule[(f1[k], f2[k])] for k in CANON[3]}
    print('第3行预测:', pred)
    for o in 'ABCD':
        diff = [k for k in CANON[3] if opts[o][k] != pred[k]]
        print(o, '灰块数', sum(v == 'G' for v in opts[o].values()), '与预测不同的区域:', diff)
    # 宽松规律（每个位置三幅中灰色出现1或2次）下的符合情况
    for o in 'ABCD':
        ok = all(1 <= [f1[k], f2[k], opts[o][k]].count('G') <= 2 for k in CANON[3])
        print(o, '满足“同一位置三幅图中灰色出现1~2次”:', ok)

# 第48题：读出每个4x4方格图中黑格位置（按像素采样）
import sys
from PIL import Image
import numpy as np

p = '/home/user/xing-ce1/江浙行测_AI题库/images/original/649.png'
im = np.array(Image.open(p).convert('L')).astype(int)
H, W = im.shape
dark = im < 128

def lines(arr, thr):
    """把超过阈值的连续索引合并成线，返回每条线中心"""
    idx = [i for i, v in enumerate(arr) if v >= thr]
    groups = []
    for i in idx:
        if groups and i - groups[-1][-1] <= 1:
            groups[-1].append(i)
        else:
            groups.append([i])
    return [(g[0] + g[-1]) / 2 for g in groups]

def find_grids(y0, y1):
    # 在 [y0,y1) 行带里找网格线
    band = dark[y0:y1]
    rows = lines(band.sum(axis=1), 0.45 * band.shape[1] * 0)  # placeholder
    return band

def read_band(y0, y1, label):
    band = dark[y0:y1]
    # 横向网格线：该行暗像素数很多
    rowsum = band.sum(axis=1)
    hl = [y0 + r for r in lines(rowsum, rowsum.max() * 0.6)]
    # 竖向线：在第一条横线与最后一条横线之间，整列几乎全暗
    top, bot = int(hl[0]), int(hl[-1])
    sub = dark[top:bot + 1]
    colsum = sub.sum(axis=0)
    vl = lines(colsum, (bot - top) * 0.95)
    print(label, 'hlines', hl)
    print(label, 'vlines', vl)
    return hl, vl

def cells(hl, vl):
    # hl: 5条横线；vl: 一组 5 条竖线
    g = []
    for r in range(4):
        row = []
        for c in range(4):
            y0, y1 = int(hl[r]) + 3, int(hl[r + 1]) - 2
            x0, x1 = int(vl[c]) + 3, int(vl[c + 1]) - 2
            frac = dark[y0:y1, x0:x1].mean()
            row.append(frac)
        g.append(row)
    return g

if __name__ == '__main__':
    out = {}
    for (y0, y1, label) in [(10, 125, 'top'), (165, 280, 'bottom')]:
        hl, vl = read_band(y0, y1, label)
        # 竖线按每 5 条分组（相邻两格共用外框时需要人工核对）
        out[label] = (hl, vl)
    # 题干：5 个图 + 问号；选项：4 个图
    for label, (hl, vl) in out.items():
        # 网格竖线：间距约 23 的连续 5 条为一组
        groups = []
        cur = [vl[0]]
        for v in vl[1:]:
            if 21 <= v - cur[-1] <= 26:
                cur.append(v)
            else:
                if len(cur) >= 5:
                    groups.append(cur[:5])
                cur = [v]
        if len(cur) >= 5:
            groups.append(cur[:5])
        print(label, 'grid groups', groups)
        for gi, gv in enumerate(groups):
            g = cells(hl, gv)
            print(f'{label} #{gi+1}')
            for row in g:
                print('   ' + ' '.join('#' if f > 0.5 else ('.' if f < 0.1 else '?') for f in row),
                      '   ', ' '.join(f'{f:.2f}' for f in row))

# -*- coding: utf-8 -*-
"""第90题：读四幅折线图（250x120 PNG）的拐点像素，与2020—2023年木浆产量同比增量逐点对照。

做法：
1. 从输入 data.json 读木浆产量表，算2020—2023年同比增量（以及几种错误口径，看各对应哪个选项）。
2. 对每幅图，取每一列深色像素的平均 y（图像坐标，向下为正），得到折线 y(x)。
3. 拐点 x 取折线首尾端点和两个转折处：用分段线性拟合（穷举两个断点）求最小残差的断点。
4. 把四个点的 y 换成“数值高度” h = -y，线性映射到数据的最小—最大区间，与数据比较；
   同时比较三段升降的方向和幅度之比。
"""
import itertools
import json
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', '..', '输入', 'data.json')
ASSET_DIR = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读'


def load_pulp_table():
    d = json.load(open(DATA, encoding='utf-8'))
    m4 = [m for m in d['materials'] if m['id'].endswith('-m4')][0]
    tab = [b for b in m4['blocks'] if b['type'] == 'table'][0]
    return {int(r[0]): float(r[1]) for r in tab['rows']}, d


def column_profile(path, thr=128):
    im = np.asarray(Image.open(path).convert('L'), dtype=float)
    h, w = im.shape
    xs, ys = [], []
    for x in range(w):
        dark = np.where(im[:, x] < thr)[0]
        if len(dark):
            xs.append(x)
            ys.append(dark.mean())
    return np.array(xs), np.array(ys), (w, h)


def fit_segments(xs, ys):
    """三段折线拟合：穷举两个断点，最小化每段直线拟合的残差平方和。"""
    best = None
    n = len(xs)
    for i in range(5, n - 10):
        for j in range(i + 5, n - 5):
            sse = 0.0
            for a, b in ((0, i), (i, j), (j, n)):
                p = np.polyfit(xs[a:b], ys[a:b], 1)
                sse += ((np.polyval(p, xs[a:b]) - ys[a:b]) ** 2).sum()
            if best is None or sse < best[0]:
                best = (sse, i, j)
    _, i, j = best
    segs = [(0, i), (i, j), (j, n)]
    fits = [np.polyfit(xs[a:b], ys[a:b], 1) for a, b in segs]
    # 拐点取相邻两段直线的交点；端点取首尾列在首/末段直线上的值
    x0, x3 = xs[0], xs[-1]
    x1 = (fits[1][1] - fits[0][1]) / (fits[0][0] - fits[1][0])
    x2 = (fits[2][1] - fits[1][1]) / (fits[1][0] - fits[2][0])
    pts = [(x0, np.polyval(fits[0], x0)), (x1, np.polyval(fits[0], x1)),
           (x2, np.polyval(fits[1], x2)), (x3, np.polyval(fits[2], x3))]
    return pts


def describe(vals):
    d = np.diff(vals)
    return d


def main():
    out, d = load_pulp_table()
    yrs = [2020, 2021, 2022, 2023]
    inc = np.array([out[y] - out[y - 1] for y in yrs])
    rate = np.array([(out[y] / out[y - 1] - 1) * 100 for y in yrs])
    level = np.array([out[y] for y in yrs])
    inc_1922 = np.array([out[y] - out[y - 1] for y in [2019, 2020, 2021, 2022]])
    print('2020—2023年同比增量（万吨）:', inc, ' 相邻差:', np.diff(inc))
    print('2020—2023年同比增速（%）  :', rate.round(2), ' 相邻差:', np.diff(rate).round(2))
    print('2020—2023年产量（万吨）    :', level, ' 相邻差:', np.diff(level))
    print('2019—2022年同比增量（万吨）:', inc_1922, ' 相邻差:', np.diff(inc_1922))

    q = [x for x in d['questions'] if x['number'] == 90][0]
    swap = inc.copy()
    swap[1], swap[2] = inc[2], inc[1]
    first127 = inc.copy()
    first127[0] = out[2019] - out[2018]
    series = {'增量2020—2023（正确口径）': inc, '增速2020—2023': rate,
              '产量2020—2023': level, '增量2019—2022（年份错位）': inc_1922,
              '增量但2021、2022两年互换(226,306,319,197)': swap,
              '首点误用2019年增量(127,319,306,197)': first127}
    print()
    for opt in 'ABCD':
        rel = q['options'][opt][0]['path']
        xs, ys, (w, h) = column_profile(os.path.join(ASSET_DIR, rel))
        pts = fit_segments(xs, ys)
        hgt = np.array([-p[1] for p in pts])           # 数值越大越靠上
        seg = np.diff(hgt)
        print(f'{opt}: 图宽高={w}x{h} 拐点(x,y)=' + ', '.join(f'({p[0]:.1f},{p[1]:.1f})' for p in pts))
        print(f'   三段升降(像素,向上为正)={seg.round(1)}  方向={"".join("升" if s > 0 else "降" for s in seg)}')
        for name, v in series.items():
            # 线性映射：用最小二乘把数据映射到像素高度 h ≈ a*v + b（a>0），看残差
            A = np.vstack([v, np.ones_like(v)]).T
            (a, b), *_ = np.linalg.lstsq(A, hgt, rcond=None)
            resid = hgt - (a * v + b)
            dir_ok = all(np.sign(np.diff(v)) == np.sign(seg))
            print(f'   对照{name}: 方向一致={dir_ok}  a={a:.3f}  最大残差={np.abs(resid).max():.1f}px')
        print()

    # 正确口径下的期望形状（映射到 B 图的像素尺度，便于在解析里描述）
    print('增量三段变化:', np.diff(inc), ' 第三段/第一段=', round(abs(np.diff(inc)[2]) / np.diff(inc)[0], 2),
          ' 第二段/第一段=', round(abs(np.diff(inc)[1]) / np.diff(inc)[0], 2))
    print('首点(2020)与末点(2023)谁高: 2020=%d, 2023=%d' % (inc[0], inc[3]))


if __name__ == '__main__':
    main()

"""第48题：提取每个面板的灰色小方块（由格线分隔的灰色区域），量化成格子坐标，
检验第一组"图1 = 图2 + 图3"（图2不旋转嵌入图1，余下部分经旋转/翻转得到图3），
再对第二组枚举四个选项。"""
import os
import sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from regions import label

P = "/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s21_p11_i02.png"
g = np.array(Image.open(P).convert('L')).astype(int)

# 灰色像素（方块填充色约128）
gray = (g > 90) & (g < 200)


def cells_in(box):
    x0, y0, x1, y1 = box
    sub = gray[y0:y1, x0:x1]
    lab, comps = label(sub)
    cs = []
    for pts in comps:
        if len(pts) < 80:  # 去掉边线抗锯齿形成的小碎块
            continue
        ys = np.array([p[0] for p in pts]) + y0
        xs = np.array([p[1] for p in pts]) + x0
        cs.append((xs.mean(), ys.mean(), len(pts)))
    if not cs:
        return frozenset(), cs
    # 估计格距：最近邻距离中位数
    pts = np.array([(c[0], c[1]) for c in cs])
    d = []
    for i in range(len(pts)):
        dd = np.sqrt(((pts - pts[i]) ** 2).sum(1))
        dd = dd[dd > 1]
        if len(dd):
            d.append(dd.min())
    step = np.median(d) if d else 15
    xmin, ymin = pts[:, 0].min(), pts[:, 1].min()
    cells = frozenset((int(round((y - ymin) / step)), int(round((x - xmin) / step))) for x, y in pts)
    return cells, (step, cs)


def norm(s):
    r0 = min(r for r, c in s); c0 = min(c for r, c in s)
    return frozenset((r - r0, c - c0) for r, c in s)


def show(s):
    s = norm(s)
    R = max(r for r, c in s) + 1; C = max(c for r, c in s) + 1
    return '\n'.join(''.join('#' if (r, c) in s else '.' for c in range(C)) for r in range(R))


def rot(s):  # 顺时针90°
    return norm(frozenset((c, -r) for r, c in s))


def flip(s):
    return norm(frozenset((r, -c) for r, c in s))


def transforms(s):
    out = {}
    cur = norm(s)
    for k in range(4):
        out[f'顺时针{90*k}°'] = cur
        out[f'镜像后顺时针{90*k}°'] = rot_k(flip(s), k)
        cur = rot(cur)
    return out


def rot_k(s, k):
    s = norm(s)
    for _ in range(k):
        s = rot(s)
    return s


def connected(s):
    s = set(s)
    if not s:
        return False
    st = [next(iter(s))]; seen = {st[0]}
    while st:
        r, c = st.pop()
        for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (r + d[0], c + d[1])
            if n in s and n not in seen:
                seen.add(n); st.append(n)
    return len(seen) == len(s)


def embeddings(big, piece):
    """piece 不旋转平移嵌入 big 的所有方式，返回剩余部分。"""
    piece = norm(piece)
    res = []
    for (br, bc) in big:
        for (pr, pc) in [min(piece)]:
            dr, dc = br - pr, bc - pc
            placed = frozenset((r + dr, c + dc) for r, c in piece)
            if placed <= big:
                res.append((dr, dc, big - placed))
    # 去重
    seen = set(); out = []
    for dr, dc, rem in res:
        if rem not in seen:
            seen.add(rem); out.append((dr, dc, rem))
    return out


boxes_top = {'1-1': (8, 8, 94, 97), '1-2': (99, 8, 185, 97), '1-3': (189, 8, 276, 97),
             '2-1': (325, 8, 411, 97), '2-2': (415, 8, 501, 97)}
boxes_opt = {'A': (119, 129, 205, 217), 'B': (209, 129, 295, 217), 'C': (300, 129, 386, 217), 'D': (391, 129, 477, 217)}
fig = {}
for k, b in {**boxes_top, **boxes_opt}.items():
    cells, info = cells_in(b)
    fig[k] = cells
    print(f'【{k}】 {len(cells)}格  格距≈{info[0]:.1f}')
    print(show(cells))

print('\n=== 第一组：图2平移嵌入图1，剩余部分 ===')
for dr, dc, rem in embeddings(fig['1-1'], fig['1-2']):
    ok = connected(rem)
    tf = [name for name, t in transforms(rem).items() if t == norm(fig['1-3'])]
    print(f'偏移({dr},{dc}) 剩余{len(rem)}格 连通={ok} 与图3相同的变换：{tf}')
    print(show(rem))

print('\n=== 第二组：图2（十字）平移嵌入图1，剩余部分 ===')
for dr, dc, rem in embeddings(fig['2-1'], fig['2-2']):
    ok = connected(rem)
    print(f'偏移({dr},{dc}) 剩余{len(rem)}格 连通={ok}')
    print(show(rem))
    for k in 'ABCD':
        tf = [name for name, t in transforms(rem).items() if t == norm(fig[k])]
        print(f'   选项{k}（{len(fig[k])}格）与剩余部分相同的变换：{tf}')

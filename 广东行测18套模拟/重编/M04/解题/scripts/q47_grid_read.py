# -*- coding: utf-8 -*-
"""Q47 读图：每格是 4×4 点阵，每个位置为 黑圆(B) / 白圆(W) / 空(.)。

读法：在每个格子里取深色像素的外接框，按 4×4 等分得到 16 个圆心；
圆心附近 3×3 像素平均灰度低 → 黑圆；否则看半径约 6 像素的圆周上深色像素比例，高 → 白圆，低 → 空。
"""
import numpy as np
from PIL import Image

IMG = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s19_p12_i01.png'
a = np.array(Image.open(IMG).convert('L')).astype(float)

rows_top = [(7, 93), (95, 180), (182, 267)]
cols_top = [(67, 155), (157, 244), (246, 333)]
panels = {}
for i, (r0, r1) in enumerate(rows_top):
    for j, (c0, c1) in enumerate(cols_top):
        if (i, j) != (2, 2):
            panels['%d%d' % (i + 1, j + 1)] = (c0, r0, c1, r1)
opt_cols = [(7, 101), (104, 199), (201, 296), (299, 393)]
for k, (c0, c1) in zip('ABCD', opt_cols):
    panels[k] = (c0, 290, c1, 382)


def read_panel(box):
    c0, r0, c1, r1 = box
    sub = a[r0 + 3:r1 - 3, c0 + 3:c1 - 3]
    d = sub < 128
    ys, xs = np.nonzero(d)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    sx = (x1 - x0) / 4.0
    sy = (y1 - y0) / 4.0
    grid = []
    for r in range(4):
        row = ''
        for c in range(4):
            cx = x0 + sx * (c + 0.5)
            cy = y0 + sy * (r + 0.5)
            core = sub[int(round(cy)) - 1:int(round(cy)) + 2, int(round(cx)) - 1:int(round(cx)) + 2].mean()
            if core < 110:
                row += 'B'
                continue
            rad = 0.40 * (sx + sy) / 2
            ring = []
            for t in np.linspace(0, 2 * np.pi, 48, endpoint=False):
                px = int(round(cx + rad * np.cos(t)))
                py = int(round(cy + rad * np.sin(t)))
                ring.append(sub[py, px] < 128)
            row += 'W' if np.mean(ring) > 0.45 else '.'
        grid.append(row)
    return grid, (round(sx, 1), round(sy, 1))


def check_rule(G):
    """按行逐位置建立 (第1幅, 第2幅) -> 第3幅 的对应表，检查前两行是否自洽，再推第三行并与选项比对。"""
    table = {}
    conflicts = []
    for r in '12':
        x, y, z = G[r + '1'], G[r + '2'], G[r + '3']
        for i in range(4):
            for j in range(4):
                key = (x[i][j], y[i][j])
                if key in table and table[key] != z[i][j]:
                    conflicts.append((r, i + 1, j + 1, key, table[key], z[i][j]))
                table.setdefault(key, z[i][j])
    print('\n前两行得到的对应表（第1幅,第2幅）→第3幅：')
    for k in sorted(table):
        print('   ', k, '->', table[k])
    print('冲突：', conflicts if conflicts else '无')
    # 同一规律的“计数”说法：第1幅有圆计1，第2幅白圆计1、黑圆计0，相加 0空1白2黑
    lv = {0: '.', 1: 'W', 2: 'B'}
    ok = all(lv[(k[0] != '.') + (k[1] == 'W')] == v for k, v in table.items())
    print('计数说法与对应表一致：', ok)
    x, y = G['31'], G['32']
    pred = []
    for i in range(4):
        row = ''
        for j in range(4):
            row += lv[(x[i][j] != '.') + (y[i][j] == 'W')]
        pred.append(row)
    print('第三行推出的问号图：', ' '.join(pred))
    for o in 'ABCD':
        diff = sum(G[o][i][j] != pred[i][j] for i in range(4) for j in range(4))
        print('  选项', o, ' '.join(G[o]), ' 不一致位置数 =', diff)
    # 再从列方向试同样的“逐位置对应表”，看是否自洽（作为排除其他方向的检验）
    table2, conf2 = {}, 0
    for c in '12':
        x, y, z = G['1' + c], G['2' + c], G['3' + c]
        for i in range(4):
            for j in range(4):
                key = (x[i][j], y[i][j])
                if key in table2 and table2[key] != z[i][j]:
                    conf2 += 1
                table2.setdefault(key, z[i][j])
    print('按列方向建立对应表的冲突数：', conf2)


if __name__ == '__main__':
    G = {}
    for k, box in panels.items():
        g, sp = read_panel(box)
        G[k] = g
        print(k, '点距', sp, ' '.join(g))
    check_rule(G)

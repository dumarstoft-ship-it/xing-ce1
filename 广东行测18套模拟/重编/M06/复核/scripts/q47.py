"""第47题：3x3 黑白（灰白）叠加。
每个面板用 regions.py 按线条切出封闭区域并判灰/白，同一行内按"相对面板左上角的质心"对齐区域，
由第1、2行推出叠加表 (第1幅颜色, 第2幅颜色) -> 第3幅颜色，再套到第3行，与四个选项比对。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from regions import regions

P = "/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s21_p11_i01.png"
COLS = [(55, 149), (153, 246), (250, 344)]
ROWS = [(13, 101), (105, 199), (203, 297)]
OPTS = {'A': (11, 102), 'B': (106, 197), 'C': (201, 292), 'D': (296, 387)}
OPT_Y = (330, 424)


def panel(x0, x1, y0, y1):
    rs = [r for r in regions(P, (x0, y0, x1, y1)) if not r['outside']]
    return [((r['cx'] - x0, r['cy'] - y0), 1 if r['color'] == 'gray' else 0) for r in rs]


def align(ref, other, tol=4.0):
    """把 other 的区域按质心对齐到 ref 的区域顺序。"""
    out = []
    for (c, _) in ref:
        best = min(other, key=lambda z: (z[0][0] - c[0]) ** 2 + (z[0][1] - c[1]) ** 2)
        d = ((best[0][0] - c[0]) ** 2 + (best[0][1] - c[1]) ** 2) ** 0.5
        assert d < tol, (c, best, d)
        out.append(best[1])
    return out


table = {}
for ri, (y0, y1) in enumerate(ROWS[:2]):
    ps = [panel(x0, x1, y0, y1) for x0, x1 in COLS]
    ref = ps[0]
    cols = [[v for _, v in ref], align(ref, ps[1]), align(ref, ps[2])]
    print(f'第{ri+1}行 区域数{len(ref)}  图1灰={sum(cols[0])} 图2灰={sum(cols[1])} 图3灰={sum(cols[2])}')
    for a, b, c in zip(*cols):
        if (a, b) in table:
            assert table[(a, b)] == c, f'第{ri+1}行与已有叠加规则冲突'
        table[(a, b)] = c
    print('   各区域(图1,图2)->图3：', sorted(set(zip(zip(cols[0], cols[1]), cols[2]))))

name = {0: '白', 1: '灰'}
print('由前两行得到的叠加表：', {f'{name[a]}+{name[b]}': name[c] for (a, b), c in sorted(table.items())})
print('  （即第3幅 = 第2幅颜色取反，与第1幅无关）')

y0, y1 = ROWS[2]
p1 = panel(*COLS[0], y0, y1); p2 = panel(*COLS[1], y0, y1)
ref = p1
v1 = [v for _, v in ref]; v2 = align(ref, p2)
pred = [table[(a, b)] for a, b in zip(v1, v2)]
print('\n第3行 预测第3幅各区域：', pred)
for k, (x0, x1) in OPTS.items():
    po = panel(x0, x1, *OPT_Y)
    vo = align(ref, po, tol=6.0)
    diff = sum(a != b for a, b in zip(pred, vo))
    print(f'选项{k}：{vo}  与预测不同的区域数 {diff}')

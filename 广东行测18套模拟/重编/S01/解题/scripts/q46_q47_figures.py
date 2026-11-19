"""S01 第46、47题图形核验（线段由放大图读出）。

第46题：正方形边框上 8 个位置顺时针编号 0左上角 1上中 2右上角 3右中 4右下角 5下中 6左下角 7左中。
每幅图 = 三个端点两两连线（落在同一条边上的连线与边框重合）。
第47题：按图读出顶点度数，算奇点数（笔画数＝奇点数/2）、线条数，区域数用欧拉公式 V−E+F=2。
"""
from itertools import combinations
NAME = ['左上角', '上中', '右上角', '右中', '右下角', '下中', '左下角', '左中']
SIDE = {0: {'上', '左'}, 1: {'上'}, 2: {'上', '右'}, 3: {'右'}, 4: {'下', '右'}, 5: {'下'}, 6: {'下', '左'}, 7: {'左'}}

def visible_lines(points):
    pts = sorted(set(points))
    return {frozenset(p) for p in combinations(pts, 2) if not (SIDE[p[0]] & SIDE[p[1]])}

fig = {  # (红, 绿, 蓝) 三个点
 1: (0, 3, 5), 2: (7, 2, 6), 3: (6, 1, 7), 4: (5, 0, 0)}
lines = {1: {(0,3),(0,5),(3,5)}, 2: {(2,7),(2,6)}, 3: {(1,7),(1,6)}, 4: {(0,5)}}
for k in fig:
    assert visible_lines(fig[k]) == {frozenset(x) for x in lines[k]}, k
# 红、绿每次逆时针移一格(-1)，蓝每次顺时针移一格(+1)
for k in (1, 2, 3):
    r, g, b = fig[k]; r2, g2, b2 = fig[k+1]
    assert (r - 1) % 8 == r2 and (g - 1) % 8 == g2 and (b + 1) % 8 == b2
r, g, b = fig[4]
nxt = ((r - 1) % 8, (g - 1) % 8, (b + 1) % 8)
pred = visible_lines(nxt)
print('第46题 问号处三点：', [NAME[i] for i in nxt], '应有连线：', sorted(tuple(sorted(NAME[i] for i in l)) for l in pred))
opts = {'A': {(1,4)}, 'B': {(1,6),(1,4)}, 'C': {(0,3),(0,4)}, 'D': {(1,7),(1,4),(4,7)}}
for k, v in opts.items():
    print('   ', k, '符合' if {frozenset(x) for x in v} == pred else '不符合')
# 交点数：4个角 + 不在角上的端点
for k, v in list(lines.items()) + list(opts.items()):
    ends = {i for l in v for i in l}
    print('    交点数', k, 4 + len([i for i in ends if i % 2 == 1]))

# ---- 第47题 ----
# 每图记：顶点度数表（含边框角点）、线条数（曲线算1条）
Q47 = {  # 度数表含边框4个角；T形点3度，十字交叉4度
 '图1': dict(deg=[2,2,2,2, 3,3], lines=1),                       # 一条斜线，两端落在上下边
 '图2': dict(deg=[2,2,2,2, 3,3,3,3], lines=2),                   # 曲线、竖线各两端落在上下边
 '图3': dict(deg=[2,2, 3,3, 3,3,3,3], lines=3),                  # 中间斜线连左下角、右上角
 'A':  dict(deg=[3,2,3,3, 3,3,3], lines=3),                      # 左上、左下角各接一线；上边点、右边点、斜线上的接点
 'B':  dict(deg=[3,2,2,2, 3,3,3,3,3,3,3], lines=4),              # 4条线的8个端点都是T形点
 'C':  dict(deg=[3,2,2,2, 3,3,3,3, 4, 3], lines=3),              # 两线十字交叉1处
 'D':  dict(deg=[2,2,2,2, 3,4,4,3, 3,3, 4,4,4], lines=4),        # 两竖线各与横线十字相交、斜线穿过横线；斜线两端与竖线端点重合（4度）
}
for k, d in Q47.items():
    V = len(d['deg']); E = sum(d['deg']) // 2
    F = E - V + 2 - 1   # 去掉外部区域
    odd = sum(x % 2 for x in d['deg'])
    print(f'第47题 {k}: 区域 {F}，线条 {d["lines"]}，奇点 {odd}（{odd//2 if odd else 1} 笔）')

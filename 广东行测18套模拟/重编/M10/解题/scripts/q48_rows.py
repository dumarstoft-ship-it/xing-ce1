"""M10 第48题（GD2016-XJ-Q058）：两组 2×3 方格涂灰。

格子读法：上行、下行各3格，1=灰。核对：
1) 同位置叠加（含左右/上下翻转、旋转180°后再叠加）找不到任何固定的“灰灰/灰白/白白”运算；
2) 灰格总数 3、5、5 | 3、3 无递变；
3) 每幅图上下两行灰格数相差1，选项中只有B如此。
"""
import itertools
F = {
 '图1': ((1,1,0),(0,0,1)), '图2': ((1,1,1),(0,1,1)), '图3': ((1,0,1),(1,1,1)),
 '图4': ((1,0,1),(0,1,0)), '图5': ((0,1,0),(1,1,0)),
 'A': ((1,1,1),(0,1,0)), 'B': ((0,1,1),(1,0,0)), 'C': ((1,1,1),(1,1,1)), 'D': ((1,1,0),(0,1,1)),
}
lr = lambda g: tuple(tuple(r[::-1]) for r in g)
ud = lambda g: (g[1], g[0])
T = {'原样': lambda g: g, '左右翻': lr, '上下翻': ud, '转180°': lambda g: lr(ud(g))}
hits = 0
for (n1,t1),(n2,t2),(n3,t3) in itertools.product(T.items(), repeat=3):
    for f in itertools.product([0,1], repeat=4):
        g1, g2 = t1(F['图1']), t2(F['图2'])
        r = t3(tuple(tuple(f[g1[i][j]*2+g2[i][j]] for j in range(3)) for i in range(2)))
        if r == F['图3']:
            hits += 1
print('叠加规则（含翻转）能由图1、图2得到图3的个数：', hits)
for k, g in F.items():
    print(f'{k}: 上行{sum(g[0])} 下行{sum(g[1])} 相差{abs(sum(g[0])-sum(g[1]))} 合计{sum(g[0])+sum(g[1])}')

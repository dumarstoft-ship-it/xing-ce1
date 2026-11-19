"""M10 第68题：四个电路开关闭合后，哪个电路的小灯泡都能正常发光（原卷2021年乡镇卷第84题题图，已看图）。
按题图连线建模（W导线、S开关、L灯泡、V电池）：
 A：左竖线连通左上角、中线左端、左下角；上方导线从左上角到L1上端的节点P，再经L2到右上角；右竖线连通右上角、
    中线右端、右下角；L1竖接在P与中线节点Q之间；开关在中线上、左竖线与Q之间；Q向右接右竖线；电池在底边。
 B：上边导线完整连通，上方另有“L1—开关”支路两端都接在这段上边导线上；L2在右竖线；电池在底边。
 C：左侧两条竖线把上、中、下三条线的左端连成一点；L1在上边，L2在下边，“电池—开关”在中线，三条线右端由右竖线连通。
 D：左右两条竖线；开关在上边，L2在中线，L1与电池串联在底边。
用并查集合并导线和闭合的开关，再做节点分析（电池带很小内阻以免短路时方程奇异），看各灯两端电压是否等于电源电压。"""
import numpy as np

E, r_int, R_bulb = 3.0, 1e-3, 10.0
circuits = {
    'A': [('W', 'TL', 'P'), ('W', 'TL', 'ML'), ('W', 'ML', 'BL'), ('W', 'TR', 'MR'), ('W', 'MR', 'BR'),
          ('W', 'Q', 'MR'), ('L', 'L2', 'P', 'TR'), ('L', 'L1', 'P', 'Q'), ('S', 'ML', 'Q'), ('V', 'BL', 'BR')],
    'B': [('W', 'TL', 'X1'), ('W', 'X1', 'X2'), ('W', 'X2', 'TR'), ('L', 'L1', 'X1', 'Y'), ('S', 'Y', 'X2'),
          ('L', 'L2', 'TR', 'BR'), ('W', 'TL', 'BL'), ('V', 'BL', 'BR')],
    'C': [('W', 'TLa', 'MLa'), ('W', 'MLa', 'BLa'), ('W', 'TLa', 'TLb'), ('W', 'BLa', 'BLb'), ('W', 'TLb', 'BLb'),
          ('L', 'L1', 'TLb', 'TR'), ('L', 'L2', 'BLb', 'BR'), ('V', 'MLa', 'Z'), ('S', 'Z', 'MR'),
          ('W', 'TR', 'MR'), ('W', 'MR', 'BR')],
    'D': [('W', 'TL', 'ML'), ('W', 'ML', 'BL'), ('W', 'TR', 'MR'), ('W', 'MR', 'BR'), ('S', 'TL', 'TR'),
          ('L', 'L2', 'ML', 'MR'), ('L', 'L1', 'BL', 'K'), ('V', 'K', 'BR')],
}

def solve(elems, closed):
    parent = {}
    def find(a):
        parent.setdefault(a, a)
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    def union(a, b):
        parent[find(a)] = find(b)
    for e in elems:
        for n in e[1:] if e[0] != 'L' else e[2:]:
            find(n)
        if e[0] == 'W' or (e[0] == 'S' and closed):
            union(e[1], e[2])
    nodes = sorted({find(n) for n in parent})
    idx = {n: i for i, n in enumerate(nodes)}
    k = len(nodes)
    G = np.zeros((k, k)); I = np.zeros(k)
    def add_g(a, b, g):
        i, j = idx[find(a)], idx[find(b)]
        if i == j:
            return
        G[i, i] += g; G[j, j] += g; G[i, j] -= g; G[j, i] -= g
    for e in elems:
        if e[0] == 'L':
            add_g(e[2], e[3], 1 / R_bulb)
        elif e[0] == 'S' and not closed:
            add_g(e[1], e[2], 1e-12)          # 断开：极小电导
        elif e[0] == 'V':                     # 诺顿等效：E/r 电流源并联 r（e[1]为正极一侧，方向不影响结论）
            add_g(e[1], e[2], 1 / r_int)
            I[idx[find(e[1])]] += E / r_int
            I[idx[find(e[2])]] -= E / r_int
    G[0, :] = 0; G[0, 0] = 1; I[0] = 0        # 接地
    V = np.linalg.solve(G, I)
    out = {}
    for e in elems:
        if e[0] == 'L':
            out[e[1]] = abs(V[idx[find(e[2])]] - V[idx[find(e[3])]])
    return out

ok = []
for name, elems in circuits.items():
    on, off = solve(elems, True), solve(elems, False)
    print(name, '闭合：', {k: round(float(v), 3) for k, v in sorted(on.items())}, '断开：', {k: round(float(v), 3) for k, v in sorted(off.items())})
    if all(abs(v - E) < 0.01 for v in on.values()):
        ok.append(name)
print('闭合后两灯都在额定电压', E, 'V 的：', ok)
assert ok == ['C']

"""M11 第68题：电源电压不变，S₁闭合，S₂由闭合到断开，各电表示数变化。选项 A A₁不变 B A₂不变 C V₁不变 D V₂不变
按题图连线（原卷2015年县级卷第69题，已看图）建网表：左竖线各点为L1—L4，右竖线各点为R1—R4（竖线是导线）；
 第1行：L1—V₂—R1；第2行：L2—V₁—J，J—S₂—R2；第3行：L3—R₁—K，K—R₂—M，M—A₂—R3（J、K由竖导线相连）；
 第4行：L4—S₁—P，P—电源—Q，Q—A₁—R4。电流表取1e-6Ω，电压表取1e9Ω，导线与闭合开关并为同一节点，用节点分析求解。"""
import numpy as np
U, R1v, R2v = 6.0, 10.0, 20.0
def netlist(s2_closed):
    W = [('L1', 'L2'), ('L2', 'L3'), ('L3', 'L4'), ('R1', 'R2'), ('R2', 'R3'), ('R3', 'R4'), ('J', 'K'), ('L4', 'P')]  # S₁闭合
    if s2_closed:
        W.append(('J', 'R2'))
    E = [('V2', 'L1', 'R1', 1e9), ('V1', 'L2', 'J', 1e9), ('R1', 'L3', 'K', R1v), ('R2', 'K', 'M', R2v),
         ('A2', 'M', 'R3', 1e-6), ('A1', 'Q', 'R4', 1e-6)]
    return W, E
def solve(s2_closed):
    W, E = netlist(s2_closed)
    parent = {}
    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            x = parent[x]
        return x
    for a, b in W:
        parent[find(a)] = find(b)
    names = {find(n) for _, a, b, _ in E for n in (a, b)} | {find('P'), find('Q')}
    idx = {n: i for i, n in enumerate(sorted(names))}
    n = len(idx)
    G = np.zeros((n + 1, n + 1)); I = np.zeros(n + 1)
    for _, a, b, r in E:
        i, j = idx[find(a)], idx[find(b)]
        if i != j:
            g = 1 / r
            G[i, i] += g; G[j, j] += g; G[i, j] -= g; G[j, i] -= g
    p, q = idx[find('P')], idx[find('Q')]              # 理想电压源：V(P)−V(Q)=U，用附加变量表示电源电流
    G[p, n] += 1; G[q, n] -= 1; G[n, p] = 1; G[n, q] = -1; I[n] = U
    G[q, :] = 0; G[q, q] = 1; I[q] = 0                  # 以Q为参考点（替换Q的节点方程）
    G[q, n] = 0
    V = np.linalg.solve(G, I)
    out = {}
    for name, a, b, r in E:
        dv = V[idx[find(a)]] - V[idx[find(b)]]
        out[name] = abs(dv) if name.startswith('V') else abs(dv / r)
    return out
on, off = solve(True), solve(False)
for k in ('A1', 'A2', 'V1', 'V2'):
    print('%s：S₂闭合 %.4f → 断开 %.4f  %s' % (k, on[k], off[k], '不变' if abs(on[k] - off[k]) < 1e-4 else '变化'))
same = [k for k in ('A1', 'A2', 'V1', 'V2') if abs(on[k] - off[k]) < 1e-4]
assert same == ['V2']
print('只有V₂（电源两端电压）不变 → D')

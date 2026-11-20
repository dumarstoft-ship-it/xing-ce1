"""S02 第68题：用一个开关控制办公室两盏灯（220V），最合理的电路。按四个选项的题图建网表，开关断开/闭合分别求两灯电压。
A：开关在干路，两灯并联；B：开关只与上面一盏灯串联，两灯并联；
C：两灯并联在电源两端，开关所在导线把两灯并联部分的两端直接连通（闭合即短路电源；若交叉处不相连，两灯根本不通电）；
D：开关与两灯串联。灯泡取484Ω（220V、100W）。"""
import numpy as np
U, R = 220.0, 484.0
nets = {
    'A': dict(W=[], L=[('a', 'b'), ('a', 'b')], S=('s', 'a'), src=('s', 'b')),
    'B': dict(W=[], L=[('c', 'b'), ('a', 'b')], S=('a', 'c'), src=('a', 'b')),
    'C': dict(W=[], L=[('a', 'b'), ('a', 'b')], S=('a', 'b'), src=('a', 'b')),
    'D': dict(W=[], L=[('a', 'c'), ('c', 'b')], S=('s', 'a'), src=('s', 'b')),
}
def solve(net, closed, r_src=0.01):
    parent = {}
    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            x = parent[x]
        return x
    for a, b in net['W'] + ([net['S']] if closed else []):
        parent[find(a)] = find(b)
    nodes = sorted({find(x) for e in net['L'] for x in e} | {find(x) for x in net['src']} | {find(x) for x in net['S']})
    idx = {x: i for i, x in enumerate(nodes)}
    G = np.zeros((len(nodes), len(nodes))); I = np.zeros(len(nodes))
    def add(a, b, g):
        i, j = idx[find(a)], idx[find(b)]
        if i == j: return
        G[i, i] += g; G[j, j] += g; G[i, j] -= g; G[j, i] -= g
    for a, b in net['L']:
        add(a, b, 1 / R)
    if not closed:
        add(*net['S'], 1e-12)
    p, q = net['src']                      # 电源以诺顿等效（小内阻）接入，避免短路时方程奇异
    add(p, q, 1 / r_src); I[idx[find(p)]] += U / r_src; I[idx[find(q)]] -= U / r_src
    G[0, :] = 0; G[0, 0] = 1; I[0] = 0
    V = np.linalg.solve(G, I)
    return [abs(V[idx[find(a)]] - V[idx[find(b)]]) for a, b in net['L']]
for k, net in nets.items():
    off, on = solve(net, False), solve(net, True)
    print(k, '断开：两灯电压', [round(float(v), 1) for v in off], '；闭合：', [round(float(v), 1) for v in on])
ok = [k for k, net in nets.items()
      if all(v < 1 for v in solve(net, False)) and all(abs(v - U) < 1 for v in solve(net, True))]
print('开关断开两灯都灭、闭合两灯都在220V正常发光的：', ok)
assert ok == ['A']

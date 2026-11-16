"""换入题 第69题（自动扶梯电路）：按 escalator_circuits.svg 的连线建立四个电路的网表，
用节点电压法算出 S1、S2 四种开合状态下电动机两端电压，逐条检查题干三项要求：
  (1) S1闭合、S2断开：电动机转动但低速（0 < U_M < 电源电压）；
  (2) S1闭合、S2闭合：电动机高速（U_M 大于(1)中的电压）；
  (3) S1断开：不论S2如何，电动机都不工作（U_M = 0）。
理想电源电压取1，R=1，电动机按电阻 R_M=1 处理；闭合开关为极小电阻，断开开关去掉。

网表（节点名对应SVG中的导线段；结点圆点处为连接）：
  A：T -S1- X1 -M- X2 -R- 负极；S2 跨接 X1、X2（与M并联）
  B：T -S2- X1 -M- X2 -R- 负极；S1 跨接 负极、X2（与R并联）
  C：T -S1- X1 -M- X2 -R- 负极；S2 跨接 负极、X2（与R并联）
  D：T -S1- X1；M 接在 X1 与负极之间；R 与 S2 串联后也接在 X1 与负极之间（与M并联）
"""
import numpy as np

V = 1.0
NETS = {
    'A': [('S1', 'T', 'X1'), ('M', 'X1', 'X2'), ('R', 'X2', 'GND'), ('S2', 'X1', 'X2')],
    'B': [('S2', 'T', 'X1'), ('M', 'X1', 'X2'), ('R', 'X2', 'GND'), ('S1', 'GND', 'X2')],
    'C': [('S1', 'T', 'X1'), ('M', 'X1', 'X2'), ('R', 'X2', 'GND'), ('S2', 'GND', 'X2')],
    'D': [('S1', 'T', 'X1'), ('M', 'X1', 'GND'), ('R', 'X1', 'Y'), ('S2', 'Y', 'GND')],
}


def motor_voltage(net, s1, s2):
    elems = []
    for name, a, b in net:
        if name == 'S1':
            if s1: elems.append((1e-9, a, b))
        elif name == 'S2':
            if s2: elems.append((1e-9, a, b))
        elif name in ('R', 'M'):
            elems.append((1.0, a, b))
    nodes = sorted({n for _, a, b in net for n in (a, b)} - {'T', 'GND'})
    idx = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)
    G = np.zeros((n, n)); I = np.zeros(n)
    fixed = {'T': V, 'GND': 0.0}
    for r, a, b in elems:
        g = 1.0 / r
        for p, q in ((a, b), (b, a)):
            if p in idx:
                G[idx[p], idx[p]] += g
                if q in idx:
                    G[idx[p], idx[q]] -= g
                else:
                    I[idx[p]] += g * fixed[q]
    # 悬空节点：加极小对地电导避免奇异
    G += np.eye(n) * 1e-15
    x = np.linalg.solve(G, I) if n else np.array([])
    volt = dict(fixed); volt.update({k: x[i] for k, i in idx.items()})
    m = [e for e in net if e[0] == 'M'][0]
    return abs(volt[m[1]] - volt[m[2]])


for k, net in NETS.items():
    u = {(s1, s2): motor_voltage(net, s1, s2) for s1 in (0, 1) for s2 in (0, 1)}
    req1 = 1e-6 < u[(1, 0)] < V - 1e-6
    req2 = u[(1, 1)] > u[(1, 0)] + 1e-6
    req3 = u[(0, 0)] < 1e-6 and u[(0, 1)] < 1e-6
    print(f'电路{k}：U_M(S1,S2) = ' + ', '.join(f'{s}:{v:.3f}' for s, v in u.items()))
    print(f'   要求(1)无人低速={req1}  要求(2)有人高速={req2}  要求(3)断开S1不工作={req3}  → 全部满足={req1 and req2 and req3}')

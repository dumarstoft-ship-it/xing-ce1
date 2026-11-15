"""Q67 nodal analysis. Topology read from original figure s17_p18_i00.png:
nodes: TL (left rail above A1), L (left rail below A1), M (middle bus), R (right rail), N2 (between A2 and L2), N3 (between L3 and A3)
A1: TL-L ; L1: TL-M ; V1: L-M ; A2: M-N2 ; L2: N2-R ; V2: M-R ; V3: TL-R ; source: L(+)-R(-) ; L3: L-N3 ; A3: N3-R
Run: python3 check_q67_circuit.py
"""
import numpy as np

def solve(R_bulb=10.0, rA=(1e-9, 1e-9, 1e-9), rV=1e12, U=6.0):
    nodes = ['TL', 'L', 'M', 'N2', 'N3']   # R is ground (0 V); L is fixed at U by ideal source
    idx = {n: i for i, n in enumerate(nodes)}
    elems = [  # (name, a, b, resistance)
        ('A1', 'TL', 'L', rA[0]), ('L1', 'TL', 'M', R_bulb), ('V1', 'L', 'M', rV),
        ('A2', 'M', 'N2', rA[1]), ('L2', 'N2', 'R', R_bulb), ('V2', 'M', 'R', rV),
        ('V3', 'TL', 'R', rV), ('L3', 'L', 'N3', R_bulb), ('A3', 'N3', 'R', rA[2]),
    ]
    n = len(nodes)
    G = np.zeros((n, n)); I = np.zeros(n)
    for _, a, b, r in elems:
        g = 1.0 / r
        for x, y in ((a, b), (b, a)):
            if x != 'R':
                G[idx[x], idx[x]] += g
                if y != 'R':
                    G[idx[x], idx[y]] -= g
    # enforce V(L) = U
    G[idx['L'], :] = 0; G[idx['L'], idx['L']] = 1; I[idx['L']] = U
    V = np.linalg.solve(G, I)
    pot = {nd: V[idx[nd]] for nd in nodes}; pot['R'] = 0.0
    out = {}
    for name, a, b, r in elems:
        out[name] = abs(pot[a] - pot[b]) / r if name.startswith('A') else abs(pot[a] - pot[b])  # meter readings are magnitudes
    return out

for label, kw in [('ideal meters', {}),
                  ('non-ideal, equal ammeter r=0.5', dict(rA=(0.5, 0.5, 0.5), rV=1e4)),
                  ('non-ideal, unequal ammeter r', dict(rA=(1.0, 0.2, 0.5), rV=1e4))]:
    o = solve(**kw)
    print(f'--- {label} (U=6V, bulb R=10 ohm)')
    print('  A1=%.4f A2=%.4f A3=%.4f (A)' % (o['A1'], o['A2'], o['A3']))
    print('  V1=%.4f V2=%.4f V3=%.4f (V)' % (o['V1'], o['V2'], o['V3']))
    print('  A: V3 smallest? ', o['V3'] < min(o['V1'], o['V2']))
    print('  B: A3 largest?  ', o['A3'] > max(o['A1'], o['A2']))
    print('  C: A1==A2?      ', abs(o['A1'] - o['A2']) < 1e-6 * max(1, o['A1']))
    print('  D: V1==V2?      ', abs(o['V1'] - o['V2']) < 1e-6 * max(1, o['V1']))

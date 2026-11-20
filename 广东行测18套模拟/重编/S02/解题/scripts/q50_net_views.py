"""S02 第50题（SYDW2024-Q068）：展开图折成立方体，检验各选项（上、前、右三面）是否可能。

不考虑数字方向，只看三面是否两两相邻、以及三面的相对位置（顺逆时针）。
判据：外法向量满足 n右 × n上 = n前 才是“前、右、上”这样的看法。
"""
import numpy as np

def fold(cells):
    start = min(cells)
    state = {start: (np.zeros(3), np.array([1., 0, 0]), np.array([0., 1, 0]), np.array([0., 0, 1]))}
    queue = [start]
    while queue:
        c = queue.pop(0)
        O, E1, E2, N = state[c]
        moves = {(1, 0): (O + E1, N, E2, -E1), (-1, 0): (O + N, -N, E2, E1),
                 (0, 1): (O + E2, E1, N, -E2), (0, -1): (O + N, E1, -N, E2)}
        for (dx, dy), st in moves.items():
            nb = (c[0] + dx, c[1] + dy)
            if nb in cells and nb not in state:
                state[nb] = st; queue.append(nb)
    return state

NET = {(0, 0): 3, (1, 0): 2, (1, 1): 1, (2, 1): 6, (3, 1): 5, (2, 2): 4}
st = fold(set(NET))
normal = {}
for c, lab in NET.items():
    O, E1, E2, N = st[c]
    center = O + 0.5 * E1 + 0.5 * E2
    normal[lab] = np.round(2 * (center - np.array([0.5, 0.5, 0.5]))).astype(int)  # 外法向
opp = sorted({tuple(sorted((a, b))) for a in normal for b in normal if a != b and (normal[a] == -normal[b]).all()})
print('相对面：', opp)
OPT = {'A': (2, 1, 3), 'B': (5, 2, 6), 'C': (2, 5, 6), 'D': (1, 4, 5)}  # (上, 前, 右)
for k, (t, f, r) in OPT.items():
    adj = all(abs(int(normal[a] @ normal[b])) == 0 for a, b in ((t, f), (t, r), (f, r)))
    ok = adj and (np.cross(normal[r], normal[t]) == normal[f]).all()
    print(k, f'上{t} 前{f} 右{r}', '三面两两相邻' if adj else '有相对面', '→ 可能' if ok else '→ 不可能')

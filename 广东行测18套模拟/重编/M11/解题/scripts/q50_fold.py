"""M11 第50题（GD2019-XJ-Q040）：把四个展开图折成立方体，检验三条虚线对角线。

题干立方体：前、上、右三个面各有一条虚线对角线，三条线两两首尾相接成一个三角形，
都不经过三个面的公共顶点（右上前顶点）。其余三面空白。
展开图按格子读入：(列, 行)，行向下；对角线 '/' 连接格子的左下、右上角，'\\' 连接左上、右下角。
"""
import numpy as np

def fold(cells):
    cells = set(cells)
    start = min(cells)
    state = {start: (np.zeros(3), np.array([1., 0, 0]), np.array([0., 1, 0]), np.array([0., 0, 1]))}
    queue = [start]
    while queue:
        c = queue.pop(0)
        O, E1, E2, N = state[c]
        moves = {
            (1, 0): (O + E1, N, E2, -E1),
            (-1, 0): (O + N, -N, E2, E1),
            (0, 1): (O + E2, E1, N, -E2),
            (0, -1): (O + N, E1, -N, E2),
        }
        for (dx, dy), st in moves.items():
            nb = (c[0] + dx, c[1] + dy)
            if nb in cells and nb not in state:
                state[nb] = st
                queue.append(nb)
    assert len(state) == 6
    return state

def pt(st, u, v):
    O, E1, E2, N = st
    return tuple(np.round(O + u * E1 + v * E2).astype(int))

def diag(st, kind):
    # 局部坐标 u 向右、v 向下；'/' 左下(0,1)—右上(1,0)，'\\' 左上(0,0)—右下(1,1)
    return frozenset([pt(st, 0, 1), pt(st, 1, 0)]) if kind == '/' else frozenset([pt(st, 0, 0), pt(st, 1, 1)])

def face_id(st):
    O, E1, E2, N = st
    corners = [pt(st, u, v) for u in (0, 1) for v in (0, 1)]
    return frozenset(corners)

NETS = {
 'A': ([(0,1),(1,1),(2,1),(3,1),(2,0),(2,2)], {(1,1): '/', (2,0): '/', (2,2): '/'}),
 'B': ([(0,0),(0,1),(1,1),(2,1),(3,1),(3,2)], {(0,0): '\\', (1,1): '\\', (2,1): '/'}),
 'C': ([(1,0),(0,1),(1,1),(2,1),(3,1),(3,2)], {(0,1): '\\', (3,1): '/', (3,2): '\\'}),
 'D': ([(2,0),(0,1),(1,1),(2,1),(3,1),(1,2)], {(0,1): '/', (2,0): '\\', (3,1): '\\'}),
}
for k, (cells, diags) in NETS.items():
    st = fold(cells)
    faces = {c: face_id(st[c]) for c in cells}
    assert len(set(faces.values())) == 6, k
    dfaces = [faces[c] for c in diags]
    common = set.intersection(*[set(f) for f in dfaces])
    segs = [diag(st[c], t) for c, t in diags.items()]
    ends = [p for s in segs for p in s]
    triangle = all(ends.count(p) == 2 for p in set(ends)) and len(set(ends)) == 3
    through_common = [bool(common) and next(iter(common)) in s for s in segs]
    ok = len(common) == 1 and triangle and not any(through_common)
    print(k, '三面共一个顶点' if len(common) == 1 else '三面不共顶点（有相对面）',
          '| 三条对角线首尾相接成三角形' if triangle else '| 不成三角形',
          '| 有线经过公共顶点' if any(through_common) else '',
          '→ 能折成' if ok else '→ 不能折成')

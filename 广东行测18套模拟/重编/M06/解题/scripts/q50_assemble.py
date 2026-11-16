"""第50题：由正视图、后视图还原组合体（21个小正方体），再穷举检验哪个选项的3个相同小立体能恰好拼成它。
坐标：x=列(正视图从左到右1..4)，y=层(1..3)，z=前后(0=前排,1=后排)。
选项里被挡住看不见的方块：A、B、C 各有 (1,1,1) 一块看不见，D 有 (1,1,1)、(2,1,1) 两块看不见；
组合体共21块=3×7，故每个小立体须为7块，看不见的方块应补上（另附：不补时的检验）。"""
import itertools
import numpy as np

composite = set()
for x in (1, 2, 4):
    for y in (1, 2, 3):
        composite.add((x, y, 0))
composite.add((3, 1, 0))
for x in (1, 2, 3):
    for y in (1, 2, 3):
        composite.add((x, y, 1))
composite |= {(4, 1, 1), (4, 2, 1)}
assert len(composite) == 21

VISIBLE = {
    'A': {(1, 1, 0), (2, 1, 0), (2, 1, 1), (1, 2, 1), (2, 2, 1), (1, 3, 1)},
    'B': {(1, 1, 0), (2, 1, 0), (1, 2, 0), (2, 1, 1), (3, 1, 1), (3, 2, 1)},
    'C': {(1, 1, 0), (1, 2, 0), (1, 2, 1), (2, 1, 1), (2, 2, 1), (2, 3, 1)},
    'D': {(1, 1, 0), (2, 1, 0), (1, 2, 1), (2, 2, 1), (3, 1, 1)},
}
HIDDEN = {'A': [(1, 1, 1)], 'B': [(1, 1, 1)], 'C': [(1, 1, 1)], 'D': [(1, 1, 1), (2, 1, 1)]}

def rot_mats(reflect=False):
    mats = []
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product([1, -1], repeat=3):
            M = np.zeros((3, 3), dtype=int)
            for i in range(3):
                M[i, perm[i]] = signs[i]
            d = round(np.linalg.det(M))
            if d == 1 or reflect:
                mats.append(M)
    return mats

def norm(cells):
    m = np.min(np.array(list(cells)), axis=0)
    return frozenset(tuple(int(v) for v in np.array(c) - m) for c in cells)

def orients(piece, reflect=False):
    return {norm([tuple(M @ np.array(c)) for c in piece]) for M in rot_mats(reflect)}

def placements(piece, target, reflect=False):
    out = set()
    for o in orients(piece, reflect):
        for t in target:
            for a in o:
                shift = np.array(t) - np.array(a)
                p = frozenset(tuple(int(v) for v in np.array(c) + shift) for c in o)
                if p <= target:
                    out.add(p)
    return list(out)

def covers(piece, target, k, reflect=False):
    if len(piece) * k != len(target):
        return []
    pl = placements(piece, target, reflect)
    sols = []
    def rec(rem, chosen):
        if not rem:
            sols.append(list(chosen)); return
        cell = min(rem)
        for p in pl:
            if cell in p and p <= rem:
                chosen.append(p); rec(rem - p, chosen); chosen.pop()
    rec(frozenset(target), [])
    return sols

def connected(cells):
    cells = set(cells); start = next(iter(cells)); seen = {start}; st = [start]
    while st:
        c = st.pop()
        for d in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]:
            n = (c[0]+d[0], c[1]+d[1], c[2]+d[2])
            if n in cells and n not in seen:
                seen.add(n); st.append(n)
    return len(seen) == len(cells)

if __name__ == '__main__':
    print('组合体21块。')
    for k in 'ABCD':
        for r in range(len(HIDDEN[k]) + 1):
            for extra in itertools.combinations(HIDDEN[k], r):
                piece = VISIBLE[k] | set(extra)
                if not connected(piece):
                    continue
                s = covers(piece, composite, 3)
                s_ref = covers(piece, composite, 3, reflect=True)
                print(f'选项{k} 补看不见的块{list(extra)} 共{len(piece)}块：'
                      f'只旋转拼法数={len(s)}，允许镜像拼法数={len(s_ref)}')
                for sol in s:
                    for p in sol:
                        print('     ', sorted(p))

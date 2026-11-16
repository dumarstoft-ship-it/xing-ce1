# 第49题：立体拼合 —— 精确覆盖搜索
# 对每个选项生成24种空间旋转（不允许镜像），平移后放入题干多面体，要求灰白位置一致；
# 枚举“去掉一个选项、其余三个拼成整体”的所有情形。
import itertools, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from q49_model import SOLID, PIECES

def rotations():
    # 24个行列式为+1的3x3置换矩阵（带符号）
    mats = []
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product((1, -1), repeat=3):
            m = [[0]*3 for _ in range(3)]
            for i in range(3):
                m[i][perm[i]] = signs[i]
            det = (m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1]) - m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])
                   + m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0]))
            if det == 1:
                mats.append(m)
    return mats

ROTS = rotations()
assert len(ROTS) == 24

def orientations(piece):
    seen = set(); out = []
    for m in ROTS:
        cubes = {}
        for (x, y, z), v in piece.items():
            p = tuple(m[i][0]*x + m[i][1]*y + m[i][2]*z for i in range(3))
            cubes[p] = v
        mn = [min(p[i] for p in cubes) for i in range(3)]
        norm = frozenset((tuple(p[i]-mn[i] for i in range(3)), v) for p, v in cubes.items())
        if norm not in seen:
            seen.add(norm); out.append(norm)
    return out

def placements(piece):
    res = []
    for ori in orientations(piece):
        for (sx, sy, sz) in SOLID:
            # 把该朝向的某一块对齐到 SOLID 的某格，枚举所有平移
            for (p, v) in ori:
                off = (sx-p[0], sy-p[1], sz-p[2])
                cells = {}
                ok = True
                for (q, w) in ori:
                    t = (q[0]+off[0], q[1]+off[1], q[2]+off[2])
                    if SOLID.get(t) != w:
                        ok = False; break
                    cells[t] = w
                if ok:
                    res.append(frozenset(cells))
    return list(set(res))

PL = {k: placements(v) for k, v in PIECES.items()}
for k in PIECES:
    g = sum(1 for v in PIECES[k].values() if v == 'G')
    print(f'选项{k}: {len(PIECES[k])}块(灰{g}块)，可放入题干且颜色吻合的位置数 = {len(PL[k])}')
total = len(SOLID)
print('题干共', total, '块，灰色', sum(1 for v in SOLID.values() if v == 'G'), '块')

all_cells = frozenset(SOLID)
for excluded in 'ABCD':
    used = [k for k in 'ABCD' if k != excluded]
    n = sum(len(PIECES[k]) for k in used)
    sols = []
    for a in PL[used[0]]:
        for b in PL[used[1]]:
            if a & b: continue
            for c in PL[used[2]]:
                if (a | b) & c: continue
                if (a | b | c) == all_cells:
                    sols.append((sorted(a), sorted(b), sorted(c)))
    print(f'去掉{excluded}：其余三项共{n}块，拼成题干的方案数 = {len(sols)}')
    for s in sols:
        for k, cells in zip(used, s):
            print(f'    {k}: {cells}')

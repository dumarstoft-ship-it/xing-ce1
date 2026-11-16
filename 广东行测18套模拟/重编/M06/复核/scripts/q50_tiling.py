"""第50题：由正视图、后视图还原的立体（21个小正方体），枚举每个选项（7个小正方体）
能否用3个完全相同的该立体拼成（允许任意旋转；另单独报告允许镜像时的结果）。

坐标 (x, y, z)：x=列(左->右,1..4)，y=层高(1..3)，z=前后(1=前排,2=后排)，均以正视图为准。

由图读出的立体：
  前排 z=1：第1层 c1-c4；第2、3层 c1,c2,c4（c3 第2、3层是缺口）
  后排 z=2：第1、2层 c1-c4；第3层 c1,c2,c3（c4 第3层空）
"""
import itertools

SOLID = set()
for x in range(1, 5):
    SOLID.add((x, 1, 1))
for y in (2, 3):
    for x in (1, 2, 4):
        SOLID.add((x, y, 1))
for y in (1, 2):
    for x in range(1, 5):
        SOLID.add((x, y, 2))
for x in (1, 2, 3):
    SOLID.add((x, 3, 2))
assert len(SOLID) == 21

# 选项（按图读出，含被遮挡但为凑足7块/保持连通所必需的方块，标注于注释）
OPTS = {
    # A：前排底层2块；后排底层2块(被遮挡)、第2层2块、第3层左1块
    'A': {(1, 1, 1), (2, 1, 1), (1, 1, 2), (2, 1, 2), (1, 2, 2), (2, 2, 2), (1, 3, 2)},
    # B：前排左列2层、前排第2列底层；后排第2列底层、第3列2层；(1,1,2)被遮挡
    'B': {(1, 1, 1), (1, 2, 1), (2, 1, 1), (2, 1, 2), (3, 1, 2), (3, 2, 2), (1, 1, 2)},
    # C：前排左列2层；后排左列第2层、(1,1,2)被遮挡；后排第2列3层
    'C': {(1, 1, 1), (1, 2, 1), (1, 2, 2), (1, 1, 2), (2, 1, 2), (2, 2, 2), (2, 3, 2)},
    # D：前排底层2块；后排第2层2块、底层第3列1块；后排底层(1,1,2)(2,1,2)被遮挡
    'D': {(1, 1, 1), (2, 1, 1), (1, 2, 2), (2, 2, 2), (3, 1, 2), (1, 1, 2), (2, 1, 2)},
}
# 只取可见方块（不补被遮挡块）的版本，用来检验"补块"是否影响结论
VISIBLE = {
    'A': {(1, 1, 1), (2, 1, 1), (1, 2, 2), (2, 2, 2), (1, 3, 2)},
    'B': {(1, 1, 1), (1, 2, 1), (2, 1, 1), (2, 1, 2), (3, 1, 2), (3, 2, 2)},
    'C': {(1, 1, 1), (1, 2, 1), (1, 2, 2), (2, 1, 2), (2, 2, 2), (2, 3, 2)},
    'D': {(1, 1, 1), (2, 1, 1), (1, 2, 2), (2, 2, 2), (3, 1, 2), (2, 1, 2)},
}


def norm(s):
    m = [min(p[i] for p in s) for i in range(3)]
    return frozenset(tuple(p[i] - m[i] for i in range(3)) for p in s)


def all_orients(s, mirror=False):
    out = set()
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product([1, -1], repeat=3):
            # 判定行列式
            M = [[0] * 3 for _ in range(3)]
            for i in range(3):
                M[i][perm[i]] = signs[i]
            det = (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1])
                   - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0])
                   + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]))
            if det != 1 and not mirror:
                continue
            t = frozenset(tuple(sum(M[i][j] * p[j] for j in range(3)) for i in range(3)) for p in s)
            out.add(norm(t))
    return out


def placements(piece, target, mirror=False):
    res = set()
    for o in all_orients(piece, mirror):
        anchor = min(o)
        for cell in target:
            d = tuple(cell[i] - anchor[i] for i in range(3))
            pl = frozenset(tuple(p[i] + d[i] for i in range(3)) for p in o)
            if pl <= target:
                res.add(pl)
    return list(res)


def tilings(piece, target, mirror=False):
    pls = placements(piece, target, mirror)
    first = min(target)
    sols = []

    def rec(remaining, chosen):
        if not remaining:
            sols.append(list(chosen)); return
        c = min(remaining)
        for p in pls:
            if c in p and p <= remaining:
                chosen.append(p)
                rec(remaining - p, chosen)
                chosen.pop()
    rec(frozenset(target), [])
    # 去掉排列重复
    uniq = {frozenset(s) for s in sols}
    return uniq, len(pls)


def show(sol):
    lab = {}
    for i, p in enumerate(sorted(sol, key=lambda s: min(s))):
        for c in p:
            lab[c] = 'abc'[i]
    lines = []
    for z in (1, 2):
        lines.append(f'  z={z}（{"前排" if z == 1 else "后排"}）')
        for y in (3, 2, 1):
            lines.append('    ' + ' '.join(lab.get((x, y, z), '.') for x in range(1, 5)))
    return '\n'.join(lines)


if __name__ == '__main__':
    for k in 'ABCD':
        s = OPTS[k]
        sol, npl = tilings(s, SOLID)
        solm, _ = tilings(s, SOLID, mirror=True)
        print(f'选项{k}：{len(s)}块，可放置方式{npl}种，仅旋转可拼成的方案数={len(sol)}，允许镜像时={len(solm)}')
        for t in list(sol)[:2]:
            print(show(t))
    print('\n--- 不补被遮挡方块时的块数（总21块需每块7块）：', {k: len(v) for k, v in VISIBLE.items()})

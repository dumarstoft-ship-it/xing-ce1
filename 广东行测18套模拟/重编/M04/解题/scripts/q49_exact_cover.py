# -*- coding: utf-8 -*-
"""Q49 立体拼合穷举：大多面体 = ① + ② + ③，③ 取各选项，看哪个能恰好拼成。

模型取自 q49_model.py（已渲染比对，与题图一致）。被挡住看不到的位置作为“可有可无”的变体全部枚举。
允许每块任意旋转（24 种）和平移，不允许镜像。
"""
import itertools
from q49_model import BIG, P1, P2_VISIBLE, P2_HIDDEN, OPT


def rotations():
    mats = []
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product((1, -1), repeat=3):
            M = [[0] * 3 for _ in range(3)]
            for i in range(3):
                M[i][perm[i]] = signs[i]
            # 行列式 = +1 才是旋转
            det = (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1]) - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0])
                   + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]))
            if det == 1:
                mats.append(M)
    return mats


ROTS = rotations()
assert len(ROTS) == 24


def norm(cells):
    mx = min(c[0] for c in cells); my = min(c[1] for c in cells); mz = min(c[2] for c in cells)
    return frozenset((x - mx, y - my, z - mz) for x, y, z in cells)


def all_orients(cells):
    out = set()
    for M in ROTS:
        out.add(norm([tuple(sum(M[i][j] * c[j] for j in range(3)) for i in range(3)) for c in cells]))
    return out


def canon(cells):
    return min(tuple(sorted(o)) for o in all_orients(cells))


def placements(shape_orients, region):
    """shape 的所有朝向在 region 内的所有放法"""
    res = []
    for o in shape_orients:
        anchor = min(o)
        for r in region:
            dx, dy, dz = r[0] - anchor[0], r[1] - anchor[1], r[2] - anchor[2]
            placed = frozenset((x + dx, y + dy, z + dz) for x, y, z in o)
            if placed <= region:
                res.append(placed)
    return set(res)


def variants(visible, hidden):
    for k in range(len(hidden) + 1):
        for sub in itertools.combinations(hidden, k):
            yield frozenset(visible | set(sub)), sub


if __name__ == '__main__':
    big = frozenset(BIG)
    p1_vars = list(variants(P1 - {(1, 1, 0)}, [(1, 1, 0)]))
    p2_vars = list(variants(P2_VISIBLE - {(1, 2, 0), (1, 2, 1)}, P2_HIDDEN + [(1, 2, 0), (1, 2, 1)]))
    p2_canon = {}
    for v, sub in p2_vars:
        p2_canon.setdefault(canon(v), []).append(sub)
    print('大多面体方块数', len(big))
    for k in 'ABCD':
        vis, hid = OPT[k]
        found = []
        for ov, osub in variants(vis, hid):
            for po in placements(all_orients(ov), big):
                rest1 = big - po
                for p1v, p1sub in p1_vars:
                    if len(rest1) - len(p1v) < 12:
                        continue
                    for pp in placements(all_orients(p1v), rest1):
                        rest2 = rest1 - pp
                        c = canon(rest2)
                        if c in p2_canon:
                            found.append((len(ov), osub, p1sub, p2_canon[c], sorted(po), sorted(pp), sorted(rest2)))
        print('选项', k, '可拼成的方案数:', len(found))
        seen = set()
        for f in found:
            key = (f[0], f[1], f[2])
            if key in seen:
                continue
            seen.add(key)
            print('   ③取%d块(补被挡位置%s)，①补被挡位置%s，②的被挡位置取%s' % (f[0], list(f[1]), list(f[2]), f[3]))
            print('     ③放在', f[4])
            print('     ①放在', f[5])
            print('     ②为  ', f[6])

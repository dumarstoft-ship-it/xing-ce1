#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""盲解阶段补充：第35题（及第31/34题）更宽的递推搜索。只用题面数字，不读仓库。
1) 整列 4 阶以内线性递推 aₙ = Σcᵢaₙ₋ᵢ + d，cᵢ∈{-2,-1,-1/2,0,1/2,1,2}，d 由首个方程定出，其余全验；
2) 奇数项子列（5项）2 阶线性递推 + 常数；
3) 奇数项差 4,9,25,? 的若干“自然”续法；
4) 奇偶交叉：奇ₖ₊₁ = α·奇ₖ + β·偶ₖ + γ（α,β∈小网格），γ 为常数/等差。"""
import itertools
from fractions import Fraction as F

C = [F(-2), F(-1), F(-1, 2), F(0), F(1, 2), F(1), F(2)]

def fit_linear(S, order):
    hits = []
    N = len(S)
    for cs in itertools.product(C, repeat=order):
        if all(c == 0 for c in cs):
            continue
        d = S[order] - sum(cs[i] * S[order - 1 - i] for i in range(order))
        ok = all(S[n] == sum(cs[i] * S[n - 1 - i] for i in range(order)) + d for n in range(order, N))
        if ok:
            checks = (N - order) - 1
            hits.append((cs, d, checks))
    return hits

def show(title, S_known, options, order_max=4):
    print('=' * 70)
    print(title)
    pos = S_known.index(None)
    for k, v in options.items():
        S = list(S_known); S[pos] = F(v)
        allh = []
        for order in range(1, order_max + 1):
            if len(S) - order - 1 >= 2:
                for cs, d, ch in fit_linear(S, order):
                    allh.append((order, cs, d, ch))
        print(f"  选项{k}={v}: 整列线性递推命中 {len(allh)}")
        for order, cs, d, ch in allh[:10]:
            terms = ' + '.join(f"({c})a[n-{i + 1}]" for i, c in enumerate(cs) if c != 0)
            print(f"     阶{order}: aₙ = {terms} + ({d})   checks={ch}")

show('第35题 整列', [15, 12, 19, 14, 28, 26, 53, 40, None], {'A': 102, 'B': 108, 'C': 112, 'D': 122})
show('第34题 整列', [48, 32, 56, 72, 100, None, 186], {'A': 122, 'B': 130, 'C': 136, 'D': 140}, 3)
show('第31题 整列', [3, 16, 43, 88, 155, None], {'A': 186, 'B': 209, 'C': 248, 'D': 261}, 3)

print('=' * 70)
print('第35题 奇数项子列 15,19,28,53,x：2 阶线性递推 + 常数（网格系数）')
for k, v in {'A': 102, 'B': 108, 'C': 112, 'D': 122}.items():
    S = [F(15), F(19), F(28), F(53), F(v)]
    h = fit_linear(S, 2)
    h1 = fit_linear(S, 1)
    print(f"  选项{k}={v}: 2阶命中 {[(tuple(str(c) for c in cs), str(d), ch) for cs, d, ch in h]}  1阶命中 {[(tuple(str(c) for c in cs), str(d), ch) for cs, d, ch in h1]}")

print('=' * 70)
print('第35题 奇数项差 4,9,25 的几种续法（以及对应第9项）')
cands = {
    '质数平方 2²,3²,5²,7²': 49,
    '斐波那契平方 2²,3²,5²,8²': 64,
    '差前两项和+12 (4+9+12=25)': 9 + 25 + 12,
    '(前两项和)×2−1 ((4+9)×2−1=25)': (9 + 25) * 2 - 1,
    '二阶差等比? 5,16 → ×3.2': None,
}
for lab, d in cands.items():
    if d is None:
        print(f"  {lab}: 不成规律")
    else:
        print(f"  {lab}: 第9项 = 53+{d} = {53 + d}")

print('=' * 70)
print('第35题 奇偶交叉：奇ₖ₊₁ = α·奇ₖ + β·偶ₖ + γₖ（k=1..3 已知，k=4 为所求），γ 常数或等差')
odd = [15, 19, 28, 53]; even = [12, 14, 26, 40]
grid = [F(-1), F(-1, 2), F(0), F(1, 2), F(1), F(3, 2), F(2), F(3)]
for a in grid:
    for b in grid:
        g = [F(odd[k + 1]) - a * odd[k] - b * even[k] for k in range(3)]
        if g[0] == g[1] == g[2]:
            pred = a * 53 + b * 40 + g[0]
            print(f"  α={a} β={b} γ常数{g[0]} → 第9项 {pred}（checks=2）")
        elif g[1] - g[0] == g[2] - g[1]:
            pred = a * 53 + b * 40 + g[2] + (g[2] - g[1])
            print(f"  α={a} β={b} γ等差{[str(x) for x in g]} → 第9项 {pred}（checks=1，弱）")

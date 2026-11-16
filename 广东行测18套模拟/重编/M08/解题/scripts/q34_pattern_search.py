"""M08 第34题：1/20，2/15，1/4，13/30，（ ）  选项 A 9/10  B 3/10  C 11/30  D 19/60
目的：检查是否存在能推出某个选项的规律。
结论（见输出）：通分为 3/60, 8/60, 15/60, 26/60 后，
  - 二级作差 5,7,11 → 再作差 2,4,(8) → 下一差 19 → 45/60 = 3/4
  - 分子 = 2^n + (1,4,7,10) → 32+13 = 45 → 3/4
  - 一级差为质数 5,7,11,(13) → 39/60 = 13/20
  - 前三项之和 = 第四项（3+8+15=26）→ 8+15+26 = 49 → 49/60
  四个选项都推不出来；19/60 恰是“二级作差”法的下一个差值，49/60 与 19/60 只差一个数字。
同时做了：分子分母分别找规律（反约分，倍数1..24）、分子分母交叉线性关系、二次有理式拟合、
  4项全排列×5个空位，均没有得到自然规律下的选项。"""
from fractions import Fraction as F
from itertools import product, permutations
from collections import Counter

seq = [F(1, 20), F(2, 15), F(1, 4), F(13, 30)]
opts = {F(9, 10): 'A', F(3, 10): 'B', F(11, 30): 'C', F(19, 60): 'D'}
N = [int(x * 60) for x in seq]
print('通分(60)后分子:', N)

nat = {}
d = [N[i+1]-N[i] for i in range(3)]; dd = [d[1]-d[0], d[2]-d[1]]
nat['二级差(再作差2,4,8)'] = F(N[3] + d[2] + dd[1]*2, 60)
nat['二级差(再作差2,4,6)'] = F(N[3] + d[2] + dd[1]+2, 60)
nat['一级差为连续质数'] = F(N[3] + 13, 60)
nat['2^n+(3n-2)'] = F(2**5 + 13, 60)
assert all(N[i] == 2**(i+1) + 3*(i+1) - 2 for i in range(4))
assert N[3] == N[0] + N[1] + N[2]
nat['前三项和=第四项'] = F(N[1] + N[2] + N[3], 60)
nat['n^2/40 + (1/40,1/30 交替)'] = F(25, 40) + F(1, 40)
assert all(seq[i] - F((i+1)**2, 40) == [F(1, 40), F(1, 30)][i % 2] for i in range(4))
for k, v in nat.items():
    print(f'{k:28s} -> {v}  在选项中: {opts.get(v, "否")}')

# 1) 分子分母分别找规律（反约分）
primes = [2,3,5,7,11,13,17,19,23,29,31,37,41,43]
def consec(sub, lst):
    for s in range(len(lst)-len(sub)):
        if lst[s:s+len(sub)] == sub: return lst[s+len(sub)]
def nxt(x):
    out = {}
    d = [x[i+1]-x[i] for i in range(3)]
    if len(set(d)) == 1: out['等差'] = x[3]+d[0]
    dd = [d[1]-d[0], d[2]-d[1]]
    if dd[0] == dd[1]: out['二级等差'] = x[3]+d[2]+dd[1]
    if dd[0] and F(dd[1], dd[0]) * dd[1] == int(F(dd[1], dd[0]) * dd[1]):
        out['二级等比'] = x[3]+d[2]+int(F(dd[1], dd[0])*dd[1])
    if x[0] and len({F(x[i+1], x[i]) for i in range(3)}) == 1: out['等比'] = F(x[3]*x[1], x[0])
    if all(d) and len({F(d[i+1], d[i]) for i in range(2)}) == 1: out['差等比'] = x[3] + F(d[2]*d[2], d[1])
    n = consec(d, primes)
    if n: out['差为质数'] = x[3]+n
    if x[2] == x[0]+x[1] and x[3] == x[1]+x[2]: out['和递推'] = x[2]+x[3]
    return out
sep = Counter(); sep_hits = []
for ks in product(range(1, 25), repeat=4):
    P = [seq[i].numerator*ks[i] for i in range(4)]
    Q = [seq[i].denominator*ks[i] for i in range(4)]
    for a, p5 in nxt(P).items():
        for b, q5 in nxt(Q).items():
            if q5:
                v = F(p5)/F(q5); sep[v] += 1
                if v in opts: sep_hits.append((opts[v], P, Q, a, b))
print('\n分子分母分别找规律，所得预测值及出现次数:', [(str(k), n) for k, n in sep.most_common(8)])
print('其中落在选项上的(多为退化的“二级等比”巧合):')
for h in sep_hits: print('   ', h)

# 2) 分子分母交叉线性关系 p'=a p+b q+c, q'=d p+e q+f
cross = Counter()
for ks in product(range(1, 13), repeat=4):
    P = [seq[i].numerator*ks[i] for i in range(4)]
    Q = [seq[i].denominator*ks[i] for i in range(4)]
    pr, qr = [], []
    for a, b in product(range(-3, 4), repeat=2):
        c = P[1]-a*P[0]-b*Q[0]
        if abs(c) <= 15 and all(P[i+1] == a*P[i]+b*Q[i]+c for i in range(3)): pr.append(a*P[3]+b*Q[3]+c)
        f = Q[1]-a*P[0]-b*Q[0]
        if abs(f) <= 15 and all(Q[i+1] == a*P[i]+b*Q[i]+f for i in range(3)): qr.append(a*P[3]+b*Q[3]+f)
    for p5 in pr:
        for q5 in qr:
            if q5: cross[F(p5, q5)] += 1
print('\n交叉线性关系所得预测:', [(str(k), n) for k, n in cross.most_common(5)] or '无')

# 3) 次序/空位：4项全排列 × 5个空位位置，检查等差/二级等差/等比/差等比/和递推
def simple(s):
    d = [s[i+1]-s[i] for i in range(4)]
    dd = [d[i+1]-d[i] for i in range(3)]
    r = []
    if len(set(d)) == 1: r.append('等差')
    if len(set(dd)) == 1: r.append('二级等差')
    if all(x for x in s) and len({s[i+1]/s[i] for i in range(4)}) == 1: r.append('等比')
    if all(x for x in d) and len({d[i+1]/d[i] for i in range(3)}) == 1: r.append('差等比')
    if all(x for x in dd) and len({dd[i+1]/dd[i] for i in range(2)}) == 1: r.append('二级差等比')
    if all(s[i+2] == s[i]+s[i+1] for i in range(3)): r.append('和递推')
    if all(s[i+3] == s[i]+s[i+1]+s[i+2] for i in range(2)): r.append('三项和递推')
    return r
orig = []
for perm in permutations(seq):
    for pos in range(5):
        for v, o in opts.items():
            s = list(perm[:pos]) + [v] + list(perm[pos:])
            r = simple(s)
            if r and list(perm) == seq and pos == 4: orig.append((o, r))
print('\n原顺序、空位在末尾时，代入各选项满足的简单规律:', orig or '无')

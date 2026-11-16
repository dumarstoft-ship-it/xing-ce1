# 第34题：1/20, 2/15, 1/4, 13/30, ( )；枚举常见简单规律，看各自推出什么、能否推出各选项
from fractions import Fraction as F
from itertools import product

seq = [F(1, 20), F(2, 15), F(1, 4), F(13, 30)]
opts = {'A': F(9, 10), 'B': F(3, 10), 'C': F(11, 30), 'D': F(49, 60)}
inv = {v: k for k, v in opts.items()}

def primes_after(n):
    k = n + 1
    while True:
        if k > 1 and all(k % d for d in range(2, int(k ** 0.5) + 1)):
            return k
        k += 1

def rules(s):
    """对长度为4的数列 s（Fraction）给出若干简单规律的下一项；只收录在已知项上成立的规律"""
    out = []
    d = [s[i + 1] - s[i] for i in range(3)]
    dd = [d[i + 1] - d[i] for i in range(2)]
    if d[0] == d[1] == d[2]: out.append(('等差', s[3] + d[2]))
    if 0 not in s and s[1] / s[0] == s[2] / s[1] == s[3] / s[2]: out.append(('等比', s[3] * s[3] / s[2]))
    out.append(('二级等差（差的差2项等差，弱）', s[3] + d[2] + 2 * dd[1] - dd[0]))
    if dd[0] != 0 and dd[1] / dd[0] == dd[1] / dd[0]:
        out.append(('二级等比（差的差2项等比，弱）', s[3] + d[2] + dd[1] * dd[1] / dd[0]))
    if 0 not in d and d[1] / d[0] == d[2] / d[1]: out.append(('差为等比', s[3] + d[2] * d[2] / d[1]))
    if all(x.denominator == 1 for x in d):
        di = [int(x) for x in d]
        if all(primes_after(di[i]) == di[i + 1] for i in range(2)):
            out.append(('差为连续质数', s[3] + primes_after(di[2])))
    if s[2] == s[0] + s[1] and s[3] == s[1] + s[2]: out.append(('前两项和', s[2] + s[3]))
    if s[2] - s[0] - s[1] == s[3] - s[1] - s[2]: out.append(('前两项和+常数', s[2] + s[3] + s[3] - s[1] - s[2]))
    if s[3] == s[0] + s[1] + s[2]: out.append(('前三项和（仅1次验证）', s[1] + s[2] + s[3]))
    if 0 not in s and s[2] == s[0] * s[1] and s[3] == s[1] * s[2]: out.append(('前两项积', s[2] * s[3]))
    # a_{n+1} = k·a_n + c（k、c 为常数，用前两步求出、第三步验证）
    if s[1] != s[0]:
        k = (s[2] - s[1]) / (s[1] - s[0]); c = s[1] - k * s[0]
        if k * s[2] + c == s[3]: out.append((f'a(n+1)={k}·a(n)+{c}', k * s[3] + c))
    # a_{n+1} = 2a_n + c_n，c_n 等差
    c = [s[i + 1] - 2 * s[i] for i in range(3)]
    if c[1] - c[0] == c[2] - c[1]: out.append(('a(n+1)=2a(n)+等差修正', 2 * s[3] + c[2] + c[2] - c[1]))
    # 平方/立方 ± 常数（指数位置可平移）
    for base, sh in product((2, 3), range(-3, 6)):
        cc = [s[i] - (i + 1 + sh) ** base for i in range(4)]
        if cc[0] == cc[1] == cc[2] == cc[3]: out.append((f'(n+{sh})^{base}{cc[0]:+}', (5 + sh) ** base + cc[0]))
        if cc[1] - cc[0] == cc[2] - cc[1] == cc[3] - cc[2]:
            out.append((f'(n+{sh})^{base}+等差', (5 + sh) ** base + cc[3] + cc[3] - cc[2]))
    for b in (2, 3):
        cc = [s[i] - b ** (i + 1) for i in range(4)]
        if cc[1] - cc[0] == cc[2] - cc[1] == cc[3] - cc[2]:
            out.append((f'{b}^n+等差', b ** 5 + cc[3] + cc[3] - cc[2]))
    return out

print('== 一、按分数值本身（含换成 60 分母后的分子 3, 8, 15, 26）')
for name, nxt in rules(seq):
    print(f'  {name}: 下一项 {nxt}（={nxt * 60}/60）', '← 选项' + inv[nxt] if nxt in inv else '')

print('  -- 换成60分母后的分子整数列 3, 8, 15, 26：')
for name, nxt in rules([x * 60 for x in seq]):
    v = nxt / 60
    print(f'  {name}: 下一项分子 {nxt} → {v}', '← 选项' + inv[v] if v in inv else '')
print('== 二、反约分：分子、分母各乘 k（1..12），一列满足较强规律（≥2次验证）、另一列至少有1次验证的规律')
strong = {'等差', '等比', '差为等比', '差为连续质数', '前两项和', '前两项积'}
def strong_rules(s):
    r = [(n, v) for n, v in rules(s) if n in strong or n.startswith('a(n+1)=') or '^' in n]
    return r
hits = {}
for ks in product(range(1, 13), repeat=4):
    P = [F(seq[i].numerator * ks[i]) for i in range(4)]
    Q = [F(seq[i].denominator * ks[i]) for i in range(4)]
    def weak_rules(x):
        return [(n, v) for n, v in rules(x) if '弱' not in n]
    pairs = list(product(strong_rules(P), weak_rules(Q))) + list(product(weak_rules(P), strong_rules(Q)))
    for (n1, p5), (n2, q5) in pairs:
        if q5 != 0 and p5 > 0 and q5 > 0:
            val = p5 / q5
            key = (tuple(int(x) for x in P), tuple(int(x) for x in Q), n1, n2)
            hits[key] = val
for (P, Q, n1, n2), val in sorted(hits.items(), key=lambda kv: (kv[1] not in inv, str(kv[0]))):
    print(f'  分子{P}[{n1}] 分母{Q}[{n2}] → {val}', '← 选项' + inv[val] if val in inv else '')
print('  共', len(hits), '组')

print('== 三、分子分母联动（反约分 k=1..12）：后项分子=前项分母±常数、后项分母=前项分子+分母 等')
link_hits = set()
for ks in product(range(1, 13), repeat=4):
    P = [seq[i].numerator * ks[i] for i in range(4)]
    Q = [seq[i].denominator * ks[i] for i in range(4)]
    # 分子+分母、分母-分子 构成强规律数列
    for lab, A_ in (('分子+分母', [p + q for p, q in zip(P, Q)]), ('分母-分子', [q - p for p, q in zip(P, Q)])):
        for n, v in strong_rules([F(x) for x in A_]):
            # 再配合分子或分母的强规律
            for n2, p5 in strong_rules([F(x) for x in P]):
                q5 = v - p5 if lab == '分子+分母' else v + p5
                if q5 > 0 and p5 > 0:
                    link_hits.add((tuple(P), tuple(Q), lab, n, '分子' + n2, p5 / q5))
    for c in range(-30, 31):
        if all(P[i + 1] == Q[i] + c for i in range(3)):
            link_hits.add((tuple(P), tuple(Q), f'后项分子=前项分母{c:+}', '', '', None))
        if all(Q[i + 1] == P[i] + Q[i] + c for i in range(3)):
            link_hits.add((tuple(P), tuple(Q), f'后项分母=前项分子+分母{c:+}', '', '', None))
        if all(P[i + 1] == P[i] + Q[i] + c for i in range(3)):
            link_hits.add((tuple(P), tuple(Q), f'后项分子=前项分子+分母{c:+}', '', '', None))
for h in sorted(link_hits, key=str):
    print('  ', h, '← 选项' + inv[h[5]] if h[5] in inv else '')
print('  共', len(link_hits), '组')

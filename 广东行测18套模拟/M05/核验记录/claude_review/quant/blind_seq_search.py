#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""盲解阶段：M05 第31-35题（数字推理）规律搜索。
只读同目录 blind_input.json；不读仓库任何文件。
做法：把每个选项代入未知位置，对整列/奇偶子列/分组/整数-小数拆分/分数改写等派生数列
套用一批“简单族”（常数、等差、等比、二级等差、连续平方/立方/质数(+常数)、前两项和、
y=a*y'+b 等），只记录在全列上至少有 2 次“验证”(checks>=2) 的拟合。
对每个选项列出命中的规律，便于判断答案是否唯一、是否存在导向其他选项的规律。"""
import json, re, os, itertools
from fractions import Fraction as F
from collections import defaultdict

WD = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(WD, 'blind_input.json'), encoding='utf-8'))
Q = {d['number']: d for d in data}

def txt(blocks):
    return ''.join(b.get('text', '') for b in blocks if b.get('type') == 'text')

def fmt(x):
    x = F(x)
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"

def parse_num(s):
    s = s.strip()
    m = re.fullmatch(r'\$\\frac\{(\d+)\}\{(\d+)\}\$', s)
    if m:
        return F(int(m.group(1)), int(m.group(2)))
    return F(s)

def parse_stem(t):
    seq = []
    for p in t.split('，'):
        p = p.strip()
        if not p:
            continue
        seq.append(None if '（' in p else parse_num(p))
    return seq

PRIMES = [p for p in range(2, 600) if all(p % d for d in range(2, int(p ** 0.5) + 1))]

def kdiff(y, k):
    for _ in range(k):
        y = [y[i + 1] - y[i] for i in range(len(y) - 1)]
    return y

def eq_all(v):
    return len(v) > 0 and all(a == v[0] for a in v)

def fam_fits(y):
    """返回 [(族名, checks)]，checks = 长度 - 参数个数，仅保留 checks>=2。"""
    L = len(y)
    res = []
    if L < 3:
        return res
    def ok(name, P):
        if L - P >= 2:
            res.append((name, L - P))
    if eq_all(y):
        ok(f"常数{fmt(y[0])}", 1)
    d = kdiff(y, 1)
    if eq_all(d) and d[0] != 0:
        ok(f"等差(公差{fmt(d[0])})", 2)
    if all(v != 0 for v in y[:-1]):
        r = [y[i + 1] / y[i] for i in range(L - 1)]
        if eq_all(r) and r[0] != 1:
            ok(f"等比(公比{fmt(r[0])})", 2)
    dd = kdiff(y, 2)
    if eq_all(dd) and dd[0] != 0:
        ok(f"二级等差(二阶差{fmt(dd[0])})", 3)
    d3 = kdiff(y, 3)
    if L >= 6 and eq_all(d3) and d3[0] != 0:
        ok(f"三级等差(三阶差{fmt(d3[0])})", 4)
    if all(v.denominator == 1 for v in y):
        yi = [int(v) for v in y]
        for pw, nm in ((2, '平方'), (3, '立方')):
            for step in (1, 2):
                for k in range(0, 60):
                    base = [(k + step * i) ** pw for i in range(L)]
                    if yi == base:
                        ok(f"连续{'奇偶数' if step == 2 else ''}{nm}({k}起,步{step})", 1)
                    c = yi[0] - base[0]
                    if c != 0 and all(yi[i] == base[i] + c for i in range(L)):
                        ok(f"连续{nm}({k}起,步{step}){c:+d}", 2)
        for i0 in range(len(PRIMES) - L):
            ps = PRIMES[i0:i0 + L]
            if yi == ps:
                ok(f"连续质数({ps[0]}起)", 1)
            c = yi[0] - ps[0]
            if c != 0 and all(yi[i] == ps[i] + c for i in range(L)):
                ok(f"连续质数({ps[0]}起){c:+d}", 2)
            sq = [p * p for p in ps]
            if yi == sq:
                ok(f"连续质数平方({ps[0]}起)", 1)
            c = yi[0] - sq[0]
            if c != 0 and all(yi[i] == sq[i] + c for i in range(L)):
                ok(f"连续质数平方({ps[0]}起){c:+d}", 2)
        for b in (2, 3):
            for k in range(0, 12):
                base = [b ** (k + i) for i in range(L)]
                c = yi[0] - base[0]
                if all(yi[i] == base[i] + c for i in range(L)):
                    ok(f"{b}的连续幂({b}^{k}起){c:+d}", 2 if c else 1)
    if all(y[i] == y[i - 1] + y[i - 2] for i in range(2, L)):
        ok("前两项之和", 2)
    else:
        c = y[2] - y[1] - y[0]
        if all(y[i] == y[i - 1] + y[i - 2] + c for i in range(2, L)):
            ok(f"前两项之和{fmt(c)}", 3)
    if y[0] != 0 and all(y[i] == y[0] * (-1) ** i for i in range(L)):
        ok(f"正负交替±{fmt(y[0])}", 1)
    if y[0] != y[1] and all(y[i] == y[i - 2] for i in range(2, L)):
        ok("周期2", 2)
    if L >= 5 and y[1] != y[0]:
        a = (y[2] - y[1]) / (y[1] - y[0])
        b = y[1] - a * y[0]
        if a not in (0, 1) and b != 0 and all(y[i] == a * y[i - 1] + b for i in range(1, L)):
            ok(f"y=({fmt(a)})·y'+({fmt(b)})", 3)
    return res

G = [F(-2), F(-1), F(-1, 2), F(0), F(1, 2), F(1), F(3, 2), F(2), F(3)]

def derived_full(S):
    N = len(S)
    out = [('原数列', S)]
    for k in (1, 2, 3):
        dk = kdiff(S, k)
        if len(dk) >= 3:
            out.append((f'{k}阶差', dk))
    if all(v != 0 for v in S[:-1]):
        R = [S[i + 1] / S[i] for i in range(N - 1)]
        out.append(('相邻比(后/前)', R))
        out.append(('相邻比之差', kdiff(R, 1)))
    out.append(('相邻和', [S[i] + S[i + 1] for i in range(N - 1)]))
    out.append(('相邻积', [S[i] * S[i + 1] for i in range(N - 1)]))
    for nm, f in [('n', lambda n: n), ('n²', lambda n: n * n), ('n³', lambda n: n ** 3),
                  ('2ⁿ', lambda n: 2 ** n), ('3ⁿ', lambda n: 3 ** n)]:
        out.append((f'aₙ−{nm}', [S[i] - f(i + 1) for i in range(N)]))
    out.append(('aₙ/n', [S[i] / (i + 1) for i in range(N)]))
    for p in G:
        for q in G:
            if p == 0 and q == 0:
                continue
            r = [S[i] - (p * S[i - 1] + q * S[i - 2]) for i in range(2, N)]
            out.append((f'aₙ−({fmt(p)}aₙ₋₁+{fmt(q)}aₙ₋₂)', r))
    if N >= 6:
        out.append(('aₙ−(aₙ₋₁+aₙ₋₂+aₙ₋₃)', [S[i] - (S[i - 1] + S[i - 2] + S[i - 3]) for i in range(3, N)]))
        out.append(('aₙ−aₙ₋₃', [S[i] - S[i - 3] for i in range(3, N)]))
    out.append(('aₙ−aₙ₋₁·aₙ₋₂', [S[i] - S[i - 1] * S[i - 2] for i in range(2, N)]))
    out.append(('aₙ−aₙ₋₁²', [S[i] - S[i - 1] ** 2 for i in range(1, N)]))
    out.append(('aₙ−(aₙ₋₁−aₙ₋₂)²', [S[i] - (S[i - 1] - S[i - 2]) ** 2 for i in range(2, N)]))
    out.append(('aₙ−(aₙ₋₁+aₙ₋₂)/2', [S[i] - (S[i - 1] + S[i - 2]) / 2 for i in range(2, N)]))
    if all(v != 0 for v in S):
        out.append(('aₙ/(aₙ₋₁+aₙ₋₂)', [S[i] / (S[i - 1] + S[i - 2]) for i in range(2, N)]))
        out.append(('aₙ/(aₙ₋₁·aₙ₋₂)', [S[i] / (S[i - 1] * S[i - 2]) for i in range(2, N)]))
    return out

def derived_sub(S):
    """子列（奇/偶项）只用少量派生，避免过拟合。"""
    N = len(S)
    out = [('子列本身', S)]
    for k in (1, 2):
        dk = kdiff(S, k)
        if len(dk) >= 3:
            out.append((f'子列{k}阶差', dk))
    if all(v != 0 for v in S[:-1]):
        out.append(('子列相邻比', [S[i + 1] / S[i] for i in range(N - 1)]))
    for p in (F(2), F(3), F(1, 2), F(-1), F(-2)):
        out.append((f'子列aₖ−{fmt(p)}aₖ₋₁', [S[i] - p * S[i - 1] for i in range(1, N)]))
    if N >= 4:
        out.append(('子列aₖ−(aₖ₋₁+aₖ₋₂)', [S[i] - S[i - 1] - S[i - 2] for i in range(2, N)]))
    return out

def interleave_cross(S):
    """奇偶两子列之间的交叉关系（第35题这类 9 项交叉数列用）。"""
    o = S[0::2]; e = S[1::2]
    out = []
    m = min(len(o), len(e))
    out.append(('奇k−偶k', [o[k] - e[k] for k in range(m)]))
    out.append(('奇k+偶k', [o[k] + e[k] for k in range(m)]))
    if all(v != 0 for v in e[:m]):
        out.append(('奇k/偶k', [o[k] / e[k] for k in range(m)]))
    out.append(('奇k+1−偶k', [o[k + 1] - e[k] for k in range(len(o) - 1) if k < len(e)]))
    out.append(('奇k+1−奇k−偶k', [o[k + 1] - o[k] - e[k] for k in range(len(o) - 1) if k < len(e)]))
    out.append(('奇k+1−2·偶k', [o[k + 1] - 2 * e[k] for k in range(len(o) - 1) if k < len(e)]))
    out.append(('偶k−奇k+1', [e[k] - o[k + 1] for k in range(len(e)) if k + 1 < len(o)]))
    out.append(('奇k+1−(偶k+偶k−1)', [o[k + 1] - e[k] - e[k - 1] for k in range(1, len(o) - 1) if k < len(e)]))
    return out

def groups(S):
    out = []
    N = len(S)
    if N % 2 == 0:
        P = [(S[i], S[i + 1]) for i in range(0, N, 2)]
        out.append(('两两分组:和', [a + b for a, b in P]))
        out.append(('两两分组:差', [a - b for a, b in P]))
        out.append(('两两分组:积', [a * b for a, b in P]))
        if all(b != 0 for a, b in P):
            out.append(('两两分组:商', [a / b for a, b in P]))
    if N % 3 == 0:
        T = [S[i:i + 3] for i in range(0, N, 3)]
        out.append(('三三分组:和', [sum(t) for t in T]))
        out.append(('三三分组:c−(a+b)', [t[2] - t[0] - t[1] for t in T]))
        out.append(('三三分组:(a+b)−c', [t[0] + t[1] - t[2] for t in T]))
        out.append(('三三分组:c−(a−b)', [t[2] - (t[0] - t[1]) for t in T]))
        out.append(('三三分组:c−a·b', [t[2] - t[0] * t[1] for t in T]))
        if all(t[0] + t[1] != 0 for t in T):
            out.append(('三三分组:c/(a+b)', [t[2] / (t[0] + t[1]) for t in T]))
    return out

def analyze(S, cross=False):
    hits = []
    for lab, y in derived_full(S):
        for fam, ch in fam_fits(y):
            hits.append(('整列', lab, fam, ch))
    for sub_name, sub in (('奇数项', S[0::2]), ('偶数项', S[1::2])):
        if len(sub) >= 3:
            for lab, y in derived_sub(sub):
                for fam, ch in fam_fits(y):
                    hits.append((sub_name, lab, fam, ch))
    if cross:
        for lab, y in interleave_cross(S):
            for fam, ch in fam_fits(y):
                hits.append(('奇偶交叉', lab, fam, ch))
    for lab, y in groups(S):
        for fam, ch in fam_fits(y):
            hits.append(('分组', lab, fam, ch))
    return hits

def report(num, S_known, options, cross=False, extra=None):
    print('=' * 78)
    print(f"第{num}题  题面: {txt(Q[num]['stem'])}")
    print('选项: ' + '  '.join(f"{k}={v}" for k, v in options.items()))
    pos = S_known.index(None)
    summary = {}
    for key, otext in options.items():
        v = parse_num(otext)
        S = list(S_known)
        S[pos] = v
        hits = analyze(S, cross=cross)
        if extra:
            hits += extra(S)
        # 去重：同一 (范围, 派生, 族) 只留一次
        seen = set(); uniq = []
        for h in hits:
            if h[:3] not in seen:
                seen.add(h[:3]); uniq.append(h)
        uniq.sort(key=lambda h: -h[3])
        summary[key] = uniq
        print(f"\n  选项{key} = {otext}：命中 {len(uniq)} 条（checks>=2）")
        for h in uniq[:40]:
            print(f"    [{h[0]}] {h[1]} → {h[2]}  (checks={h[3]})")
        if len(uniq) > 40:
            print(f"    ……另有 {len(uniq) - 40} 条")
    return summary

# ---------- 第32题：整数部分/小数部分拆分 ----------
def split_dec(otext_list):
    I, D = [], []
    for s in otext_list:
        a, b = s.split('.')
        I.append(F(int(a))); D.append(F(int(b)))
    return I, D

def q32_extra_factory(strings_known):
    def extra(S):
        # S 是 Fraction 序列；需要原始字符串才能拆分小数部分，这里由闭包提供
        return []
    return extra

def q32_split_analysis():
    num = 32
    stem = txt(Q[num]['stem'])
    raw = [p.strip() for p in stem.split('，')]
    opts = {k: txt(v) for k, v in Q[num]['options'].items()}
    print('\n' + '-' * 78)
    print('第32题 整数部分/小数部分（按小数点后数字串当整数）拆分分析')
    for key, ot in opts.items():
        strs = [r for r in raw if '（' not in r] + [ot]
        I, D = split_dec(strs)
        hitsI = []
        for sub_name, sub in (('整数部分整列', I), ('整数部分奇项', I[0::2]), ('整数部分偶项', I[1::2])):
            for lab, y in (derived_full(sub) if len(sub) >= 5 else derived_sub(sub)):
                for fam, ch in fam_fits(y):
                    hitsI.append((sub_name, lab, fam, ch))
        hitsD = []
        for sub_name, sub in (('小数部分整列', D), ('小数部分奇项', D[0::2]), ('小数部分偶项', D[1::2])):
            for lab, y in (derived_full(sub) if len(sub) >= 5 else derived_sub(sub)):
                for fam, ch in fam_fits(y):
                    hitsD.append((sub_name, lab, fam, ch))
        cross = []
        rel = {
            '整数ₙ₊₁−(整数ₙ+小数ₙ)': [I[i + 1] - I[i] - D[i] for i in range(len(I) - 1)],
            '小数ₙ₊₁−(整数ₙ−小数ₙ)': [D[i + 1] - (I[i] - D[i]) for i in range(len(I) - 1)],
            '整数ₙ−小数ₙ': [I[i] - D[i] for i in range(len(I))],
            '整数ₙ+小数ₙ': [I[i] + D[i] for i in range(len(I))],
        }
        for lab, y in rel.items():
            for fam, ch in fam_fits(y):
                cross.append(('整数×小数交叉', lab, fam, ch))
        print(f"\n  选项{key} = {ot}: 整数部分 {[int(x) for x in I]}  小数部分 {[int(x) for x in D]}")
        for h in sorted(hitsI, key=lambda h: -h[3])[:12]:
            print(f"    [{h[0]}] {h[1]} → {h[2]} (checks={h[3]})")
        for h in sorted(hitsD, key=lambda h: -h[3])[:12]:
            print(f"    [{h[0]}] {h[1]} → {h[2]} (checks={h[3]})")
        for h in cross:
            print(f"    [{h[0]}] {h[1]} → {h[2]} (checks={h[3]})")
        if not (hitsI or hitsD or cross):
            print('    （无命中）')

# ---------- 第33题：分数改写搜索 ----------
def predict_next(x):
    """已知 x（整数列表，长度 m），返回 [(族, 预测下一项, 已知部分 checks)]，checks>=1。"""
    m = len(x); out = []
    d = kdiff(x, 1); dd = kdiff(x, 2); d3 = kdiff(x, 3)
    if eq_all(d) and m - 2 >= 1:
        out.append(('等差', x[-1] + d[0], m - 2))
    if eq_all(dd) and dd[0] != 0 and m - 3 >= 1:
        out.append(('二级等差', x[-1] + d[-1] + dd[0], m - 3))
    if eq_all(d3) and d3[0] != 0 and m - 4 >= 1:
        out.append(('三级等差', x[-1] + d[-1] + dd[-1] + d3[0], m - 4))
    if all(v != 0 for v in x[:-1]):
        r = [F(x[i + 1], x[i]) for i in range(m - 1)]
        if eq_all(r) and r[0] != 1 and m - 2 >= 1:
            out.append(('等比', x[-1] * r[0], m - 2))
    # 差为连续质数
    for i0 in range(len(PRIMES) - len(d)):
        if d == PRIMES[i0:i0 + len(d)]:
            out.append(('差为连续质数', x[-1] + PRIMES[i0 + len(d)], len(d) - 1))
    # 差为连续平方/立方
    for pw in (2, 3):
        for k in range(0, 40):
            if d == [(k + i) ** pw for i in range(len(d))]:
                out.append((f'差为连续{pw}次方', x[-1] + (k + len(d)) ** pw, len(d) - 1))
    # 差为前两项和（斐波那契式）
    if len(d) >= 3 and all(d[i] == d[i - 1] + d[i - 2] for i in range(2, len(d))):
        out.append(('差为前两项和', x[-1] + d[-1] + d[-2], len(d) - 2))
    # 自身为前两项和(+c)
    if m >= 4:
        c = x[2] - x[1] - x[0]
        if all(x[i] == x[i - 1] + x[i - 2] + c for i in range(2, m)):
            out.append((f'前两项和{c:+d}', x[-1] + x[-2] + c, m - 3))
    # 差等比
    if len(d) >= 3 and all(v != 0 for v in d[:-1]):
        r = [F(d[i + 1], d[i]) for i in range(len(d) - 1)]
        if eq_all(r) and r[0] != 1:
            nx = x[-1] + d[-1] * r[0]
            if nx.denominator == 1:
                out.append(('差等比', int(nx), len(d) - 2))
    return [o for o in out if o[2] >= 1]

def q33_rewrite_search():
    num = 33
    stem = txt(Q[num]['stem'])
    S = parse_stem(stem)
    known = [s for s in S if s is not None]
    opts = {k: parse_num(txt(v)) for k, v in Q[num]['options'].items()}
    inv = {v: k for k, v in opts.items()}
    print('\n' + '-' * 78)
    print('第33题 分数改写（分子分母同乘 k）搜索：已知5项各乘 k∈1..6，看分子列、分母列各自的规律能否预测出某个选项')
    tally = defaultdict(list)
    for ks in itertools.product(range(1, 7), repeat=len(known)):
        nums = [s.numerator * k for s, k in zip(known, ks)]
        dens = [s.denominator * k for s, k in zip(known, ks)]
        pn = predict_next(nums); pd = predict_next(dens)
        for fn, vn, cn in pn:
            for fd, vd, cd in pd:
                if vd == 0:
                    continue
                val = F(vn, vd)
                if val in inv:
                    tally[inv[val]].append((cn + cd, ks, nums, dens, fn, vn, fd, vd))
    for key in sorted(opts):
        lst = sorted(tally[key], key=lambda t: -t[0])
        print(f"\n  选项{key} = {fmt(opts[key])}: 改写方案命中 {len(lst)} 个")
        for t in lst[:8]:
            print(f"    总checks={t[0]} 乘数{t[1]} 分子{t[2]}→[{t[4]}]{t[5]}  分母{t[3]}→[{t[6]}]{t[7]}")
    # 同时：分子+分母、分母−分子 等
    print('\n  附：最小项改写 2/15,4/18,7/22,12/27,19/33 的分子差、分母差：')
    nums = [2, 4, 7, 12, 19]; dens = [15, 18, 22, 27, 33]
    print('    分子', nums, '差', kdiff(nums, 1), ' 分母', dens, '差', kdiff(dens, 1))

def main():
    # 31
    for num in (31, 32, 33, 34, 35):
        S = parse_stem(txt(Q[num]['stem']))
        opts = {k: txt(v) for k, v in Q[num]['options'].items()}
        report(num, S, opts, cross=(num == 35))
        if num == 32:
            q32_split_analysis()
        if num == 33:
            q33_rewrite_search()
    # 第31题：三阶差分构造的通项
    print('\n' + '=' * 78)
    print('第31题通项核对：aₙ = (2/3)(n−1)n(n+1) + 3n²')
    print([F(2, 3) * (n - 1) * n * (n + 1) + 3 * n * n for n in range(1, 8)])
    # 第34题：aₙ = aₙ₋₁ + aₙ₋₂/2
    print('第34题核对：aₙ = aₙ₋₁ + aₙ₋₂/2')
    a = [F(48), F(32)]
    for _ in range(5):
        a.append(a[-1] + a[-2] / 2)
    print([fmt(v) for v in a])
    # 第35题：奇数项差为连续质数平方，偶数项前两项之和
    print('第35题核对：奇数项 15,19,28,53 的差', kdiff([15, 19, 28, 53], 1), '; 偶数项 12,14,26,40 的差', kdiff([12, 14, 26, 40], 1))
    for nx in (102, 108, 112, 122):
        print(f'   代入{nx}：奇数项差 {kdiff([15, 19, 28, 53, nx], 1)}')

if __name__ == '__main__':
    main()

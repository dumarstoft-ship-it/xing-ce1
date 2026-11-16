# 第32题：26，61，102，151，209，277，（ ）  选项 A357 B359 C361 D363
seq = [26, 61, 102, 151, 209, 277]
d1 = [b - a for a, b in zip(seq, seq[1:])]
d2 = [b - a for a, b in zip(d1, d1[1:])]
print("一级差:", d1)   # 35 41 49 58 68
print("二级差:", d2)   # 6 8 9 10
composites = [n for n in range(4, 30) if any(n % p == 0 for p in range(2, n))]
print("合数列:", composites[:8])
i = composites.index(d2[0])
assert composites[i:i + 4] == d2, "二级差应为连续合数"
nxt_d2 = composites[i + 4]          # 12
ans = seq[-1] + d1[-1] + nxt_d2     # 277+68+12
print("下一个二级差", nxt_d2, "→ 一级差", d1[-1] + nxt_d2, "→ 答案", ans)
opts = {"A": 357, "B": 359, "C": 361, "D": 363}
print([k for k, v in opts.items() if v == ans])
# 错误思路：二级差看成“+1递增”（6,8,9,10,11）→ 356，不在选项中；看成偶数列/每次+2→ 70 / 82 等
for wrong in (11, 14, 16, 18):
    print("若二级差为", wrong, "→", seq[-1] + d1[-1] + wrong)

"""M05 第35题：1/35，3/70，1/14，1/10，11/70，（ ）

思路：分母统一为70：2/70，3/70，5/70，7/70，11/70，分子 2,3,5,7,11 是连续质数，
下一项分子为13，所求项 13/70。
"""
from fractions import Fraction as F

terms = [F(1, 35), F(3, 70), F(1, 14), F(1, 10), F(11, 70)]
options = {"A": F(1), "B": F(3, 4), "C": F(13, 70), "D": F(37, 70)}

nums = [t * 70 for t in terms]
assert all(n.denominator == 1 for n in nums)
nums = [int(n) for n in nums]
print("通分到70后的分子:", nums)


def primes(k):
    out, n = [], 2
    while len(out) < k:
        if all(n % p for p in out):
            out.append(n)
        n += 1
    return out


assert nums == primes(5)
nxt = primes(6)[-1]
print("下一个质数:", nxt)

hits = []
for k, v in options.items():
    ok = v == F(nxt, 70)
    print(f"{k} {v}: 分子(分母70) {v * 70} -> {'符合' if ok else '不符'}")
    if ok:
        hits.append(k)
assert hits == ["C"], hits

# 排查：分子作差 1,2,2,4 若按"×2交替"续写得 11+4=15，15/70=3/14 不在选项中
print("分子一级差:", [b - a for a, b in zip(nums, nums[1:])], "（其他续写方式得到的值均不在选项中）")
print("答案: C 13/70")

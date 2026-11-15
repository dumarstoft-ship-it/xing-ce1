#!/usr/bin/env python3
"""M04 第31-45题 盲解复核脚本（只依据考生可见题面）。
精确算术（fractions.Fraction）+ 穷举。可独立重跑：python3 blind_check.py
"""
from fractions import Fraction as F
from itertools import permutations, combinations, product
from math import comb, factorial

out = []
def say(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    out.append(s)

def diffs(xs):
    return [b - a for a, b in zip(xs, xs[1:])]

# ---------------- Q31 ----------------
say("== Q31  14,39,65,94,132,197,( )  A343 B313 C278 D211")
s = [14, 39, 65, 94, 132, 197]
d1 = diffs(s); d2 = diffs(d1)
say("  一次差", d1, " 二次差", d2, " 二次差公比", [F(b, a) for a, b in zip(d2, d2[1:])])
nxt = s[-1] + d1[-1] + d2[-1] * 3
say("  二次差×3 -> 下一项", nxt)
for k, v in dict(A=343, B=313, C=278, D=211).items():
    e = s + [v]
    say(f"  {k}={v}: 一次差 {diffs(e)} 二次差 {diffs(diffs(e))}")

# ---------------- Q32 ----------------
say("== Q32  5/12,43/96,1/2,55/96,2/3,( )  A29/32 B25/32 C11/16 D11/12")
s = [F(5, 12), F(43, 96), F(1, 2), F(55, 96), F(2, 3)]
num96 = [x * 96 for x in s]
say("  通分到96的分子", [int(x) for x in num96], " 一次差", [int(x) for x in diffs(num96)])
for k, v in dict(A=F(29, 32), B=F(25, 32), C=F(11, 16), D=F(11, 12)).items():
    e = num96 + [v * 96]
    say(f"  {k}={v}: 分子(96) {[str(x) for x in e]} 一次差 {[str(x) for x in diffs(e)]} 二次差 {[str(x) for x in diffs(diffs(e))]}")
say("  奇数项 5/12,1/2,2/3 =", [str(x * 12) + '/12' for x in s[0::2]], "（下一奇数项在第7位，不是第6位）")
say("  偶数项 43/96,55/96 -> 等差下一项", F(67, 96))

# ---------------- Q33 ----------------
say("== Q33  2.04,5.12,11.36,20.108,( )  A32.324 B32.216 C47.324 D47.216")
ip = [2, 5, 11, 20]; dp = [4, 12, 36, 108]
say("  整数部分", ip, "一次差", diffs(ip), "二次差", diffs(diffs(ip)), "-> 下一整数", ip[-1] + diffs(ip)[-1] + 3)
say("  小数部分", dp, "比", [F(b, a) for a, b in zip(dp, dp[1:])], "-> 下一小数", dp[-1] * 3)

# ---------------- Q34 ----------------
say("== Q34  26,12,25,31,43.5,( )  A53 B56.5 C59 D62.5")
s = [F(26), F(12), F(25), F(31), F(87, 2)]
for i in range(2, 5):
    say(f"  a{i+1} = a{i-1}/2 + a{i} ? {s[i-2]/2 + s[i-1]} vs {s[i]}")
say("  下一项 =", float(s[3] / 2 + s[4]))

# ---------------- Q35 ----------------
say("== Q35  16,4,36,64,196,( )  A441 B484 C576 D625")
r = [4, 2, 6, 8, 14]
say("  平方根", r, " 递推 r(n)=r(n-1)+r(n-2):", [r[i-2] + r[i-1] == r[i] for i in range(2, 5)], " 下一根", r[-2] + r[-1], "->", (r[-2] + r[-1]) ** 2)
for k, v in dict(A=441, B=484, C=576, D=625).items():
    say(f"  {k}={v} = {int(round(v ** 0.5))}^2")

# ---------------- Q36 ----------------
say("== Q36  男女6:1，总数<=100，外省1/8，外省男女4:3")
sols = []
for N in range(1, 101):
    if N % 7 or N % 8:
        continue
    out_n = N // 8
    if out_n % 7:
        continue
    boys, girls = N * 6 // 7, N // 7
    ob, og = out_n * 4 // 7, out_n * 3 // 7
    local_girls = girls - og
    sols.append((N, boys, girls, out_n, ob, og, local_girls, local_girls - ob))
for t in sols:
    say("  N=%d 男%d 女%d 外省%d(男%d女%d) 本省女%d 差=%d" % t)

# ---------------- Q37 ----------------
say("== Q37  利润率25%，成本+15%，售价×1.5×0.8")
c0, p0 = F(100), F(125)
c1, p1 = c0 * F(115, 100), p0 * F(3, 2) * F(4, 5)
r0, r1 = (p0 - c0) / c0, (p1 - c1) / c1
say(f"  按成本计: 原 {float(r0):.4%} 新 {float(r1):.4%}（={r1}） 变化 {float((r1 - r0) * 100):.4f} 个百分点 -> 高5个百分点以上(A)")
q0, q1 = (p0 - c0) / p0, (p1 - c1) / p1
say(f"  若按售价计(非公考惯例): 原 {float(q0):.4%} 新 {float(q1):.4%} 变化 {float((q1 - q0) * 100):.4f} 个百分点 -> 将落到B")

# ---------------- Q38 ----------------
say("== Q38  直角三角形一圈40个等距传感器，24米直角边9个")
for label, gaps in (("9个含两端顶点", 8), ("9个不含两端(内部9个)", 10)):
    step = F(24, gaps)
    P = 40 * step
    # b + c = P - 24, c^2 - b^2 = 576
    s_bc = P - 24
    c_minus_b = F(576) / s_bc
    c = (s_bc + c_minus_b) / 2; b = (s_bc - c_minus_b) / 2
    ok = (b / step).denominator == 1 and (c / step).denominator == 1
    say(f"  {label}: 间距 {step} 周长 {P} 另一直角边 {b} 斜边 {c} 顶点落在传感器位置? {ok} 段数 {gaps},{b/step},{c/step}")

# ---------------- Q39 ----------------
say("== Q39  相遇问题")
# D = 4(v+60); v*1 + 1.2v*1.5 + 60*5 = D
# 2.8v + 300 = 4v + 240
v = F(60) / F(12, 10)
D = 4 * (v + 60)
pos_meet = v * 1 + F(12, 10) * v * F(3, 2)
remain = D - pos_meet
t_total = 5 + remain / (F(12, 10) * v)
say(f"  v甲={v} 全程={D} 相遇时甲行{pos_meet} 剩{remain} 用时{remain/(F(12,10)*v)} 甲到B共{t_total}小时")
# 独立核：逐段模拟
t, x = F(0), F(0)
x += v * 1; t += 1          # 1h
t += F(5, 2)                # 维修
x_rest = D - x
t += x_rest / (F(6, 5) * v)
say(f"  逐段：{t} 小时（选项D=10）")

# ---------------- Q40 ----------------
say("== Q40  螺丝钉/螺帽分配")
N = F(20) / (F(1, 30) - F(1, 40))
say(f"  批量 N = {N}")
# 连续LP：最小T s.t. 存在 a,b in [0,T]: 40a+30b>=N, 50(T-a)+60(T-b)>=N
def feasible(T, integer_hours=False):
    if integer_hours:
        for a in range(0, int(T) + 1):
            for b in range(0, int(T) + 1):
                if 40 * a + 30 * b >= N and 50 * (T - a) + 60 * (T - b) >= N:
                    return (a, b)
        return None
    # 连续：给定a，b取满足钉子的最小值，再看帽子
    best = None
    # 极点在 a in {0,T} 或 b in {0,T} 或两约束同时紧；用细粒度+精确极点
    cands = set()
    for a in (F(0), F(T)):
        cands.add(a)
    # 两约束同时紧：40a+30b=N, 50a+60b=110T-N
    det = F(40 * 60 - 30 * 50)
    a_t = (N * 60 - 30 * (110 * T - N)) / det
    if 0 <= a_t <= T:
        cands.add(a_t)
    for a in cands:
        b = max(F(0), (N - 40 * a) / 30)
        if b <= T and 50 * (T - a) + 60 * (T - b) >= N:
            return (a, b)
    return None
lo = None
# 精确下界：A全做钉子，B先做帽子
T_star = (N + 30 * 40) / 70  # 40T + 30(T-40) = N
say(f"  LP 下界 T* = {T_star} ≈ {float(T_star):.4f}")
for T in (51, 52, 53, 54):
    say(f"  T={T}: 连续可行 {feasible(F(T))}；整小时分配可行 {feasible(T, True)}")
# 暴力精细网格交叉验证（步长1/60小时）
best = None
for T60 in range(50 * 60, 53 * 60):
    T = F(T60, 60)
    ok = False
    for a60 in range(0, T60 + 1, 1):
        a = F(a60, 60)
        bneed = max(F(0), (N - 40 * a) / 30)
        if bneed <= T and 50 * (T - a) + 60 * (T - bneed) >= N:
            ok = True
            break
    if ok:
        best = T
        break
say(f"  1/60小时网格上最早可行 T = {best} ≈ {float(best):.4f}，向上取整 = 52")

# ---------------- Q41 ----------------
say("== Q41  外卖优惠上界")
# 实付 = 0.6P - 3*(折后满25单数) - 4*(红包张数)，满25单数=4，红包<=5
for k in range(0, 7):
    P = (F(148) + 12 + 4 * k) / F(3, 5)
    say(f"  用红包 {k} 张 -> 原价合计 {P}" + ("（超过5天上限，不可行）" if k > 5 else ""))
# 可行构造
orders = [40, 40, 55, 55, 55, 55]
disc = [F(3, 5) * o for o in orders]
pay = sum(disc) - 3 * sum(1 for d in disc if d >= 25) - 4 * 5
say(f"  构造: 原价 {orders} 折后 {[str(d) for d in disc]} 实付 {pay} 原价合计 {sum(orders)}")

# ---------------- Q42 ----------------
say("== Q42  四集合交集下界")
sat = [F(95, 100) * 400, F(3, 5) * 400, F(95, 100) * 400 - 4, F(23, 25) * 400]
uns = [400 - x for x in sat]
say(f"  满意 {[int(x) for x in sat]} 不满意 {[int(x) for x in uns]} 不满意之和 {int(sum(uns))} 最少全满意 {int(400 - sum(uns))}")
# 构造：不满意者两两不交
hh = []
idx = 0
for j, u in enumerate(uns):
    for _ in range(int(u)):
        hh.append(j); idx += 1
all_sat = 400 - len(hh)
say(f"  构造（不满意者互不重叠）后全满意户数 = {all_sat}，各项满意数核对 {[400 - hh.count(j) for j in range(4)]}")

# ---------------- Q43 ----------------
say("== Q43  概率")
men = ["M1", "M2", "M3", "M4", "M5"]; women = ["W1", "W2", "W3", "W4"]
couples = {("M1", "W1"), ("M2", "W2")}
tot = cnt1 = cnt2 = cnt_any = 0
for ms in combinations(men, 2):
    for ws in combinations(women, 2):
        tot += 1
        k = sum(1 for m in ms for w in ws if (m, w) in couples)
        cnt1 += (k == 1); cnt2 += (k == 2); cnt_any += (k >= 1)
say(f"  总数 {tot} 恰1对 {cnt1} 2对 {cnt2} 至少1对 {cnt_any} -> P(恰1对) = {F(cnt1, tot)}")
say(f"  典型错法：2×C(4,1)×C(3,1)=24 -> {F(24, 60)}（未扣两对同时入选）；至少1对 {F(cnt_any, tot)}")
for k, v in dict(A=F(9, 20), B=F(2, 5), C=F(13, 30), D=F(11, 30)).items():
    say(f"  {k}={v} = {v * 60}/60")

# ---------------- Q44 ----------------
say("== Q44  两侧垃圾桶")
L = set(range(0, 1486, 15)); R = set(range(0, 1486, 33))
both = sorted(L & R)
mid_both = [x for x in both if 0 < x < 1485]
say(f"  左 {len(L)} 右 {len(R)} 两侧重合位置 {both}（中间 {len(mid_both)} 个）")
say(f"  只合并中间重合: {len(L) + len(R) - len(mid_both)}；连两端也合并: {len(L) + len(R) - len(both)}；不合并: {len(L) + len(R)}")

# ---------------- Q45 ----------------
say("== Q45  排队穷举 8! 种")
people = ["甲", "乙", "丙", "丁", "e", "f", "g", "h"]
cnt = 0
for p in permutations(people):
    pos = {x: i for i, x in enumerate(p)}
    a, b = pos["甲"], pos["乙"]
    if a in (0, 7) or b in (0, 7):
        continue
    if abs(a - b) != 1:
        continue
    bad = False
    for x in ("丙", "丁"):
        for y in ("甲", "乙"):
            if abs(pos[x] - pos[y]) == 1:
                bad = True
    if bad:
        continue
    cnt += 1
say(f"  满足条件的排列数 = {cnt}；公式 5×2×A(4,2)×4! = {5 * 2 * 4 * 3 * factorial(4)}")

with open(__file__.replace("blind_check.py", "blind_check_output.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")

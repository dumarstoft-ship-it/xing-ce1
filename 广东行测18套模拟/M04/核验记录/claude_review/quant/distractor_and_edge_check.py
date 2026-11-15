#!/usr/bin/env python3
"""M04 第36-45题：错误选项来源（典型错法）、题面边界与解析构造的复核。
比对阶段脚本（已看过编辑答案后编写），只做验证，不改仓库。可独立重跑：
    python3 distractor_and_edge_check.py
"""
from fractions import Fraction as F
from itertools import permutations, combinations
from math import factorial, comb

out = []
def say(*a):
    s = " ".join(str(x) for x in a)
    print(s); out.append(s)

# ---------- Q36 ----------
say("== Q36 选项来源")
N = 56; girls = 8; boys = 48; o = 7; ob = 4; og = 3
say(f"  正解 本省女{girls-og}-外省男{ob}={girls-og-ob}(A)；外省女{og}(B=3)；本省女{girls-og}(C=5)；全班女{girls}(D=8)")

# ---------- Q37 ----------
say("== Q37 口径与错法")
c0, p0, c1 = F(100), F(125), F(115)
p1 = p0 * F(3, 2) * F(4, 5)
say(f"  成本口径 {float((p1-c1)/c1*100):.2f}% vs 25% -> +{float(((p1-c1)/c1 - F(1,4))*100):.2f}pp (A)")
say(f"  售价口径 {float((p1-c1)/p1*100):.2f}% vs {float((p0-c0)/p0*100):.2f}% -> +{float(((p1-c1)/p1-(p0-c0)/p0)*100):.2f}pp (会选B)")
say(f"  错把新利润除以旧成本100：{float((p1-c1)/c0*100):.0f}% -> +10pp，仍落A（解析中“不能仍除以100”的提醒不改变选项）")
say(f"  粗估35/115≈30% -> 恰+5pp，落在A/B分界，需精算：35/115={float(F(35,115)):.4f}")

# ---------- Q38 ----------
say("== Q38 不同点数-段数口径")
for label, seg24, segloop in (("正解：9点含端点->8段，闭环40点->40段", 8, 40),
                              ("误把24米边当9段", 9, 40),
                              ("误把闭环当39段", 8, 39),
                              ("误把闭环当41段", 8, 41)):
    step = F(24, seg24); P = step * segloop; s = P - 24; d = F(576) / s
    c = (s + d) / 2; b = (s - d) / 2
    say(f"  {label}: 间距{step} 周长{P} 斜边{float(c):.3f} 另一直角边{float(b):.3f} 顶点落点 {(b/step).denominator==1 and (c/step).denominator==1}")

# ---------- Q39 ----------
say("== Q39 选项来源")
v = F(50); D = 440
say(f"  正解 1+2.5+(440-50)/60 = {1 + F(5,2) + F(D - 50, 60)} (D)")
say(f"  只算相遇后：(440-140)/60 = {F(300,60)} (A=5)")
say(f"  漏掉维修2.5小时：{1 + F(D-50,60)} (B=7.5)；重复计入维修：{1 + F(5,2)*2 + F(D-50,60)} (C=12.5)")
say(f"  修后仍按原速50：{1 + F(5,2) + F(D-50,50)}（不在选项）")

# ---------- Q40 ----------
say("== Q40 下界、可实现性与错法")
Nn = 2400
T_lp = F(Nn + 30 * 40, 70)
say(f"  LP下界 {T_lp}={float(T_lp):.4f}；加权对偶界：钉权2帽权1，总量{2*Nn+Nn}，A≤80/h，B≤60/h -> {F(3*Nn,140)}")
say(f"  51小时最多钉数（B先满帽40h）：40*51+30*11={40*51+30*11} < 2400 -> 不可行；52小时：{40*52+30*12} ≥ 2400 -> 可行")
say(f"  不切换（A全钉、B全帽）：max(2400/40, 2400/60) = {max(F(Nn,40),F(Nn,60))}；各自成套生产：{float(Nn/(1/(F(1,40)+F(1,50))+1/(F(1,30)+F(1,60)))):.2f}")
say(f"  51(A)=只取整到下界整数部分的典型错；53/54无对应错法（邻近数）")

# ---------- Q41 ----------
say("== Q41 上界、错法与构造合法性")
for k in range(0, 7):
    P = (F(148) + 12 + 4 * k) / F(3, 5)
    say(f"  红包{k}张 -> 原价合计 {P} ≈ {float(P):.2f}")
say(f"  漏掉满减：(148+20)/0.6 = {F(168)/F(3,5)} (C=280)；只算到折后价：148+12+20 = 180 (A=180)")
def witness(disc):
    orig = [F(d) / F(3, 5) for d in disc]
    pay = sum(F(d) for d in disc) - 3 * sum(1 for d in disc if d >= 25) - 4 * 5
    ok_fen = all((x * 100).denominator == 1 for x in orig)
    return orig, pay, ok_fen
for name, disc in (("编辑解析构造", [20, 20, 35, 35, 35, 35]),
                   ("内部第二读者构造", [18, 18, 36, 36, 36, 36]),
                   ("建议构造", [24, 24, 33, 33, 33, 33])):
    orig, pay, ok = witness(disc)
    say(f"  {name}: 折后{disc} 原价{[str(x) if x.denominator!=1 else int(x) for x in orig]} 实付{pay} 原价和{sum(orig)} 每单原价能否以分计价: {ok}")

# ---------- Q42 ----------
say("== Q42 下界可实现与错法")
uns = [20, 160, 24, 32]
say(f"  正解 400-{sum(uns)}={400-sum(uns)} (A)；把不满意和当答案 {sum(uns)} (D)")
uns_mis = [20, 160, 400 - (380 + 4), 32]
say(f"  误把“少4户”读成“多4户”：不满意{uns_mis} 和{sum(uns_mis)} -> {400-sum(uns_mis)} (B=172)，和本身 {sum(uns_mis)} (C=228)")

# ---------- Q43 ----------
say("== Q43 样本空间、错法与原B项")
tot = comb(5, 2) * comb(4, 2)
say(f"  总数{tot}；恰1对22 -> {F(22,tot)} (D)；未扣两对同入选 2×12=24 -> {F(24,tot)} (B=2/5)；误加 2×13=26 -> {F(26,tot)} (C=13/30)")
say(f"  至少1对 23 -> {F(23,tot)}；漏乘2：12 -> {F(12,tot)}，11 -> {F(11,tot)}；A=9/20={F(9,20)*tot}/60 无明显对应")
say(f"  原转写B=14/5={float(F(14,5))}>1，可不计算直接排除")
# 不考虑性别的误读：9人中任取4人
men = list(range(5)); women = list(range(5, 9)); couples = [(0, 5), (1, 6)]
cnt = tot9 = 0
for g in combinations(range(9), 4):
    tot9 += 1
    k = sum(1 for a, b in couples if a in g and b in g)
    cnt += (k == 1)
say(f"  误读为9人任取4人：{cnt}/{tot9} = {F(cnt, tot9)}（不在选项）")

# ---------- Q44 ----------
say("== Q44 端点口径")
L = set(range(0, 1486, 15)); R = set(range(0, 1486, 33)); both = L & R
mid = [x for x in both if 0 < x < 1485]
say(f"  只合并中间{len(mid)}处：{len(L)+len(R)-len(mid)} (B)；连两端也合并：{len(L)+len(R)-len(both)} (A=136)；全不合并：{len(L)+len(R)} (D=146)；只合并两端：{len(L)+len(R)-2} (C=144)")

# ---------- Q45 ----------
say("== Q45 变体穷举")
people = ["甲", "乙", "丙", "丁", "e", "f", "g", "h"]
def count(need_not_end=True, need_adj=True, forbid_cd=True):
    c = 0
    for p in permutations(people):
        pos = {x: i for i, x in enumerate(p)}
        a, b = pos["甲"], pos["乙"]
        if need_not_end and (a in (0, 7) or b in (0, 7)):
            continue
        if need_adj and abs(a - b) != 1:
            continue
        if forbid_cd and any(abs(pos[x] - pos[y]) == 1 for x in ("丙", "丁") for y in ("甲", "乙")):
            continue
        c += 1
    return c
c_ok = count()
c_noend = count(need_not_end=False)
c_nocd = count(forbid_cd=False)
say(f"  正解 {c_ok} (C)；漏乘甲乙内部顺序 {c_ok//2} (D=1440)；重复乘2 {c_ok*2} (A=5760)")
say(f"  忽略“不在队首队尾” {c_noend}；忽略丙丁限制 {c_nocd}")
say(f"  对称性：计数必为 2!·2!·4!=96 的倍数；2880/96={F(2880,96)}，5760/96={F(5760,96)}，1440/96={F(1440,96)}，4210/96={F(4210,96)}（B=4210 结构上不可能）")

with open(__file__.replace("distractor_and_edge_check.py", "distractor_and_edge_check_output.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")

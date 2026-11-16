#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""盲解阶段：M05 第36-45题（数学运算）精确求解/有限枚举，并考察常见误读得到的结果。
只读同目录 blind_input.json（仅用于打印题面与选项），不读仓库任何文件。"""
import json, os, itertools, datetime
from fractions import Fraction as F

WD = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(WD, 'blind_input.json'), encoding='utf-8'))
Q = {d['number']: d for d in data}
def txt(blocks): return ''.join(b.get('text', '') for b in blocks if b.get('type') == 'text')
def opts(n): return {k: txt(v) for k, v in Q[n]['options'].items()}
def fmt(x):
    x = F(x); return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
def head(n):
    print('=' * 78)
    print(f"第{n}题：{txt(Q[n]['stem'])}")
    print('选项：' + '  '.join(f"{k}={v}" for k, v in opts(n).items()))
def which(n, val):
    for k, v in opts(n).items():
        try:
            if F(v.rstrip('s')) == F(val):
                return k
        except Exception:
            pass
    return '无对应选项'

# ---------------- 36 ----------------
head(36)
sols = []
for r in range(0, 101):
    w, g = 3 * r, 4
    others = r + w + g
    y = others * F(14, 9)          # 黄 = 其余之和 ×(1+5/9)
    if y.denominator == 1 and y + others <= 100:
        sols.append((r, int(y), w, g, int(y) + others))
print('正读（黄=其余×(1+5/9)）解 (红,黄,白,绿,总):', sols)
for s in sols:
    print(f"  黄−红 = {s[1] - s[0]} → {which(36, s[1] - s[0])}")
# 误读1：黄 = 其余 × 5/9
alt = [(r, others * F(5, 9)) for r in range(0, 101) for others in [4 * r + 4]
       if (others * F(5, 9)).denominator == 1 and others * F(5, 9) + others <= 100]
print('误读“黄=其余×5/9”：', [(r, fmt(y), fmt(y - r)) for r, y in alt])
# 误读2：（黄−其余）= 黄×5/9 → 黄 = 其余×9/4
alt2 = [(r, F(9, 4) * (4 * r + 4)) for r in range(0, 101)
        if (F(9, 4) * (4 * r + 4)).denominator == 1 and F(9, 4) * (4 * r + 4) + 4 * r + 4 <= 100]
print('误读“多出部分占黄的5/9”：', [(r, fmt(y), fmt(y - r)) for r, y in alt2], '（不唯一）')
print('  其他差值：黄−白 =', sols[0][1] - sols[0][2], ' 黄−绿 =', sols[0][1] - sols[0][3], ' 黄−白−绿 =', sols[0][1] - sols[0][2] - sols[0][3])

# ---------------- 37 ----------------
head(37)
# 效率 a,b（工作量/天）；12(a+b)=8a+18b → a:b
# 设 b=1，a = 6/4
b = F(1); a = F(6, 4) * b
W = 12 * (a + b)
# 日工费 p,q：12(p+q)=12, 8p+18q=14
q = (F(14) - 8 * F(1)) / (18 - 8)   # 由 p=1-q 代入：8(1-q)+18q=14 → 10q=6
p = 1 - q
tA = W / a
print(f"效率比 甲:乙 = {fmt(a)}:{fmt(b)}，总量 {fmt(W)}，甲单独 {fmt(tA)} 天，乙单独 {fmt(W / b)} 天")
print(f"日工费 甲 {fmt(p)} 万，乙 {fmt(q)} 万；甲单独总工费 = {fmt(tA * p)} 万 → {which(37, tA * p)}")
print(f"  （乙单独总工费 {fmt(W / b * q)} 万；若误把 12 万当甲乙日费和直接比例分摊等不另列）")
# 误读：工费按工作量比例（甲完成部分占多少就付多少）
print(f"  校验：合作12天费用 {fmt(12 * (p + q))}；8天甲+18天乙费用 {fmt(8 * p + 18 * q)}；工作量 {fmt(12 * (a + b))}={fmt(8 * a + 18 * b)}")

# ---------------- 38 ----------------
head(38)
# 甲 1 小时走 D+20，乙 0.5 小时走 D-20，v甲=1.3v乙
# D+20 = 1.3 * 2 * (D-20)
D = (F(20) + F(13, 10) * 2 * 20) / (F(13, 10) * 2 - 1)
v_yi = (D - 20) / F(1, 2); v_jia = (D + 20) / 1
print(f"AB = {fmt(D)} km → {which(38, D)}；v乙={fmt(v_yi)}，v甲={fmt(v_jia)}，比={fmt(v_jia / v_yi)}")
# 误读：两车都行驶了 30 分钟 / 甲行驶 30 分钟
for lab, tj, ty in (("甲1h乙0.5h(正读)", F(1), F(1, 2)), ("误把两车都算1h", F(1), F(1)), ("误把甲算0.5h乙0.5h", F(1, 2), F(1, 2)), ("误把乙算1h甲1.5h", F(3, 2), F(1))):
    # v甲 tj = D+20 ; v乙 ty = D-20 ; v甲=1.3 v乙 → D+20 = 1.3 (tj/ty)(D-20)
    k = F(13, 10) * tj / ty
    if k != 1:
        Dx = (20 + 20 * k) / (k - 1)
        print(f"  {lab}: D={fmt(Dx)} ({float(Dx):.3f}) → {which(38, Dx)}")
# 误读：v乙 = 0.7 v甲
k = (F(10, 7)) * 2
print(f"  误读 v甲=v乙/0.7: D={float((20 + 20 * k) / (k - 1)):.3f}")

# ---------------- 39 ----------------
head(39)
best = []
for L in range(1, 50):
    tri = [(x, y, z) for x in range(1, L) for y in range(x, L) for z in [L - x - y]
           if z >= y and y - x == z - y and x * x + y * y == z * z]
    if not tri:
        continue
    if L % 2:
        continue
    s = L // 2
    rects = [(a, s - a) for a in range(1, s) if a < s - a]
    if rects:
        a, b2 = max(rects, key=lambda t: t[0] * t[1])
        best.append((L, tri, (a, b2), a * b2))
for row in best:
    print(f"  绳长{row[0]}: 三角形{row[1]}，长方形最大 {row[2]} 面积 {row[3]}")
mx = max(best, key=lambda r: r[3])
print(f"最大面积 {mx[3]} → {which(39, mx[3])}（若允许正方形则 {(mx[0] // 4) ** 2} → {which(39, (mx[0] // 4) ** 2)}）")
# 若只要求长方形整数边（三角形边可非整数）：L 须为偶数且 L=12d<50
cand = [L for L in range(2, 50, 2)]
L2 = max(cand)
s = L2 // 2
print(f"  若三角形边可非整数：L 最大偶数 {L2}（12d=48 才是 AP 直角三角形周长且 <50 的最大偶数？d=4 →{48}），面积 {max(a*(s-a) for a in range(1, s) if a != s - a)}")

# ---------------- 40 ----------------
head(40)
TOTAL = 83 * 5
res = []
for s3 in range(81, 101):
    s4 = 160 - s3
    if not s4 < s3:
        continue
    for s2 in range(s3 + 1, min(s3 + 5, 100) + 1):
        for s1 in range(s2 + 1, min(s2 + 5, 100) + 1):
            s5 = TOTAL - s1 - s2 - s3 - s4
            if 0 <= s5 < s4 and s4 - s5 <= 5:
                res.append((s1, s2, s3, s4, s5))
mins3 = min(r[2] for r in res)
print(f"可行方案数 {len(res)}；第三高最低 {mins3} → {which(40, mins3)}")
print('  s3 最低时的全部方案：', [r for r in res if r[2] == mins3])
print('  s3 的可行取值：', sorted(set(r[2] for r in res)))
# 变体：把 3-4 名也计入“差不超过5”
res2 = [r for r in res if r[2] - r[3] <= 5]
print('  若3、4名之差也≤5：s3 最低', min(r[2] for r in res2))
# 变体：允许分数相同（非严格）
res3 = []
for s3 in range(80, 101):
    s4 = 160 - s3
    if s4 > s3:
        continue
    for s2 in range(s3, min(s3 + 5, 100) + 1):
        for s1 in range(s2, min(s2 + 5, 100) + 1):
            s5 = TOTAL - s1 - s2 - s3 - s4
            if 0 <= s5 <= s4 and s4 - s5 <= 5:
                res3.append((s1, s2, s3, s4, s5))
print('  若允许同分：s3 最低', min(r[2] for r in res3), [r for r in res3 if r[2] == min(x[2] for x in res3)])
# 变体：“其余任意相邻排名差不超过5”只约束 1-2、2-3、4-5 —— 即正读；再看若没有 4-5 约束
res4 = []
for s3 in range(81, 101):
    s4 = 160 - s3
    for s2 in range(s3 + 1, min(s3 + 5, 100) + 1):
        for s1 in range(s2 + 1, min(s2 + 5, 100) + 1):
            s5 = TOTAL - s1 - s2 - s3 - s4
            if 0 <= s5 < s4:
                res4.append((s1, s2, s3, s4, s5))
print('  若无4-5名约束：s3 最低', min(r[2] for r in res4))

# ---------------- 41 ----------------
head(41)
ages = [24, 26, 29, 32, 34, 36]
def count(strict=True, gap=10, ordered=True):
    subs = []
    for c in itertools.combinations(ages, 3):
        s = sum(c)
        avg_ok = s > 84 if strict else s >= 84
        if avg_ok and max(c) - min(c) <= gap:
            subs.append(c)
    return subs
subs = count(True)
print(f"“超过28岁”取严格 >28：组合 {len(subs)} 个：{subs}")
print(f"  ×3! = {len(subs) * 6} → {which(41, len(subs) * 6)}")
subs_ne = count(False)
print(f"若取 ≥28：组合 {len(subs_ne)} 个，×6 = {len(subs_ne) * 6} → {which(41, len(subs_ne) * 6)}；新增 {sorted(set(subs_ne) - set(subs))}")
print(f"不计顺序：{len(subs)} → {which(41, len(subs))}")
print(f"若‘不超过10’误作 <10：{len(count(True, 9))} 组 ×6 = {len(count(True, 9)) * 6} → {which(41, len(count(True, 9)) * 6)}")
print(f"若再给3个课题另行分配(3!×3!)：{len(subs) * 36}")
print('  选项是否为6的倍数：', {k: (int(v) % 6 == 0) for k, v in opts(41).items()})

# ---------------- 42 ----------------
head(42)
def jia(x):
    x = F(x); s = F(0)
    s += min(x, 30) / 3
    if x > 30: s += (min(x, 50) - 30) * F(4, 10)
    if x > 50: s += (min(x, 60) - 50) * F(2, 10)
    if x > 60: s += (x - 60)
    return s
p1 = jia(75); p2 = jia(45) + jia(30)
print(f"计划①甲 {fmt(p1)}；计划②甲 {fmt(jia(45))}+{fmt(jia(30))}={fmt(p2)}；差 {fmt(p1 - p2)} → {which(42, p1 - p2)}")
def yi(x):
    x = F(x); s = min(x, 30) / 3
    if x > 30: s += (min(x, 50) - 30) * F(3, 10)
    if x > 50: s += (min(x, 60) - 50) * F(4, 10)
    return s
print(f"  （乙：计划① {fmt(yi(75))}，计划② {fmt(yi(45) + yi(30))}；三人合计校验 ① {fmt(jia(75) + 2 * yi(75))}=75，② {fmt(jia(45) + 2 * yi(45) + jia(30) + 2 * yi(30))}=75）")
# 常见误算：把 75 全部按最高档/漏算 60 以上部分 等
print(f"  误把75万超出60的15万也按20%：甲 {fmt(jia(60) + 15 * F(2, 10))}，差 {fmt(jia(60) + 15 * F(2, 10) - p2)}")
print(f"  误把计划②看成一个75万：差 0；误只算超60部分：15 → {which(42, 15)}")

# ---------------- 43 ----------------
head(43)
# 7-12 月 5 日相对 7 月 5 日的星期位移
months = [7, 8, 9, 10, 11, 12]
dim = {7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
off = [0]
for m in months[:-1]:
    off.append((off[-1] + dim[m]) % 7)
print('各月5日相对7月5日的星期位移：', dict(zip(months, off)))
best = []
for w in range(7):   # w = 7月5日是星期几，0=周一 … 6=周日
    days = [(w + o) % 7 for o in off]
    good = sum(1 for d in days if d < 5)
    best.append((good, w, days))
names = '一二三四五六日'
for g, w, days in sorted(best, reverse=True):
    print(f"  7月5日为星期{names[w]}：各月5日为 {['星期' + names[d] for d in days]}，正好5号发 {g} 个月")
mx = max(b[0] for b in best)
print(f"最多 {mx} 个月 → {which(43, mx)}")
# 真实日历核对 1900-2100
real = {}
for y in range(1900, 2101):
    g = sum(1 for m in months if datetime.date(y, m, 5).weekday() < 5)
    real.setdefault(g, []).append(y)
print('  真实日历 1900-2100 年下半年“正好5号发”的月数分布：', {k: len(v) for k, v in sorted(real.items())}, '；取得最大值的年份举例：', real[max(real)][:6])

# ---------------- 44 ----------------
head(44)
N, M, E, C, ALL3 = 40, 25, 27, 21, 12
none = F(ALL3, 3)   # “多2倍”=3倍
at_least1 = N - none
# x1+x2+x3=at_least1, x1+2x2+3x3=M+E+C, x3=12
x2 = (M + E + C) - at_least1 - 2 * ALL3
x1 = at_least1 - x2 - ALL3
print(f"都不及格 {fmt(none)}；恰1科 {fmt(x1)}，恰2科 {fmt(x2)}，3科 {ALL3}；至少两科 = {fmt(x2 + ALL3)} → {which(44, x2 + ALL3)}")
# 可行性：枚举只M、只E、只C、ME、MC、EC
cnt = 0; ex = None
for me in range(0, 30):
    for mc in range(0, 30):
        ec = int(x2) - me - mc
        if ec < 0: continue
        m_only = M - ALL3 - me - mc; e_only = E - ALL3 - me - ec; c_only = C - ALL3 - mc - ec
        if min(m_only, e_only, c_only) < 0: continue
        if m_only + e_only + c_only + me + mc + ec + ALL3 + int(none) == N:
            cnt += 1; ex = ex or (m_only, e_only, c_only, me, mc, ec)
print(f"  可行的维恩分布数 {cnt}，例：只数{ex[0]} 只英{ex[1]} 只语{ex[2]} 数英{ex[3]} 数语{ex[4]} 英语{ex[5]}")
# 误读“多2倍”=2倍
none2 = F(ALL3, 2); al = N - none2; x2b = (M + E + C) - al - 2 * ALL3
print(f"  若“多2倍”理解为2倍：都不及格 {fmt(none2)}，至少两科 {fmt(x2b + ALL3)} → {which(44, x2b + ALL3)}")
print(f"  恰两科 {fmt(x2)} → {which(44, x2)}（只算恰两科的错法）")

# ---------------- 45 ----------------
head(45)
kmh = lambda v: F(v) * 1000 / 3600   # m/s
v1, v2 = kmh(60), kmh(40)
t1 = 2 * F(1000) / v1                 # 匀加速 0→v1 走 1000m：t = 2s/v
# 减速阶段：相对速度从 (v1-v2) 线性降到 0，相对位移 500-100=400
t2 = 2 * F(400) / (v1 - v2)
print(f"加速段 {fmt(t1)} s；减速段 {fmt(t2)} s；合计 {fmt(t1 + t2)} s → {which(45, t1 + t2)}")
s_jia = (v1 + v2) / 2 * t2; s_front = v2 * t2
print(f"  减速段甲走 {fmt(s_jia)} m，前车走 {fmt(s_front)} m，间距 500→{fmt(500 - (s_jia - s_front))} m；减速度 {fmt((v1 - v2) / t2)} m/s²")
# 常见误算
t2_wrong = 2 * F(400) / (v1 + v2)
print(f"  误把400m当作甲自身位移按平均速度：{float(t2_wrong):.2f} s，合计 {float(t1 + t2_wrong):.2f}")
t2_w2 = 2 * F(500) / (v1 - v2)
print(f"  误把相对位移取500m：减速段 {fmt(t2_w2)} s，合计 {fmt(t1 + t2_w2)} → {which(45, t1 + t2_w2)}")
t2_w3 = 2 * F(600) / (v1 - v2)
print(f"  误把相对位移取600m：减速段 {fmt(t2_w3)} s，合计 {fmt(t1 + t2_w3)} → {which(45, t1 + t2_w3)}")
print(f"  只算加速段 {fmt(t1)} → {which(45, t1)}；只算减速段 {fmt(t2)} → {which(45, t2)}")
t1_w = F(1000) / v1
print(f"  加速段误用 s/v：{fmt(t1_w)} s，合计 {fmt(t1_w + t2)} → {which(45, t1_w + t2)}")

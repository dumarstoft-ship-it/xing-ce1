#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第二阶段：逐题核对解析中的数值论断，并把干扰项与常见错法对应（只读仓库）。"""
import itertools, json, datetime
from fractions import Fraction as F

SEL = '/home/user/xing-ce1/广东行测18套模拟/M05/selection.json'
sel = {int(q['number']): q for q in json.load(open(SEL, encoding='utf-8'))}
def opt(n):
    return {k: ''.join(b.get('text', '') for b in v) for k, v in sel[n]['source_question']['options'].items()}
def hit(n, val):
    for k, v in opt(n).items():
        try:
            if F(v.rstrip('s')) == F(val):
                return k
        except Exception:
            pass
    return '—'
def say(*a):
    print(*a)

say('=' * 70); say('第32题：解析称“按普通小数倍数会走入错误方向”是否成立')
even = [F('9.1'), F('18.2')]
say(f'  偶数项按数值×2：9.1×2={even[0]*2}，18.2×2={even[1]*2} → 所求36.4 → 选项{hit(32, even[1]*2)}（与答案相同）')
say(f'  奇数项按数值×2：10.8×2={F("10.8")*2}≠20.16 → 只说明奇数项不是数值加倍，所求项（偶数位）用数值加倍照样得到 A')
say('  B=36.28：整数部分对(36)、小数部分取28（无规律）；C=35.4：小数部分对(4)、整数部分35（无规律）；D 两部分都不对 → 半对干扰项')

say('=' * 70); say('第35题：奇数项差 4,9,25 的底数 2,3,5 的两种续法')
for lab, b in (('质数 2,3,5,7', 7), ('斐波那契 2,3,5,8', 8)):
    say(f'  {lab} → 差 {b*b} → 第9项 {53 + b*b} → 选项{hit(35, 53 + b*b)}')
odd = [15, 19, 28, 53, 122]
say(f'  凑数规律：aₖ−2aₖ₋₁ = {[odd[i]-2*odd[i-1] for i in range(1,5)]} = k³−11 (k=0..3) → 122 → 选项{hit(35,122)}（常数−11，属拟合，不是考生会用的规律）')

say('=' * 70); say('第36题：干扰项')
r, y, w, g = 8, 56, 24, 4
for lab, v in (('黄−红', y-r), ('黄−绿', y-g), ('黄−红−绿', y-r-g), ('黄−白+红', y-w+r), ('黄−2红', y-2*r), ('黄−白−绿−红', y-w-g-r)):
    say(f'  {lab} = {v} → {hit(36, v)}')

say('=' * 70); say('第39题：C/D 是否可能出现')
say(f'  周长 L<50 的整数边长方形面积上界：L=48 时 ⌊24/2⌋² = 144；146、149 在任何周长<50的整数长方形下都不可能 → C、D 可直接排除')
say(f'  若误把“不足50”当“不超过50”并忽略三角形：L=50 → 12×13 = {12*13}；若误取 L=36：8×10 = 80')

say('=' * 70); say('第40题：解析不等式与干扰项')
x = 81
say(f'  上界和式 (x+10)+(x+5)+x+(160−x)+(159−x) = x+334，x=81 时 {(x+10)+(x+5)+x+(160-x)+(159-x)}（=415）')
say(f'  互异直接给出 x>160−x → x≥81，与和式下界重合')
# 错法：把 4-5 名也取差 5
x85 = None
for xx in range(81, 101):
    if (xx + 10) + (xx + 5) + xx + (160 - xx) + (160 - xx - 5) == 415:
        x85 = xx
say(f'  错法“三个相邻差都取满5”：(x+10)+(x+5)+x+(160−x)+(155−x)=415 → x={x85} → 选项{hit(40, x85)}')
say(f'  错法“忽略互不相同”：x=80（90,85,80,80,80）→ 选项{hit(40, 80)}；平均分 83 → 选项{hit(40, 83)}')

say('=' * 70); say('第41题：各种错法对应的数值（用于评估/替换干扰项）')
ages = [24, 26, 29, 32, 34, 36]
def cnt(avg_ok, gap_ok):
    return [c for c in itertools.combinations(ages, 3) if avg_ok(sum(c)) and gap_ok(max(c) - min(c))]
variants = {
    '正读：和>84 且 极差≤10': cnt(lambda s: s > 84, lambda d: d <= 10),
    '“超过”当“不低于”：和≥84 且 极差≤10': cnt(lambda s: s >= 84, lambda d: d <= 10),
    '“不超过10”当“小于10”：和>84 且 极差<10': cnt(lambda s: s > 84, lambda d: d < 10),
    '漏掉年龄差条件：和>84': cnt(lambda s: s > 84, lambda d: True),
    '漏掉平均年龄条件：极差≤10': cnt(lambda s: True, lambda d: d <= 10),
    '两处都放宽：和≥84 且 极差≤10': cnt(lambda s: s >= 84, lambda d: d <= 10),
}
for lab, lst in variants.items():
    say(f'  {lab}: {len(lst)} 组，×6 = {len(lst)*6} → 选项{hit(41, len(lst)*6)}；不计顺序 {len(lst)} → 选项{hit(41, len(lst))}')
say(f'  选项 70、74、76 均非 6 的倍数（70/6={F(70,6)}, 74/6={F(74,6)}, 76/6={F(76,6)}）')
# 解析中的 3+6+4
with24 = [c for c in variants['正读：和>84 且 极差≤10'] if 24 in c]
no24_with26 = [c for c in variants['正读：和>84 且 极差≤10'] if 24 not in c and 26 in c]
neither = [c for c in variants['正读：和>84 且 极差≤10'] if 24 not in c and 26 not in c]
say(f'  解析分类核对：含24 {len(with24)} 组 {with24}；不含24含26 {len(no24_with26)} 组；都不含 {len(neither)} 组')

say('=' * 70); say('第42题：解析数值核对')
def jia(x):
    x = F(x); s = min(x, 30) / 3
    if x > 30: s += (min(x, 50) - 30) * F(2, 5)
    if x > 50: s += (min(x, 60) - 50) * F(1, 5)
    if x > 60: s += x - 60
    return s
say(f'  75万：{jia(75)}；45万：{jia(45)}；30万：{jia(30)}；差 {jia(75) - jia(45) - jia(30)}')
say(f'  错法“75万按总额只看超60部分”15 → {hit(42, 15)}；错法“②当作一个75万再减”0；错法“①漏掉50-60段”{jia(75)-2-jia(45)-jia(30)} → {hit(42, jia(75)-2-jia(45)-jia(30))}；错法“①把60以上也按20%” {jia(60)+3-jia(45)-jia(30)}')
# 错法：①漏算 30-50 段的 8
say(f'  错法“①漏30-50段”: {jia(75)-8-jia(45)-jia(30)} → {hit(42, jia(75)-8-jia(45)-jia(30))}；错法“②的30万项目按40%”: {jia(75)-jia(45)-12} → {hit(42, jia(75)-jia(45)-12)}')

say('=' * 70); say('第43题：解析中“周一至周日依次 4、5、4、5、5、4、3”核对')
off = [0, 3, 6, 1, 4, 6]
counts = [sum(1 for o in off if (w + o) % 7 < 5) for w in range(7)]
say(f'  7月5日为周一…周日时的计数：{counts}')
w = 1  # 周二
say(f'  7月5日为周二：{["一二三四五六日"[(w + o) % 7] for o in off]}')
# 9 月、12 月同星期
say(f'  9月5日与12月5日星期相同：{(off[2] - off[5]) % 7 == 0}（9-12月相隔 30+31+30=91 天）')
# 国庆假期：若10月5日为工作日，题目规则仍按5号发
yrs = [y for y in range(2000, 2101) if sum(1 for m in range(7, 13) if datetime.date(y, m, 5).weekday() < 5) == 5]
say(f'  2000-2100 年中下半年恰有5个月5号为工作日的年份数：{len(yrs)}，例 {yrs[:5]}')
say(f'  其中10月5日恰为工作日的年份占比：{sum(1 for y in yrs if datetime.date(y,10,5).weekday()<5)}/{len(yrs)}（若考生把国庆假期计入会改变计数，但题设规则只涉及周六周日）')

say('=' * 70); say('第44题：干扰项对应')
def at_least_two(none):
    union = 40 - none
    extra = 25 + 27 + 21 - union
    two = extra - 2 * 12
    return two, two + 12
for lab, none in (('正读“多2倍”=3倍', F(12, 3)), ('“多2倍”当2倍', F(12, 2)), ('“多2倍”当“多2人”', F(10)), ('漏减都不及格', F(0))):
    two, ans = at_least_two(none)
    say(f'  {lab}: 都不及格 {none}，恰两科 {two}，至少两科 {ans} → 选项{hit(44, ans)}；恰两科 → 选项{hit(44, two)}')
say(f'  其他：只算“恰两科”13 → {hit(44, 13)}；至少一科 36；73−40−12−3? 均不对应 18')
for lab, v in (('36−12−6', 36 - 12 - 6), ('(73−37)/2', F(73 - 37, 2)), ('37−12−7', 18), ('恰一科11+…', 11 + 7)):
    pass

say('=' * 70); say('第45题：干扰项对应')
kmh = lambda v: F(v) * 1000 / 3600
t1 = 2 * F(1000) / kmh(60); t2 = 2 * F(400) / kmh(20)
say(f'  t1={t1}s, t2={t2}s, 合计 {t1 + t2} → {hit(45, t1 + t2)}；只算 t1 → {hit(45, t1)}；只算 t2 → {hit(45, t2)}')
cands = {
    '相对位移400m按相对速度20km/h全程(不取平均)': t1 + F(400) / kmh(20),
    '甲自身走400m、平均50km/h': t1 + F(400) / kmh(50),
    '相对位移取500m': t1 + 2 * F(500) / kmh(20),
    '相对位移取600m': t1 + 2 * F(600) / kmh(20),
    '加速段用1km÷60km/h': F(1000) / kmh(60) + t2,
    '减速段按甲位移2000m、平均45km/h': t1 + F(2000) / kmh(45),
    '减速段甲位移2000m按40km/h': t1 + F(2000) / kmh(40),
    '减速段甲位移2000m按60km/h': t1 + F(2000) / kmh(60),
}
for lab, v in cands.items():
    say(f'  {lab}: {float(v):.2f}s → {hit(45, v) if v.denominator == 1 else "—"}')

say('=' * 70); say('第43题补充：若考生把10月5日（国庆假期内）也视为不在5号发，最大值是否改变')
names = '一二三四五六日'
for w in range(7):
    days = [(w + o) % 7 for o in off]
    rule = sum(1 for d in days if d < 5)
    holiday = sum(1 for i, d in enumerate(days) if d < 5 and i != 3)   # i=3 为10月
    say(f'  7月5日周{names[w]}：按题设 {rule} 个月；把10月5日当假日 {holiday} 个月')
say('  → 两种理解下最大值都是 5（7月5日为周五时10月5日恰为周六，2024年即如此）')

say('=' * 70); say('第41题补充：建议替换后的选项 48/78/84/96 是否只有一个符合正读')
new_opts = {'A': 48, 'B': 78, 'C': 84, 'D': 96}
for k, v in new_opts.items():
    src = [lab for lab, lst in variants.items() if len(lst) * 6 == v]
    say(f'  {k}={v}：对应 {src}')

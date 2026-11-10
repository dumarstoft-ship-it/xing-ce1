# -*- coding: utf-8 -*-
"""ZL4B independent verification (D11 保留块).
Every delivered question is re-solved from the material's printed numbers.
 - computed-value questions: the option closest to the computed value (margin reported)
 - judgement questions: every option evaluated separately; exactly one must fit the stem
 - adaptations: additionally a rounding-perturbation test - every rounded input is moved to both ends of
   its rounding interval (full corner grid + centre); the keyed answer must stay the unique answer.
Results are written to verify_results.json (key -> answer, detail, perturbation summary)."""
import itertools, json, math, os, sys

SP = '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/zl4b'
R = {}
FAIL = []


def rec(key, ans, detail, src=None, pert=None):
    R[key] = dict(ans=ans, detail=detail, src=src, pert=pert)
    flag = ''
    if src is not None and src != ans:
        flag = '   <-- MISMATCH vs source ' + str(src)
        FAIL.append(key)
    print(f'{key}: {ans} | {detail}' + (f' | 扰动: {pert}' if pert else '') + flag)


def closest(val, opts):
    d = {k: abs(v - val) for k, v in opts.items()}
    s = sorted(d, key=d.get)
    return s[0], d[s[1]] - d[s[0]]


def iv(x, dec):
    """rounding interval of a printed number x with `dec` decimals"""
    h = 0.5 * 10 ** (-dec)
    return (x - h, x + h)


def grid(**ivs):
    keys = list(ivs)
    for combo in itertools.product(*[(lo, (lo + hi) / 2, hi) for (lo, hi) in ivs.values()]):
        yield dict(zip(keys, combo))


def robust_value(fn, opts, want, **ivs):
    """fn(**inputs)->value; the closest option must be `want` on the whole grid. returns (min,max,min margin)"""
    lo = hi = None
    mm = None
    n = 0
    for kw in grid(**ivs):
        v = fn(**kw)
        a, m = closest(v, opts)
        assert a == want, ('robust_value failed', want, a, v, kw)
        lo = v if lo is None else min(lo, v)
        hi = v if hi is None else max(hi, v)
        mm = m if mm is None else min(mm, m)
        n += 1
    return lo, hi, mm, n


def robust_truth(fn, want_true, **ivs):
    """fn(**inputs)->{'A':bool,...}; exactly the options in want_true must be True on the whole grid"""
    n = 0
    for kw in grid(**ivs):
        t = fn(**kw)
        got = sorted(k for k, v in t.items() if v)
        assert got == sorted(want_true), ('robust_truth failed', want_true, got, kw, t)
        n += 1
    return n


# =====================================================================================================
# M1  ZLM-JS2023A-1  “十年成就”（江苏2023年度A类 第116—120题）
# =====================================================================================================
gdp_share21, gdp_share_up = 18.5, 7.2
r_gdp, r_fiscal, r_manu, r_hitech, r_equip, r_serv = 6.6, 5.8, 6.4, 11.6, 9.2, 7.4
flow_times, user_growth = 252, 83.0
sewage21, garbage21, sewage_up, garbage_up = 97.5, 99.9, 10.2, 15.1
water21, water_up = 84.9, 23.2
pm21, pm_down = 30, 34.8

# 116 (mother of A2; not delivered)
a, m = closest(sewage21 - sewage_up, {'A': 82.4, 'B': 84.8, 'C': 87.3, 'D': 89.7})
rec('JS2023A-116(母题,未收)', a, f'97.5-10.2={sewage21 - sewage_up:.1f}', 'C')
# 117
dn = [k for k, r in {'A': r_manu, 'B': r_equip, 'C': r_serv, 'D': r_hitech}.items() if r < r_gdp]
assert dn == ['A']
rec('JS2023A-117', dn[0], f'年均增速 制造业{r_manu}<GDP{r_gdp}; 装备{r_equip}、服务业{r_serv}、高技术{r_hitech}均>GDP; 规上工业={r_hitech}-4.8={r_hitech - 4.8:.1f}={r_equip}-2.4={r_equip - 2.4:.1f}', 'A')
# 118 (mother of A1; not delivered)
a, m = closest(pm21 / (1 - pm_down / 100), {'A': 38, 'B': 42, 'C': 46, 'D': 49})
rec('JS2023A-118(母题,未收)', a, f'30/(1-34.8%)={pm21 / (1 - pm_down / 100):.2f}', 'C')
# 119
v = flow_times / (1 + user_growth / 100)
a, m = closest(v, {'A': 105, 'B': 114, 'C': 126, 'D': 138})
rec('JS2023A-119', a, f'252/1.83={v:.1f}（离次近选项的余量{m:.1f}）; 错法252×(1-83%)={252 * (1 - .83):.1f}、252/0.83={252 / .83:.1f}都不在选项中', 'D')
# 120 能推出
t120 = {'A': False,                                   # 年均增长5.8% 不是2021年当年增速 -> 推不出
        'B': 142.5 / 0.600 > 250,                     # 占全球60.0%以上 -> 全球<=237.5 -> “超过250”为假
        'C': abs((gdp_share21 - gdp_share_up) - 11.3) < 1e-9,
        'D': False}                                   # 23.2个百分点是相对2012年, 无2015年数据
assert [k for k, x in t120.items() if x] == ['C']
rec('JS2023A-120', 'C', f'B:全球5G基站<=142.5/60%={142.5 / .6:.1f}万; C:18.5-7.2={gdp_share21 - gdp_share_up:.1f}; D:84.9-23.2={water21 - water_up:.1f}是2012年', 'C')


# ---- A2 改编 (variant_of JS2023A-116): 2012年末 生活垃圾无害化处理率 比 污水处理率 ----
def a2_val(s21=sewage21, g21=garbage21, su=sewage_up, gu=garbage_up):
    return (g21 - gu) - (s21 - su)          # 垃圾 − 污水（2012年末），单位：百分点
OPT_A2 = {'A': 2.4, 'B': 4.9, 'C': -2.5, 'D': -4.9}
a, m = closest(a2_val(), OPT_A2)
lo, hi, mm, n = robust_value(a2_val, OPT_A2, 'C', s21=iv(sewage21, 1), g21=iv(garbage21, 1), su=iv(sewage_up, 1), gu=iv(garbage_up, 1))
rec('ZL4B-A2 [JS2023A-1 基期两率比较]', a, f'2012年末: 污水{sewage21 - sewage_up:.1f}%, 垃圾{garbage21 - garbage_up:.1f}%, 差{a2_val():+.1f}个百分点; 现期差{garbage21 - sewage21:+.1f}(A); 升幅差{garbage_up - sewage_up:.1f}(B/D)',
    pert=f'{n}组: {lo:+.2f}~{hi:+.2f}, 恒最接近C, 最小余量{mm:.2f}')


# ---- A1 改编 (variant_of JS2023A-118): 未达到优良断面占比的降幅 ----
def a1_val(w21=water21, wu=water_up):
    bad21 = 100 - w21
    bad12 = 100 - (w21 - wu)
    return (bad12 - bad21) / bad12 * 100
OPT_A1 = {'A': 23.2, 'B': 27.3, 'C': 37.6, 'D': 60.6}
a, m = closest(a1_val(), OPT_A1)
lo, hi, mm, n = robust_value(a1_val, OPT_A1, 'D', w21=iv(water21, 1), wu=iv(water_up, 1))
rec('ZL4B-A1 [JS2023A-1 非优良断面占比降幅]', a,
    f'2012年优良{water21 - water_up:.1f}%→非优良{100 - (water21 - water_up):.1f}%; 2021年非优良{100 - water21:.1f}%; 降幅{a1_val():.2f}%; B=23.2/84.9={23.2 / 84.9 * 100:.2f}%; C=23.2/61.7={23.2 / 61.7 * 100:.2f}%',
    pert=f'{n}组: {lo:.2f}%~{hi:.2f}%, 恒最接近D, 最小余量{mm:.2f}')

# =====================================================================================================
# M3  ZLM-GK2022X-4  电信网络诈骗（国考2022年度行政执法卷 第126—130题）
# =====================================================================================================
solved, gangs, suspects = 11.4, 1.4, 15.4          # 万起/万个/万名 (2021年1—5月)
r_solved, r_gangs, r_susp = 60.4, 80.6, 146.5
may_filed, may_mom = 8.46, 14.3                    # 5月立案8.46万起，比4月下降14.3%
sms, calls = 9.1, 6.1                              # 亿条/亿次
warn_daily = 5.2                                   # 万条/日
big_cases, r_big = 881, 160.5
net_actions_min, net_caught = 21, 2421             # “20余次”≥21
cards_tel, cards_bank, card_gangs, punished = 373.3, 56.6, 1.5, 17.3
DAYS = 31 + 28 + 31 + 30 + 31                      # 2021年1—5月=151天
MONTHS_2CARD = 8                                   # 2020年10月—2021年5月

# 127
apr = may_filed / (1 - may_mom / 100)
a, m = closest(apr + may_filed, {'A': 12, 'B': 14, 'C': 16, 'D': 18})
rec('GK2022X-127', a, f'4月={apr:.3f}万起; 4—5月={apr + may_filed:.2f}万起', 'D')
# 128 (not delivered, free)
a, m = closest(sms * 1e4 / DAYS, {'A': 545, 'B': 571, 'C': 603, 'D': 659})
rec('GK2022X-128(未收)', a, f'9.1亿/151天={sms * 1e4 / DAYS:.1f}万条', 'C')
# 129 (mother of (b); not delivered)
a, m = closest(2654 / 991, {'A': 2.7, 'B': 2.4, 'C': 2.1, 'D': 1.8})
rec('GK2022X-129(母题,未收)', a, f'2654/991={2654 / 991:.3f}', 'A')
# 130 有几项
i1 = suspects / (1 + r_susp / 100) > 10
i2 = big_cases - big_cases / (1 + r_big / 100) > 500
i3 = (cards_tel + cards_bank) / card_gangs > 300
cnt = sum([i1, i2, i3])
rec('GK2022X-130', {0: 'A', 1: 'B', 2: 'C', 3: 'D'}[cnt],
    f'①2020年1—5月嫌疑人={suspects / (1 + r_susp / 100):.2f}万<10 ✗; ②多{big_cases - big_cases / (1 + r_big / 100):.1f}起>500 ✓; ③({cards_tel}+{cards_bank})/{card_gangs}={(cards_tel + cards_bank) / card_gangs:.1f}张<300 ✗', 'B')


# ---- C1 改编 (variant_of GK2022X-129): 百万元以上案件数与破获案件总数之比的同比变化（百分点） ----
def c1_val(sv=solved, rs=r_solved, rb=r_big, bc=big_cases):
    now = bc / (sv * 1e4) * 100
    prev = (bc / (1 + rb / 100)) / (sv * 1e4 / (1 + rs / 100)) * 100
    return now - prev
OPT_C1 = {'A': 0.3, 'B': 0.8, 'C': -0.3, 'D': -0.8}
a, m = closest(c1_val(), OPT_C1)
lo, hi, mm, n = robust_value(c1_val, OPT_C1, 'A', sv=iv(solved, 1), rs=iv(r_solved, 1), rb=iv(r_big, 1))
now = big_cases / (solved * 1e4) * 100
prev = (big_cases / (1 + r_big / 100)) / (solved * 1e4 / (1 + r_solved / 100)) * 100
rec('ZL4B-C1 [GK2022X-4 两期比例差]', a, f'2021年{now:.4f}%, 2020年{prev:.4f}%, 差{c1_val():+.4f}个百分点; 忘除(1+a): {now * (r_big - r_solved) / 100:.3f}(B)',
    pert=f'{n}组: {lo:+.3f}~{hi:+.3f}, 恒最接近A, 最小余量{mm:.3f}')


# ---- C2 改编 (variant_of GK2022X-130): 能够推出的是 ----
def c2_truth(wd=warn_daily, mf=may_filed, mm_=may_mom, pu=punished, nc=net_caught):
    apr_ = mf / (1 - mm_ / 100)
    return {
        'A': wd * DAYS > 800,                 # 累计预警指令(万条)>800 ?
        'B': nc / net_actions_min > 120,      # “20余次”→至少21次→平均至多 2421/21
        'C': apr_ - mf > 1.3,                 # 4月比5月多1.3万起以上 ?
        'D': pu / MONTHS_2CARD > 3,           # 8个月月均>3万名 ?
    }
t = c2_truth()
assert [k for k, x in t.items() if x] == ['C'], t
n = robust_truth(c2_truth, ['C'], wd=iv(warn_daily, 1), mf=iv(may_filed, 2), mm_=iv(may_mom, 1), pu=iv(punished, 1))
rec('ZL4B-C2 [GK2022X-4 能推出]', 'C',
    f'A:5.2万×{DAYS}天={warn_daily * DAYS:.1f}万<800(若按155天={warn_daily * 155:.0f}万); B:2421/21={net_caught / 21:.1f}<120(2421/20={net_caught / 20:.2f}); '
    f'C:4月{apr:.3f}-5月{may_filed}={apr - may_filed:.3f}万>1.3(误用8.46×14.3%={may_filed * may_mom / 100:.2f}); D:17.3/8={punished / 8:.3f}<3(若÷5={punished / 5:.2f})',
    pert=f'{n}组: 恒只有C为真; C最小值{min(kw["mf"] / (1 - kw["mm_"] / 100) - kw["mf"] for kw in grid(mf=iv(may_filed, 2), mm_=iv(may_mom, 1))):.3f}; A最大值{iv(warn_daily, 1)[1] * DAYS:.1f}')

# =====================================================================================================
# M2  ZLM-ZJ2015A-3  台湾多层次资本市场（浙江2015年度A卷 第121—125题）
# =====================================================================================================
TW = {'集中': dict(n=809, cap=6384, mv=21352, rev=20083, tv=20789),
      '上柜': dict(n=638, cap=667, mv=1737, rev=1384, tv=2987),
      '兴柜': dict(n=285, cap=335, mv=538, rev=497, tv=154)}     # 单位：10亿新台币
decline = 23.28
sh_mv, sh_tv, sh_tv_prev = 1.34, 1.39, 1.41

# 121 规则匹配
cap_co, prof2 = 2.0, 3.0      # 实收资本2亿；最近2个年度获利能力均3%
ok_tse = cap_co >= 6          # 上市要求实收资本6亿以上
ok_otc = (cap_co >= 0.5) and (prof2 >= 2)      # 上柜：5000万以上；最近二个年度均达2%以上
assert (not ok_tse) and ok_otc
rec('ZJ2015A-121', 'B', '实收资本2亿<6亿→不能上市; ≥5000万且最近二个年度获利能力均≥2%→符合上柜; 能上柜者不必退到无门槛的兴柜', 'B')
# 122 (mother of B1; not delivered)
v = TW['集中']['mv'] / 1000 / (sh_mv / 100)
a, m = closest(v, {'A': 894.73, 'B': 1593.43, 'C': 1799.73, 'D': 2135.22})
rec('ZJ2015A-122(母题,未收)', a, f'21.352兆/1.34%={v:.2f}兆', 'B')
# 123
v = (TW['集中']['tv'] / TW['集中']['n']) / (TW['兴柜']['tv'] / TW['兴柜']['n'])
a, m = closest(v, {'A': 17.6, 'B': 27.6, 'C': 37.6, 'D': 47.6})
rec('ZJ2015A-123', a, f'(20789/809)/(154/285)={TW["集中"]["tv"] / 809:.3f}/{154 / 285:.4f}={v:.2f}', 'D')
# 124
tot12 = sum(x['tv'] for x in TW.values())
tot11 = tot12 / (1 - decline / 100)
a, m = closest(tot11 / 1000, {'A': 15.441, 'B': 23.931, 'C': 31.233, 'D': 45.023})
rec('ZJ2015A-124', a, f'2012合计{tot12}(10亿)={tot12 / 1000:.3f}兆; /(1-23.28%)={tot11 / 1000:.3f}兆, 最接近C(31.233, 差{abs(tot11 / 1000 - 31.233):.3f}); 现期23.930≈B', 'C')
# 125 (mother of B2; not delivered)
rec('ZJ2015A-125(母题,未收)', 'C', '总市值排名相同、比重仍为1.34%; 成交值排名不变、比重1.41%→1.39%', 'C')


# ---- B1 改编 (variant_of ZJ2015A-122): WFE 会员 总成交值/总市值 ----
def b1_val(smv=sh_mv, stv=sh_tv):
    return (TW['集中']['tv'] / stv) / (TW['集中']['mv'] / smv)
OPT_B1 = {'A': 0.94, 'B': 0.97, 'C': 1.01, 'D': 1.07}
a, m = closest(b1_val(), OPT_B1)
lo, hi, mm, n = robust_value(b1_val, OPT_B1, 'A', smv=iv(sh_mv, 2), stv=iv(sh_tv, 2))
rec('ZL4B-B1 [ZJ2015A-3 WFE成交值/市值]', a,
    f'WFE成交值={TW["集中"]["tv"] / 1000 / (sh_tv / 100):.1f}兆, 市值={TW["集中"]["mv"] / 1000 / (sh_mv / 100):.1f}兆, 比={b1_val():.4f}; 台湾证交所自身={20789 / 21352:.4f}(B); 比重用反={20789 / 21352 * sh_tv / sh_mv:.4f}(C); 颠倒={1 / b1_val():.4f}(D)',
    pert=f'{n}组: {lo:.4f}~{hi:.4f}, 恒最接近A, 最小余量{mm:.4f}')


# ---- B2 改编 (variant_of ZJ2015A-125): 下列说法正确的是 ----
def b2_truth(dc=decline):
    t11 = tot12 / (1 - dc / 100)
    rank12, drop = 9, 2
    rank11 = rank12 - drop                      # 2012年较2011年下降2名 → 2011年为第7名
    return {
        'A': rank11 == 11,
        'B': TW['上柜']['cap'] / TW['上柜']['n'] > TW['兴柜']['cap'] / TW['兴柜']['n'],
        'C': (t11 - tot12) / 1000 > 7,
        'D': abs((6 - 0.5) / 0.5 - 12) < 1e-9,    # 6亿是5000万的12倍 → 高11倍；“高12倍”为假
    }
t = b2_truth()
assert [k for k, x in t.items() if x] == ['C'], t
n = robust_truth(b2_truth, ['C'], dc=iv(decline, 2))
rec('ZL4B-B2 [ZJ2015A-3 说法正确]', 'C',
    f'A:2011年周转率排名=9-2=第7名; B:上柜{667 / 638:.4f}<兴柜{335 / 285:.4f}(10亿/家); C:2011年{tot11 / 1000:.3f}兆-2012年{tot12 / 1000:.3f}兆={(tot11 - tot12) / 1000:.3f}兆>7(误用现期×降幅={tot12 / 1000 * decline / 100:.2f}兆); D:6亿/5000万=12倍=高11倍(“高12倍”为假)',
    pert=f'{n}组: 恒只有C为真')

# =====================================================================================================
# M4  ZLM-ZJ2017A-1  国家自然科学基金（浙江2017年度A卷 第111—115题）
# =====================================================================================================
app_all, fund_all, fund_all_up, cost_all = 173017, 40668, 1579, 218.8
ms_n, ms_up, ms_cost, ms_rate, ms_rate_dn = 16709, 1709, 102.41, 22.9, 2.5
key_n, key_g, key_cost = 625, 3.3, 17.88
major_n, major_cost = 20, 3.18
yth_n, yth_dn, yth_cost, yth_rate, yth_rate_dn = 16155, 266, 31.95, 24.6, 0.7
reg_n, reg_up, reg_cost = 2829, 78, 10.96

# 111 (mother of D1; not delivered)
a, m = closest(reg_cost / cost_all * 100, {'A': 3, 'B': 5, 'C': 8, 'D': 10})
rec('ZJ2017A-111(母题,未收)', a, f'10.96/218.8={reg_cost / cost_all * 100:.2f}%', 'B')
# 112 (not delivered, free)
a, m = closest(key_cost * 1e4 / key_n, {'A': 213, 'B': 286, 'C': 342, 'D': 398})
rec('ZJ2017A-112(未收)', a, f'17.88亿/625={key_cost * 1e4 / key_n:.1f}万元', 'B')
# 113
sh15 = ms_n / fund_all * 100
sh14 = (ms_n - ms_up) / (fund_all - fund_all_up) * 100
a, m = closest(sh15 - sh14, {'A': 2.6, 'B': 3.1, 'C': 3.8, 'D': 4.2})
rec('ZJ2017A-113', a, f'2015年{sh15:.2f}%(材料给41%), 2014年15000/39089={sh14:.2f}%, 差{sh15 - sh14:.2f}个百分点(用41%: {41 - sh14:.2f}); 最接近A', 'A')
# 114
v = (yth_n + yth_dn) / ((yth_rate + yth_rate_dn) / 100)
a, m = closest(v / 1e4, {'A': 5.1, 'B': 5.9, 'C': 6.5, 'D': 6.9})
rec('ZJ2017A-114', a, f'2014年资助{yth_n + yth_dn}项, 资助率{yth_rate + yth_rate_dn:.1f}%, 申请{v:.0f}份; 面上2014申请={(ms_n - ms_up) / ((ms_rate + ms_rate_dn) / 100):.0f}(B陷阱)', 'C')
# 115 能推出
t115 = {'A': key_cost / key_n > major_cost / major_n,
        'B': (ms_n - ms_up) > (yth_n + yth_dn),
        'C': ms_rate > yth_rate,
        'D': key_g > reg_up / (reg_n - reg_up) * 100}
assert [k for k, x in t115.items() if x] == ['D'], t115
rec('ZJ2017A-115', 'D', f'A:重点{key_cost * 1e4 / key_n:.0f}万<重大{major_cost * 1e4 / major_n:.0f}万; B:2014面上{ms_n - ms_up}<青年{yth_n + yth_dn}; C:22.9%<24.6%; D:重点3.3%>地区{reg_up / (reg_n - reg_up) * 100:.2f}%', 'D')


# ---- D1 改编 (variant_of ZJ2017A-111): 除面上、青年外其他各类项目的平均资助率 ----
def d1_val(mr=ms_rate, yr=yth_rate):
    app_ms = ms_n / (mr / 100)
    app_y = yth_n / (yr / 100)
    return (fund_all - ms_n - yth_n) / (app_all - app_ms - app_y) * 100
OPT_D1 = {'A': 19.2, 'B': 22.7, 'C': 23.5, 'D': 23.8}
a, m = closest(d1_val(), OPT_D1)
lo, hi, mm, n = robust_value(d1_val, OPT_D1, 'B', mr=iv(ms_rate, 1), yr=iv(yth_rate, 1))
rec('ZL4B-D1 [ZJ2017A-1 其他项目资助率]', a,
    f'面上申请{ms_n / .229:.0f}, 青年申请{yth_n / .246:.0f}, 其他申请{app_all - ms_n / .229 - yth_n / .246:.0f}, 其他资助{fund_all - ms_n - yth_n}, 资助率{d1_val():.3f}%; '
    f'A=7804/40668={7804 / 40668 * 100:.2f}%; C=总体{fund_all / app_all * 100:.2f}%; D=(22.9+24.6)/2={(22.9 + 24.6) / 2:.2f}%',
    pert=f'{n}组: {lo:.2f}%~{hi:.2f}%, 恒最接近B, 最小余量{mm:.2f}')

# =====================================================================================================
# M8  ZLM-ZJ2020B-2  清洁能源（浙江2020年度B卷 第91—95题；同材料见A卷第91—95题）
# =====================================================================================================
inv17, inv_g, inv15 = 3335, 3, 3485
cn_world, cn_apac = 40, 71
wind_new, wind_new_g, wind_cum17, wind_cum_g = 52.5, -3.8, 539.1, 11
pv_inv, pv_inv_g, pv_new, pv_new_g, pv_cum17 = 1608, 18, 99.1, 29, 404.5
apac_new, apac_cum = 73.7, 221.3
WIND = {2008: 120.7, 2009: 159.1, 2010: 198.0, 2011: 238.1, 2012: 282.9, 2013: 318.7, 2014: 369.9, 2015: 432.7, 2016: 487.3, 2017: 539.1}
PV = {2008: 15.8, 2009: 23.2, 2010: 40.3, 2011: 70.5, 2012: 100.5, 2013: 138.8, 2014: 179.0, 2015: 229.1, 2016: 306.5, 2017: 404.5}

# 91
v = inv17 * cn_world / cn_apac
a, m = closest(v, {'A': 1034, 'B': 1334, 'C': 1879, 'D': 2368})
rec('ZJ2020B-91', a, f'3335×40%/71%={v:.1f}; 3335×40%={inv17 * .4:.0f}(B); 3335×71%={inv17 * .71:.0f}(D)', 'C')
# 92 (mother of H1; not delivered)
yrs = [y for y in range(2009, 2018) if (WIND[y] + PV[y]) - (WIND[y - 1] + PV[y - 1]) > 100]
rec('ZJ2020B-92(母题,未收)', {2: 'A', 3: 'B', 4: 'C', 5: 'D'}[len(yrs)], f'合计增量>100GW的年份{yrs}', 'B')
# 93
d = apac_new / pv_new * 100 - apac_cum / pv_cum17 * 100
a93 = 'D' if d > 10 else ('C' if d > 0 else ('A' if d > -10 else 'B'))
rec('ZJ2020B-93', a93, f'新增占比{apac_new / pv_new * 100:.1f}%, 累计占比{apac_cum / pv_cum17 * 100:.1f}%, 高{d:.1f}个百分点', 'D')
# 94 (not delivered, free): growth rates of PV cumulative 2009-2012
g = [PV[y] / PV[y - 1] - 1 for y in range(2009, 2013)]
rec('ZJ2020B-94(未收)', 'A', '2009—2012年光伏累计装机增速 ' + ', '.join(f'{x * 100:.1f}%' for x in g) + ' → 升、微升、降（图形选项，未收）', 'A')
# 95 可以推出的是
inv16 = inv17 / (1 + inv_g / 100)
t95 = {'A': False,   # 风能投资只有2017年绝对数1070，无增速、无上年数
       'B': True,    # 2016=3335/1.03, 2015=3485 → 2016年增速可求
       'C': False,   # 无亚太地区光伏投资数据
       'D': False}   # 图只从2008年起，无2007年数据
assert [k for k, x in t95.items() if x] == ['B']
rec('ZJ2020B-95', 'B', f'B:2016年={inv16:.1f}亿美元, 同比{(inv16 / inv15 - 1) * 100:.1f}%; A缺上年风能投资或增速; C缺亚太光伏投资; D缺2007年累计装机', 'B')


# ---- H1 改编 (variant_of ZJ2020B-92): 2017年风电+光伏报废装机容量 ----
def h1_val(wn=wind_new, w17=WIND[2017], w16=WIND[2016], pn=pv_new, p17=PV[2017], p16=PV[2016]):
    return (wn - (w17 - w16)) + (pn - (p17 - p16))
OPT_H1 = {'A': 0.7, 'B': 1.1, 'C': 1.8, 'D': 2.5}
a, m = closest(h1_val(), OPT_H1)
lo, hi, mm, n = robust_value(h1_val, OPT_H1, 'C', wn=iv(wind_new, 1), w17=iv(WIND[2017], 1), w16=iv(WIND[2016], 1), pn=iv(pv_new, 1), p17=iv(PV[2017], 1), p16=iv(PV[2016], 1))
rec('ZL4B-H1 [ZJ2020B-2 报废装机]', a,
    f'风电: 新增52.5-(539.1-487.3={WIND[2017] - WIND[2016]:.1f})={wind_new - (WIND[2017] - WIND[2016]):.1f}; 光伏: 99.1-(404.5-306.5={PV[2017] - PV[2016]:.1f})={pv_new - (PV[2017] - PV[2016]):.1f}; 合计{h1_val():.1f}GW',
    pert=f'{n}组: {lo:.2f}~{hi:.2f}, 恒最接近C, 最小余量{mm:.2f}')
# data-coherence note for the material (2016年): 新增 vs 累计差
pv_new16 = pv_new / (1 + pv_new_g / 100); wind_new16 = wind_new / (1 + wind_new_g / 100)
print(f'   [材料自洽性] 2016年: 光伏新增={pv_new16:.1f} vs 累计差{PV[2016] - PV[2015]:.1f}; 风电新增={wind_new16:.1f} vs 累计差{WIND[2016] - WIND[2015]:.1f}')

# =====================================================================================================
# M5  ZLM-GK2016D-3  市场主体（国考2016年度地市级 第121—125题＝副省级 第126—130题）
# =====================================================================================================
stock14, g14, g_up = 6932.22, 14.35, 4.02
cap14, cap_g = 129.23, 27.70
st_ent, st_ind, st_coop = 1819.28, 4984.06, 128.88
new14, new_up, newcap, newcap_up = 1292.5, 160.97, 20.66, 9.66
new_ent, new_ind, new_coop = 365.1, 896.45, 30.95
svc, svc_g = 114.10, 61.41
SVC = {'信息': (14.67, 97.87), '科研': (26.26, 70.32), '文体': (6.59, 83.51), '教育': (0.68, 86.17)}
fdi_n, fdi_n_g, fdi_cap, fdi_cap_g = 3.84, 5.76, 1796.39, 23.87
assert abs(st_ent + st_ind + st_coop - stock14) < 0.01 and abs(new_ent + new_ind + new_coop - new14) < 0.01

# 121
v = stock14 / (1 + g14 / 100) / (1 + (g14 - g_up) / 100)
a, m = closest(v, {'A': 6100, 'B': 5500, 'C': 5100, 'D': 4500})
rec('GK2016D-121', a, f'2013年增速{g14 - g_up:.2f}%; 6932.22/1.1435/1.1033={v:.1f}万户; 只退一年={stock14 / (1 + g14 / 100):.0f}(A陷阱)', 'B')
# 122 (mother of E1) / 123 (mother of E2)
a, m = closest(new_ind / new14 * 100, {'A': 75, 'B': 69, 'C': 85, 'D': 81})
rec('GK2016D-122(母题,未收)', a, f'896.45/1292.5={new_ind / new14 * 100:.1f}%', 'B')
rec('GK2016D-123(母题,未收)', 'D', '增速最快：信息传输、软件和信息技术服务业97.87%', 'D')
# 124
v = ((1 + fdi_cap_g / 100) / (1 + fdi_n_g / 100) - 1) * 100
a, m = closest(v, {'A': 17, 'B': 12, 'C': 8, 'D': 4})
rec('GK2016D-124', a, f'1.2387/1.0576-1={v:.2f}%; 差值23.87-5.76={fdi_cap_g - fdi_n_g:.2f}(偏大)', 'A')
# 125 能推出
t125 = {'A': SVC['教育'][0] / svc > 0.5,
        'B': new_coop / st_coop > 1 / 3,
        'C': cap14 / (1 + cap_g / 100) < 100,
        'D': SVC['科研'][0] / (1 + SVC['科研'][1] / 100) < 20}
assert [k for k, x in t125.items() if x] == ['D'], t125
rec('GK2016D-125', 'D', f'A:教育0.68/114.10={0.68 / 114.10 * 100:.1f}%; B:30.95/128.88={new_coop / st_coop * 100:.1f}%<1/3; C:129.23/1.277={cap14 / 1.277:.1f}>100; D:26.26/1.7032={26.26 / 1.7032:.2f}<20', 'D')


# ---- E1 改编 (variant_of GK2016D-122): 2014年注销(吊销)户数 = 新登记 − 净增 ----
def e1_val(s=stock14, g=g14, nw=new14):
    net = s - s / (1 + g / 100)
    return nw - net
OPT_E1 = {'A': 161, 'B': 298, 'C': 423, 'D': 870}
a, m = closest(e1_val(), OPT_E1)
lo, hi, mm, n = robust_value(e1_val, OPT_E1, 'C', s=iv(stock14, 2), g=iv(g14, 2), nw=iv(new14, 1))
rec('ZL4B-E1 [GK2016D-3 存量与流量]', a,
    f'2013年末实有{stock14 / 1.1435:.2f}, 净增{stock14 - stock14 / 1.1435:.2f}, 注销=1292.5-净增={e1_val():.2f}万户; B=1292.5-6932.22×14.35%={new14 - stock14 * g14 / 100:.1f}; A=160.97; D=净增',
    pert=f'{n}组: {lo:.1f}~{hi:.1f}, 恒最接近C, 最小余量{mm:.1f}')


# ---- E2 改编 (variant_of GK2016D-123): 其余现代服务业企业增速（混合增速） ----
def e2_val(tot=svc, tg=svc_g, **kw):
    parts = {k: (kw.get('x_' + k, v[0]), kw.get('g_' + k, v[1])) for k, v in SVC.items()}
    now = tot - sum(x for x, _ in parts.values())
    prev = tot / (1 + tg / 100) - sum(x / (1 + g / 100) for x, g in parts.values())
    return (now / prev - 1) * 100
OPT_E2 = {'A': 50, 'B': 66, 'C': 75, 'D': 84}
a, m = closest(e2_val(), OPT_E2)
ivs = dict(tot=iv(svc, 2), tg=iv(svc_g, 2))
for k, (x, g) in SVC.items():
    ivs['x_' + k] = iv(x, 2)
lo, hi, mm, n = robust_value(e2_val, OPT_E2, 'A', **ivs)
assert all(g > svc_g for _, g in SVC.values())          # 四个行业增速都高于整体 → 其余部分必低于整体
assert [k for k, v in OPT_E2.items() if v < svc_g] == ['A']   # 选项中只有A低于61.41%
prev_tot = svc / (1 + svc_g / 100); prev4 = sum(x / (1 + g / 100) for x, g in SVC.values())
rec('ZL4B-E2 [GK2016D-3 其余行业增速]', a,
    f'其余2014={svc - sum(x for x, _ in SVC.values()):.2f}万户, 2013={prev_tot:.3f}-{prev4:.3f}={prev_tot - prev4:.3f}万户, 增速{e2_val():.2f}%; 四行业增速均>61.41%→其余<61.41%, 选项仅A满足',
    pert=f'{n}组: {lo:.2f}%~{hi:.2f}%, 恒最接近A')

# =====================================================================================================
# M7  ZLM-JS2018A-3  汽车保有量与驾驶人（江苏2018年度A类 第116—120题）
# =====================================================================================================
car, car_g, pcar, pcar_g = 21743, 11.8, 18695, 12.9
sedan, sedan_g, psedan, psedan_g = 12185, 12.0, 11416, 12.5
nev, nev_new, nev_new_up = 153.0, 65.0, 15.6
east, mid, west = 15544, 9006, 6436
west_inc, west_r, east_r, mid_r = 1963, 19.3, 14.6, 16.7
drv, drv_avg_inc, car_drv_min = 3.85, 2467, 3.42
male, male_sh, female, female_sh, female_sh_up = 2.74, 71.2, 1.11, 28.8, 1.6

# 116 (mother of G3), 117 (mother of G2)
a, m = closest(psedan / (1 + psedan_g / 100), {'A': 10148, 'B': 11006, 'C': 13879, 'D': 16559})
rec('JS2018A-116(母题,未收)', a, f'11416/1.125={psedan / 1.125:.0f}', 'A')
a, m = closest(nev_new / nev * 100, {'A': 35.0, 'B': 42.5, 'C': 49.1, 'D': 55.2})
rec('JS2018A-117(母题,未收)', a, f'65.0/153.0={nev_new / nev * 100:.1f}%', 'B')
# 118 公式题: x*(1.193^5-1)=1963
x = west_inc / (1.193 ** 5 - 1)
forms = {'A': west_inc / (1 + 0.193 ** 5), 'B': west_inc / (1.193 ** 5 + 1), 'C': west_inc / (1.193 ** 5 - 1), 'D': west_inc / (1 - 0.193 ** 5)}
ok = [k for k, v in forms.items() if abs(v * 1.193 ** 5 - v - west_inc) < 1e-6]
assert ok == ['C']
rec('JS2018A-118', 'C', f'2012年末x满足 x×1.193^5-x=1963 → x=1963/(1.193^5-1)={x:.1f}万辆; 各式值 ' + ', '.join(f'{k}={v:.0f}' for k, v in forms.items()), 'C')
# 119
need = male * 0.30 / 0.70 - female
a, m = closest(need * 1e4, {'A': 462, 'B': 643, 'C': 963, 'D': 1099})
lo119 = (iv(male, 2)[0] * 3 / 7 - iv(female, 2)[1]) * 1e4; hi119 = (iv(male, 2)[1] * 3 / 7 - iv(female, 2)[0]) * 1e4
assert closest(lo119, {'A': 462, 'B': 643, 'C': 963, 'D': 1099})[0] == 'B' and closest(hi119, {'A': 462, 'B': 643, 'C': 963, 'D': 1099})[0] == 'B'
rec('JS2018A-119', a, f'男性不少于2.74亿且占比≤70% → 女性≥2.74×3/7={male * 3 / 7:.4f}亿, 至少增加{need * 1e4:.0f}万; (0.30-0.288)×3.85亿={0.012 * 3.85 * 1e4:.0f}万(A陷阱); 原数取整区间{lo119:.0f}~{hi119:.0f}万仍最接近B', 'B')
# 120 不能推出
t120b = {'A': abs((nev_new - nev_new_up) - 49.4) < 1e-9,      # 能推出
         'B': east + mid + west == 30986,                      # 能推出
         'C': sedan_g > car_g,                                  # 能推出
         'D': False}                                            # 只有西部的增量，东、中部2012年基数未知 → 全国年均增速求不出
assert [k for k, x in t120b.items() if not x] == ['D']
# feasible range of national CAGR (shows 16.9% is neither derivable nor excluded)
w12 = x; w17 = x * 1.193 ** 5; ec17 = car - w17
lo_c = ((car / (w12 + ec17 / 1.146 ** 5)) ** 0.2 - 1) * 100; hi_c = ((car / (w12 + ec17 / 1.167 ** 5)) ** 0.2 - 1) * 100
rec('JS2018A-120', 'D', f'A:65.0-15.6={nev_new - nev_new_up:.1f}; B:15544+9006+6436={east + mid + west}; C:12.0%>11.8%; D:东、中部基数未知, 全国年均增速只能定在{lo_c:.1f}%~{hi_c:.1f}%之间, 16.9%=(19.3+14.6+16.7)/3 是简单平均, 推不出', 'D')


# ---- G3 改编 (variant_of JS2018A-116): 2017年末驾驶人比2012年末增长 ----
def g3_val(d=drv, inc=drv_avg_inc):
    tot_inc = 5 * inc / 1e4          # 亿人
    return tot_inc / (d - tot_inc) * 100
OPT_G3 = {'A': 9.4, 'B': 32.0, 'C': 34.5, 'D': 47.1}
a, m = closest(g3_val(), OPT_G3)
lo, hi, mm, n = robust_value(g3_val, OPT_G3, 'D', d=iv(drv, 2), inc=iv(drv_avg_inc, 0))
rec('ZL4B-G3 [JS2018A-3 五年累计增长]', a,
    f'五年共增{5 * drv_avg_inc / 1e4:.4f}亿人, 2012年末{drv - 5 * drv_avg_inc / 1e4:.4f}亿人, 增长{g3_val():.2f}%; A={drv_avg_inc / 1e4 / (drv - 5 * drv_avg_inc / 1e4) * 100:.1f}%; B={5 * drv_avg_inc / 1e4 / drv * 100:.1f}%; C={4 * drv_avg_inc / 1e4 / (drv - 4 * drv_avg_inc / 1e4) * 100:.1f}%',
    pert=f'{n}组: {lo:.2f}%~{hi:.2f}%, 恒最接近D, 最小余量{mm:.2f}')


# ---- G2 改编 (variant_of JS2018A-117): 新能源汽车保有量增长（不考虑报废注销） ----
def g2_val(s=nev, nw=nev_new):
    return nw / (s - nw) * 100
OPT_G2 = {'A': 31.6, 'B': 42.5, 'C': 73.9, 'D': 135.4}
a, m = closest(g2_val(), OPT_G2)
lo, hi, mm, n = robust_value(g2_val, OPT_G2, 'C', s=iv(nev, 1), nw=iv(nev_new, 1))
rec('ZL4B-G2 [JS2018A-3 时点与时期]', a,
    f'2016年末=153.0-65.0={nev - nev_new:.1f}万辆, 增长65.0/88.0={g2_val():.2f}%; A=15.6/49.4={15.6 / 49.4 * 100:.1f}%; B=65/153={65 / 153 * 100:.1f}%; D=153/65-1={(153 / 65 - 1) * 100:.1f}%',
    pert=f'{n}组: {lo:.2f}%~{hi:.2f}%, 恒最接近C, 最小余量{mm:.2f}')

# =====================================================================================================
# M6  ZLM-JS2016A-1  2015年1~7月出口（江苏2016年度A卷 第116—120题）
# =====================================================================================================
mech, mech_g, mech_sh = 44359.4, 1.2, 57.2
elec, elec_g, mach, mach_g = 19373.1, 4.1, 12865.6, -6.6
LAB = {'服装': (5709.9, -6.4), '纺织品': (3825.5, -1.7), '鞋类': (1901.7, -1.9), '家具': (1883.7, 7.6),
       '塑料制品': (1293.3, 2.3), '箱包': (998.9, 8.0), '玩具': (465.0, 11.0)}
lab_g = -1.3
QP = {'塑料制品': (2.9, 2.3), '箱包': (-3.8, 8.0), '肥料': (54.7, 62.7), '钢材': (26.6, -2.6), '汽车': (-13.6, -4.5)}   # (量增速, 额增速)
steel_v, steel_g, auto_v, auto_g, fert_v = 2319.5, -2.6, 411.0, -4.5, 366.1

def dec_amt(v, g):       # 同比减少额（g为负）
    return v / (1 + g / 100) - v

# 116 (mother of F2), 119 (not delivered)
a, m = closest(mech / (mech_sh / 100), {'A': 63534.0, 'B': 77551.4, 'C': 82907.1, 'D': 95772.7})
rec('JS2016A-116(母题,未收)', a, f'44359.4/57.2%={mech / .572:.1f}', 'B')
a, m = closest(sum(v for v, _ in LAB.values()), {'A': 13576.1, 'B': 14087.2, 'C': 16078.0, 'D': 18079.3})
rec('JS2016A-119(未收)', a, f'7类合计={sum(v for v, _ in LAB.values()):.1f}', 'C')
# 117 同比下降最多（减少额）
dd = {'A': dec_amt(mach, mach_g), 'B': dec_amt(*LAB['服装']), 'C': dec_amt(steel_v, steel_g), 'D': dec_amt(auto_v, auto_g)}
a = max(dd, key=dd.get)
rr = {'A': mach_g, 'B': LAB['服装'][1], 'C': steel_g, 'D': auto_g}
assert min(rr, key=rr.get) == 'A'        # 按降幅读也是A
rec('JS2016A-117', a, '减少额(亿元): ' + ', '.join(f'{k}={v:.1f}' for k, v in dd.items()) + '; 按降幅也是机械设备(-6.6%)', 'A')
# 118 原题（口径两可，不收原题；F1的母题）
pg = {k: ((1 + e / 100) / (1 + q / 100) - 1) * 100 for k, (q, e) in QP.items()}
price_now = {'塑料制品': 1293.3 / 553.7, '箱包': 998.9 / 166.9, '肥料': 366.1 / 1957.3, '汽车': 411.0 / 44.5}   # 亿元/万吨(万辆)=万元/吨(辆)
rise_abs = {k: price_now[k] - price_now[k] / (1 + pg[k] / 100) for k in price_now}
print('   [JS2016A-118 原题两种口径] 涨幅%: ' + ', '.join(f'{k}={v:.2f}' for k, v in pg.items()) + ' | 上涨额(万元/吨或辆): ' + ', '.join(f'{k}={v:.4f}' for k, v in rise_abs.items()))
R['JS2016A-118(母题,原题口径两可,未收)'] = dict(ans='按涨幅B/按上涨额D', detail='原参考答案D按“上涨额”且跨吨、辆比较；按涨幅为箱包(B)', src='D', pert=None)
# 120 判断不正确（D项口径明示为“合计同比”）
toy14 = 465.0 / 1.11
inc_cnt = sum(1 for _, g in LAB.values() if g > 0)
mix = ((elec + mach) / (elec / (1 + elec_g / 100) + mach / (1 + mach_g / 100)) - 1) * 100
t120c = {'A': toy14 < 422, 'B': QP['肥料'][0] > 50 and QP['肥料'][1] > 50, 'C': inc_cnt > len(LAB) / 2, 'D': abs(mix - (-1.3)) < 0.05}
wrong = [k for k, ok_ in t120c.items() if not ok_]
assert wrong == ['D'], t120c
rec('JS2016A-120', 'D', f'A:465.0/1.11={toy14:.1f}<422 ✓; B:54.7%、62.7%均>50% ✓; C:7类中{inc_cnt}类增长 ✓; D:两类合计同比{mix:.2f}%≠-1.3%(简单平均{(elec_g + mach_g) / 2:.2f}%) ✗', 'D')
# robustness of 120 under rounding (original, for the record)
for kw in grid(eg=iv(elec_g, 1), mg=iv(mach_g, 1), tg=iv(11.0, 1)):
    mx = ((elec + mach) / (elec / (1 + kw['eg'] / 100) + mach / (1 + kw['mg'] / 100)) - 1) * 100
    assert mx > -0.6 and 465.0 / (1 + kw['tg'] / 100) < 422


# ---- F1 改编 (variant_of JS2016A-118): 平均出口价格同比涨幅最大 ----
def f1_rank(**kw):
    out = {}
    for k in ('塑料制品', '箱包', '肥料', '汽车'):
        q = kw.get('q_' + k, QP[k][0]); e = kw.get('e_' + k, QP[k][1])
        out[k] = ((1 + e / 100) / (1 + q / 100) - 1) * 100
    return out
OPT_F1 = {'A': '塑料制品', 'B': '箱包', 'C': '肥料', 'D': '汽车'}
base = f1_rank()
best = max(base, key=base.get)
assert best == '箱包'
ivs = {}
for k in ('塑料制品', '箱包', '肥料', '汽车'):
    ivs['q_' + k] = iv(QP[k][0], 1); ivs['e_' + k] = iv(QP[k][1], 1)
n = 0; gap = None
for kw in grid(**ivs):
    r_ = f1_rank(**kw)
    assert max(r_, key=r_.get) == '箱包', kw
    g_ = r_['箱包'] - max(v for k, v in r_.items() if k != '箱包')
    gap = g_ if gap is None else min(gap, g_); n += 1
rec('ZL4B-F1 [JS2016A-1 出口均价涨幅]', 'B', '单价同比: ' + ', '.join(f'{k}{v:+.2f}%' for k, v in base.items()) + f'; 钢材{pg["钢材"]:+.2f}%',
    pert=f'{n}组: 箱包恒为最大, 领先第二名至少{gap:.2f}个百分点')


# ---- F2 改编 (variant_of JS2016A-116): 机电产品中其他产品出口额同比增量 ----
def f2_val(tg=mech_g, eg=elec_g, mg=mach_g):
    inc_t = mech - mech / (1 + tg / 100)
    inc_e = elec - elec / (1 + eg / 100)
    inc_m = mach - mach / (1 + mg / 100)
    return inc_t - inc_e - inc_m
def f2_bucket(v):
    """选项为区间：A 减少200亿元以上；B 增加不到550亿元；C 增加550亿~600亿元；D 增加600亿元以上"""
    if v <= -200: return 'A'
    if 0 < v < 550: return 'B'
    if 550 <= v <= 600: return 'C'
    if v > 600: return 'D'
    return None
inc_t = mech - mech / 1.012; inc_e = elec - elec / 1.041; inc_m = mach - mach / 0.934
other15 = mech - elec - mach
wrong_paths = {'漏掉机械设备': inc_t - inc_e, '只取整体增量': inc_t, '现期×增速': mech * .012 - elec * .041 + mach * .066}
assert [f2_bucket(v) for v in wrong_paths.values()] == ['A', 'B', 'C'], wrong_paths
assert f2_bucket(f2_val()) == 'D'
lo = hi = None; n = 0
for kw in grid(tg=iv(mech_g, 1), eg=iv(elec_g, 1), mg=iv(mach_g, 1)):
    v = f2_val(**kw); assert f2_bucket(v) == 'D', (kw, v)
    lo = v if lo is None else min(lo, v); hi = v if hi is None else max(hi, v); n += 1
rec('ZL4B-F2 [JS2016A-1 机电其他产品增量]', 'D',
    f'机电增量{inc_t:.1f}, 电器{inc_e:+.1f}, 机械{inc_m:+.1f} → 其他{f2_val():+.1f}亿元(其他2015年={other15:.1f}, 增速{f2_val() / (other15 - f2_val()) * 100:.2f}%); '
    + '; '.join(f'{k}={v:.1f}→{f2_bucket(v)}' for k, v in wrong_paths.items()),
    pert=f'{n}组: {lo:.0f}~{hi:.0f}亿元, 恒落在D(600亿元以上), 距边界至少{lo - 600:.0f}亿元')

# =====================================================================================================
json.dump(R, open(f'{SP}/verify_results.json', 'w'), ensure_ascii=False, indent=1)
print()
print(len(R), 'entries;', 'FAIL:', FAIL)

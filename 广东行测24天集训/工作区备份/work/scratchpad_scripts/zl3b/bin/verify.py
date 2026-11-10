"""ZL3B independent verification: every question re-solved from the material numbers.
For computed-value questions: pick the option closest to the computed value (and check the margin).
For judgement questions: evaluate every option's truth separately and require exactly one correct choice.
Adaptations: same, plus rounding-robustness checks (perturb the material's rounded figures)."""
import itertools, math
R = {}   # id -> dict(ans=..., detail=...)

def closest(val, opts):
    d = {k: abs(v - val) for k, v in opts.items()}
    s = sorted(d, key=d.get)
    return s[0], d[s[0]], d[s[1]]

def rec(key, ans, detail, src=None):
    R[key] = dict(ans=ans, detail=detail, src=src)
    flag = '' if (src is None or src == ans) else '  <-- MISMATCH vs source ' + str(src)
    print(f'{key}: {ans}  | {detail}{flag}')

# ============ M1 ZLM-GD2014X-1 广东经济发展 ============
world, china, gd = 2.8, 9.8, 13.3
gdp_gd = 29319.97 / 0.514          # 民营经济 51.4%
tax = 6467.82 / 0.491              # 税金 49.1%
inv = 10177.28 / 0.527             # 民间投资 52.7%
# Q86 (mother of adaptation; not delivered as original)
a, d1, d2 = closest(gd / world, {'A': 1.4, 'B': 3.5, 'C': 4.8, 'D': 10.5})
rec('GD2014X-86(orig, replaced)', a, f'13.3/2.8={gd/world:.3f}; 9.8/2.8={china/world:.2f}(B trap)', 'C')
# Q87
a, d1, d2 = closest(tax, {'A': 12273, 'B': 13173, 'C': 19312, 'D': 57043})
rec('GD2014X-87', a, f'tax total={tax:.1f}; investment total={inv:.1f}(C); GDP={gdp_gd:.1f}(D)', 'B')
# Q88
g88 = 5524 / 5049 - 1
a, d1, d2 = closest(g88 * 100, {'A': 9.4, 'B': 109.4, 'C': 270, 'D': 370})
rec('GD2014X-88', a, f'5524/5049-1={g88*100:.2f}%  (B=ratio 109.4% trap)', 'B' if False else 'A')
# Q89: 1978 values (km) = 2012 / (1 + times)
rail = 2577 / 2.6; road = 19.5e4 / 3.7; air = 185.1e4 / 89.1; pipe = 6448.01 / 83.7
v = {'管道': pipe, '铁路': rail, '民航': air, '公路': road}
order = sorted(v, key=v.get)
opts89 = {'A': ['管道', '铁路', '民航', '公路'], 'B': ['管道', '铁路', '公路', '民航'],
          'C': ['民航', '公路', '管道', '铁路'], 'D': ['民航', '公路', '铁路', '管道']}
a = [k for k, o in opts89.items() if o == order]
rec('GD2014X-89', a[0], f'1978 km: ' + ', '.join(f'{k}={v[k]:.1f}' for k in order), 'A')
# Q90 (不正确)
t90 = {'A': 0.527 > 0.5,
       'B': 14.08 / 50.5 < 14.08,
       'C': 22396.35 / 56.0 > 7458.56 / 40.3,
       'D': (34.4 - 27.3) > (31.67 - 22.9)}
wrong = [k for k, ok in t90.items() if not ok]
assert len(wrong) == 1
rec('GD2014X-90', wrong[0], f'C:城镇1978={22396.35/56:.1f} 农村={7458.56/40.3:.1f}; D:城镇{34.4-27.3:.1f} vs 农村{31.67-22.9:.2f} m2', 'D')

# ---- A1 adaptation (variant_of GD2014X-86) 可以判断属实 ----
def a1_truth(gd_share_pct=51.4, priv=29319.97, gd_rate=13.3, cn_rate=9.8):
    gdp = priv / (gd_share_pct / 100)
    nat_max = gdp * 10      # share >= 1/10
    return {
        'A': False,                       # 2011年首次突破5000公里（2012年5524），"2012年首次突破"与原文不符
        'B': abs((1 + 49.5) - 49.5) < 1e-9 and False,   # 增长49.5倍 -> 是1978年的50.5倍，不是49.5倍
        'C': nat_max <= 580000,           # 全国GDP <= 10 x 广东GDP <= 58万亿元
        'D': gd_rate / cn_rate >= 1.5,    # 13.3/9.8 = 1.357
    }
base = a1_truth()
assert [k for k, t in base.items() if t] == ['C'], base
# robustness: 51.4% in [51.35, 51.45), 13.3/9.8 rounding
for s in (51.35, 51.45):
    for g in (13.25, 13.35):
        for c in (9.75, 9.85):
            tt = a1_truth(s, 29319.97, g, c)
            assert [k for k, t in tt.items() if t] == ['C'], (s, g, c, tt)
rec('ZL3B-A1 (GD2014X-1 属实)', 'C', f'广东GDP={gdp_gd:.1f}亿元, 全国<=10x={gdp_gd*10/1e4:.2f}万亿元(<=58); 全国>=8x={gdp_gd*8/1e4:.2f}万亿元; 13.3/9.8={13.3/9.8:.3f}; 港口50.5倍; 高速2011年首次破5000')

# ============ M2 ZLM-GD2016Z-1 新农村示范片 ============
r86 = 821 / 1711
a, d1, d2 = closest(r86 * 100, {'A': 47, 'B': 48, 'C': 49, 'D': 50})
rec('GD2016Z-86', a, f'821/1711={r86*100:.2f}% ; 1539/2693={1539/2693*100:.2f}%(启动口径)', 'B')
v87 = 391 * 0.670
a, d1, d2 = closest(v87, {'A': 256, 'B': 262, 'C': 267, 'D': 273})
rec('GD2016Z-87', a, f'391x67.0%={v87:.1f}; 386x67%={386*0.67:.1f}; 首批硬底化256(A)', 'B')
gaps = {'A': 100 - 79.5, 'B': 95.2 - 79.3, 'C': 86.9 - 67.0, 'D': 99.7 - 98.2}
a = max(gaps, key=gaps.get)
rec('GD2016Z-89', a, 'gaps(自然村)=' + str({k: round(x, 1) for k, x in gaps.items()}) + f'; 若误用行政村:100-93.2={100-93.2:.1f}', 'A')
t90 = {'A': 1539 > 1154, 'B': 821 / 1539 < 890 / 1154, 'C': 391 * 0.982 < 375 * 0.997, 'D': 64 > 55}
wrong = [k for k, ok in t90.items() if not ok]
assert len(wrong) == 1
rec('GD2016Z-90', wrong[0], f'竣工率 粤东西北{821/1539*100:.1f}% 珠三角{890/1154*100:.1f}%; 理事会 第二批{391*0.982:.1f} 首批{375*0.997:.1f}', 'C')

# ============ M3 ZLM-GD2015X-2 汽车产销 ============
a, d1, d2 = closest(2107.7 / 2349 * 100, {'A': 89.7, 'B': 88.9, 'C': 73.4, 'D': 67.5})
rec('GD2015X-91', a, f'2107.7/2349={2107.7/2349*100:.2f}%; /产量2372={2107.7/2372*100:.2f}%(B trap)', 'A')
pc13 = 1970 / 1.0989; cv13 = 379 / (1 - 0.065)
a, d1, d2 = closest(pc13 / cv13, {'A': 4.0, 'B': 4.4, 'C': 5.0, 'D': 5.2})
rec('GD2015X-92', a, f'2013 乘用车={pc13:.1f} 商用车={cv13:.1f} 比={pc13/cv13:.3f}; 2014现期比={1970/379:.3f}(D trap)', 'B')
chg = {'轿车': 3.1, 'SUV': 36.4, 'MPV': 46.8, '交叉型': -18.1}
abs_order = sorted(chg, key=lambda k: -abs(chg[k])); sgn_order = sorted(chg, key=lambda k: -chg[k])
opts93 = {'A': ['MPV', 'SUV', '交叉型', '轿车'], 'B': ['SUV', '轿车', 'MPV', '交叉型'],
          'C': ['SUV', '交叉型', '轿车', 'MPV'], 'D': ['MPV', 'SUV', '轿车', '交叉型']}
a_abs = [k for k, o in opts93.items() if o == abs_order][0]; a_sgn = [k for k, o in opts93.items() if o == sgn_order][0]
rec('GD2015X-93', a_abs, f'按绝对值:{abs_order}->{a_abs}; 若带符号:{sgn_order}->{a_sgn} (题干须明示口径)', 'A')
# Q95 正确
prod13 = 2372 / 1.073; sale13 = 2349 / 1.069
nev13 = 7.5 / 4.24
cn13_share = 38.4 + 2.1
pc13_ = 1970 / 1.0989
cn13 = 757 / 1.041
de_max = 0.20 * pc13_    # 德系2013占有率低于20%（今年上升）
jp13 = 0.1634 * pc13_    # 日系2013 ≈16.34%（下降0.34个百分点的读法）；若按相对0.34%：16/0.9966=16.05%
t95 = {'A': prod13 < sale13, 'B': False, 'C': nev13 < 2, 'D': cn13 < de_max + jp13}
right = [k for k, ok in t95.items() if ok]
assert right == ['C'], t95
rec('GD2015X-95', 'C', f'2013产{prod13:.1f}>销{sale13:.1f}; 客车+8.4%; 新能源2013={nev13:.3f}万; 中国品牌2013={cn13:.1f} vs 德+日<{de_max+jp13:.1f}', 'C')

# ---- A2 adaptation (variant_of GD2015X-94) 可以判断属实 ----
def a2_truth(tot=2349, rt=6.9, top=2107.7, rtop=8.9, sedan_sh=62.8, sedan_dn=4.2,
             cn_sedan=277, cn_pc=757, phev=3.0, rphev=878, bev=4.5, rbev=208):
    rest14 = tot - top
    rest13 = tot / (1 + rt / 100) - top / (1 + rtop / 100)
    inc_phev = phev - phev / (1 + rphev / 100)
    inc_bev = bev - bev / (1 + rbev / 100)
    return {
        'A': cn_sedan / cn_pc > 0.40,              # 中国品牌轿车占中国品牌乘用车 > 四成？ 36.6%
        'B': (sedan_sh + sedan_dn) < 60,           # 2013年轿车占乘用车 < 60%？ 67.0%
        'C': inc_phev > inc_bev,                   # 插电式增量 > 纯电动增量？
        'D': rest14 < rest13,                      # 前十以外企业集团销量同比下降？
    }, dict(rest14=rest14, rest13=rest13, inc_phev=inc_phev, inc_bev=inc_bev)
t, info = a2_truth()
assert [k for k, x in t.items() if x] == ['D'], t
for rt, rtop, phev, bev in itertools.product((6.85, 6.95), (8.85, 8.95), (2.95, 3.05), (4.45, 4.55)):
    tt, _ = a2_truth(rt=rt, rtop=rtop, phev=phev, bev=bev)
    assert [k for k, x in tt.items() if x] == ['D'], (rt, rtop, phev, bev, tt)
rec('ZL3B-A2 (GD2015X-2 属实)', 'D', f"其余集团2014={info['rest14']:.1f} 2013={info['rest13']:.1f} ({(info['rest14']/info['rest13']-1)*100:.1f}%); 轿车2013占比={62.8+4.2:.1f}%(核:{1238/1.031/(1970/1.0989)*100:.1f}%); 中国品牌轿车/中国品牌乘用车={277/757*100:.1f}%; 增量 插电{info['inc_phev']:.2f} 纯电{info['inc_bev']:.2f}")

# ============ M4 ZLM-JS2025A-1 中国制造75年 ============
gdp23 = 39.9 / 0.317
a, d1, d2 = closest(gdp23 * 0.262, {'A': 27.4, 'B': 30.1, 'C': 33.0, 'D': 36.7})
rec('JS2025A-116', a, f'GDP={gdp23:.2f}万亿, 制造业={gdp23*0.262:.2f}; 39.9x26.2/31.7... ; 误把39.9当GDP:{39.9*0.262:.2f}', 'C')
v117 = (33.6 - 5.4) - (15.7 - 6.3)
a, d1, d2 = closest(v117, {'A': 14.8, 'B': 18.8, 'C': 19.2, 'D': 19.8})
rec('JS2025A-117', a, f'2012: 装备{33.6-5.4:.1f} 高技术{15.7-6.3:.1f} 差{v117:.1f}; 2023差{33.6-15.7:.1f}', 'B')
v118 = 3011.3 / 1.093 - 944.3 / 1.303
a, d1, d2 = closest(v118, {'A': 1854.2, 'B': 1891.1, 'C': 2030.4, 'D': 2067.0})
rec('JS2025A-118', a, f'2022 非新能源={v118:.1f}; 2023非新能源={3011.3-944.3:.1f}(D trap)', 'C')
inc = {'A': (10000 - 1621) / 14, 'B': (107000 - 1621) / 29, 'C': (209000 - 1621) / 34, 'D': (399000 - 1621) / 45}
a = max(inc, key=inc.get)
rec('JS2025A-119', a, 'avg incr(亿元/年)=' + str({k: round(x) for k, x in inc.items()}), 'D')
t120 = {'A': 9.7e8 / 898 < 110e4, 'B': False, 'C': False, 'D': False}
# B: 年均5.7%是2013-2023，不能推出2018-2023；C: 四成以上 => 多于200种，不是"近200"; D: 化肥9522倍 > 水泥3064倍
assert [k for k, x in t120.items() if x] == ['A']
rec('JS2025A-120', 'A', f'1949平板玻璃={9.7e8/898/1e4:.1f}万重量箱(<110); 500x40%=200; 化肥9522>粗钢6449>水泥3064', 'A')

# ============ M5 ZLM-GK2013-3 上市公司一季报 ============
v126 = 4572.78 / 0.88 / 534
a, d1, d2 = closest(v126, {'A': 0.63, 'B': 7.54, 'C': 8.56, 'D': 9.73})
rec('GK2013-126', a, f'Q4={4572.78/0.88:.1f}, /534={v126:.3f}; Q1均={4572.78/534:.2f}(C); x0.88/534={4572.78*0.88/534:.2f}(B); 336.7/534={336.7/534:.2f}(A)', 'D')
v128 = (2892.18 - 2892.18 / 1.10) / 25
a, d1, d2 = closest(v128, {'A': 5, 'B': 11, 'C': 51, 'D': 105})
rec('GK2013-128', a, f'per-company incr={v128:.2f}; base per company={2892.18/1.1/25:.1f}(D); 2892.18x10%/25={2892.18*0.1/25:.2f}', 'B')
v129 = -3.77 / (493.39 / 0.8) * 100
a, d1, d2 = closest(v129, {'A': 2.57, 'B': 1.80, 'C': -0.96, 'D': -0.61})
rec('GK2013-129', a, f'Q4 rev={493.39/0.8:.1f}, margin={v129:.3f}%; 用x0.8:{-3.77/(493.39*0.8)*100:.3f}%(C); Q1 margin={12.65/493.39*100:.2f}%(A)', 'D')
t130 = {'A': False,  # 净利润环比下降25%
        'B': 73.25 / 336.7 > 0.25,
        'C': 322 / 6 > 6167.68 / 534,
        'D': 15.90 / 4 > 4572.78 / 534}
assert [k for k, x in t130.items() if x] == ['C'], t130
rec('GK2013-130', 'C', f'中小板占{73.25/336.7*100:.1f}%; 钢铁均存货{322/6:.1f} vs {6167.68/534:.2f}; 建机均收入{15.90/4:.3f} vs {4572.78/534:.2f}', 'C')
# ---- A4 adaptation (variant_of GK2013-130) 可以判断属实 ----
def a4_truth(rev_yoy=30.74, np_yoy=30.52, np_qoq=-25.0):
    q4_2010 = 336.7 / (1 + np_qoq / 100)
    q1_2010 = 336.7 / (1 + np_yoy / 100)
    m11 = 336.7 / 4572.78
    m10 = (336.7 / (1 + np_yoy / 100)) / (4572.78 / (1 + rev_yoy / 100))
    return {
        'A': False,                 # 30.74%只覆盖已公布一季报的534家，不能代表沪深两市全部上市公司
        'B': q4_2010 > q1_2010,     # 2010Q4净利润（环比基期） > 2010Q1净利润（同比基期）
        'C': False,                 # 存货是“较上年年末增长10%”，不是同比
        'D': m10 < m11,             # 2010Q1净利润率 < 2011Q1？
    }, dict(q4=q4_2010, q1=q1_2010, m10=m10, m11=m11)
t, info = a4_truth()
assert [k for k, x in t.items() if x] == ['B'], t
for ry, ny, nq in itertools.product((30.735, 30.745), (30.515, 30.525), (-25.05, -24.95)):
    tt, _ = a4_truth(ry, ny, nq)
    assert [k for k, x in tt.items() if x] == ['B'], (ry, ny, nq, tt)
rec('ZL3B-A4 (GK2013-3 属实)', 'B', f"2010Q4净利润={info['q4']:.1f} 2010Q1={info['q1']:.1f}; 净利润率2010Q1={info['m10']*100:.3f}% 2011Q1={info['m11']*100:.3f}%")
# 127 (dropped as light) for the record
a, d1, d2 = closest((73.25 / 202) / (13.16 / 71), {'A': 2, 'B': 3, 'C': 4, 'D': 5})
rec('GK2013-127(not delivered)', a, f'{(73.25/202)/(13.16/71):.3f}', 'A')

# ============ M6 ZLM-ZJ2016A-2 国有企业 ============
a, d1, d2 = closest(103155.5 / 0.94 / 1e4, {'A': 10.5, 'B': 11, 'C': 11.5, 'D': 12})
rec('ZJ2016A-116(orig, replaced)', a, f'{103155.5/0.94:.1f}', 'B')
tot, items = -5.1, {'销售': -2.9, '管理': 2.3, '财务': 7.3}
n_up = sum(1 for x in items.values() if x > tot)
a = {0: 'A', 1: 'B', 2: 'C', 3: 'D'}[n_up]
rec('ZJ2016A-117', a, f'{n_up} items grow faster than total(-5.1%)', 'D')
s15 = 191354.4 / 369109.1; s14 = (191354.4 / 1.107) / (369109.1 / 1.122)
dd = (s15 - s14) * 100
a, d1, d2 = closest(dd, {'A': -0.7, 'B': -1.5, 'C': 0.7, 'D': 1.5})
rec('ZJ2016A-118', a, f'share15={s15*100:.2f}% share14={s14*100:.2f}% diff={dd:.2f}pp', 'A')
lr = 363304 / 554658.3
a = 'A' if lr < .5 else 'B' if lr < .6 else 'C' if lr < .7 else 'D'
rec('ZJ2016A-119', a, f'中央资产负债率={lr*100:.2f}%', 'C')
t120 = {'A': 60216.5 < 63191.3 and 40129 < 39964.2,
        'B': (9383 / 1.0013) / (103155.5 / 0.94) >= 0.10,
        'C': 1054875.4 * 0.12 / 1.12 < 120000,
        'D': (322462.3 / 500217.1) > (322462.3 / 1.137) / (500217.1 / 1.138)}
assert [k for k, x in t120.items() if x] == ['C'], t120
rec('ZJ2016A-120', 'C', f'B:{(9383/1.0013)/(103155.5/0.94)*100:.2f}%; C:资产增量={1054875.4*0.12/1.12/1e4:.2f}万亿; D:地方负债率 15={322462.3/500217.1*100:.3f}% 14={(322462.3/1.137)/(500217.1/1.138)*100:.3f}%', 'C')

# ---- A3 adaptation (variant_of ZJ2016A-116) 可以判断属实 ----
def a3_truth(profit=4997.3, rp=8.0, rev=103155.5, rr=6.0, rc=63191.3, rrc=7.0):
    dprofit = profit / (1 - rp / 100) - profit
    sh15 = rc / rev; sh14 = (rc / (1 - rrc / 100)) / (rev / (1 - rr / 100))
    return {
        'A': False,           # 3月当月同比：材料只给1~3月累计，无法判断
        'B': dprofit > 400,   # 利润同比减少超过400亿元
        'C': False,           # 销售费用同比下降2.9%（5.1%是营业总成本）
        'D': sh14 < sh15,     # 2014年中央企业收入占比低于2015年？
    }, dict(dprofit=dprofit, sh15=sh15, sh14=sh14)
t, info = a3_truth()
assert [k for k, x in t.items() if x] == ['B'], t
for rp, rr, rrc in itertools.product((7.95, 8.05), (5.95, 6.05), (6.95, 7.05)):
    tt, _ = a3_truth(rp=rp, rr=rr, rrc=rrc)
    assert [k for k, x in tt.items() if x] == ['B'], (rp, rr, rrc, tt)
rec('ZL3B-A3 (ZJ2016A-2 属实)', 'B', f"利润减少={info['dprofit']:.1f}亿元(>400); 中央收入占比 2015={info['sh15']*100:.2f}% 2014={info['sh14']*100:.2f}%")

# ============ M7 ZLM-JS2024A-1 跨省联网 ============
a, d1, d2 = closest(27.9 * 0.128 / 1.128, {'A': 3.2, 'B': 3.4, 'C': 3.6, 'D': 3.8})
rec('JS2024A-116(not delivered)', a, f'{27.9*0.128/1.128:.3f}', 'A')
v117 = 354.3e8 / 282.6e4 / 1e4
a, d1, d2 = closest(v117, {'A': 1.15, 'B': 1.20, 'C': 1.25, 'D': 1.30})
rec('JS2024A-117', a, f'人均={v117:.4f}万元; 若用全口径394.1/2854.1={394.1e8/2854.1e4/1e4:.4f}万元', 'C')
v118 = 1.46 / 2.46 * 100
a, d1, d2 = closest(v118, {'A': 57.1, 'B': 59.3, 'C': 60.4, 'D': 61.2})
rec('JS2024A-118', a, f'Q2/(Q1+Q2)=1.46/2.46={v118:.2f}%', 'B')
cats = {'A': (40.1, 47.6), 'B': (36.8, 49.6), 'C': (24.6, 39.0), 'D': (97.9, 89.5)}
up = [k for k, (m, p) in cats.items() if (1 + m / 100) / (1 + p / 100) > 1]
assert up == ['D']
rec('JS2024A-119', 'D', 'per-capita ratio=' + str({k: round((1 + m / 100) / (1 + p / 100), 4) for k, (m, p) in cats.items()}), 'D')
t120 = {'A': False,                                   # 只有环比，无同比
        'B': abs(2571.6 / 282.6 - 1 - 8.1) < 0.05,    # 多8.1倍 = 是9.1倍
        'C': False,                                   # 备案 ≠ 享受直接结算
        'D': 3.9 * 0.759 / 1.759 >= 15.1 * 0.289 / 1.289}
assert [k for k, x in t120.items() if x] == ['B'], t120
rec('JS2024A-120', 'B', f'2571.6/282.6={2571.6/282.6:.3f}倍 -> 多{2571.6/282.6-1:.2f}倍; D:慢特病增量{3.9*0.759/1.759:.2f} 普通门诊{15.1*0.289/1.289:.2f}', 'B')

# ============ M8 ZLM-JS2020A-3 人口70年 ============
v116 = (11.4 / 9.9 - 1) * 100
a, d1, d2 = closest(v116, {'A': 14.0, 'B': 15.2, 'C': 16.4, 'D': 19.3})
rec('JS2020A-116', a, f'1980末9.9->1990末11.4: {v116:.2f}%; 误用1981末10.0: {(11.4/10.0-1)*100:.1f}%(A)', 'B')
V1 = (6.99 / 5.67) ** (1 / 8) - 1; V2 = (8.08 / 6.99) ** (1 / 10) - 1; V3 = (9.16 / 8.08) ** (1 / 10) - 1
vv = {'82-90': V1, '90-00': V2, '00-10': V3}
order = sorted(vv, key=lambda k: -vv[k])
opts117 = {'A': ['82-90', '90-00', '00-10'], 'B': ['82-90', '00-10', '90-00'], 'C': ['90-00', '82-90', '00-10'], 'D': ['90-00', '00-10', '82-90']}
a = [k for k, o in opts117.items() if o == order][0]
rec('JS2020A-117', a, 'V=' + str({k: round(x * 100, 3) for k, x in vv.items()}), 'A')
p2018 = 11.4 + 28 * 0.0878
v118a = p2018 - 18 * 0.0711; v118b = 14.0 - 18 * 0.0711
a, d1, d2 = closest(v118a, {'A': 11.6, 'B': 12.1, 'C': 12.6, 'D': 13.1})
a2, _, _ = closest(v118b, {'A': 11.6, 'B': 12.1, 'C': 12.6, 'D': 13.1})
assert a == a2
rec('JS2020A-118', a, f'2018末(=1990末+28x878万)={p2018:.3f}亿; 2000末={v118a:.3f}亿(用"近14亿"则{v118b:.3f}); 若误算17年:{p2018-17*0.0711:.3f}', 'C')
inc = {'A': 1.4 - 0.6, 'B': 3.6 - 1.4, 'C': 8.9 - 3.6, 'D': 13.0 - 8.9}
a = max(inc, key=inc.get)
rec('JS2020A-119', a, 'pp=' + str({k: round(x, 1) for k, x in inc.items()}) + '（A段起点1980末未给，<=1.4，不影响）', 'C')
hs10 = 22.9 - 8.9; hs18 = 29.3 - 13.0
t120 = {'A': False,   # 年均≠某一年
        'B': True,    # "达到峰值后增量由正转负"按原解析读作此后逐年减少
        'C': 8.97 / 14.0 > 0.60,
        'D': hs18 > hs10}  # 比重上升且总人口增加
cannot = [k for k, x in t120.items() if not x]
assert cannot == ['A']
rec('JS2020A-120', 'A', f'高中占比2010={hs10:.1f}% 2018={hs18:.1f}%; 劳动年龄/总人口>={8.97/14*100:.1f}%', 'A')


# =====================================================================
# UPGRADE 11-09: harder items (in-place). Each adaptation: all options evaluated,
# exactly one correct, rounding perturbation of every rounded input.
# =====================================================================
def only(truth):
    return [k for k, v in truth.items() if v]

# ---- U002 (variant_of GD2014X-87): 民营以外税收 / GDP ----
def u002(tax_sh=49.1, gdp_sh=51.4, priv_tax=6467.82, priv=29319.97):
    tax = priv_tax / (tax_sh / 100); gdp = priv / (gdp_sh / 100)
    val = (tax - priv_tax) / gdp * 100
    return val, dict(A=priv_tax / gdp * 100, C=tax / gdp * 100, D=(tax - priv_tax) / (gdp - priv) * 100)
OPT002 = {'A': 11.3, 'B': 11.8, 'C': 23.1, 'D': 24.2}
v, tr = u002()
assert closest(v, OPT002)[0] == 'B'
for ts in (49.05, 49.15):
    for gs in (51.35, 51.45):
        vv, _ = u002(ts, gs)
        assert closest(vv, OPT002)[0] == 'B', (ts, gs, vv)
rec('U002 (GD2014X-1 民营以外税收/GDP)', 'B', f'{v:.3f}%; traps A={tr["A"]:.2f} C={tr["C"]:.2f} D={tr["D"]:.2f}')

# ---- U003 (variant_of GD2014X-88): 按2012年增量外推首次突破7000 ----
inc = 5524 - 5049
yr = 2012; L = 5524
while L <= 7000:
    yr += 1; L += inc
yr_rate = 2012; L2 = 5524.0; g = 5524 / 5049
while L2 <= 7000:
    yr_rate += 1; L2 *= g
assert yr == 2016 and yr_rate == 2015
rec('U003 (GD2014X-1 增量外推)', 'C', f'增量{inc}; 2015末={5524+3*inc} 2016末={5524+4*inc}; 若按增速: {yr_rate}年')

# ---- U007 (variant_of GD2016Z-87): 第二批 自来水∩硬底化 至少 ----
def int_counts(n, pct):
    return [c for c in range(n + 1) if round(c / n * 1000) / 10 == pct or abs(c / n * 100 - pct) < 0.05]
w = int_counts(391, 67.0); h = int_counts(391, 59.8)
assert w == [262] and h == [234], (w, h)
lo = 262 + 234 - 391; hi = min(262, 234)
assert lo == 105 and hi == 234
rec('U007 (GD2016Z-1 容斥下限)', 'B', f'自来水{w} 硬底化{h} 至少{lo} 至多{hi}; 按386计则{round(386*0.67)+round(386*0.598)-386}')

# ---- U010 (variant_of GD2015X-91): 前十比重比上年 ----
def u010(rt=6.9, rtop=8.9):
    s14 = 2107.7 / 2349; s13 = (2107.7 / (1 + rtop / 100)) / (2349 / (1 + rt / 100))
    return (s14 - s13) * 100, (s14 / s13 - 1) * 100
OPT010 = {'A': 1.6, 'B': 1.9, 'C': 2.0, 'D': -1.6}
d10, rel10 = u010()
assert closest(d10, OPT010)[0] == 'A'
for rt in (6.85, 6.95):
    for rtop in (8.85, 8.95):
        dd, _ = u010(rt, rtop)
        assert closest(dd, OPT010)[0] == 'A', (rt, rtop, dd)
rec('U010 (GD2015X-2 两期比重差)', 'A', f'+{d10:.3f}pp; 相对变化{rel10:.2f}%(B); 增速差2.0(C)')

# ---- U012 (variant_of GD2015X-93): 2013 中国品牌轿车/中国品牌乘用车 ----
def u012(r_sedan=-17.4, r_cn=4.1):
    return 277 / (1 + r_sedan / 100) / (757 / (1 + r_cn / 100)) * 100
OPT012 = {'A': 28.0, 'B': 36.6, 'C': 40.5, 'D': 46.1}
v12 = u012(); v12b = (0.28 * 1238 / 1.031) / (0.405 * 1970 / 1.0989) * 100
assert closest(v12, OPT012)[0] == 'D' and closest(v12b, OPT012)[0] == 'D'
for a in (-17.45, -17.35):
    for b in (4.05, 4.15):
        assert closest(u012(a, b), OPT012)[0] == 'D'
rec('U012 (GD2015X-2 其中+基期比重)', 'D', f'同比路线{v12:.2f}% 占有率路线{v12b:.2f}%; 2014={277/757*100:.1f}%')

# ---- U013 (A2 revised, variant_of GD2015X-95) ----
def u013(r_truck=-8.9, r_cv=-6.5, r_suv=36.4, r_mpv=46.8, r_pc=9.89, r_sedan=3.1):
    share14 = 318 / 379; share13 = (318 / (1 + r_truck / 100)) / (379 / (1 + r_cv / 100))
    mix = (408 + 191) / (408 / (1 + r_suv / 100) + 191 / (1 + r_mpv / 100)) - 1
    rest13 = 1970 / (1 + r_pc / 100) - 1238 / (1 + r_sedan / 100)
    return {'A': share14 > share13, 'B': (62.8 + 4.2) < 60, 'C': mix > 0.40, 'D': rest13 < 600}, dict(s14=share14, s13=share13, mix=mix, rest13=rest13)
t13, i13 = u013()
assert only(t13) == ['D'], t13
for args in itertools.product((-8.95, -8.85), (-6.55, -6.45), (36.35, 36.45), (46.75, 46.85), (9.885, 9.895), (3.05, 3.15)):
    tt, _ = u013(*args)
    assert only(tt) == ['D'], (args, tt)
# integer-sales rounding of 408 / 191 (±0.5) for option C
assert (408.5 + 191.5) / (408.5 / 1.3635 + 191.5 / 1.4675) - 1 < 0.40
rec('U013 (GD2015X-2 属实·修订)', 'D', f"货车占比 2014={i13['s14']*100:.2f}% 2013={i13['s13']*100:.2f}%; SUV+MPV={i13['mix']*100:.2f}%; 2013轿车以外={i13['rest13']:.1f}万辆")

# ---- JS2019A 117-120 (originals, swapped in for JS2024A) ----
others = 86 + 36 + 9 + 8 + 4 + 3
buy = 162 - others
order = sorted({'购买': buy, '护送': 9, '看病': 4}.items(), key=lambda x: -x[1])
assert [k for k, _ in order] == ['购买', '护送', '看病']
rec('JS2019A-117', 'C', f'购买商品或服务=162-{others}={buy}分钟 > 护送9 > 看病4', 'C')
v118 = 239 / 0.531
opts118 = {'A': 350, 'B': 400, 'C': 450, 'D': 500}
assert closest(v118, opts118)[0] == 'C'
rec('JS2019A-118', 'C', f'239/53.1%={v118:.1f}分钟; 用59.0%:{239/0.59:.1f}(B); 264/53.1%:{264/0.531:.1f}(D)', 'C')
wm = (264 - 215) / (315 - 215)
assert closest(48580 * wm / 1e4, {'A': 2.4, 'B': 2.6, 'C': 2.9, 'D': 3.0})[0] == 'A'
rec('JS2019A-119', 'A', f'男性占比={wm:.3f}, 人数={48580*wm:.0f}', 'A')
ww = (264 - 199) / (290 - 199); rest = (162 - ww * 154) / (1 - ww)
t120 = {'A': rest > 180, 'B': False, 'C': (59.0 + 70.2 - 100) >= 59.0, 'D': False}
# B: 男性55.3%<全体70.2% → 女性>70.2%，不在两者之间；D: 看病4分钟/2.2%，公益3分钟/4.1%，反例
assert only(t120) == ['A'], t120
rec('JS2019A-120', 'A', f'工作日权重={ww:.4f}, 休息日无酬={rest:.1f}分钟(>180); 都参与至少{59.0+70.2-100:.1f}%', 'A')

# ---- U031 (variant_of ZJ2016A-119): 负债同比增量中地方占比 ----
def u031(rl=13.7, rt=11.9, rc=10.4):
    local = 322462.3 * (rl / 100) / (1 + rl / 100)
    tot = 685766.3 * (rt / 100) / (1 + rt / 100)
    cen = 363304 * (rc / 100) / (1 + rc / 100)
    return local / tot * 100, local / (local + cen) * 100
def band031(x):
    return 'A' if x < 45 else 'B' if x < 50 else 'C' if x < 55 else 'D'
a1, a2 = u031()
assert band031(a1) == 'C' and band031(a2) == 'C'
for rl, rt, rc in itertools.product((13.65, 13.75), (11.85, 11.95), (10.35, 10.45)):
    x1, x2 = u031(rl, rt, rc)
    assert band031(x1) == 'C' and band031(x2) == 'C', (rl, rt, rc, x1, x2)
stock = 322462.3 / 685766.3 * 100
cen_inc_share = 100 - a2
rec('U031 (ZJ2016A-2 增量结构)', 'C', f'地方增量占比={a1:.2f}%(两增量相加作分母{a2:.2f}%); 存量占比={stock:.2f}%(B); 中央增量占比={cen_inc_share:.2f}%(B); 增速之比={13.7/(10.4+13.7)*100:.1f}%(D)')

# ---- U035 (variant_of JS2020A-118): 1991-2000年年均增加 ----
def u035(a=878, b=711):
    return (28 * a - 18 * b) / 10
OPT035 = {'A': 795, 'B': 1179, 'C': 1250, 'D': 1320}
v35 = u035()
assert closest(v35, OPT035)[0] == 'B'
for a in (877.5, 878.5):
    for b in (710.5, 711.5):
        assert closest(u035(a, b), OPT035)[0] == 'B'
rec('U035 (JS2020A-3 年均逆推)', 'B', f'{v35:.1f}万人; 简单平均{(878+711)/2}; 误数17年{(28*878-17*711)/10:.1f}; 用近14亿{((14-11.4)*1e4-18*711)/10:.1f}')

# ---- U036 (variant_of JS2020A-119): 大专及以上人数 2000末→2010末 增长倍数 ----
def u036(s00=3.6, s10=8.9, p2018=None):
    p18 = (11.4 + 28 * 0.0878) if p2018 is None else p2018
    p00 = p18 - 18 * 0.0711; p10 = p18 - 8 * 0.0711
    return (s10 * p10) / (s00 * p00) - 1
OPT036 = {'A': 1.5, 'B': 1.6, 'C': 2.5, 'D': 2.6}
v36 = u036(); v36b = u036(p2018=14.0)
assert closest(v36, OPT036)[0] == 'B' and closest(v36b, OPT036)[0] == 'B'
for s0 in (3.55, 3.65):
    for s1 in (8.85, 8.95):
        assert closest(u036(s0, s1), OPT036)[0] == 'B', (s0, s1, u036(s0, s1))
rec('U036 (JS2020A-3 比重×人口)', 'B', f'增长{v36:.3f}倍(用近14亿:{v36b:.3f}); 只用比重{8.9/3.6-1:.3f}(A); 是{v36+1:.2f}倍(D)')

if __name__ == '__main__':
    import json
    json.dump(R, open('/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/zl3b/verify_results.json', 'w'), ensure_ascii=False, indent=1)
    print('ALL CHECKS PASSED,', len(R), 'records')

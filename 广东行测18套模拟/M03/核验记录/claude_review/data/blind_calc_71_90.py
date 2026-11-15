#!/usr/bin/env python3
"""M03 第71-90题（资料分析）盲解复算脚本。

只读取考生可见的 题目.jsonl（材料、题干、选项），不读答案/解析/底稿。
所有表格数字直接从 题目.jsonl 解析，避免手抄误差。
对每题输出：精确值、与各选项的距离、最接近项是否唯一、与相邻选项的差距。

用法: python3 blind_calc_71_90.py [repo_root]
"""
import json, sys
from fractions import Fraction as F

repo = sys.argv[1] if len(sys.argv) > 1 else '/home/user/xing-ce1'
path = repo + '/广东行测18套模拟/M03/题目.jsonl'
Q = {}
for line in open(path, encoding='utf-8'):
    d = json.loads(line)
    if 71 <= d['number'] <= 90:
        Q[d['number']] = d


def table(qnum, idx):
    """Return (headers, rows) of the idx-th table block in the question's materials."""
    tabs = [b for m in Q[qnum]['materials'] for b in m['blocks'] if b['type'] == 'table']
    t = tabs[idx]
    return t['headers'], t['rows']


def num(s):
    s = s.replace('−', '-').replace(',', '')
    return None if s in ('—', '-', '') else float(s)


def pct(x):
    return '%.4f%%' % (x * 100)


def show(title, val, opts, unit=''):
    """Print exact value and distance to each numeric option."""
    print('  精确值: %.6f%s' % (val, unit))
    ds = sorted(((abs(val - o), k, o) for k, o in opts.items()))
    for dist, k, o in ds:
        print('    %s=%s  距离 %.4f' % (k, o, dist))
    best = ds[0]
    print('  最接近: %s；次近 %s，次近距离/最近距离 = %s' % (
        best[1], ds[1][1], ('%.2f' % (ds[1][0] / best[0])) if best[0] > 0 else 'inf'))


print('=' * 70)
print('第71-75题：文字材料（超高清视频）')
print('=' * 70)
print('71: 检索题，材料末段“产品端促销、产业链对接、内容制播及AI赋能四大板块”→ A')
print('72: A/B/D 材料均有直接表述；C“8K节目量位居全国首位”材料只提4K，无8K信息 → C 不能推出')

print('\n73: 广东月产能105万片=全国总产能25%')
nat_month = F(105) / F(25, 100)
print('  全国月产能 = 105/25%% = %s 万片；全年(12个月满负荷) = %s 万片' % (nat_month, nat_month * 12))
print('  对照: 105*12 = %d（只算广东）；420*5 = %d' % (105 * 12, 420 * 5))
show('73', float(nat_month * 12), {'A': 1260, 'B': 2100, 'C': 3880, 'D': 5040})

print('\n74: 2026Q1 手机产量 同比+9.4%，较2024Q1 +4.4%')
r = 1.044 / 1.094 - 1
print('  2025Q1 同比(相对2024Q1) = 1.044/1.094 - 1 = %s' % pct(r))
print('  简单相减 4.4-9.4 = -5.0（边界陷阱）；精确为 -4.57%%，距5%%边界 %.2f 个百分点' % (5 + r * 100))
print('  → 下降不到5%% → D')

print('\n75:')
print('  A: 107.9-22.4 = %.1f 个百分点（选项说75.5）→ 错' % (107.9 - 22.4))
tv = 2905 / 0.89
print('  B: 电视用户总量 = 2905/89%% = %.1f 万户 > 3000 → 对；若89%%为四舍五入(88.5%%~89.5%%) 区间 %.1f~%.1f 仍>3000' % (
    tv, 2905 / 0.895, 2905 / 0.885))
print('  C: 彩电、手机分别占全国60.3%%、44.7%%，基数不同，无法比较绝对量 → 不能推出')
b2017 = 10803 / 3.5
print('  D: “较2017年增长2.5倍”→2017=10803/3.5=%.1f，增长额=%.1f 亿元 >7500 → 错' % (b2017, 10803 - b2017))
print('     （若误读为“是2017年的2.5倍”：2017=%.1f，增长额=%.1f<7500，会误判为对）' % (10803 / 2.5, 10803 - 10803 / 2.5))

print('\n' + '=' * 70)
print('第76-80题：汽车制造业九列表')
print('=' * 70)
h, rows = table(76, 0)
print('  表头:', h)
T = {}
for r_ in rows:
    T[int(r_[0])] = dict(zip(h[1:], [num(x) for x in r_[1:]]))
ent, loss_n, loss, loss_g, rev, rev_g, prof, prof_g = h[1:]

# internal consistency: growth columns vs levels
print('  表内一致性：同比列 vs 相邻年水平值反算（差>0.06个百分点则标记）')
for y in range(2014, 2024):
    for lvl, g in ((loss, loss_g), (rev, rev_g), (prof, prof_g)):
        a, b, gg = T[y][lvl], T[y - 1][lvl], T[y][g]
        if a is None or b is None or gg is None:
            continue
        calc = (a / b - 1) * 100
        flag = '  <-- 不一致' if abs(calc - gg) > 0.06 else ''
        if flag:
            print('    %d %s: 反算 %.2f vs 表 %.1f%s' % (y, lvl, calc, gg, flag))
print('    （无标记即全部一致）')

print('\n76: 亏损面 = 亏损企业数/企业数')
lm = {y: T[y][loss_n] / T[y][ent] for y in T}
for y in sorted(lm):
    print('    %d: %s' % (y, pct(lm[y])))
d76 = (lm[2022] - lm[2016]) * 100
print('  2022-2016 = %.4f 个百分点 → 扩大14.3 → C' % d76)

print('\n77: 2013→2023 倍数（年均增速排序等价于倍数排序）')
for k in (prof, loss, loss_n, ent):
    ratio = T[2023][k] / T[2013][k]
    print('    %s: %.4f 倍，年均 %s' % (k, ratio, pct(ratio ** 0.1 - 1)))
print('  → 亏损总额最快 → B')

print('\n78: 主营业务利润率 = 利润总额/主营业务收入；同比上升 ⇔ 利润增速 > 收入增速')
for y in range(2013, 2019):
    pg, rg = T[y][prof_g], T[y][rev_g]
    lvl = T[y][prof] / T[y][rev]
    prev = (T[y - 1][prof] / T[y - 1][rev]) if (y - 1) in T else (T[y][prof] / (1 + pg / 100)) / (T[y][rev] / (1 + rg / 100))
    print('    %d: 利润率 %s，上年 %s，利润增速 %.1f vs 收入增速 %.1f → %s' % (
        y, pct(lvl), pct(prev), pg, rg, '上升' if lvl > prev else '下降'))
print('  → 2013、2014 两年上升（2013需用表中同比增速推2012）→ B；若漏掉2013会得1（A）')

print('\n79: 平均每家亏损企业亏损额（亿元→万元 ×10000）')
a22 = T[2022][loss] * 10000 / T[2022][loss_n]
a21 = T[2021][loss] * 10000 / T[2021][loss_n]
print('  2022: %.4f 万元；2021: %.4f 万元；差 %.4f 万元' % (a22, a21, a22 - a21))
show('79', a22 - a21, {'A': 880, 'B': 111, 'C': -880, 'D': -111}, ' 万元')

print('\n80:')
y135 = range(2016, 2021)
mx = max(y135, key=lambda y: T[y][loss]); mn = min(y135, key=lambda y: T[y][loss])
print('  ① 十三五(2016-2020) 亏损总额最多 %d=%.1f，最少 %d=%.1f，倍数 %.4f → >3 成立' % (
    mx, T[mx][loss], mn, T[mn][loss], T[mx][loss] / T[mn][loss]))
inc13 = T[2013][prof] - T[2013][prof] / (1 + T[2013][prof_g] / 100)
print('  ② 2013利润增量 = 5107.7-5107.7/1.256 = %.2f 亿元 → >1000 成立' % inc13)
print('  ③ 表为年度数据，2023全年亏损增量 = %.1f 亿元；“2023年12月当月”无法由年度数据推出 → 不成立' % (
    T[2023][loss] - T[2022][loss]))
print('  → 2项 → C')

print('\n' + '=' * 70)
print('第81-85题：空调累计产量')
print('=' * 70)
h, rows = table(81, 0)
C = {r_[0]: (num(r_[1]), num(r_[2])) for r_ in rows}
for k, v in C.items():
    print('    %s: 累计 %s 万台，累计增速 %s%%' % (k, v[0], v[1]))
jun22 = C['2023年6月'][0] / (1 + C['2023年6月'][1] / 100)
may22 = C['2023年5月'][0] / (1 + C['2023年5月'][1] / 100)
jul22 = C['2023年7月'][0] / (1 + C['2023年7月'][1] / 100)
print('\n81: 2022H2 = 2022年12月累计 - 2022年6月累计；2022年6月累计 = 14060/1.166 = %.2f' % jun22)
h2 = C['2022年12月'][0] - jun22
show('81', h2, {'A': 10189, 'B': 11236, 'C': 12058, 'D': 13131}, ' 万台')

print('\n82:')
sep = C['2022年9月'][0] - C['2022年8月'][0]
octo = C['2022年10月'][0] - C['2022年9月'][0]
nov = C['2022年11月'][0] - C['2022年10月'][0]
dec = C['2022年12月'][0] - C['2022年11月'][0]
print('  当月产量 9月 %d，10月 %d，11月 %d，12月 %d' % (sep, octo, nov, dec))
r82 = (octo / sep - 1) * 100
show('82', r82, {'A': 7, 'B': 17, 'C': -7, 'D': -17}, '%')

print('\n83: 2023年6月当月 = 14060-11425；2022年6月当月 = 14060/1.166 - 11425/1.142')
jun23m = C['2023年6月'][0] - C['2023年5月'][0]
jun22m = jun22 - may22
r83 = (jun23m / jun22m - 1) * 100
print('  2023年6月 %.0f；2022年6月 %.2f' % (jun23m, jun22m))
show('83', r83, {'A': 16.6, 'B': 20.8, 'C': 23.2, 'D': 28.3}, '%')
jul23m = C['2023年7月'][0] - C['2023年6月'][0]
jul22m = jul22 - jun22
print('  [旁证] 同法算2023年7月当月同比 = %.2f%%，材料文字给出29.0%%（表与文字不完全自洽，属真实统计口径差，不影响作答）' % (
    (jul23m / jul22m - 1) * 100))

print('\n84: 出口单价 = 金额/数量；(1-15.4%)/(1+1.3%) - 1')
r84 = ((1 - 0.154) / (1 + 0.013) - 1) * 100
show('84', r84, {'A': -13.9, 'B': -16.5, 'C': 13.9, 'D': 16.5}, '%')
print('  简单相减近似 -15.4-1.3 = -16.7，仍最近B')

print('\n85: 2022年10-12月环比增量')
inc = [octo - sep, nov - octo, dec - nov]
print('  10月 %+d，11月 %+d，12月 %+d → 单调上升，两段升幅 %d、%d（比 %.2f）' % (
    inc[0], inc[1], inc[2], inc[1] - inc[0], inc[2] - inc[1], (inc[1] - inc[0]) / (inc[2] - inc[1])))
print('  同时：当月产量 %d,%d,%d 也上升；环比增速 %.2f%%,%.2f%%,%.2f%% 也上升；累计增速 3.2,2.0,1.8 下降(→C陷阱)' % (
    octo, nov, dec, (octo / sep - 1) * 100, (nov / octo - 1) * 100, (dec / nov - 1) * 100))
print('  选项图形(见q85_options_x5.png): A上升直线 B先降后升 C下降 D先升后降 → A')

print('\n' + '=' * 70)
print('第86-90题：能源生产/消费双表')
print('=' * 70)
h1, r1 = table(86, 0)
h2_, r2 = table(86, 1)
P = {int(r_[0]): [num(x) for x in r_[1:]] for r_ in r1}
S = {int(r_[0]): [num(x) for x in r_[1:]] for r_ in r2}
print('  行和校验（总量 = 原煤+原油+天然气+其他）:')
for nm, D in (('生产', P), ('消费', S)):
    for y in sorted(D):
        tot, *parts = D[y]
        print('    %s %d: 总量 %d，分项和 %d，差 %d' % (nm, y, tot, sum(parts), tot - sum(parts)))

print('\n86: 其他能源生产量同比')
for y in range(2019, 2023):
    print('    %d: +%.0f，%s' % (y, P[y][4] - P[y - 1][4], pct(P[y][4] / P[y - 1][4] - 1)))
print('  → 2022最慢（次慢2020） → D')

print('\n87: 2021 原煤消费增量 / 原油消费增量')
dc = S[2021][1] - S[2020][1]; do = S[2021][2] - S[2020][2]
show('87', dc / do, {'A': 1.2, 'B': 1.5, 'C': 2.2, 'D': 2.5})
print('  （原煤增量 %d，原油增量 %d）' % (dc, do))

print('\n88: 2022消费构成')
for i, nm in enumerate(['原煤(灰)', '原油(黑白格)', '天然气(白)', '其他(黑)'], start=1):
    print('    %s %s，%.1f°' % (nm, pct(S[2022][i] / S[2022][0]), S[2022][i] / S[2022][0] * 360))
print('  选项扇区实测见 q88_pie_measure.py：B 最接近，D 天然气偏大/其他偏小，A、C 原煤约2/3')

print('\n89: 天然气年均生产量')
g = [P[y][3] for y in range(2018, 2023)]
print('  %s 合计 %d，均值 %.1f → 24000~25000 → C；距24000下界仅 %.1f（合计差%d）' % (
    g, sum(g), sum(g) / 5, sum(g) / 5 - 24000, sum(g) - 120000))
print('  取整到千位估算: %d → 会误落B区间；取整到百位: %d' % (
    sum(round(x, -3) for x in g) / 5, sum(round(x, -2) for x in g) / 5))

print('\n90:')
for y in range(2018, 2023):
    print('    A: %d 原煤消费-生产 = %+d' % (y, S[y][1] - P[y][1]))
cnt = sum(1 for y in range(2018, 2023) if abs(S[y][1] - P[y][1]) > 10000)
cnt1 = sum(1 for y in range(2018, 2023) if S[y][1] - P[y][1] > 10000)
print('  A: |相差|>10000 的年份 %d 个（2018 和 2022）；若只看“消费>生产” 则 %d 个 → 按“相差”取绝对值，A错' % (cnt, cnt1))
for y in range(2019, 2023):
    print('    B: %d 原煤%+d 原油%+d 天然气%+d' % (y, S[y][1] - S[y - 1][1], S[y][2] - S[y - 1][2], S[y][3] - S[y - 1][3]))
print('  B: 2022原油、天然气消费下降 → 错')
c = (S[2021][1] + S[2021][2] + S[2021][3]) / S[2021][0]
print('  C: 2021 三项占比 = %s > 80%% → 对' % pct(c))
print('  D: 2022较2020 = %s < 10%% → 错' % pct(S[2022][0] / S[2020][0] - 1))
print('  → C')

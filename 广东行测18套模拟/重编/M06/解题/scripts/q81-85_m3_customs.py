# -*- coding: utf-8 -*-
"""第81—85题（资料第3组，2024年4月全国监管货运进出境）核算脚本。数据从输入 data.json 的表格读取。"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '..', '..', '输入', 'data.json'), encoding='utf-8'))
m3 = [m for m in d['materials'] if m['id'].endswith('-m3')][0]
tab = [b for b in m3['blocks'] if b['type'] == 'table'][0]
T = {}
for name, unit, apr, g_apr, ytd, g_ytd in tab['rows']:
    key = name.replace('其中：', '')
    T[key] = dict(apr=float(apr), g_apr=float(g_apr), ytd=float(ytd), g_ytd=float(g_ytd), unit=unit)
for k, v in T.items():
    print(k, v)

TOT, IMP, EXP = '监管进出口货运量', '进口', '出口'
VT = '监管运输工具进出境总数'
TOOLS = ['进出境汽车', '进出境火车', '进出境船舶', '进出境飞机']


def nearest(val, opts):
    return min(opts.items(), key=lambda kv: abs(kv[1] - val))


def base(v, g):
    return v / (1 + g / 100)


# ---------------- 自洽检查 ----------------
print('\n[自洽检查]')
for col in ('apr', 'ytd'):
    s = T[IMP][col] + T[EXP][col]
    print(f'{col}: 进口+出口={s:.1f}  合计={T[TOT][col]}  差={s - T[TOT][col]:.1f}')
    s2 = sum(T[t][col] for t in TOOLS)
    print(f'{col}: 四种运输工具之和={s2:.0f}  总数={T[VT][col]:.0f}  差={s2 - T[VT][col]:.0f}')
for col, g in (('apr', 'g_apr'), ('ytd', 'g_ytd')):
    b = base(T[IMP][col], T[IMP][g]) + base(T[EXP][col], T[EXP][g])
    print(f'{col}: 由进口、出口增速反推合计增速={(T[TOT][col] / b - 1) * 100:.3f}%  表中={T[TOT][g]}')
    b2 = sum(base(T[t][col], T[t][g]) for t in TOOLS)
    print(f'{col}: 由四种工具增速反推总数增速={(T[VT][col] / b2 - 1) * 100:.3f}%  表中={T[VT][g]}')
# 1—3月（=1—4月-4月）的同比增速是否合理
print('2024年1—3月与2023年1—3月（由1—4月减4月得到）：')
for k in [TOT, IMP, EXP, VT] + TOOLS:
    cur = T[k]['ytd'] - T[k]['apr']
    prev = base(T[k]['ytd'], T[k]['g_ytd']) - base(T[k]['apr'], T[k]['g_apr'])
    print(f'  {k}: 2024年1—3月={cur:.1f}，2023年1—3月={prev:.1f}，1—3月同比={(cur / prev - 1) * 100:.2f}%')

# ---------------- 第81题 ----------------
print('\n[81] 2023年1—4月监管进出口货运量（亿吨）')
opts = {'A': 16.6, 'B': 17.1, 'C': 17.4, 'D': 17.9}
v = base(T[TOT]['ytd'], T[TOT]['g_ytd'])
print(f'正确：176583.3/1.063={v:.2f}万吨={v / 1e4:.4f}亿吨 → {nearest(v / 1e4, opts)}')
for k, val in {
    '乘(1-6.3%)': T[TOT]['ytd'] * (1 - 0.063),
    '不折算，直接用2024年': T[TOT]['ytd'],
    '用4月增速9.6%折算': base(T[TOT]['ytd'], T[TOT]['g_apr']),
    '用进口增速6.8%': base(T[TOT]['ytd'], T[IMP]['g_ytd']),
    '用出口增速5.3%': base(T[TOT]['ytd'], T[EXP]['g_ytd']),
    '乘(1+6.3%)': T[TOT]['ytd'] * 1.063,
}.items():
    print(f'  {k}: {val / 1e4:.4f}亿吨 → 最近 {nearest(val / 1e4, opts)}')

# ---------------- 第82题 ----------------
print('\n[82] 4月各运输工具占总数比重同比上升的个数')
b_tot = T[VT]['g_apr']
cnt = 0
for t in TOOLS:
    a = T[t]['g_apr']
    sh_now = T[t]['apr'] / T[VT]['apr'] * 100
    sh_prev = base(T[t]['apr'], a) / base(T[VT]['apr'], b_tot) * 100
    up = sh_now > sh_prev
    cnt += up
    print(f'  {t}: 增速{a}% vs 总数{b_tot}%  比重 {sh_prev:.4f}% → {sh_now:.4f}%  {"上升" if up else "下降"}')
print(f'上升的有{cnt}种')
cnt_ytd = sum(T[t]['g_ytd'] > T[VT]['g_ytd'] for t in TOOLS)
print(f'  （若误用1—4月增速判断：上升{cnt_ytd}种；若误以为“增速为正即比重上升”：{sum(T[t]["g_apr"] > 0 for t in TOOLS)}种）')

# ---------------- 第83题 ----------------
print('\n[83] 2023年1—3月监管出口货运量（万吨）')
opts = {'A': 39477, 'B': 41210, 'C': 43562, 'D': 45941}
y23_ytd = base(T[EXP]['ytd'], T[EXP]['g_ytd'])
y23_apr = base(T[EXP]['apr'], T[EXP]['g_apr'])
v = y23_ytd - y23_apr
print(f'2023年1—4月=58731.9/1.053={y23_ytd:.2f}；2023年4月=17521.6/1.075={y23_apr:.2f}；差={v:.2f} → {nearest(v, opts)}')
for k, val in {
    '2024年1—3月(不折算)': T[EXP]['ytd'] - T[EXP]['apr'],
    '2024年1—3月÷1.053': (T[EXP]['ytd'] - T[EXP]['apr']) / 1.053,
    '2024年1—3月÷1.075': (T[EXP]['ytd'] - T[EXP]['apr']) / 1.075,
    '2023年1—4月-2024年4月': y23_ytd - T[EXP]['apr'],
    '2024年1—4月-2023年4月': T[EXP]['ytd'] - y23_apr,
    '1—4月×(1-5.3%)-4月×(1-7.5%)': T[EXP]['ytd'] * (1 - 0.053) - T[EXP]['apr'] * (1 - 0.075),
    '2023年1—4月×3/4': y23_ytd * 3 / 4,
    '2024年1—4月×3/4': T[EXP]['ytd'] * 3 / 4,
    '2023年1—4月-2023年4月(进口)': base(T[IMP]['ytd'], T[IMP]['g_ytd']) - base(T[IMP]['apr'], T[IMP]['g_apr']),
    '2023年1—4月(出口)': y23_ytd,
}.items():
    print(f'  {k}: {val:.2f} → 最近 {nearest(val, opts)}')

# ---------------- 第84题 ----------------
print('\n[84] 4月高于1—3月月均的运输工具个数')
cnt = 0
for t in TOOLS:
    avg13 = (T[t]['ytd'] - T[t]['apr']) / 3
    hi = T[t]['apr'] > avg13
    cnt += hi
    print(f'  {t}: 4月={T[t]["apr"]:.0f}  1—3月月均=({T[t]["ytd"]:.0f}-{T[t]["apr"]:.0f})/3={avg13:.1f}  '
          f'4×4月={4 * T[t]["apr"]:.0f} vs 1—4月={T[t]["ytd"]:.0f}  {"高于" if hi else "不高于"}  超出{(T[t]["apr"] / avg13 - 1) * 100:.2f}%')
print(f'高于的有{cnt}种')
for t in TOOLS:
    print(f'  （误把1—4月÷3当1—3月月均）{t}: {T[t]["ytd"] / 3:.1f}  4月高于? {T[t]["apr"] > T[t]["ytd"] / 3}')

# ---------------- 第85题 ----------------
print('\n[85] 逐项')
print(f'A：69460/30={T["进出境飞机"]["apr"] / 30:.2f}架/天 > 2300 → 错误（“不超过2300”不成立）')
ratio = T['进出境飞机']['ytd'] / T['进出境船舶']['ytd']
print(f'B：264766/127518={ratio:.4f}倍，“多”{ratio - 1:.4f}倍 → 说“多2.1倍”错误（“是”约2.1倍）')
inc = T[IMP]['ytd'] - base(T[IMP]['ytd'], T[IMP]['g_ytd'])
print(f'C：117851.4×6.8%/1.068={inc:.2f}万吨 > 7000 → 正确；（直接乘6.8%={T[IMP]["ytd"] * 0.068:.2f}）'
      f'；7000对应的临界增速≈{7000 / (T[IMP]["ytd"] - 7000) * 100:.3f}%')
print(f'D：进口-出口={T[IMP]["apr"] - T[EXP]["apr"]:.1f}万吨，是进口比出口多，方向说反 → 错误')

# -*- coding: utf-8 -*-
"""第86—89题（资料第4组，全国纸浆／木浆产量）核算脚本；第90题读图见 q90_line_chart_pixels.py。"""
import itertools
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '..', '..', '输入', 'data.json'), encoding='utf-8'))
m4 = [m for m in d['materials'] if m['id'].endswith('-m4')][0]
tab = [b for b in m4['blocks'] if b['type'] == 'table'][0]
W = {int(r[0]): float(r[1]) for r in tab['rows']}     # 木浆产量（万吨）
print('木浆:', W)

TOTAL23, G_TOTAL, G_TOTAL_2Y = 8823, 2.75, 7.89
WOOD23, G_WOOD = 2312, 9.31
G_NONWOOD = 3.05
RECY23, G_RECY = 5936, 0.37


def nearest(val, opts):
    return min(opts.items(), key=lambda kv: abs(kv[1] - val))


# ---------------- 自洽检查 ----------------
print('\n[自洽检查]')
print(f'文字木浆2023={WOOD23} 表中={W[2023]}；表算增速={(W[2023] / W[2022] - 1) * 100:.3f}% 文字={G_WOOD}%')
nonwood23 = TOTAL23 - WOOD23 - RECY23
print(f'非木浆2023=8823-2312-5936={nonwood23}')
tot22 = TOTAL23 / (1 + G_TOTAL / 100)
recy22 = RECY23 / (1 + G_RECY / 100)
nonwood22_by_total = tot22 - W[2022] - recy22
print(f'2022总量={tot22:.2f}，再生={recy22:.2f}，木浆={W[2022]} → 非木浆(由总量反推)={nonwood22_by_total:.2f}')
print(f'  对应非木浆增速={(nonwood23 / nonwood22_by_total - 1) * 100:.3f}%（文字3.05%）')
g_total_calc = TOTAL23 / (W[2022] + recy22 + nonwood23 / (1 + G_NONWOOD / 100)) - 1
print(f'  由三类分项增速反推总量增速={g_total_calc * 100:.3f}%（文字2.75%）')
tot21 = TOTAL23 / (1 + G_TOTAL_2Y / 100)
print(f'2021总量={tot21:.2f}；2022较2021增速={(tot22 / tot21 - 1) * 100:.3f}%；'
      f'间隔增速核对：(1+2.75%)×(1+r22)=1+7.89% → r22={((1 + G_TOTAL_2Y / 100) / (1 + G_TOTAL / 100) - 1) * 100:.3f}%')
print(f'2021木浆占总量={W[2021] / tot21 * 100:.2f}%，2022={W[2022] / tot22 * 100:.2f}%，2023={W[2023] / TOTAL23 * 100:.2f}%')

# ---------------- 第86题 ----------------
print('\n[86]')
opts = {'A': 2182, 'B': 2236, 'C': 2345, 'D': 2535}
a = W[2021] + W[2022] + W[2023]
b = W[2018] + W[2019] + W[2020]
print(f'2021—2023={a:.0f}，2018—2020={b:.0f}，差={a - b:.0f} → {nearest(a - b, opts)}')
print(f'  逐年配对：(1809-1137)+(2115-1264)+(2312-1490)={W[2021] - W[2018]:.0f}+{W[2022] - W[2019]:.0f}+{W[2023] - W[2020]:.0f}')
print(f'  尾数法：1+5+2=8→…6；7+4+0=11→…1；差尾数 6-1=5 → 只有C(2345)尾数为5')
# 看错误组合
for k, v in {
    '2020—2023减2017?无': None,
    '2021—2023减2019—2021': (W[2021] + W[2022] + W[2023]) - (W[2019] + W[2020] + W[2021]),
    '2022—2023减2019—2020': (W[2022] + W[2023]) - (W[2019] + W[2020]),
    '2021—2023减2018—2019(两年)': a - (W[2018] + W[2019]),
    '2020—2023减2018—2019': (W[2020] + W[2021] + W[2022] + W[2023]) - (W[2018] + W[2019]) - 0,
}.items():
    if v is not None:
        print(f'  {k}: {v:.0f} → 最近 {nearest(v, opts)}')

# ---------------- 第87题 ----------------
print('\n[87] 2022年非木浆')
opts = {'A': 558, 'B': 575, 'C': 622, 'D': 715}
v = nonwood23 / (1 + G_NONWOOD / 100)
print(f'正确：(8823-2312-5936)/1.0305={nonwood23}/1.0305={v:.3f} → {nearest(v, opts)}')
print(f'  由2022年总量反推：{nonwood22_by_total:.3f} → {nearest(nonwood22_by_total, opts)}')
for k, val in {
    '2023年非木浆(未折算)': nonwood23,
    '575×(1-3.05%)': nonwood23 * (1 - G_NONWOOD / 100),
    '575×(1+3.05%)': nonwood23 * (1 + G_NONWOOD / 100),
    '2022总量-2022木浆-2023再生': tot22 - W[2022] - RECY23,
    '8823-2115-5936(木浆用2022，其余2023)': TOTAL23 - W[2022] - RECY23,
    '2022总量(÷1.0789)-2022木浆-再生2022': TOTAL23 / (1 + G_TOTAL_2Y / 100) - W[2022] - recy22,
    '8823/1.0275-2312-5936/1.0037': tot22 - W[2023] - recy22,
    '8823-2312/1.0931-5936/1.0037': TOTAL23 - W[2023] / (1 + G_WOOD / 100) - recy22,
    '8823/1.0275-2312/1.0931... (同正确)': tot22 - W[2023] / (1 + G_WOOD / 100) - recy22,
    '8823×(1-2.75%)-2115-5936×(1-0.37%)': TOTAL23 * (1 - G_TOTAL / 100) - W[2022] - RECY23 * (1 - G_RECY / 100),
}.items():
    print(f'  {k}: {val:.3f} → 最近 {nearest(val, opts)}')

# ---------------- 第88题 ----------------
print('\n[88] 保持2023年同比增长量，2026年木浆产量')
opts = {'A': 3198, 'B': 2903, 'C': 3462, 'D': 3715}
inc = W[2023] - W[2022]
v = W[2023] + 3 * inc
print(f'2023年增量=2312-2115={inc:.0f}；2026=2312+3×{inc:.0f}={v:.0f} → {nearest(v, opts)}')
for k, val in {
    '保持增速9.31%(按增速)': W[2023] * (1 + G_WOOD / 100) ** 3,
    '多算一年(+4×197)': W[2023] + 4 * inc,
    '少算一年(+2×197)': W[2023] + 2 * inc,
    '用2022年增量306': W[2023] + 3 * (W[2022] - W[2021]),
    '用2023年增量×3+2115': W[2022] + 3 * inc,
    '用年均增量(2018—2023)': W[2023] + 3 * (W[2023] - W[2018]) / 5,
    '用2021年增量319': W[2023] + 3 * (W[2021] - W[2020]),
    '按增速4次': W[2023] * (1 + G_WOOD / 100) ** 4,
    '用增速×3线性 2312×(1+3×9.31%)': W[2023] * (1 + 3 * G_WOOD / 100),
    '用增量306×... 2312+3×306+...': W[2023] + 4 * (W[2022] - W[2021]),
}.items():
    print(f'  {k}: {val:.1f} → 最近 {nearest(val, opts)}')

# ---------------- 第89题 ----------------
print('\n[89] 以2018年为基期，2018—2022年年均增加量')
opts = {'A': 167.5, 'B': 173.5, 'C': 244.5, 'D': 314.5}
v = (W[2022] - W[2018]) / 4
print(f'(2115-1137)/4={W[2022] - W[2018]:.0f}/4={v:.2f} → {nearest(v, opts)}')
for k, val in {
    '除以5(把年份个数当间隔数)': (W[2022] - W[2018]) / 5,
    '(2312-1137)/5': (W[2023] - W[2018]) / 5,
    '(2312-1137)/4': (W[2023] - W[2018]) / 4,
    '(2115-1264)/4': (W[2022] - W[2019]) / 4,
    '(2115-1264)/5': (W[2022] - W[2019]) / 5,
    '(1809-1137)/4': (W[2021] - W[2018]) / 4,
    '(2115-1137)/6': (W[2022] - W[2018]) / 6,
    '各年产量平均-基期': (sum(W[y] for y in range(2018, 2023)) / 5 - W[2018]),
    '各年产量平均(2019—2022)-基期': (sum(W[y] for y in range(2019, 2023)) / 4 - W[2018]),
    '(2115+1809+1490+1264)/4-1137... 同上': None,
    '年均增长率×...': None,
}.items():
    if val is not None:
        print(f'  {k}: {val:.2f} → 最近 {nearest(val, opts)}')
# 搜一下哪些简单组合恰好等于干扰项
print('  干扰项反查（两年份之差÷n，n=1..6）：')
for t in (167.5, 173.5, 314.5):
    for y1, y2 in itertools.combinations(sorted(W), 2):
        for n in range(1, 7):
            if abs((W[y2] - W[y1]) / n - t) < 0.051:
                print(f'    {t} = ({W[y2]:.0f}-{W[y1]:.0f})/{n}  [{y2}-{y1}]')
    for combo_n in (2, 3, 4, 5):
        for ys in itertools.combinations(sorted(W), combo_n):
            s = sum(W[y] for y in ys)
            for n in range(1, 7):
                for sub in sorted(W):
                    if abs((s / combo_n - W[sub]) - t) < 0.051:
                        print(f'    {t} = mean{ys}-{sub}')

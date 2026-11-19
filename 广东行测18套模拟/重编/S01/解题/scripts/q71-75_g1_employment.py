# -*- coding: utf-8 -*-
"""S01 第71—75题（SYDW2023-M1，广东全社会就业人员）核算与本组自洽检查。
柱状图按原卷裁图 SYDW2023-p16-i01.png 核对柱顶标注，与转写一致；文字与原卷第16页一致
（原卷“促进就业创造了有利条件”“从2012年来的3236.78万人”两处按编排改为“为促进就业……”“2012年末”）。
第75题四幅选项图：从 SYDW2023-p17-i01.png 量取各标记中心的高度（腐蚀去掉线条后按连通块面积区分方块、圆点、三角）。"""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

years = list(range(2012, 2022))
emp = [6171, 6273, 6428, 6566, 6703, 6858, 6960, 6995, 7039, 7072]
town12, town21, prd12, prd21 = 4305.70, 5473.00, 3236.78, 4400.97
sec21 = {'第一': 753, '第二': 2565, '第三': 3754}
chg = {'第一': -490, '第二': -63, '第三': 1454}          # 2021年比2012年

print('== 本组自洽检查 ==')
inc = emp[-1] - emp[0]
cagr = (emp[-1] / emp[0]) ** (1 / 9) - 1
print('2021年比2012年增加 %d（文字901），增长 %.2f%%（文字14.6%%），年均 %.2f%%（文字1.5%%）' % (inc, (emp[-1] / emp[0] - 1) * 100, cagr * 100))
assert inc == 901
tc = (town21 / town12) ** (1 / 9) - 1
print('城镇就业人员年均 %.2f%%，比全社会高 %.2f 个百分点（文字1.2）' % (tc * 100, (tc - cagr) * 100))
sec12 = {k: sec21[k] - chg[k] for k in sec21}
print('三次产业 2021年合计 %d（=7072），2012年 %s 合计 %d（=6171）' % (sum(sec21.values()), sec12, sum(sec12.values())))
assert sum(sec21.values()) == emp[-1] and sum(sec12.values()) == emp[0]
assert prd12 < town12 and prd21 < town21
print('未发现矛盾。')

print('\n== 第71题 ==')
print('901/9 = %.1f 万人 -> B 100；误除以10得 %.1f -> A 90' % (inc / 9, inc / 10))

print('\n== 第72题 ==')
print('1.5%%+1.2%% = 2.7%% -> C；按4305.70→5473.00、9年复算 %.2f%%；误用1.5%%或1.2%%都落在B' % (tc * 100))

print('\n== 第73题 ==')
s12, s21 = prd12 / town12, prd21 / town21
print('2012年末 %.3f%%，2021年末 %.3f%%，增加 %.3f 个百分点 -> A 5.2' % (s12 * 100, s21 * 100, (s21 - s12) * 100))
print('（误用全社会就业人员作分母：%.2f 个百分点，不在选项中）' % ((prd21 / emp[-1] - prd12 / emp[0]) * 100))

print('\n== 第74题 ==')
for y in (2014, 2015, 2016, 2017):
    i = years.index(y)
    print('  %d年 增量 %d，基数 %d，增长率 %.3f%%' % (y, emp[i] - emp[i - 1], emp[i - 1], (emp[i] / emp[i - 1] - 1) * 100))
print('2014年最高 -> A（2014、2017年增量都是155，2017年基数大、现期最高，误选D）')

print('\n== 第75题 ==')
sh12 = {k: v / emp[0] for k, v in sec12.items()}
sh21 = {k: v / emp[-1] for k, v in sec21.items()}
o12 = sorted(sh12, key=lambda k: -sh12[k])
o21 = sorted(sh21, key=lambda k: -sh21[k])
print('2012年占比 %s，顺序 %s' % ({k: round(v * 100, 1) for k, v in sh12.items()}, '>'.join(o12)))
print('2021年占比 %s，顺序 %s' % ({k: round(v * 100, 1) for k, v in sh21.items()}, '>'.join(o21)))

p = '/home/user/xing-ce1/广东/事业单位/结构化/assets/SYDW2023/SYDW2023-p17-i01.png'
g = np.asarray(Image.open(p).convert('L'), dtype=float)
er = ndi.binary_erosion(g < 100, structure=np.ones((13, 13)))
lab, n = ndi.label(er)
shape_of = lambda a: '第二' if a > 250 else ('第一' if a > 90 else '第三')   # 方块、圆点、三角
panels = {'A': (0, 700, 0, 330), 'B': (720, 1430, 0, 330), 'C': (0, 700, 400, 720), 'D': (720, 1430, 400, 720)}
legend_rows = (360, 395, 735, 775)
marks = {k: {} for k in panels}
for i in range(1, n + 1):
    cy, cx = ndi.center_of_mass(er, lab, i)
    if legend_rows[0] < cy < legend_rows[1] or legend_rows[2] < cy < legend_rows[3]:
        continue
    for k, (x0, x1, y0, y1) in panels.items():
        if x0 <= cx < x1 and y0 <= cy < y1:
            marks[k].setdefault((x0 + x1) / 2 < cx, {})[shape_of((lab == i).sum())] = cy
for k in 'ABCD':
    res = []
    for right, yr in ((False, 2012), (True, 2021)):
        m = marks[k].get(right, {})
        order = sorted(m, key=lambda s: m[s])
        res.append('%d年 %s%s' % (yr, '>'.join(order), '' if len(m) == 3 else '（缺%s：与另一标记重合）' % ''.join(set(sh12) - set(m))))
    print('  选项%s：%s' % (k, '；'.join(res)))
print('只有D与 2012年 %s、2021年 %s 相符 -> D' % ('>'.join(o12), '>'.join(o21)))

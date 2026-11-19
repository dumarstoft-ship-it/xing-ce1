# -*- coding: utf-8 -*-
"""S01 第81—85题（SYDW2022-M2，A国消费电子新机出货量）核算与本组自洽检查。
表格按原卷裁图 SYDW2022-p17-i02.png 核对，与转写一致；原卷第17页正文“同比下降9.3%”的9.3%是嵌入小图，转写无误；
第81题原卷题干“出货量量”，编排改为“出货量”。
第84题折线图：从 SYDW2022-p18-i01.png 量取5个圆点中心（腐蚀去掉连线后取连通块质心）。"""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

yrs = list(range(2015, 2021))
tab = {'智能手机': [4.27, 4.65, 4.44, 3.96, 3.67, 3.33], '平板电脑': [0.26, 0.26, 0.22, 0.22, 0.22, 0.23],
       '笔记本电脑': [0.38, 0.36, 0.36, 0.35, 0.36, 0.39], '其他': [0.35, 0.46, 0.66, 0.79, 1.17, 1.43]}
tot = [round(sum(v[i] for v in tab.values()), 2) for i in range(6)]

print('== 本组自洽检查 ==')
non_phone = [sum(tab[k][i] for k in ('平板电脑', '笔记本电脑', '其他')) for i in range(6)]
print('2020年合计 %.2f（正文5.38）；非手机类同比 %.2f%%（正文17.1%%）；手机同比 %.2f%%（正文下降9.3%%）；2019年合计 %.2f，整体小幅下滑'
      % (tot[5], (non_phone[5] / non_phone[4] - 1) * 100, (tab['智能手机'][5] / tab['智能手机'][4] - 1) * 100, tot[4]))
assert tot[5] == 5.38 and tot[5] < tot[4]
print('未发现矛盾。')

print('\n== 第81题 ==')
d = tot[5] - tot[4]
print('5.38−5.42 = %.2f 亿台 = %.0f 万台 -> A 少不到1000万台（误把0.04亿台当4000万台 -> B）' % (d, d * 1e4))

print('\n== 第82题 ==')
cnt = 0
for i in range(1, 6):
    ok = {k: v[i] >= v[i - 1] for k, v in tab.items()}
    cnt += all(ok.values())
    print('  %d年 不低于上年：%s' % (yrs[i], ok))
print('四种都不低于上年的年份 %d 个 -> A（2016年漏看笔记本电脑0.38→0.36会得1个 -> B）' % cnt)

print('\n== 第83题 ==')
a, b = sum(tab['智能手机'][1:]), sum(tab['平板电脑'][1:])
print('2016—2020年 手机 %.2f / 平板 %.2f = %.3f -> C 17.4（含2015年为 %.2f）'
      % (a, b, a / b, sum(tab['智能手机']) / sum(tab['平板电脑'])))

print('\n== 第84题 ==')
p = '/home/user/xing-ce1/广东/事业单位/结构化/assets/SYDW2022/SYDW2022-p18-i01.png'
g = np.asarray(Image.open(p).convert('L'), dtype=float)
er = ndi.binary_erosion(g < 100, structure=np.ones((11, 11)))
lab, n = ndi.label(er)
pts = sorted(ndi.center_of_mass(er, lab, range(1, n + 1)), key=lambda t: t[1])
assert n == 5
h = [-y for y, x in pts]                       # 越高越大
rank = lambda v: [sorted(v, reverse=True).index(x) + 1 for x in v]
print('图中5点（2016—2020）高度名次：%s' % rank(h))
for k, v in tab.items():
    inc = [round(v[i] - v[i - 1], 2) for i in range(1, 6)]
    r = rank(inc)
    print('  %s 增量 %s 名次 %s%s' % (k, inc, r, '  <- 与图一致' if r == rank(h) else ''))
inc = [tab['其他'][i] - tab['其他'][i - 1] for i in range(1, 6)]
print('“其他”增量与点高的相关系数 %.3f -> D' % np.corrcoef(inc, h)[0, 1])

print('\n== 第85题（能推出的） ==')
print('A 平板 2018—2020合计 %.2f < 2015—2017合计 %.2f 错误' % (sum(tab['平板电脑'][3:]), sum(tab['平板电脑'][:3])))
print('B 笔记本 2017—2020年均 %.4f > 0.36（合计1.46>1.44）正确 -> B' % (sum(tab['笔记本电脑'][2:]) / 4))
gr = [round((tab['其他'][i] / tab['其他'][i - 1] - 1) * 100, 1) for i in range(1, 6)]
print('C 其他 2016—2020年增速 %s，超过50%%的年份 %d 个 错误' % (gr, sum(x > 50 for x in gr)))
print('D 手机最高 %d年，笔记本最高 %d年，不同 错误' % (yrs[tab['智能手机'].index(max(tab['智能手机']))], yrs[tab['笔记本电脑'].index(max(tab['笔记本电脑']))]))

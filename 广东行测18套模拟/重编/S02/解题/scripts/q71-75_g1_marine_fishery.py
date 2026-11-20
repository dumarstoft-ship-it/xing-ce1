# -*- coding: utf-8 -*-
"""S02 第71—75题（SYDW2024-M2，海洋渔业与海水产品）核算与本组自洽检查。
柱状图按原卷裁图 SYDW2024-p15-i01.png 核对柱顶标注，与转写一致；文字与原卷一致。
第72题原卷题干作“广东省渔业增加值占全国渔业增加值”，但材料只有“海洋渔业增加值”（全国4343亿元、广东538亿元），
本题实际用的就是这两个数；选项原卷作“个百分比”，编排改为“个百分点”。"""

nat_va, nat_va_g = 4343, 0.031
gd_va, gd_va_g = 538, 0.009
nat_prod, nat_prod_g = 3459.53, 0.021
gd_prod, gd_prod_g, gd_aq_g = 458.39, 0.007, 0.010
far_sea = 6.3
yrs = list(range(2018, 2023))
catch = [139.83, 126.36, 119.29, 118.8, 118.72]
aqua = [316.73, 329.13, 331.24, 336.24, 339.67]

print('== 本组自洽检查 ==')
tot = [c + a for c, a in zip(catch, aqua)]
print('2022年 捕捞+养殖 = %.2f（文字458.39）；海水产品增速 %.2f%%（文字0.7%%）；养殖增速 %.2f%%（文字1.0%%）'
      % (tot[4], (tot[4] / tot[3] - 1) * 100, (aqua[4] / aqua[3] - 1) * 100))
assert abs(tot[4] - gd_prod) < 0.005
print('未发现矛盾。')

print('\n== 第71题 ==')
print('3459.53/1.021×2.1%% = %.2f 万吨 -> C 60—80（现期×增速 %.2f，同样在C）' % (nat_prod / (1 + nat_prod_g) * nat_prod_g, nat_prod * nat_prod_g))

print('\n== 第72题 ==')
s22 = gd_va / nat_va
s21 = gd_va / (1 + gd_va_g) / (nat_va / (1 + nat_va_g))
print('海洋渔业增加值比重 2021年 %.3f%%、2022年 %.3f%%，变化 %.3f 个百分点 -> B 减少0.3' % (s21 * 100, s22 * 100, (s22 - s21) * 100))
print('公式：%.3f%%×(0.9%%−3.1%%)/1.009 = %.3f 个百分点' % (s22 * 100, s22 * (gd_va_g - nat_va_g) / (1 + gd_va_g) * 100))

print('\n== 第73题 ==')
print('(139.83−118.72)/139.83 = %.2f%% -> B 15%%；除以2022年 %.2f%% -> 最接近C 19%%'
      % ((catch[0] - catch[4]) / catch[0] * 100, (catch[0] - catch[4]) / catch[4] * 100))

print('\n== 第74题 ==')
sh = [a / t for a, t in zip(aqua, tot)]
print('养殖占比 %s，2018—2021年最高为2021年 -> D' % {y: round(s * 100, 2) for y, s in zip(yrs, sh)})
assert max(range(4), key=lambda i: sh[i]) == 3

print('\n== 第75题（选正确） ==')
print('A 2018年海水产品 %.2f，2022年 %.2f，增长 %.2f%% < 1%% 正确 -> A' % (tot[0], tot[4], (tot[4] / tot[0] - 1) * 100))
print('B 2021年养殖增速 %.2f%%，不是3.5%% 错误' % ((aqua[3] / aqua[2] - 1) * 100))
print('C 2019年海水产品变化 %.2f 万吨（减少）错误' % (tot[1] - tot[0]))
print('D 2022年远洋占捕捞 %.2f%%，2021年远洋产量未给出，推不出 错误' % (far_sea / catch[4] * 100))

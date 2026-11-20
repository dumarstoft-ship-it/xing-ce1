# -*- coding: utf-8 -*-
"""M11 第71—75题（GD2014-XJ-M1，广东改革开放以来经济与民生，纯文字材料）核算与本组检查。
文字与原卷第10页文字层一致；第74题A项原卷作“公路通车路程”，编排改为“公路通车里程”（与材料和其余三项一致）。"""

world, china, gd = 2.8, 9.8, 13.3
private_gdp, private_share = 29319.97, 0.514
private_tax, tax_share = 6467.82, 0.491
private_inv, inv_share = 10177.28, 0.527
transport = {'铁路营业里程': (2577, 1.6), '公路通车里程': (195000, 2.7),
             '民用航线里程': (1851000, 88.1), '管道输油（气）里程': (6448.01, 82.7)}   # 公里，增长倍数
port, port_x = 14.08, 49.5
hw11, hw12 = 5049, 5524
urban_exp, urban_x, rural_exp, rural_x = 22396.35, 55.0, 7458.56, 39.3
urban_area, urban_add, rural_area, rural_add = 34.4, 27.3, 31.67, 22.9

print('== 本组检查 ==')
print('民营经济÷51.4%%＝%.0f亿元（2012年广东GDP约5.7万亿，合理）；各段数据之间没有可互相核对而矛盾的地方。' % (private_gdp / private_share))

print('\n== 第71题 ==')
print('13.3/2.8 = %.3f -> C 4.8；误用中国 9.8/2.8 = %.2f -> B；广东/中国 %.2f -> A；相减 %.1f -> D'
      % (gd / world, china / world, gd / china, gd - world))

print('\n== 第72题 ==')
print('税收总额 6467.82/49.1%% = %.1f -> B 13173；配错比重：÷52.7%% = %.1f -> A；民间投资÷52.7%% = %.1f -> C；民营经济÷51.4%% = %.1f -> D'
      % (private_tax / tax_share, private_tax / inv_share, private_inv / inv_share, private_gdp / private_share))

print('\n== 第73题 ==')
print('(5524−5049)/5049 = %.3f%% -> A 9.4%%；5524/5049 = %.1f%% -> B；公路“增长2.7倍”误用 -> C 270%%、D 370%%'
      % ((hw12 / hw11 - 1) * 100, hw12 / hw11 * 100))

print('\n== 第74题 ==')
base = {k: v / (1 + x) for k, (v, x) in transport.items()}
for k, v in base.items():
    print('  1978年%s ≈ %.0f 公里' % (k, v))
order = sorted(base, key=base.get)
print('由小到大：%s -> A' % '＜'.join(order))
assert order == ['管道输油（气）里程', '铁路营业里程', '民用航线里程', '公路通车里程']
print('若公路与民用航线直接比2012年值（19.5万＜185.1万），得B的顺序')

print('\n== 第75题（选不正确） ==')
print('A 民间投资占比 %.1f%% > 50%% 正确' % (inv_share * 100))
print('B 吞吐量增长49.5倍，2012年 > 1978年（1978年约 %.2f 亿吨）正确' % (port / (1 + port_x)))
u78, r78 = urban_exp / (1 + urban_x), rural_exp / (1 + rural_x)
print('C 1978年城镇人均消费性支出 %.1f 元 > 农村 %.1f 元 正确' % (u78, r78))
ua, ra = urban_area - urban_add, rural_area - rural_add
print('D 1978年城镇人均住宅建筑面积 %.2f < 农村人均生活住房面积 %.2f 平方米，“比农村大”不正确 -> D' % (ua, ra))
assert ua < ra

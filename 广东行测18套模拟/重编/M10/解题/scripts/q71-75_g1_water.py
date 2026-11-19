# -*- coding: utf-8 -*-
"""M10 第71—75题（GD2020-XJ-M3，2019年广东规模以上工业企业用水）核算与本组自洽检查。
表格按原卷裁图 GD2020-XJ-p14-i02.png 逐格核对，与转写一致；文字与原卷第14—15页文字层一致。"""

use = {'自来水': 35.67, '地表淡水': 2.52, '地下淡水': 0.03, '其他水': 1.32}
total_use = 39.54
regions = {'珠三角': (29.85, -0.006, 0.755), '粤东': (2.46, -0.100, 0.062),
           '粤西': (2.96, -0.082, 0.075), '粤北': (4.27, -0.024, 0.108)}
reuse, reuse_g, reuse_rate = 147.10, 0.025, 0.788
ind = {'电力': (50.72, -0.013, 0.345), '冶金': (40.82, 0.039, 0.278), '石油石化': (32.12, 0.035, 0.218)}
firms_reuse, firms_share = 3573, 0.070
big_firms, big_share = 88, 0.962

print('== 本组自洽检查 ==')
s = sum(use.values())
print('分水种之和 %.2f（材料39.54）；自来水占比 %.2f%%（材料90.2%%）' % (s, use['自来水'] / total_use * 100))
assert abs(s - total_use) < 0.005
s = sum(v for v, _, _ in regions.values())
print('四地区之和 %.2f（材料39.54）' % s)
assert abs(s - total_use) < 0.005
for k, (v, r, sh) in regions.items():
    print('  %s 占比 %.2f%%（表%.1f%%）' % (k, v / total_use * 100, sh * 100))
    assert abs(v / total_use - sh) < 0.0006
rr = reuse / (reuse + total_use)
print('2019年重复用水率 %.2f%%（材料78.8%%）' % (rr * 100))
assert abs(rr - reuse_rate) < 0.0006
for k, (v, g, sh) in ind.items():
    print('  %s 占重复用水量 %.2f%%（材料%.1f%%）' % (k, v / reuse * 100, sh * 100))
    assert abs(v / reuse - sh) < 0.0006
print('规模以上工业企业约 %.0f 家；有重复用水企业占比7.0%%，无重复用水约%.0f%%（材料“九成多”）'
      % (firms_reuse / firms_share, (1 - firms_share) * 100))
print('88家大户：按“占全部重复用水量96.2%%”理解，合计 %.2f 亿立方米、平均 %.3f 亿立方米；其余%d家合计 %.2f 亿、平均 %.1f 万立方米'
      % (reuse * big_share, reuse * big_share / big_firms, firms_reuse - big_firms,
         reuse * (1 - big_share), reuse * (1 - big_share) / (firms_reuse - big_firms) * 1e4))
print('  （平均%.2f亿立方米远超1000万立方米，与“超过1000万立方米”一致；该句“仅占”与96.2%%字面矛盾，见第75题issues）'
      % (reuse * big_share / big_firms))

print('\n== 第71题 ==')
a = (use['地表淡水'] + use['地下淡水']) / total_use
print('(2.52+0.03)/39.54 = %.3f%%  -> B 6.4%%' % (a * 100))
print('只算地表淡水 %.2f%%；误含其他水 (2.52+0.03+1.32)/39.54 = %.2f%%，即1-90.2%%=9.8%% -> D'
      % (use['地表淡水'] / total_use * 100, (total_use - use['自来水']) / total_use * 100))

print('\n== 第72题 ==')
base = {k: v / (1 + r) for k, (v, r, _) in regions.items()}
dec = {k: base[k] - regions[k][0] for k in regions}
for k in regions:
    print('  %s 2018年 %.3f，减少 %.3f（现期×降幅近似 %.3f）' % (k, base[k], dec[k], -regions[k][0] * regions[k][1]))
use18 = sum(base.values())
print('2018年用水量 %.3f，2019年比2018年减少 %.3f 亿立方米 -> A 减少约0.8' % (use18, use18 - total_use))
# 上界：珠三角降0.6%，其余三地区合计不足10亿、降幅都不超过10%
ub = 29.85 * 0.006 / 0.994 + (2.46 + 2.96 + 4.27) * 0.10 / 0.90
print('上界估计：%.2f 亿立方米 < 2.8，C不可能' % ub)
avg_rate = sum(r for _, r, _ in regions.values()) / 4
print('（四地区增速简单平均 %.2f%%，按此算全省减少 %.2f，介于选项之间，不是干净的错误路径）'
      % (avg_rate * 100, total_use * -avg_rate / (1 + avg_rate)))

print('\n== 第73题 ==')
reuse18 = reuse / (1 + reuse_g)
r18 = reuse18 / (use18 + reuse18)
print('2018年重复用水量 %.3f，用水量 %.3f，重复用水率 %.3f%% -> A 78.0%%' % (reuse18, use18, r18 * 100))
assert r18 < reuse_rate
wrong = reuse * (1 + reuse_g) / (reuse * (1 + reuse_g) + (total_use - (use18 - total_use)))
print('方向弄反（重复用水量147.10×1.025、用水量39.54-0.82）：%.2f%% -> C 79.6%%' % (wrong * 100))
print('直接用2019年78.8% -> B')

print('\n== 第74题 ==')
b3 = {k: v / (1 + g) for k, (v, g, _) in ind.items()}
other18 = reuse18 - sum(b3.values())
print('2018年三大行业 %s，合计 %.3f；其他行业 %.3f，占 %.2f%% -> B 15%%'
      % ({k: round(v, 3) for k, v in b3.items()}, sum(b3.values()), other18, other18 / reuse18 * 100))
sh18 = {k: sh * (1 + reuse_g) / (1 + g) for k, (v, g, sh) in ind.items()}
print('按基期比重公式：%s，其他 %.2f%%' % ({k: round(v * 100, 2) for k, v in sh18.items()}, (1 - sum(sh18.values())) * 100))
print('2019年其他行业占比 %.1f%%（同样最接近15%%）' % ((1 - sum(sh for _, _, sh in ind.values())) * 100))

print('\n== 第75题 ==')
print('A 全省规模以上工业企业 3573/7.0%% = %.0f 家（约5.1万，不是4.3万）错误' % (firms_reuse / firms_share))
avg_b = reuse * 1e4 / firms_reuse
print('B 平均重复用水量 147.10亿/3573 = %.1f 万立方米（不是41.2万；0.0412亿误按×1000换算才得41.2）错误' % avg_b)
print('C 88家平均 147.10×96.2%%/88 = %.3f 亿；即使全算给88家也只有 %.3f 亿 < 1.8；1.8×88 = %.1f > 147.10 错误'
      % (reuse * big_share / big_firms, reuse / big_firms, 1.8 * big_firms))
lo = ind['电力'][0] / (ind['电力'][0] + total_use)
print('D 电力行业重复用水率 ≥ 50.72/(50.72+39.54) = %.2f%% > 50%% 正确 -> D' % (lo * 100))
assert lo > 0.5

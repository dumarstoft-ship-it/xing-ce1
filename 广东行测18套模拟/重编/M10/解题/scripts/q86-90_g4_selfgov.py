# -*- coding: utf-8 -*-
"""M10 第86—90题（GD2022-XZ-M1，基层群众性自治组织）核算与本组自洽检查。
堆积柱状图按原卷裁图 GD2022-XZ-p17-i01.png 核对数据标签，与转写一致；文字与原卷第16页一致。"""

yrs = list(range(2015, 2021))
vill = [58.1, 55.9, 55.4, 54.2, 53.3, 50.2]   # 村委会（万个）
resi = [10.0, 10.3, 10.6, 10.8, 11.0, 11.3]   # 居委会（万个）
T20, dec_rate, sh_v, sh_r = 61.5, 0.0435, 0.8163, 0.1837
groups_v, members_v, groups_r, members_r = 376.1, 207.3, 123.6, 61.6
elect = [9.7, 18.2, 27.6, 8.8, 6.1]           # 2016—2020年完成选举数（万个）
voters, voted = 1.1, 0.65                      # 亿人

print('== 本组自洽检查 ==')
tot = [a + b for a, b in zip(vill, resi)]
print('各年合计 %s；2020年 %.1f（文字61.5）' % ([round(t, 1) for t in tot], tot[-1]))
assert abs(tot[-1] - T20) < 1e-9
print('2020年同比 %.2f%%（文字减少4.35%%）；村委会占比 %.2f%%、居委会 %.2f%%（文字81.63%%、18.37%%）'
      % ((tot[-1] / tot[-2] - 1) * 100, vill[-1] / T20 * 100, resi[-1] / T20 * 100))
assert abs(tot[-1] / tot[-2] - 1 + dec_rate) < 0.0001 and abs(vill[-1] / T20 - sh_v) < 0.0001
print('未发现矛盾（“截止2020年底”应为“截至”，只是用字）。')

print('\n== 第86题 ==')
print('2019年 %.1f − 2020年 %.1f = %.1f 万个 -> B；由文字倒推 61.5×4.35%%/(1−4.35%%) = %.3f'
      % (tot[-2], tot[-1], tot[-2] - tot[-1], T20 * dec_rate / (1 - dec_rate)))

print('\n== 第87题 ==')
s19 = vill[-2] / tot[-2]
print('2019年村委会比重 %.3f%%，2020年 81.63%%（按图 %.3f%%），变化 %.3f（按图 %.3f）个百分点 -> A 降低约1.26'
      % (s19 * 100, vill[-1] / tot[-1] * 100, (sh_v - s19) * 100, (vill[-1] / tot[-1] - s19) * 100))
print('村委会降幅 %.2f%% 大于总数降幅 4.35%%，比重下降' % ((vill[-1] / vill[-2] - 1) * 100))

print('\n== 第88题 ==')
for i in range(1, 5):
    print('  %d年 增幅 %.1f%%，增加 %.1f 万个' % (2016 + i, (elect[i] / elect[i - 1] - 1) * 100, elect[i] - elect[i - 1]))
print('增幅最大2017年 -> A；增加个数最多是2018年（9.4>8.5）-> B 是误比增长量')

print('\n== 第89题 ==')
print('376.1/50.2 = %.3f -> C 7.5' % (groups_v / vill[-1]))

print('\n== 第90题 ==')
print('A 村民小组/居民小组 = %.2f 倍，不是5倍 错误' % (groups_v / groups_r))
print('B 平均每个村委会成员 207.3/50.2 = %.3f 人 > 4（50.2×4=%.1f<207.3）正确 -> B' % (members_v / vill[-1], vill[-1] * 4))
print('C 投票比例 0.65/1.1 = %.2f%% < 60%%（1.1×60%%=0.66）错误' % (voted / voters * 100))
print('D 村委会逐年减少 %s，居委会逐年增加 %s，趋势相反 错误'
      % (all(vill[i] < vill[i - 1] for i in range(1, 6)), all(resi[i] > resi[i - 1] for i in range(1, 6))))

# -*- coding: utf-8 -*-
"""M10 第81—85题（GD2021-XZ-M2，G省智能机器人产业，回忆整理版材料）逐题独立核算与本组自洽检查。
这组只有答案键“91--95 D.C.C.B.A”，没有解析，所以每题都按材料数据完整复算，并检查材料内部是否自洽。
两张表按原卷裁图 GD2021-XZ-p12-i01.png、p12-i02.png 核对，与转写一致（第二张表标题图中印作“产业园大行业”）。"""

ind = ['工业机器人', '特殊作业', '智能无人飞行器', '服务消费']
firms = [95, 4, 17, 24]
out = [76.88, 2.77, 201.07, 26.18]          # 总产值（亿元）
out_g = [0.574, 1.630, 0.317, -0.228]
rev = [48.62, 1.07, 233.07, 43.86]          # 营业收入（亿元）
rev_g = [0.275, 1.184, 0.460, 0.403]
prof = [-8.61, 0.22, 40.74, -0.9]           # 利润总额（亿元）
T_firms, T_out, T_out_g, gap_pp = 140, 306.90, 0.298, 32.8
T_rev, workers, workers_g = 326.62, 3.12, 0.086

print('== 本组自洽检查 ==')
print('企业数之和 %d（材料140）；总产值之和 %.2f（材料306.90）；营业收入之和 %.2f（材料326.62）'
      % (sum(firms), sum(out), sum(rev)))
assert sum(firms) == T_firms and abs(sum(out) - T_out) < 0.005 and abs(sum(rev) - T_rev) < 0.005
b_out = [v / (1 + g) for v, g in zip(out, out_g)]
print('总产值分行业基期之和 %.2f；由306.90÷1.298倒推 %.2f（差%.2f，属四舍五入）' % (sum(b_out), T_out / (1 + T_out_g), sum(b_out) - T_out / (1 + T_out_g)))
assert abs(sum(b_out) - T_out / (1 + T_out_g)) < 0.2
b_rev = [v / (1 + g) for v, g in zip(rev, rev_g)]
print('营业收入基期之和 %.2f，整体增速 %.2f%%（材料“超40%%”）；四个行业营收增速都为正（材料“均实现正增长”）'
      % (sum(b_rev), (T_rev / sum(b_rev) - 1) * 100))
assert T_rev / sum(b_rev) - 1 > 0.40 and min(rev_g) > 0
print('全部规模以上工业产值增速 29.8%%−32.8个百分点 = %.1f%%；306.90÷0.3%% ≈ %.0f 亿元' % (T_out_g * 100 - gap_pp, T_out / 0.003))

print('\n== 第81题 ==')
inc = [v - b for v, b in zip(out, b_out)]
order = sorted(range(4), key=lambda i: -inc[i])
print('总产值同比增量：%s' % {ind[i]: round(inc[i], 3) for i in range(4)})
print('排序 %s -> D ③>①>②>④' % '>'.join('①②③④'[i] for i in order))
assert order == [2, 0, 1, 3]
print('按增长率排序为 %s（不在选项中）；只用增速比①③会得①>③ -> A' %
      '>'.join('①②③④'[i] for i in sorted(range(4), key=lambda i: -out_g[i])))

print('\n== 第82题 ==')
avg = [v / n for v, n in zip(out, firms)]
print('平均每个企业产值：%s -> C' % {ind[i]: round(avg[i], 3) for i in range(4)})
assert max(range(4), key=lambda i: avg[i]) == 2

print('\n== 第83题 ==')
P = sum(prof)
print('利润总额合计 %.2f，总体利润率 %.2f%% -> C 9.6%%' % (P, P / T_rev * 100))
m = [p / r for p, r in zip(prof, rev)]
print('各行业利润率 %s，简单平均 %.2f%% -> B 4.6%%' % ([round(x * 100, 2) for x in m], sum(m) / 4 * 100))
print('负利润当正数相加 %.2f/326.62 = %.2f%% -> 最接近D 14.6%%' % (sum(abs(p) for p in prof), sum(abs(p) for p in prof) / T_rev * 100))

print('\n== 第84题 ==')
g = rev[0] - b_rev[0]
print('工业机器人营业收入增长量 48.62×0.275/1.275 = %.3f 亿元 -> B 10' % g)
print('1/n近似：27.5%%≈1/3.64，48.62/4.64 = %.2f' % (48.62 / 4.64))
print('现期×增速 48.62×27.5%% = %.2f -> 最接近C 15' % (rev[0] * rev_g[0]))

print('\n== 第85题（选不正确） ==')
print('A 全部规模以上工业产值增速 = %.1f%%（下降3%%），“增长3%%”不正确 -> A' % (T_out_g * 100 - gap_pp))
print('B 2019年前三季度营业收入 = %.2f 亿元 > 200（仅无人飞行器+工业机器人+服务消费三项基期 %.1f）正确'
      % (sum(b_rev), b_rev[2] + b_rev[0] + b_rev[3]))
print('C 平均用工人数基期 3.12/1.086 = %.3f 万人 正确' % (workers / (1 + workers_g)))
print('D 利润率 %s，特殊作业最高 正确' % {ind[i]: round(m[i] * 100, 2) for i in range(4)})
assert max(range(4), key=lambda i: m[i]) == 1
print('\n五题：D C C B A，与答案键“91--95 D.C.C.B.A”一致。')

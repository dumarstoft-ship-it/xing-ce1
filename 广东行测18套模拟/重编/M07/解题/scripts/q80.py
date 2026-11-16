"""第80题：选出错误的说法。"""
from q76_80_group2_data import y24, rev_g24, rev_g23, regions
# A：2024年1-2月至1-6月各累计期，利润率同比是否均下降：利润增速 < 收入增速 即下降
print('A：')
allDown = True
for m in range(2, 7):
    pg, rg = y24[m][2], rev_g24[m]
    down = pg < rg
    allDown &= down
    print(f'  1-{m}月 利润增速 {pg}% vs 收入增速 {rg}% -> 利润率{"下降" if down else "上升"}；'
          f'利润率由 {100*(y24[m][1]/(1+pg/100))/(y24[m][0]/(1+rg/100)):.2f}% 变为 {100*y24[m][1]/y24[m][0]:.2f}%')
print('  A正确' if allDown else '  A错误')
# B：二季度利润/一季度利润
q2 = y24[6][1] - y24[3][1]; q1 = y24[3][1]
print(f'B：二季度利润 = 743.7-278.9 = {q2:.1f}；比值 {q2:.1f}/{q1} = {q2/q1:.3f} ≈ 1.7 -> B正确')
# C：2023年4月收入 vs 3月
r23 = {m: y24[m][0]/(1+rev_g24[m]/100) for m in range(2, 7)}
apr = r23[4]-r23[3]; mar = r23[3]-r23[2]
print(f'C：2023年1-2月 {r23[2]:.1f}，1-3月 {r23[3]:.1f}，1-4月 {r23[4]:.1f}；3月 {mar:.1f}，4月 {apr:.1f} -> 4月{"高于" if apr > mar else "低于"}3月，C正确')
# 估算：1-4月≈5547/1.037≈5349；1-3月≈3840/1.084≈3542；1-2月≈2463/1.076≈2289
# D：同比变化幅度（增速绝对值）
amp = {k: abs(g) for k, (v, g) in regions.items()}
print('D：各地区增速', {k: round(g, 1) for k, (v, g) in regions.items()}, '变化幅度最大：', max(amp, key=amp.get), '-> D错误')
# 对照：若按增长量（绝对量）看
east = 8676-408.8-525.4-20.8
incs = {'东部': east - east/1.052, '中部': 408.8-408.8/1.12, '西部': 525.4-525.4/1.046, '东北': 20.8-20.8/0.979}
print('（对照）各地区增长量：', {k: round(v, 1) for k, v in incs.items()})

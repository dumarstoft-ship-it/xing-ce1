"""改写资料题 第82题（两期比重）、第89题（增量排序）的计算。"""

# ---------- 第82题 ----------
total, g_total = 3309354, 0.301
items = {'进出境汽车': (2828439, 0.328), '进出境火车': (376851, 0.098),
         '进出境船舶': (34604, 0.109), '进出境飞机': (69460, 0.793)}
print('第82题  分项之和=', sum(v for v, _ in items.values()), ' 表中总数=', total)
base_total = total / (1 + g_total)
for k, (v, g) in items.items():
    now = v / total
    base = (v / (1 + g)) / base_total
    # 公式：现期比重×(a-b)/(1+a)
    formula = now * (g - g_total) / (1 + g)
    print(f'  {k}：现期比重{now*100:.3f}%  上年同期{base*100:.3f}%  变化{(now-base)*100:+.3f}个百分点'
          f'（公式{formula*100:+.3f}）  比重的相对变化{((1+g)/(1+g_total)-1)*100:+.1f}%')
best = max(items, key=lambda k: items[k][0] / total * (items[k][1] - g_total) / (1 + items[k][1]))
print('  比重上升百分点最多：', best)

# ---------- 第89题 ----------
T, gT = 8823, 0.0275
wood, gw = 2312, 0.0931
recyc, gr = 5936, 0.0037
nonwood = T - wood - recyc
gn = 0.0305
inc = {'木浆': wood * gw / (1 + gw), '非木浆': nonwood * gn / (1 + gn), '再生纸浆': recyc * gr / (1 + gr)}
print(f'\n第89题  非木浆产量 = 8823-2312-5936 = {nonwood} 万吨')
for k, v in inc.items():
    print(f'  {k}同比增量 ≈ {v:.2f} 万吨')
print(f'  表中木浆 2023-2022 = {2312 - 2115}；总量增量 {T*gT/(1+gT):.2f}，三项之和 {sum(inc.values()):.2f}')
print('  从多到少：', '、'.join(sorted(inc, key=lambda k: -inc[k])))

# -*- coding: utf-8 -*-
"""M08 资料第2组（第76—80题）：全国国内旅游。数据自洽检查 + 第76—80题核算。"""

years = list(range(2015, 2024))
trips = dict(zip(years, [39.9, 44.4, 50.0, 55.4, 60.1, 28.8, 32.5, 25.3, 48.9]))   # 亿人次
spend = dict(zip(years, [3.4, 3.9, 4.6, 5.1, 5.7, 2.2, 2.9, 2.0, 4.9]))           # 万亿元

# 文字材料（2023年）
agencies, profit = 56275, 37.4            # 家，亿元
trips23, g_trips = 48.9, 0.933
urban_trips23, g_urban_trips = 37.6, 0.949
spend23, g_spend = 4.9, 1.403
urban_spend23, g_urban_spend = 4.2, 1.475
rural_spend23, g_rural_spend = 0.7, 1.064

print("== 自洽检查 ==")
print(f"2022出游人次（由增速反推）= 48.9/1.933 = {trips23/(1+g_trips):.3f}，表中 {trips[2022]}")
print(f"2022总花费（由增速反推）= 4.9/2.403 = {spend23/(1+g_spend):.4f}，表中 {spend[2022]}")
print(f"表中2023/2022：人次 {trips[2023]/trips[2022]-1:.2%}（文 93.3%），花费 {spend[2023]/spend[2022]-1:.2%}（文 140.3%，差异来自2.0的取整）")
print(f"城镇+农村花费 = {urban_spend23+rural_spend23:.1f}（总 4.9）")
u22 = urban_spend23 / (1 + g_urban_spend)
r22 = rural_spend23 / (1 + g_rural_spend)
print(f"2022城镇花费 {u22:.4f} + 农村 {r22:.4f} = {u22+r22:.4f}（总花费反推 {spend23/(1+g_spend):.4f}，表 2.0）")
ut22 = urban_trips23 / (1 + g_urban_trips)
print(f"2022城镇人次 {ut22:.3f}，农村人次 {trips[2022]-ut22:.3f}；2023农村人次 {trips23-urban_trips23:.1f}")

print("\n== 第76题 ==")
a23 = spend[2023] * 1e12 / (trips[2023] * 1e8)
a22 = spend[2022] * 1e12 / (trips[2022] * 1e8)
print(f"2023人均每次 {a23:.1f} 元，2022 {a22:.1f} 元，增长 {a23/a22-1:.2%}")
print(f"按文字增速：2.403/1.933-1 = {(1+g_spend)/(1+g_trips)-1:.2%}")

print("\n== 第77题 ==")
ratio = u22 / r22
print(f"2022城镇/农村 = {u22:.4f}/{r22:.4f} = {ratio:.3f} 倍，多 {ratio-1:.3f} 倍")
print(f"若用2023年：4.2/0.7 = {urban_spend23/rural_spend23:.2f} 倍，多 {urban_spend23/rural_spend23-1:.2f} 倍")
# 用统计公报两位小数的真实值（4.18、0.74）看稳健性
print(f"（稳健性：若用4.18、0.74：{4.18/2.475/(0.74/2.064):.3f} 倍）")
r22_sub = spend[2022] - u22
print(f"（另一途径：表中2022总花费2.0减城镇基期{u22:.4f}得农村{r22_sub:.4f}，倍数 {u22/r22_sub:.3f}，多 {u22/r22_sub-1:.2f} 倍——2.0是取整值，误差被放大）")

print("\n== 第78题 ==")
ua23 = urban_spend23 * 1e12 / (urban_trips23 * 1e8)
ua22 = u22 * 1e12 / (ut22 * 1e8)
print(f"2023城镇人均每次 {ua23:.1f} 元，2022 {ua22:.1f} 元，变化 {ua23-ua22:+.1f} 元；增速 {(1+g_urban_spend)/(1+g_urban_trips)-1:.2%}")
print(f"基期平均数×增速 = {ua22*((1+g_urban_spend)/(1+g_urban_trips)-1):.1f}")
print(f"易错：万亿÷亿只乘10^3：2023 {ua23/10:.1f}、2022 {ua22/10:.1f}，差 {(ua23-ua22)/10:.1f} 元 → 不到100元（C）")

print("\n== 第79题 ==")
cnt, cnt_up = 0, 0
for y in range(2018, 2024):
    g = spend[y] / spend[y - 1] - 1
    flag = abs(g) > 0.5
    cnt += flag
    cnt_up += g > 0.5
    print(f"{y}: {spend[y-1]}→{spend[y]} 同比 {g:+.2%} {'>50%' if flag else ''}")
print(f"变化幅度(绝对值)超过50%：{cnt} 个；只数增长超过50%：{cnt_up} 个")

print("\n== 第80题 ==")
per = profit * 1e8 / agencies
print(f"A 平均每家旅行社营业利润 = 37.4亿/56275 = {per:.0f} 元 = {per/1e4:.2f} 万元 > 60万 ? {per > 6e5}；量级多乘10得 {per*10/1e4:.1f} 万元")
print(f"B 城镇人次增速94.9% > 总增速93.3% → 城镇比重上升、农村比重下降；"
      f"农村人次增速 = {(trips23-urban_trips23)/(trips[2022]-ut22)-1:.2%}；"
      f"农村比重 2022 {(trips[2022]-ut22)/trips[2022]:.2%} → 2023 {(trips23-urban_trips23)/trips23:.2%}")
s135 = sum(trips[y] for y in range(2016, 2021))
print(f"C 十三五(2016-2020)出游人次合计 {s135:.1f} 亿，月均 {s135/60:.3f} 亿")
s_wrong = sum(trips[y] for y in range(2015, 2020))
print(f"  （若误用2015-2019：{s_wrong:.1f}/60 = {s_wrong/60:.3f}）")
mx = max(range(2018, 2023), key=lambda y: spend[y])
incs = {y: round(spend[y] - spend[y - 1], 2) for y in range(2018, 2023)}
print(f"D 2018-2022总花费最多的年份 {mx}（{spend[mx]}），各年增量 {incs}，增量最多 {max(incs, key=incs.get)}")

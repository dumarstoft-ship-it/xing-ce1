# -*- coding: utf-8 -*-
"""M08 资料第4组（第86—89题）：全国铁路货运。数据自洽检查 + 第86—89题核算（第90题另见 q90_chart.py）。"""

ship = {2018: 409268, 2019: 441213, 2020: 455236, 2021: 477372, 2022: 498424, 2023: 503535}  # 万吨

# 文字材料（2023年）
total23, inc23, g_total = 50.35, 0.51, 0.010          # 亿吨
nat23, g_nat = 39.11, 0.002                            # 国家铁路发送量
g_oth = 0.039                                          # 其他铁路发送量增速
coal, g_coal = 278101, 0.019
metal, g_metal = 90986, -0.053
oil, g_oil = 13050, 0.054
grain, g_grain = 6847, -0.080
tk23, tk_inc = 36460.39, 514.70                        # 亿吨公里
tk_nat23, g_tk_nat = 32638.50, -0.001
tk_oth23, g_tk_oth = 3821.89, 0.166

print("== 自洽检查 ==")
print(f"表2023 {ship[2023]} 万吨 = {ship[2023]/1e4:.4f} 亿吨（文 50.35）；增量 {ship[2023]-ship[2022]} 万吨（文 0.51亿吨）；"
      f"增速 {ship[2023]/ship[2022]-1:.3%}（文 1.0%）")
oth23 = total23 - nat23
nat22, oth22 = nat23 / (1 + g_nat), oth23 / (1 + g_oth)
print(f"其他铁路发送量2023 = 50.35-39.11 = {oth23:.2f}；2022 国家 {nat22:.3f} + 其他 {oth22:.3f} = {nat22+oth22:.3f}（表 {ship[2022]/1e4:.4f}）")
print(f"周转量：国家+其他 = {tk_nat23+tk_oth23:.2f}（文 {tk23}）")
tk22 = tk23 - tk_inc
tk_nat22, tk_oth22 = tk_nat23 / (1 + g_tk_nat), tk_oth23 / (1 + g_tk_oth)
print(f"2022周转量：总 {tk22:.2f}；国家 {tk_nat22:.2f} + 其他 {tk_oth22:.2f} = {tk_nat22+tk_oth22:.2f}（差 {tk_nat22+tk_oth22-tk22:+.2f}，增速取整误差范围内）")
print(f"总周转量增速 {tk_inc/tk22:.3%}")
print(f"四个品类合计 {coal+metal+oil+grain} 万吨 < 总发送量 {ship[2023]}")

print("\n== 第86题 ==")
d = (oil - grain) / 12
print(f"(13050-6847)/12 = {oil-grain}/12 = {d:.2f} 万吨")
oil22, grain22 = oil / (1 + g_oil), grain / (1 + g_grain)
print(f"误用上年：石油 {oil22:.1f}，粮食 {grain22:.1f}，月均差 {(oil22-grain22)/12:.2f}")
print(f"误不除12：{oil-grain}；误用和：{(oil+grain)/12:.1f}")

print("\n== 第87题 ==")
r_nat = (1 + g_tk_nat) / (1 + g_nat) - 1
r_oth = (1 + g_tk_oth) / (1 + g_oth) - 1
print(f"国家铁路平均运距变化 = 0.999/1.002-1 = {r_nat:+.3%}")
print(f"其他铁路平均运距变化 = 1.166/1.039-1 = {r_oth:+.3%}")
print(f"易错：公式颠倒（发送量÷周转量）：国家 {(1+g_nat)/(1+g_tk_nat)-1:+.3%}，其他 {(1+g_oth)/(1+g_tk_oth)-1:+.3%} → 仅①上升（A）")
print(f"国家：2023 {tk_nat23/nat23:.1f} 公里，2022 {tk_nat22/nat22:.1f} 公里；"
      f"其他：2023 {tk_oth23/oth23:.1f} 公里，2022 {tk_oth22/oth22:.1f} 公里")

print("\n== 第88题 ==")
sh22 = tk_nat22 / tk22
sh23 = tk_nat23 / tk23
print(f"2022国家铁路周转量 = 32638.50/0.999 = {tk_nat22:.2f}；全国 = 36460.39-514.70 = {tk22:.2f}；比重 {sh22:.3%}")
print(f"基期比重公式：{sh23:.4%}×(1+{tk_inc/tk22:.4%})/(1-0.1%) = {sh23*(1+tk_inc/tk22)/(1+g_tk_nat):.3%}")
print(f"误用2023年比重：{sh23:.3%}；误用发送量比重：2023 {nat23/total23:.3%}，2022 {nat22/(ship[2022]/1e4):.3%}")
print(f"若用其他铁路基期反推总量：{tk_nat22/(tk_nat22+tk_oth22):.3%}")

print("\n== 第89题 ==")
a = (ship[2023] - ship[2020]) / 3 / 1e4
print(f"(503535-455236)/3 = {(ship[2023]-ship[2020])} / 3 = {a:.4f} 亿吨")
print(f"误除以4：{(ship[2023]-ship[2020])/4/1e4:.3f}；以2019为基期/4：{(ship[2023]-ship[2019])/4/1e4:.3f}；"
      f"以2019为基期/3：{(ship[2023]-ship[2019])/3/1e4:.3f}；2020-2022/2：{(ship[2022]-ship[2020])/2/1e4:.3f}")

# -*- coding: utf-8 -*-
"""M08 资料第1组（第71—75题）：广东省职业教育。数据自洽检查 + 第73—75题核算。"""

# 材料数据
total_schools_2022 = 625          # 所
total_students_2022 = 280.5       # 万人
zk_schools_2022 = 93              # 专科层次职业学校，所
zk_students_2022 = 125.4          # 万人
g_schools = 0.192                 # 比2011年增长
g_students = 0.831
zk_share_higher_edu = 0.501       # 专科层次在校生占全省高等教育在校生
bk_schools, bk_students = 2, 1.9  # 本科层次职业学校
shuanggao, shifan_zz, jishi = 14, 62, 10
train_total = 797                 # 三大工程累计培训，万人次

print("== 自洽检查 ==")
zk_schools_2011 = zk_schools_2022 / (1 + g_schools)
print(f"2011年专科学校数 = 93/1.192 = {zk_schools_2011:.3f}（应接近整数）")
for n in (77, 78, 79):
    print(f"  若2011年为{n}所，增长率 = {zk_schools_2022/n-1:.4%}")
zk_students_2011 = zk_students_2022 / (1 + g_students)
print(f"2011年专科在校生 = 125.4/1.831 = {zk_students_2011:.3f} 万人")
higher_edu = zk_students_2022 / zk_share_higher_edu
print(f"2022年全省高等教育在校生 = 125.4/0.501 = {higher_edu:.2f} 万人")
print(f"专科+本科层次在校生 = {zk_students_2022+bk_students:.1f} 万人 < 职业院校在校生 {total_students_2022}；"
      f"其余（中职等）{total_students_2022-zk_students_2022-bk_students:.1f} 万人")

print("\n== 第73题 ==")
print(f"A 2011年专科学校 = {zk_schools_2011:.2f} 所 > 75 ? {zk_schools_2011 > 75}")
print("B 白天鹅宾馆中高职毕业生占68% > 70% ? ", 0.68 > 0.70)
print("C 10所高水平技师学院是“十八大至2022年十年间”累计建设，不是2022年当年 → 错")
print(f"D 非专科层次职业院校 = 625-93 = {total_schools_2022-zk_schools_2022}（≠432）；"
      f"若再去掉本科层次2所 = {total_schools_2022-zk_schools_2022-bk_schools}")

print("\n== 第74题 ==")
inc = zk_students_2022 * g_students / (1 + g_students)
print(f"增长量 = 125.4×0.831/1.831 = {inc:.3f} 万人")
print(f"错误：直接乘增长率 125.4×0.831 = {zk_students_2022*g_students:.2f}")
print(f"错误：求成2011年在校生 125.4/1.831 = {zk_students_2011:.2f}，最接近选项：",
      min([50.3, 56.9, 62.1, 69.2], key=lambda x: abs(x - zk_students_2011)))
print(f"估算：0.831/1.831 ≈ 0.454；125.4×0.454 = {125.4*0.454:.2f}")

print("\n== 第75题 ==")
print(f"A 高等教育在校生 = {higher_edu:.2f} 万人 < 260 ? {higher_edu < 260}")
print(f"B 示范中职-双高高职 = {shifan_zz-shuanggao}（=48）")
avg = total_students_2022 * 1e4 / total_schools_2022
print(f"C 平均每所职业院校在校生 = 2805000/625 = {avg:.1f} 人 ≥ 4000 ? {avg >= 4000}")
print("D 材料只给三大工程合计培训797万人次，无分项 → 无法推出")
print(f"易错：若把职业院校在校生{total_students_2022}万人当成高等教育在校生，{total_students_2022} < 260 ? {total_students_2022 < 260} → 会认为A不成立而误选A")

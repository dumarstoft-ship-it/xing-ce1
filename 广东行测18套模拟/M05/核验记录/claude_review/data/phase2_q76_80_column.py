# -*- coding: utf-8 -*-
"""第二阶段：第76—80题"同比增长"列——删去转写附注后，按'绝对增量'与按'百分比'两种读法各题结论对比。只读 M05/题目.jsonl。"""
import json
from fractions import Fraction as F
M05 = "/home/user/xing-ce1/广东行测18套模拟/M05/题目.jsonl"
Q = {r["number"]: r for r in (json.loads(l) for l in open(M05, encoding="utf-8") if l.strip())}
tb = [b for b in Q[76]["materials"][0]["blocks"] if b["type"] == "table"][0]
print("M05 表头：", tb["headers"], "；notes 字段：", tb.get("notes", "（无）"))
T = {r[0]: [F(x.replace("−", "-")) if i >= 2 else x for i, x in enumerate(r)] for r in tb["rows"]}
imp, exp_, tot, io = T["监管进口货运量"], T["监管出口货运量"], T["监管运输工具总数"], T["监管进出境总数"]
car, rail, ship, air = T["其中：进出境汽车"], T["进出境火车"], T["进出境船舶"], T["进出境飞机"]

def base_abs(cur, inc): return cur - inc
def base_pct(cur, g): return cur / (1 + g / 100)

print("\n一、若读作百分比，'增长率'数值本身：")
for k, r in T.items():
    print("   %-10s 9月 %s%%   1—9月 %s%%" % (k, r[3], r[5]))
print("   → 1018%、11001%、7531496% 等不可能是同比增速；仅出口 9月 −55% 单看似可能，但同表进口为 1018%，整体不成立。")

print("\n二、各题两种读法：")
# Q76
a = base_abs(imp[2], imp[3]) + base_abs(exp_[2], exp_[3]); p = base_pct(imp[2], imp[3]) + base_pct(exp_[2], exp_[3])
print("76 绝对增量：%s → A；百分比读法：%.1f → 不对应任何选项（46161/46051/31870/29830）" % (a, float(p)))
# Q77
rates_abs = {k: r[5] / (r[4] - r[5]) for k, r in (("汽车", car), ("火车", rail), ("船舶", ship), ("飞机", air))}
rates_pct = {k: r[5] for k, r in (("汽车", car), ("火车", rail), ("船舶", ship), ("飞机", air))}
ra = sorted(rates_abs, key=rates_abs.get, reverse=True); rp = sorted(rates_pct, key=rates_pct.get, reverse=True)
print("77 绝对增量：排序 %s → 第二 %s（B）；百分比读法：排序 %s → 第二 %s（A，等同'只比增量'的经典陷阱）" % (ra, ra[1], rp, rp[1]))
print("78 不用增长列，两种读法同为 C")
# Q79
r_abs = base_abs(imp[4], imp[5]) / base_abs(exp_[4], exp_[5]); r_pct = base_pct(imp[4], imp[5]) / base_pct(exp_[4], exp_[5])
print("79 绝对增量：%.4f → B；百分比读法：%.4f → 不接近任何选项（最近 D 1.53 也差 0.49）" % (float(r_abs), float(r_pct)))
# Q80
A_abs = base_abs(car[2], car[3]) / base_abs(io[2], io[3]); A_pct = base_pct(car[2], car[3]) / base_pct(io[2], io[3])
B_abs = tot[5] - tot[3]
C_abs = rail[3] / tot[3]
print("80 绝对增量：A %.2f%%（假）B %s（假）C %.2f%%（假）D 2430122（真）→ D 唯一" % (float(A_abs * 100), B_abs, float(C_abs * 100)))
print("   百分比读法：A %.2f%%（假）；B 选项本身写'同比增长不足700万辆艘'——以'辆艘'计量'同比增长'，题面自证该列为绝对增量；C 贡献率无法用百分率直接求；D 不涉增长列 → 仍为 D" % float(A_pct * 100))

print("\n三、材料与题面自身的识别线索：")
print("   1. 单位列（万吨/辆艘/辆/节/艘/架）按行给出，且增长列未标%或（%）；")
print("   2. 1—9月累计同比增长 7531496、6432622 等量级只能是绝对量；进出境四项增量之和 = 进出境总数增量（9月 413997、1—9月 7163173），百分率不可相加，绝对量可加；")
s9 = car[3] + rail[3] + ship[3] + air[3]; s19 = car[5] + rail[5] + ship[5] + air[5]
print("      实算：9月 %s = %s；1—9月 %s = %s" % (s9, io[3], s19, io[5]))
print("   3. 第76题四个选项都是万吨整数，且 46161/46051 只在绝对增量读法下出现；第80题B项'同比增长不足700万辆艘'。")
print("\n结论：删去转写附注后，考生能从材料本身判定该列为绝对增量；误读为百分比只会得到荒谬值或经典陷阱选项（77题A），不产生两解。")

"""M08换入题复算：第43题（ZJ2024-A类-061，行程）、第45题（ZJ2021-A类-056，构造最值）、
第54题（JS2020-A类-097，分析推理）。图形题见 swap_q48_grid.py、swap_q49_fold.py。"""
from fractions import Fraction as F
from itertools import permutations

# 第43题：骑行速度记为1（每小时1份路程），开车5。同行1小时后休息1/3小时；
# 甲继续骑；乙骑回A地（1小时），再开车到B。乙比甲早到12分钟。设AB＝D。
# 甲用时：1＋1/3＋(D－1)；乙用时：1＋1/3＋1＋D/5；二者差1/5小时。
D = (F(1) + F(1) + F(1, 5)) / (1 - F(1, 5))        # D－1－1－D/5＝1/5
t_jia = 1 + F(1, 3) + (D - 1)
print("第43题：AB＝", D, "份；甲全程", t_jia * 60, "分钟")
assert t_jia * 60 == 185
# 易错：漏算中途休息的20分钟
print("  漏算休息：", (t_jia - F(1, 3)) * 60, "分钟 → 误选A")
assert (t_jia - F(1, 3)) * 60 == 165

# 第45题：A＝B＋4，C＝45×1/5＝9，D不超过任何其他地区；求A的最小值（枚举全部整数分配）
best = None
for B in range(0, 46):
    A = B + 4
    Dd = 45 - 9 - A - B
    if Dd < 0:
        continue
    if Dd <= min(A, B, 9):
        best = A if best is None else min(best, A)
print("第45题：A地区至少", best, "人")
assert best == 16
print("  D＝9时：2B＝36－9－4＝23，B不是整数；D＝8时B＝12、A＝16")
# 易错：只记得D不超过A、B，忘了D也不能超过C的9人
alt = min(B + 4 for B in range(0, 46) if 0 <= 45 - 9 - (B + 4) - B <= min(B + 4, B))
print("  忽略D≤C时A至少", alt, "人（此时D＝10＞9）→ 误选C")
assert alt == 15

# 第54题：5人分到5个窗口，各负责自己熟悉的业务
know = {"小丽": {"登记"}, "小马": {"登记", "咨询"}, "小高": {"报送", "投诉"},
        "老王": {"登记", "咨询", "报送"}, "老董": {"登记", "咨询", "报送", "投诉", "综合"}}
people = list(know)
wins = ["登记", "咨询", "报送", "投诉", "综合"]
sols = [dict(zip(people, p)) for p in permutations(wins) if all(w in know[x] for x, w in zip(people, p))]
print("第54题：可行安排", len(sols), "种：", sols)
opts = {"A": lambda s: s["老董"] != "综合", "B": lambda s: s["小高"] == "报送",
        "C": lambda s: s["小马"] != "咨询", "D": lambda s: s["老王"] == "报送"}
right = [k for k, f in opts.items() if all(f(s) for s in sols)]
print("  必然正确：", right)
assert right == ["D"]

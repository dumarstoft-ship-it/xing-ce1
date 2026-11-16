# 第37题：甲队完成的工作量比乙队多1/6，乙队效率比甲队快1/8，甲队所用时间比乙队多（以乙为基准）？
# 题面转写中 1/6 被错放到句首；按原卷版面应在“比乙队多”之后（见 issues）。
from fractions import Fraction as F
W_jia, W_yi = F(7), F(6)      # 工作量 7:6
e_jia, e_yi = F(8), F(9)      # 效率 8:9
t_jia, t_yi = W_jia / e_jia, W_yi / e_yi
ans = (t_jia - t_yi) / t_yi
print("t甲=%s t乙=%s  t甲/t乙=%s  多出 %s" % (t_jia, t_yi, t_jia / t_yi, ans))
assert ans == F(5, 16)
options = {"A": F(5, 16), "B": F(7, 16), "C": F(5, 12), "D": F(7, 12)}
print("命中选项:", [k for k, v in options.items() if v == ans])

# 常见误读能否落到其他选项
alts = {
    "以甲的时间为基准": (t_jia - t_yi) / t_jia,
    "把'乙快1/8'读成甲效率=7/8乙": (W_jia / 7) / (W_yi / 8) - 1,
    "把'甲多1/6'读成乙=5/6甲": (F(6) / 8) / (F(5) / 9) - 1,
    "把'多1/6'当成总量的1/6（甲7/12、乙5/12）": (F(7, 12) / 8) / (F(5, 12) / 9) - 1,
}
for name, v in alts.items():
    hit = [k for k, o in options.items() if o == v]
    print(name, "->", v, hit)
print("1/6 若错放在别处，题面将缺少工作量关系，无法求解。")

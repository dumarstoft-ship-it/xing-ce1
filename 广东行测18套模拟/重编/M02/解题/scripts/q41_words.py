"""第41题：6月共30天。前15天每天比前一天多背5个；第16天到月底每天相同，比第1天多45个；
全月共1500个。求第1天背的个数。 选项 A8 B9 C10 D11

核验：逐一代入选项按天累加；并枚举 1~100 确认唯一解。
"""
options = {"A": 8, "B": 9, "C": 10, "D": 11}


def total(a):
    first15 = [a + 5 * i for i in range(15)]      # 第1~15天
    rest = [a + 45] * 15                           # 第16~30天
    return sum(first15) + sum(rest), first15[-1]


for k, a in options.items():
    t, d15 = total(a)
    print(k, a, "全月合计", t, "（第15天%d个）" % d15, "符合" if t == 1500 else "")
print("1~100 中满足合计1500的第1天个数:", [a for a in range(1, 101) if total(a)[0] == 1500])

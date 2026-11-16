"""第35题：1015，1816，2221，1933，（ ）  选项 A2977 B5831 C3726 D4615

核验思路：四位数机械拆分。试几种拆法（前两位/后两位的和、差、积，各位数字和等），
看哪种拆法形成规律，再检查四个选项中有几个符合。
"""
seq = [1015, 1816, 2221, 1933]
options = {"A": 2977, "B": 5831, "C": 3726, "D": 4615}


def split2(x):
    return x // 100, x % 100


def digits(x):
    return [int(c) for c in str(x)]


rules = {
    "前两位+后两位": lambda x: sum(split2(x)),
    "前两位-后两位": lambda x: split2(x)[0] - split2(x)[1],
    "前两位×后两位": lambda x: split2(x)[0] * split2(x)[1],
    "各位数字和": lambda x: sum(digits(x)),
    "前两位": lambda x: split2(x)[0],
    "后两位": lambda x: split2(x)[1],
}
for name, f in rules.items():
    vals = [f(x) for x in seq]
    d = [vals[i + 1] - vals[i] for i in range(len(vals) - 1)]
    print(name, vals, "一级差", d, "  选项值:", {k: f(v) for k, v in options.items()})

# 规律：前两位+后两位 = 25,34,43,52（公差9），下一项应为61
target = sum(split2(seq[-1])) + 9
print("下一项的前两位+后两位应为", target)
print("满足的选项:", [k for k, v in options.items() if sum(split2(v)) == target])

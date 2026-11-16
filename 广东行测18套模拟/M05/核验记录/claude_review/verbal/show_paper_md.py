# 只读：显示 题本_待审.md 第16—30题原始行（空白可见：行尾两空格=硬换行，␣=空格）
import re
P = "/home/user/xing-ce1/广东行测18套模拟/M05/题本_待审.md"
lines = open(P, encoding="utf-8").read().split("\n")
start = next(i for i, l in enumerate(lines) if l.strip() == "### 16.")
end = next(i for i, l in enumerate(lines) if l.strip() == "### 31.")
for i in range(start, end):
    l = lines[i]
    vis = l.replace(" ", "␣").replace("　", "□").replace("\t", "⇥")
    print(f"{i+1:4d}: {vis}⏎")

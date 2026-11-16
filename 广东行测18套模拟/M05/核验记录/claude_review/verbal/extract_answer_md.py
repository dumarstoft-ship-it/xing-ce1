# 只读：摘出 答案与解析_待审.md 中第16—30题的解析段
P = "/home/user/xing-ce1/广东行测18套模拟/M05/答案与解析_待审.md"
lines = open(P, encoding="utf-8").read().split("\n")
s = next(i for i, l in enumerate(lines) if l.startswith("### 第16题"))
e = next(i for i, l in enumerate(lines) if l.startswith("### 第31题"))
print("\n".join(lines[s:e]))

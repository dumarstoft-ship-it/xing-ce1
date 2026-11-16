"""第42题：5种兴趣班，每位老人参加1～3种（被调查者均参加了兴趣班）。
求至少调查多少人才能保证有3人参加的兴趣班完全相同。
枚举所有组合作为“抽屉”，最不利情形每个抽屉2人，再加1人。
"""
from itertools import combinations

classes = ["书法", "绘画", "摄影", "合唱", "古典乐器"]
drawers = [c for r in (1, 2, 3) for c in combinations(classes, r)]
print("可能的参加组合数:", len(drawers), "（C(5,1)+C(5,2)+C(5,3) = 5+10+10）")
need = 2 * len(drawers) + 1
print("至少需要调查:", need)
# 对照：若把“不参加”也算一类或允许4、5种
print("若含4、5种:", 2 * (2 ** 5 - 1) + 1, "；若再含不参加:", 2 * 2 ** 5 + 1)
options = {"A": 36, "B": 41, "C": 48, "D": 51}
hits = [k for k, v in options.items() if v == need]
assert hits == ["D"]
print("答案:", hits)

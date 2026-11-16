"""M05 第69题：验证 Fe、Cu、Ag 活动性强弱，选出"不能达到目的"的实验组合。
按真实活动性顺序 Fe > H > Cu > Ag 推出每个实验的现象，再从现象反推能得到的大小关系，
求传递闭包，看三种金属的顺序是否被完全确定。
"""
from itertools import combinations

true_rank = {"Fe": 3, "H": 2, "Cu": 1, "Ag": 0}   # 数值越大越活泼


def react(metal, ion):
    """金属单质能否置换出溶液中的ion（H代表酸中的氢）"""
    return true_rank[metal] > true_rank[ion]


experiments = {
    "①": [("Fe", "Cu")],             # Fe 放入 CuSO4
    "②": [("Cu", "Ag")],             # Cu 放入 AgNO3
    "③": [("Ag", "Cu")],             # Ag 放入 CuSO4
    "④": [("Fe", "H"), ("Cu", "H")],  # Fe、Cu 分别放入稀盐酸
}


def relations(exp_keys):
    rel = set()
    for k in exp_keys:
        for metal, ion in experiments[k]:
            if react(metal, ion):
                rel.add((metal, ion))       # 有反应：metal 比 ion 活泼
            else:
                rel.add((ion, metal))       # 无反应：ion 比 metal 活泼（或同为不反应的判定）
    # 传递闭包
    changed = True
    while changed:
        changed = False
        for a, b in list(rel):
            for c, d in list(rel):
                if b == c and (a, d) not in rel:
                    rel.add((a, d))
                    changed = True
    return rel


def determined(rel):
    metals = ["Fe", "Cu", "Ag"]
    return all((a, b) in rel or (b, a) in rel for a, b in combinations(metals, 2))


options = {"A": "①③", "B": "①④", "C": "②④", "D": "③④"}
bad = []
for k, combo in options.items():
    rel = relations(list(combo))
    ok = determined(rel)
    shown = sorted((a, b) for a, b in rel if a != "H" and b != "H")
    print(f"{k} {combo}: 得到的关系 {shown} -> {'能确定 Fe>Cu>Ag' if ok else '不能确定'}")
    if not ok:
        bad.append(k)
assert bad == ["B"], bad
print("答案: B（①④都只说明Fe比Cu活泼，无法比较Ag）")

"""M06改写的两道资料题复算（编排.json rewrite）：第82题（比重上升最多）、第89题（原第87题，三类纸浆增量排序）。"""
# 第82题：2024年4月监管运输工具
tot, rt = 3309354, 30.1
items = {"A 汽车": (2828439, 32.8), "B 火车": (376851, 9.8), "C 船舶": (34604, 10.9), "D 飞机": (69460, 79.3)}
base = tot / (1 + rt / 100)
diff = {k: a / tot * 100 - a / (1 + r / 100) / base * 100 for k, (a, r) in items.items()}
for k, v in diff.items():
    print("第82题", k, f"比重变化 {v:+.3f} 个百分点")
best = max(diff, key=diff.get)
assert best.startswith("A")
# 只看增速差会选飞机
assert max(items, key=lambda k: items[k][1] - rt).startswith("D")

# 第89题：2023年三类纸浆同比增量
total, wood, recy = 8823, 2312, 5936
nonwood = total - wood - recy
inc = {"木浆": wood * 9.31 / 109.31, "非木浆": nonwood * 3.05 / 103.05, "再生纸浆": recy * 0.37 / 100.37}
order = sorted(inc, key=inc.get, reverse=True)
print("第89题 非木浆产量", nonwood, {k: round(v, 2) for k, v in inc.items()}, "→", "、".join(order))
assert order == ["木浆", "再生纸浆", "非木浆"]                       # C
assert sorted(inc, key={"木浆": 9.31, "非木浆": 3.05, "再生纸浆": 0.37}.get, reverse=True) == ["木浆", "非木浆", "再生纸浆"]   # 按增速：B
assert sorted(inc, key={"木浆": wood, "非木浆": nonwood, "再生纸浆": recy}.get, reverse=True) == ["再生纸浆", "木浆", "非木浆"]  # 按产量：A
assert abs((wood - 2115) - inc["木浆"]) < 0.2                          # 与图中2022年产量一致
print("两题复算一致")

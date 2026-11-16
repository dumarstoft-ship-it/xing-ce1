"""第40题：Pro版补贴售价15%，标准版补贴售价12%，售价=定价×折扣。哪款补贴最多？
选项 A平板 B耳机 C笔记本 D智能手表
"""
from fractions import Fraction as F

rows = [
    ("A", "平板", "标准版", 3500, F(80, 100)),
    ("B", "耳机", "Pro版", 1200, F(90, 100)),
    ("C", "笔记本", "标准版", 4000, F(75, 100)),
    ("D", "智能手表", "Pro版", 1800, F(88, 100)),
]
res = []
for opt, name, cfg, price, disc in rows:
    sale = price * disc
    rate = F(15, 100) if cfg == "Pro版" else F(12, 100)
    sub = sale * rate
    res.append((sub, opt, name))
    print(opt, name, cfg, "售价", float(sale), "补贴", float(sub))
best = max(res)
print("补贴最多:", best[1], best[2], float(best[0]))

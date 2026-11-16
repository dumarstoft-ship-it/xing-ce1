"""第44题：长200米、宽128米的长方形四周等距种松树，四个顶点都种，间距为整数米；
再在每两棵相邻松树之间补种1棵侧柏。求侧柏最少棵数。
枚举所有可行间距（须同时整除200和128），闭合环形：侧柏数 = 间隔数 = 周长/间距。
"""
from math import gcd

L, W = 200, 128
perim = 2 * (L + W)
feasible = [d for d in range(1, W + 1) if L % d == 0 and W % d == 0]
print("可行间距:", feasible, "，gcd =", gcd(L, W))
counts = {d: perim // d for d in feasible}
print("各间距对应松树数/侧柏数:", counts)
least = min(counts.values())
print("侧柏最少:", least)
options = {"A": 66, "B": 74, "C": 82, "D": 90}
hits = [k for k, v in options.items() if v == least]
assert hits == ["C"]
print("答案:", hits)

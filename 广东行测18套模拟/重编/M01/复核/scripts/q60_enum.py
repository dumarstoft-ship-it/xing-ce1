"""第60题枚举：选5个球（大3/中2/小1），任意投篮顺序；投中得球分，第一次不中得0，其余不中得1。
问各选项的选球方式能否得到 9 分。
"""
import itertools

val = {"大": 3, "中": 2, "小": 1}
options = {
    "A 三大两中": ["大"] * 3 + ["中"] * 2,
    "B 两大三小": ["大"] * 2 + ["小"] * 3,
    "C 一大四中": ["大"] + ["中"] * 4,
    "D 一大四小": ["大"] + ["小"] * 4,
}
for name, balls in options.items():
    scores = set()
    ways = []
    for order in set(itertools.permutations(balls)):
        for hits in itertools.product((True, False), repeat=5):
            s = sum(val[b] if h else (0 if i == 0 else 1) for i, (b, h) in enumerate(zip(order, hits)))
            scores.add(s)
            if s == 9 and len(ways) < 1:
                ways.append((order, hits))
    print(name, "可得分数:", sorted(scores), "| 能得9分" if 9 in scores else "| 不能得9分", ways[:1])

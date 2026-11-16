"""Enumeration checks for the analytical-reasoning items Q52, Q54, Q60."""
import itertools

# ---------------- Q52 ----------------
print("Q52: winners (甲,乙,丙) consistent with exactly one true prediction")
sols = []
for j, y, b in itertools.product([0, 1], repeat=3):
    li = j and y                       # 小李: 甲乙均中标
    zhang = (not b) or j               # 小张: 若丙中标则甲中标
    wang = not (j and y)               # 小王: 甲乙至多一个中标
    if li + zhang + wang == 1:
        sols.append((j, y, b))
print("   ", sols)
print("    A 甲乙均中标:", all(j and y for j, y, b in sols),
      "| B 乙丙均中标:", all(y and b for j, y, b in sols),
      "| C 乙可能中标:", any(y for j, y, b in sols),
      "| D 只有丙:", all((not j) and (not y) and b for j, y, b in sols))

# ---------------- Q54 ----------------
grid = ["1112", "4552", "4662", "4333"]
cells = {}
for r, row in enumerate(grid):
    for c, ch in enumerate(row):
        cells.setdefault(int(ch), []).append((r, c))
area = {k: len(v) for k, v in cells.items()}
adj = {k: set() for k in cells}
for r in range(4):
    for c in range(4):
        for dr, dc in ((0, 1), (1, 0)):
            rr, cc = r + dr, c + dc
            if rr < 4 and cc < 4 and grid[r][c] != grid[rr][cc]:
                a, b = int(grid[r][c]), int(grid[rr][cc])
                adj[a].add(b)
                adj[b].add(a)
print("\nQ54 areas", area, "adjacency", {k: sorted(v) for k, v in adj.items()})
plants = ["甲", "乙", "丙", "丁", "戊", "己"]
res = []
for perm in itertools.permutations(range(1, 7)):
    pos = dict(zip(plants, perm))
    if not (area[pos["甲"]] == area[pos["丙"]] and pos["丙"] not in adj[pos["甲"]]):
        continue
    if not (area[pos["乙"]] != area[pos["己"]] and pos["己"] not in adj[pos["乙"]]):
        continue
    if len(adj[pos["戊"]]) != 3:
        continue
    if pos["乙"] != 5:
        continue
    res.append(pos)
for p in res:
    print("   ", p)
print("    A 甲在2:", all(p["甲"] == 2 for p in res), "| B 丁在6:", all(p["丁"] == 6 for p in res),
      "| C 戊在1:", all(p["戊"] == 1 for p in res), "| D 己在3:", all(p["己"] == 3 for p in res))

# ---------------- Q60 ----------------
people = ["甲", "乙", "丙", "丁", "戊", "己", "庚"]


def count(gap_ok):
    n = 0
    out = []
    for perm in itertools.permutations(range(1, 8)):
        d = dict(zip(people, perm))
        if not gap_ok(abs(d["乙"] - d["丙"])):
            continue
        if not (d["丙"] < d["甲"] and gap_ok(d["甲"] - d["丙"])):
            continue
        if abs(d["丁"] - d["戊"]) == 1:
            continue
        if d["庚"] - d["甲"] != 1:
            continue
        n += 1
        out.append("".join(p for p, _ in sorted(d.items(), key=lambda kv: kv[1])))
    return n, out


n1, o1 = count(lambda diff: diff - 1 > 2)   # 间隔 = 中间相隔的天数
n2, o2 = count(lambda diff: diff > 2)       # 间隔 = 日期之差
print("\nQ60 interval = days strictly between (diff-1>2):", n1, o1)
print("Q60 interval = date difference (diff>2):", n2)

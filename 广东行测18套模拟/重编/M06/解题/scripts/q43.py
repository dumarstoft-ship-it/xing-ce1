# 第43题：四部门共78人，最少12人，人数成等差；最多部门分三组成等差，第二多小组几人？
sols = []
for d in range(0, 40):
    depts = [12 + i * d for i in range(4)]
    if sum(depts) == 78:
        sols.append(depts)
print("部门人数:", sols)
assert sols == [[12, 17, 22, 27]]
big = sols[0][-1]
groups = [(a, b, c) for a in range(1, big) for b in range(a, big) for c in range(b, big)
          if a + b + c == big and b - a == c - b]
print("三组等差的分法:", groups)
mids = set(g[1] for g in groups)
print("第二多（中间）小组人数:", mids)
assert mids == {9}
print("答案: B")

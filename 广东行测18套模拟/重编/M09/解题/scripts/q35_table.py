"""M09 第35题：表格数阵
    2  3  4  5
    5  6 11 13
    8  9 18  ?     选项 A14 B17 C19 D21
核验思路：
1. 按列看：每列都是等差数列（公差3、3、7、8），第4列 5,13,? → 21；
2. 按行看：第4个数比第3个数依次多1、2、3（行号），18+3=21；
3. 穷举“第4个数 = p·a + q·b + r·c + s（系数取−3…3的整数，常数−5…5）”这类行内线性规律，
   凡能同时拟合前两行的，看它给第三行哪些值，统计落在各选项上的情况，确认没有同样简单的规律指向别的选项。"""
from itertools import product
from collections import Counter
rows = [(2, 3, 4, 5), (5, 6, 11, 13), (8, 9, 18)]
opts = {'A': 14, 'B': 17, 'C': 19, 'D': 21}
# 1. 列等差
cols = list(zip(*[r[:3] for r in rows]))
for j, c in enumerate(cols):
    print(f'第{j+1}列', c, '差', [c[1]-c[0], c[2]-c[1]])
    assert c[1] - c[0] == c[2] - c[1]
col4 = rows[1][3] + (rows[1][3] - rows[0][3])
print('第4列按等差得', col4)
# 2. 行内 d-c = 行号
print('各行第4数−第3数:', [r[3]-r[2] for r in rows[:2]], '→ 第三行应为3，得', rows[2][2]+3)
assert rows[2][2] + 3 == col4 == 21
# 3. 行内线性规律穷举（不含常数随行号变化的情形）
hits = Counter()
examples = {}
for p, q, r, s in product(range(-3, 4), range(-3, 4), range(-3, 4), range(-5, 6)):
    if (p, q, r) == (0, 0, 0):
        continue
    f = lambda a, b, c: p*a + q*b + r*c + s
    if all(f(*row[:3]) == row[3] for row in rows[:2]):
        v = f(*rows[2])
        hits[v] += 1
        examples.setdefault(v, (p, q, r, s))
print('能拟合前两行的行内线性规律给出的第三行取值（取值:规律个数）:')
for v, n in sorted(hits.items(), key=lambda t: -t[1])[:12]:
    tag = [k for k, o in opts.items() if o == v]
    print(f'  {v:>4}: {n:>3} 条 例 p,q,r,s={examples[v]} {"←选项"+tag[0] if tag else ""}')
simple = {k: hits.get(o, 0) for k, o in opts.items()}
print('落在各选项上的规律条数:', simple)

"""M10 第31题：2，12，30，56，90，（ ）  选项 A132 B138 C144 D150"""
seq = [2, 12, 30, 56, 90]
opts = {'A': 132, 'B': 138, 'C': 144, 'D': 150}
# 写法一：相邻两数之积 1×2、3×4、5×6、7×8、9×10
assert all(a == (2 * k - 1) * (2 * k) for k, a in enumerate(seq, 1))
v1 = 11 * 12
# 写法二：一级差 10、18、26、34 公差为8
d = [b - a for a, b in zip(seq, seq[1:])]
assert len({y - x for x, y in zip(d, d[1:])}) == 1, d
v2 = seq[-1] + d[-1] + 8
print('一级差', d, '→ 下一差', d[-1] + 8, '；两种写法', v1, v2)
assert v1 == v2 == 132
print('答案：', [k for k, v in opts.items() if v == v1])

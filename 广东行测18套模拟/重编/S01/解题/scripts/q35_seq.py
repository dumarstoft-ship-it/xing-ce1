"""S01 第35题：30，32，42，60，86，（ ）  选项 A112 B120 C132 D144
一级差 2、10、18、26 公差8 → 下一差34 → 120。"""
seq = [30, 32, 42, 60, 86]
d = [b - a for a, b in zip(seq, seq[1:])]
assert len({y - x for x, y in zip(d, d[1:])}) == 1
nxt = seq[-1] + d[-1] + 8
opts = {'A': 112, 'B': 120, 'C': 132, 'D': 144}
print('一级差', d, '下一项', nxt, '答案：', [k for k, v in opts.items() if v == nxt])
assert nxt == 120

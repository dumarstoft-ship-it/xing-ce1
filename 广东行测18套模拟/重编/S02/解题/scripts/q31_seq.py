"""S02 第31题：98，86，74，62，（ ）  选项 A49 B50 C51 D52 —— 公差−12的等差数列。"""
seq = [98, 86, 74, 62]
d = {b - a for a, b in zip(seq, seq[1:])}
assert d == {-12}
nxt = seq[-1] - 12
opts = {'A': 49, 'B': 50, 'C': 51, 'D': 52}
print('下一项', nxt, '答案：', [k for k, v in opts.items() if v == nxt])

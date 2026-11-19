"""M09 第33题：6，12，19，32，52，（ ）  选项 A84 B85 C86 D87
核验：一级差 6,7,13,20，前两个差之和等于后一个差（和数列），下一个差13+20=33；
等价写法：a(n)=a(n-1)+a(n-2)+1。"""
seq = [6, 12, 19, 32, 52]
opts = {'A': 84, 'B': 85, 'C': 86, 'D': 87}
d = [b - a for a, b in zip(seq, seq[1:])]
print('一级差:', d)
assert all(d[i] + d[i + 1] == d[i + 2] for i in range(len(d) - 2))
nxt = seq[-1] + d[-2] + d[-1]
rec = [seq[i - 1] + seq[i - 2] + 1 for i in range(2, len(seq))]
print('a(n-1)+a(n-2)+1:', rec)
assert rec == seq[2:] and seq[-1] + seq[-2] + 1 == nxt
ok = [k for k, v in opts.items() if v == nxt]
print('下一项', nxt, '对应选项', ok)
assert ok == ['B']
# 易错：只做“前两项相加”不加1 → 32+52=84（A）
print('漏掉“+1”：', seq[-1] + seq[-2], '→A')

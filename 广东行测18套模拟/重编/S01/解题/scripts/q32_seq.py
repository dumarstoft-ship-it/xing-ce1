"""S01 第32题：3.14，9.20，12.23，21.32，33.44，（ ）  选项 A44.55 B49.61 C54.65 D60.66
整数部分 3、9、12、21、33：从第三项起每项等于前两项之和 → 21+33=54；
项内关系：小数部分 = 整数部分 + 11 → 65。"""
seq = ['3.14', '9.20', '12.23', '21.32', '33.44']
ip = [int(s.split('.')[0]) for s in seq]
fp = [int(s.split('.')[1]) for s in seq]
assert all(ip[i] == ip[i - 1] + ip[i - 2] for i in range(2, 5))
assert all(f == i + 11 for i, f in zip(ip, fp))
nxt_i = ip[-1] + ip[-2]
nxt = f'{nxt_i}.{nxt_i + 11}'
opts = {'A': '44.55', 'B': '49.61', 'C': '54.65', 'D': '60.66'}
print('整数部分', ip, '小数部分', fp, '→', nxt)
print('满足“小数=整数+11”的选项：', [k for k, v in opts.items() if int(v.split('.')[1]) == int(v.split('.')[0]) + 11])
print('答案：', [k for k, v in opts.items() if v == nxt])
assert nxt == '54.65'

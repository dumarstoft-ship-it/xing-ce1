"""M11 第32题：8，3，17，5，24，9，26，18，30，（ ）  选项 A22 B25 C33 D36
十项两两分组：(8,3)(17,5)(24,9)(26,18)(30,?)，组内和为11、22、33、44 → 55。"""
seq = [8, 3, 17, 5, 24, 9, 26, 18, 30]
opts = {'A': 22, 'B': 25, 'C': 33, 'D': 36}
pairs = [(seq[i], seq[i + 1]) for i in range(0, 8, 2)]
sums = [a + b for a, b in pairs]
assert sums == [11, 22, 33, 44]
ans = 55 - 30
print('组内和', sums, '→ 第5组和55，所求项', ans, '答案：', [k for k, v in opts.items() if v == ans])
# 其他分法检验：奇数项8、17、24、26、30与偶数项3、5、9、18作差均无规律
odd, even = seq[0::2], seq[1::2]
print('奇数项差', [b - a for a, b in zip(odd, odd[1:])], '偶数项差', [b - a for a, b in zip(even, even[1:])])
print('组内差', [a - b for a, b in pairs])

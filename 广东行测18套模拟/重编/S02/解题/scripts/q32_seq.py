"""S02 第32题：1.3，4.1，2.4，5.2，3.5，（ ）  选项 A6.3 B6.4 C6.5 D6.6
每项整数部分与小数部分之和为4、5、6、7、8 → 9；也可分奇偶项：整数部分1、2、3与4、5、6，小数部分3、4、5与1、2、3。"""
seq = ['1.3', '4.1', '2.4', '5.2', '3.5']
sp = [tuple(int(t) for t in s.split('.')) for s in seq]
assert [a + b for a, b in sp] == [4, 5, 6, 7, 8]
opts = {'A': '6.3', 'B': '6.4', 'C': '6.5', 'D': '6.6'}
ok = [k for k, s in opts.items() if sum(int(t) for t in s.split('.')) == 9]
ip, fp = [a for a, _ in sp], [b for _, b in sp]
print('整数部分', ip, '小数部分', fp, '；数字和为9的选项', ok)
assert ok == ['A'] and ip[1::2] == [4, 5] and fp[1::2] == [1, 2]      # 偶数项续写为6.3

"""M08 第32题：2.04，5.12，11.36，20.108，（ ）  机械拆分：整数部分、小数部分分开看"""
from decimal import Decimal as D
seq = ['2.04', '5.12', '11.36', '20.108']
opts = {'A': '32.324', 'B': '32.216', 'C': '47.324', 'D': '47.216'}
ints = [int(s.split('.')[0]) for s in seq]
decs = [int(s.split('.')[1]) for s in seq]
print('整数部分', ints, '差', [ints[i+1]-ints[i] for i in range(3)])
print('小数部分', decs, '比', [decs[i+1]/decs[i] for i in range(3)])
d = [ints[i+1]-ints[i] for i in range(3)]
assert d == [3, 6, 9]
nxt_int = ints[-1] + 12
assert decs == [4, 12, 36, 108]
nxt_dec = decs[-1] * 3
pred = f'{nxt_int}.{nxt_dec}'
print('预测:', pred)
ans = [k for k, v in opts.items() if v == pred]
assert ans == ['A']
print('答案', ans)

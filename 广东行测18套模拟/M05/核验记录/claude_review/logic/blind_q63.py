# Q63 bid winners (any subset may win; also check the 'at least one wins' variant).
from itertools import product
def imp(a,b): return (not a) or b
sols_any, sols_nonempty = [], []
for a,b,c in product([False,True],repeat=3):
    s1 = a and b                 # 小李
    s2 = imp(c, a)               # 小张
    s3 = not (a and b)           # 小王
    if [s1,s2,s3].count(True)==1:
        sols_any.append((a,b,c))
        if a or b or c: sols_nonempty.append((a,b,c))
def fmt(t): return '中标: ' + ('、'.join(n for n,v in zip('甲乙丙',t) if v) or '无')
print("恰一人预测正确的中标情形 (允许任意子集):")
for t in sols_any: print('  ', fmt(t))
print("若至少一个品牌中标:", [fmt(t) for t in sols_nonempty])
opts = {
 'A 甲、乙均能中标': lambda a,b,c: a and b,
 'B 乙、丙均能中标': lambda a,b,c: b and c,
 'C 乙可能中标(存在乙中标的情形)': None,
 'D 只有丙能中标': lambda a,b,c: c and not a and not b,
}
for k,f in opts.items():
    if f is None:
        print(k, '成立' if any(t[1] for t in sols_any) else '不成立'); continue
    vals=[f(*t) for t in sols_any]
    print(k, '一定为真' if all(vals) else ('可能为真' if any(vals) else '一定为假'))

# Q60 ranking prediction puzzle.
from itertools import permutations
P = ['甲','乙','丙','丁']
pred = {
 '张': {'甲':4,'乙':3,'丙':2,'丁':1},
 '王': {'甲':3,'乙':2,'丙':4,'丁':1},
 '李': {'甲':4,'乙':2,'丙':1,'丁':3},
 '赵': {'甲':2,'乙':3,'丙':1,'丁':4},
}
def hits(r, who): return sum(r[x]==pred[who][x] for x in P)
sols = []
for perm in permutations([1,2,3,4]):
    r = dict(zip(P, perm))
    if hits(r,'张')==0 and hits(r,'王')==1 and hits(r,'李')==1 and hits(r,'赵')==1:
        sols.append(r)
print("满足总条件(张全错, 王李赵各对1个)的名次方案:", len(sols))
for r in sols: print('  ', r, ' 王猜对的选手:', [x for x in P if r[x]==pred['王'][x]])
cond = [r for r in sols if r['甲']==pred['王']['甲']]
print("附加'王猜对了甲的名次'后的方案:", len(cond))
for r in cond: print('  ', r)
opts = {'A 丁第四': lambda r: r['丁']==4, 'B 丙第一': lambda r: r['丙']==1,
        'C 乙第二': lambda r: r['乙']==2, 'D 乙第一': lambda r: r['乙']==1}
for k,f in opts.items():
    vals=[f(r) for r in cond]
    print(k, '一定为真' if vals and all(vals) else ('可能为真' if any(vals) else '一定为假'))

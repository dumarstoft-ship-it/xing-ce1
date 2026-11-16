"""第54题 真假推理：四个项目 养老Y 少儿S 健身J 图书T，开设与否全枚举。
甲: S→T；乙: J→Y；丙: Y、S、T至多开一个；丁: S且非T。只有一人说对。"""
from itertools import product
sols = []
for Y, S, J, T in product([0, 1], repeat=4):
    jia = (not S) or T
    yi = (not J) or Y
    bing = (Y + S + T) <= 1
    ding = S and not T
    if sum(map(bool, [jia, yi, bing, ding])) == 1:
        sols.append(dict(Y=Y, S=S, J=J, T=T, true=[n for n, v in zip('甲乙丙丁', [jia, yi, bing, ding]) if v]))
print('满足“只有一人说对”的方案：')
for s in sols:
    print(s)
opts = {
 'A 开T不开S': lambda s: s['T'] and not s['S'],
 'B 开Y不开J': lambda s: s['Y'] and not s['J'],
 'C S和J都开': lambda s: s['S'] and s['J'],
 'D Y和T都不开': lambda s: (not s['Y']) and (not s['T']),
}
for k, f in opts.items():
    vals = [bool(f(s)) for s in sols]
    print(k, '在所有解中均成立' if all(vals) else ('均不成立' if not any(vals) else '不确定'))

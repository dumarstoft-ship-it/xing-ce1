# Q56 tunnel arrangement. Positions 1..6 numbered from NORTH to SOUTH (1 = northernmost).
from itertools import permutations
names = ['长川','大美','青山','绿水','彩石','白玉']
def base_ok(p):
    # (1) 白玉在彩石北边且相邻: 彩石 = 白玉+1 ; 白玉在大美南边且不相邻: 大美 <= 白玉-2
    if p['彩石'] != p['白玉'] + 1: return False
    if not (p['大美'] < p['白玉'] and p['白玉'] - p['大美'] >= 2): return False
    # (2) 长川与青山之间隔一条隧道
    if abs(p['长川'] - p['青山']) != 2: return False
    return True
all_sol, cond_sol = [], []
for perm in permutations(range(1,7)):
    p = dict(zip(names, perm))
    if not base_ok(p): continue
    all_sol.append(p)
    if abs(p['绿水'] - p['白玉']) == 1:
        cond_sol.append(p)
def show(p):
    order = sorted(p, key=lambda n: p[n])
    return '北→南: ' + ' '.join(order)
print("满足(1)(2)的排列数:", len(all_sol))
for p in all_sol: print('  ', show(p))
print("附加'绿水与白玉相邻'后的排列数:", len(cond_sol))
for p in cond_sol: print('  ', show(p))
opts = {
 'A 彩石由南向北第二位': lambda p: 7 - p['彩石'] == 2,
 'B 大美由北向南第二位': lambda p: p['大美'] == 2,
 'C 长川由北向南第三位': lambda p: p['长川'] == 3,
 'D 青山由南向北第三位': lambda p: 7 - p['青山'] == 3,
}
for k,f in opts.items():
    vals = [f(p) for p in cond_sol]
    print(k, '一定为真' if all(vals) else ('可能为真' if any(vals) else '一定为假'))

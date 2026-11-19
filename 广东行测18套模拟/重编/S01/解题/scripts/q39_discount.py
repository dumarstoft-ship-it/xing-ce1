"""S01 第39题：满100元减30元，买4件与买3件花费相同，求单价。 选项 A30 B40 C50 D60
两种读法都检验：每满100减30（可叠加）；满100减30（只减一次）。"""
def cost_each100(total):
    return total - 30 * (total // 100)
def cost_once(total):
    return total - 30 if total >= 100 else total
opts = {'A': 30, 'B': 40, 'C': 50, 'D': 60}
for name, f in (('每满100减30', cost_each100), ('满100减30', cost_once)):
    ok = [k for k, p in opts.items() if f(4 * p) == f(3 * p)]
    allp = [p for p in range(1, 301) if f(4 * p) == f(3 * p)]
    print(name, '：选项中成立', ok, '；1—300元整数单价中成立的', allp)
    assert ok == ['A']
print('单价30：3件90元不减，4件120元减30得90元')

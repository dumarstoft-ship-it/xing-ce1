"""换入题 第60题（夏令营）：枚举4人的(类别, 数量)，检验各选项是否必然成立。
条件(2)按"恰有1人选1个、恰有2人选2个"理解，另检验"至少"的理解。"""
import itertools

PEOPLE = ['贾', '易', '白', '单']
CATS = ['雏鹰', '精英', '综合']


def ok(s, exact=True):
    cnt1 = sum(1 for p in PEOPLE if s[p][1] == 1)
    cnt2 = sum(1 for p in PEOPLE if s[p][1] == 2)
    c1 = s['贾'][0] != s['单'][0] and s['贾'][1] != s['单'][1]
    c2 = (cnt1 == 1 and cnt2 == 2) if exact else (cnt1 >= 1 and cnt2 >= 2)
    c3 = s['白'] == ('综合', 3)
    c4 = set(s[p][0] for p in PEOPLE) == set(CATS) and s['易'][0] == '雏鹰' and s['单'][0] == '雏鹰'
    return c1 and c2 and c3 and c4


OPTS = {
    'A': lambda s: s['易'][1] == 2,
    'B': lambda s: s['贾'][0] == s['白'][0],
    'C': lambda s: any(s[p][0] == s['白'][0] or s[p][1] == s['白'][1] for p in PEOPLE if p != '白'),
    'D': lambda s: s['单'] == ('雏鹰', 2),
}

for exact in (True, False):
    sols = []
    for combo in itertools.product(itertools.product(CATS, [1, 2, 3]), repeat=4):
        s = dict(zip(PEOPLE, combo))
        if ok(s, exact):
            sols.append(s)
    print(f'条件(2)按{"恰有" if exact else "至少"}理解：满足条件的情形 {len(sols)} 种')
    for s in sols:
        print('   ', s)
    for k, f in OPTS.items():
        vals = {f(s) for s in sols}
        print(f'   选项{k}：', '必然成立' if vals == {True} else ('必然不成立' if vals == {False} else '可能成立但不必然'))

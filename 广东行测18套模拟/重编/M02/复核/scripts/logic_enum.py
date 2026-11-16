"""Enumeration checks for the logic questions of M02 (s17 q51, q54, q56, q60, q63)."""
import itertools

def entails(premises, concl, vars_):
    for vals in itertools.product([False, True], repeat=len(vars_)):
        e = dict(zip(vars_, vals))
        if all(p(e) for p in premises) and not concl(e):
            return False
    return True

def possible(premises, stmt, vars_):
    for vals in itertools.product([False, True], repeat=len(vars_)):
        e = dict(zip(vars_, vals))
        if all(p(e) for p in premises) and stmt(e):
            return True
    return False

imp = lambda a, b: (not a) or b

# ---- Q51: sci=科学饮食结构, bal=均衡营养, reg=规律喂食, dec=免疫衰退
V = ['sci', 'bal', 'reg', 'dec']
P51 = [lambda e: imp(not e['sci'], e['dec']),                      # 缺乏科学结构 -> 衰退
       lambda e: imp(not (e['bal'] and e['reg']), not e['sci'])]   # 除非 均衡且规律，否则 不科学
opts51 = {'A': lambda e: imp(e['bal'] and e['reg'], not e['dec']),
          'B': lambda e: imp(e['bal'] and e['reg'], e['sci']),
          'C': lambda e: imp(e['dec'], not e['sci']),
          'D': lambda e: imp(not e['reg'], e['dec'])}
print('Q51 entailed:', [k for k, f in opts51.items() if entails(P51, f, V)])

# ---- Q54: who is surely notified
people = ['冯', '陈', '楚', '魏', '周', '吴', '郑']
sols = []
for vals in itertools.product([False, True], repeat=7):
    e = dict(zip(people, vals))
    c1 = (e['周'] and e['吴']) != (e['吴'] and e['郑'])        # 要么…要么… (exactly one)
    c2 = imp(e['郑'] or not e['吴'], e['冯'] and e['楚'])
    c3 = imp(e['陈'] or e['吴'], e['魏'] and not e['楚'])
    if c1 and c2 and c3:
        sols.append(e)
print('Q54 #models', len(sols), '; always notified:', [p for p in people if all(s[p] for s in sols)],
      '; never:', [p for p in people if not any(s[p] for s in sols)])
# also with inclusive reading of (1)
sols_inc = []
for vals in itertools.product([False, True], repeat=7):
    e = dict(zip(people, vals))
    c1 = (e['周'] and e['吴']) or (e['吴'] and e['郑'])
    c2 = imp(e['郑'] or not e['吴'], e['冯'] and e['楚'])
    c3 = imp(e['陈'] or e['吴'], e['魏'] and not e['楚'])
    if c1 and c2 and c3:
        sols_inc.append(e)
print('Q54 (inclusive-or reading) always notified:', [p for p in people if all(s[p] for s in sols_inc)])

# ---- Q56
courses = ['地理', '鉴赏', '急救', '历史']
names = ['甲', '乙', '丙', '丁', '戊']
ok = []
for asg in itertools.product(courses, repeat=5):
    a = dict(zip(names, asg))
    g = [a['甲'] == '地理',
         a['乙'] == a['丁'],
         not (a['丙'] == '鉴赏' and a['丁'] == '鉴赏'),
         a['甲'] != '急救' or a['丙'] != '历史',
         a['乙'] != '鉴赏']
    if sum(g) == 1:
        ok.append(a)
print('Q56 #assignments', len(ok))
chk = {'A 有人选地理': all('地理' in a.values() for a in ok),
       'B 没人选地理': all('地理' not in a.values() for a in ok),
       'C 乙丙都不选急救': all(a['乙'] != '急救' and a['丙'] != '急救' for a in ok),
       'D 乙丁都不选鉴赏': all(a['乙'] != '鉴赏' and a['丁'] != '鉴赏' for a in ok)}
print('Q56 necessarily true:', [k for k, v in chk.items() if v])
print('   fixed:', {n: sorted({a[n] for a in ok}) for n in names})

# ---- Q60
grades = ['大一', '大二', '大三']; majors = ['文学', '数学', '计算机']
res = []
for g in itertools.permutations(grades):
    for m in itertools.permutations(majors):
        G = dict(zip(['李', '赵', '钱'], g)); M = dict(zip(['李', '赵', '钱'], m))
        # (1) 李与"大一数学"的成员是好友: such a member exists and is not 李
        one = [p for p in G if G[p] == '大一' and M[p] == '数学']
        c1 = len(one) == 1 and one[0] != '李'
        # (2) 钱年级最高(大三)，曾和计算机专业成员共同演出 -> 钱 不是计算机
        c2 = G['钱'] == '大三' and M['钱'] != '计算机'
        if c1 and c2:
            res.append({p: G[p] + M[p] for p in G})
print('Q60 solutions:', res)

# ---- Q63: plan=周密预案, succ=成功举办, cap=承载能力足够, exp=经验丰富, safe=安全有序
V = ['plan', 'succ', 'cap', 'exp', 'safe']
P63 = [lambda e: imp(e['plan'], e['succ']), lambda e: imp(e['succ'], e['cap']),
       lambda e: imp(e['safe'], e['exp'] and e['cap'])]
st63 = {'A': lambda e: (not e['plan']) and e['cap'],
        'B': lambda e: e['exp'] and e['cap'] and not e['safe'],
        'C': lambda e: e['cap'] and (not e['exp']) and e['safe'],
        'D': lambda e: e['succ']}
print('Q63 impossible under premises:', [k for k, f in st63.items() if not possible(P63, f, V)])

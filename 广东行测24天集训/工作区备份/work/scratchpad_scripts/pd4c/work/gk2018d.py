from itertools import product, combinations, permutations
C = ['哲','逻','数','统','宗','史','艺']
def models(r4, r2):
    """r4: 'some' = 哲学至少有一次与数学或艺术同日; 'every' = 每一次哲学都与数学或艺术同日
       r2: 'some' = 数学(每次)安排在某次逻辑的次日; 'everylogic' = 另要求每次逻辑的次日都...(不合理,不用)"""
    M = []
    for dbl in C:
        # choose days for each course: single -> one day; doubled -> two different days
        others = [c for c in C if c != dbl]
        for d2 in combinations(range(1,5), 2):
            if 3 in d2 or 4 not in d2: continue
            for ds in product(range(1,5), repeat=6):
                days = {c: (d,) for c, d in zip(others, ds)}
                days[dbl] = d2
                # each day exactly 2 slots
                cnt = [0]*5
                for c in C:
                    for d in days[c]: cnt[d] += 1
                if cnt[1:] != [2,2,2,2]: continue
                if 3 not in days['艺']: continue
                # (2) 数学只能安排在逻辑的次日
                if not all(any(d == l+1 for l in days['逻']) for d in days['数']): continue
                if not (1 in days['统'] or 2 in days['统']): continue
                same = lambda d: (d in days['数']) or (d in days['艺'])
                if r4 == 'some':
                    if not any(same(d) for d in days['哲']): continue
                else:
                    if not all(same(d) for d in days['哲']): continue
                M.append((dbl, days))
    return M
for r4 in ('some','every'):
    M = models(r4, 'some')
    print('reading', r4, 'models', len(M))
    print(' doubled possible:', sorted({m[0] for m in M}))
    for c in C:
        print('  ', c, 'days possible', sorted({d for m in M for d in m[1][c]}))
    # Q106 cannot be on day 4
    print(' Q106 cannot day4:', [c for c in ['史','哲','艺','宗'] if not any(4 in m[1][c] for m in M)])
    print(' Q107 any day:', [c for c in ['数','宗','统'] if {d for m in M for d in m[1][c]} == {1,2,3,4}])
    print(' Q108 cannot double:', [c for c in ['哲','逻','统','史'] if not any(m[0]==c for m in M)])
    print(' Q109 逻 not on:', [d for d in (1,2,3,4) if not any(d in m[1]['逻'] for m in M)])
    S = [m for m in M if m[0]=='宗']
    print(' Q110 宗 doubled -> 史 days:', sorted({m[1]['史'] for m in S}), len(S))

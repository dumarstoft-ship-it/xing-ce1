from itertools import product
D = ['财','研','人','后','法','销']
def models(strict_after=True):
    M = []
    for s in product(D, repeat=6):
        if any(s.count(d) > 2 for d in D): continue
        if s[1] == '法' or s[3] == '法': continue
        ok = True
        for i, d in enumerate(s):
            if d == '后' and not (i + 1 < 6 and s[i + 1] == '法'): ok = False
            if d == '研' and not (i + 1 < 6 and s[i + 1] == '后'): ok = False
        if ok: M.append(s)
    return M
M = models(); print(len(M))
opts106 = {'A': '财人后法财人', 'B': '销财法人财销', 'C': '人财法研法后', 'D': '法销人后财销'}
print('106', [k for k, v in opts106.items() if tuple(v) in set(M)])
print('107 后勤 days', sorted({i + 1 for s in M for i, d in enumerate(s) if d == '后'}))
S = [s for s in M if s.count('后') == 2]
o108 = {'A': lambda s: s[0] == '研', 'B': lambda s: s[5] == '人', 'C': lambda s: s[2] == '财', 'D': lambda s: s[4] == '法'}
print('108 cannot', [k for k, f in o108.items() if not any(f(s) for s in S)], len(S), sorted({tuple(i+1 for i,d in enumerate(s) if d=='后') for s in S}))
S = [s for s in M if s[2] == '财' and s[4] == '财']
o109 = {'A': ('后', '法'), 'B': ('法', '销'), 'C': ('财', '销'), 'D': ('研', '人')}
print('109 can', [k for k, (a, b) in o109.items() if any(s[0] == a and s[5] == b for s in S)], len(S))
S = [s for s in M if '财' not in s and '后' not in s]
o110 = {'A': lambda s: s[3] == '销', 'B': lambda s: s[4] == '法', 'C': lambda s: s[1] in ('销', '人'), 'D': lambda s: s[2] in ('法', '人')}
print('110 must', [k for k, f in o110.items() if all(f(s) for s in S)], len(S), S[:10])

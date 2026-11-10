import json, re, itertools, collections, sys
def L(p): return [json.loads(l) for l in open(p) if l.strip()]
M = L('/home/user/work/out2/YY2B/questions.jsonl')
A = L('/home/user/work/out2/YY2A/questions.jsonl')
def nz(s): return re.sub(r'[^一-鿿0-9A-Za-z]', '', s or '')
def lcs(a, b):
    a, b = nz(a), nz(b)
    if not a or not b: return ''
    best = ''; prev = [0]*(len(b)+1)
    for i in range(1, len(a)+1):
        cur = [0]*(len(b)+1)
        for j in range(1, len(b)+1):
            if a[i-1] == b[j-1]:
                cur[j] = prev[j-1]+1
                if cur[j] > len(best): best = a[i-cur[j]:i]
        prev = cur
    return best
COMMON = {'这段文字意在说明','这段文字意在强调','最适合做这段文字标题的是','这段文字接下来最可能讲的是','这段文字主要讲了','这段文字主要介绍了','对这段文字理解准确的是','将以上6个句子重新排列语序正确的一项是','依次填入画横线部分最恰当的一项是','填入画横线部分最恰当的一项是'}
def body(q):  # stem without prompt line
    s = q['stem']; parts = s.split('\n')
    return '\n'.join(parts[:-1]) if len(parts) > 1 else s
issues = []
for day in ['D04', 'D05', 'D06']:
    items = [('M', q) for q in M if q['day'] == day] + [('A', q) for q in A if q['day'] == day]
    for (sx, x), (sy, y) in itertools.combinations(items, 2):
        if sx == 'A' and sy == 'A': continue
        c = lcs(body(x), body(y))
        if len(c) >= 9 and c not in COMMON: issues.append((day, 'shared-text', x['id'], y['id'], c))
    # answer leaks
    for sx, x in items:
        ans = x['checked_answer']; at = x['options'].get(ans, '')
        if re.fullmatch(r'[①-⑧]+', at): continue
        words = at.split() if (sx == 'A' and x.get('topic') == '选词填空') else [at]
        for sy, y in items:
            if y is x or (sx == 'A' and sy == 'A'): continue
            st = y['stem'] + ' ' + ' '.join(y['options'].values())
            for w in words:
                w2 = nz(w)
                if not w2: continue
                if len(words) > 1 or len(w2) <= 4:
                    if w2 in nz(st): issues.append((day, 'answer-word-in-other', x['id'], y['id'], w2))
                else:
                    c = lcs(w2, st)
                    if len(c) >= 7: issues.append((day, 'answer-phrase-in-other', x['id'], y['id'], c))
for i in issues: print(*i)
print(len(issues), 'flags')

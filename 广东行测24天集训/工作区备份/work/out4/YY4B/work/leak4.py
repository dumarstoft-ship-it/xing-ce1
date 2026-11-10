"""Same-day leak check: shared text (>=9 chars) and answer phrases appearing in other items. Includes YY4A if present."""
import json, re, itertools, sys, os
def L(p): return [json.loads(l) for l in open(p) if l.strip()] if os.path.exists(p) else []
M = L('/home/user/work/out4/YY4B/questions.jsonl')
A = L('/home/user/work/out4/YY4A/questions.jsonl')
def nz(s): return re.sub(r'[^一-鿿0-9A-Za-z]', '', s or '')
def lcs(a, b):
    a, b = nz(a), nz(b)
    if not a or not b: return ''
    best = ''; prev = [0]*(len(b)+1)
    for i in range(1, len(a)+1):
        cur = [0]*(len(b)+1); ai = a[i-1]
        for j in range(1, len(b)+1):
            if ai == b[j-1]:
                cur[j] = prev[j-1]+1
                if cur[j] > len(best): best = a[i-cur[j]:i]
        prev = cur
    return best
COMMON = {nz(x) for x in ['将以上6个句子重新排列语序正确的','个句子重新排列语序正确的是','将以上6个句子重新排','这段文字接下来最可能','将以上句子重新排列顺序最恰当的一组是','语序正确的一项是','这段文字意在说明','这段文字意在强调','最适合做这段文字标题的是','这段文字接下来最可能讲的是','这段文字主要讲了','这段文字主要介绍了','对这段文字理解准确的是','将以上6个句子重新排列语序正确的是','依次填入画横线部分最恰当的一项是','填入画横线部分最恰当的一项是','将以上6个句子重新排列，语序正确的是','对这段文字理解不准确的是','习近平新时代中国特色社会主义思想','中国特色社会主义']}
def body(q):
    s = q['stem']; parts = s.split('\n')
    return '\n'.join(parts[:-1]) if len(parts) > 1 else s
def alltext(q): return q['stem'] + ' ' + ' '.join(q['options'].values())
issues = []
days = sorted({q['day'] for q in M})
for day in days:
    items = [('M', q) for q in M if q['day'] == day] + [('A', q) for q in A if q['day'] == day]
    for (sx, x), (sy, y) in itertools.combinations(items, 2):
        if sx == 'A' and sy == 'A': continue
        c = lcs(body(x), body(y))
        if len(c) >= 9 and c not in COMMON: issues.append((day, 'shared-text', x['id'], y['id'], c))
        c2 = lcs(alltext(x), alltext(y))
        if len(c2) >= 10 and c2 not in COMMON and c2 != c: issues.append((day, 'shared-text(incl.options)', x['id'], y['id'], c2))
    for sx, x in items:
        ans = x['checked_answer']; at = x['options'].get(ans, '')
        if re.fullmatch(r'[①-⑧\-－—]+', at):  # ordering: check that restored order isn't hinted elsewhere -> skip
            continue
        words = at.split() if (sx == 'A' and x.get('topic') in ('选词填空', '实词填空', '关联词填空')) else [at]
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
                    if len(c) >= 6 and c not in COMMON: issues.append((day, 'answer-phrase-in-other', x['id'], y['id'], c))
for i in issues: print(*i)
print(len(issues), 'flags', '| YY4A items:', len(A))

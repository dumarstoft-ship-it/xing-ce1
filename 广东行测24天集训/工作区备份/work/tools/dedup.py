"""Build a flat question index with cross-paper duplicate groups.
Output: /home/user/work/qindex.jsonl  (one row per question: tag, pid, qno, section, answer, rate, dup_group, norm_head)
"""
import json, glob, os, re, collections
IDX = '/home/user/work/index'; ANS = '/home/user/work/answers'
def norm(t):
    t = re.sub(r'^\s*\d{1,3}\s*[\.．、]?', '', t)
    t = re.sub(r'[\s　（）()“”"\'‘’，,。．.、：:；;！!？?\-—_【】\[\]《》<>·…]', '', t)
    return t
rows = []
for f in sorted(glob.glob(f'{IDX}/*.json')):
    tag = os.path.basename(f)[:-5]
    qs = json.load(open(f))
    afile = f'{ANS}/{tag}.json'
    if not os.path.exists(afile):
        # answers may live under the other repo's tag
        alt = tag[:-3] if tag.endswith('_xc') else tag + '_xc'
        afile = f'{ANS}/{alt}.json' if os.path.exists(f'{ANS}/{alt}.json') else None
    A = json.load(open(afile))['answers'] if afile else {}
    for q in qs:
        if q['kind'] != 'q': continue
        a = A.get(str(q['qno']), {})
        n = norm(q['text'])
        rows.append(dict(tag=tag, pid=tag.replace('_xc', ''), qno=q['qno'], section=q['section'], material=q.get('material'),
                         answer=a.get('ans'), rate=a.get('rate'), yicuo=a.get('yicuo'), n=n, nimg=len(q['images']),
                         ans_file=os.path.basename(afile) if afile else None))
# duplicate grouping by 5-gram shingles of first 120 normalized chars
def sh(s, k=5):
    s = s[:160]
    return {s[i:i+k] for i in range(max(1, len(s)-k+1))}
buckets = collections.defaultdict(list)
for i, r in enumerate(rows):
    if len(r['n']) >= 12: buckets[r['n'][:12]].append(i)
parent = list(range(len(rows)))
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]; x = parent[x]
    return x
S = [sh(r['n']) for r in rows]
# compare within same head bucket plus a looser pass on 8-char heads
for key_len in (12, 8):
    b = collections.defaultdict(list)
    for i, r in enumerate(rows):
        if len(r['n']) >= key_len: b[r['n'][:key_len]].append(i)
    for idxs in b.values():
        if len(idxs) < 2 or len(idxs) > 40: continue
        for x in range(len(idxs)):
            for y in range(x+1, len(idxs)):
                i, j = idxs[x], idxs[y]
                a, c = S[i], S[j]
                if a and c and len(a & c) / len(a | c) > 0.6:
                    parent[find(i)] = find(j)
groups = collections.defaultdict(list)
for i in range(len(rows)): groups[find(i)].append(i)
gid = 0
for g in groups.values():
    gid += 1
    for i in g: rows[i]['dup_group'] = f'D{gid:05d}'; rows[i]['dup_size'] = len(g)
with open('/home/user/work/qindex.jsonl', 'w') as fo:
    for r in rows:
        r2 = dict(r); r2['head'] = r['n'][:40]; del r2['n']
        fo.write(json.dumps(r2, ensure_ascii=False) + '\n')
multi = [g for g in groups.values() if len(g) > 1]
print('questions', len(rows), 'dup groups', len(multi))
# summarize cross-paper duplicates (excluding same pid in two repos)
cross = collections.Counter()
for g in multi:
    pids = sorted({rows[i]['pid'] for i in g})
    if len(pids) > 1: cross[' + '.join(pids)] += 1
for k, v in cross.most_common(40): print(v, k)

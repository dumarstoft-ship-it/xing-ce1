"""比对盲审答案与答案键。用法：python3 cmp_blind.py <盲审目录>"""
import json, os, sys, glob
d = sys.argv[1]; K = json.load(open(f'{d}/blind_key.json'))
A = {}
for f in glob.glob(f'{d}/ans_*.json'): A.update(json.load(open(f)))
tot = ok = 0; out = []
for bid, k in sorted(K.items()):
    a = A.get(bid)
    if a is None: continue
    ans = (a.get('answer') or '').strip().upper()[:1]; tot += 1; good = ans == k['answer']; ok += good
    out.append(dict(bid=bid, id=k['id'], key=k['answer'], blind=ans, agree=good, why=k['why'], issue=a.get('issue', ''), method=a.get('method', '')))
    if not good or a.get('issue'): print(('' if good else 'DIS ') + k['id'], k['answer'], ans, '|', (a.get('issue') or '')[:300])
json.dump(out, open(f'{d}/compare.json', 'w'), ensure_ascii=False, indent=1)
print('agree', ok, '/', tot, '（未作答', len(K) - tot, '）')

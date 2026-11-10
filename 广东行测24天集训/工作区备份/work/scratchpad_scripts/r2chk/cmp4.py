import json, collections
K = json.load(open('/home/user/work/verify/sample4_key.json'))
A = json.load(open('/home/user/work/verify/sample4_answers.json'))
agree = []; dis = []; conf = collections.Counter(); low = []
for y, k in K.items():
    a = A.get(y) or {}
    ans = (a.get('answer') or '').strip().upper()
    conf[a.get('confidence')] += 1
    row = (y, k['id'], k['local'], k['paper'], k['qno'], k.get('variant_of'), k['answer'], ans, a.get('confidence'), (a.get('issue') or ''))
    (agree if ans == k['answer'] else dis).append(row)
    if a.get('confidence') not in ('高',) or a.get('issue'): low.append(row + ((a.get('reason') or '')[:300],))
print('agree', len(agree), 'disagree', len(dis), dict(conf))
for r in dis: print('DIS', r, '\n   ', (A.get(r[0]) or {}).get('reason', '')[:600])
for r in low: print('NOTE', r[:10], '\n   ', r[10])

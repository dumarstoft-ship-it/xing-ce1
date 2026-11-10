import json, os, collections, sys
import os as _os
OUT = _os.environ.get('OUT_DIR', '/home/user/work/out')
REQ = ['id','module','day','group','group_title','topic','source','done_status','stem','options','material_or_article','assets','source_answer','checked_answer','brief_solution','selection_value','variant_of','check_status','flags','notes']
qi = {}
for l in open('/home/user/work/qindex.jsonl'):
    r = json.loads(l); qi[(r['pid'], r['qno'])] = r.get('dup_group')
agents = sys.argv[1:] or sorted(x for x in _os.listdir(OUT) if _os.path.exists(f'{OUT}/{x}/questions.jsonl'))
seen = {}; issues = []; stats = collections.Counter()
for a in agents:
    p = f'{OUT}/{a}/questions.jsonl'
    if not os.path.exists(p): continue
    for l in open(p):
        q = json.loads(l)
        if q.get('group', '').endswith(('BX', 'BR')): continue  # excluded/reserve
        stats[(a, q.get('day'))] += 1
        miss = [k for k in REQ if k not in q]
        if miss: issues.append(f'{a} {q.get("id")}: missing {miss}')
        o = q.get('options') or {}
        if not isinstance(o, dict) or sorted(o) != ['A','B','C','D']: issues.append(f'{a} {q["id"]}: options keys {list(o) if isinstance(o, dict) else type(o)}')
        ca = q.get('checked_answer')
        if not ca or any(ch not in 'ABCD' for ch in str(ca)): issues.append(f'{a} {q["id"]}: checked_answer={ca}')
        if q.get('source_answer') and ca and q['source_answer'] != ca: issues.append(f'{a} {q["id"]}: source {q["source_answer"]} != checked {ca} status={q.get("check_status")}')
        for asset in q.get('assets') or []:
            pa = asset if os.path.isabs(asset) else os.path.join(OUT, a, asset)
            if not os.path.exists(pa) and not os.path.exists(os.path.join(OUT, asset)) and not os.path.exists(os.path.join('/home/user/work/out', asset)): issues.append(f'{a} {q["id"]}: asset missing {asset}')
        s = q.get('source') or {}
        pid = str(s.get('paper', '')).replace('_xc', ''); qno = s.get('qno')
        key = (pid, qno)
        g = qi.get(key)
        k2 = g or key
        if q.get('variant_of'): k2 = ('variant', q['id'])
        if k2 in seen and not q.get('variant_of'):
            issues.append(f'DUP {a} {q["id"]} {key} also {seen[k2]}')
        seen[k2] = f'{a}:{q["id"]}'
        if q.get('module') != '言语' and not (q.get('selection_value') or '').strip(): issues.append(f'{a} {q["id"]}: empty selection_value')
print(dict(stats))
print(len(issues), 'issues'); print('\n'.join(issues[:60]))

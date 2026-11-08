"""把题型标签收短：python3 -I zz_norm_type.py <结果.json>   括号里的补充说明去掉，“主旨概括”记作主旨。"""
import json, sys, re
f = sys.argv[1]
r = json.load(open(f, encoding='utf-8'))
for a in r['articles']:
    for q in a['questions']:
        t0 = q.get('type', '')
        t = re.sub(r'（.*?）|\(.*?\)', '', t0).strip()
        if t == '主旨概括': t = '主旨'
        if t != t0: print(a['id'], t0, '→', t); q['type'] = t
json.dump(r, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

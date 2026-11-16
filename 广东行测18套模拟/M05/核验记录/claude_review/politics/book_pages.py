# 只读：按 pdf_page 取讲义转写文本
import json, sys
p = '/home/user/xing-ce1/学习资料/政治理论常识/颜培天广东政治理论常识.pages.jsonl'
rows = [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]
print('rows', len(rows), 'keys', list(rows[0].keys()))
want = [int(x) for x in sys.argv[1:]]
by = {}
for r in rows:
    by.setdefault(r.get('pdf_page'), []).append(r)
for pg in want:
    for r in by.get(pg, []):
        print('='*30, 'pdf_page', pg, {k: v for k, v in r.items() if k != 'text'})
        print(r.get('text'))

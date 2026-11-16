# 只读：在讲义转写文本中检索关键词，输出命中页码汇总及上下文
import json, sys, re
p = '/home/user/xing-ce1/学习资料/政治理论常识/颜培天广东政治理论常识.pages.jsonl'
rows = [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]
summary = {}
detail = []
for kw in sys.argv[1:]:
    pages = []
    detail.append('#' * 20 + ' ' + kw)
    for r in rows:
        t = r.get('text') or ''
        for m in re.finditer(re.escape(kw), t):
            pages.append(r['pdf_page'])
            s = max(0, m.start() - 120); e = min(len(t), m.end() + 160)
            detail.append(f"  [pdf_page {r['pdf_page']} printed {r.get('printed_page')} {r.get('sections')}] ...{t[s:e].replace(chr(10), ' ')}...")
    summary[kw] = sorted(set(pages))
    if not pages:
        detail.append('  (无命中)')
print('==== 命中页码汇总 ====')
for k, v in summary.items():
    print(f'{k}: {v if v else "无命中"}')
print()
print('\n'.join(detail))

#!/usr/bin/env python3
"""Audit whether lecture pages cited in provenance (Q1-Q15) actually contain the topic.
For each question: keyword hits on cited pages vs. on other pages. Read-only on repo; writes JSON to work dir."""
import json, os
BOOK = '/home/user/xing-ce1/学习资料/政治理论常识/颜培天广东政治理论常识.pages.jsonl'
SEL = '/home/user/xing-ce1/广东行测18套模拟/M04/selection.json'
import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lecture_page_audit.json')
pages = {json.loads(l)['pdf_page']: json.loads(l) for l in open(BOOK, encoding='utf-8')}
sel = {q['number']: q for q in json.load(open(SEL, encoding='utf-8')) if 1 <= q['number'] <= 15}
KW = {
    1: ['毫不动摇', '公有制'], 2: ['主要矛盾', '主要方面'], 3: ['剩余价值', '必要劳动', '剩余劳动'],
    4: ['民主监督', '协商民主', '政治协商'], 5: ['市民化', '进城落户', '宅基地', '城乡融合', '城镇化', '农村'],
    6: ['制度型开放', '自贸', '对外开放', '改革开放'], 7: ['创造性转化', '创新性发展', '传统文化', '文化'],
    8: ['感性认识', '理性认识', '飞跃'], 9: ['四大考验', '执政考验', '精神懈怠', '四大挑战', '执政能力、领导水平'],
    10: ['绿色低碳', '碳', '生态系统'], 11: ['近亲属', '租赁', '优先购买'],
    12: ['地貌', '丹霞', '七星岩', '湖光岩', '喀斯特', '火山'], 13: ['四渡赤水', '金沙江', '泸定桥', '吴起'],
    14: ['北斗', '导航', '短报文'], 15: ['两税法', '一条鞭法', '摊丁入亩', '赋税', '唐朝', '明朝', '清朝']}
res = {}
for n in range(1, 16):
    cited = sel[n]['provenance'].get('book_pages', [])
    kws = KW[n]
    cited_hits = {p: [k for k in kws if k in pages[p]['text']] for p in cited}
    other_hits = {p: [k for k in kws if k in pages[p]['text']] for p in pages if p not in cited}
    other_hits = {p: v for p, v in other_hits.items() if v}
    res[n] = {'cited_pages': cited, 'book_scope': sel[n]['provenance'].get('book_scope'),
              'keywords': kws, 'cited_page_hits': cited_hits,
              'cited_pages_without_any_hit': [p for p, v in cited_hits.items() if not v],
              'uncited_pages_with_hits': other_hits}
json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for n, r in res.items():
    print(f"Q{n}: cited={r['cited_pages']} no-hit={r['cited_pages_without_any_hit']} uncited-hits={list(r['uncited_pages_with_hits'].items())[:6]}")

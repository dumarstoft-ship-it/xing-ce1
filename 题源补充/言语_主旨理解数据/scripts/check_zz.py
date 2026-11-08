"""检查主旨理解题：python3 -I check_zz.py <结果.json> <文章目录>
逐题核对段号、选项、答案；把题干材料和原文第 from_p 到 to_p 段逐字比对，列出删去的和添上（改写）的文字。
题干应当是从原文截取、删改出来的：保留下来的字占题干的比例低于 85%，或者添上的字太多，就报出来。
hide_p 是做完这题之前先收起的段落（会露出答案的提要等），不能落在任何一道题的范围里。
hide_title、contested 要写 true 或 false；正确项就是文章标题的，这题要写 hide_title。"""
import json, sys, os, difflib, re
f, src = sys.argv[1], sys.argv[2]
r = json.load(open(f, encoding='utf-8'))
bad = 0
for art in r['articles']:
    path = os.path.join(src, art['id'] + '.json')
    if not os.path.exists(path): print('找不到文章', art['id']); bad += 1; continue
    a = json.load(open(path, encoding='utf-8'))
    paras = a['paras']
    print('#', art['id'], a['title'], f"（{len(art['questions'])} 题）")
    spans = []
    for i, q in enumerate(art['questions'], 1):
        probs = []
        fp, tp = q.get('from_p'), q.get('to_p')
        if not (isinstance(fp, int) and isinstance(tp, int) and 1 <= fp <= tp <= len(paras)):
            print(f'  第{i}题 段号不对：{fp}-{tp}（全文 {len(paras)} 段）'); bad += 1; continue
        spans.append((fp, tp, i))
        hide = q.get('hide_p') or []
        if not isinstance(hide, list) or any(not isinstance(h, int) or not (1 <= h <= len(paras)) for h in hide):
            probs.append(f'hide_p 要写段号列表：{hide}')
        orig = '\n'.join(paras[p - 1] for p in range(fp, tp + 1))
        pas = (q.get('passage') or '').strip()
        if not pas: probs.append('没有题干材料')
        ops = q.get('options') or []
        if len(ops) != 4 or len(set(ops)) != 4: probs.append('选项不是 4 个不同的')
        if any(o.strip()[:2] in ('A.', 'B.', 'C.', 'D.', 'A．', 'B．', 'C．', 'D．') for o in ops): probs.append('选项带了字母前缀')
        if q.get('answer') not in ('A', 'B', 'C', 'D'): probs.append('答案要写 A/B/C/D')
        if not (q.get('stem') or '').strip(): probs.append('没有题干问句')
        if not (q.get('note') or '').strip(): probs.append('没有说明')
        for k in ('hide_title', 'contested'):
            if k in q and not isinstance(q[k], bool): probs.append(f'{k} 要写 true 或 false')
        norm = lambda x: re.sub(r'[\s“”‘’"\'，,。：:；;？?！!、（）()《》<>·]', '', x or '')
        if q.get('answer') in ('A', 'B', 'C', 'D') and len(ops) == 4 and norm(ops['ABCD'.index(q['answer'])]) == norm(a['title']) and not q.get('hide_title'):
            probs.append('正确项就是文章标题，要写 hide_title: true，否则网页顶上就把答案露出来了')
        sm = difflib.SequenceMatcher(None, orig, pas, autojunk=False)
        kept = sum(b.size for b in sm.get_matching_blocks())
        dels, adds = [], []
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag in ('delete', 'replace') and i2 > i1: dels.append(orig[i1:i2])
            if tag in ('insert', 'replace') and j2 > j1: adds.append(pas[j1:j2])
        ratio = kept / max(1, len(pas))
        addn = sum(len(x) for x in adds)
        if ratio < 0.85: probs.append(f'题干只有 {ratio:.0%} 的字照录原文，改写太多')
        print(f'  第{i}题 第{fp}-{tp}段 {q.get("type","")} 题干 {len(pas)} 字，照录 {ratio:.0%}；删去 {sum(len(x) for x in dels)} 字，添改 {addn} 字')
        for x in dels:
            x = x.replace('\n', '¶')
            if len(x.strip('¶ ')) >= 2: print('      删：' + (x if len(x) <= 60 else x[:28] + '……' + x[-28:]))
        for x in adds:
            x = x.replace('\n', '¶')
            if len(x.strip('¶ ')) >= 1: print('      添：' + x[:60])
        for p in probs: print('    ！' + p)
        bad += bool(probs)
    spans.sort()
    for x, y in zip(spans, spans[1:]):
        if y[0] <= x[1]: print(f'  ！第{x[2]}题和第{y[2]}题段落重叠'); bad += 1
    for i, q in enumerate(art['questions'], 1):
        for h in q.get('hide_p') or []:
            if any(fp <= h <= tp for fp, tp, _ in spans): print(f'  ！第{i}题 hide_p 里的第{h}段落在某道题的范围里'); bad += 1
print('有问题的题：', bad)
sys.exit(1 if bad else 0)

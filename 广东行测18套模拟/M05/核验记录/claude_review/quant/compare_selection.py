#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第二阶段：只读仓库。对 M05 第31-45题：
- 列出 selection.json 的 answer/analysis/source_id/edits/selection_reason/verification；
- 与题源 全部题目.jsonl（按 id）逐字比对题干与选项（含 selection.json 内嵌的 source_question）；
- 与盲解 blind_answers.json 对照答案；
- 与 blind_input.json 比对（确认盲解所用题面就是 selection 题面）。"""
import json, os, difflib

REPO = '/home/user/xing-ce1'
M05 = os.path.join(REPO, '广东行测18套模拟', 'M05')
BANK = os.path.join(REPO, '模考', '2026下半年广东卷_16-33季_AI可读', '全部题目.jsonl')
WD = os.path.dirname(os.path.abspath(__file__))

sel = json.load(open(os.path.join(M05, 'selection.json'), encoding='utf-8'))
bank = {}
with open(BANK, encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line:
            r = json.loads(line); bank[r['id']] = r
blind = json.load(open(os.path.join(WD, 'blind_answers.json'), encoding='utf-8'))
binput = {d['number']: d for d in json.load(open(os.path.join(WD, 'blind_input.json'), encoding='utf-8'))}
paper = {}
with open(os.path.join(M05, '题目.jsonl'), encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line:
            r = json.loads(line); paper[int(r['number'])] = r

def flat(blocks):
    out = []
    for b in blocks or []:
        if b.get('type') == 'text':
            out.append(b['text'])
        else:
            out.append(f"<{b.get('type')}:{b.get('asset_id') or b.get('src') or b.get('id') or ''}>")
    return ''.join(out)

def opts(o):
    return {k: flat(v) for k, v in (o or {}).items()}

def diff(a, b):
    if a == b:
        return '一致'
    sm = difflib.SequenceMatcher(None, a, b)
    parts = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != 'equal':
            parts.append(f"{tag}: 源[{a[i1:i2]}] → 卷[{b[j1:j2]}]")
    return '不一致：' + '；'.join(parts)

rows = []
for q in sel:
    n = int(q['number'])
    if not (31 <= n <= 45):
        continue
    sid = q.get('source_id')
    src = bank.get(sid)
    print('=' * 80)
    print(f"第{n}题  source_id={sid}  subtype={q.get('subtype')}")
    pq = paper[n]
    q = dict(q); q['stem'] = pq['stem']; q['options'] = pq['options']
    print(f"  卷面(题目.jsonl)题干：{flat(q['stem'])}")
    print(f"  卷面选项：{opts(q['options'])}")
    print(f"  题目.jsonl 其他字段：materials={pq.get('materials')} options_mode={pq.get('options_mode')}")
    if src:
        print(f"  题源第{src.get('season')}季 第{src.get('number')}题  answer字段={src.get('answer')}")
        print(f"  题干比对（源→卷）：{diff(flat(src['stem']), flat(q['stem']))}")
        so, qo = opts(src['options']), opts(q['options'])
        print(f"  选项比对：{'一致' if so == qo else {k: diff(so.get(k, ''), qo.get(k, '')) for k in sorted(set(so) | set(qo)) if so.get(k) != qo.get(k)}}")
        if src.get('material'):
            print(f"  题源材料：{src.get('material')}")
        if src.get('source_asset_ids'):
            print(f"  题源图片：{src.get('source_asset_ids')}")
    else:
        print('  !!! 题源中找不到该 id')
    sq = q.get('source_question')
    if sq:
        print(f"  selection内嵌source_question与题源一致：{flat(sq['stem']) == flat(src['stem']) and opts(sq['options']) == opts(src['options']) if src else 'N/A'}")
    bi = binput.get(n)
    print(f"  blind_input 题面与卷面一致：{flat(bi['stem']) == flat(q['stem']) and opts(bi['options']) == opts(q['options'])}")
    print(f"  答案键：{q.get('answer')}   源答案：{q.get('source_answer')}   盲解：{blind[str(n)]['answer']}  → {'一致' if blind[str(n)]['answer'] == q.get('answer') else '不一致!!!'}")
    print(f"  edits：{json.dumps(q.get('edits'), ensure_ascii=False)}")
    print(f"  selection_reason：{q.get('selection_reason')}")
    print(f"  source_notice：{q.get('source_notice')}")
    print(f"  verification：{json.dumps(q.get('verification'), ensure_ascii=False)}")
    print(f"  analysis：{q.get('analysis')}")
    rows.append((n, q.get('answer'), blind[str(n)]['answer']))
print('=' * 80)
print('汇总（题号, 答案键, 盲解）：', rows)
print('一致数：', sum(1 for r in rows if r[1] == r[2]), '/', len(rows))
from collections import Counter
print('答案键字母分布：', Counter(r[1] for r in rows))

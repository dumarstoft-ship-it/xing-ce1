#!/usr/bin/env python3
"""M03 第71-90题：当前题面（题目.jsonl / selection.json）与题库原题（source_question）逐项比对。

检查:
  1. 题干、选项文字是否与原题一致（列出差异）；
  2. 材料文字：去掉分段后是否逐字一致；
  3. 表格：表头、每个单元格是否一致（数字有无转错）；
  4. 图形选项路径是否与原题一致；
  5. 打印 edits / stem_override / selection_reason / verification 摘要。

用法: python3 source_diff_71_90.py [repo_root]
"""
import json, sys, difflib

repo = sys.argv[1] if len(sys.argv) > 1 else '/home/user/xing-ce1'
sel = json.load(open(repo + '/广东行测18套模拟/M03/selection.json', encoding='utf-8'))
vis = {}
for line in open(repo + '/广东行测18套模拟/M03/题目.jsonl', encoding='utf-8'):
    d = json.loads(line)
    vis[d['number']] = d


def blocks_text(bl):
    out = []
    for b in bl:
        if b['type'] == 'text':
            out.append(b['text'])
        elif b['type'] == 'figure':
            out.append('[FIG ' + b.get('path', '') + ']')
        elif b['type'] == 'table':
            out.append('[TABLE ' + str(b.get('title')) + ']')
    return '\n'.join(out)


def norm(s):
    return s.replace('\n', '').replace(' ', '').replace('　', '')


def diff(a, b):
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    res = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op != 'equal':
            res.append('%s 原[%s] → 现[%s]' % (op, a[max(0, i1 - 6):i2 + 6], b[max(0, j1 - 6):j2 + 6]))
    return res


seen_mat = set()
for x in sel:
    n = x['number']
    if not 71 <= n <= 90:
        continue
    sq = x['source_question']
    v = vis[n]
    print('=' * 72)
    print('第%d题  源 %s  源页 %s' % (n, x['source_id'], sq.get('source_pages')))
    # stem
    s_src = blocks_text(sq['stem'])
    s_cur = blocks_text(v['stem'])
    if s_src == s_cur:
        print('  题干: 与原题一致')
    else:
        print('  题干: 有改动')
        print('    原: ' + s_src.replace('\n', ' / '))
        print('    现: ' + s_cur.replace('\n', ' / '))
    if 'stem_override' in x:
        so = x['stem_override']
        so_t = blocks_text(so) if isinstance(so, list) else str(so)
        print('  stem_override 与 题目.jsonl 题干%s' % ('一致' if norm(so_t) == norm(s_cur) else '不一致！'))
    # options
    for k in sorted(set(sq['options']) | set(v['options'])):
        a = blocks_text(sq['options'].get(k, []))
        b = blocks_text(v['options'].get(k, []))
        if a != b:
            print('  选项%s 改动: 原[%s] 现[%s]' % (k, a, b))
    # materials
    src_m = sq.get('material')
    for m in v['materials']:
        key = m['id']
        if key in seen_mat:
            continue
        seen_mat.add(key)
        print('  -- 材料 %s（首次出现，逐项比对）' % key)
        src_blocks = src_m['blocks'] if src_m else []
        src_text = norm(''.join(b['text'] for b in src_blocks if b['type'] == 'text'))
        cur_text = norm(''.join(b['text'] for b in m['blocks'] if b['type'] == 'text'))
        if src_text == cur_text:
            print('     文字（去空白/换行）: 逐字一致')
        else:
            print('     文字差异:')
            for line in diff(src_text, cur_text):
                print('       ' + line)
        st = [b for b in src_blocks if b['type'] == 'table']
        ct = [b for b in m['blocks'] if b['type'] == 'table']
        print('     表格数: 原 %d / 现 %d' % (len(st), len(ct)))
        for i, (a, b) in enumerate(zip(st, ct)):
            if a.get('title') != b.get('title'):
                print('     表%d 标题: 原[%s] 现[%s]' % (i + 1, a.get('title'), b.get('title')))
            if a.get('headers') != b.get('headers'):
                print('     表%d 表头: 原%s\n                现%s' % (i + 1, a.get('headers'), b.get('headers')))
            ra, rb = a.get('rows', []), b.get('rows', [])
            ncell = 0; bad = []
            for r1, r2 in zip(ra, rb):
                for c1, c2 in zip(r1, r2):
                    ncell += 1
                    if c1 != c2:
                        bad.append((r1[0], c1, c2))
            print('     表%d: 原 %d 行 / 现 %d 行；比对 %d 格，不一致 %d 格 %s' % (
                i + 1, len(ra), len(rb), ncell, len(bad), bad[:20]))
            if a.get('notes') != b.get('notes'):
                print('     表%d 注: 原[%s] 现[%s]' % (i + 1, a.get('notes'), b.get('notes')))
            extra_a = {k: a[k] for k in a if k not in ('type', 'title', 'headers', 'rows', 'notes')}
            extra_b = {k: b[k] for k in b if k not in ('type', 'title', 'headers', 'rows', 'notes')}
            if extra_a or extra_b:
                print('     表%d 其它字段: 原%s 现%s' % (i + 1, json.dumps(extra_a, ensure_ascii=False)[:300], json.dumps(extra_b, ensure_ascii=False)[:300]))
        # paragraphs
        cur_paras = [b['text'] for b in m['blocks'] if b['type'] == 'text']
        print('     现材料文字块 %d 个，各块长度 %s' % (len(cur_paras), [len(p) for p in cur_paras]))
        for p in cur_paras:
            print('       > ' + p[:60] + ('…' if len(p) > 60 else ''))
    # editorial info
    for e in x.get('edits', []):
        print('  edit[%s]: %s' % (e.get('type'), json.dumps({k: v_ for k, v_ in e.items() if k != 'type'}, ensure_ascii=False)))
    print('  selection_reason: ' + x.get('selection_reason', ''))
    ver = x.get('verification', {})
    print('  verification: status=%s source_answer_available=%s' % (ver.get('status'), ver.get('source_answer_available')))
    print('  source_answer: %s；source_question.answer: %s' % (x.get('source_answer'), sq.get('answer')))

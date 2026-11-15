import json, difflib, re, sys
base = '/home/user/xing-ce1/广东行测18套模拟/M04/'
sel = json.load(open(base + 'selection.json'))
tm = {}
for l in open(base + '题目.jsonl'):
    if l.strip():
        q = json.loads(l); tm[q['number']] = q

def render(parts):
    out = []
    for p in parts:
        if p.get('type') == 'text': out.append(p['text'])
        else: out.append('[%s]' % json.dumps(p, ensure_ascii=False))
    return ''.join(out)

def norm_layout(s):
    # remove only layout: newlines, spaces (ASCII and full-width ideographic space kept separately)
    s = s.replace('\n', '')
    s = re.sub(r'[ \t]+', '', s)
    return s

report = []
for q in sel:
    n = q['number']
    if not (16 <= n <= 30): continue
    so = q['stem_override']
    sq = q['source_question']
    src_stem = sq.get('stem')
    a = norm_layout(so); b = norm_layout(src_stem)
    same_stem = (a == b)
    diffs = []
    if not same_stem:
        sm = difflib.SequenceMatcher(None, b, a, autojunk=False)
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op != 'equal':
                diffs.append((op, b[max(0,i1-8):i2+8], a[max(0,j1-8):j2+8]))
    # options
    opt_diffs = {}
    for k in 'ABCD':
        so_o = q['options'].get(k); src_o = sq['options'].get(k)
        if norm_layout(so_o or '') != norm_layout(src_o or ''):
            opt_diffs[k] = (src_o, so_o)
    # examinee-visible vs stem_override
    t = tm[n]
    t_stem = render(t['stem'])
    t_same = norm_layout(t_stem) == norm_layout(so)
    t_opt_same = all(norm_layout(render(t['options'][k])) == norm_layout(q['options'][k]) for k in 'ABCD')
    # character class checks
    weird = sorted(set(ch for ch in so if ord(ch) > 0x2000 and not ('一' <= ch <= '鿿')))
    report.append({'number': n, 'stem_identical_after_layout_norm': same_stem, 'stem_diffs': diffs,
                   'option_diffs': opt_diffs, 'timu_stem_matches_override': t_same, 'timu_options_match': t_opt_same,
                   'nonCJK_symbols_in_override': ''.join(weird),
                   'raw_has_spaces_in_override': bool(re.search(r'[ ]', so)),
                   'src_answer': q['source_answer'], 'editor_answer': q['answer']})
for r in report:
    print(json.dumps(r, ensure_ascii=False))

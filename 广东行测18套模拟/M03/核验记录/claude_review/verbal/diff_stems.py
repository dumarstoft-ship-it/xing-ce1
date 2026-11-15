import json, difflib, re, sys
# 用法：python3 diff_stems.py [selection.json] [题目.jsonl]；缺省为仓库中M03的两份文件
M03 = '/home/user/xing-ce1/广东行测18套模拟/M03'
sel_path = sys.argv[1] if len(sys.argv) > 1 else M03 + '/selection.json'
qj_path = sys.argv[2] if len(sys.argv) > 2 else M03 + '/题目.jsonl'
d = json.load(open(sel_path, encoding='utf-8'))
qj = {}
for line in open(qj_path, encoding='utf-8'):
    if line.strip():
        o = json.loads(line); qj[o['number']] = o
def norm_source(s):
    # remove hard line breaks (but keep the final newline before instruction), and spaces around blanks
    lines = s.split('\n')
    return lines
out = []
for x in d:
    n = x['number']
    if not (16 <= n <= 30):
        continue
    src = x['source_question']['stem']
    ov = x['stem_override']
    # source: join lines except the last line (instruction) separated
    src_lines = src.split('\n')
    # strategy: remove all '\n' and ' ' from both, compare char by char
    a = src.replace('\n','').replace(' ','')
    b = ov.replace('\n','').replace(' ','')
    same = (a == b)
    rec = {'number': n, 'source_id': x['source_id'], 'identical_after_removing_newlines_spaces': same}
    if not same:
        sm = difflib.SequenceMatcher(None, a, b)
        rec['diffs'] = [(tag, a[i1:i2], b[j1:j2]) for tag,i1,i2,j1,j2 in sm.get_opcodes() if tag != 'equal']
    # spaces in source that were not around blanks
    spaces = [m.start() for m in re.finditer(' ', src)]
    ctx = []
    for p in spaces:
        ctx.append(src[max(0,p-3):p+4].replace('\n','\\n'))
    rec['source_space_contexts'] = ctx
    # option comparison
    so = x['source_question']['options']
    rec['options_identical'] = (so == x['options'])
    # compare with 题目.jsonl
    q = qj[n]
    stem_txt = ''.join(s['text'] for s in q['stem'] if s['type']=='text')
    rec['qjsonl_stem_equals_override'] = (stem_txt.replace('\n','') == ov.replace('\n',''))
    qopts = {k: ''.join(t['text'] for t in v if t['type']=='text') for k,v in q['options'].items()}
    rec['qjsonl_options_equal'] = (qopts == x['options'])
    # blanks
    rec['blanks_source'] = re.findall(r'_+', src)
    rec['blanks_override'] = re.findall(r'_+', ov)
    out.append(rec)
print(json.dumps(out, ensure_ascii=False, indent=1))

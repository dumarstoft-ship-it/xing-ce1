# Character-level comparison of M05/题目.jsonl (Q51-65) against the source text.
# Read-only on the repo. Shows exact differences, including whitespace and newlines.
import json, difflib, unicodedata
REPO='/home/user/xing-ce1'
m05=[json.loads(l) for l in open(f'{REPO}/广东行测18套模拟/M05/题目.jsonl',encoding='utf-8') if l.strip()]
m05={r['number']:r for r in m05 if 51<=r['number']<=65}
sel={q['number']:q for q in json.load(open(f'{REPO}/广东行测18套模拟/M05/selection.json',encoding='utf-8')) if 51<=q['number']<=65}
js={}
for l in open(f'{REPO}/江浙行测_AI题库/questions.jsonl',encoding='utf-8'):
    r=json.loads(l); js[r['question_id']]=r
gd={}
for l in open(f'{REPO}/模考/2026下半年广东卷_16-33季_AI可读/全部题目.jsonl',encoding='utf-8'):
    r=json.loads(l); gd[r['id']]=r
def blocks_text(blocks):
    out=[]
    for b in blocks:
        if b.get('type')=='text': out.append(b['text'])
        else: out.append('[%s:%s]'%(b.get('type'),b.get('ref') or b.get('id') or b.get('src')))
    return ''.join(out)
def show(s): return s.replace('\n','⏎').replace(' ','␣').replace('　','□')
def diff(a,b,label):
    if a==b:
        print(f'  {label}: IDENTICAL'); return
    print(f'  {label}: DIFFER')
    sm=difflib.SequenceMatcher(None,a,b,autojunk=False)
    for op,i1,i2,j1,j2 in sm.get_opcodes():
        if op!='equal':
            print(f'    {op}: M05[{i1}:{i2}]={show(a[i1:i2])!r}  SRC[{j1}:{j2}]={show(b[j1:j2])!r}  ctx=…{show(a[max(0,i1-8):i2+8])}…')
for n in range(51,66):
    q=m05[n]; sid=sel[n]['source_id']
    print('='*10, n, sid)
    stem=blocks_text(q['stem'])
    if sid in js:
        s=js[sid]
        diff(stem, s['stem'], 'stem')
        for k in 'ABCD':
            diff(blocks_text(q['options'][k]), s['options'][k], f'opt {k}')
        if q.get('materials') or s.get('materials'):
            mt=[blocks_text(m['blocks']) for m in q.get('materials',[])]
            st=[m['content'] for m in s.get('materials',[])]
            for i,(a,b) in enumerate(zip(mt,st)): diff(a,b,f'material {i}')
            if len(mt)!=len(st): print('  material count differ', len(mt), len(st))
    else:
        s=gd[sid]
        diff(stem, blocks_text(s['stem']), 'stem')
        for k in 'ABCD':
            diff(blocks_text(q['options'][k]), blocks_text(s['options'][k]), f'opt {k}')
        if q.get('materials') or s.get('material'):
            print('  materials M05:', q.get('materials'), ' SRC:', s.get('material'))
    # flag suspicious characters in M05 text
    alltxt = stem + ''.join(blocks_text(q['options'][k]) for k in 'ABCD') + ''.join(blocks_text(m['blocks']) for m in q.get('materials',[]))
    flags=[]
    for i,ch in enumerate(alltxt):
        if ch in ':?;,!()' : flags.append(f'half-width {ch!r} at …{show(alltxt[max(0,i-6):i+6])}…')
        if ch==' ': flags.append(f'space at …{show(alltxt[max(0,i-6):i+6])}…')
    nl=[show(alltxt[max(0,i-10):i+10]) for i,ch in enumerate(alltxt) if ch=='\n']
    print('  M05 newlines:', nl)
    for f in flags: print('  FLAG', f)

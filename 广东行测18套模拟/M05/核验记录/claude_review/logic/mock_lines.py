# Reconstruct the original line layout of mock-bank stems from per-line span widths.
# Each original line's text width ~= span x1 - 68.05 (line 1 starts its text after the question number at 52.40).
# Estimate glyph widths: full-width CJK/punct = W, ASCII = W/2. Greedy-fit text paragraphs (split at M05 '\n')
# onto the observed line widths, and report for every hard break in the text whether the original line was short (true paragraph end).
import json, unicodedata
REPO='/home/user/xing-ce1'
sel={q['number']:q for q in json.load(open(f'{REPO}/广东行测18套模拟/M05/selection.json',encoding='utf-8')) if 51<=q['number']<=65}
gd={}
for l in open(f'{REPO}/模考/2026下半年广东卷_16-33季_AI可读/全部题目.jsonl',encoding='utf-8'):
    r=json.loads(l); gd[r['id']]=r
def cw(ch, W):
    return W/2 if ord(ch)<128 else W
for n in range(51,66):
    sid=sel[n]['source_id']
    if sid not in gd: continue
    r=gd[sid]; spans=r['source_spans']
    stem=''.join(b.get('text','') for b in r['stem'])
    paras=stem.split('\n')
    # estimate W from a full line: full text width 448.3 / chars
    W=10.934
    widths=[(s['bbox_pt'][2]-68.05) for s in spans]
    print('='*6,'M05',n,sid)
    li=0
    for pi,p in enumerate(paras):
        tw=sum(cw(c,W) for c in p)
        # how many lines this paragraph takes in a 448.3pt column
        import math
        nlines=max(1,math.ceil((tw-0.5)/448.3))
        last=tw-(nlines-1)*448.3
        obs=widths[li:li+nlines]
        print(f'  para{pi+1}: chars={len(p):3d} est_width={tw:7.1f}pt -> {nlines} line(s), est last-line width={last:6.1f}; observed spans {[round(x,1) for x in obs]}')
        print(f'         text: {p[:30]}…{p[-14:]}')
        li+=nlines
    print(f'  remaining spans (options etc.): {[round(x,1) for x in widths[li:]]}')

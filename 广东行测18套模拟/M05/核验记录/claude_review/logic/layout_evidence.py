# Evidence for the original line layout of six mock-bank stems. The original mock PDFs are not in the repo; the bank's
# source_spans are per-line bboxes (PDF pt): text margin x0=68.05 (line 1 starts with the question number at 52.40),
# right margin x1~516.4. A soft wrap can only follow a FULL line (排满). If the line before the 设问/收尾句 is short
# (未排满) and a following line's width equals the width of the 设问/收尾句 alone, that sentence stood on its own line
# in the original, while the bank (and M05) merged it into the previous paragraph.
import json
REPO='/home/user/xing-ce1'
gd={}
for l in open(f'{REPO}/模考/2026下半年广东卷_16-33季_AI可读/全部题目.jsonl',encoding='utf-8'):
    r=json.loads(l); gd[r['id']]=r
W=10.934
def width(s): return sum(W/2 if c==' ' else (W*0.55 if ord(c)<128 else W) for c in s)
cases=[('M05-52','gd-mock-2026h2-s16-q59','要使上述观点成立'),('M05-55','gd-mock-2026h2-s19-q59','要使上述推理成立'),
       ('M05-57','gd-mock-2026h2-s18-q63','下列选项最能指出'),('M05-59','gd-mock-2026h2-s19-q62','下列选项如果为真'),
       ('M05-61','gd-mock-2026h2-s18-q64','下列选项的逻辑结构'),('M05-63','gd-mock-2026h2-s19-q52','中标结果出来后发现')]
for label,sid,marker in cases:
    r=gd[sid]; stem=''.join(b.get('text','') for b in r['stem'])
    para=[p for p in stem.split('\n') if marker in p][0]
    sent=para[para.index(marker):]
    if '\n' in sent: sent=sent.split('\n')[0]
    sw=width(sent)
    before=para[:para.index(marker)]
    print('='*8, label, sid, '原PDF页', r['source_pages'])
    print(f'  M05/源库文本：“…{before[-12:]}{sent}” —— 该句与上一句同段（句前无换行）')
    print(f'  该句单独成行时推算宽度 {sw:.1f}pt：{sent}')
    best=None
    for k,s in enumerate(r['source_spans']):
        x0,y0,x1,y1=s['bbox_pt']; ow=x1-68.05
        full='排满' if x1>510 else '未排满'
        hit=abs(ow-sw)<=0.08*sw
        print(f'   行{k+1}: p{s["pdf_page"]} y0={y0:6.1f} x0={x0:5.1f} x1={x1:6.1f} {full:3s} 宽{ow:6.1f}pt' + ('   ≈该句单独一行' if hit and best is None else ''))
        if hit and best is None: best=k
    if best is not None:
        prev=r['source_spans'][best-1]['bbox_pt']
        print(f'  结论：行{best+1}（{r["source_spans"][best]["bbox_pt"][2]-68.05:.1f}pt）≈该句宽度；其上一行 x1={prev[2]:.1f} 未排满（软折行不可能），故原卷该句另起一行。')

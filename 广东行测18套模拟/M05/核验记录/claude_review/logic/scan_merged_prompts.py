# Heads-up scan (outside Q51-65 too): mock-sourced M05 questions whose last sentence (设问) is merged into the previous
# paragraph in the text, while the bank's line boxes show a short line followed by a line whose width matches that sentence.
import json, re
REPO='/home/user/xing-ce1'
gd={}
for l in open(f'{REPO}/模考/2026下半年广东卷_16-33季_AI可读/全部题目.jsonl',encoding='utf-8'):
    r=json.loads(l); gd[r['id']]=r
sel={q['number']:q for q in json.load(open(f'{REPO}/广东行测18套模拟/M05/selection.json',encoding='utf-8'))}
W=10.934
def width(s): return sum(W/2 if c==' ' else (W*0.55 if ord(c)<128 else W) for c in s)
hits=[]
for n,q in sorted(sel.items()):
    sid=q['source_id']
    if sid not in gd: continue
    r=gd[sid]; stem=''.join(b.get('text','') for b in r['stem'] if b.get('type')=='text')
    last=stem.split('\n')[-1]
    sents=re.split(r'(?<=[。？！：])', last)
    sents=[s for s in sents if s]
    if len(sents)<2: continue
    tail=sents[-1]
    if not re.match(r'^(下列|要使|以下|由此|根据|据此|则|那么|问|这段|如果|若)', tail): continue
    tw=width(tail); spans=r['source_spans']
    for k in range(1,len(spans)):
        prev=spans[k-1]['bbox_pt']; cur=spans[k]['bbox_pt']
        if prev[2]<505 and abs((cur[2]-68.05)-tw)<=0.08*tw and cur[0]>60:
            hits.append((n,sid,tail)); break
for h in hits: print('M05第%d题 %s 设问疑另起一行：%s'%h)
print('共', len(hits), '题')

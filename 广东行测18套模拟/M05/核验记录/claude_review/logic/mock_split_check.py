# Test two hypotheses for the original layout of mock-bank stems whose 设问 is merged in the text:
#  H_merged : 设问 continues in the same paragraph (text exactly as in M05)
#  H_split  : 设问 / closing sentence starts a new line
# Predict each line's width with W=10.934pt per full-width char (ASCII = 0.5W, digits in "（n）" ~0.95W)
# and compare with the observed span widths (x1-68.05). Column width 448.3pt.
import json, math
REPO='/home/user/xing-ce1'
gd={}
for l in open(f'{REPO}/模考/2026下半年广东卷_16-33季_AI可读/全部题目.jsonl',encoding='utf-8'):
    r=json.loads(l); gd[r['id']]=r
W=10.934; COL=448.3
def width(s): return sum(W/2 if ord(c)<128 and c==' ' else (W*0.55 if ord(c)<128 else W) for c in s)
def layout(paras):
    out=[]
    for p in paras:
        w=width(p); n=max(1,math.ceil((w-1)/COL))
        out += [COL]*(n-1)+[w-(n-1)*COL]
    return [round(x,1) for x in out]
cases={
 'M05-52 gd-mock-2026h2-s16-q59':('gd-mock-2026h2-s16-q59','要使上述观点成立'),
 'M05-55 gd-mock-2026h2-s19-q59':('gd-mock-2026h2-s19-q59','要使上述推理成立'),
 'M05-57 gd-mock-2026h2-s18-q63':('gd-mock-2026h2-s18-q63','下列选项最能指出'),
 'M05-59 gd-mock-2026h2-s19-q62':('gd-mock-2026h2-s19-q62','下列选项如果为真'),
 'M05-61 gd-mock-2026h2-s18-q64':('gd-mock-2026h2-s18-q64','下列选项的逻辑结构'),
 'M05-63 gd-mock-2026h2-s19-q52':('gd-mock-2026h2-s19-q52','中标结果出来后发现'),
}
for label,(sid,marker) in cases.items():
    r=gd[sid]; stem=''.join(b.get('text','') for b in r['stem'])
    paras=stem.split('\n')
    obs=[round(s['bbox_pt'][2]-68.05,1) for s in r['source_spans']]
    merged=layout(paras)
    sp=[]
    for p in paras:
        if marker in p:
            i=p.index(marker); sp += [p[:i], p[i:]]
        else: sp.append(p)
    split=layout(sp)
    print('='*6,label)
    print('  observed spans (stem part first):', obs[:len(split)+1], ' (…', len(obs),'spans total incl. options)')
    print('  H_merged predicted:', merged)
    print('  H_split  predicted:', split)
    def err(pred): 
        return round(sum(abs(a-b) for a,b in zip(pred,obs)),1) if len(pred)<=len(obs) else None
    print('  total |error| merged =', err(merged), '  split =', err(split))

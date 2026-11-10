# -*- coding: utf-8 -*-
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from data_g1 import G1, FIG
from data_g2 import G2
from data_g3 import G3
P='/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/pd3a'
meta=json.load(open(f'{P}/meta.json'))
OUT='/home/user/work/out3/PD3A'
groups=[('D09-G1','平面类图推（第3组·上）',G1),('D09-G2','平面类图推（第3组·下）',G2),('D09-G3','空间类图推（第3组）',G3)]
recs=[]; n=0
for gid,gt,items in groups:
    for i,it in enumerate(items,1):
        n+=1
        tag,q=it['key'].rsplit('-',1); q=int(q)
        m=meta[it['key']]
        asset=f"assets/{tag}-{q}.png"
        assert os.path.exists(f'{OUT}/{asset}'), asset
        flags=list(it.get('flags',[]))
        recs.append(dict(
            id=f'PD3A-{n:03d}', module='判断', day='D09', group=gid, group_title=gt,
            topic=it['topic'], order=i,
            source=dict(paper=tag, file=m['file'], page=m['pages'][0], pages=m['pages'], qno=q,
                        ans_file=it['ans_file'], ans_page=it['ans_page'], version_note=''),
            done_status='已做情况未知',
            stem=it['stem'], options=it.get('opts',dict(FIG)),
            material_or_article=None, assets=[asset],
            source_answer=it['ans'], checked_answer=it['ans'],
            brief_solution=it['sol'], selection_value=it['val'],
            variant_of=None, check_status='已核验', flags=flags, notes=it['notes'],
            replaced_from=None, img_dups=it.get('dups',[]),
            space=(gid=='D09-G3')))
with open(f'{OUT}/questions.jsonl','w') as f:
    for r in recs: f.write(json.dumps(r,ensure_ascii=False)+'\n')
print(len(recs))
from collections import Counter
print(Counter(r['checked_answer'] for r in recs))
for g in ['D09-G1','D09-G2','D09-G3']:
    seq=[r['checked_answer'] for r in recs if r['group']==g]
    print(g,len(seq),''.join(seq), 'adjacent-dup' if any(a==b for a,b in zip(seq,seq[1:])) else 'ok')
allseq=[r['checked_answer'] for r in recs]
print('cross-boundary adjacent dup', any(a==b for a,b in zip(allseq,allseq[1:])))

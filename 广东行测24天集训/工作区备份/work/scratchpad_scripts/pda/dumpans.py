import json, os, re, collections, sys
sys.path.insert(0,'.')
from anstext import segs
inv=json.load(open('inv.json'))
by=collections.defaultdict(list)
for r in inv:
    if r['cls'] in ('?',) and r['nimg']==0: continue
    by[r['tag']].append(r)
out={}
for tag,rs in sorted(by.items()):
    m=re.match(r'([A-Z]+)(\d{4})',tag); y=int(m.group(2))
    if y<2017: continue
    af=f'/home/user/work/answers/{tag}.json'
    if not os.path.exists(af):
        alt=tag[:-3] if tag.endswith('_xc') else tag+'_xc'
        af=f'/home/user/work/answers/{alt}.json'
        if not os.path.exists(af): continue
    a=json.load(open(af))
    try: S=segs('/home/user/'+a['file'])
    except Exception as e: print('ERR',tag,e); continue
    for r in rs:
        s=S.get(r['qno'])
        out[f"{tag}-{r['qno']}"]=dict(cls=r['cls'],ans=a['answers'].get(str(r['qno']),{}).get('ans'),page=s['page'] if s else None,text=s['text'][:700] if s else None, afile=a['file'])
json.dump(out,open('anstexts.json','w'),ensure_ascii=False)
print(len(out))

import json,unicodedata,re,sys
qi={}
for l in open('/home/user/work/qindex.jsonl'):
    r=json.loads(l); qi[(r['tag'],r['qno'])]=r
keys=sys.argv[1:]
out={}
for key in keys:
    pid,q=key.rsplit('-',1); q=int(q)
    found=None
    for tag in (pid,pid+'_xc'):
        try: d=json.load(open(f'/home/user/work/index/{tag}.json'))
        except FileNotFoundError: continue
        for x in d:
            if x['kind']=='q' and x['qno']==q: found=(tag,x); break
        if found: break
    if not found: out[key]=None; continue
    tag,x=found
    t=unicodedata.normalize('NFKC',x['text'])
    out[key]=dict(tag=tag,file=x['file'],segs=x['segs'],text=t,images=x.get('images'))
json.dump(out,open('raw.json','w'),ensure_ascii=False,indent=1)
for k,v in out.items():
    if v is None: print('=====',k,'NONE'); continue
    print('=====',k,v['tag'],'pages',sorted(set(s[0]+1 for s in v['segs'])),'imgs',len(v['images'] or []))
    print(v['text'])

import json,re,sys
C=[json.loads(l) for l in open('/home/user/work/out/claims.jsonl')]
taken={}
for c in C:
    for k in c.get('dups',[c['key']]): taken.setdefault(k,c['owner'])
def show(tag, qnos, maxm=1600, maxq=420):
    d=json.load(open(f'/home/user/work/index/{tag}.json'))
    mids=[]
    for x in d:
        if x['kind']=='q' and x['qno'] in qnos and x.get('material') not in mids: mids.append(x.get('material'))
    for x in d:
        if x['kind']=='material' and x['mid'] in mids:
            t=re.sub(r'· 本试卷由粉笔[^\n]*\n[^\n]*\n','',x['text'])
            print('=== MAT',x['mid'],x['segs'],'imgs',len(x['images'])); print(t[:maxm])
    for x in d:
        if x['kind']=='q' and x['qno'] in qnos:
            k=f"{tag.replace('_xc','')}-{x['qno']}"
            print(f"--- Q{x['qno']} [{taken.get(k,'free')}] segs={x['segs']} imgs={len(x['images'])}"); print(re.sub(r'\s+',' ',re.sub(r'· 本试卷由粉笔[^\n]*\n','',x['text']))[:maxq])
args=sys.argv[1:]
for a in args:
    tag,qs=a.split(':'); a0,a1=map(int,qs.split('-'))
    print('##########',tag); show(tag, list(range(a0,a1+1)))

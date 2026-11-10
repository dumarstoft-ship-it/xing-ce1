import json,sys,unicodedata,re
qi={}
for l in open('/home/user/work/qindex.jsonl'):
    r=json.loads(l); qi[(r['pid'],r['qno'],r['tag'])]=r
def get(key):
    pid,q=key.rsplit('-',1); q=int(q)
    for tag in (pid,pid+'_xc'):
        try: d=json.load(open(f'/home/user/work/index/{tag}.json'))
        except FileNotFoundError: continue
        for x in d:
            if x['kind']=='q' and x['qno']==q:
                r=qi.get((pid,q,tag),{})
                return tag,x,r
    return None,None,None
for key in sys.argv[1:]:
    tag,x,r=get(key)
    if not x: print('=====',key,'NOT FOUND'); continue
    t=unicodedata.normalize('NFKC',x['text'])
    t=re.sub(r'·\s*本试卷由粉笔用户.*?生成\n?','',t)
    print('=====',key,tag,'ans',r.get('answer'),'rate',r.get('rate'),'yc',r.get('yicuo'),'dup',r.get('dup_size'),'p',x['segs'][0][0]+1)
    print(t.strip())

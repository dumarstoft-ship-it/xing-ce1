# blind show: prints question text only (no answers / no yicuo)
import json,sys,os,re
W='/home/user/work'
qi={}
for l in open(f'{W}/qindex.jsonl'):
    r=json.loads(l); qi[(r['pid'],r['qno'])]=r
idx={}
def load(tag):
    if tag not in idx:
        p=f'{W}/index/{tag}.json'
        idx[tag]=json.load(open(p)) if os.path.exists(p) else []
    return idx[tag]
both = '--both' in sys.argv
for key in [a for a in sys.argv[1:] if not a.startswith('--')]:
    pid,q=key.rsplit('-',1); q=int(q)
    r=qi.get((pid,q),{})
    tags=[t for t in (pid,pid+'_xc') if os.path.exists(f'{W}/index/{t}.json')]
    print('='*8,key,'rate=',r.get('rate'),'dup=',r.get('dup_size'),'tags=',tags)
    for t in (tags if both else tags[:1]):
        for x in load(t):
            if x.get('kind')=='q' and x['qno']==q:
                print('[%s p%s]'%(t,[s[0]+1 for s in x['segs']]))
                print(x['text'].strip())
                if x.get('images'): print('IMAGES:',x['images'])

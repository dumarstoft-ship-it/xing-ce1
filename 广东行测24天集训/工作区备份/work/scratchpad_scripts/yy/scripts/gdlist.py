import json, re, sys, glob, os
IDX='/home/user/work/index'
tags=sorted(os.path.basename(p)[:-5] for p in glob.glob(IDX+'/GD20*.json'))
def classify(t):
    tt=t.replace('\n','').replace(' ','')
    if re.search(r'重新排列|排序|语序', tt): return '排序'
    if re.search(r'填入.{0,8}横线.{0,12}(一句|句子)|最恰当的一句|填入.*?的句子', tt): return '语句填空'
    if re.search(r'依次填入|填入.{0,8}(横线|括号|空)|填入画横线', tt):
        return '填空?'
    return '其他'
out=[]
for tag in tags:
    d=json.load(open(f'{IDX}/{tag}.json'))
    for x in d:
        if x['kind']!='q': continue
        t=x.get('text') or ''
        c=classify(t)
        if x.get('section')=='言语' or (x.get('section') is None and c!='其他') or (c in ('排序','语句填空','填空?')):
            out.append(dict(tag=tag,qno=x['qno'],sec=x.get('section'),cls=c,head=t.replace('\n','')[:70]))
json.dump(out,open(sys.argv[1],'w'),ensure_ascii=False,indent=0)
import collections
cc=collections.Counter((o['tag'],o['cls']) for o in out)
for tag in tags:
    print(tag, {k[1]:v for k,v in cc.items() if k[0]==tag}, 'secs', collections.Counter(o['sec'] for o in out if o['tag']==tag))

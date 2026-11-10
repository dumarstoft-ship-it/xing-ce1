import json,sys,re
IDX='/home/user/work/index'
tag=sys.argv[1]; lo=int(sys.argv[2]); hi=int(sys.argv[3]); mlen=int(sys.argv[4]) if len(sys.argv)>4 else 700
d=json.load(open(f'{IDX}/{tag}.json'))
for x in d:
    if x['kind']=='material':
        qn=[int(q['qno']) for q in d if q['kind']=='q' and q.get('material')==x['mid']]
        if qn and lo<=min(qn)<=hi:
            print('=== MAT',x['mid'],'imgs',len(x['images'])); print(re.sub(r'\n','',x['text'])[:mlen])
    if x['kind']=='q' and lo<=int(x['qno'])<=hi:
        t=re.sub(r'\n',' ',x['text'])
        print(f"  Q{x['qno']} [{len(x['images'])}img] {t[:mlen if int(x['qno'])==hi and x.get('material') is None else 260]}")

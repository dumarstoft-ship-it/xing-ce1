import json,sys,re
IDX='/home/user/work/index'
tag=sys.argv[1]; lo=int(sys.argv[2]); hi=int(sys.argv[3])
full='--full' in sys.argv
d=json.load(open(f'{IDX}/{tag}.json'))
for x in d:
    if x['kind']=='material':
        qn=[int(q['qno']) for q in d if q['kind']=='q' and q.get('material')==x['mid']]
        if qn and lo<=min(qn)<=hi:
            print('=== MAT',x['mid'],x['segs'],'imgs',len(x['images']))
            print(x['text'][:None if full else 1500])
    if x['kind']=='q' and lo<=int(x['qno'])<=hi:
        print('--- Q',x['qno'],x.get('section'),x.get('material'),x['segs'],'imgs',len(x['images']))
        print(x['text'][:None if full else 600])

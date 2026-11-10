import json,sys,re
c=json.load(open('cands.json'))
typ=sys.argv[1]
for x in c:
    if x['taken'] is None and x['typ']==typ:
        print(x['key'], 'n=%d'%x['n'], 'rate=%s'%x['rate'], 'dup=%s'%x['dupsize'], x['prompt'][-50:])

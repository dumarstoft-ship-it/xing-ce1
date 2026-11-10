import json,sys
M=json.load(open('meta.json'))
for k in sys.argv[1:]:
    v=M[k]
    for t,x in v['versions'].items():
        print('=====',k,t,x['file'][-40:],x['pages'],'IMG' if x.get('images') else '')
        print(x['stem'])
        for kk in 'ABCD': print(kk,':',x['options'].get(kk))

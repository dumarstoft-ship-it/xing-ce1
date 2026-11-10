import json, sys, difflib
d=json.load(open('drafts.json'))
for k in sys.argv[1:]:
    x=d[k]; print('=====',k); print(x['stem']); print(json.dumps(x['options'],ensure_ascii=False))
    if 'alt' in x:
        a=x['alt']
        if a['stem']!=x['stem']:
            for op in difflib.SequenceMatcher(None,x['stem'],a['stem'],autojunk=False).get_opcodes():
                if op[0]!='equal': print('   ALTDIFF',op[0], repr(x['stem'][max(0,op[1]-6):op[2]+6]), '->', repr(a['stem'][max(0,op[3]-6):op[4]+6]))
        if a['options']!=x['options']: print('   ALT opts', json.dumps(a['options'],ensure_ascii=False))

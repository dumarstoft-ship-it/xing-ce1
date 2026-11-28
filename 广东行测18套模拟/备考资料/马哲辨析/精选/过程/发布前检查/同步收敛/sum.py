import sys,json
for f in sys.argv[2:]:
    s=open(f,encoding='utf8').read()
    print('===',f)
    if not s.strip(): print('(empty yet)'); continue
    i=s.find('\nEXAMPLE'); j=s.find('\nPAGE ERRORS'); k=min([x for x in (i,j,len(s)) if x>0])
    try:
        d=json.loads(s[:k])
        print({x:d[x] for x in ['flags','seeds','rounds','steps','answers','resets','writes','maxSettle10','nerr','clean','sec']})
        for t,v in sorted(d['types'].items(), key=lambda kv:-kv[1]['rounds']): print('  ',v['rounds'],t,'| seeds',v['seeds'])
    except Exception as e: print('parse fail',e,s[:200])
    want=sys.argv[1].split(',')
    for line in s[k:].split('\n'):
        if any(line.startswith('EXAMPLE '+w) for w in want if w) or line.startswith('PAGE') or line.startswith('unhandled'): print(line[:1100])

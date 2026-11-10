import json, sys, re, os, unicodedata, pymupdf
pymupdf.TOOLS.mupdf_display_errors(False)
W='/home/user/work'
def norm(s): return unicodedata.normalize('NFKC', s)
pid=sys.argv[1]; qnos=[int(x) for x in sys.argv[2].split(',')]
mode=sys.argv[3] if len(sys.argv)>3 else 'qm'
tags=[t for t in (pid, pid+'_xc') if os.path.exists(f'{W}/index/{t}.json')]
for t in tags:
    d=json.load(open(f'{W}/index/{t}.json'))
    mats={x['mid']:x for x in d if x['kind']=='material'}
    shown=set()
    for q in d:
        if q['kind']=='q' and q['qno'] in qnos:
            m=q.get('material')
            print(f"=== [{t}] Q{q['qno']} sec={q.get('section')} mat={m} segs={q['segs']} file={q['file']}")
            if 'm' in mode and m in mats and m not in shown:
                shown.add(m)
                print(f"--- MATERIAL {m} segs={mats[m]['segs']} images={mats[m].get('images')}")
                print(norm(mats[m]['text']))
            print('--- Q:'); print(norm(q['text']))
            a=f'{W}/answers/{t}.json'
            if os.path.exists(a):
                A=json.load(open(a)); r=A['answers'].get(str(q['qno']))
                print('--- ANS', t, r, A['file'])
    if 'a' in mode:
        a=f'{W}/answers/{t}.json'
        if os.path.exists(a):
            A=json.load(open(a)); doc=pymupdf.open('/home/user/'+A['file'])
            txt=norm('\n'.join(p.get_text() for p in doc))
            for qn in qnos:
                for m in re.finditer(r'(?:^|\n)\s*(?:【\s*)?%d\s*[、\.．】]'%qn, txt):
                    seg=txt[m.start():m.start()+900]
                    print(f'--- ANALYSIS {t} Q{qn} @ {m.start()}:'); print(seg)

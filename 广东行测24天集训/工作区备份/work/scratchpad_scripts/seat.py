import json, glob, os, re, sys
sys.argv=[sys.argv[0]]+sys.argv[1:]
exec(open('formal.py').read().split("prx = re.compile")[0])
pat = re.compile(sys.argv[1]); mx = int(sys.argv[2]) if len(sys.argv) > 2 else 300
seen=set()
for f in sorted(glob.glob(W + '/index/*.json')):
    tag = os.path.basename(f)[:-5]; pid = tag.replace('_xc', '')
    if re.match(r'GD202[456]', pid): continue
    rows = json.load(open(f))
    for q in rows:
        if q.get('kind') not in ('q','material') : continue
        if q.get('section') not in ('判断', None): continue
        t = q['text'].replace('\n', ' ')
        if not pat.search(t): continue
        key = f"{pid}-{q.get('qno')}" if q.get('kind')=='q' else q.get('mid')
        if key in seen: continue
        seen.add(key)
        st = status(key) if q.get('kind')=='q' else 'MATERIAL'
        if os.environ.get('FREE') and not (st.startswith('FREE') or st=='MATERIAL'): continue
        a = ans.get(tag, {}).get(str(q.get('qno'))) or ans.get(pid, {}).get(str(q.get('qno')))
        print(f"### {key} [{st}] ans={(a or {}).get('ans')} rate={(a or {}).get('rate')} p={q['segs'][0][0]+1} img={len(q.get('images') or [])}")
        print('   ' + t[:mx])

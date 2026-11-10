"""show.py <tag> <qno> [--render] : print material text + all questions of that material (+ answers);
--render also renders material & question PNGs into r/ (170dpi or given)."""
import json, sys, os, re, unicodedata, subprocess
W = '/home/user/work'
SP = '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/zl2a'
tag, qno = sys.argv[1], int(sys.argv[2])
d = json.load(open(f'{W}/index/{tag}.json'))
q = next(x for x in d if x['kind'] == 'q' and x['qno'] == qno)
mid = q.get('material')
try:
    ans = json.load(open(f'{W}/answers/{tag}.json'))['answers']
except Exception:
    ans = {}
def norm(t): return unicodedata.normalize('NFKC', t)
if mid:
    m = next(x for x in d if x['kind'] == 'material' and x['mid'] == mid)
    print('=== MATERIAL', mid, 'segs', m['segs'], 'imgs', len(m.get('images', [])))
    print(norm(m['text']))
    qs = [x for x in d if x['kind'] == 'q' and x.get('material') == mid]
else:
    qs = [q]
for x in qs:
    a = ans.get(str(x['qno']), {})
    print(f"--- Q{x['qno']} segs={x['segs']} imgs={len(x.get('images', []))} ans={a.get('ans')} rate={a.get('rate')} yicuo={a.get('yicuo')}")
    print(norm(x['text']))
if '--render' in sys.argv:
    os.makedirs(f'{SP}/r', exist_ok=True)
    dpi = '200'
    if mid:
        print(subprocess.run(['python3', f'{W}/tools/render.py', 'm', tag, mid, f'{SP}/r'], capture_output=True, text=True).stdout)
    for x in qs:
        print(subprocess.run(['python3', f'{W}/tools/render.py', 'q', tag, str(x['qno']), f'{SP}/r', dpi], capture_output=True, text=True).stdout.strip())

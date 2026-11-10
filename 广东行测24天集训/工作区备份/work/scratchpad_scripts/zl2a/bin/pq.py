"""pq.py <tag> <qno> [dpi] : render the page(s) holding question qno and the page before (material usually above)."""
import json, sys, subprocess
W = '/home/user/work'; SP = '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/zl2a'
tag, qno = sys.argv[1], int(sys.argv[2]); dpi = sys.argv[3] if len(sys.argv) > 3 else '95'
d = json.load(open(f'{W}/index/{tag}.json'))
q = next(x for x in d if x['kind'] == 'q' and x['qno'] == qno)
pages = sorted({s[0] for s in q['segs']})
f = q['file']
want = sorted({max(0, pages[0] - 1)} | set(pages)) if '--prev' in sys.argv else pages
for p in want:
    print(subprocess.run(['python3', f'{SP}/bin/page.py', f, str(p + 1), dpi], capture_output=True, text=True).stdout.strip())

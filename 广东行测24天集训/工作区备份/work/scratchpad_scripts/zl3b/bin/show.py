"""Print a survey block's material text + its questions. usage: show.py TAG START"""
import json, sys, re, unicodedata
SP = '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/zl3b'
rows = json.load(open(f'{SP}/survey.json'))
tag, start = sys.argv[1], int(sys.argv[2])
end = int(sys.argv[3]) if len(sys.argv) > 3 else None
r = [x for x in rows if x['tag'] == tag and x['start'] == start][0]
e = end or r['end']
print('FILE', r['file'], 'REG', r['reg'])
print('TAKEN', r['taken'])
print('---- MATERIAL ----')
print(unicodedata.normalize('NFKC', r['text']))
d = json.load(open(f'/home/user/work/index/{tag}.json'))
try:
    a = json.load(open(f'/home/user/work/answers/{tag}.json'))['answers']
except Exception:
    a = {}
print('---- QUESTIONS ----')
for x in d:
    if x['kind'] == 'q' and start <= x['qno'] <= e:
        t = unicodedata.normalize('NFKC', x['text'])
        print(f"[{x['qno']}] ans={a.get(str(x['qno']), {}).get('ans')} segs={x['segs']} imgs={x.get('images')}")
        print(t[:900])
        print()

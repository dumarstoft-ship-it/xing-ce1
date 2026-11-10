import json, re, unicodedata, glob, os, sys
def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s_（）()　,，。.、；;：:“”"‘’\'！!？?—…\-]', '', s)
def grams(s, n=8): return {s[i:i+n] for i in range(len(s)-n+1)}
ALL = []
for f in sorted(glob.glob('/home/user/work/index/*.json')):
    tag = os.path.basename(f)[:-5]
    for q in json.load(open(f)):
        if q.get('kind') == 'q':
            ALL.append((tag, q['qno'], q.get('section'), grams(norm(q.get('text') or ''), 8)))
print('index questions', len(ALL))
mine = json.load(open(sys.argv[1]))
for k, t in mine.items():
    g = grams(norm(t), 8)
    hits = sorted(((len(g & gg), tag, qno, sec) for tag, qno, sec, gg in ALL if len(g & gg) >= 2), reverse=True)
    print(k, len(g), hits[:10])

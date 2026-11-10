import sys, json, re, unicodedata, os
sys.path.insert(0, os.path.dirname(__file__))
from sel import SEL
W = '/home/user/work'
JUNK = re.compile(r'(·\s*本试卷由粉笔用户.*?生成|\d{4}年[^\n]*?网友回忆版\)|【认准淘宝店铺[^】]*】[^\n]*|淘宝:[^\n]*|TB:Seeyee[^\n]*|获取试卷更新[^\n]*|免费获取更多考公资料[^\n]*|第\s*\d+\s*页\s*,?\s*共\s*\d+\s*页|^\s*-\s*\d+\s*-\s*$)', re.M)
def parse(text, qno):
    t = unicodedata.normalize('NFKC', text)
    t = JUNK.sub('', t)
    t = re.sub(r'^\s*' + str(qno) + r'\s*[\.、．]?\s*', '', t.strip())
    t = re.sub(r'\(单选题\)', '', t)
    # split options
    m = re.split(r'(?:(?<=\s)|^|(?<=[。?？:：\)）]))([ABCD])\s*[\.、．]\s*', t)
    stem = m[0]; opts = {}
    for i in range(1, len(m) - 1, 2):
        opts[m[i]] = re.sub(r'\s+', ' ', m[i + 1]).strip()
    stem = re.sub(r'\s*\n\s*', '', stem).strip()
    return stem, opts
out = {}
for g, mats in SEL.items():
    for mid, tag, qs in mats:
        d = json.load(open(f'{W}/index/{tag}.json'))
        for q in qs:
            x = next(y for y in d if y['kind'] == 'q' and y['qno'] == q)
            stem, opts = parse(x['text'], q)
            out[f'{tag}-{q}'] = dict(stem=stem, options=opts, nimg=len(x.get('images', [])), segs=x['segs'], file=x['file'])
            flag = '' if sorted(opts) == ['A', 'B', 'C', 'D'] and all(opts.values()) else '  <<< CHECK'
            print(f'{tag}-{q}: {stem}{flag}')
            for k in sorted(opts): print(f'      {k}: {opts[k]}')
json.dump(out, open('/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/zl2a/v/stems.json', 'w'), ensure_ascii=False, indent=1)

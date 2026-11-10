import pool, re, json, os, sys
def tag_of(pid):
    return pid if os.path.exists(f'/home/user/work/index/{pid}.json') else pid + '_xc'
JUNK = [r'2016 年江苏省公务员录用考试《行测》真题A', r'2018 年江苏省公务员录用考试《行测》真题A', r'· 本试卷由粉笔用户用户\w+生成', r'2026年浙江省公务员录用考试《行测》题\(A类\)\(网友回忆版\)',
        r'获取试卷更新[^\n]*', r'第\s*\d+\s*页\s*共\s*\d+\s*页', r'^\s*-\s*\d+\s*-\s*$']
def clean(t):
    for j in JUNK: t = re.sub(j, '', t, flags=re.M)
    return t
def split(text):
    t = clean(text)
    t = re.sub(r'^\s*\d+\s*[、\.．]?\s*', '', t, count=1)   # leading qno
    # options
    m = re.search(r'(?:^|\n|\s)A\s*[、\.．]', t)
    stem = t[:m.start()] if m else t
    rest = t[m.start():] if m else ''
    parts = re.split(r'(?:^|\n|\s)([A-D])\s*[、\.．]', rest)
    opts = {}
    for i in range(1, len(parts) - 1, 2):
        opts[parts[i]] = re.sub(r'\s+', '', parts[i + 1])
    return stem, opts
def get(key):
    pid, q = key.rsplit('-', 1); q = int(q)
    tag = tag_of(pid); x = pool.qtext(tag, q)
    stem, opts = split(x['text'])
    return dict(key=key, tag=tag, page=x['segs'][0][0] + 1, file=x['file'], stem=stem, options=opts, material=x.get('material'), images=x.get('images'))
if __name__ == '__main__':
    for k in sys.argv[1:]:
        d = get(k)
        print('=====', k, d['tag'], 'page', d['page'], d['file'])
        print('STEM:', d['stem'])
        for o, v in d['options'].items(): print(f'  {o}: {v}')

import json, re, sys, unicodedata, difflib
sys.path.insert(0, 'tools')
from rawq import raw
import pymupdf
rows = [json.loads(l) for l in open('/home/user/work/out2/PD2C/questions.jsonl')]
def norm(s):
    s = unicodedata.normalize('NFKC', s)
    s = re.sub(r'[\s　]', '', s)
    s = re.sub(r'^\d+[、.．]', '', s)
    s = s.replace('(', '').replace(')', '').replace('“', '"').replace('”', '"')
    s = re.sub(r'(?<![A-Za-z])([A-D])[、.．]', '', s)     # option labels
    s = re.sub(r'(?:\d{1,3}[.、])(?=[A-D一-龥])', '', s)  # stray question numbers like "106."
    s = s.replace(';', '').replace(':', '').replace(',', '').replace('。', '').replace('?', '').replace('，', '').replace('；', '').replace('：', '')
    return s
def gk2021d_page():
    d = pymupdf.open('/home/user/xing-ce1/国考/真题/2021年国家公务员考试《行测》真题（市地级）.pdf')
    pg = d[13]; return pg.get_text('text', clip=pymupdf.Rect(0, 500, pg.rect.width, 842))
tagfix = {'GK2024F-115': 'GK2024F_xc', 'GD2022X-84': 'GD2022X_xc'}
for r in rows:
    if r['variant_of']: continue
    key = r['source_key']; paper, qno = key.rsplit('-', 1); qno = int(qno)
    tag = tagfix.get(key) or (paper + ('_xc' if r['source']['file'].startswith('xingce/') else ''))
    mine = norm(r['stem'] + ''.join(r['options'].values()))
    if paper == 'GK2021D':
        t = gk2021d_page()
        # keep shared stem + this question block
        stem_part = t[t.index('某单位'): t.index('106')]
        m = re.search(rf'{qno}、(.*?)(?=\n{qno+1}、|第五部分)', t, re.S)
        src = norm(stem_part + m.group(1))
    else:
        f, pages, t = raw(tag, qno)
        t = re.sub(r'材料\n.*', '', t, flags=re.S) if key == 'SC2023-85' else t
        src = norm(t)
    sm = difflib.SequenceMatcher(None, src, mine, autojunk=False)
    diffs = [(op, src[a:b], mine[c:d]) for op, a, b, c, d in sm.get_opcodes() if op != 'equal']
    ratio = sm.ratio()
    print(f"{r['id']} {key:16s} ratio={ratio:.3f} diffs={diffs[:8]}")

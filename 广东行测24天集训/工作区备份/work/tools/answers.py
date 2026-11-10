"""Extract per-question reference answers (and 正确率/易错项 if present) from 解析 PDFs with text layers."""
import pymupdf, re, json, os, sys, unicodedata
pymupdf.TOOLS.mupdf_display_errors(False)
sys.path.insert(0, os.path.dirname(__file__))
from papers import registry, ROOT

QMARK = re.compile(r'(?:^|\n)\s*(?:第\s*(\d{1,3})\s*题|【\s*(?:解析\s*)?(\d{1,3})\s*(?:[—\-－]|】)|题目\s*(\d{1,3})|(\d{1,3})\s*[、\.．](?!\d)|(\d{1,3})[ \t]*\n(?!\s*\d))')
ANS = re.compile(r'(?:正确答案(?:是|为)?|参考答案(?:是|为)?|【答案】|答案(?:是|为)?)\s*[:：]?\s*[【\[]?\s*([A-H](?:\s*[、,，]?\s*[A-H]){0,7}|正确|错误|对|错|√|×)\s*[】\]]?')
ANS2 = re.compile(r'(?:故(?:本题)?(?:正确答案|答案)?(?:为|选|是)|因此[,，]?\s*选择|答案锁定)\s*[:：]?\s*[【\[]?([A-H]{1,8}|正确|错误)')
RATE = re.compile(r'正确率\s*[:：]?\s*(\d{1,3})\s*%')
YCX = re.compile(r'易错项\s*[:：]?\s*([A-H])')

def extract(path):
    doc = pymupdf.open(path)
    t = unicodedata.normalize('NFKC', '\n'.join(p.get_text() for p in doc))
    t = re.sub(r'[ \t]+', ' ', t)
    marks = []
    for m in QMARK.finditer(t):
        n = int(next(g for g in m.groups() if g))
        marks.append((m.start(), n))
    # keep increasing sequence (greedy, allow small gaps)
    seq, last = [], 0
    for pos, n in marks:
        if last < n <= last + 3:
            seq.append((pos, n)); last = n
    res = {}
    for i, (pos, n) in enumerate(seq):
        end = seq[i + 1][0] if i + 1 < len(seq) else len(t)
        seg = t[pos:end]
        a = ANS.search(seg) or ANS2.search(seg)
        ans = None
        if a:
            ans = re.sub(r'[\s、,，]', '', a.group(1))
            ans = {'对': '正确', '√': '正确', '错': '错误', '×': '错误'}.get(ans, ans)
        r = RATE.search(seg); y = YCX.search(seg)
        res[n] = dict(ans=ans, rate=int(r.group(1)) if r else None, yicuo=y.group(1) if y else None, chars=len(seg))
    return res

if __name__ == '__main__':
    reg = registry()
    os.makedirs('/home/user/work/answers', exist_ok=True)
    only = sys.argv[1:]
    for r in reg:
        if r['kind'] != 'ans' or r['text'] < 3000 or not r['pid']: continue
        if r['year'] and r['year'] < 2013: continue
        if only and r['pid'] not in only: continue
        tag = r['pid'] + ('' if r['path'].startswith('xing-ce1') else '_xc')
        res = extract(os.path.join(ROOT, r['path']))
        got = sum(1 for v in res.values() if v['ans'])
        mx = max(res) if res else 0
        rates = sum(1 for v in res.values() if v['rate'] is not None)
        json.dump(dict(file=r['path'], answers=res), open(f'/home/user/work/answers/{tag}.json', 'w'), ensure_ascii=False)
        miss = [n for n in range(1, mx + 1) if n not in res or not res[n]['ans']]
        print(f"{tag:14} max={mx:3} got={got:3} rates={rates:3} miss={miss[:15]}{'...' if len(miss)>15 else ''}")

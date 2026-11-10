"""getans.py <tag> <q0> <q1> [maxchars]: per question, cut the analysis text from 'q、' to the next question marker,
save to v/ans/<tag>_<q>.txt (first line = file, second = page), print page + answer sentence + head of reasoning."""
import sys, re, json, unicodedata, pymupdf, os
pymupdf.TOOLS.mupdf_display_errors(False)
SP = '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/zl3a'
EXTRA = {}
tag, q0, q1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
mx = int(sys.argv[4]) if len(sys.argv) > 4 else 260
f = EXTRA.get(tag) or json.load(open(f'/home/user/work/answers/{tag}.json'))['file']
doc = pymupdf.open('/home/user/' + f)
pages = [unicodedata.normalize('NFKC', pg.get_text()) for pg in doc]
full = ''; starts = []
for t in pages:
    starts.append(len(full)); full += t + '\n'
def pos(q, after=0):
    pat = re.compile(r'(?:(?<=\n)|^)\s*(?:【\s*)?(?:第\s*)?' + str(q) + r'(?:\s*题)?\s*(?:[\.、．:：】]|\s)|【解析' + str(q) + r'—|【题目' + str(q) + r'】|第【' + str(q) + r'】题')
    for m in pat.finditer(full):
        if m.start() >= after: return m.start()
    return None
last = 0
for q in range(q0, q1 + 1):
    a = pos(q, last)
    if a is None:
        print(q, 'NOT FOUND'); continue
    b = pos(q + 1, a + 5) or len(full)
    if b - a > 6000: b = a + 6000
    seg = full[a:b]
    pg = max(i for i, s in enumerate(starts) if s <= a) + 1
    open(f'{SP}/v/ans/{tag}_{q}.txt', 'w').write(f'{f}\npage {pg}\n{seg}')
    ans = re.findall(r'(?:正确答案|答案)\s*(?:为|是|:|：)?\s*([A-D])|故(?:本题)?选\s*([A-D])|因此[,，]?选择?\s*([A-D])', seg)
    ans = [x for t in ans for x in t if x]
    rate = re.search(r'正确率\s*[:：]?\s*(\d+)\s*%', seg); yc = re.search(r'易错项\s*[:：]?\s*([A-D])', seg)
    head = re.sub(r'\s+', ' ', seg)[:mx]
    print(f'{q} p{pg} ans={ans} rate={rate.group(1) if rate else None} yicuo={yc.group(1) if yc else None} | {head}')
    last = a + 3

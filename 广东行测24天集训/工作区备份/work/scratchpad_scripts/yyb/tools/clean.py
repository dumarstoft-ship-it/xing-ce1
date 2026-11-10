import re, sys, json
sys.path.insert(0, '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/yyb/tools')
from qx import get, raw, crop
JUNK = [r'·\s*本试卷由粉笔用户[^\n]*', r'\d{4}年广东省公务员录用考试《行测》题[（(]网友回忆版[)）]', r'【通关达人资料库】[^\n]*',
        r'第\s*\d+\s*页[，,]?\s*共\s*\d+\s*页', r'(?m)^\s*-\s*\d+\s*-\s*$', r'(?m)^\s*\d{1,3}\s*$', r'【认准淘宝店铺[^】]*】[^\n]*', r'(?m)^\s*\d{1,3}\.\s*$']
PROMPT = re.compile(r'(这段文字|这段话|上述文段|以上文段|该段文字|上述文字|本段文字|对这段|对上述|对于这段|根据|通过|作者|下列选项|以下|与这段|由上述|如果这是|因此，个人|最能概括|这段文字理解)')
def clean(t):
    for j in JUNK: t = re.sub(j, '', t)
    t = t.replace('　', ' ')
    t = re.sub(r'^\s*\d{1,3}\s*[、\.．]\s*', '', t.strip())
    # split options
    m = re.search(r'(?:^|\n|\s)A\s*[、\.．]?\s*(?=\S)', t)
    # find option positions
    pos = []
    for L in 'ABCD':
        mm = list(re.finditer(r'(?:(?<=\n)|(?<=\s)|(?<=^))' + L + r'\s*[、\.．]?\s*(?=[^\s、\.．])', t))
        pos.append(mm)
    # choose increasing sequence: last A before B ... simple: take the first A after which B,C,D appear in order
    best = None
    for a in pos[0]:
        b = next((x for x in pos[1] if x.start() > a.start()), None)
        if not b: continue
        c = next((x for x in pos[2] if x.start() > b.start()), None)
        if not c: continue
        d = next((x for x in pos[3] if x.start() > c.start()), None)
        if not d: continue
        best = (a, b, c, d)
    if not best: return t, None
    a, b, c, d = best
    body = t[:a.start()]
    opts = {'A': t[a.end():b.start()], 'B': t[b.end():c.start()], 'C': t[c.end():d.start()], 'D': t[d.end():]}
    def j(s):
        s = re.sub(r'\s*\n\s*', '', s.strip())
        s = re.sub(r'[ \t]{2,}', ' ', s)
        return s.strip()
    opts = {k: j(v) for k, v in opts.items()}
    lines = [l.strip() for l in body.strip().split('\n') if l.strip()]
    # prompt = last line(s) starting with PROMPT keyword
    k = len(lines)
    for i in range(len(lines) - 1, -1, -1):
        if PROMPT.match(lines[i]) and (lines[i].endswith(('：', ':', '）', ')', '（ ）', '()')) or '是' in lines[i][-6:] or '（' in lines[i]):
            k = i; break
    passage = ''.join(lines[:k]); prompt = ''.join(lines[k:])
    passage = re.sub(r'[ \t]{2,}', ' ', passage)
    return (passage + ('\n' + prompt if prompt else '')), opts
if __name__ == '__main__':
    for key in sys.argv[1:]:
        tag, q = key.rsplit('-', 1)
        qq = get(tag, int(q))
        stem, opts = clean(raw(qq))
        print('=====', key); print(stem); print(json.dumps(opts, ensure_ascii=False))

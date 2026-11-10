import re, sys, os, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qx import get, raw
import clean2
from clean2 import norm_text, find_opts, j, PROMPT, CIRC
RADICAL = re.compile(r'[⺀-⻿⼀-⿟]')
SUPP = {'⻚':'页','⻔':'门','⻓':'长','⻛':'风','⻜':'飞','⻢':'马','⻋':'车','⻅':'见','⻆':'角','⻉':'贝','⻰':'龙','⻨':'麦','⻥':'鱼','⻦':'鸟','⻓':'长','⻩':'黄','⻬':'齐','⻮':'齿','⻘':'青','⻝':'食','⻄':'西','⻅':'见','⻓':'长','⻊':'足','⻣':'骨','⻤':'鬼','⻢':'马','⻁':'虎','⻌':'辶','⻏':'阝','⻖':'阝'}
def fix_radicals(s):
    """Kangxi/CJK-radical code points used by some PDF fonts for ordinary characters -> standard CJK. Returns (text, changed_chars)."""
    ch = sorted(set(RADICAL.findall(s)))
    if not ch: return s, []
    def rep(m):
        c = m.group(0)
        if c in SUPP: return SUPP[c]
        n = unicodedata.normalize('NFKC', c)
        return n
    return RADICAL.sub(rep, s), ch
EXTRA_JUNK = [r'·?\s*本试卷由粉笔用户\S*?生成', r'免费获取更多考公资料[^\n]*', r'添加微信\S*',
              r'20\d\d年国家公务员录用考试《行测》题[（(][^\n]*?[)）]', r'第\s*\d+\s*页[，,]\s*共\s*\d+\s*页',
              r'四、推理判断。[^\n]*', r'\d{4}年[^\n]{0,12}(浙江|江苏|山东|四川|河北)[^\n]{0,20}《行测》[^\n]*']
def dejunk3(t):
    t, ch = fix_radicals(t)
    for p in EXTRA_JUNK: t = re.sub(p, '', t)
    return clean2.dejunk(t), ch
def clean_pd3(r):
    t, ch = dejunk3(r)
    t = re.sub(r'^\s*\d{1,3}\s*[、\.．]?\s*', '', t.strip())
    a, b, c, d = find_opts(t)
    body = t[:a.start()]
    opts = {'A': j(t[a.end():b.start()]), 'B': j(t[b.end():c.start()]), 'C': j(t[c.end():d.start()]), 'D': j(t[d.end():])}
    lines = [l.strip() for l in body.strip().split('\n') if l.strip()]
    k = None
    for i in range(len(lines) - 1, -1, -1):
        if PROMPT.match(lines[i]): k = i; break
    if k is None: k = len(lines) - 1
    passage = ''.join(lines[:k]); prompt = ''.join(lines[k:])
    return norm_text(passage), norm_text(prompt), opts, ch
def clean_px3(r):
    t, ch = dejunk3(r)
    t = re.sub(r'^\s*\d{1,3}\s*[、\.．]?\s*(?=[①-⑧])', '', t.strip())
    t = re.sub(r'^\s*\d{1,3}\s*[、\.．]\s*', '', t)
    om = list(re.finditer(r'([A-D])\s*[\.．、]\s*([①-⑧](?:\s*[-－—]?\s*[①-⑧]){3,7})', t))
    opts = {m.group(1): re.sub(r'\s+', '', m.group(2)) for m in om}
    body = t[:om[0].start()]
    pm = re.search(r'((?:将以上|将上述|把以上)[^\n]*?(?:是|为)[^\n]*)', body)
    prompt = re.sub(r'\s+', '', pm.group(1)) if pm else ''
    lead = body[:body.find('①')]
    body2 = body.replace(pm.group(1), '') if pm else body
    chunks = [c for c in re.split(r'(?=[①-⑧])', body2) if c.strip() and c.strip()[0] in CIRC]
    sents = [norm_text(re.sub(r'\s+', '', c)) for c in chunks]
    return sents, norm_text(prompt), norm_text(re.sub(r'\s+', '', lead)), opts, ch
if __name__ == '__main__':
    import json
    for key in sys.argv[1:]:
        tag, q = key.rsplit('-', 1); r = raw(get(tag, int(q)))
        print('=====', key)
        if re.search(r'重新排|排序', r) and not key.startswith('GK2020D-55'):
            s, p, lead, o, ch = clean_px3(r); print('LEAD:', lead, 'RAD:', ch); print('\n'.join(s)); print(p); print(o)
        else:
            ps, pr, o, ch = clean_pd3(r); print(ps); print(pr, 'RAD:', ch); print(json.dumps(o, ensure_ascii=False))

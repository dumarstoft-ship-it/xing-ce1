"""Parse question text from index into stem + options (same approach as ZL2A build)."""
import json, re, unicodedata
W = '/home/user/work'
CJK = r'　-〿一-鿿＀-￯“”‘’（）《》【】'
def despace(s):
    s = re.sub(r'(?<=[%s])[ \t]+' % CJK, '', s)
    s = re.sub(r'[ \t]+(?=[%s])' % CJK, '', s)
    s = re.sub(r'(?<=\d)[ \t]+(?=[%s])' % CJK, '', s)
    s = re.sub(r'(?<=[%s])[ \t]+(?=\d)' % CJK, '', s)
    return re.sub(r'\s+', ' ', s).strip()
JUNK = re.compile(r'(·\s*本试卷由粉笔用户.*?生成|\d{4}年[^\n]*?网友回忆版\)|【认准淘宝店铺[^】]*】[^\n]*|淘宝:[^\n]*|TB:Seeyee[^\n]*|获取试卷更新[^\n]*|免费获取更多考公资料[^\n]*|第\s*\d+\s*页\s*,?\s*共\s*\d+\s*页|第\d+⻚,共\d+⻚|^\s*-\s*\d+\s*-\s*$|\(材料\d\).*$|（材料\d）.*$)', re.M | re.S)
def parse(text, qno):
    t = unicodedata.normalize('NFKC', text)
    t = JUNK.sub('', t)
    t = re.sub(r'^\s*' + str(qno) + r'\s*[\.、．]?\s*', '', t.strip())
    t = re.sub(r'\(单选题\)', '', t)
    m = re.split(r'(?:(?<=\s)|^|(?<=[。?？:：\)）]))([ABCD])\s*[\.、．]\s*', t)
    stem = despace(re.sub(r'\s*\n\s*', '', m[0])); opts = {}
    for i in range(1, len(m) - 1, 2):
        opts[m[i]] = despace(m[i + 1])
    return stem, opts
_cache = {}
def qrec(tag, qno):
    if tag not in _cache:
        _cache[tag] = {x['qno']: x for x in json.load(open(f'{W}/index/{tag}.json')) if x['kind'] == 'q'}
    return _cache[tag][qno]

import re, json
def clean(t):
    t = t.replace('　', ' ')
    t = re.sub(r'·?\s*本试卷由粉笔用户[^\n]*?生成', '', t)
    t = re.sub(r'2026年广东省公务员录用考试《行测》题\(网友回忆版\)', '', t)
    t = re.sub(r'\n', '', t)
    t = re.sub(r'[ \t]+', ' ', t).strip()
    return t
def parse(text, qno):
    t = clean(text)
    t = re.sub(r'^\s*%d\s*[、\.．]?\s*(\(单选题\))?\s*' % qno, '', t)
    # find option markers
    best = None
    for ma in re.finditer(r'A\s*[\.．、]', t):
        rest = t[ma.end():]
        mb = re.search(r'B\s*[\.．、]', rest)
        if not mb: continue
        r2 = rest[mb.end():]; mc = re.search(r'C\s*[\.．、]', r2)
        if not mc: continue
        r3 = r2[mc.end():]; md = re.search(r'D\s*[\.．、]', r3)
        if not md: continue
        best = (ma, mb, mc, md)
    if not best: return t, None
    ma, mb, mc, md = best
    stem = t[:ma.start()].strip()
    rest = t[ma.end():]
    A = rest[:mb.start()].strip(); r2 = rest[mb.end():]
    B = r2[:mc.start()].strip(); r3 = r2[mc.end():]
    C = r3[:md.start()].strip(); D = r3[md.end():].strip()
    return stem, {'A': A, 'B': B, 'C': C, 'D': D}

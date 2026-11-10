"""Segment exam PDFs (text layer) into questions with page regions.
Output: /home/user/work/index/{pid}.json  — list of questions:
  {pid, qno, section, sec_title, material_id, segs:[[page,y0,y1],...], text, images:[[page,bbox]...]}
Materials (资料 / 文章阅读) are separate entries with kind='material'.
"""
import pymupdf, re, json, os, sys, unicodedata
pymupdf.TOOLS.mupdf_display_errors(False)
sys.path.insert(0, os.path.dirname(__file__))
from papers import registry, ROOT

WATERMARK = re.compile(r'(认准淘宝|淘宝店铺|淘宝：|通关达人|罗老师|资料铺子|一站式备考|微信|公众号|QQ群|更多资料)')
PAGENUM = re.compile(r'(^第\s*\d+\s*页|^-\s*\d+\s*-$|^\d+\s*/\s*\d+$|^共\s*\d+\s*页|^\d{1,3}$|^第\s*\d+\s*页\s*共)')
NOISE = re.compile(r'(认准淘宝|淘宝店铺|淘宝：|通关达人|罗老师|资料铺子|一站式备考|^第\s*\d+\s*页|^-\s*\d+\s*-$|^\d+\s*/\s*\d+$|^共\s*\d+\s*页|微信|公众号|QQ群|更多资料|^\d{1,3}$)')
SEC_KEYS = [('政治理论', '政治'), ('常识', '常识'), ('言语', '言语'), ('数量', '数量'), ('数字推理', '数量'), ('数学运算', '数量'),
            ('判断推理', '判断'), ('图形推理', '判断'), ('定义判断', '判断'), ('类比推理', '判断'), ('逻辑判断', '判断'), ('演绎推理', '判断'),
            ('科学推理', '科学'), ('资料分析', '资料'), ('思维', '判断')]
SEC_HDR = re.compile(r'^\s*(第[一二三四五六七八九十]+部分|[一二三四五六七八九十]+\s*[\.、．]|[（(][一二三四五六七八九十]+[)）]|(?=(常识判断|言语理解|数量关系|判断推理|资料分析|科学推理|政治理论)))\s*([^\d]{0,40})')
MAT_HDR = re.compile(r'(根据|阅读).{0,30}(资料|材料|文字|图|表|文章|短文).{0,25}(回答|完成|作答|解答)|^\s*[（(][一二三四五六七八九十]{1,3}[)）]\s*$|^\s*[（(][一二三四五六七八九十]{1,3}[)）]\s*\S|^\s*(资料|材料)[一二三四五六七八九十]')
NUM_ALONE = re.compile(r'^\s*(\d{1,3})\s*[\.．、]?\s*$')
NUM_INLINE = re.compile(r'^[\s　]*(\d{1,3})\s*[\.．、](?!\d)\s*(\S.*)$')
NUM_LOOSE = re.compile(r'^[\s\u3000]*(\d{1,3})\s*[\.．、]\s*\d')

def page_lines(page):
    d = page.get_text('dict')
    H = page.rect.height
    lines, imgs = [], []
    for b in d['blocks']:
        if b['type'] == 1:
            x0, y0, x1, y1 = b['bbox']
            if (x1 - x0) > 0.9 * page.rect.width and (y1 - y0) > 0.6 * H: continue  # full-page background
            if (x1-x0) < 3 or (y1-y0) < 3: continue
            imgs.append([round(v, 1) for v in b['bbox']])
            continue
        for l in b['lines']:
            t = unicodedata.normalize('NFKC', ''.join(s['text'] for s in l['spans'])).replace('\u3000', '  ')
            if not t.strip(): continue
            x0, y0, x1, y1 = l['bbox']
            ts = t.strip()
            if WATERMARK.search(ts): continue
            if PAGENUM.search(ts) and (y0 < 60 or y0 > H - 70): continue
            lines.append(dict(x0=x0, y0=y0, x1=x1, y1=y1, t=t))
    # images drawn as vector? also collect drawings bbox quickly (skip)
    lines.sort(key=lambda l: (round(l['y0'] / 3), l['x0']))
    return lines, imgs

def section_of(t):
    for k, v in SEC_KEYS:
        if k in t: return v
    return None

def segment(path, pid):
    doc = pymupdf.open(path)
    allL = []
    for pno, page in enumerate(doc):
        L, imgs = page_lines(page)
        for l in L: l['p'] = pno
        allL.append((L, imgs))
    # left margin estimate: most common x0 of lines
    from collections import Counter
    xs = Counter(round(l['x0']) for L, _ in allL for l in L)
    margin = xs.most_common(1)[0][0] if xs else 40
    starts = []  # (p, y, qno, kind, line_idx)
    last = 0
    section, sec_title = None, ''
    events = []
    for pno, (L, imgs) in enumerate(allL):
        for i, l in enumerate(L):
            t = l['t'].strip()
            m = SEC_HDR.match(t)
            if m and len(t) < 120:
                s = section_of(t)
                if s:
                    events.append(dict(kind='section', p=pno, y=l['y0'], sec=s, title=t[:60]))
                    continue
            if MAT_HDR.search(t) and len(t) < 200 and (section in ('资料', None) or '资料' in t or '材料' in t or '回答' in t):
                events.append(dict(kind='mathdr', p=pno, y=l['y0'], title=t[:80]))
            m1 = NUM_ALONE.match(t)
            m2 = NUM_INLINE.match(l['t'])
            n = None
            m3 = NUM_LOOSE.match(l['t'])
            strict = True
            if m1 and l['x0'] < margin + 4:
                n = int(m1.group(1))
            elif m2 and l['x0'] < margin + 25:
                n = int(m2.group(1))
            elif m3 and l['x0'] < margin + 25:
                n = int(m3.group(1)); strict = False
            if n is not None and ((strict and last < n <= last + 6) or (not strict and n == last + 1)):
                # guard: inline numbers in 资料 text like "1．" lists are below last; years filtered by (?!\d)
                events.append(dict(kind='q', p=pno, y=l['y0'], qno=n, inline=bool(m2 and not m1)))
                last = n
            elif m1 and section_of(t) is None and n is None:
                pass
            if m and not section_of(t):
                pass
    # assign sections & build regions
    events.sort(key=lambda e: (e['p'], e['y'], 0 if e['kind'] == 'section' else (1 if e['kind'] == 'mathdr' else 2)))
    out = []
    cur_sec, cur_title = None, ''
    mat_count = 0
    cur_mat = None
    pages_h = [doc[i].rect.height for i in range(len(doc))]
    boundaries = [e for e in events if e['kind'] in ('q', 'mathdr', 'section')]
    for idx, e in enumerate(boundaries):
        if e['kind'] == 'section':
            cur_sec, cur_title = e['sec'], e['title']
            if cur_sec != '资料': cur_mat = None
            continue
        nxt = boundaries[idx + 1] if idx + 1 < len(boundaries) else None
        # region from (e.p, e.y) to (nxt.p, nxt.y)
        segs = []
        p0, y0 = e['p'], e['y'] - 2
        if nxt is None:
            p1, y1 = len(doc) - 1, pages_h[-1] - 40
        else:
            p1, y1 = nxt['p'], nxt['y'] - 2
        for p in range(p0, p1 + 1):
            ya = y0 if p == p0 else 0
            yb = y1 if p == p1 else pages_h[p]
            if yb - ya > 4: segs.append([p, round(ya, 1), round(yb, 1)])
        # text and images in region
        txt, ims = [], []
        for (p, ya, yb) in segs:
            L, imgs = allL[p]
            for l in L:
                if ya - 1 <= l['y0'] < yb: txt.append(l['t'])
            for bb in imgs:
                if bb[1] < yb and bb[3] > ya: ims.append([p, bb])
        text = '\n'.join(txt)
        if e['kind'] == 'mathdr':
            if cur_sec in ('资料', None) or True:
                mat_count += 1
                cur_mat = f"{pid}-M{mat_count}"
                out.append(dict(kind='material', pid=pid, mid=cur_mat, section=cur_sec, title=e['title'], segs=segs, text=text, images=ims))
            continue
        q = dict(kind='q', pid=pid, qno=e['qno'], section=cur_sec, sec_title=cur_title, material=cur_mat if cur_sec == '资料' else None,
                 segs=segs, text=text, images=ims)
        out.append(q)
    return out

if __name__ == '__main__':
    reg = registry()
    os.makedirs('/home/user/work/index', exist_ok=True)
    only = sys.argv[1:] 
    summary = []
    for r in reg:
        if r['kind'] != 'q' or not r['path'].endswith('.pdf') or r['text'] < 3000 or not r['pid']: continue
        if r['year'] and r['year'] < 2013: continue
        if only and r['pid'] not in only: continue
        tag = r['pid'] + ('' if r['path'].startswith('xing-ce1') else '_xc')
        try:
            qs = segment(os.path.join(ROOT, r['path']), tag)
        except Exception as ex:
            print('ERR', tag, ex); continue
        for q in qs: q['file'] = r['path']
        json.dump(qs, open(f'/home/user/work/index/{tag}.json', 'w'), ensure_ascii=False)
        nq = [q for q in qs if q['kind'] == 'q']
        nums = [q['qno'] for q in nq]
        secs = {}
        for q in nq: secs[q['section']] = secs.get(q['section'], 0) + 1
        missing = sorted(set(range(1, max(nums) + 1)) - set(nums)) if nums else []
        nm = sum(1 for q in qs if q['kind'] == 'material')
        print(f"{tag:14} q={len(nq):3} max={max(nums) if nums else 0:3} miss={missing[:12]} mats={nm} secs={secs}")

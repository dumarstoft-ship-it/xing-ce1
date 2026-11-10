"""Export 数量关系 source text (stem, options, source answer, source analysis) per paper for GPT.
Writes Markdown per paper + one JSONL into OUT. No rewriting, no re-solving."""
import json, os, re, sys, unicodedata, bisect, pymupdf
from collections import OrderedDict
pymupdf.TOOLS.mupdf_display_errors(False)
sys.path.insert(0, os.path.dirname(__file__))
from answers import QMARK, ANS, ANS2
OUT = sys.argv[1] if len(sys.argv) > 1 else '/home/user/work/quant/out'
IMG = os.path.join(OUT, 'img')
os.makedirs(IMG, exist_ok=True)
IDX = '/home/user/work/index'; ANSD = '/home/user/work/answers'
WM = re.compile(r'(本试卷由|粉笔用户|认准淘宝|淘宝店铺|淘宝：|淘宝:|通关达人|罗老师|资料铺子|一站式备考|持续更新|^\s*\d+\s*/\s*\d+\s*$|^\s*-\s*\d+\s*-\s*$|^\s*第\s*\d+\s*页.*共\s*\d+\s*页\s*$)')

# explicit 数量 ranges where auto section labels are unreliable
RANGES = {'GD2017': (16, 30), 'GD2018': (16, 30), 'GD2019X': (16, 30), 'GD2019Z': (11, 25), 'GD2020X': (26, 40),
          'GD2020Z': (31, 45), 'GD2021Z': (31, 45), 'GD2022X': (26, 40), 'GD2022X_xc': (26, 40), 'GD2022Z': (31, 45),
          'GD2023X': (26, 40), 'GD2023X_xc': (26, 40), 'GD2023Z': (31, 45), 'GD2024': (31, 45), 'GD2024_xc': (31, 45),
          'GD2025': (31, 45), 'GD2025_xc': (31, 45), 'GD2026': (31, 45)}
LABEL = {'GD': '广东省考', 'GK': '国考', 'ZJ': '浙江省考', 'JS': '江苏省考', 'SD': '山东省考', 'SC': '四川省考', 'HB': '河北省考', 'SZ': '深圳市考'}
VAR = {'X': '县级', 'Z': '乡镇', 'F': '副省级', 'D': '地市级', 'A': 'A类', 'B': 'B卷', 'S': '上半年', 'H': '下半年', 'SW': '思维能力测验', '1': '行测1', '2': '行测2'}
OPT = re.compile(r'(?:(?<=\n)|(?<=\s\s)|(?<=^)|(?<=　))\s*([A-D])\s*[\.．、]')

def clean_lines(t):
    return '\n'.join(l for l in t.split('\n') if not WM.search(l.strip()))

def fix_letter_layout(t):
    # layout where option letter is a separate span placed after its text: '\n   .3.6\nB\n' -> '\nB.3.6\n'
    return re.sub(r'\n[ \t]*\.([^\n]*)\n[ \t]*([B-D])[ \t]*(?=\n|$)', lambda m: '\n' + m.group(2) + '.' + m.group(1).strip(), t)

def split_options(text):
    text = fix_letter_layout(text)
    body = re.sub(r'^\s*\d{1,3}\s*[\.．、]\s*', '', text, count=1)
    marks = [(m.start(), m.group(1), m.end()) for m in OPT.finditer(body)]
    best = None
    for i, (p, L, e) in enumerate(marks):
        if L != 'A': continue
        seq = [(p, L, e)]; want = 'B'
        for (p2, L2, e2) in marks[i + 1:]:
            if L2 == want: seq.append((p2, L2, e2)); want = chr(ord(want) + 1)
            if want == 'E': break
        if len(seq) == 4: best = seq
    if not best: return body.strip(), None
    stem = body[:best[0][0]].strip()
    opts = OrderedDict()
    for k, (p, L, e) in enumerate(best):
        end = best[k + 1][0] if k + 1 < 4 else len(body)
        opts[L] = re.sub(r'\s+', ' ', body[e:end]).strip()
    return stem, opts

def analysis_index(path):
    doc = pymupdf.open('/home/user/' + path)
    full, offs = '', []
    for p in doc:
        offs.append(len(full))
        full += clean_lines(unicodedata.normalize('NFKC', p.get_text())) + '\n'
    full = re.sub(r'[ \t]+', ' ', full)
    def scan(start):
        seq, last = [], 0
        for m in QMARK.finditer(full, start):
            n = int(next(g for g in m.groups() if g))
            if last < n <= last + 3: seq.append((m.start(), n)); last = n
        return seq
    seq = scan(0)
    segs = {}
    for i, (pos, n) in enumerate(seq):
        end = seq[i + 1][0] if i + 1 < len(seq) else len(full)
        segs[n] = (pos, end)
    return full, offs, segs, len(doc)

def ocr_analysis_region(afile, full, offs, segs, n, tag):
    """analysis text layer empty for question n: crop the region between its marker and the next marker, OCR it."""
    import subprocess
    from PIL import Image
    s, e = segs[n]
    first = full[s:e].strip().split('\n')[0].strip()
    nxt = full[e:e + 200].strip().split('\n')[0].strip() if e < len(full) else None
    doc = pymupdf.open('/home/user/' + afile)
    s_ = s + (len(full[s:e]) - len(full[s:e].lstrip()))
    e_ = e + (len(full[e:e + 50]) - len(full[e:e + 50].lstrip())) if e < len(full) else e
    p0 = page_of(offs, s_) - 1; p1 = page_of(offs, max(s_, e - 1)) - 1
    if nxt: p1 = page_of(offs, e_) - 1
    def ypos(p, txt, default):
        if not txt: return default
        r = doc[p].search_for(txt[:12])
        return r[0].y0 if r else default
    y0 = ypos(p0, first, 0)
    ims = []
    for p in range(p0, p1 + 1):
        page = doc[p]
        ya = y0 - 2 if p == p0 else 40
        yb = ypos(p1, nxt, page.rect.height - 40) - 2 if p == p1 else page.rect.height - 40
        if yb - ya < 8: continue
        pix = page.get_pixmap(clip=pymupdf.Rect(20, ya, page.rect.width - 20, yb), dpi=200)
        ims.append(Image.frombytes('RGB', (pix.width, pix.height), pix.samples))
    if not ims: return None, None
    W = max(i.width for i in ims); H = sum(i.height for i in ims)
    c = Image.new('RGB', (W, H), 'white'); y = 0
    for i in ims: c.paste(i, (0, y)); y += i.height
    fn = f'{tag}_a{n}.png'; path = os.path.join(IMG, fn)
    c.convert('L').save(path, optimize=True)
    if os.environ.get('NO_OCR'):
        return 'img/' + fn, None
    try:
        txt = subprocess.run(['tesseract', path, 'stdout', '-l', 'chi_sim', '--psm', '6'], capture_output=True, text=True, timeout=300, env=dict(os.environ, OMP_THREAD_LIMIT='1')).stdout
        txt = re.sub(r'(?<=[\u4e00-\u9fff，。、；：（）])\s+(?=[\u4e00-\u9fff，。、；：（）])', '', txt).strip()
    except Exception as ex:
        txt = None
    return 'img/' + fn, txt

def page_of(offs, pos):
    return bisect.bisect_right(offs, pos)  # 1-based

def fix_merged(qs, lo, hi):
    """split questions whose text swallowed following missing numbers (e.g. GD2022Z 32-35)."""
    have = {q['qno'] for q in qs}
    out = []
    for q in qs:
        out.append(q)
        missing = [n for n in range(q['qno'] + 1, hi + 1) if n not in have]
        if not missing: continue
        t = q['text']; cuts = []
        for n in missing:
            m = re.search(r'(?:^|\n)\s*%d\s*[\.．、]' % n, t)
            if m: cuts.append((m.start(), n))
            else: break
        if not cuts: continue
        cuts.sort(); parts = []
        prev = 0; prevn = q['qno']
        for pos, n in cuts:
            parts.append((prevn, t[prev:pos])); prev, prevn = pos, n
        parts.append((prevn, t[prev:]))
        q['text'] = parts[0][1]
        for n, tx in parts[1:]:
            nq = dict(q); nq['qno'] = n; nq['text'] = tx.strip('\n'); nq['split_from'] = q['qno']
            out.append(nq); have.add(n)
    return sorted(out, key=lambda x: x['qno'])

def render(q, tag):
    doc = pymupdf.open('/home/user/' + q['file'])
    from PIL import Image
    ims = []
    for (p, y0, y1) in q['segs']:
        page = doc[p]
        clip = pymupdf.Rect(20, max(0, y0 - 2), page.rect.width - 20, min(page.rect.height, y1 + 2))
        pix = page.get_pixmap(clip=clip, dpi=150)
        ims.append(Image.frombytes('RGB', (pix.width, pix.height), pix.samples))
    W = max(i.width for i in ims); H = sum(i.height for i in ims)
    c = Image.new('RGB', (W, H), 'white'); y = 0
    for i in ims: c.paste(i, (0, y)); y += i.height
    fn = f'{tag}_q{q["qno"]}.png'
    c.convert('L').save(os.path.join(IMG, fn), optimize=True)
    return 'img/' + fn

def meta(tag):
    pid = tag.replace('_xc', '')
    m = re.match(r'([A-Z]+?)(20\d\d)(.*)', pid)
    pre, yr, var = m.group(1), m.group(2), m.group(3)
    return pid, f"{LABEL.get(pre, pre)} {yr}年度 {VAR.get(var, var)}".strip()

def export(tag, ans_tag=None, note=''):
    qs = json.load(open(f'{IDX}/{tag}.json'))
    qfile = qs[0]['file']
    pid, label = meta(tag)
    if tag in RANGES:
        lo, hi = RANGES[tag]
        sel = [q for q in qs if q['kind'] == 'q' and lo <= q['qno'] <= hi]
    else:
        sel = [q for q in qs if q['kind'] == 'q' and q['section'] == '数量']
        lo, hi = (min(q['qno'] for q in sel), max(q['qno'] for q in sel)) if sel else (0, -1)
    sel = fix_merged(sel, lo, hi)
    ans_tag = ans_tag or tag
    A, afile, full, offs, asegs = {}, None, None, None, {}
    if os.path.exists(f'{ANSD}/{ans_tag}.json'):
        aj = json.load(open(f'{ANSD}/{ans_tag}.json')); A = aj['answers']; afile = aj['file']
        full, offs, asegs, _ = analysis_index(afile)
    recs = []
    for q in sel:
        q = dict(q); q['text'] = clean_lines(q['text'])
        stem, opts = split_options(q['text'])
        flags = []
        if q.get('images'): flags.append(f"题目区域含{len(q['images'])}处嵌入图片（可能是图形/公式/表格/数字），文字层不含其内容，待核图")
        core = re.sub(r'[\s,，、()（）\.。:：?？_]', '', stem)
        if len(core) < 8: flags.append('题干文字缺失或过短（疑为图片/公式），待核图')
        if opts is None: flags.append('未能按A—D切出选项（可能为图片选项或排版异常），选项见原文/截图，待核图')
        elif any(not v for v in opts.values()): flags.append('部分选项无文字（疑为图片或公式），待核图')
        if re.search(r'[-�□]', q['text']): flags.append('含异常字符（私有区/替换符），待核图')
        if re.search(r'(?:^|\n)\s*\d{1,3}\s*(?:\n\s*\d{1,3}\s*){1,}(?:\n|$)', stem) and '数' in label: flags.append('疑似分数/上下标被拆行，待核图')
        if q.get('split_from'): flags.append(f"本题由切题时并入第{q['split_from']}题的文字中拆出，页码沿用该区域，请对照截图")
        a = A.get(str(q['qno']), {})
        an_txt, an_pages, an_ocr, an_crop = None, None, None, None
        if afile and q['qno'] in asegs:
            s, e = asegs[q['qno']]
            an_txt = full[s:e].strip()
            s_ = s + (len(full[s:e]) - len(full[s:e].lstrip()))
            an_pages = sorted({page_of(offs, s_), page_of(offs, max(s_, e - 2))})
            body = re.sub(r'^\S*\s*\d{1,3}\s*\S{0,4}', '', an_txt, count=1)
            gaps = len(re.findall(r'\n\s*[,，。;；:：、)）]', body)) + len(re.findall(r'(?:[\u4e00-\u9fff]|[=＝]) +(?=[,，。;；:：、)）])', body))
            if len(re.sub(r'\s', '', body)) >= 25 and gaps >= 2:
                an_crop, _ = ocr_analysis_region(afile, full, offs, asegs, q['qno'], tag) if os.environ.get('NO_OCR') else (None, None)
                flags.append(f'原解析文字层中约有{gaps}处空缺（公式/数字多为图片），已附解析截图，以截图为准（待核图）')
            if len(re.sub(r'\s', '', body)) < 25:
                an_crop, an_ocr = ocr_analysis_region(afile, full, offs, asegs, q['qno'], tag)
                flags.append('原解析在解析PDF中无文字层（疑为图片），已截图' + ('' if os.environ.get('NO_OCR') else '并附OCR文本（未逐字校对，以截图为准）'))
                if not a.get('ans') and an_ocr:
                    mm = re.search(r'正确答案\s*[为是]?\s*[:：]?\s*([A-D])', an_ocr)
                    if mm: a = dict(a); a['ans_ocr'] = mm.group(1)
        img = render(q, tag) if flags else None
        pages = sorted({p + 1 for (p, _, _) in q['segs']})
        recs.append(OrderedDict(paper=pid, label=label, repo=qfile.split('/')[0], q_file=qfile, q_pages=pages, qno=q['qno'],
                                stem=stem, options=opts, raw_text=q['text'], extraction_flags=flags, crop=img,
                                ans_repo=(afile.split('/')[0] if afile else None), ans_file=afile, ans_pages=an_pages,
                                source_answer=a.get('ans'), source_rate=a.get('rate'), source_yicuo=a.get('yicuo'),
                                source_analysis=an_txt, source_analysis_ocr=an_ocr, analysis_crop=an_crop,
                                source_answer_from_ocr=a.get('ans_ocr'), version_note=note))
    return recs, dict(tag=tag, pid=pid, label=label, q_file=qfile, ans_file=afile, n=len(recs), range=(lo, hi),
                      n_flag=sum(1 for r in recs if r['extraction_flags']), n_ans=sum(1 for r in recs if r['source_answer']),
                      n_analysis=sum(1 for r in recs if r['source_analysis']), note=note)

def to_md(recs, info):
    L = [f"# 数量关系原文｜{info['label']}（{info['pid']}）", '',
         f"- 题本：`{info['q_file']}`（仓库 {info['q_file'].split('/')[0]}）",
         f"- 解析：`{info['ans_file']}`" if info['ans_file'] else '- 解析：本批无可用文字层解析（见索引说明）',
         f"- 数量部分原题号：{info['range'][0]}—{info['range'][1]}，共 {info['n']} 题；带“待核图”提示 {info['n_flag']} 题",
         f"- 说明：{info['note']}" if info['note'] else '- 说明：题干、选项照题本文字层抽取；原解析照解析文字层抽取，未改写、未重解。页码为 PDF 物理页（从 1 起）。',
         '- 提示：自动抽取。分数、根号、上下标、图形、表格在文字层中可能缺失或拆行；凡标“待核图”的题附截图（img/），以截图/原 PDF 为准。', '']
    for r in recs:
        L.append(f"## 原题 {r['qno']}　（题本第 {','.join(map(str, r['q_pages']))} 页）")
        if r['extraction_flags']:
            L.append('> 抽取提示：' + '；'.join(r['extraction_flags']) + (f"　截图：`{r['crop']}`" if r['crop'] else ''))
        L += ['', '**题干**', '', r['stem'] or '（无文字）', '']
        if r['options']:
            L.append('**选项**'); L.append('')
            for k, v in r['options'].items(): L.append(f"- {k}. {v}")
            L.append('')
        else:
            L += ['**题目原始文字（未能切分选项）**', '', '```', r['raw_text'], '```', '']
        ans = r['source_answer'] or '（未抽到）'
        extra = []
        if r['source_rate'] is not None: extra.append(f"原解析标注正确率 {r['source_rate']}%")
        if r['source_yicuo']: extra.append(f"易错项 {r['source_yicuo']}")
        L.append(f"**原参考答案**：{ans}" + (f"（解析第 {','.join(map(str, r['ans_pages']))} 页）" if r['ans_pages'] else '') + ('；' + '，'.join(extra) if extra else ''))
        L.append('')
        if r.get('source_answer_from_ocr') and not r['source_answer']:
            L += [f"**原参考答案（OCR 识别，待核图）**：{r['source_answer_from_ocr']}", '']
        if r['source_analysis'] and not r.get('source_analysis_ocr'):
            cap = '**原解析（照录，未改写）**' + (f"　公式可能缺失，见截图 `{r['analysis_crop']}`" if r.get('analysis_crop') else '')
            L += [cap, '', '```text', r['source_analysis'], '```', '']
        elif r.get('source_analysis_ocr'):
            L += [f"**原解析（解析 PDF 此处为图片；OCR 文本未校对，以截图 `{r['analysis_crop']}` 为准）**", '', '```text', r['source_analysis_ocr'], '```', '']
        elif r.get('analysis_crop'):
            L += [f"**原解析**：解析 PDF 此处为图片，无文字层，见截图 `{r['analysis_crop']}`（待核图）", '']
        else:
            L += ['**原解析**：未抽到文字（解析为扫描件/缺失/格式未识别）', '']
    return '\n'.join(L) + '\n'

if __name__ == '__main__':
    plan = json.load(open('/home/user/work/quant/plan.json'))
    allrecs, infos = [], []
    for item in plan:
        recs, info = export(item['tag'], item.get('ans_tag'), item.get('note', ''))
        fn = f"{item['tag']}.md"
        open(os.path.join(OUT, fn), 'w').write(to_md(recs, info))
        info['md'] = fn; infos.append(info); allrecs += recs
        print(f"{item['tag']:12} n={info['n']:3} ans={info['n_ans']:3} analysis={info['n_analysis']:3} flag={info['n_flag']:3} range={info['range']}")
    with open(os.path.join(OUT, 'quant_source.jsonl'), 'w') as fo:
        for r in allrecs: fo.write(json.dumps(r, ensure_ascii=False) + '\n')
    json.dump(infos, open(os.path.join(OUT, '_infos.json'), 'w'), ensure_ascii=False, indent=1)

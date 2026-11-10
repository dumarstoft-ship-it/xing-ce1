"""Build OCR supplement for scanned Guangdong analyses (数量 part) + GD2021X transcription."""
import json, os, re, glob, bisect
from PIL import Image
OCR = '/home/user/work/ocr'; OUT = '/home/user/work/quant/ocr_supp'
RANGES = {'GD2017': (16, 30), 'GD2018': (16, 30), 'GD2019X': (16, 30), 'GD2019Z': (11, 25), 'GD2020X': (26, 40),
          'GD2020Z': (31, 45), 'GD2021Z': (31, 45), 'GD2021X': (26, 40)}
LETTER = {'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D', '4': 'A', '8': 'B', 'O': 'D', '0': 'D', 'a': 'A', 'c': 'C'}
def load(tag):
    meta = json.load(open(f'{OCR}/{tag}_ans/_meta.json'))
    pages = sorted(glob.glob(f'{OCR}/{tag}_ans/p*.txt'))
    full, offs = '', []
    for p in pages:
        offs.append(len(full)); full += open(p).read() + '\n'
    return meta, full, offs, len(pages)
def page_of(offs, pos): return bisect.bisect_right(offs, pos)
recs = []; md = {}
for tag, (lo, hi) in RANGES.items():
    meta, full, offs, npg = load(tag)
    # question markers at line start: number + 、 (OCR may give , . ， etc.)
    marks = [(m.start(), int(m.group(1))) for m in re.finditer(r'(?m)^\s*(\d{1,3})\s*[、，,\.．]', full)]
    seq, last = [], 0
    for pos, n in marks:
        if last < n <= last + 3: seq.append((pos, n)); last = n
    segs = {}
    for i, (pos, n) in enumerate(seq):
        end = seq[i + 1][0] if i + 1 < len(seq) else len(full)
        segs[n] = (pos, end)
    L = [f"# 数量关系原解析（OCR 补充）｜{tag}", '',
         f"- 解析文件：`{meta['file']}`（扫描件，无文字层）",
         '- 以下文字由 Tesseract OCR（chi_sim）识别，**未逐字校对**；数字、符号、分数、字母常有误识别（如 A 被识别成 4）。“OCR 读出的答案字母”只作线索，用前请看页面截图。',
         f"- 页面截图：`img/{tag}_ans_p<页码>.png`（数量部分所在页）", '']
    used_pages = set()
    for n in range(lo, hi + 1):
        if n not in segs:
            L += [f'## 原题 {n}', '', 'OCR 未定位到本题解析（题号识别失败），请看截图。', '']
            recs.append(dict(paper=tag, qno=n, ans_file=meta['file'], ans_pages=None, ocr_answer=None, ocr_text=None, note='OCR未定位'))
            continue
        s, e = segs[n]; txt = full[s:e].strip()
        pg = sorted({page_of(offs, s), page_of(offs, max(s, e - 2))}); used_pages.update(pg)
        m = re.search(r'正确答案\s*[为是]?\s*[:：]?\s*([A-Da-c4O08])', txt) or re.search(r'答案\s*[为是]\s*([A-Da-c4O08])', txt)
        a = LETTER.get(m.group(1)) if m else None
        recs.append(dict(paper=tag, qno=n, ans_file=meta['file'], ans_pages=pg, ocr_answer=a, ocr_text=txt))
        L += [f'## 原题 {n}　（解析第 {",".join(map(str, pg))} 页）', '', f"**OCR 读出的答案字母**：{a or '（未读出）'}　（待核图）", '', '```text', txt, '```', '']
    for p in sorted(used_pages):
        src = f'{OCR}/{tag}_ans/p{p:03d}.png'
        if os.path.exists(src):
            im = Image.open(src).convert('L'); im = im.resize((im.width * 130 // 250, im.height * 130 // 250), Image.LANCZOS)
            im.quantize(16).save(f'{OUT}/img/{tag}_ans_p{p}.png', optimize=True)
    md[tag] = '\n'.join(L) + '\n'
    open(f'{OUT}/{tag}_OCR解析.md', 'w').write(md[tag])
    got = sum(1 for r in recs if r['paper'] == tag and r.get('ocr_answer'))
    print(tag, 'located', sum(1 for n in range(lo, hi + 1) if n in segs), 'answers', got, 'pages', sorted(used_pages))
with open(f'{OUT}/ocr_analysis.jsonl', 'w') as fo:
    for r in recs: fo.write(json.dumps(r, ensure_ascii=False) + '\n')

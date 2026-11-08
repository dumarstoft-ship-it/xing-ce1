"""Build printable two-pass question books (PDF) for round 1 from GPT v2 Markdown books on main."""
import os, re, subprocess, json, sys, html as H
from bs4 import BeautifulSoup
from PIL import Image
import hashlib
CACHE = '/home/user/work/books/img_cache'; os.makedirs(CACHE, exist_ok=True)
def compress(path):
    h = hashlib.md5(path.encode()).hexdigest()[:12]
    im = Image.open(path)
    if im.mode in ('RGBA', 'LA', 'P'):
        im = im.convert('RGBA'); bg = Image.new('RGB', im.size, 'white'); bg.paste(im, mask=im.split()[-1]); im = bg
    im = im.convert('RGB')
    if im.width > 1300: im = im.resize((1300, int(im.height * 1300 / im.width)), Image.LANCZOS)
    small = im.resize((max(1, im.width // 10), max(1, im.height // 10)))
    spread = max((max(p) - min(p)) for p in small.getdata())
    if spread < 40:
        out = f'{CACHE}/{h}.png'
        if not os.path.exists(out): im.convert('L').quantize(16, dither=Image.Dither.NONE).save(out, optimize=True)
    else:
        out = f'{CACHE}/{h}.png'
        if not os.path.exists(out): im.quantize(64, dither=Image.Dither.NONE).save(out, optimize=True)
    return out

BASE = '/home/user/work/main_wt/广东行测24天集训'
OUT = '/home/user/work/books/out'; os.makedirs(OUT, exist_ok=True)
DAYS = {
 'D01': {'title': 'D01 · 数量 135 题 ＋ 言语 40 题', 'parts': [('GPT_数量/D01/D01_数字推理001-030_题本.md', '数量 · 数字推理（N001—N030）'), ('GPT_数量/D01/D01_数学运算001-060_题本.md', '数量 · 数学运算（M001—M060）'), ('GPT_数量/D01/D01_数学运算061-105_题本.md', '数量 · 数学运算（M061—M105）'), ('GPT_复核/第1批/D01_言语_题目册.md', '言语 40 题')]},
 'D02': {'title': 'D02 · 资料 135 题 ＋ 言语 40 题', 'parts': [('GPT_复核/第1批/D02_资料_题目册.md', '资料分析 135 题'), ('GPT_复核/第1批/D02_言语_题目册.md', '言语 40 题')]},
 'D03': {'title': 'D03 · 判断 135 题 ＋ 言语 40 题', 'parts': [('GPT_复核/第1批/D03_判断_题目册.md', '判断推理 135 题'), ('GPT_复核/第1批/D03_言语_题目册.md', '言语 40 题')]},
}
CSS = """
@page { size: A4; margin: 16mm 14mm 16mm 14mm; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: "Noto Sans CJK SC","Noto Sans SC","Source Han Sans SC","WenQuanYi Zen Hei","WenQuanYi Micro Hei","PingFang SC","Microsoft YaHei",sans-serif; font-size: 10.5pt; line-height: 1.6; color: #111; }
h1.part { font-size: 15pt; margin: 0 0 6mm; padding-bottom: 2mm; border-bottom: 1.5px solid #333; break-before: page; }
h1.part.first { break-before: auto; }
h2 { font-size: 12pt; margin: 6mm 0 2mm; padding: 1mm 0; border-bottom: 1px solid #bbb; break-after: avoid; }
section.q { break-inside: avoid; margin: 0 0 4.5mm; }
section.q h3 { font-size: 9.5pt; font-weight: 700; color: #444; margin: 0 0 1mm; break-after: avoid; }
section.q p { margin: 0.6mm 0; }
section.mat { margin: 0 0 3mm; }
img { display: block; max-width: 100%; max-height: 240mm; height: auto; margin: 1.5mm 0; break-inside: avoid; }
.opts { display: grid; gap: 0.4mm 4mm; margin: 0.8mm 0 0; }
.opts.c4 { grid-template-columns: repeat(4, 1fr); }
.opts.c2 { grid-template-columns: repeat(2, 1fr); }
.opts.c1 { grid-template-columns: 1fr; }
details { display: none; }
details[open] { display: block; border-left: 2px solid #ccc; padding-left: 3mm; }
details[open] summary { display: none; }
.cover { height: 250mm; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; break-after: page; }
.cover .big { font-size: 26pt; font-weight: 700; margin-bottom: 8mm; }
.cover .pass { font-size: 20pt; margin-bottom: 14mm; letter-spacing: 0.2em; }
.cover .meta { font-size: 11pt; color: #444; line-height: 2; }
a { color: inherit; text-decoration: none; }
"""
LINKLINE = re.compile(r'^\s*\[[^\]]*\]\([^)]*\.(md|jsonl|json|html)\)(\s*[｜|]\s*\[[^\]]*\]\([^)]*\))*\s*$')
def md_to_html(path):
    src = open(os.path.join(BASE, path), encoding='utf-8').read()
    lines = [l for l in src.split('\n') if not LINKLINE.match(l)]
    md = '\n'.join(lines)
    out = subprocess.run(['pandoc', '-f', 'gfm', '-t', 'html5', '--wrap=none'], input=md, capture_output=True, text=True, check=True).stdout
    soup = BeautifulSoup(out, 'html.parser')
    d = os.path.dirname(os.path.join(BASE, path))
    for img in soup.find_all('img'):
        s = img.get('src', '')
        if s and not s.startswith(('data:', 'file:', 'http')): img['src'] = 'file://' + compress(os.path.abspath(os.path.join(d, s)))
    # drop the book's own H1 and intro paragraphs before the first H2/H3
    first = soup.find(['h2', 'h3'])
    for el in list(soup.children):
        if el is first: break
        if getattr(el, 'name', None) or str(el).strip(): el.extract()
    # wrap questions: each h3 + following siblings until next h2/h3
    body = BeautifulSoup('', 'html.parser')
    out_nodes = []; cur = None
    for el in list(soup.children):
        name = getattr(el, 'name', None)
        if name == 'h3':
            cur = soup.new_tag('section', attrs={'class': 'q'}); cur.append(el); out_nodes.append(cur); continue
        if name == 'h2':
            cur = None
            # material header (资料): keep h2 + its image + details together as a 'mat' block
            if '材料' in el.get_text():
                cur = soup.new_tag('section', attrs={'class': 'mat'}); cur.append(el); out_nodes.append(cur); continue
            out_nodes.append(el); continue
        if cur is not None: cur.append(el)
        else: out_nodes.append(el)
    # compact A-D options into a grid
    OPT = re.compile(r'^\s*([A-D])[\.．、]\s*(.*)$')
    allp = [p for n in out_nodes if getattr(n, 'name', None) for p in ([n] if n.name == 'p' else n.find_all('p'))]
    for p in allp:
        lines = [x.strip() for x in p.get_text('\n').split('\n') if x.strip()]
        if len(lines) == 4 and all(OPT.match(x) for x in lines) and [OPT.match(x).group(1) for x in lines] == list('ABCD'):
            mx = max(len(x) for x in lines)
            cols = 4 if mx <= 9 else (2 if mx <= 20 else 1)
            div = soup.new_tag('div', attrs={'class': f'opts c{cols}'})
            for x in lines:
                sp = soup.new_tag('span'); sp.string = x; div.append(sp)
            p.replace_with(div)
    # open details for materials without image
    for sec in out_nodes:
        if getattr(sec, 'name', None) == 'section' and 'mat' in sec.get('class', []):
            if not sec.find('img'):
                for det in sec.find_all('details'): det['open'] = ''
    return ''.join(str(n) for n in out_nodes)
def build(day, cfg, pass_label):
    parts = []
    for i, (p, title) in enumerate(cfg['parts']):
        parts.append(f'<h1 class="part{" first" if i == 0 else ""}">{H.escape(title)}</h1>' + md_to_html(p))
    cover = (f'<div class="cover"><div class="big">第1轮 · {H.escape(cfg["title"])}</div><div class="pass">题本 · {pass_label}</div>'
             f'<div class="meta">版本：main 34db477（第一轮 v2，2026-11-08）<br>只含题目，不含答案；答案与原文见仓库“第1轮_使用入口”各答案册<br>'
             f'{"第一遍做完后，第二遍在后面的“第二遍”题本上作答，两遍都做完再核对答案" if pass_label == "第一遍" else "第二遍在本册作答；两遍都做完再核对答案"}</div></div>')
    return f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>第1轮 {day} {pass_label}</title><style>{CSS}</style></head><body>{cover}{"".join(parts)}</body></html>'
if __name__ == '__main__':
    for day, cfg in DAYS.items():
        for k, label in (('1', '第一遍'), ('2', '第二遍')):
            open(f'{OUT}/{day}_{k}.html', 'w', encoding='utf-8').write(build(day, cfg, label))
        print(day, 'html ok')

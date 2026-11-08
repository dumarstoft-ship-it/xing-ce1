"""Build printable two-pass question books (PDF) for round 2: D04 quantity from GPT main (D04-v1), D05/D06 and verbal from Claude batch 2 (via gen_md_r2.py)."""
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

BASE = '/home/user/work/main_wt2/广东行测24天集训'
OUT = '/home/user/work/books/out_r2'; os.makedirs(OUT, exist_ok=True)
DAYS = {
 'D04': {'title': 'D04 · 数量 135 题 ＋ 言语 40 题', 'parts': [('GPT_数量/D04/完整135题_v1/D04_数字推理001-030_题本.md', '数量 · 数字推理（N001—N030）'), ('GPT_数量/D04/完整135题_v1/D04_数学运算001-040_题本.md', '数量 · 数学运算（M001—M040）'), ('GPT_数量/D04/完整135题_v1/D04_数学运算041-080_题本.md', '数量 · 数学运算（M041—M080）'), ('GPT_数量/D04/完整135题_v1/D04_数学运算081-105_题本.md', '数量 · 数学运算（M081—M105）'), ('/home/user/work/books/r2_md/D04_言语.md', '言语 40 题')]},
 'D05': {'title': 'D05 · 资料 135 题 ＋ 言语 40 题', 'parts': [('/home/user/work/books/r2_md/D05_资料.md', '资料分析 135 题'), ('/home/user/work/books/r2_md/D05_言语.md', '言语 40 题')]},
 'D06': {'title': 'D06 · 判断 135 题 ＋ 言语 40 题', 'parts': [('/home/user/work/books/r2_md/D06_判断.md', '判断推理 135 题'), ('/home/user/work/books/r2_md/D06_言语.md', '言语 40 题')]},
}
VERSION = '版本：Claude 第2批（分支 claude/optimistic-bardeen-qkrbx0，GPT 第2轮审核后修订，2026-11-08）；D04 数量为 GPT main 上的 D04-v1'
DAY_NOTES = {
 'D04': ('<div class="note"><b>D04 数量：GPT 还在修订，做题时请注意</b>（GPT 第2轮审核已确认，题本暂未改）<br>'
         '· M018：按“两个项目全部完成前，任何工人不得调动；先完工的一组也不支援另一组”理解。<br>'
         '· M092：按“乙恰好在某一天结束时全部完成”理解。<br>'
         '· M049：按实际时间计，可不足一天。M035：两人位置重合即算一次相遇，追平也算。<br>'
         '· M041、M084、N004、N025、N027：42 天习题本前三天做过，GPT 会替换；本次可跳过，或当复习。<br>'
         '· N007：有另一条说得通的规律，GPT 会替换；可跳过。<br>'
         'GPT 改完后会重出 D04 这一本。</div>'),
 'D05': ('<div class="note">资料按材料连续排列：同一份材料的设问连着做。本日材料较多（60 份），阅读量比真题卷大。</div>'),
}
PART_NOTES = {
 'D04_数字推理001-030_题本.md': '选择最符合常见数列规律的选项。a/b 表示分数，√ 表示根号；机械拆分按题面数字书写形式观察。本册不使用仅尾零不同但数值相同的选项。',
 'D04_数学运算001-040_题本.md': '说明：效率恒定、工作量可相加等条件以各题表述为准；未另说明时，通常工程题按恒定效率模型处理。不可拆分、停机、整数人数及工序先后等限制不可忽略。',
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
.cover .note { margin-top: 12mm; max-width: 165mm; text-align: left; font-size: 10pt; line-height: 1.75; border: 1px solid #999; padding: 4mm 5mm; }
p.partnote { font-size: 9.5pt; color: #333; border-left: 2px solid #999; padding-left: 3mm; margin: 0 0 4mm; }
a { color: inherit; text-decoration: none; }
"""
LINKLINE = re.compile(r'^\s*\[[^\]]*\]\([^)]*\.(md|jsonl|json|html)\)(\s*[｜|]\s*\[[^\]]*\]\([^)]*\))*\s*$')
def md_to_html(path):
    full = path if os.path.isabs(path) else os.path.join(BASE, path)
    src = open(full, encoding='utf-8').read()
    lines = [l for l in src.split('\n') if not LINKLINE.match(l)]
    md = '\n'.join(lines)
    out = subprocess.run(['pandoc', '-f', 'gfm', '-t', 'html5', '--wrap=none'], input=md, capture_output=True, text=True, check=True).stdout
    soup = BeautifulSoup(out, 'html.parser')
    d = os.path.dirname(full)
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
        pn = PART_NOTES.get(os.path.basename(p))
        parts.append(f'<h1 class="part{" first" if i == 0 else ""}">{H.escape(title)}</h1>' + (f'<p class="partnote">{H.escape(pn)}</p>' if pn else '') + md_to_html(p))
    notes = DAY_NOTES.get(day, '')
    cover = (f'<div class="cover"><div class="big">第2轮 · {H.escape(cfg["title"])}</div><div class="pass">题本 · {pass_label}</div>'
             f'<div class="meta">{VERSION}<br>只含题目，不含答案；答案与原文见仓库各答案册（见打包目录 README）<br>'
             f'{"第一遍做完后，第二遍在后面的“第二遍”题本上作答，两遍都做完再核对答案" if pass_label == "第一遍" else "第二遍在本册作答；两遍都做完再核对答案"}</div>'
             f'{notes}</div>')
    return f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>第2轮 {day} {pass_label}</title><style>{CSS}</style></head><body>{cover}{"".join(parts)}</body></html>'
if __name__ == '__main__':
    for day, cfg in DAYS.items():
        for k, label in (('1', '第一遍'), ('2', '第二遍')):
            open(f'{OUT}/{day}_{k}.html', 'w', encoding='utf-8').write(build(day, cfg, label))
        print(day, 'html ok')

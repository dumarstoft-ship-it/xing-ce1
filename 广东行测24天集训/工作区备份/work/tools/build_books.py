"""Build offline HTML question books and answer books from merged records.
Input: /home/user/work/build/merged.jsonl (final records with final ids), materials.jsonl, articles.jsonl, asset root dir.
Output: HTML files (images embedded as base64)."""
import json, os, sys, base64, html, re, io
from PIL import Image
B = '/home/user/work/build'
def esc(s): return html.escape(s or '').replace('\n', '<br>')
_IMGS = {}
_KEYS = {}
def _encode(path):
    im = Image.open(path)
    if im.mode in ('RGBA', 'LA'):
        bg = Image.new('RGB', im.size, 'white'); bg.paste(im, mask=im.split()[-1]); im = bg
    im = im.convert('RGB')
    if im.width > 1100: im = im.resize((1100, int(im.height * 1100 / im.width)), Image.LANCZOS)
    # grayscale if colour spread is tiny
    small = im.resize((max(1, im.width // 8), max(1, im.height // 8)))
    px = list(small.getdata()); spread = max((max(p) - min(p)) for p in px) if px else 0
    buf = io.BytesIO()
    if spread < 40: im.convert('L').quantize(16, dither=Image.Dither.NONE).save(buf, 'PNG', optimize=True)
    else: im.quantize(48, dither=Image.Dither.NONE).save(buf, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()
def img_tag(path, maxw='100%'):
    if not path or not os.path.exists(path): return f'<div class="missing">［缺图：{esc(os.path.basename(path or ""))}］</div>'
    k = _KEYS.get(path)
    if not k:
        k = f'i{len(_KEYS)}'; _KEYS[path] = k; _IMGS[k] = _encode(path)
    return f'<img data-k="{k}" style="max-width:{maxw}" alt="">'
def _img_script():
    if not _IMGS: return ''
    js = 'const IM=' + json.dumps(_IMGS) + ';document.querySelectorAll("img[data-k]").forEach(function(e){e.src=IM[e.dataset.k];});'
    _IMGS.clear(); _KEYS.clear()
    return '<script>' + js + '</script>'

CSS = """
:root{--ink:#1d2125;--soft:#5b636b;--rule:#d9dcd6;--paper:#fbfbf8;--chip:#eef0ec;--accent:#1f5f8b;--warn:#9a3412}
@media (prefers-color-scheme: dark){:root{--ink:#e4e6e3;--soft:#a3a9ae;--rule:#30363c;--paper:#16191c;--chip:#23292f;--accent:#8fb6dd;--warn:#f0a07a}
 img{filter:invert(0.88) hue-rotate(180deg)}}
body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.75 "PingFang SC","Microsoft YaHei","Noto Sans SC",system-ui,sans-serif}
main{max-width:860px;margin:0 auto;padding:16px;overflow-wrap:anywhere}
h1{font-size:1.35rem;margin:.4em 0}h2{font-size:1.1rem;margin:1.6em 0 .6em;padding-top:.6em;border-top:2px solid var(--rule)}
.meta{color:var(--soft);font-size:.85rem}.q{margin:1.1em 0 1.4em;padding-bottom:.8em;border-bottom:1px dashed var(--rule)}
.qid{display:inline-block;font-size:.78rem;background:var(--chip);border-radius:4px;padding:0 6px;margin-right:6px;color:var(--soft);font-variant-numeric:tabular-nums}
.src{font-size:.75rem;color:var(--soft)}.opt{margin:.15em 0 .15em 1.2em}.mat{background:var(--chip);border-radius:6px;padding:10px 12px;margin:1em 0}
.mat .mt{font-size:.8rem;color:var(--soft)}img{display:block;margin:.4em 0;height:auto}
.ans{font-weight:700;color:var(--accent)}.flag{color:var(--warn);font-size:.8rem}.missing{color:var(--warn)}
.art{border-left:3px solid var(--rule);padding:2px 0 2px 12px;margin:.6em 0 1.2em}.art p{margin:.4em 0}
table{border-collapse:collapse;font-size:.85rem}td,th{border:1px solid var(--rule);padding:2px 6px}
nav a{margin-right:10px;font-size:.85rem;color:var(--accent)}
"""
def page(title, body):
    return f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)}</title><style>{CSS}</style></head><body><main>{body}</main>{_img_script()}</body></html>'

def src_label(q):
    s = q.get('source') or {}
    p = s.get('paper') or ''
    return f"{p}·{s.get('qno')}" if p and s.get('qno') is not None else p

def options_html(q):
    o = q.get('options') or {}
    if isinstance(o, dict):
        if all((v or '').strip() in ('', '见图', '见图示', '图') for v in o.values()): return ''
        return ''.join(f'<div class="opt">{esc(k)}. {esc(v)}</div>' for k, v in o.items())
    return ''

def build_question_book(recs, mats, arts, asset_root, title, intro):
    out = [f'<h1>{esc(title)}</h1><div class="meta">{intro}</div>']
    cur_g = None; shown_mat = set()
    for q in recs:
        if q.get('group') != cur_g:
            cur_g = q.get('group'); shown_mat = set()
            out.append(f'<h2>{esc(q.get("group_title") or cur_g)}</h2>')
        mid = q.get('material_or_article')
        if mid and mid in mats and mid not in shown_mat:
            m = mats[mid]; shown_mat.add(mid)
            parts = [f'<div class="mat"><div class="mt">材料 {esc(mid)}</div>']
            t = m.get('text') or ''
            if t: parts.append(f'<div>{esc(t)}</div>')
            needs_img = (not t.strip()) or any(k in t for k in ('见图', '【表】', '【图】', '图表', '如图', '下图', '下表', '见表', '（图', '（表'))
            if needs_img:
                for a in m.get('assets', []): parts.append(img_tag(os.path.join(asset_root, a)))
            elif m.get('assets'):
                parts.append('<div class="meta">（纯文字材料；原页截图存于 ' + esc(', '.join(m['assets'])) + '）</div>')
            parts.append('</div>'); out.append(''.join(parts))
        out.append(f'<div class="q" id="{esc(q["id"])}"><span class="qid">{esc(q["id"])}</span><span class="src">{esc(src_label(q))}</span>'
                   f'<div>{esc(q.get("stem"))}</div>')
        for a in q.get('assets') or []: out.append(img_tag(os.path.join(asset_root, a)))
        out.append(options_html(q) + '</div>')
    return page(title, '\n'.join(out))

def build_answer_book(recs, arts, title, intro, verbal=False):
    out = [f'<h1>{esc(title)}</h1><div class="meta">{intro}</div>']
    cur_g = None; pending_arts = []
    def flush():
        for aid in pending_arts:
            a = arts.get(aid)
            if not a: out.append(f'<div class="missing">［缺原文对象 {esc(aid)}］</div>'); continue
            t = a.get('text') or ''
            paras = ''.join(f'<p>{esc(p)}</p>' for p in t.split('\n') if p.strip())
            kc = a.get('kind_cn') or ''
            out.append(f'<div class="art"><div class="mt meta">原文 {esc(aid)}｜{esc(a.get("title") or "")}' + (f'｜{esc(kc)}' if kc else '') + f'</div>{paras}<div class="meta">{esc(a.get("note") or "")}</div></div>')
        pending_arts.clear()
    for q in recs:
        if q.get('group') != cur_g:
            if verbal: flush()
            cur_g = q.get('group')
            out.append(f'<h2>{esc(q.get("group_title") or cur_g)}</h2>')
        ans = q.get('checked_answer') or q.get('source_answer') or '（无）'
        line = f'<div class="q"><span class="qid">{esc(q["id"])}</span><span class="ans">{esc(ans)}</span> <span class="src">{esc(src_label(q))}</span>'
        if not verbal and q.get('precision_need'): line += f'<span class="meta">　精度：{esc(q["precision_need"])}</span>'
        if not verbal and q.get('brief_solution'): line += f'<div>{esc(q["brief_solution"])}</div>'
        if q.get('flags'): line += f'<div class="flag">{esc("；".join(q["flags"]))}</div>'
        if q.get('dispute_note'): line += f'<div class="flag">原解析争议标记（照录）：{esc(q["dispute_note"])}</div>'
        out.append(line + '</div>')
        aid = q.get('material_or_article')
        if verbal and aid and aid not in pending_arts: pending_arts.append(aid)
    if verbal: flush()
    return page(title, '\n'.join(out))

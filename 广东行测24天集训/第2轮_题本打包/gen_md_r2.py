"""Generate printable Markdown (same shape as GPT's round-1 books) from Claude's round-2 package.
Questions only: no answers, no solutions, no article texts. Output: /home/user/work/books/r2_md/<day>_<module>.md"""
import json, os, re, collections
PKG = '/home/user/work/build/pkg_r2'
OUT = '/home/user/work/books/r2_md'; os.makedirs(OUT, exist_ok=True)
Q = [json.loads(l) for l in open(f'{PKG}/questions.jsonl')]
M = {m['mid']: m for m in (json.loads(l) for l in open(f'{PKG}/materials.jsonl'))}
MOD = {'ZL': '资料', 'PD': '判断', 'YY': '言语'}
KW = ('见图', '【表】', '【图】', '图表', '如图', '下图', '下表', '见表', '（图', '（表')

def esc(t):
    t = (t or '').replace('\\', '\\\\')
    return re.sub(r'([*_#<>\[\]`|])', r'\\\1', t)

def para(t):
    """Keep the source line structure: each source line becomes its own hard-broken line."""
    lines = [l.rstrip() for l in (t or '').split('\n')]
    blocks, cur = [], []
    for l in lines:
        if not l.strip():
            if cur: blocks.append(cur); cur = []
        else: cur.append(esc(l.strip()))
    if cur: blocks.append(cur)
    return '\n\n'.join('  \n'.join(b) for b in blocks)

def src_label(q):
    s = q['source']; p = str(s.get('paper') or '').replace('_xc', '')
    if p.upper().startswith('HTML'): return ''
    lab = f"{p}·{s.get('qno')}"
    if q.get('variant_of'): lab = f"改编自 {q['variant_of']}"
    return lab

def img(path):
    return f'![](/home/user/work/build/pkg_r2/{path})'

by = collections.defaultdict(list)
for q in Q: by[(q['day'], q['id'].split('-')[1])].append(q)
for (day, mc), recs in sorted(by.items()):
    L = [f'# {day} {MOD[mc]} {len(recs)} 题', '']
    cur_g = None; shown = set()
    for q in recs:
        if q.get('group') != cur_g:
            cur_g = q.get('group'); shown = set()
            L += [f'## {esc(q.get("group_title") or cur_g)}', '']
        mid = q.get('material_or_article')
        if mc == 'ZL' and mid and mid in M and mid not in shown:
            shown.add(mid); m = M[mid]; t = m.get('text') or ''
            L += [f'## 材料 {esc(mid)}', '']
            needs_img = (not t.strip()) or any(k in t for k in KW)
            if needs_img:
                for a in m.get('assets', []): L += [img(a), '']
            else:
                L += [para(t), '']
        lab = src_label(q)
        L += [f'### {q["id"]}' + (f'　{esc(lab)}' if lab else ''), '']
        if q.get('stem'): L += [para(q['stem']), '']
        for a in q.get('assets') or []: L += [img(a), '']
        opts = q.get('options') or {}
        if opts and not all((v or '').strip() == '见图' for v in opts.values()):
            L += ['  \n'.join(f'{k}. {esc(v)}' for k, v in opts.items()), '']
    open(f'{OUT}/{day}_{MOD[mc]}.md', 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print(day, MOD[mc], len(recs))

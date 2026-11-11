"""资料减量版：按保留清单从各批成品生成 Markdown 题本（只写题目，不写答案）。
材料按本册出现顺序连续编号（材料 01、02……），同一材料的题连排。
用法：python3 gen_md_reduced.py <配置json> ；配置：{"out": md路径, "title": 标题, "parts": [{"title": 分部标题, "items": [["第2批","D05-ZL-002"], ...]}]}"""
import json, os, re, sys
REPO = '/home/user/xing-ce1/广东行测24天集训/Claude_资料判断言语/'
KW = ('见图', '【表】', '【图】', '图表', '如图', '下图', '下表', '见表', '（图', '（表')
_cache = {}
def batch(b):
    if b not in _cache:
        Q = {q['id']: q for q in (json.loads(l) for l in open(REPO + b + '/questions.jsonl'))}
        M = {m['mid']: m for m in (json.loads(l) for l in open(REPO + b + '/materials.jsonl'))}
        _cache[b] = (Q, M)
    return _cache[b]
def esc(t):
    t = (t or '').replace('\\', '\\\\')
    return re.sub(r'([*_#<>\[\]`|])', r'\\\1', t)
def para(t):
    blocks, cur = [], []
    for l in (t or '').split('\n'):
        if not l.strip():
            if cur: blocks.append(cur); cur = []
        else: cur.append(esc(l.strip()))
    if cur: blocks.append(cur)
    return '\n\n'.join('  \n'.join(b) for b in blocks)
def src_label(q):
    s = q['source']; p = str(s.get('paper') or '').replace('_xc', '')
    if q.get('variant_of'): return f"改编自 {q['variant_of']}"
    return f"{p}·{s.get('qno')}"
cfg = json.load(open(sys.argv[1]))
L = [f"# {cfg['title']}", '']
mat_no = {}; last_mat = None; n = 0
for part in cfg['parts']:
    L += [f"## {esc(part['title'])}", '']
    last_mat = None
    for b, qid in part['items']:
        Q, M = batch(b); q = Q[qid]; n += 1
        mid = q.get('material_or_article')
        if mid and mid != last_mat:
            m = M[mid]
            if mid not in mat_no:
                mat_no[mid] = len(mat_no) + 1
                L += [f"## 材料 {mat_no[mid]:02d} · {esc(mid)}", '']
                t = m.get('text') or ''
                if (not t.strip()) or any(k in t for k in KW):
                    for a in m.get('assets', []): L += [f"![]({REPO}{b}/{a})", '']
                else:
                    L += [para(t), '']
            else:
                L += [f"## 材料 {mat_no[mid]:02d}（续）· {esc(mid)}", '']
            last_mat = mid
        L += [f"### {qid}　{esc(src_label(q))}", '']
        if q.get('stem'): L += [para(q['stem']), '']
        for a in q.get('assets') or []: L += [f"![]({REPO}{b}/{a})", '']
        opts = q.get('options') or {}
        if opts and not all((v or '').strip() == '见图' for v in opts.values()):
            L += ['  \n'.join(f'{k}. {esc(v)}' for k, v in opts.items()), '']
os.makedirs(os.path.dirname(cfg['out']), exist_ok=True)
open(cfg['out'], 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print(cfg['out'], n, 'questions', len(mat_no), 'materials')

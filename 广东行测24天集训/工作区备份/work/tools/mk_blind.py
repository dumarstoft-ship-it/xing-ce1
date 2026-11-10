"""从合并后的成品包里抽题，生成盲审用的题目文件（不含答案、解法、来源）和答案键。
用法：python3 mk_blind.py <成品包目录> <输出目录> [--random-zl N] [--random-pd N] [--seed S] [--ids id1,id2,...]
默认抽：全部改编题（variant_of 非空）、没有原参考答案的题、flags 或 check_status 提示要复核的题，
再按 --random-zl/--random-pd 各随机补若干道原题。言语不盲审（不论证唯一答案）。
输出：<输出目录>/blind_ZL.jsonl、blind_PD.jsonl（每行 {bid, stem, options, material_text, material_images, images}，图片为绝对路径）
      <输出目录>/blind_key.json（{bid: {id, answer, why}}）。盲审者只能看 blind_*.jsonl。
比对：python3 cmp_blind.py <输出目录>（盲审者把答案写成 <输出目录>/ans_ZL.json、ans_PD.json：{bid: {"answer": "A", ...}}）"""
import json, os, sys, random
pkg, out = sys.argv[1], sys.argv[2]
arg = lambda k, d: (sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d)
nzl, npd, seed = int(arg('--random-zl', 6)), int(arg('--random-pd', 20)), int(arg('--seed', 20261110))
ids = set(filter(None, arg('--ids', '').split(',')))
os.makedirs(out, exist_ok=True)
Q = [json.loads(l) for l in open(f'{pkg}/questions.jsonl')]
M = {m['mid']: m for m in (json.loads(l) for l in open(f'{pkg}/materials.jsonl'))}
def why(q):
    w = []
    if q.get('variant_of'): w.append('改编')
    if not q.get('source_answer'): w.append('无原参考答案')
    if any(k in ''.join(q.get('flags') or []) for k in ('复核', '口径', '依赖', '两可', '争议')): w.append('编者标记')
    if q['id'] in ids: w.append('指定')
    return w
rnd = random.Random(seed); key = {}
for mc, n in (('ZL', nzl), ('PD', npd)):
    qs = [q for q in Q if q['id'].split('-')[1] == mc]
    must = [q for q in qs if why(q)]
    rest = [q for q in qs if not why(q)]
    pick = must + rnd.sample(rest, min(n, len(rest)))
    pick.sort(key=lambda q: q['id'])
    with open(f'{out}/blind_{mc}.jsonl', 'w') as w:
        for i, q in enumerate(pick, 1):
            bid = f'{mc}-{i:03d}'
            m = M.get(q.get('material_or_article') or '', {})
            rec = dict(bid=bid, stem=q['stem'], options=q['options'],
                       material_text=m.get('text', ''), material_images=[os.path.abspath(f'{pkg}/{a}') for a in m.get('assets', [])],
                       images=[os.path.abspath(f'{pkg}/{a}') for a in q.get('assets') or []])
            w.write(json.dumps(rec, ensure_ascii=False) + '\n')
            key[bid] = dict(id=q['id'], answer=q['checked_answer'], why=why(q) or ['随机'])
    print(mc, len(pick), 'must', len(must))
json.dump(key, open(f'{out}/blind_key.json', 'w'), ensure_ascii=False, indent=0)

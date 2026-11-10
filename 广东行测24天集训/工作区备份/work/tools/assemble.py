"""Assemble first-batch package: final IDs, assets, materials, articles, review list, books."""
import json, os, sys, shutil, collections, csv, re
sys.path.insert(0, os.path.dirname(__file__))
from build_books import build_question_book, build_answer_book
OUT = os.environ.get('OUT_DIR', '/home/user/work/out'); MATROOT = '/home/user/work/out'; PKG = sys.argv[1] if len(sys.argv) > 1 else '/home/user/work/build/pkg'
CFG = json.load(open(os.environ.get('CFG_PATH', '/home/user/work/build/assemble_cfg.json')))
def L(a): return [json.loads(l) for l in open(f'{OUT}/{a}/questions.jsonl') if l.strip()]
os.makedirs(PKG + '/assets', exist_ok=True)
def resolve(agent, p):
    for c in (p if os.path.isabs(p) else None, os.path.join(OUT, agent, p), os.path.join(OUT, p)):
        if c and os.path.exists(c): return c
    return None
final, reserve, problems = [], [], []
mats_used = set(); arts = {}
for day, plan in CFG['days'].items():
    for module_code, parts in plan.items():
        n = 0
        for (agent, groups) in parts:
            recs = L(agent)
            excl = set(CFG.get('exclude', {}).get(agent, []))
            for g in groups:
                rs = sorted([r for r in recs if r['group'] == g and r['id'] not in excl], key=lambda r: (r.get('order') or 0, r['id']))
                for r in rs:
                    n += 1
                    fid = f'{day}-{module_code}-{n:03d}'
                    r2 = dict(r); r2['local_id'] = r['id']; r2['id'] = fid; r2['day'] = day; r2['editor'] = agent
                    na = []
                    for p in r.get('assets') or []:
                        src = resolve(agent, p)
                        if not src: problems.append(f'{fid} ({agent} {r["id"]}): missing asset {p}'); continue
                        dst = f'assets/{agent}/{os.path.basename(src)}'
                        os.makedirs(f'{PKG}/assets/{agent}', exist_ok=True); shutil.copy2(src, f'{PKG}/{dst}'); na.append(dst)
                    r2['assets'] = na
                    m = r.get('material_or_article')
                    if module_code == 'ZL' and m: mats_used.add(m)
                    final.append(r2)
# reserve / excluded / conflicts (once per agent)
for agent in sorted({a for plan in CFG['days'].values() for parts in plan.values() for (a, _) in parts}):
    excl = set(CFG.get('exclude', {}).get(agent, [])); rg = set(CFG.get('reserve_groups', {}).get(agent, []))
    for r in L(agent):
        if r['id'] in excl or r['group'] in rg:
            rr = dict(r); rr['editor'] = agent; rr['why_not_in_package'] = CFG.get('why', {}).get(r['id']) or CFG.get('why', {}).get(r['group'], ''); reserve.append(rr)
# materials
mats = {}
for mid in sorted(mats_used):
    mj = f'{MATROOT}/zl_materials/{mid}/material.json'
    if not os.path.exists(mj): problems.append(f'material missing: {mid}'); continue
    m = json.load(open(mj)); na = []
    for p in m.get('assets') or []:
        cand = [os.path.join(MATROOT, p), os.path.join(MATROOT, 'zl_materials', mid, os.path.basename(p))]
        src = next((c for c in cand if os.path.exists(c)), None)
        if not src: problems.append(f'{mid}: missing asset {p}'); continue
        dst = f'assets/materials/{mid}/{os.path.basename(src)}'
        os.makedirs(os.path.dirname(f'{PKG}/{dst}'), exist_ok=True); shutil.copy2(src, f'{PKG}/{dst}'); na.append(dst)
    m['assets'] = na; mats[mid] = m
# articles
for a in [x for x in os.listdir(OUT) if x.startswith('YY') and os.path.exists(f'{OUT}/{x}/articles.jsonl')]:
    for l in open(f'{OUT}/{a}/articles.jsonl'):
        x = json.loads(l)
        if x.get('text') in (None, 'None'): x['text'] = ''
        arts[x['aid']] = x
used_arts = {r['material_or_article'] for r in final if r['module'] == '言语' and r.get('material_or_article')}
arts = {k: v for k, v in arts.items() if k in used_arts}
# write data
with open(f'{PKG}/questions.jsonl', 'w') as fo:
    for r in final: fo.write(json.dumps(r, ensure_ascii=False) + '\n')
with open(f'{PKG}/materials.jsonl', 'w') as fo:
    for m in mats.values(): fo.write(json.dumps(m, ensure_ascii=False) + '\n')
with open(f'{PKG}/articles.jsonl', 'w') as fo:
    for m in arts.values(): fo.write(json.dumps(m, ensure_ascii=False) + '\n')
with open(f'{PKG}/备选与冲突待复核.jsonl', 'w') as fo:
    for r in reserve: fo.write(json.dumps(r, ensure_ascii=False) + '\n')
# books
MOD = {'ZL': '资料', 'PD': '判断', 'YY': '言语'}
INTRO = {'ZL': '专项：做两遍后再核对答案。题号旁为原题来源（卷号·原题号）；材料先读后答。',
         'PD': '专项：图推在前；做两遍后再核对答案。题号旁为原题来源（卷号·原题号）。',
         'YY': '言语：做一遍再看答案原文册。题号旁为原题来源；同一篇文章的题做完再看原文。'}
by = collections.defaultdict(list)
for r in final: by[(r['day'], r['id'].split('-')[1])].append(r)
for (day, mc), recs in sorted(by.items()):
    t = f'{day} {MOD[mc]} {len(recs)} 题'
    open(f'{PKG}/{day}_{MOD[mc]}_题目册.html', 'w').write(build_question_book(recs, mats, arts, PKG, t + '｜题目册', INTRO[mc]))
    if mc == 'YY':
        open(f'{PKG}/{day}_{MOD[mc]}_答案原文册.html', 'w').write(build_answer_book(recs, arts, t + '｜答案与原文册', '只给原参考答案和原文，不附解析；原有争议标记照录。', verbal=True))
    else:
        open(f'{PKG}/{day}_{MOD[mc]}_答案册.html', 'w').write(build_answer_book(recs, arts, t + '｜答案册', '核验后答案＋简短解法；“原答案”与核验一致时不重复列出。'))
cnt = collections.Counter((r['day'], r['id'].split('-')[1]) for r in final)
print(dict(cnt)); print(len(final), 'final', len(reserve), 'reserve/excluded', len(mats), 'materials', len(arts), 'articles')
print('\n'.join(problems[:40]))

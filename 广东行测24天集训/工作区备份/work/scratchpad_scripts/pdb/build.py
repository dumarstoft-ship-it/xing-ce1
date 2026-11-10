import json, sys, re, os
D = '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/pdb'
sys.path.insert(0, D)
from spec import GROUPS, ITEMS, SCAN, SCAN_ANS, VERSION
from repl_spec import REPL, DROPPED, SCAN_NEW, NEW
INV = {v: k for k, v in REPL.items()}
for g_ in GROUPS:
    GROUPS[g_]['order'] = [INV.get(k_, k_) for k_ in GROUPS[g_]['order'] if k_ not in DROPPED]
ITEMS.update(NEW)
for k_, v_ in SCAN_NEW.items():
    SCAN[k_] = v_[:4]; SCAN_ANS[k_] = v_[4]
OLD = {}
for l_ in open(f'{D}/questions_v1_backup.jsonl'):
    r_ = json.loads(l_); OLD[r_['source_key']] = (r_['id'], r_['order'])
P = json.load(open(f'{D}/pool.json')); idx = {(o['pid'], o['qno']): o for o in P}
parsed = json.load(open(f'{D}/parsed.json'))
from parse import parse
import anseg
am = json.load(open(f'{D}/ansmeta.json'))
claims = [json.loads(l) for l in open('/home/user/work/out/claims.jsonl') if l.strip()]
cl = {c['key']: c for c in claims if c['owner'] == 'PD-B'}
# manual text fix
parsed['GD2020X-68']['stem'] = '对于城市街头小摊贩占道经营影响交通的问题,有学者认为应当在不影响城市交通的特定区域设置面向小摊贩的集中营业区,这样就能够缓解小摊贩随意占道经营产生的交通堵塞问题。要使上述论证成立,必须补充的前提是()。'
parsed['GD2020X-68']['options'] = {'A': '集中营业区不会向入驻的小摊贩收取管理费用', 'B': '集中营业区不会产生噪音、环境污染等其它城市问题',
                                   'C': '设置集中营业区后占道经营的小摊贩会前往该处摆设摊位', 'D': '集中营业区的交通位置便利,小摊贩能够在该处获得更高利润'}

from zhnorm import zh
GT = {'B1': 'PD01-B1', 'B2': 'PD01-B2', 'B3': 'PD01-B3', 'BR': 'PD01-BR'}
out = []; n = 0
for g in ['B1', 'B2', 'B3', 'BR']:
    for k in GROUPS[g]['order']:
        fid, order = OLD[REPL.get(k, k)]
        if g != 'BR': n += 1
        pid, q = k.rsplit('-', 1); q = int(q); o = idx[(pid, q)]; it = ITEMS[k]
        pages = sorted({s[0] + 1 for s in o['segs']})
        if k == 'GD2020X-68': pages = [pages[0]]
        if k in SCAN:
            af, ap, rate, yc = SCAN[k]; sa = SCAN_ANS[k]; scan = True
        elif k not in am:
            af = None
            for t_ in [o['tag'], pid, pid + '_xc']:
                if os.path.exists(f'/home/user/work/answers/{t_}.json'): af = json.load(open(f'/home/user/work/answers/{t_}.json'))['file']; break
            r_ = anseg.seg(af, q) if af else None
            if r_:
                rt_ = re.search(r'正确率\s*[:：]?\s*(\d{1,3})\s*%', r_['text']); yc_ = re.search(r'易错项\s*[:：]?\s*([A-H])', r_['text'])
                ap, sa, rate, yc = r_['page'], r_['final'], (int(rt_.group(1)) if rt_ else None), (yc_.group(1) if yc_ else None)
            else:
                af, ap, rate, yc, sa = None, None, None, None, None
            scan = False
        elif k in am:
            af, ap, rate, yc = am[k]['ans_file'], am[k]['ans_page'], am[k]['rate'], am[k]['yicuo']; sa = am[k]['final']; scan = False
        else:
            af, ap, rate, yc, sa, scan = None, None, None, None, None, False
        flags = []
        vn = VERSION.get(pid)
        if pid in ('GD2024', 'GD2026') or (vn and '回忆' in vn): flags.append('网友回忆版')
        if pid == 'GD2026': flags.append('无解析-编者自定答案')
        if k == 'SZ2020SW-75': flags.append('原卷用字疑误(防火烧荒)')
        if k not in parsed:
            st_, op_ = parse(o['text'], q); parsed[k] = dict(stem=st_, options=op_)
        st = zh(parsed[k]['stem']); op = {L: zh(v) for L, v in parsed[k]['options'].items()}
        assert op and all(op[L] for L in 'ABCD'), k
        assert it['ans'] in 'ABCD'
        if sa is not None: assert sa == it['ans'], (k, sa, it['ans'])
        dups = [d for d in cl[k]['dups'] if d != k]
        notes = []
        if dups: notes.append('同题另见：' + '、'.join(dups) + '（claim.py 已一并锁定）')
        if scan: notes.append(f'解析为扫描件，已出图核对第{ap}页原文，答案{sa}')
        elif af: notes.append(f'解析原文核对：第{ap}页“正确答案{sa}”')
        if rate is not None: notes.append(f'解析标注全站正确率{rate}%，易错项{yc}')
        if pid == 'GD2026': notes.append('2026年度广东卷无解析，答案为编者独立推定；无可辩护的第二答案')
        if k == 'GD2020X-68': notes.append('原卷本页题后有“69——75题暂缺”说明，与本题无关，已从题干中剔除')
        if k == 'SZ2020SW-75': notes.append('题干与D项原文均作“防火烧荒”，按文意应为“放火烧荒”，照录原文，答案册已注明')
        if pid == 'GD2026': notes.append('原文页内粉笔水印文字已剔除')
        notes.append('编者难度估计：' + {'E': '易', 'M': '中', 'H': '难'}[it['diff']])
        if REPL.get(k): notes.append(f'11-08 原位替换：原题{REPL[k]}出自用户已做的广东2024—2026卷，换为本题，沿用原编号与组内位置')
        if g == 'BR': notes.append('备选：已核验并登记，因本日论证题已达配额且与组内题训练点部分重合，移作后续判断日备用')
        rec = dict(
            id=fid, module='判断', day='PD01', group=GT[g], group_title=GROUPS[g]['title'], topic=it['topic'], order=order,
            source=dict(paper=pid, file=o['file'], page=pages[0], pages=pages, qno=q, ans_file=af, ans_page=ap, version_note=vn),
            done_status='已做情况未知', stem=st, options=op, material_or_article=None, assets=[],
            source_answer=sa, checked_answer=it['ans'], brief_solution=it['sol'], selection_value=it['val'], variant_of=None,
            check_status='已核验', flags=flags, notes='；'.join(notes),
            source_key=k, source_rate=rate, source_yicuo=yc, difficulty_est=it['diff'], same_item_in=dups, replaced_from=REPL.get(k))
        out.append(rec)
os.makedirs('/home/user/work/out/PD-B', exist_ok=True)
with open('/home/user/work/out/PD-B/questions.jsonl', 'w') as f:
    for r in out: f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(len(out))
import collections
print(collections.Counter(r['group'] for r in out))
print(collections.Counter(r['checked_answer'] for r in out))
for g in ['PD01-B1', 'PD01-B2', 'PD01-B3', 'PD01-BR']:
    print(g, ''.join(r['checked_answer'] for r in out if r['group'] == g), ''.join(r['difficulty_est'] for r in out if r['group'] == g))

# ---------- 冲突待复核（不计入正式包） ----------
from conf_spec import CONF, SCANC, RATES
conf = json.load(open(f'{D}/conf.json'))
cl2 = {c['key']: c for c in [json.loads(l) for l in open('/home/user/work/out/claims.jsonl') if l.strip()] if c['owner'] == 'PD-B'}
xs = []
for i, k in enumerate(['SZ20201-40', 'HB2020-109', 'GD2020X-59', 'GD2020X-66', 'GD2022X-63', 'GK2025F-111', 'GD2022X-64', 'GD2020X-63', 'SD2020-75', 'JS2021A-93'], 1):
    c = conf[k]; s = CONF[k]; pid, q = k.rsplit('-', 1); q = int(q)
    if k in SCANC:
        af, ap, sa, rate, yc = SCANC[k]
    else:
        af, ap, sa = c['ans_file'], c['ans_page'], c['ans']; rate, yc = RATES.get(k, (None, None))
    dups = [d for d in cl2[k]['dups'] if d != k]
    notes = []
    if dups: notes.append('同题另见：' + '、'.join(dups))
    notes.append(('解析为扫描件，已出图核对第%s页' % ap) if k in SCANC else ('解析原文第%s页' % ap))
    if rate is not None: notes.append(f'解析标注全站正确率{rate}%，易错项{yc}')
    notes.append('处理建议：' + s['sug'])
    xs.append(dict(
        id=f'PD-B-X{i:02d}', module='判断', day='PD01', group='PD01-BX', group_title='冲突待复核（不计入正式包）', topic=s['topic'], order=i,
        source=dict(paper=pid, file=c['file'], page=c['page'], pages=c['pages'], qno=q, ans_file=af, ans_page=ap, version_note=VERSION.get(pid)),
        done_status='已做情况未知', stem=zh(c['stem']), options={L: zh(v) for L, v in c['options'].items()}, material_or_article=None, assets=[],
        source_answer=sa, checked_answer=s['lean'], brief_solution=s['sol'], selection_value='低正确率/争议题，复核后才能决定是否入包。',
        variant_of=None, check_status='冲突待复核', flags=s['flags'], notes='；'.join(notes),
        source_key=k, source_rate=rate, source_yicuo=yc, editor_lean=s['lean'], same_item_in=dups, replaced_from=None))
with open('/home/user/work/out/PD-B/questions.jsonl', 'a') as f:
    for r in xs: f.write(json.dumps(r, ensure_ascii=False) + '\n')
print('conflicts', len(xs))

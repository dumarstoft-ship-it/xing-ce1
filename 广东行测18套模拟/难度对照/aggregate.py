"""汇总三人逐题评分：按锚点（GD2025第36—40、71—80题）把两位模拟卷评分人的秒数换算到真题评分人的尺度，
再算每套资料、数学运算的耗时、步数分布、口径坑，与2024—2026年真题平均比较。"""
import json, collections, statistics, sys
from pathlib import Path
D = Path(__file__).resolve().parent
def load(f):
    p = D / f
    return json.load(open(p, encoding='utf-8')) if p.exists() else []
gd, ra, rb = load('GD.json'), load('M01-M04.json'), load('M05-M08.json')
ANCH = set(range(36, 41)) | set(range(71, 81))
def anchor_sum(rows):
    return sum(x['est_seconds'] for x in rows if x.get('paper') == 'GD2025' and x.get('number') in ANCH and 'est_seconds' in x)
base = anchor_sum(gd)
scale = {}
for name, rows in (('A', ra), ('B', rb)):
    s = anchor_sum(rows)
    scale[name] = base / s if s else 1.0
print('锚点合计（秒）：真题评分人', base, '；M01—M04评分人', anchor_sum(ra), '；M05—M08评分人', anchor_sum(rb), '→ 换算系数', {k: round(v, 3) for k, v in scale.items()})
MODES = ['读', '一步', '两步', '三步及以上']
def summarize(rows, paper, k=1.0):
    qs = [x for x in rows if x.get('paper') == paper and 'number' in x]
    mats = [x for x in rows if x.get('paper') == paper and 'group' in x]
    data = [x for x in qs if 71 <= x['number'] <= 90]
    math = [x for x in qs if 36 <= x['number'] <= 45]
    mode = collections.Counter(x['mode'] for x in data)
    mmode = collections.Counter(x['mode'] for x in math)
    comp = [x['options_to_check'] for x in data if x.get('options_to_check')]
    traps = sum(len(x.get('traps') or []) for x in data)
    dsec = k * (sum(x['est_seconds'] for x in data) + sum(x['material_seconds'] for x in mats))
    msec = k * sum(x['est_seconds'] for x in math)
    return {'paper': paper, 'n_data': len(data), 'n_math': len(math), 'data_mode': [mode.get(m, 0) for m in MODES],
            'comp_avg': round(statistics.mean(comp), 1) if comp else None, 'traps': traps,
            'data_min': round(dsec / 60, 1), 'math_mode': [mmode.get(m, 0) for m in MODES], 'math_min': round(msec / 60, 1)}
res = [summarize(gd, p) for p in ('GD2024', 'GD2025', 'GD2026')]
res += [summarize(ra, p, scale['A']) for p in ('M01', 'M02', 'M03', 'M04')]
res += [summarize(rb, p, scale['B']) for p in ('M05', 'M06', 'M07', 'M08')]
real = [r for r in res if r['paper'].startswith('GD')]
rd = statistics.mean(r['data_min'] for r in real); rm = statistics.mean(r['math_min'] for r in real)
print(f"真题平均：资料{rd:.1f}分钟，数学运算{rm:.1f}分钟")
print('卷\t资料题数\t资料 读/一步/两步/三步+\t综合分析平均验项\t口径坑\t资料分钟\t数学 读/一步/两步/三步+\t数学分钟\t比真题多（分钟）')
for r in res:
    extra = (r['data_min'] - rd) + (r['math_min'] - rm)
    print(r['paper'], r['n_data'], '/'.join(map(str, r['data_mode'])), r['comp_avg'], r['traps'], r['data_min'],
          '/'.join(map(str, r['math_mode'])), r['math_min'], f"{extra:+.1f}", sep='\t')
json.dump(res, open(D / 'summary.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

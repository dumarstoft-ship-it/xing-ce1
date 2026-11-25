"""国考地市级卷资料分析核算脚本的公共部分（check_GK2019-2021.py、check_GK2015-2023.py 共用）。

每个核算脚本提供一份配置（cfg，dict）：
  PAPERS     卷名列表；POOL 题池文件；COMPUTE {卷: 返回{题号: 选项}的函数}；
  RATINGS    {卷: {题号: (type, mode, est_seconds, options_to_check, heaviest_option_mode, 依据)}}；
  MATS       {卷: {组: (material_seconds, material_form, region, material_note)}}；
  DRILL_USED {材料id: 集训用过的依据}（只用于提醒，excluded 由 重编/tools/exclusions.py 刷新）；
  ISSUES     {题id: [题目问题]}；MAT_ISSUES {材料id: [材料问题]}（可省）。
run(cfg, argv) 做自检与核算；带 --write-pool 时先按评定重写题池（excluded 保留原值）。
"""
import hashlib
import json
from pathlib import Path

BANK = Path(__file__).resolve().parent.parent          # 国考/资料分析
REPO = BANK.parents[1]
MODES = ('读', '一步', '两步', '三步及以上')


def nearest(x, opts):
    """数值选项：取最接近的一项。"""
    return 'ABCD'[min(range(4), key=lambda i: abs(opts[i] - x))]


def one_true(flags):
    """“能够推出的是”：恰有一项为真。"""
    assert sum(flags) == 1, flags
    return 'ABCD'[flags.index(True)]


def shape(vals):
    """折线形状：相邻升降，以及末点与首点比较。"""
    steps = tuple('+' if b > a else '-' for a, b in zip(vals, vals[1:]))
    return steps + ('末高于首' if vals[-1] > vals[0] else '末低于首',)


def pool_records(cfg):
    out = []
    for p in cfg['PAPERS']:
        recs = [json.loads(l) for l in open(BANK / f'{p}.jsonl', encoding='utf-8')]
        groups = {}
        for r in recs:
            groups.setdefault(r['material']['id'], []).append(r)
        for mid, rs in groups.items():
            ms, form, region, note = cfg['MATS'][p][mid.split('-')[-1]]
            out.append({'paper': p, 'material_id': mid, 'material_seconds': ms, 'questions': [r['id'] for r in rs],
                        'material_form': form, 'region': region, 'material_note': note, 'dup_of': None,
                        'issues': list(cfg.get('MAT_ISSUES', {}).get(mid, [])), 'excluded': None})
            for r in rs:
                n = r['question_number']
                t, mode, est, otc, heavy, _ = cfg['RATINGS'][p][n]
                out.append({'id': r['id'], 'paper': p, 'number': n, 'section': '资料分析', 'part': '资料分析',
                            'material_id': mid, 'dup_of': None, 'type': t, 'mode': mode, 'est_seconds': est,
                            'options_to_check': otc, 'heaviest_option_mode': heavy,
                            'issues': list(cfg['ISSUES'].get(r['id'], [])), 'excluded': None})
    return out


def strip_excluded(recs):
    """excluded 由 重编/tools/exclusions.py 按排除名单刷新，这里不比、不改。"""
    return [{k: v for k, v in r.items() if k != 'excluded'} for r in recs]


def write_pool(cfg):
    pool = cfg['POOL']
    new = pool_records(cfg)
    if pool.exists():                      # 保留 exclusions.py 写入的 excluded
        old = {r.get('id') or r['material_id']: r.get('excluded') for r in json.loads(pool.read_text(encoding='utf-8'))}
        for r in new:
            r['excluded'] = old.get(r.get('id') or r['material_id'])
    pool.write_text(json.dumps(new, ensure_ascii=False, indent=1), encoding='utf-8')
    print('已写', pool.relative_to(REPO))


def check(cfg, verbose=False):
    errors = []
    for p in cfg['PAPERS']:
        recs = [json.loads(l) for l in open(BANK / f'{p}.jsonl', encoding='utf-8')]
        man = {m['id']: m for m in json.loads((BANK / 'assets' / p / 'manifest.json').read_text(encoding='utf-8'))}
        nums = [r['question_number'] for r in recs]
        mats = {r['material']['id'] for r in recs}
        if nums != list(range(111, 131)) or len(mats) != 4:
            errors.append(f'{p}: 题号或材料组数不对')
        calc = cfg['COMPUTE'][p]()
        used_imgs = set()
        for r in recs:
            n = r['question_number']
            a = r['answer']
            if a['status'] != 'known' or len(a['values']) != 1 or len(a['values'][0]) != 1:
                errors.append(f'{r["id"]}: 答案不唯一')
            if len(r['options']) != 4 or [o['label'] for o in r['options']] != list('ABCD'):
                errors.append(f'{r["id"]}: 选项不是四项')
            for o in r['options']:
                if not o['text'] and not o['image_refs']:
                    errors.append(f'{r["id"]}: {o["label"]}项为空')
            if calc[n] != a['values'][0][0]:
                errors.append(f'{r["id"]}: 核算得{calc[n]}，题库答案{a["values"][0][0]}')
            blocks = [b for b in r['material']['content'] if b['type'] == 'image'] + r['figures']
            for b in blocks:
                f = BANK / b['path']
                used_imgs.add(b['image_id'])
                if not f.exists():
                    errors.append(f'{r["id"]}: 缺图 {b["path"]}')
                elif hashlib.sha256(f.read_bytes()).hexdigest() != man[b['image_id']]['sha256']:
                    errors.append(f'{r["id"]}: 图与清单哈希不符 {b["path"]}')
            t, mode, est, otc, heavy, note = cfg['RATINGS'][p][n]
            if mode not in MODES or (heavy and heavy not in MODES) or (t == '综合分析判断') != (otc is not None):
                errors.append(f'{r["id"]}: 评定字段不合规')
            if verbose:
                print(f'{r["id"]}  答案{a["values"][0][0]}  {t}｜{mode}｜{est}s'
                      + (f'｜验{otc}项，最重{heavy}' if otc else '') + f'\n    {note}')
        if used_imgs != set(man):
            errors.append(f'{p}: 清单与题库引用的图片不一致 {sorted(set(man) ^ used_imgs)}')
    pool = cfg['POOL']
    if pool.exists():
        cur = json.loads(pool.read_text(encoding='utf-8'))
        if strip_excluded(cur) != strip_excluded(pool_records(cfg)):
            errors.append('题池文件与本脚本的评定不一致（重新生成：--write-pool，excluded 保留原值）')
        ex = {r.get('id') or r['material_id']: r.get('excluded') for r in cur}
        for mid, why in cfg['DRILL_USED'].items():
            qs = [r['id'] for r in cur if r.get('material_id') == mid and 'id' in r]
            miss = [k for k in [mid] + qs if not ex.get(k)]
            if miss:
                print(f'提醒：{mid} 是集训第2天用过的材料（{why}），题池里未排除：{"、".join(miss)}')
    else:
        errors.append('题池文件不存在（生成：--write-pool）')
    for e in errors:
        print('错误：', e)
    print('核算与自检：', '全部通过' if not errors else f'{len(errors)}处问题')
    return not errors


def run(cfg, argv):
    if '--write-pool' in argv:
        write_pool(cfg)
    return 0 if check(cfg, '-v' in argv) else 1

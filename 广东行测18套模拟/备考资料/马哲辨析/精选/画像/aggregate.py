#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 merged.json 算出 真题画像.json。

用法：python3 aggregate.py
输入：同目录 merged.json（405题的最终归类）；
      ../知识点目录.md（只取知识点的标题、档次和所属模块）；
      ../题库/G*.json（只数各模块有多少知识点、多少道题，缺了也能跑）。
输出：../真题画像.json
所有数字都在这里算，画像文档只引用这里的结果。
"""
import collections
import glob
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MERGED = os.path.join(HERE, 'merged.json')
CATALOG = os.path.join(ROOT, '知识点目录.md')
BANK_GLOB = os.path.join(ROOT, '题库', 'G*.json')
OUT = os.path.join(ROOT, '真题画像.json')

DOMAIN_NAME = {
    'D1': '马哲', 'D2': '党的创新理论', 'D3': '发展战略与经济社会政策', 'D4': '党的建设',
    'D5': '制度、会议与规划', 'D6': '党史与精神谱系', 'D7': '法律', 'D8': '广东',
    'D9': '时政成就与科技时事', 'D10': '经济常识', 'D11': '科技与生活常识', 'D12': '地理与人文', 'D13': '其他',
}
DOMAINS = list(DOMAIN_NAME)
DOMAIN_MODULE = {'D1': '马哲', 'D2': 'P1', 'D3': 'P2', 'D4': 'P3', 'D5': 'P4', 'D6': 'H', 'D7': 'LAW', 'D8': 'GD'}
MODULES = ['马哲', 'P1', 'P2', 'P3', 'P4', 'H', 'LAW', 'GD']
MODULE_NAME = {
    '马哲': '马哲（M1—M7）', 'P1': '新思想概念组与文化', 'P2': '发展理论、产业与生态关系', 'P3': '政绩观、自我革命与党的建设',
    'P4': '中央到省的制度、会议与规划', 'H': '精选党史、著作与改革节点', 'LAW': '法律结构、法典化与新法', 'GD': '2026广东重要事项',
    'M1': '总论与哲学立场', 'M2': '物质、运动、意识与规律', 'M3': '联系、发展与辩证否定', 'M4': '矛盾分析',
    'M5': '五对范畴与思维方法', 'M6': '实践、认识与真理', 'M7': '唯物史观与道德交叉点',
}
M_MODULES = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7']
OUTSIDE = '题库外'
RECENT = (2024, 2025, 2026)
MID = (2022, 2023)
PERIODS = [('2013—2018', range(2013, 2019)), ('2019—2021', range(2019, 2022)), ('2022—2023', range(2022, 2024)), ('2024—2026', range(2024, 2027))]
GROUPS = [('理论（D1+D2）', ['D1', 'D2']), ('政策（D3）', ['D3']), ('党建、制度、党史、法律（D4—D7）', ['D4', 'D5', 'D6', 'D7']),
          ('广东（D8）', ['D8']), ('题库覆盖的八个领域（D1—D8）', ['D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8']),
          ('时政成就（D9）', ['D9']), ('经济、科技、地理人文常识（D10—D12）', ['D10', 'D11', 'D12'])]

# 统一命题位的说明和排列顺序（名字要和 merged.json 里的 slot 一致；新出现的名字会排在最后）
SLOT_DESC = collections.OrderedDict([
    ('马哲判断题', '判断题里的一句马哲表述，主语或属性被替换'),
    ('马哲概念选择题', '围绕一个马哲概念给四个表述逐项辨析，2024年起都是多选'),
    ('马哲材料配原理', '给一段材料、讲话或古语，问体现哪条哲学原理（单选）'),
    ('新思想原话理解', '总书记重要论述、新思想概念的原话和定位句，含五大发展理念配举措'),
    ('六个必须坚持', '给一段原话配“必须坚持××”，或辨析其中一条的内涵'),
    ('古语配观点', '给一个政治观点或要求，选意思最贴近的古语、用典'),
    ('党的路线宗旨', '群众路线、思想路线（实事求是）、基本路线、宗旨'),
    ('中央全会与党代会文件', '最近一次党代会报告、中央全会决定或建议的原话、定位句、名单'),
    ('三农与乡村振兴政策', '中央一号文件、脱贫攻坚、乡村振兴等三农政策表述'),
    ('改革与民生政策', '就业、社保等民生政策，以及商事、放管服、供给侧等改革举措'),
    ('生态双碳与治水政策', '碳达峰碳中和、治水等生态政策的规范表述'),
    ('全国两会与政府工作报告', '当年全国两会的届次日期、国务院政府工作报告的举措'),
    ('五年规划', '五年规划纲要的内容和五年规划（计划）的沿革'),
    ('党章党规', '党章、党内法规条文和干部标准'),
    ('基层自治与治理', '村委会、居委会、乡镇政府的关系和基层治理'),
    ('国家机构与职权', '人大、政府等国家机构的性质、职权和设立'),
    ('广东党史', '发生在广东的党史事件'),
    ('党史著作', '毛泽东著作的出处和主旨'),
    ('党史事件与会议', '党史事件、会议的内容和意义，含用诗词、周年节点引出的题'),
    ('党史时序与时期', '事件排序，或把事件、人物归到四个历史时期'),
    ('精神谱系与英模人物', '英模人物、表彰和精神谱系'),
    ('新施行新修订法律', '上一两年新通过、新施行或新修订的法律'),
    ('宪法与法理常识', '宪法、宪法相关法、立法法和法理'),
    ('部门法常识', '民法、行政法、经济法、社会法等长期有效的条文'),
    ('省高质量发展大会', '当年年初广东省高质量发展大会的原话'),
    ('粤港澳大湾区', '大湾区规划、定位和跨海通道'),
    ('广东省情地理', '广东的地理、气候、物产和岭南文化'),
    ('总书记视察广东讲话', '总书记最近一次到广东视察的讲话要求'),
    ('广东年度部署与新规', '省政府工作报告、省内新政策和地方法规'),
    ('科技工程成就', '当年科技和重大工程成就'),
    ('外交与国际时事', '领导人出访、主场外交和外交理念'),
    ('国内大事与发展成就', '当年国内大事、新设节日和发展成就盘点'),
    ('经济与人口常识', '经济学、金融财税概念和人口国情'),
    ('理化常识', '物理、化学原理'),
    ('生物医学与生活常识', '生物、医学和日常生活常识'),
    ('环境能源与农林常识', '环境、能源和农林常识'),
    ('文史常识', '古代文学、历史、艺术'),
    ('天文地理常识', '天文、气象、地理'),
    ('传统历法节俗', '节气、干支、传统节日'),
])


def r2(x):
    """保留两位小数；整数值写成整数。"""
    x = round(float(x) + 1e-9, 2)
    return int(x) if x == int(x) else x


def pct(part, whole):
    return round(100.0 * part / whole + 1e-9, 1) if whole else 0.0


def unit_module(uid, cat):
    if uid in cat:
        return cat[uid]['module']
    if re.match(r'M\d\.', uid):
        return uid[:2]
    m = re.match(r'(K-)?(P\d|LAW|GD|H|PT)', uid)
    key = m.group(2) if m else '?'
    return {'PT': 'P3'}.get(key, key)


def load_catalog():
    """知识点目录：编号 -> 模块、档次、标题。模块取所在小节的标题（K 开头的卡也按小节归模块）。"""
    cat = collections.OrderedDict()
    if not os.path.exists(CATALOG):
        return cat
    module = None
    for line in open(CATALOG, encoding='utf-8'):
        line = line.strip()
        h = re.match(r'##\s+([A-Z]+\d?)\s', line)   # \s 也匹配全角空格
        if h:
            module = h.group(1)
            continue
        m = re.match(r'- ([A-Z0-9\.\-]+)｜([ABC])｜([^｜]*)｜', line)
        if m:
            cat[m.group(1)] = {'module': module, 'priority': m.group(2), 'title': m.group(3)}
    return cat


def load_bank_sizes(cat):
    """各模块的知识点数（取目录）和题数（取题库文件，每题只算在主知识点所在模块），以及题型、题目来源的分布。"""
    units = collections.Counter(v['module'] for v in cat.values())
    questions = collections.Counter()
    forms = collections.Counter()      # (模块, 题型)
    kinds = collections.Counter()      # (模块, 来源, 题型)
    seen = set()
    for path in sorted(glob.glob(BANK_GLOB)):
        for u in json.load(open(path, encoding='utf-8')).get('units', []):
            for q in u.get('questions', []):
                if q.get('primary') and q['id'] not in seen:
                    seen.add(q['id'])
                    questions[u['module']] += 1
                    forms[(u['module'], q.get('type', ''))] += 1
                    kinds[(u['module'], q.get('kind', ''), q.get('type', ''))] += 1
    return units, questions, forms, kinds


def main():
    rows = json.load(open(MERGED, encoding='utf-8'))
    cat = load_catalog()
    bank_units, bank_questions, bank_forms, bank_kinds = load_bank_sizes(cat)
    uniq = [r for r in rows if not r['same_as']]          # 去掉重复题
    recent = [r for r in uniq if r['year'] in RECENT]
    total_w = sum(r['weight'] for r in uniq)
    assert all(r['weight'] == 0 for r in rows if r['same_as'])

    out = collections.OrderedDict()

    # ---------- meta ----------
    papers = collections.OrderedDict()
    for r in rows:
        p = papers.setdefault(r['paper'], {'year': r['year'], 'exam': r['exam'], 'n_full': 0, 'n': 0})
        p['n_full'] += 1
        p['n'] += 0 if r['same_as'] else 1
    out['meta'] = collections.OrderedDict([
        ('source', 'merged.json'),
        ('n_total', len(rows)), ('n_unique', len(uniq)), ('n_duplicate', len(rows) - len(uniq)),
        ('n_recent', len(recent)),
        ('total_weight', r2(total_w)),
        ('weight_rule', '年份权重：2024—2026年为3，2022—2023年为2，2019—2021年为1，2013—2018年为0.5；选调生卷再乘0.5；重复题记0'),
        ('weight_by_period', collections.OrderedDict(
            (name, {'n': sum(1 for r in uniq if r['year'] in yrs), 'weight': r2(sum(r['weight'] for r in uniq if r['year'] in yrs)),
                    'share': pct(sum(r['weight'] for r in uniq if r['year'] in yrs), total_w)}) for name, yrs in PERIODS)),
        ('domain_name', DOMAIN_NAME), ('domain_module', DOMAIN_MODULE), ('module_name', MODULE_NAME),
        ('note', '题数、占比都已去掉重复题（同年两张卷共用的题只算一次）；n_full 是卷面原有题数。'),
        ('keys', collections.OrderedDict([
            ('by_year_domain', '每张卷各领域的题数：domains 去掉重复题，domains_full 是卷面原样'),
            ('by_year_total', '按年份（省考、选调分开）合计的各领域题数，去重'),
            ('share_all', '全部年份按 weight 加权的各领域占比'),
            ('share_recent', '2024—2026年三张卷各领域的题数和占比'),
            ('share_by_period', '四个时期省考卷各领域的不加权占比，用来看走向'),
            ('share_groups', '把领域并成几组后的加权占比和近三年占比'),
            ('recent_papers', '近三年三张卷逐题的题型、领域、命题位、考点和命中的知识点'),
            ('slots', '每个统一命题位：出现年份、加权次数、近三年次数、直接命中和同位的知识点'),
            ('unit_hits', '被真题直接命中的知识点，按加权次数排序；weak 为弱命中'),
            ('analog_hits', '有同位命中的知识点，按加权次数排序'),
            ('forms', '近三年和2022—2023年的题型×问法×考法分布，以及判断、多选的答案分布'),
            ('coverage', '题库对真题的覆盖：直接命中、只有同位卡、无对应、题库外各多少题'),
            ('module_share', '题库各模块对应的真题占比、题库规模、命中的卡数；mazhe_inner 是马哲七个模块'),
            ('currency', '常青题、当年时政题、新法题在各时期的数量'),
        ])),
    ])

    # ---------- by_year_domain ----------
    byd = []
    for pid, p in papers.items():
        d_n = collections.Counter(r['domain'] for r in uniq if r['paper'] == pid)
        d_full = collections.Counter(r['domain'] for r in rows if r['paper'] == pid)
        t_full = collections.Counter(r['type'] for r in rows if r['paper'] == pid)
        byd.append(collections.OrderedDict([
            ('year', p['year']), ('paper', pid), ('exam', p['exam']), ('n', p['n']), ('n_full', p['n_full']),
            ('domains', {d: d_n[d] for d in DOMAINS if d_n[d]}),
            ('domains_full', {d: d_full[d] for d in DOMAINS if d_full[d]}),
            ('types_full', dict(t_full)),
        ]))
    byd.sort(key=lambda t: (t['year'], t['exam'] != '省考', t['paper']))
    out['by_year_domain'] = byd
    by_year = collections.OrderedDict()
    for y in sorted({r['year'] for r in uniq}):
        for exam in ('省考', '选调生'):
            sub = [r for r in uniq if r['year'] == y and r['exam'] == exam]
            if sub:
                c = collections.Counter(r['domain'] for r in sub)
                by_year['%d%s' % (y, '' if exam == '省考' else '选调')] = collections.OrderedDict(
                    [('n', len(sub)), ('domains', {d: c[d] for d in DOMAINS if c[d]})])
    out['by_year_total'] = by_year

    # ---------- share_all / share_recent / share_by_period ----------
    w_dom = collections.Counter()
    n_dom = collections.Counter()
    for r in uniq:
        w_dom[r['domain']] += r['weight']
        n_dom[r['domain']] += 1
    out['share_all'] = collections.OrderedDict(
        (d, {'name': DOMAIN_NAME[d], 'n': n_dom[d], 'weight': r2(w_dom[d]), 'share': pct(w_dom[d], total_w)}) for d in DOMAINS)
    rc = collections.Counter(r['domain'] for r in recent)
    per_year = {y: collections.Counter(r['domain'] for r in recent if r['year'] == y) for y in RECENT}
    out['share_recent'] = collections.OrderedDict(
        (d, {'name': DOMAIN_NAME[d], 'n': rc[d], 'share': pct(rc[d], len(recent)),
             'by_year': {str(y): per_year[y][d] for y in RECENT}}) for d in DOMAINS)
    sbp = collections.OrderedDict()
    for name, yrs in PERIODS:
        sub = [r for r in uniq if r['year'] in yrs and r['exam'] == '省考']
        c = collections.Counter(r['domain'] for r in sub)
        groups = collections.OrderedDict()
        for gname, ds in GROUPS:
            gn = sum(c[d] for d in ds)
            groups[gname] = {'n': gn, 'share': pct(gn, len(sub))}
        sbp[name] = collections.OrderedDict([('n', len(sub)), ('scope', '省考卷，去重，不加权'),
                                             ('domains', {d: {'n': c[d], 'share': pct(c[d], len(sub))} for d in DOMAINS}),
                                             ('groups', groups)])
    out['share_by_period'] = sbp
    out['share_groups'] = collections.OrderedDict()
    for gname, ds in GROUPS:
        out['share_groups'][gname] = collections.OrderedDict([
            ('domains', ds),
            ('weight', r2(sum(w_dom[d] for d in ds))), ('share_all', pct(sum(w_dom[d] for d in ds), total_w)),
            ('recent_n', sum(rc[d] for d in ds)), ('share_recent', pct(sum(rc[d] for d in ds), len(recent))),
        ])

    # ---------- recent_papers ----------
    rp = collections.OrderedDict()
    for y in RECENT:
        qs = sorted([r for r in uniq if r['year'] == y], key=lambda r: r['number'])
        runs = []
        for r in qs:
            if runs and runs[-1][0] == r['type'] and runs[-1][2] == r['number'] - 1:
                runs[-1][2] = r['number']
            else:
                runs.append([r['type'], r['number'], r['number']])
        rp[str(y)] = collections.OrderedDict([
            ('paper', qs[0]['paper']), ('n', len(qs)),
            ('layout', [{'type': t, 'from': a, 'to': b, 'n': b - a + 1} for t, a, b in runs]),
            ('types', dict(collections.Counter(r['type'] for r in qs))),
            ('sections', dict(collections.Counter(r.get('section', '') for r in qs))),
            ('domains', {d: n for d, n in ((d, sum(1 for r in qs if r['domain'] == d)) for d in DOMAINS) if n}),
            ('questions', [collections.OrderedDict([
                ('number', r['number']), ('id', r['id']), ('type', r['type']), ('section', r.get('section', '')),
                ('domain', r['domain']), ('slot', r['slot']), ('topic', r['topic']), ('ask', r['ask']), ('style', r['style']),
                ('currency', r['currency']), ('units', r['units']), ('weak_units', r.get('weak_units', [])), ('analog_units', r['analog_units']),
            ]) for r in qs]),
        ])
    out['recent_papers'] = rp

    # ---------- slots ----------
    slot_names = [s for s in SLOT_DESC] + sorted({r['slot'] for r in uniq} - set(SLOT_DESC))
    slots = []
    for s in slot_names:
        qs = [r for r in uniq if r['slot'] == s]
        if not qs:
            continue
        by_y = collections.Counter(r['year'] for r in qs)
        rq = sorted([r for r in qs if r['year'] in RECENT], key=lambda r: r['id'])
        mq = sorted([r for r in qs if r['year'] in MID], key=lambda r: r['id'])
        au = collections.Counter()
        au_w = collections.Counter()
        du = collections.Counter()
        du_w = collections.Counter()
        for r in qs:
            for u in r['analog_units']:
                au[u] += 1
                au_w[u] += r['weight']
            for u in r['units']:
                du[u] += 1
                du_w[u] += r['weight']
        dom = collections.Counter(r['domain'] for r in qs)
        slots.append(collections.OrderedDict([
            ('slot', s), ('desc', SLOT_DESC.get(s, '')),
            ('domains', {d: dom[d] for d in DOMAINS if dom[d]}),
            ('main_domain', dom.most_common(1)[0][0]),
            ('n', len(qs)), ('weighted', r2(sum(r['weight'] for r in qs))),
            ('years', sorted(by_y)), ('by_year', {str(y): by_y[y] for y in sorted(by_y)}),
            ('years_shengkao', sorted({r['year'] for r in qs if r['exam'] == '省考'})),
            ('years_xuandiao', sorted({r['year'] for r in qs if r['exam'] != '省考'})),
            ('n_shengkao', sum(1 for r in qs if r['exam'] == '省考')),
            ('mid_n', len(mq)),
            ('recent_n', len(rq)), ('recent_papers_n', len({r['year'] for r in rq})),
            ('recent_ids', [r['id'] for r in rq]),
            ('recent_by_year', {str(y): [r['number'] for r in sorted(rq, key=lambda r: r['number']) if r['year'] == y] for y in RECENT}),
            ('mid_ids', [r['id'] for r in mq]),
            ('types', dict(collections.Counter(r['type'] for r in qs))),
            ('recent_types', dict(collections.Counter(r['type'] for r in rq))),
            ('currency', dict(collections.Counter(r['currency'] for r in qs))),
            ('units', collections.OrderedDict((u, {'n': du[u], 'weighted': r2(du_w[u])}) for u, _ in sorted(du_w.items(), key=lambda t: (-t[1], t[0])))),
            ('analog_units', collections.OrderedDict((u, {'n': au[u], 'weighted': r2(au_w[u])}) for u, _ in sorted(au_w.items(), key=lambda t: (-t[1], t[0])))),
            ('ids', [r['id'] for r in sorted(qs, key=lambda r: r['id'])]),
        ]))
    out['slots'] = slots

    # ---------- unit_hits / analog_hits ----------
    def hit_table(field):
        tab = collections.OrderedDict()
        for r in uniq:
            for u in r[field]:
                weak = field == 'units' and u in r.get('weak_units', [])
                tab.setdefault(u, []).append(collections.OrderedDict(
                    [('id', r['id']), ('year', r['year']), ('weight', r['weight'])] + ([('weak', weak)] if field == 'units' else [])))
        res = []
        for u, hits in tab.items():
            hits.sort(key=lambda h: (-h['year'], h['id']))
            item = collections.OrderedDict([
                ('unit', u), ('module', unit_module(u, cat)), ('priority', cat.get(u, {}).get('priority', '')),
                ('title', cat.get(u, {}).get('title', '')),
                ('n', len(hits)), ('weighted', r2(sum(h['weight'] for h in hits))),
            ])
            if field == 'units':
                item['n_weak'] = sum(1 for h in hits if h['weak'])
                item['weighted_strong'] = r2(sum(h['weight'] for h in hits if not h['weak']))
            item['recent_n'] = sum(1 for h in hits if h['year'] in RECENT)
            item['years'] = sorted({h['year'] for h in hits})
            item['hits'] = hits
            res.append(item)
        res.sort(key=lambda t: (-t['weighted'], -t['recent_n'], t['unit']))
        for k, item in enumerate(res, 1):
            item['rank'] = k
        return res
    unit_hits = hit_table('units')
    analog_hits = hit_table('analog_units')
    out['unit_hits_summary'] = collections.OrderedDict([
        ('bank_units', len(cat)),
        ('units_direct_hit', len(unit_hits)), ('units_direct_hit_recent', sum(1 for h in unit_hits if h['recent_n'])),
        ('units_direct_hit_strong', sum(1 for h in unit_hits if h['weighted_strong'] > 0)),
        ('units_only_weak', [h['unit'] for h in unit_hits if h['weighted_strong'] == 0]),
        ('units_analog_hit', len(analog_hits)), ('units_analog_hit_recent', sum(1 for h in analog_hits if h['recent_n'])),
        ('units_any_hit', len({h['unit'] for h in unit_hits} | {h['unit'] for h in analog_hits})),
        ('hit_pairs', sum(h['n'] for h in unit_hits)), ('weak_pairs', sum(h['n_weak'] for h in unit_hits)),
        ('note', 'weak=True 的命中是“同一知识点，但题眼不在卡的陈述里”，weighted_strong 不计这些。'),
    ])
    out['unit_hits'] = unit_hits
    out['analog_hits'] = analog_hits

    # ---------- forms ----------
    def forms(sub):
        combos = collections.OrderedDict()
        for r in sub:
            combos.setdefault((r['type'], r['ask'], r['style']), []).append(r['id'])
        res = collections.OrderedDict([
            ('n', len(sub)),
            ('by_type', dict(collections.Counter(r['type'] for r in sub))),
            ('by_ask', dict(collections.Counter(r['ask'] for r in sub))),
            ('by_style', dict(collections.Counter(r['style'] for r in sub).most_common())),
            ('by_type_ask', {'%s/%s' % k: v for k, v in sorted(collections.Counter((r['type'], r['ask']) for r in sub).items())}),
            ('by_type_style', {'%s/%s' % k: v for k, v in sorted(collections.Counter((r['type'], r['style']) for r in sub).items(), key=lambda t: (t[0][0], -t[1]))}),
            ('by_currency', dict(collections.Counter(r['currency'] for r in sub))),
            ('combos', [collections.OrderedDict([('type', k[0]), ('ask', k[1]), ('style', k[2]), ('n', len(v)), ('share', pct(len(v), len(sub))), ('ids', sorted(v))])
                        for k, v in sorted(combos.items(), key=lambda t: (-len(t[1]), t[0]))]),
        ])
        judge = [r for r in sub if r['type'] == '判断']
        multi = [r for r in sub if r['type'] == '多选']
        res['judge_answers'] = dict(collections.Counter(r['my_answer'] for r in judge))
        res['judge_wrong_ids'] = sorted(r['id'] for r in judge if r['my_answer'] == '错误')
        res['judge_domains'] = dict(collections.Counter(r['domain'] for r in judge))
        res['judge_slots'] = dict(collections.Counter(r['slot'] for r in judge).most_common())
        res['judge_by_year'] = {str(y): dict(collections.Counter(r['my_answer'] for r in judge if r['year'] == y)) for y in sorted({r['year'] for r in judge})}
        res['multi_slots'] = dict(collections.Counter(r['slot'] for r in multi).most_common())
        res['multi_answer_len'] = {str(k): v for k, v in sorted(collections.Counter(len(r['my_answer']) for r in multi).items())}
        res['multi_domains'] = dict(collections.Counter(r['domain'] for r in multi))
        res['single_domains'] = dict(collections.Counter(r['domain'] for r in sub if r['type'] == '单选'))
        return res
    out['forms'] = collections.OrderedDict([
        ('2024-2026', forms(recent)),
        ('2022-2023', forms([r for r in uniq if r['year'] in MID])),
        ('note', '判断题、多选题的答案取归类人作答（my_answer）；2026年卷仓库里没有官方答案。'),
    ])

    # ---------- coverage：题库对真题的覆盖 ----------
    def coverage(sub, weighted):
        cls = collections.OrderedDict((k, []) for k in ['直接命中', '只有弱命中', '只有同位卡', '同领域但题库无对应', '题库外领域'])
        for r in sub:
            strong = [u for u in r['units'] if u not in r.get('weak_units', [])]
            if strong:
                k = '直接命中'
            elif r['units']:
                k = '只有弱命中'
            elif r['domain'] not in DOMAIN_MODULE:
                k = '题库外领域'
            elif r['analog_units']:
                k = '只有同位卡'
            else:
                k = '同领域但题库无对应'
            cls[k].append(r)
        tot_n, tot_w = len(sub), sum(r['weight'] for r in sub)
        res = collections.OrderedDict()
        for k, v in cls.items():
            w = sum(r['weight'] for r in v)
            item = collections.OrderedDict([('n', len(v)), ('share', pct(len(v), tot_n)), ('weight', r2(w)), ('weight_share', pct(w, tot_w))])
            if not weighted:
                item['ids'] = sorted(r['id'] for r in v)
            if k == '题库外领域':
                item['outside_with_analog'] = sum(1 for r in v if r['analog_units'])
            res[k] = item
        return res
    out['coverage'] = collections.OrderedDict([
        ('2024-2026', coverage(recent, False)),
        ('2022-2023', coverage([r for r in uniq if r['year'] in MID], False)),
        ('all_weighted', coverage(uniq, True)),
        ('note', '每题只归一类：有直接命中的先归直接命中（全是弱命中的单列）；其余的，D9以后的归题库外领域（其中有同位卡的另记在 outside_with_analog），'
                 'D1—D8 的有同位卡归“只有同位卡”，没有的归“同领域但题库无对应”。题库是做过近三年真题之后整理的，近三年的直接命中有事后补卡的成分。'),
    ])

    # ---------- module_share ----------
    def mod_of(r):
        return DOMAIN_MODULE.get(r['domain'], OUTSIDE)
    mw = collections.Counter()
    mn = collections.Counter()
    mrec = collections.Counter()
    for r in uniq:
        mw[mod_of(r)] += r['weight']
        mn[mod_of(r)] += 1
        if r['year'] in RECENT:
            mrec[mod_of(r)] += 1
    in_bank_w = sum(mw[m] for m in MODULES)
    in_bank_rec = sum(mrec[m] for m in MODULES)
    tot_bank_units = sum(bank_units.values())
    tot_bank_q = sum(bank_questions.values())

    def bank_of(m):
        mods = M_MODULES if m == '马哲' else [m]
        return sum(bank_units[x] for x in mods), sum(bank_questions[x] for x in mods)

    hit_by_mod = collections.defaultdict(lambda: {'units_hit': 0, 'units_hit_strong': 0, 'weighted': 0.0, 'recent_units_hit': 0})
    for h in unit_hits:
        d = hit_by_mod[h['module']]
        d['units_hit'] += 1
        d['units_hit_strong'] += 1 if h['weighted_strong'] > 0 else 0
        d['weighted'] += h['weighted']
        d['recent_units_hit'] += 1 if h['recent_n'] else 0
    ana_by_mod = collections.defaultdict(lambda: {'units_hit': 0, 'weighted': 0.0})
    for h in analog_hits:
        ana_by_mod[h['module']]['units_hit'] += 1
        ana_by_mod[h['module']]['weighted'] += h['weighted']
    any_hit_units = {h['unit'] for h in unit_hits} | {h['unit'] for h in analog_hits}

    def touched(mods):
        return sum(1 for u in any_hit_units if unit_module(u, cat) in mods)

    # 换一个角度：不看题目归在哪个领域，看它直接命中的卡属于哪个模块（一道题命中几张卡就平分）
    hm_recent = collections.Counter()
    hm_all = collections.Counter()
    for r in uniq:
        if not r['units']:
            continue
        for u in r['units']:
            mod = unit_module(u, cat)
            mod = '马哲' if mod in M_MODULES else mod
            hm_all[mod] += r['weight'] / len(r['units'])
            if r['year'] in RECENT:
                hm_recent[mod] += 1.0 / len(r['units'])

    modules = collections.OrderedDict()
    for m in MODULES + [OUTSIDE]:
        item = collections.OrderedDict([
            ('name', MODULE_NAME.get(m, '题库外（D9—D13）')),
            ('n', mn[m]), ('weight', r2(mw[m])), ('share_all', pct(mw[m], total_w)),
            ('share_all_in_bank', pct(mw[m], in_bank_w) if m != OUTSIDE else None),
            ('recent_n', mrec[m]), ('share_recent', pct(mrec[m], len(recent))),
            ('share_recent_in_bank', pct(mrec[m], in_bank_rec) if m != OUTSIDE else None),
        ])
        if m != OUTSIDE:
            bu, bq = bank_of(m)
            mods = M_MODULES if m == '马哲' else [m]
            item['bank_units'] = bu
            item['bank_units_share'] = pct(bu, tot_bank_units)
            item['bank_questions'] = bq
            item['bank_questions_share'] = pct(bq, tot_bank_q)
            item['units_direct_hit'] = sum(hit_by_mod[x]['units_hit'] for x in mods)
            item['units_direct_hit_recent'] = sum(hit_by_mod[x]['recent_units_hit'] for x in mods)
            item['units_analog_hit'] = sum(ana_by_mod[x]['units_hit'] for x in mods)
            item['units_any_hit'] = touched(mods)
            item['units_never_hit'] = bu - item['units_any_hit']
            item['never_hit_units'] = [u for u, v in cat.items() if v['module'] in mods and u not in any_hit_units]
            item['recent_questions_hitting_cards'] = r2(hm_recent[m])
            item['recent_questions_hitting_cards_share'] = pct(hm_recent[m], len(recent))
            item['weight_hitting_cards'] = r2(hm_all[m])
            item['weight_hitting_cards_share'] = pct(hm_all[m], total_w)
        modules[m] = item

    # 马哲内部：按 unit_hits 里命中的 M 卡分。一道题命中几张 M 卡，就把这道题的权重平分给这几张卡，保证每道题只算一次。
    frac_all = collections.Counter()      # 任何领域的题命中 M 卡
    frac_d1 = collections.Counter()       # 只算 D1 的题
    frac_recent = collections.Counter()   # 近三年，按题数（不加权）
    for r in uniq:
        ms = [u for u in r['units'] if re.match(r'M\d\.', u)]
        if not ms:
            continue
        for u in ms:
            frac_all[u[:2]] += r['weight'] / len(ms)
            if r['domain'] == 'D1':
                frac_d1[u[:2]] += r['weight'] / len(ms)
            if r['year'] in RECENT:
                frac_recent[u[:2]] += 1.0 / len(ms)
    tot_all, tot_d1, tot_rec = sum(frac_all.values()), sum(frac_d1.values()), sum(frac_recent.values())
    inner = collections.OrderedDict()
    for m in M_MODULES:
        cards = [h for h in unit_hits if h['module'] == m]
        inner[m] = collections.OrderedDict([
            ('name', MODULE_NAME[m]),
            ('bank_units', bank_units[m]), ('bank_questions', bank_questions[m]),
            ('bank_questions_share_of_mazhe', pct(bank_questions[m], sum(bank_questions[x] for x in M_MODULES))),
            ('units_hit', len(cards)), ('units_hit_recent', sum(1 for h in cards if h['recent_n'])),
            ('hit_weighted_sum', r2(sum(h['weighted'] for h in cards))),
            ('hit_units', [h['unit'] for h in cards]),
            ('hit_ids', sorted({x['id'] for h in cards for x in h['hits']})),
            ('recent_hit_ids', sorted({x['id'] for h in cards for x in h['hits'] if x['year'] in RECENT})),
            ('weight_split', r2(frac_all[m])), ('split_share', pct(frac_all[m], tot_all)),
            ('share_all', round(modules['马哲']['share_all'] * frac_all[m] / tot_all + 1e-9, 1) if tot_all else 0.0),
            ('d1_only_split_share', pct(frac_d1[m], tot_d1)),
            ('recent_split', r2(frac_recent[m])), ('recent_split_share', pct(frac_recent[m], tot_rec)),
        ])
    out['module_share'] = collections.OrderedDict([
        ('modules', modules),
        ('bank_total', {'units': tot_bank_units, 'questions': tot_bank_q}),
        ('bank_types', collections.OrderedDict(
            (m, {t: sum(v for (mm, tt), v in bank_forms.items() if tt == t and (mm in M_MODULES if m == '马哲' else mm == m)) for t in ('判断', '单选', '多选')})
            for m in MODULES)),
        ('bank_mazhe_kinds', collections.OrderedDict(
            (k, {t: sum(v for (mm, kk, tt), v in bank_kinds.items() if mm in M_MODULES and kk == k and tt == t) for t in ('判断', '单选', '多选')})
            for k in sorted({kk for (mm, kk, tt) in bank_kinds if mm in M_MODULES}))),
        ('recent_types_by_module', collections.OrderedDict(
            (m, dict(collections.Counter(r['type'] for r in recent if mod_of(r) == m))) for m in MODULES + [OUTSIDE])),
        ('mazhe_inner', inner),
        ('mazhe_inner_note', 'weight_split：命中 M 卡的每道题把自己的权重平分给它命中的几张 M 卡，再按模块相加（含 D2、D7 里命中 M 卡的题）；'
                             'split_share 是各模块占这个总数的比例；share_all = 马哲在全部真题中的加权占比 × split_share；'
                             'd1_only_split_share 只算归在 D1 的题；recent_split 是近三年按题数（不加权）的同样算法。'),
        ('mazhe_hit_weight_total', r2(tot_all)), ('mazhe_recent_hit_questions', r2(tot_rec)),
    ])

    # ---------- currency ----------
    cur = collections.OrderedDict()
    for name, sub in [('2024-2026', recent), ('2022-2023', [r for r in uniq if r['year'] in MID]), ('2019-2021', [r for r in uniq if 2019 <= r['year'] <= 2021]), ('2013-2018', [r for r in uniq if r['year'] <= 2018])]:
        c = collections.Counter(r['currency'] for r in sub)
        cur[name] = collections.OrderedDict([('n', len(sub))] + [(k, {'n': c[k], 'share': pct(c[k], len(sub))}) for k in ['常青', '当年时政', '近年新法新政']])
    c2 = collections.Counter((r['domain'], r['currency']) for r in recent)
    cur['2024-2026_by_domain'] = {d: {k: c2[(d, k)] for k in ['常青', '当年时政', '近年新法新政'] if c2[(d, k)]} for d in DOMAINS if any(c2[(d, k)] for k in ['常青', '当年时政', '近年新法新政'])}
    out['currency'] = cur

    json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('写出', OUT)
    print('题数 %d，去重后 %d，近三年 %d，总权重 %s' % (len(rows), len(uniq), len(recent), r2(total_w)))
    print('命题位 %d 个；直接命中的知识点 %d 个；同位命中的知识点 %d 个' % (len(slots), len(unit_hits), len(analog_hits)))


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""Build YY2A deliverables (round 2: 言语 D04-D06 选词填空 + 语句填空) -> questions.jsonl, articles.jsonl, checks.txt.
Adapted from the round-1 YY-A script (/home/user/work/out/YY-A/src/build.py). Read-only on all sources:
  - GD items: gd_items2.py (transcribed from page images; answers read from the analysis pages)
  - HTML items: the user's HTML (script#data JSON), blanks/answers taken from the source data and re-checked here.
Run: python3 build2.py   (writes into /home/user/work/out2/YY2A/)"""
import json, re, sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gd_items2 import GD

OUT = '/home/user/work/out2/YY2A'
PREFIX = 'YY2A'
HTML_FILE = 'xing-ce1/学习资料/盖句精读（词句新版·全151篇·手机版）(2).html'
R1_GD = '/home/user/work/out/YY-A/src'          # round-1 GD items (for the cross-round repeat check only)


def _load_html():
    raw = open('/home/user/' + HTML_FILE, encoding='utf-8').read()
    m = re.search(r'<script id="data" type="application/json">(.*?)</script>', raw, re.S)
    return json.loads(m.group(1))


D = _load_html()
ART = {a['id']: a for a in D}
R1_ARTICLES = {'20260128_30136235', '20260908_30179764', 'nf20260304_10164275',
               '20260106_30129738', '20251202_30117958', '20260522_30158429'}


def ptext(para):
    return ''.join(sg.get('t', sg.get('m', '')) for sg in para)


# ---- HTML plan: day -> [(article id, {qid: [extra context paragraph numbers]})]; every article is used whole (no skipped question).
PLAN = {
    'D04': [('20260928_30183385', {'q1': [], 'q2': [], 'q3': [], 'q4': [], 'q5': [], 'q6': [], 'q7': []}),
            ('20260731_30172375', {'q1': [], 'q2': [], 'q3': [], 'q4': [], 'q5': []}),
            ('nf20260930_10182667', {'q1': [], 'q2': [], 'q3': [], 'q4': []})],
    'D05': [('nf20260515_10170502', {'q1': [], 'q2': [], 'q3': []}),
            ('20260313_30145108', {'q1': [], 'q2': [], 'q3': [], 'q4': [], 'q5': [], 'q6': []}),
            ('20260819_30175817', {'q1': [], 'q2': [], 'q3': [], 'q4': [], 'q5': []})],
    'D06': [('nf20251215_10156656', {'q1': [], 'q2': [], 'q3': [], 'q4': [], 'q5': [], 'q6': []}),
            ('20260728_30171396', {'q1': [], 'q2': [], 'q3': [], 'q4': [], 'q5': []}),
            ('20260302_30142983', {'q1': [], 'q2': [], 'q3': [], 'q4': []})],
}
SKIPPED = {}

HTML_VALUE = {
 # D04 ① 人民日报·思想纵横 2026-09-28《从“摸象”与“称象”中悟方法》
 ('20260928_30183385', 'q1'): '人民日报思想纵横2026-09-28；单句成段的成语填空，“往往能＿”的程度与“方法”的搭配（四个成语原站称与2021国考副省级第21题同组）',
 ('20260928_30183385', 'q2'): '同篇；句中引语须同时兜住“大处着眼”与“精准落子”两头，干扰项各只有一头',
 ('20260928_30183385', 'q3'): '同篇；“单打独斗”的反面，四个合作类成语分主动/被动、合力/并行',
 ('20260928_30183385', 'q4'): '同篇；双空“不是…而是…”的反向对照，空后还要搭“统筹兼顾”“各美其美”类语义',
 ('20260928_30183385', 'q5'): '同篇；“一村一策”的反面是哪种工作毛病，四个都是常见批评用语',
 ('20260928_30183385', 'q6'): '同篇；段尾“有同志感悟”的长句，须同时对上“系统”与“精准”两层，四项句式相同',
 ('20260928_30183385', 'q7'): '同篇；“大×大×”四个熟语，按对举的另一半（只见树木不见森林）和后句“重精细”定位',
 # D04 ② 人民日报·人民时评 2026-07-31《“冷门”“热门”辩证看》
 ('20260731_30172375', 'q1'): '人民日报人民时评2026-07-31；段中承上启下句，主语须是本段段首所说的“需求”，干扰项取自同篇其他几段的论点',
 ('20260731_30172375', 'q2'): '同篇；比喻名词（格子间/象牙塔/独木桥/小圈子），须对上“彼此隔绝”的“彼此”',
 ('20260731_30172375', 'q3'): '同篇；“以往…不为外人所知。而今…”今昔对照的后半句',
 ('20260731_30172375', 'q4'): '同篇；“没有A，便没有B”条件句的双成语，字面最工整的一组不是答案',
 ('20260731_30172375', 'q5'): '同篇；篇末落点句，须同时承接“国家需要”和“个人”两头',
 # D04 ③ 南方日报·评论 2026-09-30《让平安之花在南粤大地灼灼绽放》
 ('nf20260930_10182667', 'q1'): '南方日报评论2026-09-30（平安广东）；“对…＿”的成语与介词搭配，并与后句“亲自擘画”一心一行成对',
 ('nf20260930_10182667', 'q2'): '同篇；“××性××性”四字组合，须对上“容易诱发”“见事早”',
 ('nf20260930_10182667', 'q3'): '同篇；治理模式“转型”的方向词，“惩/防”两手与“标本兼治”给出线索',
 ('nf20260930_10182667', 'q4'): '同篇；三个“是”层层推进的末项，须换角度且回扣段尾“营造良好环境”',
 # D05 ① 南方日报·评论 2026-05-15《以良法善治保障广东走在前列》
 ('nf20260515_10170502', 'q1'): '南方日报评论2026-05-15（法治广东）；段首引语定调，四句都谈“法与治”；与同日GD2023X-21（段首名句）同类，可对照',
 ('nf20260515_10170502', 'q2'): '同篇；三个“把握”与其后展开内容对号入座的排序题',
 ('nf20260515_10170502', 'q3'): '同篇；立法成果的定语，须对上“找准…所需…重点”',
 # D05 ② 人民日报·思想纵横 2026-08-19《决策如何做到科学合理》
 ('20260819_30175817', 'q1'): '人民日报思想纵横2026-08-19；例子的落点句，须回扣前文原则“还湖于民”',
 ('20260819_30175817', 'q2'): '同篇；“重…轻…”格式对应的成语，四个都是“做法错了”类成语',
 ('20260819_30175817', 'q3'): '同篇；“只有＿，决策才能…”的条件，须分别收住前面两个“需要”',
 ('20260819_30175817', 'q4'): '同篇；领起“钉钉子的坚守功”的引语，与“法与时转则治”等名句的取舍',
 ('20260819_30175817', 'q5'): '同篇；“＿责任追究制度”，线索在同句后半“无论岗位调整、职务离任”',
 # D05 ③ 人民日报·人民时评 2026-03-13《变压器为何热销海外》
 ('20260313_30145108', 'q1'): '人民日报人民时评2026-03-13；“同台竞技…稳居第一”的成语，“顺势而为”被句首“风口之下”勾出',
 ('20260313_30145108', 'q2'): '同篇；“从…到…”列举后的形容词，“庞大”被紧跟的“产能约占全球60%”勾出',
 ('20260313_30145108', 'q3'): '同篇；“不能＿”须由下一句“配套…产业链供应链”反推',
 ('20260313_30145108', 'q4'): '同篇；例子后的概括句，四项句式相近，只能看与“需求→研制”的先后是否一致',
 ('20260313_30145108', 'q5'): '同篇；引语里的口语化比喻，须对上外商后半句的解释',
 ('20260313_30145108', 'q6'): '同篇；分号两半主语性质相反（现成场景/复杂环境），对调项最迷惑',
 # D06 ① 南方日报·理论周刊 2025-12-15《加强干部队伍建设 选优配强领导班子》
 ('nf20251215_10156656', 'q1'): '南方日报理论周刊2025-12-15（广东干部队伍建设）；“不是抽象的，而是＿”的两个形容词，第二个要看前后两处党史线索',
 ('nf20251215_10156656', 'q2'): '同篇；“易得风气之先，也易＿”一正一反的成语，“腹背受敌”最像',
 ('nf20251215_10156656', 'q3'): '同篇；“亲清统一”给双空分工，干扰项各坏一半',
 ('nf20251215_10156656', 'q4'): '同篇；段首总起句，须罩住本段“全局”与“长远”两层，干扰项是下一段的话',
 ('nf20251215_10156656', 'q5'): '同篇；工作方法类比喻（弹钢琴/牵牛鼻子/钉钉子/摸着石头过河），按“统筹兼顾、综合平衡”定位',
 ('nf20251215_10156656', 'q6'): '同篇；“必须有＿作保障”，按空后的容错纠错机制定位，干扰项是同部分前两段的话',
 # D06 ② 人民日报·评论员观察 2026-07-28《既见“绿树”也见“人”》
 ('20260728_30171396', 'q1'): '人民日报评论员观察2026-07-28（生态与民生）；两项举措与后面两个“避免”逐一对应',
 ('20260728_30171396', 'q2'): '同篇；法治原则的表述，须同时罩住“核心保护区”的严格要求与“原有居民”的例外',
 ('20260728_30171396', 'q3'): '同篇；今昔对比“穷在深山”的反面，“脱贫致富”是条件反射式干扰',
 ('20260728_30171396', 'q4'): '同篇；段尾收束的名句，四项都与“青山/金山”相关，须看与前文“守”与“用”的关系',
 ('20260728_30171396', 'q5'): '同篇；双横线名句填空（均出《桃花源记》），按“山水美景”“人间烟火”两个中心语对号',
 # D06 ③ 人民日报·人民时评 2026-03-02《读懂AI红包大战》
 ('20260302_30142983', 'q1'): '人民日报人民时评2026-03-02；“不在于…而在于…”后半句，须接住紧随其后的“借此”和“同样”',
 ('20260302_30142983', 'q2'): '同篇；空前给原因、空后给结果的经济术语（使用/学习/迁移/获客成本）',
 ('20260302_30142983', 'q3'): '同篇；冒号后列举“有的…有的…”之前的成语，“殊途同归”抢了下一句的话',
 ('20260302_30142983', 'q4'): '同篇；“表面看…实质…”对举，空在表面一侧',
}

EXTRA_NOTES = {
 ('20260928_30183385', 'q2'): '【跨轮重复】本题答案“致广大而尽精微”与第1轮 D03-YY-035（HTML 20251202_30117958:q5，篇末引语）的答案相同，选项组不同；用户可能凭记忆选中，本题照常保留（同篇7题整体使用，原文公开后此题无法单独留存）。',
 ('20260313_30145108', 'q1'): '【跨轮重复】本题答案“脱颖而出”与第1轮 D01-YY-001（GD2023Z-2）的答案相同，选项组不同（本题干扰项为顺势而为/崭露头角/逆势而上）；照常保留。',
 ('nf20260515_10170502', 'q1'): '【编排】原站解析称“广东卷常在段首放引语（2023年第21题、2024年第24题）”，故同日 D05-GY 放 GD2023X-21（段首名句）作对照；只在编排上体现，不写解析。',
}
GD_EXTRA_NOTES = {
 ('GD2021X', 2): '【数据】GD2021X（县级卷）是扫描件，不在共享 index/qindex，claim.py 无法自动联锁同题：GD2021X-3＝GD2021Z-5，GD2021X-8＝GD2021Z-9（第1轮已用，已手工补登 claim）。本题 GD2021X-2 与乡镇卷无同题。',
 ('GD2023X', 21): '【编排】同日 D05-H1 南方日报篇 q1 也是段首引语题，原站解析点名过本题（2023年第21题）。',
 ('GD2019X', 8): '【编排】GD2019X-4（如火如荼）与本题同出新华网大湾区纪实一文，GD2021X-1 答案也是“如火如荼”（大湾区题材）；后续若用这两题，建议不与本题同日或相邻日。',
}

BL = '______'          # 选词 blank
LL = '____________'    # 语句 blank
OTHER = '______（另题）'


def masked_para(a, pno, target_q, sel_qids):
    """Paragraph pno (1-based) with target blanks -> BL/LL, other selected blanks -> OTHER."""
    t = ptext(a['paras'][pno - 1])
    spans = []
    for q in a['q']:
        if q['p'] != pno or q['id'] not in sel_qids:
            continue
        for b in q['blanks']:
            if target_q is not None and q['id'] == target_q['id']:
                spans.append((b['b'], b['e'], LL if q['kind'] == '语句填空' else BL))
            else:
                spans.append((b['b'], b['e'], OTHER))
    spans.sort(key=lambda x: -x[0])
    for i in range(len(spans) - 1):
        assert spans[i + 1][1] <= spans[i][0], ('overlap', a['id'], pno)
    for b, e, rep in spans:
        t = t[:b] + rep + t[e:]
    return t


def html_prompt(q, has_other):
    multi = len(q['blanks']) > 1
    if q['kind'] == '语句填空':
        s = '依次填入画横线部分最恰当的一项是（　　）。' if multi else '填入画横线部分最恰当的一句是（　　）。'
    else:
        s = '依次填入画横线部分最恰当的一项是（　　）。' if multi else '填入画横线部分最恰当的一项是（　　）。'
    if has_other:
        s += '（标“另题”的横线属同篇另一题，本题不作答）'
    return s


def restored_text_html(a):
    head = [f"《{a['title']}》",
            '｜'.join(x for x in [a['src'], a['col'], a['date'], a['page'], a['author']] if x),
            f"链接：{a['url']}", '']
    paras = [ptext(p) for p in a['paras']]
    return '\n'.join(head + paras), paras


TOK = re.compile(r'_{6,}|（\s*）')


def gd_restore(item):
    s = item['stem']
    toks = TOK.findall(s)
    assert len(toks) == len(item['fills']), (item['paper'], item['qno'], toks, item['fills'])
    out = s
    for f in item['fills']:
        m = TOK.search(out)
        out = out[:m.start()] + f + out[m.end():]
    return out


def answer_texts(q):
    """List of answer strings (one per blank) for the leak / repeat checks."""
    return q['_fills']


def main():
    os.makedirs(OUT, exist_ok=True)
    questions, articles = [], []
    n = 0

    def nid():
        nonlocal n
        n += 1
        return f'{PREFIX}-{n:03d}'

    for day in ['D04', 'D05', 'D06']:
        # ---- GD groups: GX (选词, 按年份由近及远), GY (语句)
        gd_x = sorted([g for g in GD if g['day'] == day and g['topic'] == '选词填空'], key=lambda g: g['pos'])
        gd_y = sorted([g for g in GD if g['day'] == day and g['topic'] == '语句填空'], key=lambda g: g['pos'])
        for grp in (gd_x, gd_y):
            assert [g['pos'] for g in grp] == list(range(1, len(grp) + 1)), (day, [g['pos'] for g in grp])
        yrs = [int(g['paper'][2:6]) for g in gd_x]
        assert yrs == sorted(yrs, reverse=True), (day, 'GX title says 按年份由近及远', yrs)
        for grp_items, gname, gtitle in [(gd_x, f'{day}-GX', '广东真题·选词填空（按年份由近及远）'),
                                         (gd_y, f'{day}-GY', '广东真题·语句填空')]:
            for order, it in enumerate(grp_items, 1):
                aid = f"ART-GD-{it['paper']}-{it['qno']}"
                restored = gd_restore(it)
                stem = it['stem'] + (('\n' + it['prompt']) if it['prompt'] else '')
                yr = int(it['paper'][2:6])
                ans_letter = it['answer']
                ans_opt = it['options']['ABCD'.index(ans_letter)]
                assert ' '.join(it['fills']) == ans_opt, (it['paper'], it['qno'], it['fills'], ans_opt)
                q = dict(
                    id=nid(), module='言语', day=day, official_day=day, group=gname, group_title=gtitle,
                    topic=it['topic'], order=order,
                    source=dict(paper=it['paper'], file=it['file'], page=it['page'], qno=it['qno'],
                                ans_file=it['ans_file'], ans_page=it['ans_page'], version_note=it['version_note']),
                    done_status='已做情况未知', stem=stem,
                    options={k: v for k, v in zip('ABCD', it['options'])},
                    material_or_article=aid, assets=[],
                    source_answer=ans_letter, checked_answer=ans_letter, brief_solution='',
                    selection_value=it['value'], variant_of=None, check_status='已核验',
                    flags=list(it['flags']),
                    notes=('言语只做数据完整性与原文对应检查：题面已对原卷页图逐字核对，答案取自解析第%s页（%s）。' % (
                        it['ans_page'], '扫描件，出图目读' if yr <= 2021 else '文字层，并与 answers/%s.json 一致' % it['paper'])
                           + (f"解析载全站正确率{it['rate']}、易错项{it['yicuo']}。" if it.get('rate') else '解析未载正确率。')
                           + (f"解析所载文段出处：{it['chuchu']}。" if it.get('chuchu') else '解析未载文段出处。')
                           + '原文为据参考答案回填的恢复文段，非外部原文；外部原文' + ('待补（有出处、无正文）。' if it.get('chuchu') else '无出处可查。')
                           + GD_EXTRA_NOTES.get((it['paper'], it['qno']), '')),
                    source_rate=it.get('rate'), source_yicuo=it.get('yicuo'), source_passage_title=it.get('chuchu'),
                    claim_key=f"{it['paper']}-{it['qno']}",
                    _fills=list(it['fills']),
                )
                questions.append(q)
                articles.append(dict(
                    aid=aid, kind='restored_from_answer', kind_cn='按参考答案回填的文段（非外部原文）',
                    source=dict(paper=it['paper'], file=it['file'], page=it['page'], qno=it['qno'],
                                ans_file=it['ans_file'], ans_page=it['ans_page'], passage_title_per_analysis=it.get('chuchu')),
                    title=it.get('chuchu'),
                    text=restored,
                    external_original=dict(status='待补' if it.get('chuchu') else '无出处',
                                           title_per_analysis=it.get('chuchu'), text=None),
                    note='非外部原文：以原卷参考答案（%s）回填空格得到的恢复文段。%s' % (
                        ans_letter, (f"解析所载文段出处：{it['chuchu']}；外部原文待补（本会话网络不能访问报刊原站，未抓取正文）。"
                                     if it.get('chuchu') else '解析未载文段出处，外部原文无从查找。'))))
        # ---- HTML article groups
        for hidx, (aid_src, qmap) in enumerate(PLAN[day], 1):
            a = ART[aid_src]
            assert aid_src not in R1_ARTICLES, aid_src
            gname = f'{day}-H{hidx}'
            gtitle = f"一文多题：{a['src']}·{a['col']} {a['date']}（原文待本组做完再看）"
            sel = set(qmap.keys())
            assert sel == {q['id'] for q in a['q']} or all((aid_src, k) in SKIPPED for k in {q['id'] for q in a['q']} - sel), aid_src
            aid = f'ART-HTML-{aid_src}'
            order = 0
            for q in a['q']:
                if q['id'] not in sel:
                    continue
                order += 1
                pnos = sorted(set([q['p']] + qmap[q['id']]))
                parts = [masked_para(a, pn, q if pn == q['p'] else None, sel) for pn in pnos]
                passage = '\n'.join(parts)
                has_other = OTHER in passage
                stem = passage + '\n' + html_prompt(q, has_other)
                letter = 'ABCD'[q['answer']]
                t = ptext(a['paras'][q['p'] - 1])
                fills = [t[b['b']:b['e']] for b in q['blanks']]
                got = ' '.join(fills)
                assert got == q['options'][q['answer']], (aid_src, q['id'], got)       # integrity: blank text == answer option
                ctx_desc = '仅本段' if len(pnos) == 1 else ('本段＋' + '、'.join(f'第{x}段' for x in pnos if x != q['p']))
                qq = dict(
                    id=nid(), module='言语', day=day, official_day=day, group=gname, group_title=gtitle,
                    topic=q['kind'], order=order,
                    source=dict(paper='HTML盖句精读', file=HTML_FILE, page=None, qno=f"{aid_src}:{q['id']}",
                                ans_file=HTML_FILE, ans_page=None,
                                version_note=f"HTML 内嵌 JSON（script#data）文章 {aid_src} 的 q 列表 {q['id']}；空在第{q['p']}段，字符位置 " +
                                             '；'.join(f"{b['b']}–{b['e']}" for b in q['blanks']),
                                article_id=aid_src, para=q['p'], blanks=q['blanks'], context_paras=pnos),
                    done_status='已做情况未知', stem=stem,
                    options={k: v for k, v in zip('ABCD', q['options'])},
                    material_or_article=aid, assets=[],
                    source_answer=letter, checked_answer=letter, brief_solution='',
                    selection_value=HTML_VALUE[(aid_src, q['id'])], variant_of=None, check_status='已核验',
                    flags=(['多空'] if len(q['blanks']) > 1 else []) + (['同段另题遮蔽'] if has_other else []),
                    notes=('言语只做数据完整性与原文对应检查：已用程序核对该段拼接原文在空缺位置的文字＝选项%s（%s）。题干上下文：%s，原文照录未改写；同段其他入选题的空缺以“（另题）”遮蔽。原文 %s 须待本组各题做完再看。原站解析存于 source_note（原始备份，不进训练答案册）。' % (
                        letter, q['options'][q['answer']], ctx_desc, aid)) + EXTRA_NOTES.get((aid_src, q['id']), ''),
                    source_note=q['note'],
                    claim_key=f"HTML:{aid_src}:{q['id']}",
                    _fills=fills,
                )
                questions.append(qq)
            text, paras = restored_text_html(a)
            skipped = [k[1] for k in SKIPPED if k[0] == aid_src]
            articles.append(dict(
                aid=aid, kind='html_original', kind_cn='用户HTML源数据还原的原文',
                source=dict(file=HTML_FILE, html_article_id=aid_src, src=a['src'], col=a['col'], date=a['date'],
                            page=a['page'], author=a['author'], url=a['url'], group=a['gname']),
                title=a['title'], text=text, paras=paras,
                external_original=dict(status='未核实', url=a['url'],
                                       why='本会话网络不能访问报刊原站（paper.people.com.cn、epaper.southcn.com 经代理均返回 403），未与外部原文逐字比对'),
                note=('据用户 HTML 源数据（paras 中 t/m 片段按序拼接）还原的原文段落，未改写；各题空缺处的原文用词即在段中。未与报刊原站逐字比对。'
                      f"本篇入选题：{'、'.join(sorted(sel, key=lambda x: int(x[1:])))}" +
                      (f"；未入选：{'、'.join(skipped)}" if skipped else '；本篇全部题目均入选') +
                      '。原文须待本篇各题做完后再看。原站解析（note）不随原文展示。')))

    # ---------------- checks ----------------
    log = []
    # (1) leak check: no answer string of a question appears in any EARLIER stem of the same day
    by_day = collections.defaultdict(list)
    for q in questions:
        by_day[q['day']].append(q)
    leaks = []
    for day, qs in by_day.items():
        for i, q in enumerate(qs):
            for f in answer_texts(q):
                for p in qs[:i]:
                    if f in p['stem']:
                        leaks.append((day, q['id'], f, 'earlier stem', p['id']))
                # long sentence answers: also look for any 8-char piece
                if len(f) >= 10:
                    for p in qs[:i]:
                        for k in range(len(f) - 7):
                            piece = f[k:k + 8]
                            if piece in p['stem']:
                                leaks.append((day, q['id'], piece, 'earlier stem (8-char piece)', p['id']))
                                break
    log.append(f'[leak] answers found in earlier stems of the same day: {len(leaks)}')
    for x in leaks:
        log.append('   ' + repr(x))
    # (1b) later stems that contain an earlier answer (allowed; listed for information)
    later = []
    for day, qs in by_day.items():
        for i, q in enumerate(qs):
            for f in answer_texts(q):
                if len(f) < 2:
                    continue
                for p in qs[i + 1:]:
                    if f in p['stem']:
                        later.append((day, q['id'], f, 'appears later in', p['id']))
    log.append(f'[info] earlier answers that reappear in LATER stems (not a leak): {len(later)}')
    for x in later:
        log.append('   ' + repr(x))
    # (2) own stem contains its answer outside the blank
    own = []
    for q in questions:
        for f in answer_texts(q):
            if len(f) >= 2 and f in q['stem']:
                own.append((q['id'], f))
    log.append(f'[info] answer text also visible elsewhere in its own stem: {len(own)}')
    for x in own:
        log.append('   ' + repr(x))
    # (3) cross-round repeats: answer strings already used as answers in round 1 (YY-A)
    sys.path.insert(0, R1_GD)
    import importlib
    r1 = importlib.import_module('gd_items')
    r1_ans = {}
    for it in r1.GD:
        for f in it['fills']:
            r1_ans.setdefault(f, []).append(f"GD:{it['paper']}-{it['qno']}")
    for aid_src in R1_ARTICLES:
        a = ART[aid_src]
        for q in a['q']:
            t = ptext(a['paras'][q['p'] - 1])
            for b in q['blanks']:
                r1_ans.setdefault(t[b['b']:b['e']], []).append(f"HTML:{aid_src}:{q['id']}")
    rep = []
    for q in questions:
        for f in answer_texts(q):
            if f in r1_ans:
                rep.append((q['id'], f, r1_ans[f]))
    log.append(f'[info] answers identical to a round-1 (D01-D03) answer: {len(rep)}')
    for x in rep:
        log.append('   ' + repr(x))
    # (4) answer-letter distribution
    c = collections.Counter((q['day'], q['checked_answer']) for q in questions)
    for day in ['D04', 'D05', 'D06']:
        log.append(f"[dist] {day}: " + ' '.join(f"{k}={c[(day, k)]}" for k in 'ABCD'))
    log.append('[dist] all: ' + ' '.join(f"{k}={sum(c[(d, k)] for d in ['D04', 'D05', 'D06'])}" for k in 'ABCD'))
    # (5) counts
    cnt = collections.Counter((q['day'], q['topic'], 'GD' if q['source']['paper'].startswith('GD') else 'HTML') for q in questions)
    for k in sorted(cnt):
        log.append(f'[count] {k} {cnt[k]}')
    log.append(f'[count] questions {len(questions)} articles {len(articles)}')

    for q in questions:
        q['answer_text'] = q.pop('_fills')      # blank-by-blank answer text (for downstream leak checks; not shown in books)
    with open(f'{OUT}/questions.jsonl', 'w') as f:
        for q in questions:
            f.write(json.dumps(q, ensure_ascii=False) + '\n')
    with open(f'{OUT}/articles.jsonl', 'w') as f:
        for a in articles:
            f.write(json.dumps(a, ensure_ascii=False) + '\n')
    open(f'{OUT}/checks.txt', 'w').write('\n'.join(log) + '\n')
    print('\n'.join(log))


if __name__ == '__main__':
    main()

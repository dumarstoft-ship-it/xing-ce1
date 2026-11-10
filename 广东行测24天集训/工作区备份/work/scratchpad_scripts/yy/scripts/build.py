# -*- coding: utf-8 -*-
"""Build YY-A deliverables (questions.jsonl, articles.jsonl) for YY01-YY03.
Run with: python3 -I build.py  (paths absolute)."""
import json, re, sys, os, copy
sys.path.insert(0, '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/yy/scripts')
from gd_items import GD

OUT = '/home/user/work/out/YY-A'
HTML_FILE = 'xing-ce1/学习资料/盖句精读（词句新版·全151篇·手机版）(2).html'
D = json.load(open('/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/yy/html_data.json'))
ART = {a['id']: a for a in D}
OFFICIAL = {'YY01': 'D01', 'YY02': 'D02', 'YY03': 'D03'}

def ptext(para):
    return ''.join(sg.get('t', sg.get('m', '')) for sg in para)

# ---- HTML plan: article -> {qid: [extra context paragraph numbers]} (1-based paragraph numbers, document order) ----
PLAN = {
    'YY01': [('20260128_30136235', {'q1': [], 'q2': [], 'q3': [], 'q4': [], 'q5': []}),
             ('20260908_30179764', {'q1': [], 'q2': [], 'q3': [], 'q4': [], 'q5': [], 'q6': []})],
    'YY02': [('nf20260304_10164275', {'q1': [], 'q2': [], 'q3': [], 'q4': [], 'q5': []}),
             ('20260106_30129738', {'q1': [], 'q2': [], 'q3': [], 'q4': [], 'q5': []})],
    'YY03': [('20251202_30117958', {'q1': [2], 'q2': [9], 'q3': [12], 'q4': [], 'q5': [14]}),
             ('20260522_30158429', {'q1': [], 'q2': [6], 'q3': [], 'q4': [], 'q5': []})],
}
SKIPPED = {('20260522_30158429', 'q6'): '需全文主旨（“前瞻性”）才能在B/C间定夺，本段及前后一段不足以作答；原文随本篇原文公开，已登记为“未入题·勿再用”'}

HTML_VALUE = {
 ('20260128_30136235', 'q1'): '人民日报思想纵横2026-01-28；成语分寸（整治刚开展时能说到哪一步），与同日GD2025-17同属“程度分寸”',
 ('20260128_30136235', 'q2'): '同篇；领导人原话填空，干扰项为同一作者同话题名言，对应广东语句题的引语考法',
 ('20260128_30136235', 'q3'): '同篇；三类原因并列、其一待概括，须与同段另两类区分',
 ('20260128_30136235', 'q4'): '同篇；分类论述的收尾句，须回扣段落话题',
 ('20260128_30136235', 'q5'): '同篇；“想清楚＿”的宾语，四项都像动笔前该想的事，考与题旨同向',
 ('20260908_30179764', 'q1'): '人民日报人民时评2026-09-08；让步—转折结构中“让”的一句',
 ('20260908_30179764', 'q2'): '同篇；“不是…而是…”反向对照选成语',
 ('20260908_30179764', 'q3'): '同篇；普通动词挖空，靠后文转折锁定分寸',
 ('20260908_30179764', 'q4'): '同篇；冒号后须从引文提取的“误区”，干扰项都是真实误区',
 ('20260908_30179764', 'q5'): '同篇；成语与“从容铺陈”的语义协调',
 ('20260908_30179764', 'q6'): '同篇；“×化”类动词与宾语“能力”的搭配',
 ('nf20260304_10164275', 'q1'): '南方日报评论2026-03-04（大湾区）；三项排比逐项对应，与同日GD2025-16同一路数',
 ('nf20260304_10164275', 'q2'): '同篇；小词承载前后对照',
 ('nf20260304_10164275', 'q3'): '同篇；例子后概括句的分寸（进行时还是完成时）',
 ('nf20260304_10164275', 'q4'): '同篇；“而在会场外”的对照决定落点',
 ('nf20260304_10164275', 'q5'): '同篇；南方日报对句开段，可与同日GD2024-18“潮涌湾区，＿”对照',
 ('20260106_30129738', 'q1'): '人民日报金台随笔2026-01-06；例子与后文之间的过渡句',
 ('20260106_30129738', 'q2'): '同篇；成语的适用对象与尺度',
 ('20260106_30129738', 'q3'): '同篇；诗句填空须同时满足多项条件，对应广东卷名句填空',
 ('20260106_30129738', 'q4'): '同篇；双空，分别受下句反面与“不仅…更…”递进管辖',
 ('20260106_30129738', 'q5'): '同篇；层递骨架中的转身句，四项句式相同只能凭内容',
 ('20251202_30117958', 'q1'): '人民日报人民时评2025-12-02（减贫）；主语与成语语义叠用的陷阱',
 ('20251202_30117958', 'q2'): '同篇；例子与论点之间的连接句',
 ('20251202_30117958', 'q3'): '同篇；由个人推到群体的承接句，干扰项取自同篇别节',
 ('20251202_30117958', 'q4'): '同篇；四个作风熟语，须按所修饰的中心语逐个衡量',
 ('20251202_30117958', 'q5'): '同篇；篇末引语，可与同日GD2022X-7句中引语对照',
 ('20260522_30158429', 'q1'): '人民日报人民时评2026-05-22；“早”的论证换来的结果怎么说',
 ('20260522_30158429', 'q2'): '同篇；例子中承接上段论点的职责表述，需带上段作答',
 ('20260522_30158429', 'q3'): '同篇；双空分受“立足当前/着眼未来”管辖的“×之×”',
 ('20260522_30158429', 'q4'): '同篇；“不是…而是…”中的换道与同道追赶',
 ('20260522_30158429', 'q5'): '同篇；破局办法须对上“外部智力”与离岸、飞地',
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
    # no overlaps expected
    for i in range(len(spans) - 1):
        assert spans[i + 1][1] <= spans[i][0], ('overlap', a['id'], pno)
    for b, e, rep in spans:
        t = t[:b] + rep + t[e:]
    return t

def html_prompt(q, has_other):
    if q['kind'] == '语句填空':
        s = '填入画横线部分最恰当的一句是（　　）。'
    elif len(q['blanks']) > 1:
        s = '依次填入画横线部分最恰当的一项是（　　）。'
    else:
        s = '填入画横线部分最恰当的一项是（　　）。'
    if has_other:
        s += '（标“另题”的横线属同篇另一题，本题不作答）'
    return s

def restored_text_html(a):
    head = [f"《{a['title']}》",
            '｜'.join(x for x in [a['src'], a['col'], a['date'], a['page'], a['author']] if x),
            f"链接：{a['url']}", '']
    paras = [ptext(p) for p in a['paras']]
    return '\n'.join(head + paras), paras

def gd_restore(item):
    s = item['stem']
    toks = re.findall(r'_{6,}|（\s*）', s)
    assert len(toks) == len(item['fills']), (item['paper'], item['qno'], toks, item['fills'])
    out = s
    for f in item['fills']:
        m = re.search(r'_{6,}|（\s*）', out)
        out = out[:m.start()] + f + out[m.end():]
    return out

def main():
    os.makedirs(OUT, exist_ok=True)
    questions, articles = [], []
    n = 0
    def nid():
        nonlocal n
        n += 1
        return f'YY-A-{n:03d}'
    for day in ['YY01', 'YY02', 'YY03']:
        gidx = 0
        # ---- GD 选词 group
        yr = lambda g: (-int(g['paper'][2:6]), g['paper'], g['qno'])
        gd_x = sorted([g for g in GD if g['day'] == day and g['topic'] == '选词填空'], key=yr)
        gd_y = [g for g in GD if g['day'] == day and g['topic'] == '语句填空']
        for grp_items, gtitle in [(gd_x, '广东真题·选词填空（按年份由近及远）'), (gd_y, '广东真题·语句填空')]:
            gidx += 1
            gname = f'{day}-G{gidx}'
            for order, it in enumerate(grp_items, 1):
                aid = f"ART-GD-{it['paper']}-{it['qno']}"
                restored = gd_restore(it)
                stem = it['stem'] + (('\n' + it['prompt']) if it['prompt'] else '')
                flags = list(it['flags'])
                q = dict(
                    id=nid(), module='言语', day=day, official_day=OFFICIAL[day], group=gname, group_title=gtitle,
                    topic=it['topic'], order=order,
                    source=dict(paper=it['paper'], file=it['file'], page=it['page'], qno=it['qno'],
                                ans_file=it['ans_file'], ans_page=it['ans_page'], version_note=it['version_note']),
                    done_status='已做情况未知', stem=stem,
                    options={k: v for k, v in zip('ABCD', it['options'])},
                    material_or_article=aid, assets=[],
                    source_answer=it['answer'], checked_answer=it['answer'], brief_solution='',
                    selection_value=it['value'], variant_of=None, check_status='已核验',
                    flags=flags,
                    notes=('言语只做数据完整性与原文对应检查：题面已对原卷页图逐字核对，答案取自解析第%s页（%s）。' % (
                        it['ans_page'], '扫描件，出图目读' if int(it['paper'][2:6]) <= 2021 else '文字层')
                           + (f"解析载全站正确率{it['rate']}、易错项{it['yicuo']}。" if it.get('rate') else '')
                           + (f"解析所载文段出处：{it['chuchu']}。" if it.get('chuchu') else '解析未载文段出处。')
                           + '原文为据参考答案回填的恢复文段，非外部原文。'),
                    source_rate=it.get('rate'), source_yicuo=it.get('yicuo'), source_passage_title=it.get('chuchu'),
                    claim_key=f"{it['paper']}-{it['qno']}",
                )
                questions.append(q)
                articles.append(dict(
                    aid=aid, kind='restored_from_answer',
                    source=dict(paper=it['paper'], file=it['file'], page=it['page'], qno=it['qno'],
                                ans_file=it['ans_file'], ans_page=it['ans_page'], passage_title_per_analysis=it.get('chuchu')),
                    title=it.get('chuchu'),
                    text=restored,
                    note='非外部原文：以原卷参考答案（%s）回填空格得到的恢复文段。%s未检索外部原文。' % (
                        it['answer'], (f"解析所载文段出处：{it['chuchu']}；" if it.get('chuchu') else '解析未载文段出处；'))))
        # ---- HTML article groups
        for aid_src, qmap in PLAN[day]:
            a = ART[aid_src]
            gidx += 1
            gname = f'{day}-G{gidx}'
            gtitle = f"一文多题：{a['src']}·{a['col']} {a['date']}（原文待本组做完再看）"
            sel = set(qmap.keys())
            aid = f'ART-HTML-{aid_src}'
            order = 0
            for q in a['q']:
                if q['id'] not in sel:
                    continue
                order += 1
                pnos = sorted(set([q['p']] + qmap[q['id']]))
                parts = []
                for pn in pnos:
                    parts.append(masked_para(a, pn, q if pn == q['p'] else None, sel))
                passage = '\n'.join(parts)
                has_other = OTHER in passage
                stem = passage + '\n' + html_prompt(q, has_other)
                letter = 'ABCD'[q['answer']]
                ctx_desc = '仅本段' if len(pnos) == 1 else ('本段＋' + '、'.join(f'第{x}段' for x in pnos if x != q['p']))
                qq = dict(
                    id=nid(), module='言语', day=day, official_day=OFFICIAL[day], group=gname, group_title=gtitle,
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
                    notes=('言语只做数据完整性与原文对应检查：已用程序核对该段拼接原文在空缺位置的文字＝选项%s（%s）。题干上下文：%s，原文照录未改写；同段/上下文中本组其他题的空缺以“（另题）”遮蔽。原文 %s 须待本组各题做完再看。原站解析存于 source_note（原始备份，不进训练答案册）。' % (
                        letter, q['options'][q['answer']], ctx_desc, aid)),
                    source_note=q['note'],
                    claim_key=f"HTML:{aid_src}:{q['id']}",
                )
                # integrity: blank text == answer option
                t = ptext(a['paras'][q['p'] - 1])
                got = ' '.join(t[b['b']:b['e']] for b in q['blanks'])
                assert got == q['options'][q['answer']], (aid_src, q['id'], got)
                questions.append(qq)
            text, paras = restored_text_html(a)
            skipped = [k[1] for k in SKIPPED if k[0] == aid_src]
            articles.append(dict(
                aid=aid, kind='html_original',
                source=dict(file=HTML_FILE, html_article_id=aid_src, src=a['src'], col=a['col'], date=a['date'],
                            page=a['page'], author=a['author'], url=a['url'], group=a['gname']),
                title=a['title'], text=text, paras=paras,
                note=('据 HTML 源数据（paras 中 t/m 片段按序拼接）还原的原文段落，未改写；空缺处即原文。'
                      f"本篇入选题：{'、'.join(sorted(sel, key=lambda x: int(x[1:])))}" +
                      (f"；未入选：{'、'.join(skipped)}（{SKIPPED[(aid_src, skipped[0])]}）" if skipped else '；本篇全部题目均入选') +
                      '。原文须待本篇各题做完后再看。原站解析（note）不随原文展示。')))
    with open(f'{OUT}/questions.jsonl', 'w') as f:
        for q in questions:
            f.write(json.dumps(q, ensure_ascii=False) + '\n')
    with open(f'{OUT}/articles.jsonl', 'w') as f:
        for a in articles:
            f.write(json.dumps(a, ensure_ascii=False) + '\n')
    # summary
    import collections
    c = collections.Counter((q['day'], q['topic'], 'GD' if q['source']['paper'].startswith('GD') else 'HTML') for q in questions)
    for k in sorted(c):
        print(k, c[k])
    print('questions', len(questions), 'articles', len(articles))

if __name__ == '__main__':
    main()

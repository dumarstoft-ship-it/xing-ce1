# -*- coding: utf-8 -*-
"""Build YY3A deliverables (round 3: 言语 D07-D09 选词填空 + 语句填空) -> questions.jsonl, articles.jsonl, checks.txt.
Adapted from the round-2 YY2A script (/home/user/work/out2/YY2A/src/build2.py). Read-only on all sources:
  - GD items: gd_items3.py (transcribed from page images; answers read from the analysis pages)
  - HTML items: the user's HTML (script#data JSON); blanks/answers taken from the source data and re-checked here
    (the text at every blank position of the re-assembled paragraph must equal the reference-answer option).
Run: python3 build3.py   (writes into /home/user/work/out3/YY3A/)"""
import json, re, sys, os, collections, importlib.util
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gd_items3 import GD

OUT = '/home/user/work/out3/YY3A'
PREFIX = 'YY3A'
DAYS = ['D07', 'D08', 'D09']
HTML_FILE = 'xing-ce1/学习资料/盖句精读（词句新版·全151篇·手机版）(2).html'
R1_SRC = '/home/user/work/out/YY-A/src/gd_items.py'          # round-1 GD items (repeat check only)
R2_SRC = '/home/user/work/out2/YY2A/src/gd_items2.py'        # round-2 GD items (repeat check only)


def _load_html():
    raw = open('/home/user/' + HTML_FILE, encoding='utf-8').read()
    m = re.search(r'<script id="data" type="application/json">(.*?)</script>', raw, re.S)
    return json.loads(m.group(1))


D = _load_html()
ART = {a['id']: a for a in D}
R1_ARTICLES = {'20260128_30136235', '20260908_30179764', 'nf20260304_10164275',
               '20260106_30129738', '20251202_30117958', '20260522_30158429'}
R2_ARTICLES = {'20260928_30183385', '20260731_30172375', 'nf20260930_10182667',
               'nf20260515_10170502', '20260313_30145108', '20260819_30175817',
               'nf20251215_10156656', '20260728_30171396', '20260302_30142983'}


def ptext(para):
    return ''.join(sg.get('t', sg.get('m', '')) for sg in para)


# ---- HTML plan: day -> [(article id, {qid: [extra context paragraph numbers]})]; every article is used whole (no skipped question).
# Context paragraphs are added only where the cue the question relies on sits outside the blank's own paragraph, and only
# when that paragraph carries no answer of a LATER question of the same day (checked below).
PLAN = {
    'D07': [('nf20260831_10180091', {'q1': [], 'q2': [], 'q3': [], 'q4': [], 'q5': [], 'q6': []}),
            ('20251225_30127104', {'q1': [], 'q2': [5], 'q3': [], 'q4': []}),
            ('20260901_30178420', {'q1': [], 'q2': [], 'q3': [], 'q4': [], 'q5': []})],
    'D08': [('nf20260506_10169594', {'q1': [], 'q2': [], 'q3': [], 'q4': [], 'q5': [], 'q6': [], 'q7': []}),
            ('20260813_30174634', {'q1': [], 'q2': [12], 'q3': [], 'q4': []}),
            ('20260917_30181544', {'q1': [], 'q2': [], 'q3': [], 'q4': [], 'q5': []})],
    'D09': [('nf20251208_10155869', {'q1': [], 'q2': [], 'q3': [], 'q4': []}),
            ('20260609_30161950', {'q1': [], 'q2': [], 'q3': [9], 'q4': [], 'q5': []}),
            ('20260428_30153667', {'q1': [], 'q2': [], 'q3': [7], 'q4': [], 'q5': []})],
}
SKIPPED = {}

HTML_VALUE = {
 # D07 ① 南方日报·理论周刊·知行 2026-08-31《从旅游大省迈向高水平旅游强省》
 ('nf20260831_10180091', 'q1'): '南方日报理论周刊2026-08-31（广东旅游强省）；“加快建设……＿”的判断语，四个都是给一项工作下断语的四字格，要与空前所摆的“第一梯队”这一理由同向',
 ('nf20260831_10180091', 'q2'): '同篇；例子（一部电影带热汕头入境游）后的收口句，须回到前句“国际特色旅游城市”这一档，A把档次抬高，B把例子拔高',
 ('nf20260831_10180091', 'q3'): '同篇；“＿式观光”与后文“沉浸式体验”相对，四个成语都带浅、快、窄之意，要选说“看”的那一个',
 ('nf20260831_10180091', 'q4'): '同篇；段首总起句，要为后文“打破城乡二元结构”“城乡融合发展”提出话题，干扰项或讲旅游本身、或只讲乡村一头',
 ('nf20260831_10180091', 'q5'): '同篇；与“民生产业”并列的产业定位词，下一句“惠民、富民、便民”里的“富民”是现成陷阱',
 ('nf20260831_10180091', 'q6'): '同篇；“实现长效＿”的比喻词，同句的“政策倾斜和资金投入”本身就是“输血”，手段与目的要分清',
 # D07 ② 人民日报·人民时评 2025-12-25《抓创新就是要“不问出身”》
 ('20251225_30127104', 'q1'): '人民日报人民时评2025-12-25（广州下放职称评审权）；带引号的机制名，须读进前面的“下放职称评审权”，A前半与答案一字不差、后半“逐级审批”与“下放”相矛盾',
 ('20251225_30127104', 'q2'): '同篇；粤语说法“饮头啖汤”与“吃定心丸”“搭顺风车”“开小灶”四个熟语比喻的辨析；题干加上一段（q1空缺以“另题”遮蔽），交代广州先行先试的改革',
 ('20251225_30127104', 'q3'): '同篇；“但”后的一句与紧跟的“与自然界……不同，小草有可能长成大树”一正一反，四项都像自然界的道理',
 ('20251225_30127104', 'q4'): '同篇；“日益成为科技创新的＿”的分寸，“事实上”推翻传统看法，同段“百花竞秀”管住“主导力量”',
 # D07 ③ 人民日报·金台随笔 2026-09-01《“红梅”为何别样红》
 ('20260901_30178420', 'q1'): '人民日报金台随笔2026-09-01（工业遗存活化）；“观察……的一个生动＿”，“生动缩影”是高频惯性搭配，要看动词“观察”',
 ('20260901_30178420', 'q2'): '同篇；“不只是消费场所，还是社区的＿”，冒号后的市集、读书会、闲坐、嬉戏是对空格的解释',
 ('20260901_30178420', 'q3'): '同篇；段中设问句，前接“价值转换和精神承接”，后接“历史与现实的对话桥梁”，干扰项多是同篇别段的论点',
 ('20260901_30178420', 'q4'): '同篇；“通过口述史、老物件展陈……让历史＿”，要的是做法带来的效果，“可歌可泣”“可圈可点”只是对历史的评价',
 ('20260901_30178420', 'q5'): '同篇；段首引语，四句古诗文都能谈新与旧，须对上段尾“形态各异，但内核相通……文脉绵延强根魂”',
 # D08 ① 南方日报·理论周刊·新论 2026-05-06《以“五个更加注重”谱写 广东海洋经济高质量发展新篇章》
 ('nf20260506_10169594', 'q1'): '南方日报理论周刊2026-05-06（广东海洋经济）；转折前是一串规模数字、转折后是“自主创新能力仍有待提升”，“外强中干”分寸过重',
 ('nf20260506_10169594', 'q2'): '同篇；“在欧美设立研发中心，＿引进海外人才”，人才不必迁来的引进方式；“定向”与上句“靶向”重复',
 ('nf20260506_10169594', 'q3'): '同篇；“推进海域＿设权”，后半句“水面、水体、海床、底土”与“不同开发主体在同一海域”给出线索，“平面分区”最像',
 ('nf20260506_10169594', 'q4'): '同篇；“传统产业优化升级、新兴产业＿、未来产业＿的＿格局”，三空按产业成熟度对号，A只把前两空对调',
 ('nf20260506_10169594', 'q5'): '同篇；“＿布局沿海产业带”，后半“珠三角研发＋粤东粤西制造与资源开发”是分工，句末“协同”诱选“一体化”',
 ('nf20260506_10169594', 'q6'): '同篇；分论点句须罩住其后蓝碳交易、蓝色债券、生态旅游、信用积分四项，A是同篇第11段原句（即本日q5题干中的句子）',
 ('nf20260506_10169594', 'q7'): '同篇；篇末“既是思路图，更是方法论”之后的落点，递进句重心在后，A只接住“思路图”',
 # D08 ② 人民日报·评论员观察 2026-08-13《“从群众切身需要来考量”》
 ('20260813_30174634', 'q1'): '人民日报评论员观察2026-08-13（基层工作方法）；“‘乐于干’不等于‘＿’”，下一句“干劲如何使对地方”点明对比的维度',
 ('20260813_30174634', 'q2'): '同篇；调查研究的要求句，四项都是“A，更要B”格式；题干加下一段（驻村干部“步子走下去了，心却没贴在一起”）作上下文',
 ('20260813_30174634', 'q3'): '同篇；“敢往矛盾堆里扎、多做＿事”，“锦上添花”是现成的反义陷阱',
 ('20260813_30174634', 'q4'): '同篇；“争执是表象，根源是＿”，要由同段后文开的“药方”（发展产业、就近务工）反推病根，A“确权滞后”单看最合理',
 # D08 ③ 人民日报·评论员观察 2026-09-17《舍得在“看不见的地方”下功夫》
 ('20260917_30181544', 'q1'): '人民日报评论员观察2026-09-17（西吉文学与合肥创新生态）；带引号的比喻词，要同时扣住“不仅仅在于走出多少作家”与“扎根泥土”',
 ('20260917_30181544', 'q2'): '同篇；段尾收束句（与q1同段，互相以“另题”遮蔽），A把落点拉回段首已否定的“走出多少作家”',
 ('20260917_30181544', 'q3'): '同篇；“不在修枝剪叶，而在＿”，答案由“同理”之后的“激发内生动力”翻译出来，“护苗”最像',
 ('20260917_30181544', 'q4'): '同篇；“乔木参天、灌木茁壮、苗木葱郁的＿景观”，干扰项只把“长得好”再说一遍，答案是对三层结构的概括',
 ('20260917_30181544', 'q5'): '同篇；古诗句填空，“自会迎来＿的盛景”与段中“挖大树”“摘桃子”的单打独斗相对，C是同诗上一句',
 # D09 ① 南方日报·理论周刊·知行 2025-12-08《以生态之笔绘就共同富裕新图景》
 ('nf20251208_10155869', 'q1'): '南方日报理论周刊2025-12-08（绿美广东与共同富裕）；“虽然守着绿水青山，但＿”的转折后半，要接住下一句“将生态优势转化为发展优势”',
 ('nf20251208_10155869', 'q2'): '同篇；“不仅……而且＿”的递进分寸，紧跟的“为后续的产业融合、民生改善提供坚实支撑”限定只走到“打底”这一步',
 ('nf20251208_10155869', 'q3'): '同篇；“生态与经济空间＿的区域发展不平衡问题”，后文珠三角、沿海、北部山区的分工给出线索；“失衡”与句尾“不平衡”重复',
 ('nf20251208_10155869', 'q4'): '同篇；与“含金量”配对的“含×量”，四个都是报刊常见说法，要回到主语“绿美广东生态建设”',
 # D09 ② 人民日报·评论员观察 2026-06-09《“换道超车”的门道》
 ('20260609_30161950', 'q1'): '人民日报评论员观察2026-06-09（换道超车）；比喻句，下一句“困在既有格局里往往寸步难行”给出反面',
 ('20260609_30161950', 'q2'): '同篇；“依据自身禀赋、＿作出选择，实现错位发展”，“取长补短”只差一字、方向相反',
 ('20260609_30161950', 'q3'): '同篇；例子的落点，“弯道超车”最熟最易选；题干加第9段（“弯道超车不易，直道超车更难……换道则是……”）作上下文',
 ('20260609_30161950', 'q4'): '同篇；“充分发挥＿”的优势类术语，同段“因地制宜”“依托自身根基”给出线索，“后发优势”被上一题的答案勾出',
 ('20260609_30161950', 'q5'): '同篇；名言填空，前有“一己之进、一时之胜”，后有“开放合作”“志在长远”，四句都谈合作或包容',
 # D09 ③ 人民日报·人民时评 2026-04-28《考实真政绩  画准实干人》
 ('20260428_30153667', 'q1'): '人民日报人民时评2026-04-28（干部政绩考核）；接“政绩画像”比喻的四字格，“看实景、听口碑”对“写实”，“浓墨重彩”同为绘画用语',
 ('20260428_30153667', 'q2'): '同篇；“从事后评价转为＿”，“事前预判”与“事后”字面相反最易误选，后文“平时”“日常”“一贯”给出线索',
 ('20260428_30153667', 'q3'): '同篇；用“既……又……”把“紧箍咒”“回头看”两个比方翻成白话；题干加上一段（同一句式“既用望远镜又用显微镜”）作上下文，干扰项取自同篇别段',
 ('20260428_30153667', 'q4'): '同篇；“不可能一种考核办法＿”，前文列的是地方之间的差别而非时间变化，“一劳永逸”最顺口',
 ('20260428_30153667', 'q5'): '同篇；两个“性”分别对应“一单位一策差异化考核”和“同一量级放在一起考核”，干扰项各只接住一半',
}

EXTRA_NOTES = {
 ('nf20260831_10180091', 'q5'): '【数据】源数据第29段在空缺之后、句号之前有一个零宽字符（U+200C），照录未删，不影响显示与作答；同篇第12段另有两处同类字符（不在题干中）。',
 ('20251225_30127104', 'q2'): '【上下文】题干加第5段（q1所在段，q1空缺以“另题”遮蔽）：原站解析以该段“广州遴选10家龙头民企，下放职称评审权”的先行先试作为本空依据，单看第6段不足以作答。',
 ('20260813_30174634', 'q2'): '【上下文】题干加第12段：原站解析的依据（“步子走下去了，心却没贴在一起”）在下一段，第11段本身只有一句，不足以作答。',
 ('20260609_30161950', 'q3'): '【上下文】题干加第9段：原站解析排除“弯道超车”的依据是第9段“弯道超车不易，直道超车更难……换道则是……”，单看第14段难以区分。第9段不含本篇其他题的答案。',
 ('20260428_30153667', 'q3'): '【上下文】题干加第7段：原站解析指出第7、8两段同一句式（先问“如何……？”，再用两个比方，最后“既……又……”翻成白话），第7段给出样板；该段不含本篇其他题的答案。',
}
GD_EXTRA_NOTES = {
 ('GD2020X', 2): '【编排】GD2020Z-9（片段，未登记）的文段含“公众本身不仅是被动的接受者，更是主动的参与者”，即本题答案；该题若被选用，须排在本题之后（同日排在本题之后或更晚的日子），不能早于 D07。本题放在本轮第一天 D07 的第一题，即为此。',
 ('GD2022X', 5): '【编排】关联词按“隔天1道”放在 D07、D09，后续可放 D11、D13……D23（剩余关联词7道，恰好每隔一天1道）。',
 ('GD2018', 11): '【编排】广东语句上一道在 D05（GD2023X-21，段首名句），本题隔4天放在 D09；剩余3道（GD2019X-12、GD2020X-6、GD2022Z-6）建议约 D13/D14、D18、D22/D23 各1道。',
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


def _load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    os.makedirs(OUT, exist_ok=True)
    questions, articles = [], []
    n = 0

    def nid():
        nonlocal n
        n += 1
        return f'{PREFIX}-{n:03d}'

    for day in DAYS:
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
                assert 2017 <= yr <= 2023, it['paper']
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
                           + f"供给段：{it['seg']}（{it['kind']}）。"
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
            assert aid_src not in R1_ARTICLES and aid_src not in R2_ARTICLES, aid_src
            gname = f'{day}-H{hidx}'
            gtitle = f"一文多题：{a['src']}·{a['col']} {a['date']}（原文待本组做完再看）"
            sel = set(qmap.keys())
            assert sel == {q['id'] for q in a['q']}, (aid_src, 'every question of the article must be used')
            aid = f'ART-HTML-{aid_src}'
            order = 0
            for q in a['q']:
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
                    flags=(['多空'] if len(q['blanks']) > 1 else []) + (['同段另题遮蔽'] if has_other else [])
                          + (['加上下文段'] if len(pnos) > 1 else []),
                    notes=('言语只做数据完整性与原文对应检查：已用程序核对该段拼接原文在空缺位置的文字＝选项%s（%s）。题干上下文：%s，原文照录未改写；同篇其他入选题的空缺以“（另题）”遮蔽。原文 %s 须待本组各题做完再看。原站解析存于 source_note（原始备份，不进训练答案册）。' % (
                        letter, q['options'][q['answer']], ctx_desc, aid)) + EXTRA_NOTES.get((aid_src, q['id']), ''),
                    source_note=q['note'],
                    claim_key=f"HTML:{aid_src}:{q['id']}",
                    _fills=fills,
                )
                questions.append(qq)
            text, paras = restored_text_html(a)
            articles.append(dict(
                aid=aid, kind='html_original', kind_cn='用户HTML源数据还原的原文',
                source=dict(file=HTML_FILE, html_article_id=aid_src, src=a['src'], col=a['col'], date=a['date'],
                            page=a['page'], author=a['author'], url=a['url'], group=a['gname']),
                title=a['title'], text=text, paras=paras,
                external_original=dict(status='未核实', url=a['url'],
                                       why='本会话网络不能访问报刊原站（paper.people.com.cn、epaper.southcn.com 经代理均返回 403），未与外部原文逐字比对'),
                note=('据用户 HTML 源数据（paras 中 t/m 片段按序拼接）还原的原文段落，未改写；各题空缺处的原文用词即在段中。未与报刊原站逐字比对。'
                      f"本篇入选题：{'、'.join(sorted(sel, key=lambda x: int(x[1:])))}；本篇全部题目均入选。"
                      '原文须待本篇各题做完后再看。原站解析（note）不随原文展示。')))

    # ---------------- checks ----------------
    log = []
    by_day = collections.defaultdict(list)
    for q in questions:
        by_day[q['day']].append(q)
    # (0) context paragraphs must not carry an answer of a later question of the same day (subsumed by (1), listed for clarity)
    # (1) leak check: no answer string of a question appears in any EARLIER stem of the same day
    leaks = []
    for day, qs in by_day.items():
        for i, q in enumerate(qs):
            for f in q['_fills']:
                for p in qs[:i]:
                    if f in p['stem']:
                        leaks.append((day, q['id'], f, 'earlier stem', p['id']))
                if len(f) >= 10:                      # long sentence answers: also look for any 8-char piece
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
            for f in q['_fills']:
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
        for f in q['_fills']:
            if len(f) >= 2 and f in q['stem']:
                own.append((q['id'], f))
    log.append(f'[info] answer text also visible elsewhere in its own stem: {len(own)}')
    for x in own:
        log.append('   ' + repr(x))
    # (2b) answer text shown earlier the same day as an OPTION of another question (not a leak: a distractor does not reveal
    #      the key, but the word has been seen; listed for information) and invisible characters in stems/options
    seen_opt = []
    for day, qs in by_day.items():
        for i, q in enumerate(qs):
            for f in q['_fills']:
                if len(f) < 2:
                    continue
                for p in qs[:i]:
                    if any(f in (v or '') for v in p['options'].values()):
                        seen_opt.append((day, q['id'], f, 'is an option of earlier', p['id']))
    log.append(f'[info] answer text that appeared earlier the same day as an option of another question: {len(seen_opt)}')
    for x in seen_opt:
        log.append('   ' + repr(x))
    ZW = re.compile('[​‌‍⁠﻿]')
    zw = [(q['id'], 'stem' if ZW.search(q['stem']) else 'options') for q in questions
          if ZW.search(q['stem']) or any(ZW.search(v or '') for v in q['options'].values())]
    log.append(f'[info] zero-width characters (copied verbatim from the source text) in stems/options: {len(zw)}')
    for x in zw:
        log.append('   ' + repr(x))
    # (3) cross-round repeats: answer strings already used as answers in rounds 1-2 (YY-A, YY2A)
    prev_ans = {}
    for path, tag in [(R1_SRC, 'R1'), (R2_SRC, 'R2')]:
        mod = _load_module(path, 'gd_' + tag)
        for it in mod.GD:
            for f in it['fills']:
                prev_ans.setdefault(f, []).append(f"{tag} GD:{it['paper']}-{it['qno']}")
    for tag, arts in [('R1', R1_ARTICLES), ('R2', R2_ARTICLES)]:
        for aid_src in arts:
            a = ART[aid_src]
            for q in a['q']:
                t = ptext(a['paras'][q['p'] - 1])
                for b in q['blanks']:
                    prev_ans.setdefault(t[b['b']:b['e']], []).append(f"{tag} HTML:{aid_src}:{q['id']}")
    rep = []
    for q in questions:
        for f in q['_fills']:
            if len(f) >= 2 and f in prev_ans:
                rep.append((q['id'], f, prev_ans[f]))
    log.append(f'[info] answers identical to a round-1/2 (D01-D06) answer: {len(rep)}')
    for x in rep:
        log.append('   ' + repr(x))
    # (3b) whole option sets / stems repeated from rounds 1-2 (should be none)
    # (4) answer-letter distribution
    c = collections.Counter((q['day'], q['checked_answer']) for q in questions)
    for day in DAYS:
        log.append(f"[dist] {day}: " + ' '.join(f"{k}={c[(day, k)]}" for k in 'ABCD'))
    log.append('[dist] all: ' + ' '.join(f"{k}={sum(c[(d, k)] for d in DAYS)}" for k in 'ABCD'))
    # (5) counts
    cnt = collections.Counter((q['day'], q['topic'], 'GD' if q['source']['paper'].startswith('GD') else 'HTML') for q in questions)
    for k in sorted(cnt):
        log.append(f'[count] {k} {cnt[k]}')
    for day in DAYS:
        tc = collections.Counter(q['topic'] for q in by_day[day])
        assert tc['选词填空'] == 12 and tc['语句填空'] == 6, (day, tc)
        log.append(f'[count] {day}: 选词 {tc["选词填空"]} 语句 {tc["语句填空"]}')
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

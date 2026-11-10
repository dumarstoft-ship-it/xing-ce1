"""YY4B round-4 build: verbal D10-D12, passage reading (片段) 18/day + sentence ordering (排序) 4/day.
Reads plan4.py (PLAN/PXPLAN/META); writes questions.jsonl, articles.jsonl, source crops (assets/src) and claim_plan.json.
All items are real exam questions: no adaptation, no solutions; checked_answer == source_answer (the analysis file's answer)."""
import json, re, os, sys, collections
SP = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, SP)
from qx import get, raw, crop
from clean4 import clean_pd4, clean_px4, RADICAL
from ansx import info, seg
from simcheck import sims
from plan4 import PLAN, PXPLAN, META
from PIL import Image
OUT = '/home/user/work/out4/YY4B'
DAYS = ['D10', 'D11', 'D12']
os.makedirs(f'{OUT}/assets/src', exist_ok=True); os.makedirs(f'{SP}/crops', exist_ok=True)

PXMETA = {  # key: topic phrase
 'GK2017D-50': '大数据的价值在于“用”（以煤矿作比；数字经济）',
 'GK2015D-52': '发动机与中国工业的“心脏病”（产业/自主研发）',
 'SC2023-45': '中华美育精神：美与善的统一（文化）',
 'ZJ2021A-39': '读书贵精与著作“少而精”（文化/阅读）',
 'GK2021F-43': '多元化纠纷解决机制与“枫桥经验”（法治/基层治理）',
 'GK2014-50': '“再生建筑”的由来与发展（城市/建筑史）',
 'HB2020-40': '语言与文化一体两面（语言文化）',
 'JS2020A-23': '生态环境保护的法律体系（生态法治）',
 'GK2019D-50': '植物科学画在中国与西方的源流（科学文化史）',
 'GK2015D-53': '生态红线（生态文明）',
 'SD2020-34': '雅典文明衰落的“环境破坏说”及其被否定（历史/学术史）',
 'ZJ2018A-105': '顺境与逆境（人生哲理）',
}
TYPE_CN = {'主旨': '主旨概括', '意图': '意图判断', '细节': '细节判断', '标题': '标题填入', '下文': '下文推断', '词句': '词句理解',
           '观点': '意图判断', '目的': '词句理解', '俗语': '主旨概括', '名言': '主旨概括', '关键词': '主旨概括'}
DETAIL = {  # finer question form (editor record; the six base labels above stay comparable with earlier rounds)
 'GD2016X-27': '选非（理解有误）', 'GD2014X-23': '可以得知', 'GD2016X-31': '词语所指（“新集体文化”）', 'GD2016X-30': '俗语匹配（意思最贴近）',
 'GD2014X-32': '作者观点', 'GK2017F-37': '核心观点（选项为警句式概括）', 'GK2017F-46': '作者看法（四字词概括）',
 'GK2017F-49': '与原文相符', 'GK2021D-46': '主要说的是', 'GK2013-58': '未暗示的信息（选非）', 'GK2013-60': '与主旨无关的名言（选非）',
 'GK2014-56': '没有论及（选非）', 'GK2014-59': '可以推出', 'GK2014-60': '关键词', 'GK2015F-43': '写作目的（介绍《新尔雅》的目的）',
 'GK2015F-46': '例证作用（用“团购”说明什么）', 'GK2015F-48': '与原文相符', 'GK2016F-48': '名句概括道理', 'GK2016F-60': '应用推断（可解释哪一行为）',
 'GK2025X-65': '没有解释哪一问题（选非）', 'GK2014-44': '引言后文推断', 'GK2013-43': '散文标题',
}
CAT_NOTE = {'法治': '法治', '三农': '三农', '经济': '经济', '社会': '社会治理/民生', '党政': '党政时政', '国际': '国际时政',
            '文化': '文化', '生态': '生态文明', '科技时政': '科技时政（讲发展态势与对策，非机理说明）', '军事议论': '军事议论文（讲战略与用人，非装备说明）'}

def paper_cn(pid):
    m = re.match(r'([A-Z]+)(\d{4})(.*)', pid); prov, y, v = m.groups()
    if prov == 'GK': return f'国考{y}年度' + {'F': '副省级', 'D': '地市级', 'X': '行政执法卷', '': '卷'}.get(v, '')
    if prov == 'GDXD': return {'XC': '广东选调2019年（选调优秀大学毕业生）《行测》卷', 'ZH': '广东选调2020年《综合行政能力测验》卷'}[v]
    if prov == 'GD': return f'广东{y}年度' + {'Z': '乡镇卷', 'X': '县级以上卷' if y == '2014' else '县级卷', '': '卷'}.get(v, v)
    name = {'SD': '山东', 'JS': '江苏', 'ZJ': '浙江', 'SC': '四川', 'HB': '河北', 'SZ': '深圳'}[prov]
    return f'{name}{y}年度' + {'A': 'A类', 'H': '下半年卷', 'S': '上半年卷', '': '卷'}.get(v, v)

CJK = r'一-鿿“”‘’《》（）'
def fullwidth_punct(s):
    n0 = s
    s = re.sub(rf'(?<=[{CJK}]),(?=[{CJK}])', '，', s)
    s = re.sub(rf'(?<=[{CJK}]);(?=[{CJK}])', '；', s)
    s = re.sub(rf'(?<=[{CJK}]):(?=[{CJK}“])', '：', s)
    s = re.sub(rf'(?<=[{CJK}]):(?=\s*$)', '：', s, flags=re.M)
    s = re.sub(rf'(?<=[{CJK}])\?(?=\s*$)', '？', s, flags=re.M)
    return s, s != n0

# ---------- answers ----------
GDA = 'xing-ce1/答案解析/'
SCAN = {  # answers read by the editor from scanned analysis pages (page region rendered, then read by eye; OCR was used only to locate the item)
 'GD2016X-27': dict(ans='D', page=4, rate=None, yc=None, cc='《新常态是中国经济由大变强过程》',
    file=GDA + '2016年广东公务员考试《行测》真题（县级卷）答案及解析.pdf',
    how='解析为扫描件（无文字层），编者将第4页该题区域出图目读：“27、文段与选项一一对应。……D 项‘已经’一词与文段表达的时态不一致，原文是‘已接近完成’说明还未完成。本题为选非题，故正确答案为 D。”；同题乡镇卷 GD2016Z-15 的扫描件解析（第2页）同样出图目读，亦为“故正确答案为 D”，并载“【文段出处】《新常态是中国经济由大变强过程》”（县级卷解析此题未载出处，出处据乡镇卷解析照录）'),
 'GD2015X-20': dict(ans='D', page=3, rate=None, yc=None, cc=None,
    file=GDA + '2015年广东公务员考试《行测》真题县级卷答案及解析.pdf',
    how='解析为扫描件（无文字层），编者将第3页该题区域出图目读：“20、本题为中心理解题。……结合选项可知，D 项为正确答案。……故正确答案为 D。”；同题乡镇卷 GD2015Z-20 选项次序不同（该卷 A 个性化定制是传统零售业的发展方向、B 互联网将打破信息不对称的格局、C 互联网会对传统零售业和制造业产生影响、D 互联网会对传统行业进行渗透与改造，已对原页核对），其扫描件解析第3页为“故正确答案为 C”，所指选项内容与本卷 D 项相同，两份解析实质一致'),
 'GD2016X-31': dict(ans='D', page=5, rate=None, yc=None, cc='《培厚“精神新土层”，迎接“新集体生活”》',
    file=GDA + '2016年广东公务员考试《行测》真题（县级卷）答案及解析.pdf',
    how='解析为扫描件（无文字层），编者将第5页该题区域出图目读：“31、文段首句指出‘新集体文化’是网络时代独有的文化……D 项符合，当选。……故正确答案为 D。【文段出处】《培厚‘精神新土层’，迎接‘新集体生活’》”'),
 'GD2014X-23': dict(ans='D', page=6, rate=45, yc='A', cc=None,
    file=GDA + '2014年广东公务员考试《行测》真题（县级以上卷）答案及解析.pdf',
    how='解析为扫描件（无文字层），编者将第6页该题区域出图目读：“23、正确答案：D，全站正确率：45%，易错项：A。……因此，选择 D 选项。”'),
 'GD2016X-30': dict(ans='D', page=5, rate=None, yc=None, cc='《当几回热锅上的蚂蚁》',
    file=GDA + '2016年广东公务员考试《行测》真题（县级卷）答案及解析.pdf',
    how='解析为扫描件（无文字层），编者将第5页该题区域出图目读：“30、文段首句提出观点‘犯其至难方能图其至远’……D 项，‘成人不自在，自在不成人’……符合要求。……故正确答案为 D。【文段出处】《当几回热锅上的蚂蚁》”'),
 'GD2014X-32': dict(ans='B', page=7, rate=59, yc='A', cc=None,
    file=GDA + '2014年广东公务员考试《行测》真题（县级以上卷）答案及解析.pdf',
    how='解析为扫描件（无文字层），编者将第7页该题区域出图目读：“32、正确答案：B，全站正确率：59%，易错项：A。……因此，选择 B 选项。”'),
 'GK2021F-43': dict(ans='D', page=13, rate=61, yc='C', cc=None,
    file='xing-ce1/国考/答案解析/2021年国家公务员考试《行测》真题（副省级）参考答案及解析...pdf',
    how='副省级解析为扫描件（无文字层；xingce 仓库同名解析亦无文字层），编者将第13页出图（140dpi）目读：“43、正确答案：D，全站正确率：61%，易错项：C。……⑤句适合做首句，排除 A 项和 B 项。……④②论述党的十八届四中全会文件，③句正好指代④②中的‘文件’。因此，选择 D 选项。”，与 D 项⑤①⑥④②③相符；同页“44、正确答案：B，全站正确率：64%”与地市级同题（GK2021D-52）文字层解析一致，页面对应无误'),
}
CC_MANUAL = {  # source named inside the analysis prose rather than in a 【文段出处】 line
 'GK2014-60': '莫言《用耳朵阅读》',
}
CC_MANUAL_NOTE = {'GK2014-60': '原解析正文称“文段选自莫言《用耳朵阅读》”，无单列【文段出处】。',
                  'GD2016X-27': '文段出处见同题乡镇卷（GD2016Z-15）的解析；县级卷解析此题未载出处。'}
NO_CC = ('暂无', '无', '未找到', '暂未找到')
def cc_clean(raw_cc):
    """Join a (possibly wrapped) source-title line from the analysis; drop text-layer spaces next to digits/Latin, keep spaces between CJK words."""
    if not raw_cc: return None
    s = raw_cc.replace('\n', '').strip()
    s = re.sub(r'(?<=[0-9A-Za-z.])[ \t]+(?=[一-鿿])', '', s)
    s = re.sub(r'(?<=[一-鿿])[ \t]+(?=[0-9A-Za-z])', '', s)
    s = re.sub(r'[ \t]{2,}', ' ', s).strip()
    return s or None
def get_cc(segtext):
    m = re.search(r'(?:【(?:文段|文章)?(?:出处|来源)】|(?:文段|文章)(?:出处|来源)[：:])[ \t]*\n?[ \t]*([^\n]+)((?:\n[^\n【]{1,60}》[^\n]*)?)', segtext)
    if not m: return None
    first = m.group(1)
    cont = m.group(2) if ('《' in first and '》' not in first) else ''
    return cc_clean(first + cont)
def bound(s, q):
    """cut an analysis segment at the start of the next item (some analyses defeat ansx's own next-item pattern)"""
    m = re.search(rf'\n\s*{q + 1}\s*[、\.．]\s*\S', s[20:])
    return s[:20 + m.start()] if m else s
ANS_PAT = r'(?:正确答案[：:]\s*|故正确答案为\s*|正确选项为\s*|因此[，,]?\s*选择\s*)([A-D])'
def answer_of(tag, q, k):
    if k in SCAN:
        a = SCAN[k]; return a['ans'], a['page'], a['rate'], a['yc'], a['cc'], a['file'], a['how'], None
    r = info(tag, q)
    s = bound(r['seg'], q)
    disp = None
    m = re.search(r'此题存在争议[^。\n]*。', s)
    if m: disp = m.group(0).strip()
    assert '争议' not in s or disp, (k, 'unparsed dispute remark')
    cc = get_cc(s)
    if cc in NO_CC: cc = None
    if k in CC_MANUAL: assert CC_MANUAL[k].split('《')[1].rstrip('》') in s, k; cc = CC_MANUAL[k]
    head = s[:m.start()] if m else s   # every answer statement before any dispute remark must agree
    letters = set(re.findall(ANS_PAT, head))
    assert len(letters) == 1, (k, letters)
    main = letters.pop()
    auto = json.load(open(f'/home/user/work/answers/{tag}.json'))['answers'].get(str(q), {}).get('ans')
    assert auto == main, (k, auto, main)
    rate = re.search(r'正确率[：:]?\s*(\d{1,3})\s*%', s); yc = re.search(r'易错项[：:]?\s*([A-D])', s)
    how = '解析文字层答案句（如“故正确答案为X”“正确答案：X”“因此，选择X选项”）提取，与 answers/ 自动抽取一致'
    if disp: how += '（取争议说明之前的原参考答案）'
    return main, r['page'], int(rate.group(1)) if rate else None, yc.group(1) if yc else None, cc, r['file'], how, disp
def partner_answers(partners):
    out = []
    for p in partners:
        pt, pq = p.rsplit('-', 1)
        for t in (pt, pt + '_xc'):
            if os.path.exists(f'/home/user/work/answers/{t}.json'):
                try:
                    rr = seg(t, int(pq))
                    if rr:
                        ls = set(re.findall(ANS_PAT, bound(rr['seg'], int(pq))))
                        assert len(ls) == 1, (p, ls)
                        out.append((t + '-' + pq, ls.pop()))
                except AssertionError: raise
                except Exception: pass
    return out

def page_list(segs): return sorted({s[0] + 1 for s in segs})
def outlet(cc):
    """publication / site named before the (last) article title, e.g. 人民日报《…》 -> 人民日报"""
    if not cc or '《' not in cc: return None
    o = cc[:cc.rindex('《')].strip('：:-－— ')
    return o or None
def title_of(cc):
    if not cc: return None
    m = re.findall(r'《[^《》]*》', cc); return m[-1] if m else cc

# per-item text patches: (old, new, note). Only to restore what the PDF text layer lost or mis-coded; each checked against the page image.
STEM_PATCH = {
 'GK2017F-49': [('最大的困难是资金问题，的人认为', '最大的困难是资金问题，64.2%的人认为', None),
                ('同行竞争过度，占。', '同行竞争过度，占26.9%。',
                 '原页“64.2%”“26.9%”两处为嵌入的小图，文字层为空；已按原页放大图（330dpi）补录，并与地市级同题 GK2017D-59 的文字层（两处数字俱全）核对一致，其余用字未动。')],
 'GK2016F-52': [('政府信用评级―样', '政府信用评级一样',
                 '原页“东部发达地区和西部欠发达地区的政府信用评级一样”的“一”印作横线“―”（文字层码位 U+2015，地市级同题 GK2016D-50 相同）；据紧接的下一分句“地方政府信用和国家信用评级一样”及文意录为“一”，其余用字未动。')],
 'GK2021D-46': [('《汉书・平帝纪》', '《汉书·平帝纪》', None),
                ('爱德华•琴纳', '爱德华·琴纳', '原PDF文字层两处间隔号码位为“・”（U+30FB）和“•”（U+2022），原页均印作居中圆点，已统一为间隔号“·”，用字未改。')],
}
OPT_PATCH = {
 'GDXD2019XC-55': ({'D': ('艰苦奋斗造就革命胜利出最合理的1项。', '艰苦奋斗造就革命胜利')},
                   '文字层把下一部分标题“四、推理判断……选出最合理的1项。”的折行尾巴粘在 D 项后，已按原页删去。'),
 'GK2014-60': ({'A': ('耳朵阅读回忆', '耳朵 阅读 回忆'), 'B': ('耳朵阅读灵感', '耳朵 阅读 灵感'), 'C': ('阅读故事灵感', '阅读 故事 灵感'), 'D': ('阅读故事回忆', '阅读 故事 回忆')},
               '选项为三个并列的关键词，原页以空格分隔；清洗时空格被并掉，已按原页恢复。'),
}
END_PUNCT = {  # editor-supplied sentence-end marks for restored ordering passages where the default '。' would split one sentence
 'ZJ2018A-105': {'②': '，', '⑥': '？'},   # ②③ 为“不但……更……”一句；⑥为反问句
}
AS_PRINTED = {
 'GD2014X-32': '题干“产生排他心里的同时”原卷如此（“心里”疑为“心理”之误），照录未改。',
}
FLAGS = {
 'GK2017F-49': ['文字层缺字已据原页补录'],
 'GK2016F-52': ['文字层码位已据原页改正'],
 'GK2021D-46': ['文字层码位已据原页改正'],
 'GD2014X-32': ['原卷用字照录'],
}
for _k in SCAN: FLAGS.setdefault(_k, []).append('答案取自扫描件')
NOTES = {
 'GD2015X-20': '乡镇卷同题 GD2015Z-20 选项次序与本卷不同（见答案来源），本包取县级卷题面与县级卷解析。',
 'GK2021F-43': '本题仅见于副省级卷（地市级卷无此题）；副省级解析未载文段出处。',
 'GK2023F-44': '同题亦见 xingce 仓库的 GK2023F 版本（index 标签 GK2023F_xc，同一卷同一题号，登记键相同）。',
 'GK2023F-39': '同题亦见 xingce 仓库的 GK2023F 版本（index 标签 GK2023F_xc，同一卷同一题号，登记键相同）。',
 'GK2024F-41': '同题亦见 xingce 仓库的 GK2024F 版本（index 标签 GK2024F_xc，同一卷同一题号，登记键相同）。',
}
def fmt_rate(rate, yc):
    if rate is None: return None
    return f'原解析全站正确率{rate}%' + (f'、易错项{yc}' if yc else '')
def year_of(pid): return int(re.search(r'\d{4}', pid).group())

recs, arts = [], []; n = 0; claim_plan = []
for day in DAYS:
    for gk, keys in (('pd', PLAN[day]), ('px', PXPLAN[day])):
        for order, key in enumerate(keys, 1):
            n += 1; rid = f'YY4B-{n:03d}'
            tag, q = key.rsplit('-', 1); q = int(q); pid = tag.replace('_xc', ''); k = f'{pid}-{q}'
            qq = get(tag, q); r = raw(qq); pages = page_list(qq['segs'])
            notes = []; flags = list(FLAGS.get(k, []))
            if gk == 'pd':
                passage, prompt, opts, rad = clean_pd4(r)
                for a, b, note in STEM_PATCH.get(k, []):
                    assert passage.count(a) == 1, (k, a); passage = passage.replace(a, b)
                    if note: notes.append(note)
                if k in OPT_PATCH:
                    ch, note = OPT_PATCH[k]
                    for L, (a, b) in ch.items(): assert opts[L] == a, (k, L, opts[L]); opts[L] = b
                    notes.append(note)
                passage, c1 = fullwidth_punct(passage); prompt, c2 = fullwidth_punct(prompt)
                o2 = {}; c3 = False
                for L, v in opts.items():
                    v2, c = fullwidth_punct(v); o2[L] = v2; c3 = c3 or c
                opts = o2
                stem = passage + '\n' + prompt
                if c1 or c2 or c3: notes.append('原PDF文字层此处为半角标点（,:;?），已统一为全角，用字未改。')
            else:
                assert k not in STEM_PATCH and k not in OPT_PATCH
                sents, prompt, lead, opts, rad = clean_px4(r)
                assert not lead, (k, lead)
                s2 = []; chg = False
                for s in sents:
                    x, c = fullwidth_punct(s); s2.append(x); chg = chg or c
                sents = s2; prompt, c2 = fullwidth_punct(prompt)
                stem = '\n'.join(sents) + '\n' + prompt
                if chg or c2: notes.append('原PDF文字层此处为半角标点，已统一为全角，用字未改。')
            alltxt = stem + ''.join(opts.values())
            assert not RADICAL.findall(alltxt), (k, RADICAL.findall(alltxt))
            assert not re.search(r'[―・•]', alltxt), (k, 'unpatched code point')
            assert set(opts) == set('ABCD') and all(opts.values()), (k, opts)
            ans, ans_page, rate, yc, cc, ans_file, how, disp = answer_of(tag, q, k)
            assert ans in 'ABCD', (k, ans)
            if gk == 'pd': assert META[key][1] == ans, (k, META[key][1], ans)   # plan sheet vs. analysis
            if disp and '争议(原标)' not in flags: flags.append('争议(原标)')
            vnote = '网友回忆版' if '网友回忆版' in qq['file'] else None
            if vnote and '网友回忆版' not in flags: flags.append('网友回忆版')
            partners = sorted({f'{t.replace("_xc", "")}-{qq2}' for c, t, qq2, sec, _ in (sims(tag, q) or []) if c >= 0.9} - {k})
            pc = paper_cn(pid); y = year_of(pid)
            if gk == 'pd':
                typ, _, cat, short = META[key]
                topic = TYPE_CN[typ]; detail = DETAIL.get(k)
                if pid.startswith('GDXD'): role = '广东选调卷原题，作“广东系锚题”（gd_anchor=选调），校准广东命题取向'; anchor = '选调'
                elif pid.startswith('GD'): role = '广东省考老卷片段（2013—2016年度；用户11-09定为可作“广东锚题”，gd_anchor=true），校准广东命题取向'; anchor = True
                elif cat == '科技': role = '当日唯一一道科技说明文（每天至多1道）'; anchor = False
                elif y >= 2017: role = f'国考2017—2025年度剩余的{CAT_NOTE[cat]}类片段（国考优先，先用2017—2025年度）'; anchor = False
                else: role = f'国考2013—2016年度片段，{CAT_NOTE[cat]}题材（2017—2025年度非科技片段用尽后按用户顺序接用）'; anchor = False
                sv = [f'{pc}原题（{topic}' + (f'·{detail}' if detail else '') + '）', f'题材：{short}', role]
            else:
                cnt = len(sents); detail = None
                topic = f'语句排序（{cnt}句）'
                if pid.startswith('GK'): role = '国考排序（用户：国考、省考排序各年度能用皆用）'; anchor = False
                else: role = '外省排序（用户已放开排序外省卷）' + ('；新拉入的江苏2015—2019/浙江2015—2020A卷' if re.match(r'(JS201[5-9]|ZJ201[5-9]|ZJ2020A)', pid) else ''); anchor = False
                sv = [f'{pc}原题（{topic}）', f'题材：{PXMETA[k]}', role]
            fr = fmt_rate(rate, yc)
            if fr: sv.append(fr)
            if disp: sv.append('原解析标有争议，照录')
            o = outlet(cc)
            if k in CC_MANUAL: sv.append(f'原解析称文段选自{cc}')
            elif o and gk == 'pd': sv.append(f'原解析所载出处：{o}')
            pa = partner_answers(partners) if k not in SCAN else []
            if pa:
                assert all(a2 == ans for _, a2 in pa), (k, ans, pa)
                how += '；同题他卷解析（' + '、'.join(f'{t}:{a2}' for t, a2 in pa) + '）一致'
            if k in AS_PRINTED: notes.append(AS_PRINTED[k])
            if k in CC_MANUAL_NOTE: notes.append(CC_MANUAL_NOTE[k])
            if NOTES.get(k): notes.append(NOTES[k])
            if re.search(r'·{3,}|\.{6}|•{3,}', r): notes.append('原PDF文字层省略号为六个点（“······”或“......”），已统一为“……”，用字未改。')
            notes.append(f'题干、选项已对原页截图（assets/src/{rid}.png）逐字核对；答案来源：{how}，见解析第{ans_page}页。')
            if partners: notes.append('同一文段亦见 ' + '、'.join(partners) + '，已一并登记占用。')
            if gk == 'px' and order == 4:
                notes.append('本题为当日第4道排序（可撤位）：如改为每日3道，本题可整体撤下并释放登记。')
            dst = f'assets/src/{rid}.png'
            tmp = f'{SP}/crops/{key}_150.png'
            if not os.path.exists(tmp): crop(qq, tmp, dpi=150)
            Image.open(tmp).convert('L').save(f'{OUT}/{dst}', optimize=True)
            prov = re.match(r'[A-Z]+', pid).group(0)
            aid = f'ART-{prov}-{pid}-{q}'
            src = {'paper': pid, 'file': qq['file'], 'page': pages[0], 'pages': pages, 'qno': q, 'index_tag': tag,
                   'ans_file': ans_file, 'ans_page': ans_page, 'version_note': vnote}
            if pid.startswith('GDXD'): src['section_note'] = 'index 把本卷言语部分标成“常识”；已按原页核对：本题位于原卷“三、阅读理解”部分'
            rec = {'id': rid, 'module': '言语', 'day': day, 'official_day': day,
                   'group': f'{day}-{"PD" if gk == "pd" else "PX"}', 'group_title': None,
                   'topic': topic, 'topic_detail': detail, 'order': order, 'source': src, 'done_status': '已做情况未知',
                   'stem': stem, 'options': opts, 'material_or_article': aid, 'assets': [], 'source_crop': dst,
                   'source_answer': ans, 'checked_answer': ans, 'source_rate': rate, 'source_yicuo': yc,
                   'source_passage_title': cc, 'dispute_note': disp,
                   'brief_solution': '', 'selection_value': '；'.join(sv) + '。',
                   'variant_of': None, 'check_status': '已核验', 'flags': flags, 'notes': ' '.join(notes),
                   'replaced_from': None, 'gd_anchor': anchor, 'px_slot4_replaceable': (gk == 'px' and order == 4),
                   'claim_key': k, 'dup_keys': partners, 'related_passages': []}
            recs.append(rec)
            ext = {'status': '待补' if cc else '无出处', 'title_per_analysis': cc, 'text': None}
            asrc = {'paper': pid, 'file': qq['file'], 'page': pages[0], 'qno': q, 'ans_file': ans_file, 'ans_page': ans_page, 'passage_title_per_analysis': cc}
            patch_note = ' '.join(x[2] for x in STEM_PATCH.get(k, []) if x[2]) + (' ' + AS_PRINTED[k] if k in AS_PRINTED else '')
            if gk == 'pd':
                art = {'aid': aid, 'kind': 'exam_passage', 'kind_cn': '原题文段：逐字照录考试题干中的文段，不是外部文章全文',
                       'source': asrc, 'title': title_of(cc), 'text': passage, 'external_original': ext,
                       'note': (f'外部文章全文未取得；出处据原解析照录：{cc}' + ('（' + CC_MANUAL_NOTE[k].rstrip('。') + '）' if k in CC_MANUAL_NOTE else '') if cc else '外部文章全文未取得；原解析未载文段出处') + '。原题文段逐字照录题干，未改写、未从解析倒推。',
                       'editor_note': ('本轮未联网取外部原文，不以模型改写或从解析倒推代替。 ' + patch_note).strip()}
            else:
                order_str = re.sub(r'[^①-⑧]', '', opts[ans])
                smap = {s[0]: s[1:] for s in sents}
                assert sorted(order_str) == sorted(smap), (k, order_str, list(smap))
                seq = [smap[c] for c in order_str]
                out = []; added = []
                for c_, s in zip(order_str, seq):
                    if c_ in END_PUNCT.get(k, {}): out.append(s + END_PUNCT[k][c_]); added.append(END_PUNCT[k][c_])
                    elif s.endswith(('。', '！', '？', '；', '…')) or (s.endswith(('”', '’')) and len(s) > 1 and s[-2] in '。！？…'): out.append(s)
                    elif s.startswith(('如何', '怎样', '为何', '为什么')) or s.endswith(('吗', '呢')): out.append(s + '？'); added.append('？')
                    else: out.append(s + '。'); added.append('。')
                text = ''.join(out)
                art = {'aid': aid, 'kind': 'restored_from_answer', 'kind_cn': '按参考答案顺序还原的文段（非外部原文）',
                       'source': asrc, 'title': title_of(cc), 'order': order_str, 'text': text, 'external_original': ext,
                       'note': f'非外部原文：按参考答案{ans}（{order_str}）还原，句内用字未改' + (('，句末标点（' + '、'.join(f'“{x}”' for x in sorted(set(added), key='。，？'.index)) + '）为编者所补（原题各句无句末标点）') if added else '') + '。' + (f'出处据原解析照录：{cc}；外部原文正文待补。' if cc else '原解析未载出处。'),
                       'editor_note': '还原文段只按参考答案顺序连接原句；外部原文未检索（本轮未联网），不以模型改写代替。'}
            arts.append(art)
            claim_plan.append((k, partners, rid, day, gk))
# group titles per day (computed from content; no solution hints)
for day in DAYS:
    pdr = [r for r in recs if r['day'] == day and r['group'].endswith('PD')]
    pxr = [r for r in recs if r['day'] == day and r['group'].endswith('PX')]
    for r in pdr: r['group_title'] = '片段阅读（广东系锚题＋国考）'
    srcs = []
    if any(r['source']['paper'].startswith('GK') for r in pxr): srcs.append('国考')
    if any(r['source']['paper'].startswith('GDXD') for r in pxr): srcs.append('广东选调')
    if any(not r['source']['paper'].startswith(('GK', 'GD')) for r in pxr): srcs.append('外省')
    for r in pxr: r['group_title'] = '语句排序（' + '＋'.join(srcs) + '）'
with open(f'{OUT}/questions.jsonl', 'w') as f:
    for r in recs: f.write(json.dumps(r, ensure_ascii=False) + '\n')
with open(f'{OUT}/articles.jsonl', 'w') as f:
    for a in arts: f.write(json.dumps(a, ensure_ascii=False) + '\n')
json.dump(claim_plan, open(f'{SP}/claim_plan.json', 'w'), ensure_ascii=False, indent=0)
print(len(recs), len(arts))
print(collections.Counter((r['day'], r['group'][-2:]) for r in recs))

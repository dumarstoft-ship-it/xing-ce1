"""Replace exactly 8 records of /home/user/work/out2/PD2C/questions.jsonl in place (same id, group, order); all other lines untouched."""
import json

P = '/home/user/work/out2/PD2C/questions.jsonl'
GK20F = 'xing-ce1/国考/真题/2020年国家公务员考试《行测》真题（副省级）.pdf'
GK20F_ANS = 'xing-ce1/国考/答案解析/2020年国家公务员考试《行测》真题（省级）答案及解析...pdf'
SUP = 'xing-ce1/题源补充/真题_江苏浙江2015-2020/'

NEW = {
'PD2C-001': dict(
    topic='条件推理-“只有…才”的翻译与四种推理形式',
    source=dict(paper='GK2020F', file=GK20F, page=13, qno=107, ans_file=GK20F_ANS, ans_page=22,
                version_note='副省级卷；与地市级卷GK2020D-102同题（已一并登记）'),
    stem='一切生命有机体都需要新陈代谢，否则生命就会停止。文明也是一样，如果长期自我封闭，必将走向衰落。交流互鉴是文明发展的本质要求。只有同其他文明交流互鉴、取长补短，才能保持旺盛生命活力。\n由此可以推出：',
    options={'A': '一种文明如果没有同其他文明交流互鉴，就不能保持旺盛生命活力',
             'B': '一种文明如果没有长期自我封闭，就不会走向衰落',
             'C': '一种文明如果同其他文明交流互鉴、取长补短，就能保持旺盛生命活力',
             'D': '一种文明如果没有保持旺盛生命活力，它就没有同其他文明取长补短'},
    source_answer='A', checked_answer='A',
    brief_solution='只翻讲文明的句子：长期自我封闭→衰落；保持旺盛生命活力→交流互鉴且取长补短（“只有…才”，“只有”后是必要条件）。A“没交流互鉴→不能保持活力”是“只有…才”句的逆否，后件为“且”，否定一项即可✓；B是否前，C是肯后，D“没保持活力→没取长补短”也是否前，均推不出。首句讲生命有机体，只是类比。答案A。提速：先画箭头，再给每个选项贴“逆否/否前/肯后”标签。',
    selection_value='“只有…才”“如果…必将”同段出现，四个选项依次是逆否、否前、肯后、否前；D把否前写成“没有…就没有…”，最像逆否——热身练“先画箭头再判形式”，并分清首句类比不参与推理。',
    notes='替换GK2024F-106（用户在42天习题本前三天做过）。与解析一致（解析第22页：A否后推否前；B否前；C肯后；D否前）。程序穷举：只把文明的三句设为命题，A在全部15个模型中成立，B、C、D都有反例。与地市级卷GK2020D-102同题，claim已一并锁定。',
    difficulty='易', source_rate=None, source_yicuo=None, verify='verify/verify_d06.py::gk2020f_107',
    source_key='GK2020F-107', replaced_from='GK2024F-106'),

'PD2C-003': dict(
    topic='条件推理-选言前件的否后与德摩根（反向设问）',
    source=dict(paper='ZJXD2020', file=SUP + '2020年度浙江省党政机关选调应届优秀大学毕业生《行测》真题.pdf', page=4, qno=30,
                ans_file=SUP + '2020年度浙江省党政机关选调应届优秀大学毕业生《行测》真题参考答案及解析_.pdf', ans_page=7,
                version_note='浙江2020年度选调《行测》（11-08新拉入题源）'),
    stem='假设“如果甲爱看越剧或乙不爱看越剧，那么丙爱看越剧”为真，由下列哪项可推出“乙爱看越剧”的结论？',
    options={'A': '丙不爱看越剧', 'B': '甲不爱看越剧', 'C': '甲和丙都爱看越剧', 'D': '甲和丙有一个不爱看越剧'},
    source_answer='A', checked_answer='A',
    brief_solution='条件：（甲爱看或乙不爱看）→丙爱看。要推出“乙爱看”，而乙只在前件里，只能否后：丙不爱看→并非（甲爱看或乙不爱看）＝甲不爱看且乙爱看，A✓。B：甲不爱看时前件真假还看乙，推不出；C：甲爱看只能推出丙爱看，乙不定；D：若是甲不爱看、丙爱看，乙仍不定。答案A。提速：结论藏在前件里，直接找“否定后件”的选项。',
    selection_value='反向设问：要推出的结论藏在“或”字前件里，只有否后才能把它拿出来，再用德摩根把“并非（甲爱看或乙不爱看）”拆成“甲不爱看且乙爱看”；B、C、D分别对应“只否一个析取支”“肯前”“二者之一不明”三种错觉。',
    notes='替换JS2024A-91（用户已做）。与解析一致（解析第7页：否后必否前＋德摩根）。程序：对每个选项检查“与规则相容且所有模型中乙都爱看”，只有A成立；D按“恰有一个不爱看”和“至少一个不爱看”两种读法都推不出。浙江2020年度选调卷（11-08新拉入，属2017—2026范围）。',
    difficulty='易', source_rate=None, source_yicuo=None, verify='verify/verify_d06.py::zjxd2020_30',
    source_key='ZJXD2020-30', replaced_from='JS2024A-91'),

'PD2C-005': dict(
    topic='条件推理-量词陷阱（“普遍”≠“所有”）＋否前/否后',
    source=dict(paper='GDXD2019SW', file='xing-ce1/真题/2019年广东省选调优秀大学毕业生笔试《思维能力测验》真题.pdf', page=3, qno=12,
                ans_file='xing-ce1/答案解析/2019年广东省选调优秀大学毕业生笔试《思维能力测验》答案及解析.pdf', ans_page=3,
                version_note='广东2019年选调《思维能力测验》；原卷题面作“普通存在”，解析作“普遍存在”'),
    stem='近年来，我国快递行业飞速发展。但是，当前我国快递行业普通存在服务同质化的问题。由于服务缺少特色，一旦某家快递公司涨价，消费者就会选择其他快递公司。\n根据上述表述，下列判断一定正确的是（）。\nⅠ.所有快递公司都存在服务同质化问题\nⅡ.如果某家快递公司不涨价，消费者就不会选择其他快递公司\nⅢ.如果消费者一直选择某家快递公司，那么这家快递公司一定没有涨价',
    options={'A': 'Ⅰ', 'B': 'Ⅲ', 'C': 'Ⅰ、Ⅱ', 'D': 'Ⅰ、Ⅲ'},
    source_answer='B', checked_answer='B',
    brief_solution='唯一的条件句：某家涨价→消费者选择其他公司。Ⅰ：题干只说行业“普通（即普遍）存在”同质化，推不出“所有”公司都有✗；Ⅱ：不涨价→不选其他，是否前✗；Ⅲ：“一直选择某家”即没有选择其他公司，否后得这家没涨价✓。答案B（只有Ⅲ）。提速：先判Ⅰ，Ⅰ错即可排除A、C、D。',
    selection_value='量词＋条件双陷阱：“普遍存在”≠“所有都有”；Ⅲ把“没有选择其他公司”换说成“一直选择某家”，要先还原成后件的否定再逆否；组合选项判对Ⅰ一项就能排除三个选项。',
    notes='替换GD2022X-56（用户已做）。与解析一致（解析第3页：Ⅰ“普遍存在”推不出“所有”；Ⅱ否前；Ⅲ否后必否前）。原卷题面作“普通存在服务同质化的问题”，解析作“普遍存在”，疑为原卷笔误，题面照原卷未改。程序穷举：3家公司、“普遍”只取多数（≥2家）有同质化，只有Ⅲ在全部108个模型中成立。',
    difficulty='易-中', source_rate=None, source_yicuo=None, verify='verify/verify_d06.py::gdxd2019sw_12',
    source_key='GDXD2019SW-12', replaced_from='GD2022X-56'),

'PD2C-006': dict(
    topic='条件推理-条件句的真假（前件假则真）＋分情况',
    source=dict(paper='JS2017A', file=SUP + '2017年江苏公务员考试《行测》真题（A类）.pdf', page=12, qno=97,
                ans_file=SUP + '2017年江苏公务员考试《行测》真题（A类）参考答案及解析.pdf', ans_page=30,
                version_note='江苏2017年A类（11-08新拉入题源）；解析为扫描件：第30页末为题头（答案、正确率），第31页为解析，已出图核对'),
    stem='张某死了，法医查明是中毒而亡。张某的两个邻居甲和乙对前来调查的赵警官说了这样的话：\n甲：如果张某死于谋杀，他老婆李某脱不了干系，这段时间她正和张某闹离婚；\n乙：张某不是死于自杀，就是死于谋杀，不可能是意外；\n赵警官听了甲乙的话以后，作出如下两个判断：\n（1）甲乙两人说的都是对的或都是错的，那么张某就是死于意外\n（2）甲乙两人中有一人说的是错的，那么张某就不是死于意外\n调查后发现，赵警官的判断都是正确的。\n可以推出以下哪项？',
    options={'A': '张某死于谋杀', 'B': '张某死于自杀', 'C': '张某死于意外', 'D': '李某杀了张某'},
    source_answer='A', checked_answer='A',
    brief_solution='甲的话按条件句判对错：谋杀→李某有干系（“正在闹离婚”是理由）；乙：死因不是意外。关键：前件假，条件句为真。若是意外：乙错，甲因前件假而对，一对一错，由（2）不是意外，矛盾；若是自杀：甲、乙都对，由（1）是意外，矛盾；所以是谋杀，乙对。若李某有干系，甲也对，又推出意外，矛盾——故李某无干系、甲错，符合（2）。答案A；D与之相反。提速：按三种死因逐一代入两条判断。',
    selection_value='条件句真值是硬点：死因不是谋杀时，甲的“如果谋杀，则……”自动为真——想不到这一点就会误选C（原卷正确率30%，易错C）；同时练按死因分三种情况、用两条判断逐一排除。',
    notes='替换SC2020H-81（用户已做）。与扫描版解析一致（解析第30页末题头：正确答案A，全站正确率30%，易错项C；第31页解析，已出图核对）。解析把甲的话译为“谋杀→李某”，“这段时间她正和张某闹离婚”作理由、不作判断对象；按此读法，赵警官（2）的“有一人说的是错的”按“恰有一人”或“至少一人”理解，程序穷举都唯一得A。若把“正在闹离婚”也算作甲断言的一部分，死因不唯一（脚本有说明性输出）；这不是通行读法，已在解法首句写明按条件句判对错。原位置是“长链倒推”（中），本题更难，使本组有一道中-难题。',
    difficulty='中-难', source_rate='30%', source_yicuo='C', verify='verify/verify_d06.py::js2017a_97',
    source_key='JS2017A-97', replaced_from='SC2020H-81'),

'PD2C-016': dict(
    topic='分析推理-座位编号＋条件句否后排除',
    source=dict(paper='GK2020F', file=GK20F, page=14, qno=111, ans_file=GK20F_ANS, ans_page=23, version_note='副省级卷'),
    stem='甲、乙、丙、丁、戊五人乘坐高铁出差，他们正好坐在同一排的A、B、C、D、F五个座位。已知：\n（1）若甲或者乙中的一人坐在C座，则丙坐在B座；\n（2）若戊坐在C座，则丁坐在F座。\n如果丁坐在B座，那么可以确定的是：',
    options={'A': '甲坐在A座', 'B': '乙坐在D座', 'C': '丙坐在C座', 'D': '戊坐在F座'},
    source_answer='C', checked_answer='C',
    brief_solution='两个条件的前件都落在C座。丁坐B：丙就不坐B，由（1）否后，甲、乙都不坐C；丁不坐F，由（2）否后，戊不坐C；C座只能是丙，C✓。甲、乙、戊在A、D、F三座怎么坐都行，A、B、D都不确定。答案C。提速：先问“条件指向的C座能坐谁”，不必列座位表。',
    selection_value='座位题的条件推理版：两个条件的前件都指向C座，用两次否后必否前逐人排除，一步锁定丙——练“从条件指向的位置下手”，30秒题。',
    notes='替换GD2023X-58（用户已做）。与解析一致（解析第23页）。程序穷举：丁坐B时满足条件的排法共6种，丙都坐C；A、B、D各只在其中2种成立。',
    difficulty='易', source_rate=None, source_yicuo=None, verify='verify/verify_d06.py::gk2020f_111',
    source_key='GK2020F-111', replaced_from='GD2023X-58'),

'PD2C-018': dict(
    topic='分析推理-分组（一周排课：数量配平推隐藏约束）',
    source=dict(paper='GK2019F', file='xing-ce1/国考/真题/2019年国家公务员考试行测真题（省级）.pdf', page=13, qno=115,
                ans_file='xing-ce1/国考/答案解析/2019年国家公务员考试行测真题（省级）答案及解析...pdf', ans_page=26,
                version_note='副省级卷（文件名作“省级”）'),
    stem='小若为了参加一项法律考试，准备在一周之内复习14门课程，其中民法课程5门、经济法课程3门、行政法课程3门、商法课程2门、国际私法课程1门。但是因为精力有限，小若每天只能复习2门课程，并且需要满足以下条件：\n（1）星期四只能复习2门民法课程，其余每天必须复习两类不同的课程；\n（2）国际私法必须在星期天复习；\n（3）民法和行政法不能在同一天复习；\n（4）经济法和商法不能在同一天复习。\n由此可以推出，以下哪两类课程不可能在同一天复习？',
    options={'A': '经济法和国际私法', 'B': '行政法和经济法', 'C': '行政法和商法', 'D': '民法和经济法'},
    source_answer='A', checked_answer='A',
    brief_solution='周四是2门民法，其余6天、12个位置：民3、经3、行3、商2、国1，每天两类不同。民不能配民、配行，只能配经、商、国；行不能配民，也只能配经、商、国。民、行共6门各占一天，6个搭档正好用尽经3、商2、国1——所以经、商、国三类彼此永不同天。国际私法只能和民法或行政法同天，A“经济法和国际私法”不可能✓；B、C、D都排得出。答案A。',
    selection_value='看似要排一周课表，实为数量配平：民法、行政法各3门都只能找经、商、国作搭档，6个空位恰好用完，推出“经、商、国彼此不同天”的隐藏约束——国考副省级压轴的分组题，练先算数量再推结构。',
    notes='替换GD2023X-56（用户已做）。与解析一致（解析第26页）。程序穷举全部合法周课表（共200种：周四民法2门、周日含国际私法），永不同天的类别对只有民—行、经—商（题干直接禁止）和经—国、商—国（推出），选项中只有A；B、C、D都有可行课表。',
    difficulty='中-难', source_rate=None, source_yicuo=None, verify='verify/verify_d06.py::gk2019f_115',
    source_key='GK2019F-115', replaced_from='GD2023X-56'),

'PD2C-019': dict(
    topic='分析推理-双向互选＋每组人数上下限',
    source=dict(paper='JS2019A', file=SUP + '2019年江苏公务员考试《行测》试卷（A卷）.pdf', page=10, qno=93,
                ans_file=SUP + '2019年江苏公务员考试《行测》试卷（A卷）答案及解析.pdf', ans_page=19,
                version_note='江苏2019年A卷（11-08新拉入题源）'),
    stem='某地开展企业结对扶贫创新活动，倡导企业家与贫困家庭互选，要求每户贫困家庭只能选1位企业家，而每位企业家只能在选他的贫困家庭中选择1-2户开展帮扶活动。现有企业家甲、乙、丙3人面对张、王、李、赵4户贫困家庭，已知：\n（1）张、王2户至少有1户选择甲；\n（2）王、李、赵3户中至少有2户选择乙；\n（3）张、李2户中至少有1户选择丙。\n事后得知，互选顺利完成，每户贫困家庭均按自己心愿选到了企业家，而每位企业家也按要求选到了贫困家庭。\n根据以上信息，可以得出以下哪项？',
    options={'A': '企业家甲选到了张户', 'B': '企业家乙选到了赵户', 'C': '企业家丙选到了李户', 'D': '企业家甲选到了王户'},
    source_answer='B', checked_answer='B',
    brief_solution='每户只选1位、每位企业家收1—2户，4户分给3人只能是2、1、1。（2）王、李、赵中至少2户选乙，乙又最多2户，所以乙恰好2户、都在王李赵中，甲、丙各1户，张不选乙。分情况：张选甲→由（3）李选丙→乙得王、赵；张选丙→由（1）王选甲→乙得李、赵。两种方案都有乙—赵，B✓；A、C、D各只在一种方案中成立。答案B。',
    selection_value='先把互选规则翻成“每组1—2户”，再用“至少2户＋最多2户”把乙夹死为2户；剩下只需对张分两种情况，两支都得乙—赵——练人数上下限夹逼后的分类讨论。',
    notes='替换HB2024-105（用户已做）。与解析一致（解析第19页）。程序穷举4户×3位企业家的81种选择：满足“每位企业家1—2户”和三条件的方案恰2种（张甲王乙李丙赵乙、张丙王甲李乙赵乙），只有B在两种中都成立。江苏2019年A卷（11-08新拉入题源）。',
    difficulty='中', source_rate=None, source_yicuo=None, verify='verify/verify_d06.py::js2019a_93',
    source_key='JS2019A-93', replaced_from='HB2024-105'),

'PD2C-021': dict(
    topic='分析推理-职业匹配＋“只有会计师说真话”',
    source=dict(paper='JS2021A', file='xingce/2021年江苏公务员考试《行测》真题（A卷）.pdf', page=13, qno=94,
                ans_file='xingce/2021年江苏公务员考试《行测》真题（A卷）参考答案及解析.pdf', ans_page=25,
                version_note='江苏2021年A卷（xingce版）'),
    stem='甲、乙、丙、丁4位中学同学毕业30年后相聚。现在，他们已成为企业家、大学教师、歌手和会计师，且每人只有一种身份，并不重复。他们在中学时代就各人的未来职业有过如下预言：\n甲：乙不会成为歌手；\n乙：丙会成为会计师；\n丙：丁不会成为企业家；\n丁：乙不会成为大学教师。\n现在看来，他们当中只有会计师的预言是正确的。\n根据上述信息可以推断，甲、乙、丙、丁的职业分别是：',
    options={'A': '企业家、大学教师、歌手、会计师', 'B': '大学教师、歌手、企业家、会计师',
             'C': '企业家、歌手、会计师、大学教师', 'D': '会计师、大学教师、歌手、企业家'},
    source_answer='D', checked_answer='D',
    brief_solution='只有会计师的预言为真，其余三人都说错。乙说“丙是会计师”：若丙是会计师，乙就说对了，可乙不是会计师，矛盾；所以丙不是会计师，乙说错，乙也不是会计师。若丁是会计师：甲错→乙是歌手，丙错→丁是企业家，与丁是会计师冲突。故甲是会计师：丙错→丁是企业家，丁错→乙是大学教师，丙是歌手，甲“乙不是歌手”为真，D✓。提速：选项是完整方案，可先用乙的预言排除C，再逐项代入。答案D。',
    selection_value='真假与身份绑定：“只有会计师说对”同时决定谁说真话、谁是会计师，从“乙预言丙是会计师”切入能一下排除两人；易错B（漏查丙的预言其实为真），原卷正确率48%——匹配题里练“假设—检验”。',
    notes='替换SC2025-85（用户已做）。与解析一致（解析第25页：正确答案D，全站正确率48%，易错项B）。程序穷举24种职业分配，满足“会计师的预言为真、其余三人为假”的只有D一种。原位置是方桌座位题；座位类在2017—2026年度已无未用原题，本组座位由016、022承担，此处改用匹配题。xingce版（江苏2021年A卷），xing-ce1无此卷。',
    difficulty='中', source_rate='48%', source_yicuo='B', verify='verify/verify_d06.py::js2021a_94',
    source_key='JS2021A-94', replaced_from='SC2025-85'),
}

KEEP = ['id', 'module', 'day', 'group', 'group_title']        # carried over from the old record
ORDER = ['id', 'module', 'day', 'group', 'group_title', 'topic', 'order', 'source', 'done_status', 'stem', 'options', 'material_or_article',
         'assets', 'source_answer', 'checked_answer', 'brief_solution', 'selection_value', 'variant_of', 'check_status', 'flags', 'notes',
         'difficulty', 'source_rate', 'source_yicuo', 'verify', 'set', 'source_key', 'replaced_from']

raw = open(P, encoding='utf-8').read()
assert raw.endswith('\n')
lines = raw[:-1].split('\n')
out, done = [], set()
for l in lines:
    old = json.loads(l)
    if old['id'] not in NEW:
        out.append(l); continue
    n = NEW[old['id']]
    rec = {k: old[k] for k in KEEP}
    rec.update(n)
    rec['order'] = old['order']
    rec.update(done_status='已做情况未知', material_or_article=None, assets=[], variant_of=None, check_status='已核验', flags=[], set=None)
    assert rec['source_answer'] == rec['checked_answer']
    assert old['source_key'] == rec['replaced_from'], (old['id'], old['source_key'], rec['replaced_from'])
    rec = {k: rec[k] for k in ORDER}
    assert set(old.keys()) | {'replaced_from'} == set(rec.keys()), old['id']
    out.append(json.dumps(rec, ensure_ascii=False)); done.add(old['id'])
assert done == set(NEW), done
open(P, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('replaced', sorted(done))

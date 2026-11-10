# -*- coding: utf-8 -*-
"""GD real-exam items for D07-D09 (round 3), transcribed from the page images (200 dpi renders; the index text layer
was only used to locate the items). Punctuation normalised to full-width; typesetting spaces between digits and CJK dropped.
Blank markers: '______' where the original prints an underline (any length); '（  ）' where the original prints parentheses;
'____________' for the sentence blank of a 语句填空 item.
Answers: 2017-2021 analyses are scans -> read from the rendered page images (全站正确率/易错项 only where the analysis prints them);
2022-2023 analyses have a text layer -> read from the text and cross-checked with answers/<tag>.json.
Tie-break rule used in the selection: among items of equal training value in the same supply segment, prefer one whose
answer letter is not B (the HTML articles chosen for D07-D09 already carry many B answers; options are never altered).
Supply rotation (user rule for D07-D24): GD 选词 2-3 per day rotating over 2017-18 / 2019-21 / 2022-23, a 关联词 item every
other day (D07, D09, D11 ... D23 -> 9 days for the 9 remaining 关联词 items); GD 语句 about one per 4-5 days (previous one D05 -> D09)."""

A22X = 'xing-ce1/答案解析/2022年广东公务员考试行测试题（县级）答案解析.pdf'
A23Z = 'xing-ce1/答案解析/2023年广东省公务员录用考试《行测》题（乡镇卷）答案解析.pdf'
A21Z = 'xing-ce1/答案解析/2021年0314广东公务员考试《行测》真题（乡镇）参考答案及解析.pdf'
A20X = 'xing-ce1/答案解析/2020年0809广东公务员考试《行测》真题（县级以上）参考答案及解析.pdf'
A20Z = 'xing-ce1/答案解析/2020年0809广东公务员考试《行测》真题（乡镇）参考答案及解析.pdf'
A19X = 'xing-ce1/答案解析/2019年广东公务员考试《行测》真题（县级）答案及解析.pdf'
A18 = 'xing-ce1/答案解析/2018年广东省公务员录用考试《行测》真题（县级、乡镇统一卷）答案及解析.pdf'
A17 = 'xing-ce1/答案解析/2017年广东公务员考试《行测》真题答案及解析.pdf'

Q22X = 'xing-ce1/真题/2022年广东公务员考试行测试题（县级).pdf'
Q23Z = 'xing-ce1/真题/2023年广东省公务员录用考试《行测》题（乡镇卷）.pdf'
Q21Z = 'xing-ce1/真题/2021年0314广东公务员考试《行测》真题（乡镇）.pdf'
Q20X = 'xing-ce1/真题/2020年0809广东公务员考试《行测》真题（县级以上）（7道题暂缺）.pdf'
Q20Z = 'xing-ce1/真题/2020年0809广东公务员考试《行测》真题（乡镇）.pdf'
Q19X = 'xing-ce1/真题/2019年广东公务员考试《行测》真题（县级）.pdf'
Q18 = 'xing-ce1/真题/2018年广东省公务员录用考试《行测》真题（县级、乡镇统一卷）.pdf'
Q17 = 'xing-ce1/真题/2017年广东公务员考试《行测》真题.pdf'

B = '______'
L = '____________'
P2 = '（  ）'
P4 = '（    ）'

# pos = fixed position inside its group (pins the delivered IDs). Groups: GX = 广东选词, GY = 广东语句.
# seg = supply segment used for the rotation bookkeeping (2017-18 / 2019-21 / 2022-23); kind = 实词 or 关联词.
GD = [
 # ---------------- D07 ----------------
 dict(pos=1, day='D07', topic='选词填空', seg='2019-21', kind='关联词', paper='GD2020X', qno=2, file=Q20X, page=1, ans_file=A20X, ans_page=1,
      stem=f'在政务公开中，公众本身{B}是被动的接受者，{B}是主动的参与者。只有公众不断地广泛参与，政务公开才有不断深入的动力。',
      prompt='填入横线部分最恰当的一项是：',
      options=['既 又', '不仅 更', '即使 也', '因为 所以'], answer='B', fills=['不仅', '更'],
      rate='63%', yicuo='A', chuchu=None, flags=[],
      version_note='原卷文件名注“7道题暂缺”，本题完整',
      value='广东2020县级卷原题，解析载全站正确率63%（易错A）：剩余关联词库存里正确率最低的一道；“被动的接受者”与“主动的参与者”之间是并列还是递进，A“既…又…”最像'),
 dict(pos=2, day='D07', topic='选词填空', seg='2019-21', kind='实词', paper='GD2019X', qno=5, file=Q19X, page=1, ans_file=A19X, ans_page=1,
      stem=f'中国特色社会主义进入新时代，文艺创作、学术创新拥有无比{P4}的空间。而高质量的文化{P4}，是满足人民美好生活向往的重要组成部分，也是时代发展所需。',
      prompt='',
      options=['浩瀚 需求', '悠长 创作', '广阔 供给', '宽敞 库存'], answer='C', fills=['广阔', '供给'],
      chuchu='《以高质量文化供给，汇聚向上向善的力量》', flags=[],
      version_note='原卷此题无提示语，照原样保留；县级卷独有题（乡镇卷第1—5题为本卷第2、3、6、9、10题的同题或近似题，无本题）',
      value='广东2019县级卷原题；两空分别搭配“空间”与“高质量的文化”，第一空四个形容词都有“大、长”之意，第二空要对上后文“满足人民美好生活向往”'),
 dict(pos=3, day='D07', topic='选词填空', seg='2017-18', kind='实词', paper='GD2017', qno=3, file=Q17, page=1, ans_file=A17, ans_page=1,
      stem=f'生活中细小的变化都可能让我们的感觉大不相同，我们要学会欣赏和赞扬，随时{B}身边美好的事物，因为关注美好事物有助于规避不良情绪，同时切记多与乐观豁达、愉快向上的人相处。此外，{B}一下日常生活节奏，也会让你的生活更有活力。',
      prompt='依次填入画横线部分最恰当的一项是：',
      options=['留意 改善', '发现 改变', '寻找 调整', '发掘 调节'], answer='B', fills=['发现', '改变'],
      chuchu='《人生的幸福感曲线》', flags=[],
      version_note='原卷横线较短（文字层为5个下划线），按本包体例统一录作6个下划线',
      value='广东2017卷原题；“随时＿身边美好的事物”与“＿一下日常生活节奏”两处动宾搭配，四组都是常用近义动词，校准广东卷在细微差别上的取舍'),
 # ---------------- D08 ----------------
 dict(pos=1, day='D08', topic='选词填空', seg='2022-23', kind='实词', paper='GD2023Z', qno=4, file=Q23Z, page=1, ans_file=A23Z, ans_page=2,
      stem=f'备耕种先行。种子作为春耕时必不可少的农资，数量和质量都至关重要。如今，乡村储备仓库里一袋袋优质早稻种子{B}，还会有专业人员定时查看种子情况，确保{B}。',
      prompt='',
      options=['琳琅满目 分毫不差', '漫山遍野 巨细无遗', '堆积如山 万无一失', '铺天盖地 滴水不漏'], answer='C', fills=['堆积如山', '万无一失'],
      chuchu='《浏阳小河乡：春耕备耕生产忙不负农作好时光》', flags=[],
      version_note='仅 xing-ce1 有该卷题本（xingce 只有该卷解析，答案同为C）；原卷此题无提示语，照原样保留；乡镇卷独有题（县级卷无同题）',
      value='广东2023乡镇卷原题（剩余选词库存中最新的一年）；两空成语分别形容仓库里种子之多与定时查看的效果，四组都是“多”与“无差错”类成语，要看搭配对象“种子”和“确保”'),
 dict(pos=2, day='D08', topic='选词填空', seg='2019-21', kind='实词', paper='GD2020Z', qno=4, file=Q20Z, page=1, ans_file=A20Z, ans_page=1,
      stem=f'在广袤的大地上，通过“三支一扶”计划成长起来的年轻人，在不同领域和岗位上担当作为，无私奉献，{B}了青春的价值，{B}出一曲曲奋斗赞歌。',
      prompt='填入横线部分最恰当的一项是：',
      options=['诠释 谱写', '书写 传唱', '证明 吟诵', '展现 描绘'], answer='A', fills=['诠释', '谱写'],
      rate='84%', yicuo='B', chuchu=None, flags=[],
      version_note='乡镇卷独有题（县级卷无同题）',
      value='广东2020乡镇卷原题，解析载全站正确率84%（易错B）：“＿了青春的价值”“＿出一曲曲奋斗赞歌”两处动宾搭配，四组都是“写、唱、说”一类动词'),
 # ---------------- D09 ----------------
 dict(pos=1, day='D09', topic='选词填空', seg='2022-23', kind='关联词', paper='GD2022X', qno=5, file=Q22X, page=1, ans_file=A22X, ans_page=3,
      stem=f'社会是企业家施展才华的舞台。{B}真诚回报社会、切实履行社会责任的企业家，{B}能真正得到社会认可，{B}是符合时代要求的企业家。',
      prompt='依次填入画横线部分最恰当的一项是：',
      options=['只有 才 才', '只要 就 就', '如果 不仅 还', '因为 所以 就'], answer='A', fills=['只有', '才', '才'],
      chuchu='《弘扬企业家精神，带领企业战胜困难》', flags=[],
      version_note='县级卷独有题；解析第2页起、续至第3页（答案与文段出处在第3页），与 answers/GD2022X.json 一致',
      value='广东2022县级卷原题；三空关联词，“真诚回报社会”对“得到认可”“符合时代要求”是必要条件还是充分条件，B“只要…就…”最像'),
 dict(pos=2, day='D09', topic='选词填空', seg='2019-21', kind='实词', paper='GD2021Z', qno=1, file=Q21Z, page=1, ans_file=A21Z, ans_page=1,
      stem=f'建设“红色村”，既要注重源于“红”、体现“红”，更要注重传承“红”、弘扬“红”，用红色文化烘托红色精神，以红色精神{B}红色基因。',
      prompt='填入横线处最恰当的词语是：',
      options=['发现', '激活', '激荡', '发掘'], answer='B', fills=['激活'],
      rate='82%', yicuo='D', chuchu='南方杂志《广东“红色村”渐次花开》', flags=[],
      version_note='乡镇卷第1题；县级卷（GD2021X）第1—5题中无同题（已对县级卷第1页原图）',
      value='广东2021乡镇卷原题（广东“红色村”题材），解析载全站正确率82%（易错D）：“以红色精神＿红色基因”与前句“用红色文化烘托红色精神”并列，四个动词都能和“基因”沾边'),
 dict(pos=3, day='D09', topic='选词填空', seg='2017-18', kind='实词', paper='GD2018', qno=10, file=Q18, page=1, ans_file=A18, ans_page=2,
      stem=f'{P2}的中华民族发展史是中国人民书写的，{P2}的中华文明是中国人民创造的，{P2}的中华民族精神是中国人民培育的，中华民族迎来了从站起来、富起来到强起来的伟大飞跃是中国人民奋斗出来的。',
      prompt='',
      options=['波澜壮阔 博大精深 历久弥新', '恢弘壮丽 源远流长 同舟共济', '气势磅礴 奔流不息 与时俱进', '延绵不断 厚积薄发 奋发有为'], answer='A',
      fills=['波澜壮阔', '博大精深', '历久弥新'],
      chuchu='《人民是历史的创造者 人民是真正的英雄》', flags=[],
      version_note='原卷此题无提示语，照原样保留',
      value='广东2018统一卷原题；三个成语分别修饰“发展史”“中华文明”“民族精神”，第二空“博大精深/源远流长”都能修饰文明，须三空连看'),
 dict(pos=1, day='D09', topic='语句填空', seg='2017-18', kind='语句', paper='GD2018', qno=11, file=Q18, page=1, ans_file=A18, ans_page=2,
      stem=f'改革开放使我国走向繁荣富强，经济实力、科技实力、国防实力、综合国力快速提升。改革开放之所以能给我国带来翻天覆地的变化，一个重要原因是{L}，主要体现为我们既坚持以经济建设为中心、把发展作为第一要务，又主动为发展营造安全环境。前者以改革开放解放和发展生产力，提高资源配置效率和发展水平；后者改变了我们处理自身与外部关系的方式，主动改善和发展与其他国家的关系，积极缓解外部安全威胁。',
      prompt='填入划线部分的句子，最恰当的是（　　）。',
      options=['它推动了经济快速发展和综合国力的提高', '它得到了人民群众的衷心拥护和支持', '它优化了政策制度体系和施政方式', '它带来了重大的理念和战略转变'], answer='D',
      fills=['它带来了重大的理念和战略转变'],
      chuchu='《人民日报大家手笔：统筹发展和安全》', flags=[],
      version_note='题面跨原卷第1—2页（第1页末起，第2页续）；解析第2页',
      value='广东2018统一卷原题；横线后“主要体现为……前者……后者……”逐层解释横线，所填原因句要同时统领“以经济建设为中心”和“营造安全环境”两方面，A只接住其一'),
]

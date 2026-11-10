# -*- coding: utf-8 -*-
"""GD real-exam items for D04-D06 (round 2), transcribed from the page images (checked against the index text where a text layer exists).
Blank markers: '______' where the original prints an underline; '（  ）' / '（    ）' where the original prints parentheses.
Answers: 2017-2021 analyses are scans -> read from the page images (rate/易错项 only where the analysis prints them);
2022-2023 analyses have a text layer -> read from the text and cross-checked with answers/<tag>.json.
GD2021X (县级) is a scanned paper that is not in the shared index: the stem was transcribed from the page image at 260 dpi."""

A23X = 'xing-ce1/答案解析/2023年广东省公务员录用考试《行测》题（县级卷）答案解析.pdf'
A22X = 'xing-ce1/答案解析/2022年广东公务员考试行测试题（县级）答案解析.pdf'
A21X = 'xing-ce1/答案解析/2021年0314广东公务员考试《行测》真题（县级）参考答案及解析.pdf'
A20X = 'xing-ce1/答案解析/2020年0809广东公务员考试《行测》真题（县级以上）参考答案及解析.pdf'
A20Z = 'xing-ce1/答案解析/2020年0809广东公务员考试《行测》真题（乡镇）参考答案及解析.pdf'
A19X = 'xing-ce1/答案解析/2019年广东公务员考试《行测》真题（县级）答案及解析.pdf'
A18 = 'xing-ce1/答案解析/2018年广东省公务员录用考试《行测》真题（县级、乡镇统一卷）答案及解析.pdf'
A17 = 'xing-ce1/答案解析/2017年广东公务员考试《行测》真题答案及解析.pdf'

Q23X = 'xing-ce1/真题/2023年广东省公务员录用考试《行测》题（县级卷）.pdf'
Q22X = 'xing-ce1/真题/2022年广东公务员考试行测试题（县级).pdf'
Q21X = 'xing-ce1/真题/2021年0314广东公务员考试《行测》真题（县级）.pdf'
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
GD = [
 # ---------------- D04 ----------------
 dict(pos=1, day='D04', topic='选词填空', paper='GD2020X', qno=3, file=Q20X, page=1, ans_file=A20X, ans_page=1,
      stem=f'作为人间最{B}、最{B}的情感，爱国是流淌在中华民族血脉之中，去不掉、打不破、灭不了的情感，是中国人民和中华民族维护民族独立和民族尊严的强大精神动力。',
      prompt='填入横线部分最恰当的一项是：',
      options=['深层 持久', '真挚 复杂', '特殊 难忘', '强烈 丰富'], answer='A', fills=['深层', '持久'],
      rate='71%', yicuo='D', chuchu=None, flags=[], version_note='原卷文件名注“7道题暂缺”，本题完整',
      value='广东2020县级卷原题，解析载全站正确率71%（易错D）：两空形容词修饰“情感”，须与后文“去不掉、打不破、灭不了”相照应；四组都是常见搭配'),
 dict(pos=2, day='D04', topic='选词填空', paper='GD2017', qno=8, file=Q17, page=1, ans_file=A17, ans_page=2,
      stem=f'利用互联网等信息技术促进留守儿童家庭的亲子交流，不仅有很强的必要性，也具备相当的{B}。长期以来，我国科技和信息工作的推进，已经为{B}留守儿童难题奠定了良好的软硬件基础。',
      prompt='依次填入画横线部分最恰当的一项是：',
      options=['合理性 根治', '现实性 治理', '可行性 缓解', '针对性 解决'], answer='C', fills=['可行性', '缓解'],
      chuchu='《用信息技术缓解“留守儿童”难题》', flags=[],
      version_note='解析第1页起、续至第2页（答案与文段出处在第2页）',
      value='广东2017卷原题；“必要性—可行性”的对举与“＿留守儿童难题”的分寸（根治/解决说过头）'),
 # ---------------- D05 ----------------
 dict(pos=1, day='D05', topic='选词填空', paper='GD2022X', qno=2, file=Q22X, page=1, ans_file=A22X, ans_page=1,
      stem=f'党的百年历史，就是党与群众水乳交融、{B}的历史。一条扁担、一张借据、半条棉被就是党与人民血肉相连、情深似海的{B}。',
      prompt='依次填入画横线部分最恰当的一项是：',
      options=['唇齿相依 印记', '相濡以沫 记忆', '休戚与共 见证', '众志成城 证明'], answer='C', fills=['休戚与共', '见证'],
      chuchu='光明日报《汇聚乡村振兴的红色力量》', flags=[],
      version_note='xing-ce1 版；xingce 网友回忆版（GD2022X_xc-2）与乡镇卷同题（GD2022Z-4）文字一致（已对图），claim 已一并锁定',
      value='广东2022县级卷原题；与“水乳交融”并列的关系类成语（唇齿相依/相濡以沫/休戚与共）分寸辨析＋“扁担、借据、棉被”是什么的名词'),
 dict(pos=2, day='D05', topic='选词填空', paper='GD2021X', qno=2, file=Q21X, page=1, ans_file=A21X, ans_page=1,
      stem=f'求同，就要守住政治底线，不断{B}共同思想政治基础。不能因为{B}最大公约数，就动摇了必须固守的政治底线。',
      prompt='填入横线处的词语最恰当的一项是：',
      options=['奠定 追寻', '筑牢 思索', '巩固 寻求', '打造 探索'], answer='C', fills=['巩固', '寻求'],
      rate='78%', yicuo='A', chuchu='人民日报大家手笔《画出最大同心圆》', flags=['扫描件转录'],
      version_note='县级卷题本为扫描件，无文字层、未进共享 index；题面按第1页原图（260dpi）逐字转录；解析亦为扫描件，第1页出图目读',
      value='广东2021县级卷原题，解析载全站正确率78%（易错A）：“不断＿共同思想政治基础”与“＿最大公约数”两处动宾搭配，四组动词都能和“基础”连用'),
 dict(pos=3, day='D05', topic='选词填空', paper='GD2018', qno=7, file=Q18, page=1, ans_file=A18, ans_page=2,
      stem=f'在当代中国，维护社会公平正义，就是要在现代化进程中逐步建立起以权利公平、机会公平、规则公平为主要内容的社会公平保障体系，{P2}公平的社会环境，让公平正义的阳光{P2}每一个国民，使每个社会成员都能享有平等的权利，有实现个人理想的机会，有表达利益{P2}的合法途径。',
      prompt='',
      options=['打造 映照 诉求', '营造 普照 诉求', '创造 照射 要求', '制造 照耀 要求'], answer='B', fills=['营造', '普照', '诉求'],
      chuchu='《社会主义是当代中国实现现代化的成功之路》', flags=[], version_note='原卷此题无提示语，照原样保留',
      value='广东2018统一卷原题；三空分别与“社会环境”“阳光…每一个国民”“利益”搭配，“普照”对“每一个”'),
 dict(pos=1, day='D05', topic='语句填空', paper='GD2023X', qno=21, file=Q23X, page=5, ans_file=A23X, ans_page=7,
      stem=f'{L}，理论学习贵在独立思考、学用结合，重在学有所悟、用有所得，在学习和实践中“众里寻他千百度”，最终“蓦然回首”，在“灯火阑珊处”领悟真谛。只有坚持学习与思考相统一，带着问题学习，养成边学习边思考的习惯，在学习中联系实际，对现实中的问题进行深入思考，才能真正将理论学深悟透。',
      prompt='以下句子最适合填入划横线处的是（　　）。',
      options=['学而不思则罔，思而不学则殆', '吾尝终日而思矣，不如须臾之所学也', '业精于勤，荒于嬉；行成于思，毁于随', '知之者不如好之者，好之者不如乐之者'], answer='A',
      fills=['学而不思则罔，思而不学则殆'],
      chuchu='《人民日报:学习理论要有三种境界》', flags=['版本差异(标点)'],
      version_note='xing-ce1 版作“＿＿＿＿，理论学习贵在……”；xingce 粉笔网友回忆版（GD2023X_xc-21）作““＿＿。”理论学习贵在……”（横线加引号、句号），不影响作答；此处用 xing-ce1 版',
      value='广东2023县级卷原题；段首名句定调，四项都是谈学习的名句，要对上后文“学习与思考相统一”；同日南方日报篇有段首引语题，可对照'),
 # ---------------- D06 ----------------
 dict(pos=1, day='D06', topic='选词填空', paper='GD2020Z', qno=3, file=Q20Z, page=1, ans_file=A20Z, ans_page=1,
      stem=f'良好乡风具有浸润人心，{B}向善，规范行为，{B}力量的积极作用，要以实施乡风文明培育行动为抓手，加强乡村德治，培育稳脱贫，促振兴的文化软环境。',
      prompt='填入横线部分最恰当的一项是：',
      options=['带动 集中', '带领 凝结', '引导 集聚', '引领 凝聚'], answer='D', fills=['引领', '凝聚'],
      rate='68%', yicuo='C', chuchu=None, flags=[], version_note='解析第1页起、续至该页下半',
      value='广东2020乡镇卷原题，解析载全站正确率68%（易错C）：两组近义动词（带动/带领/引导/引领，集中/凝结/集聚/凝聚）与“向善”“力量”的搭配，主语是“乡风”'),
 dict(pos=2, day='D06', topic='选词填空', paper='GD2019X', qno=8, file=Q19X, page=1, ans_file=A19X, ans_page=2,
      stem=f'新时代广东发展需要抓住粤港澳大湾区建设的历史{P4}，同时必须{P4}供求结构、经济增长内生动力、生产要素高效便捷流动、生态环境等面临的发展难题。',
      prompt='',
      options=['机遇 破除', '机会 破除', '机遇 破解', '机会 破解'], answer='C', fills=['机遇', '破解'],
      chuchu='新华网《着眼发展大局，共享时代荣光——以习近平同志为核心的党中央关心粤港澳大湾区建设纪实》', flags=[],
      version_note='原卷此题无提示语，照原样保留；解析第1页起、续至第2页（答案在第2页）',
      value='广东2019县级卷原题（大湾区题材）；“历史机遇/机会”“破解/破除难题”两组近义词的固定搭配'),
 dict(pos=3, day='D06', topic='选词填空', paper='GD2018', qno=8, file=Q18, page=1, ans_file=A18, ans_page=2,
      stem=f'历代仁人志士所处的历史时代不同，但都以自己的行为作出了这样的诠释：“忠”就是{P2}，在国家和民族危难之时大义凛然，挺身而出；“忠”就是{P2}，在是非曲直面前旗帜鲜明，刚直不阿；“忠”就是{P2}，在各种诱惑面前心有定力，不为所动。',
      prompt='',
      options=['担当 正直 坚持', '勇敢 刚正 坚守', '担当 刚正 坚守', '勇敢 正直 坚持'], answer='C', fills=['担当', '刚正', '坚守'],
      chuchu='《立政德应当成为领导干部的自觉追求》', flags=[], version_note='原卷此题无提示语，照原样保留',
      value='广东2018统一卷原题；三空各由后面的分句注释（挺身而出/刚直不阿/不为所动），担当—勇敢、刚正—正直、坚守—坚持三组近义词'),
]

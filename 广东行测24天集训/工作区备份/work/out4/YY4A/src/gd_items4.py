# -*- coding: utf-8 -*-
"""GD real-exam items for D10-D12 (round 4), transcribed from the page images (200 dpi renders of each question region;
the index text layer was only used to locate the items and, afterwards, for a character-by-character comparison - see
verify4.py). Punctuation normalised to full-width; typesetting spaces between digits and CJK dropped.
Blank markers: '______' where the original prints an underline (any length); '（  ）' / '（    ）' where the original prints
parentheses (2 spaces for the narrow print of GD2018, 4 for the wide print of GD2019X - as in rounds 1-3).
Answers: 2017-2021 analyses are scans -> read from rendered page images (110 dpi survey + 200 dpi crops of the answer and
出处 lines; 全站正确率/易错项 only where the analysis prints them); 2023 analysis has a text layer -> read from the text
and cross-checked with answers/GD2023X.json and with the xingce copy of the same analysis.

Selection rules followed (brief YY4A + round-3 handover):
  * 8 GD 选词 for the three days (3 / 2 / 3), three-segment rotation 2017-18 / 2019-21 / 2022-23;
    this round: 2017-18 实词 x3, 2019-21 实词 x3, 2022-23 实词 x1, 关联词 x1 (D11 only; 关联词 every other day: D07, D09, D11 ...).
  * "有正确率的优先挑低的": among the rated 2019-21 实词 left (2020Z-1 81%, 2021Z-5 84%, 2020X-4 86%, 2021X-5 87%,
    2020X-1 88%, 2021X-1 88%) the two lowest usable ones are taken (2020Z-1, 2020X-4). 2021Z-5 (84%) is NOT taken now:
    its answer "诠释" is the answer of D08's GD2020Z-4, and it shares the options 一脉相承 / 相辅相成 with 2020X-4.
  * avoid-list from round 3 respected: none of 如火如荼 (2019X-4, 2021X-1), 日新月异 (2018-2, 2022X-4), 坚实 (2019X-3, 2017-6),
    凝聚 (2023X-17) is used; of the 因地制宜 pair only 2020Z-1 is used (2018-6 must stay away from D12 and its neighbours).
  * cross-round repeats checked before selection (see build4.py): GD2017-10 (遏制 = D01 GD2018-4), GD2018-2 (迸发 = D02
    GD2014X-16), GD2020Z-2 (不仅 更 = D07 GD2020X-2) were left for later days for that reason.
"""

A23X = 'xing-ce1/答案解析/2023年广东省公务员录用考试《行测》题（县级卷）答案解析.pdf'
A20X = 'xing-ce1/答案解析/2020年0809广东公务员考试《行测》真题（县级以上）参考答案及解析.pdf'
A20Z = 'xing-ce1/答案解析/2020年0809广东公务员考试《行测》真题（乡镇）参考答案及解析.pdf'
A19X = 'xing-ce1/答案解析/2019年广东公务员考试《行测》真题（县级）答案及解析.pdf'
A18 = 'xing-ce1/答案解析/2018年广东省公务员录用考试《行测》真题（县级、乡镇统一卷）答案及解析.pdf'
A17 = 'xing-ce1/答案解析/2017年广东公务员考试《行测》真题答案及解析.pdf'

Q23X = 'xing-ce1/真题/2023年广东省公务员录用考试《行测》题（县级卷）.pdf'
Q20X = 'xing-ce1/真题/2020年0809广东公务员考试《行测》真题（县级以上）（7道题暂缺）.pdf'
Q20Z = 'xing-ce1/真题/2020年0809广东公务员考试《行测》真题（乡镇）.pdf'
Q19X = 'xing-ce1/真题/2019年广东公务员考试《行测》真题（县级）.pdf'
Q18 = 'xing-ce1/真题/2018年广东省公务员录用考试《行测》真题（县级、乡镇统一卷）.pdf'
Q17 = 'xing-ce1/真题/2017年广东公务员考试《行测》真题.pdf'

B = '______'
P2 = '（  ）'
P4 = '（    ）'

# pos = fixed position inside its group (pins the delivered IDs). Group GX = 广东选词 (ordered by year, newest first).
# seg = supply segment used for the rotation bookkeeping (2017-18 / 2019-21 / 2022-23); kind = 实词 or 关联词.
# also = other claim keys of the same item that claim.py does not lock by itself (none this round: GD2019X-6 / GD2019Z-5
#        share a dup_group and are locked together automatically; listed in `same_as` for the record).
GD = [
 # ---------------- D10 ----------------
 dict(pos=1, day='D10', topic='选词填空', seg='2022-23', kind='实词', paper='GD2023X', qno=16, file=Q23X, page=4, ans_file=A23X, ans_page=5,
      stem=f'只要坚持生态优先、绿色发展，锲而不舍，{B}，就一定能把绿水青山变成金山银山。',
      prompt='填入画横线部分最恰当的一项是（    ）。',
      options=['点石成金', '水滴石穿', '风雨无阻', '久久为功'], answer='D', fills=['久久为功'],
      chuchu='党建网《学习语｜推动经济社会发展全面绿色转型》', flags=['提示语取自xingce版'],
      same_as=[],
      version_note='xing-ce1 版本题面无提示语，提示语取自 xingce 网友回忆版同题（GD2023X_xc-16），题干与选项两版一致；县级卷独有题（乡镇卷言语第1—5题中无同题）；'
                   '解析第5页起、续至第6页（答案行在第5页，“故正确答案为D”与文段出处在第6页），xingce 版同一解析文字相同',
      value='广东2023县级卷原题；与“锲而不舍”并列的四字格，四项里两项带“石”、一项带“金”，“金山银山”勾着“点石成金”，“水滴石穿”与“锲而不舍”同义但多了结果'),
 dict(pos=2, day='D10', topic='选词填空', seg='2019-21', kind='实词', paper='GD2019X', qno=6, file=Q19X, page=1, ans_file=A19X, ans_page=1,
      stem=f'持续深入的人才发展体制机制改革，为{P4}、{P4}、{P4}、{P4}打牢了坚实基础，有力推进了新时代中国特色社会主义伟大事业不断夺取新的伟大胜利。',
      prompt='',
      options=['引才 聚才 用才 育才', '聚才 用才 育才 引才', '用才 育才 引才 聚才', '育才 引才 聚才 用才'], answer='D',
      fills=['育才', '引才', '聚才', '用才'],
      chuchu='光明日报《爱才敬才成就人尽其才》', flags=[],
      same_as=['GD2019Z-5'],
      version_note='原卷此题无提示语，照原样保留；与乡镇卷第5题（GD2019Z-5）同题（已对两卷原图，题干、选项一致；乡镇卷解析同为D、同一出处）',
      value='广东2019县级卷原题（乡镇卷同题）；四个词只换顺序的排列题，要按人才工作的先后与落点排出“育、引、聚、用”，与本日 HTML 的同组词换序题（广货篇q5、未病先防篇q4）是同一种出法，放在同日作广东锚'),
 dict(pos=3, day='D10', topic='选词填空', seg='2017-18', kind='实词', paper='GD2017', qno=2, file=Q17, page=1, ans_file=A17, ans_page=1,
      stem=f'这些亮相于世界互联网大会的中国创新成果，勾勒出未来生活的诱人{B}，也{B}着“创新中国”的蓬勃生机。',
      prompt='依次填入画横线部分最恰当的一项是：',
      options=['图景 彰显', '图画 呈现', '画面 凸显', '景象 显示'], answer='A', fills=['图景', '彰显'],
      chuchu='《稳重向好，增长更有含金量》', flags=[],
      same_as=[],
      version_note='2017年度县乡统一卷；横线照文字层录作6个下划线',
      value='广东2017卷原题；“勾勒出未来生活的诱人＿”与“＿着蓬勃生机”两处搭配，四组都是“图、景”类名词配“显”类动词，校准广东卷对抽象对象与感情色彩的取舍'),
 # ---------------- D11 ----------------
 dict(pos=1, day='D11', topic='选词填空', seg='2019-21', kind='实词', paper='GD2020X', qno=4, file=Q20X, page=1, ans_file=A20X, ans_page=1,
      stem=f'党的十八大以来，反腐败与改作风{B}、既{B}毒瘤更净化生态，既治病救人更强身健体，共同汇聚成全面从严治党的强劲脉动。',
      prompt='填入划横线部分最恰当的一组是：',
      options=['齐头并进 扫除', '相辅相成 驱除', '一脉相承 去除', '双管齐下 剜除'], answer='D', fills=['双管齐下', '剜除'],
      rate='86%', yicuo='A', chuchu=None, flags=[],
      same_as=[],
      version_note='原卷文件名注“7道题暂缺”，本题完整；原卷第一空后印作顿号（“……改作风＿、既＿毒瘤……”），照原样保留；县级卷独有题（乡镇卷第1—5题中无同题）',
      value='广东2020县级卷原题，解析载全站正确率86%（易错A）：剩余有正确率的实词里第三低；第一空四个成语都能说“两件事一起”，要看“共同汇聚”，第二空“＿毒瘤”四个“×除”只差一个字'),
 dict(pos=2, day='D11', topic='选词填空', seg='2017-18', kind='关联词', paper='GD2018', qno=9, file=Q18, page=1, ans_file=A18, ans_page=2,
      stem=f'中国发展到今天，我们{P2}不需要对西方文明持仰视与全盘肯定的态度，{P2}对传统文化回归的呼唤也必须建立在科学理性的基础上，{P2}不能落入对“己”过于自信与对“他”全然排斥的窠臼。',
      prompt='',
      options=['肯定 但 也', '固然 但 而', '虽然 而 却', '即使 而 又'], answer='B', fills=['固然', '但', '而'],
      chuchu=None, flags=[],
      same_as=[],
      version_note='原卷此题无提示语，照原样保留；县级、乡镇统一卷',
      value='广东2018统一卷原题；三空关联词，先让一步再转折、再正反对举，“固然/虽然”“而/却/又”各只差一层；剩余关联词里唯一的三空转折题，接着 D07 递进、D09 条件换一种关系'),
 # ---------------- D12 ----------------
 dict(pos=1, day='D12', topic='选词填空', seg='2019-21', kind='实词', paper='GD2020Z', qno=1, file=Q20Z, page=1, ans_file=A20Z, ans_page=1,
      stem=f'真正打赢脱贫攻坚战，还需要大力发展优势特色扶贫产业，通过统一规划、连片开发，建设一批特色鲜明、带动能力强的扶贫产业，{B}发展休闲农业、设施农业等农村二三产业。',
      prompt='填入横线部分最恰当的一项是：',
      options=['因势利导', '因地制宜', '因时制宜', '因材施教'], answer='B', fills=['因地制宜'],
      rate='81%', yicuo='A', chuchu=None, flags=[],
      same_as=[],
      version_note='原卷两处逗号印作半角（“扶贫产业,通过”“扶贫产业, ＿”），按本包体例统一为全角；乡镇卷独有题（县级卷第1—5题中无同题）',
      value='广东2020乡镇卷原题，解析载全站正确率81%（易错A）：剩余有正确率的实词里最低的一道；四个“因×”成语，区别在依据的是趋势、地方、时间还是对象'),
 dict(pos=2, day='D12', topic='选词填空', seg='2017-18', kind='实词', paper='GD2018', qno=5, file=Q18, page=1, ans_file=A18, ans_page=1,
      stem=f'总理在两会上所作的政府工作报告是一个{P2}民心、{P2}民意、体现民情的报告，也是一个增强信心、鼓舞士气、催人奋进的报告。',
      prompt='',
      options=['代表 反应', '表现 反映', '表现 反应', '代表 反映'], answer='D', fills=['代表', '反映'],
      chuchu='《为了人民重托——记政府工作报告起草》', flags=[],
      same_as=[],
      version_note='原卷此题无提示语，照原样保留；解析所载出处中的破折号印作“－－”，录作“——”；县级、乡镇统一卷',
      value='广东2018统一卷原题；“代表/表现”“反应/反映”两对形近、音近词的交叉组合，四项各错一半，考词性与搭配对象'),
 dict(pos=3, day='D12', topic='选词填空', seg='2017-18', kind='实词', paper='GD2017', qno=5, file=Q17, page=1, ans_file=A17, ans_page=1,
      stem=f'中央政令下达后，除了加大督查力度，更需要强化政策信息{B}，通过各种渠道让政策为民众所熟知，利用舆论和公众的监督，提高政策执行的{B}。',
      prompt='依次填入画横线部分最恰当的一项是：',
      options=['公布 水平', '发布 速度', '宣传 力度', '公开 效率'], answer='D', fills=['公开', '效率'],
      chuchu='《关注政令不畅现象》', flags=[],
      same_as=[],
      version_note='2017年度县乡统一卷；横线照文字层录作6个下划线',
      value='广东2017卷原题；“强化政策信息＿”四个近义动词（公布、发布、宣传、公开）与“提高政策执行的＿”四个名词的双空互证，同句已有“加大督查力度”'),
]

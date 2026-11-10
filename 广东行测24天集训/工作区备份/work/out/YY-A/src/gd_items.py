# -*- coding: utf-8 -*-
"""GD real-exam items for YY01-YY03, transcribed from the page images (checked against index text).
Blank markers: '______' where the original prints an underline; '（  ）' / '（    ）' where the original prints parentheses.
Every answer was read from the analysis page (scanned pages viewed as images for 2014-2021; text layer for 2022-2025)."""

A25 = 'xing-ce1/答案解析/2025年广东省公务员录用考试《行测》答案及解析.pdf'
A24 = 'xing-ce1/答案解析/2024年广东省公务员录用考试《行测》答案及解析.pdf'
A23X = 'xing-ce1/答案解析/2023年广东省公务员录用考试《行测》题（县级卷）答案解析.pdf'
A23Z = 'xing-ce1/答案解析/2023年广东省公务员录用考试《行测》题（乡镇卷）答案解析.pdf'
A22Z = 'xing-ce1/答案解析/2022年广东公务员考试行测试题（乡镇）答案解析.pdf'
A22X = 'xing-ce1/答案解析/2022年广东公务员考试行测试题（县级）答案解析.pdf'
A21Z = 'xing-ce1/答案解析/2021年0314广东公务员考试《行测》真题（乡镇）参考答案及解析.pdf'
A20X = 'xing-ce1/答案解析/2020年0809广东公务员考试《行测》真题（县级以上）参考答案及解析.pdf'
A20Z = 'xing-ce1/答案解析/2020年0809广东公务员考试《行测》真题（乡镇）参考答案及解析.pdf'
A19X = 'xing-ce1/答案解析/2019年广东公务员考试《行测》真题（县级）答案及解析.pdf'
A18 = 'xing-ce1/答案解析/2018年广东省公务员录用考试《行测》真题（县级、乡镇统一卷）答案及解析.pdf'
A17 = 'xing-ce1/答案解析/2017年广东公务员考试《行测》真题答案及解析.pdf'
A16X = 'xing-ce1/答案解析/2016年广东公务员考试《行测》真题（县级卷）答案及解析.pdf'
A15X = 'xing-ce1/答案解析/2015年广东公务员考试《行测》真题县级卷答案及解析.pdf'
A14X = 'xing-ce1/答案解析/2014年广东公务员考试《行测》真题（县级以上卷）答案及解析.pdf'
A14Z = 'xing-ce1/答案解析/2014年广东省公务员录用考试《行测》题（乡镇）答案及解析.pdf'

Q25 = 'xing-ce1/真题/2025年广东省公务员录用考试《行测》题.pdf'
Q24 = 'xing-ce1/真题/2024年广东省公务员录用考试《行测》题（网友回忆版）.pdf'
Q23X = 'xing-ce1/真题/2023年广东省公务员录用考试《行测》题（县级卷）.pdf'
Q23Z = 'xing-ce1/真题/2023年广东省公务员录用考试《行测》题（乡镇卷）.pdf'
Q22Z = 'xing-ce1/真题/2022年广东公务员考试行测试题（乡镇）.pdf'
Q22X = 'xing-ce1/真题/2022年广东公务员考试行测试题（县级).pdf'
Q21Z = 'xing-ce1/真题/2021年0314广东公务员考试《行测》真题（乡镇）.pdf'
Q20X = 'xing-ce1/真题/2020年0809广东公务员考试《行测》真题（县级以上）（7道题暂缺）.pdf'
Q20Z = 'xing-ce1/真题/2020年0809广东公务员考试《行测》真题（乡镇）.pdf'
Q19X = 'xing-ce1/真题/2019年广东公务员考试《行测》真题（县级）.pdf'
Q18 = 'xing-ce1/真题/2018年广东省公务员录用考试《行测》真题（县级、乡镇统一卷）.pdf'
Q17 = 'xing-ce1/真题/2017年广东公务员考试《行测》真题.pdf'
Q16X = 'xing-ce1/真题/2016年广东公务员考试《行测》真题（县级卷）.pdf'
Q15X = 'xing-ce1/真题/2015年广东公务员考试《行测》真题县级卷.pdf'
Q14X = 'xing-ce1/真题/2014年广东公务员考试《行测》真题（县级及以上）.pdf'
Q14Z = 'xing-ce1/真题/2014年广东省公务员录用考试《行测》题（乡镇）.pdf'

B = '______'
L = '____________'
P2 = '（  ）'
P4 = '（    ）'

# Each item: pos (fixed position inside its group; pins the delivered IDs), day, topic, paper, qno, file, page, ans_file, ans_page, stem (passage), prompt, options, answer,
#            fills (answer words in blank order, for the restored passage), rate, yicuo, chuchu, flags, version_note, value,
#            replaced_from (11-08: in-place replacement of an item from the user-done GD2024-2026 papers)
GD = [
 # ---------------- YY01 ----------------
 dict(pos=1, day='YY01', topic='选词填空', paper='GD2023Z', qno=2, file=Q23Z, page=1, ans_file=A23Z, ans_page=1,
      stem=f'当前，各乡镇纷纷在特色农产品上做文章，但真正能在市场竞争中{B}的，还是那些品类独特、品质优良的农产品。',
      prompt='',
      options=['历久弥新', '脱颖而出', '一枝独秀', '披荆斩棘'], answer='B', fills=['脱颖而出'],
      chuchu='人民日报《别让“盛果期”变成“剩果期”(现场评论)》', flags=[],
      version_note='仅 xing-ce1 有该卷题本（xingce 只有该卷解析）；原卷此题无提示语，照原样保留',
      replaced_from='GD2025-17',
      value='广东2023乡镇卷原题；近义成语的分寸（主体是否唯一），与被替换的GD2025-17同属“说过头”类成语设计'),
 dict(pos=2, day='YY01', topic='选词填空', paper='GD2023X', qno=18, file=Q23X, page=4, ans_file=A23X, ans_page=6,
      stem=f'政府部门要制定政策、营造环境，发挥宣传发动、组织协调、引导扶持作用，但绝不能{B}。要坚持有为政府和有效市场相促进，充分发挥市场机制作用，调动市场主体积极性，以重点产业项目为{B}，促进资源要素更多向乡村流动，以产业“活水”变输血为造血。',
      prompt='依次填入画横线部分最恰当的一项是（    ）。',
      options=['置身事外 核心', '越俎代庖 根本', '大包大揽 载体', '袖手旁观 导向'], answer='C', fills=['大包大揽', '载体'],
      chuchu='《<关于推动文化产业赋能乡村振兴的意见>政策解读》', flags=[],
      version_note='xing-ce1 版本题面无提示语，提示语取自 xingce 网友回忆版同题（GD2023X_xc-18），其余文字两版一致',
      value='广东2023县级卷原题；政府角色“绝不能＿”的成语辨析＋“以…为＿”的名词搭配，双空互证'),
 dict(pos=3, day='YY01', topic='选词填空', paper='GD2020Z', qno=5, file=Q20Z, page=1, ans_file=A20Z, ans_page=1,
      stem=f'近几年，脱贫攻坚取得决定性成就的一个重要原因，就是通过派驻工作组、第一书记等驻村帮扶力量，为贫困农村带去了{B}的领导、{B}的思路，{B}的资源保障，破解了农村发展的人才之困。',
      prompt='填入横线部分最恰当的一项是：',
      options=['强劲 开明 充分', '强硬 明晰 丰富', '坚强 开阔 有力', '坚毅 明确 充沛'], answer='C', fills=['坚强', '开阔', '有力'],
      rate='32%', yicuo='D', chuchu=None, flags=[], version_note='',
      value='广东2020乡镇卷原题，解析载全站正确率仅32%（易错D）：三空形容词分别与“领导/思路/资源保障”搭配，语感与命题人偏差大的一类'),
 dict(pos=4, day='YY01', topic='选词填空', paper='GD2018', qno=4, file=Q18, page=1, ans_file=A18, ans_page=1,
      stem=f'经过五年的不懈努力，群众反映强烈的突出问题得到有效{P2}，不正之风得以扭转，可以说作风建设改变了中国，在全面从严治党历史进程中写下了{P2}的一笔。',
      prompt='',
      options=['遏制 铿锵有力', '遏止 入木三分', '遏止 掷地有声', '遏制 浓墨重彩'], answer='D', fills=['遏制', '浓墨重彩'],
      chuchu='《习近平批示后，中纪委再揭“四风”15个新表现》', flags=[], version_note='原卷此题无提示语，照原样保留',
      value='广东2018统一卷原题；“遏制/遏止”的程度与“写下了＿的一笔”的固定搭配'),
 dict(pos=5, day='YY01', topic='选词填空', paper='GD2016X', qno=23, file=Q16X, page=2, ans_file=A16X, ans_page=4,
      stem=f'新中国成立以来，普通话的推广对于普及教育、提高全民文化素质起到了重要作用，这一点{P4}。但随着普通话的地位越来越重要，各地方言受到很大的冲击。一些汉语方言悄然发生变化，其发音、词汇不断向普通话靠拢；一些汉语方言甚至出现快速{P4}的状况。',
      prompt='',
      options=['无可厚非 式微', '毋庸置疑 衰微', '显而易见 衰减', '不言而喻 衰败'], answer='B', fills=['毋庸置疑', '衰微'],
      chuchu='《方言，你知道多少？》', flags=['老卷(2016年度)'], version_note='原卷此题无提示语，照原样保留',
      value='广东2016县级卷原题（老卷）；评价性成语的语义倾向＋“快速＿”的程度轻重'),
 dict(pos=6, day='YY01', topic='选词填空', paper='GD2014X', qno=17, file=Q14X, page=2, ans_file=A14X, ans_page=4,
      stem=f'以节俭清正{B}奢靡之风，{B}勤俭节约传统美德和“八项规定”，保持质朴和勤俭的本色，刹住公款吃喝，规范接待标准，精简活动规模，杜绝浪费陋习，狠刹挥霍享乐和骄奢淫逸的不良风气。',
      prompt='填入划横线处最恰当的一项是：',
      options=['克制 恪守', '克服 遵守', '克制 遵守', '克服 恪守'], answer='D', fills=['克服', '恪守'],
      rate='22%', yicuo='A', chuchu=None, flags=['老卷(2014年度)'], version_note='解析第4页起、续至第5页',
      value='广东2014县级卷原题（老卷），解析载全站正确率22%（易错A）：动词与对象、程度轻重的双空辨析，语感与命题人分歧极大'),
 dict(pos=1, day='YY01', topic='语句填空', paper='GD2023Z', qno=6, file=Q23Z, page=2, ans_file=A23Z, ans_page=2,
      stem=f'农村生态文明建设，{L}。一是必须加速由高耗能高污染的粗放型农业生产方式向清洁循环的集约型农业发展方式转变，加强农业科技研发与推广应用，建立全产业链绿色化农业发展模式。二是促进农业资源循环利用，积极推进农业清洁生产，提高禽畜养殖废弃物资源化利用。',
      prompt='以下句子填入划横线处，最恰当的是（    ）。',
      options=['必须与美丽乡村建设紧密结合', '必须大力推进绿色循环农业发展', '必须充分利用科技研发促进农业生产', '必须树立“绿水青山就是金山银山”的价值导向'], answer='B', fills=['必须大力推进绿色循环农业发展'],
      chuchu='光明网《农村生态文明建设成就瞩目》', flags=[],
      version_note='仅 xing-ce1 有该卷题本（xingce 只有该卷解析）',
      replaced_from='GD2024-28',
      value='广东2023乡镇卷原题；首句中心句挖空、后文“一是…二是…”分述，与被替换的GD2024-28同一结构'),
 dict(pos=1, day='YY02', topic='选词填空', paper='GD2022Z', qno=5, file=Q22Z, page=1, ans_file=A22Z, ans_page=2,
      stem=f'乡村振兴，关键是产业振兴。因地制宜发展特色产业，大力推动一二三产业融合发展，不断{B}产业链、{B}供应链、{B}价值链，走出一条科学有效、农民受益的产业发展之路。',
      prompt='依次填入横线处最恰当的是：',
      options=['延伸 提升 打造', '延伸 打造 提升', '提升 打造 延伸', '提升 延伸 打造'], answer='B', fills=['延伸', '打造', '提升'],
      chuchu='《乡村振兴关键是产业振兴》', flags=[],
      version_note='仅 xing-ce1 有该卷题本（xingce 只有该卷解析）',
      replaced_from='GD2025-16',
      value='广东2022乡镇卷原题；三空动宾逐项搭配（产业链/供应链/价值链），与被替换的GD2025-16同属逐项对应'),
 dict(pos=2, day='YY02', topic='选词填空', paper='GD2022X', qno=3, file=Q22X, page=1, ans_file=A22X, ans_page=1,
      stem=f'一代代特区建设者{B}、艰苦创业，将昔日落后的边陲小镇、荒滩渔村建成了繁华的现代化城市，在建设中国特色社会主义伟大进程中谱写了勇立潮头、{B}的壮丽篇章。',
      prompt='依次填入画横线部分最恰当的一项是：',
      options=['披荆斩棘 开拓进取', '紧锣密鼓 开天辟地', '一往无前 开云见日', '乘风破浪 开疆拓土'], answer='A', fills=['披荆斩棘', '开拓进取'],
      chuchu='《勇当新时代的“拓荒牛”——发扬特区精神》', flags=[],
      version_note='xing-ce1 版；xingce 网友回忆版（GD2022X_xc-3）同题文字一致（已对图）；解析第1页起、续至第2页',
      replaced_from='GD2024-18',
      value='广东2022县级卷原题；广东特区题材的双成语填空，第二空与“勇立潮头”并列，替换原GD2024-18（湾区题材成语）'),
 dict(pos=3, day='YY02', topic='选词填空', paper='GD2021Z', qno=3, file=Q21Z, page=1, ans_file=A21Z, ans_page=1,
      stem=f'正是广大基层干部群众以无比巨大的热情投入改革，以只争朝夕的劲头{B}改革，以一往无前的勇气探路改革，才令改革开放的大潮澎湃不息，蔚为壮观，{B}出令世界惊叹的成就。',
      prompt='填入横线处的词语最恰当的一项是：',
      options=['推动 创建', '参与 创造', '推进 构建', '参加 制造'], answer='B', fills=['参与', '创造'],
      rate='64%', yicuo='A', chuchu='半月谈《改革开放再出发，基层跑起来》', flags=[], version_note='',
      value='广东2021乡镇卷原题，正确率64%（易错A）：排比中动词与并列项的一致＋“＿出成就”的搭配'),
 dict(pos=4, day='YY02', topic='选词填空', paper='GD2020X', qno=5, file=Q20X, page=1, ans_file=A20X, ans_page=1,
      stem=f'伟大的成就与变革，往往是前所未有的，是{B}的，是惊心动魄的，却没有一个是{B}，是信手拈来的，是一蹴而就的。',
      prompt='填入划横线部分最恰当的一组是：',
      options=['空前绝后 一帆风顺', '开天辟地 空中楼阁', '荡气回肠 轻而易举', '振聋发聩 日行千里'], answer='C', fills=['荡气回肠', '轻而易举'],
      rate='55%', yicuo='A', chuchu=None, flags=[], version_note='原卷文件名注“7道题暂缺”，本题完整；解析第1页起、续至第2页',
      value='广东2020县级卷原题，正确率55%（易错A）：并列结构中的语义照应与成语正反对应'),
 dict(pos=5, day='YY02', topic='选词填空', paper='GD2019X', qno=1, file=Q19X, page=1, ans_file=A19X, ans_page=1,
      stem=f'提升市民的幸福感、获得感是城市治理精细化的根本目的。如果把城市治理比作绣花，那么，以人民为中心的原则就是那条在千头万绪中{P4}城市治理方方面面的线。',
      prompt='',
      options=['疏通', '贯彻', '联合', '串联'], answer='D', fills=['串联'],
      chuchu='《把精细化作为城市治理提质升级重要抓手》', flags=[], version_note='原卷此题无提示语，照原样保留',
      value='广东2019县级卷原题；比喻（绣花之“线”）内部的动词照应'),
 dict(pos=6, day='YY02', topic='选词填空', paper='GD2014X', qno=16, file=Q14X, page=2, ans_file=A14X, ans_page=4,
      stem=f'必须更加注重改革的系统性、整体性、协同性，让一切劳动、知识、技术、管理、资本的活力竞相{B}，让一切创造社会财富的源泉充分{B}，让发展成果更多更公平惠及全体人民。',
      prompt='填入划横线处最恰当的一项是：',
      options=['迸发 涌动', '散发 涌流', '迸发 涌流', '散发 涌动'], answer='C', fills=['迸发', '涌流'],
      rate='42%', yicuo='A', chuchu=None, flags=['老卷(2014年度)'], version_note='',
      value='广东2014县级卷原题（老卷），正确率42%（易错A）：中央文件固定表述“活力竞相＿”“源泉充分＿”'),
 dict(pos=7, day='YY02', topic='选词填空', paper='GD2014Z', qno=32, file=Q14Z, page=3, ans_file=A14Z, ans_page=7,
      stem=f'在过去的十年间，信息技术的飞速发展给当代人的生活、工作方式带来巨大的变革，而{B}这一切的基础——通信网络，在神州大地上实现了{B}式的发展。',
      prompt='填入划横线处最恰当的一项是：',
      options=['建造 飞越', '建造 跨越', '缔造 飞越', '缔造 跨越'], answer='D', fills=['缔造', '跨越'],
      rate='40%', yicuo='C', chuchu=None, flags=['老卷(2014年度)'], version_note='',
      value='广东2014乡镇卷原题（老卷），正确率40%（易错C）：动词与抽象宾语搭配＋“＿式的发展”'),
 dict(pos=1, day='YY02', topic='语句填空', paper='GD2021Z', qno=9, file=Q21Z, page=1, ans_file=A21Z, ans_page=2,
      stem=f'要深深地扎根于人民群众之中，不断从人民群众及其参与的各项实践中汲取营养和力量。正所谓，“{L}”。当前，密切联系群众最直接的要求就是推动广大党员干部走近群众，扑下身子搞好调研，真正了解群众所思所想所盼。从群众关注的烦心事、紧要事和身边事等细微之处入手，及时发现问题、精准研判问题、有效解决问题。',
      prompt='下列句子填入划横线处，最恰当的是：',
      options=['天地之大，黎元为先', '凡治国之道，必先富民', '得众则得国，失众则失国', '知屋漏者在宇下，知政失者在草野'], answer='D', fills=['知屋漏者在宇下，知政失者在草野'],
      rate='61%', yicuo='C', chuchu='中国青年报《牢牢坚守人民情怀》', flags=[],
      version_note='题面跨第1—2页（选项C、D在第2页）',
      replaced_from='GD2025-23',
      value='广东2021乡镇卷原题，正确率61%（易错C）：段中名句承上启下，与被替换的GD2025-23同类'),
 dict(pos=1, day='YY03', topic='选词填空', paper='GD2023X', qno=19, file=Q23X, page=4, ans_file=A23X, ans_page=6,
      stem=f'广东，正在加速打开高质量发展新局面。从上到下，从内到外，从你到我，每个人、每家企业都在全力奔跑，展现出{B}的热烈氛围和{B}的崭新气象。',
      prompt='依次填入画横线部分最恰当的一项是（    ）。',
      options=['龙腾虎跃 意气风发', '一马平川 奋勇当先', '争先恐后 欣欣向荣', '万马奔腾 时不我待'], answer='D', fills=['万马奔腾', '时不我待'],
      chuchu='《再造一个新广东》', flags=[],
      version_note='xing-ce1 版本题面无提示语，提示语取自 xingce 网友回忆版同题（GD2023X_xc-19）；题面跨第4—5页',
      value='广东2023县级卷原题；广东题材的双成语填空，考成语形象与前文语境的照应'),
 dict(pos=2, day='YY03', topic='选词填空', paper='GD2022X', qno=1, file=Q22X, page=1, ans_file=A22X, ans_page=1,
      stem=f'每一寸鲜血浸染的红色热土，每一段感人至深的红色往事，都{B}着艰苦卓绝的牺牲奉献，{B}着气吞山河的壮丽辉煌，是全党全国各族人民弥足珍贵的精神财富。',
      prompt='依次填入画横线部分最恰当的一项是：',
      options=['汇聚 镌刻', '凝聚 描绘', '汇集 勾勒', '凝结 铭刻'], answer='D', fills=['凝结', '铭刻'],
      chuchu='《红色江山永不变色》', flags=[], version_note='xing-ce1 版本；xingce 网友回忆版同题文字一致',
      value='广东2022县级卷原题；动词与抽象宾语（牺牲奉献/壮丽辉煌）的双空搭配'),
 dict(pos=3, day='YY03', topic='选词填空', paper='GD2021Z', qno=4, file=Q21Z, page=1, ans_file=A21Z, ans_page=1,
      stem=f'乡村振兴，必须在人才队伍建设上尽快破题，研究出台乡村振兴引才专项政策，打通农业人才服务基层的{B}，{B}基层农业人才的发展空间等。一些地方的农校、政府已经在通过鼓励学生“下地”、农民“上学”等方式，为基层农技岗位输送人才。',
      prompt='填入横线处的词语最恰当的一项是：',
      options=['禁锢 扩张', '渠道 增长', '脉络 扩展', '桎梏 提升'], answer='C', fills=['脉络', '扩展'],
      rate='70%', yicuo='D', chuchu='半月谈《学农不务农，过半农科生想转行，“农技人才荒”掣肘乡村振兴》', flags=[], version_note='',
      value='广东2021乡镇卷原题，正确率70%（易错D）：“打通…的＿”与“＿…发展空间”的搭配辨析'),
 dict(pos=4, day='YY03', topic='选词填空', paper='GD2017', qno=4, file=Q17, page=1, ans_file=A17, ans_page=1,
      stem=f'一个人的成长成才，并不完全由其起点决定，而是看在这个过程之中个人所付出的努力。如果一味{B}“出生在农村，注定样样落后”，不仅是对一些客观事实选择性地无视，而且{B}了个人奋斗的价值。',
      prompt='依次填入画横线部分最恰当的一项是：',
      options=['鼓吹 漠视', '宣扬 肯定', '渲染 抹杀', '鼓励 否定'], answer='C', fills=['渲染', '抹杀'],
      chuchu='《警惕“宿命论”正义感背后的负能量》', flags=[], version_note='',
      value='广东2017卷原题；动词的感情色彩与“不仅…而且＿了”的递进程度'),
 dict(pos=5, day='YY03', topic='选词填空', paper='GD2015X', qno=7, file=Q15X, page=1, ans_file=A15X, ans_page=2,
      stem=f'某市推出“自住型商品房”，意在{B}涨价预期，但由于自住型商品房用地进一步{B}了普通商品房用地，使得商品房地价一再上涨。',
      prompt='填入划横线部分最恰当的一项是：',
      options=['平抑 缩减', '制止 挤压', '抑制 压缩', '平抑 挤压'], answer='D', fills=['平抑', '挤压'],
      chuchu='京地价三级跳明年房价难摁住', flags=['老卷(2015年度)'], version_note='',
      value='广东2015县级卷原题（老卷）；动词与“预期”“用地”的搭配及句子主干分析'),
 dict(pos=6, day='YY03', topic='选词填空', paper='GD2014X', qno=20, file=Q14X, page=2, ans_file=A14X, ans_page=5,
      stem=f'“四风”问题的形成是一个长期的过程，具有反复性和顽固性，其背后是{B}的陈旧观念、{B}的“潜规则”、{B}的利益纠结。',
      prompt='填入划横线处最恰当的一项是：',
      options=['根深蒂固 习以为常 错综复杂', '盘根错节 习以为常 扑朔迷离', '盘根错节 司空见惯 扑朔迷离', '根深蒂固 司空见惯 错综复杂'], answer='A', fills=['根深蒂固', '习以为常', '错综复杂'],
      rate='46%', yicuo='D', chuchu=None, flags=['老卷(2014年度)'], version_note='',
      value='广东2014县级卷原题（老卷），正确率46%（易错D）：三空成语分别对应“观念/潜规则/利益纠结”'),
 dict(pos=7, day='YY03', topic='选词填空', paper='GD2014Z', qno=38, file=Q14Z, page=3, ans_file=A14Z, ans_page=8,
      stem=f'我们身边有许许多多优秀基层干部，把自己的生命无私地投入于百姓的幸福生活，他们闪光的足迹，就是最{B}的表述和最{B}的注解。',
      prompt='填入划横线处最恰当的一项是：',
      options=['生动 透彻', '深刻 透彻', '生动 精辟', '深刻 精辟'], answer='C', fills=['生动', '精辟'],
      rate='44%', yicuo='A', chuchu=None, flags=['老卷(2014年度)'], version_note='解析第8页起、续至第9页',
      value='广东2014乡镇卷原题（老卷），正确率44%（易错A）：“最＿的表述/注解”的形容词搭配'),
 dict(pos=1, day='YY03', topic='语句填空', paper='GD2022X', qno=7, file=Q22X, page=1, ans_file=A22X, ans_page=3,
      stem=f'国有企业作为中国特色社会主义经济制度重要载体，是我国经济社会发展的中坚力量。当前，国有企业改革和发展面临新问题和新挑战，特别是在全面建成小康社会，开启建设社会主义现代化国家新征程的重要历史交汇时刻，国有企业以“{L}”的顽强意志，把企业党建建在实处，应对好每一场重大风险挑战，提高企业效益、增强企业竞争实力，实现又好又快发展，成为改革的主力军和先行者。',
      prompt='下列句子填入画横线处，最恰当的是：',
      options=['踏平坎坷成大道，斗罢艰险又出发', '山重水复疑无路，柳暗花明又一村', '没有比人更高的山，没有比脚更长的路', '世上无难事，只要肯登攀'], answer='A', fills=['踏平坎坷成大道，斗罢艰险又出发'],
      chuchu='《国企党建要握“根”聚“魂”》', flags=['版本差异(一字)'],
      version_note='xing-ce1 版本作“国有企业以“…”的顽强意志”；xingce 粉笔网友回忆版（GD2022X_xc-7）作“国有企业要以“…”的顽强意志”，一字之差，不影响作答；此处用 xing-ce1 版；解析第3页起、续至第4页',
      value='广东2022县级卷原题；句中嵌入名句（“以‘＿’的顽强意志”），与同日人民时评篇末引语题对照'),
]

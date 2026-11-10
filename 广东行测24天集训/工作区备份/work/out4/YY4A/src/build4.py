# -*- coding: utf-8 -*-
"""Build YY4A deliverables (round 4: 言语 D10-D12 选词填空 + 语句填空) -> questions.jsonl, articles.jsonl, checks.txt.
Adapted from the round-3 YY3A script (/home/user/work/out3/YY3A/src/build3.py). Read-only on all sources:
  - GD items: gd_items4.py (transcribed from page images; answers read from the analysis pages)
  - HTML items: the user's HTML (script#data JSON); blanks/answers taken from the source data and re-checked here
    (the text at every blank position of the re-assembled paragraph must equal the reference-answer option).
What is new compared with round 3:
  - cross-round repeat check reads the delivered questions.jsonl of rounds 1-3 (so the 11-08 replacements of round 1 are
    covered) and reports equal answers AND answers that contain / are contained in an earlier answer;
  - single-character answers (this round: 翼 / 基 / 魂) are not searched as bare substrings (a single character is in
    almost every stem); they are searched as the collocation "为X" instead;
  - HTML articles already used are taken from the claim registry as well as from rounds 1-3;
  - a list of answers that repeat inside this round, and of options repeated on the same day (information only).
Run: python3 build4.py   (writes into /home/user/work/out4/YY4A/)"""
import json, re, sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gd_items4 import GD

OUT = '/home/user/work/out4/YY4A'
PREFIX = 'YY4A'
DAYS = ['D10', 'D11', 'D12']
HTML_FILE = 'xing-ce1/学习资料/盖句精读（词句新版·全151篇·手机版）(2).html'
PREV_Q = [('R1', '/home/user/work/out/YY-A/questions.jsonl'),       # D01-D03 (after the 11-08 replacements)
          ('R2', '/home/user/work/out2/YY2A/questions.jsonl'),      # D04-D06
          ('R3', '/home/user/work/out3/YY3A/questions.jsonl')]      # D07-D09
CLAIMS = '/home/user/work/out/claims.jsonl'


def _load_html():
    raw = open('/home/user/' + HTML_FILE, encoding='utf-8').read()
    m = re.search(r'<script id="data" type="application/json">(.*?)</script>', raw, re.S)
    return json.loads(m.group(1))


D = _load_html()
ART = {a['id']: a for a in D}


def ptext(para):
    return ''.join(sg.get('t', sg.get('m', '')) for sg in para)


# ---- HTML plan: day -> [(article id, {qid: [extra context paragraph numbers]})]; every article is used whole (no skipped question).
# Each article was read in full with the blanks masked before it was accepted (see the report for the rejected ones).
# This round 45 of the 46 questions are answered from the blank's own paragraph; one context paragraph is added
# (大家谈 q2: the cue named by the source note is the opening example in paragraph 5; that paragraph carries no answer
# of another question - checked below by the same-day leak check).
PLAN = {
    'D10': [('nf20260212_10163099', {'q1': [], 'q2': [], 'q3': [], 'q4': [], 'q5': []}),
            ('20260814_30174907', {'q1': [], 'q2': [], 'q3': [], 'q4': [], 'q5': []}),
            ('20251222_30126193', {'q1': [], 'q2': [], 'q3': [], 'q4': [], 'q5': []})],
    'D11': [('nf20261008_10182982', {'q1': [], 'q2': [], 'q3': [], 'q4': [], 'q5': [], 'q6': []}),
            ('20260508_30155603', {'q1': [], 'q2': [], 'q3': [], 'q4': [], 'q5': []}),
            ('20260903_30178833', {'q1': [], 'q2': [], 'q3': [], 'q4': [], 'q5': []})],
    # D12: the article first chosen as the second one, 20260817_30175302 (评论员观察《练好“钉钉子”的功夫》, 2选3语), was
    # taken out again: its q5 answer “定力” stands in the passage of GD2016X-30, which YY4B has planned for D12, and its
    # answer “大局” stands in paragraph 3 of the 经济特区 article. In merged order R1 (片段 before the H groups) the first
    # would be a same-day leak. It is replaced by 20260422_30152558 (大家谈, 2选3语); the 钉钉子 article stays unused
    # (claims released) for a later day - see HTML_VALUE_RESERVE below and the report.
    'D12': [('nf20260911_10181143', {'q1': [], 'q2': [], 'q3': [], 'q4': []}),
            ('20260422_30152558', {'q1': [], 'q2': [5], 'q3': [], 'q4': [], 'q5': []}),
            ('20260126_30135630', {'q1': [], 'q2': [], 'q3': [], 'q4': [], 'q5': [], 'q6': []})],
}

HTML_VALUE = {
 # D10 ① 南方日报·评论 2026-02-12《“广货”这样“行天下”》
 ('nf20260212_10163099', 'q1'): '南方日报评论2026-02-12（广货行天下）；“现代化产业体系＿”的四字格，四项方向都对、差在成熟度，要与空前“全部31个制造业大类”“约160种全国第一”的分量相称，“方兴未艾”最顺口（与q2同段，互相以“另题”遮蔽）',
 ('nf20260212_10163099', 'q2'): '同篇；例子证明什么的归纳词，前有“一小时产业圈”、后有“10天走完过去两个月的流程”，上一句“把成本控制到极致”勾着“价格优势”',
 ('nf20260212_10163099', 'q3'): '同篇；“其一”一层的收束半句，要回应层首的“知之有限”，干扰项分别取自“其二”“其三”两层和“平、靓、正”（与q4同段，互相遮蔽）',
 ('nf20260212_10163099', 'q4'): '同篇；“有效需求不足与供给＿不足的矛盾”，由后文的药方“畅通产销对接、打通流通堵点”倒推病名，“多样性”被上一层的“多样化需求”勾出',
 ('nf20260212_10163099', 'q5'): '同篇；“以科技创新为＿、以产业优势为＿、以文化内涵为＿”三个单字的对号排列，四项只是同三字换序，“创新是灵魂”的熟话是陷阱；与本日广东题 GD2019X-6 同一种出法',
 # D10 ② 人民日报·评论员观察 2026-08-14《善治之道，在“未病先防”》
 ('20260814_30174907', 'q1'): '人民日报评论员观察2026-08-14（基层治理“治未病”）；段尾收束半句，要回答段首设问“为啥居民没投诉”，B项接住“邻里陌生”却答不了设问',
 ('20260814_30174907', 'q2'): '同篇；第一空接“异常信号”的比喻先筛掉两项，第二空在“察”与“防”之间分高下，“未雨绸缪”属防，“明察秋毫”只有细、没有由小见大',
 ('20260814_30174907', 'q3'): '同篇；段首俗语填空，后接“解决基层矛盾往往如此”与“不让小事拖大、大事拖炸”，要选讲处置时机的一句，“千里之堤，溃于蚁穴”只讲危害',
 ('20260814_30174907', 'q4'): '同篇；三个心理名词各配一个修饰语（“万一没事”“怕麻烦缠身”“只图眼下清净”），四项为同三词换序，B项只对调后两词',
 ('20260814_30174907', 'q5'): '同篇；篇末古语填空，后句“防范在先、发现在早、处置在小”是三层，四句都与治病有关，最贴标题的“不治已病治未病”只有一层且与“处置在小”相反',
 # D10 ③ 人民日报·思想纵横 2025-12-22《为基层减负要“瘦身”更要“提质”》
 ('20251222_30126193', 'q1'): '人民日报思想纵横2025-12-22（为基层减负）；“表面看时间线抓得很紧，实则……徒做虚功、＿”的反转，“劳而无功”与并列的“徒做虚功”语义重复',
 ('20251222_30126193', 'q2'): '同篇；段首引语填空，紧跟的解读句“根源仍在于……理想信念”要求引语同时管住信念与作风并分出本末，B项也有“根本”二字（与q3同段，互相遮蔽）',
 ('20251222_30126193', 'q3'): '同篇；“跳不出路径依赖，缺乏‘＿’的智慧”，两个“钥匙”说法只差一个对比点，“一把钥匙开一把锁”针对的是一刀切而不是守旧',
 ('20251222_30126193', 'q4'): '同篇；两个带引号的说法各被前文一句锁住：“预留必要的完成时间”对第一空，“一刀切”“千篇一律”对第二空，“朝令夕改”字面最像',
 ('20251222_30126193', 'q5'): '同篇；长句末尾的落点句，本段骨架是“瘦身的目的是提质”，检验减负的尺子要量结果，A项量的是“瘦身”本身',
 # D11 ① 南方日报·理论周刊·专论 2026-10-08《在“第二个结合”中激发岭南文化创新创造活力》
 ('nf20261008_10182982', 'q1'): '南方日报理论周刊2026-10-08（“第二个结合”与岭南文化）；一串追问中的第三问，后一问以“这些精神结构”回指，空里必须先出现所指，D项把后一问的意思提前说了',
 ('nf20261008_10182982', 'q2'): '同篇；分号对举的后半句，前半是“地方文化只有被放回文明母体”，后半须把主语和方向倒过来，C项主语对、内容却离开了“地方”',
 ('nf20261008_10182982', 'q3'): '同篇；四个例子之后的三字格评语，A项“可识别、可展示、可消费”是本篇q1题干里作者批评过的标签，要逐个核例子（“乐于参与”“进入日常消费”）',
 ('nf20261008_10182982', 'q4'): '同篇；“历史岭南同现代广东之间形成更加深刻的文化＿”，空前结构框住的是“之间”的关系，后句“在延续中更新”作解，“主体性”“包容性”是全文高频词',
 ('nf20261008_10182982', 'q5'): '同篇；三组“既能够……又能够……”排比的第一组后半，要从没遮的两组归纳规律（对象不变、回到自己的立场），D项“读懂中国”换了对象',
 ('nf20261008_10182982', 'q6'): '同篇；“不再只是作为符号＿于产品，而是进一步深入……之中”，前半要的是浅的一头，三个更好听的干扰项（融入、渗透、贯穿）说的都是后半句的意思',
 # D11 ② 人民日报·人民时评 2026-05-08《“向东看”见证中国感召力》
 ('20260508_30155603', 'q1'): '人民日报人民时评2026-05-08（“访华潮”与中国感召力）；“一个巧合是，A与B＿”，“不谋而合”也有未经约定之意，但说的是想法一致而不是时间上碰到一起',
 ('20260508_30155603', 'q2'): '同篇；段尾“正如……所言”的引语要替本段作结，段首定调是“连续性和稳定性”“可预期的确定性”，B项“最具吸引力的投资目的地”只说吸引力、不说靠得住',
 ('20260508_30155603', 'q3'): '同篇；“重启闲置工厂并创造上千个就业岗位，成为西班牙＿的标杆项目”，例子挂在“以绿色发展为例”之下，“绿色转型”最顺手',
 ('20260508_30155603', 'q4'): '同篇；三个“面对……中国……”排比的中间一项，要与“提出四点主张”“提出全球治理倡议”同向并接住段尾“稳定器”，B项“对等反制”最像新闻用语',
 ('20260508_30155603', 'q5'): '同篇；引语里顺着前文“地图”打的比方，空里要同时接住喻体和毛病（中心放错、带偏见），“有色的眼镜”是现成说法却换了喻体',
 # D11 ③ 人民日报·评论员观察 2026-09-03《取舍之间显格局》
 ('20260903_30178833', 'q1'): '人民日报评论员观察2026-09-03（地方发展的取舍）；“到头来很容易‘＿’”说的是结局，前文的“产业跟风”是开头，只差一字的“一哄而上”把时间说倒了',
 ('20260903_30178833', 'q2'): '同篇；四个经济学“××成本”的辨析，前提是“土地、资金等要素都是有限的”，后半句“错失的还有转型机会”用一个“还”字照应',
 ('20260903_30178833', 'q3'): '同篇；典故“田忌赛马，胜在＿”，以弱胜强、出奇制胜都是这个典故能讲的道理，要看紧跟的“摸透自身情况、熟悉外部格局”（与q4同段，互相遮蔽）',
 ('20260903_30178833', 'q4'): '同篇；“面对竞争红海，不妨更灵活地寻找＿，在一米宽中掘出万米深”，空后半句即是解释，前一句“警惕脱离实际的盲从”排除“下一个风口”',
 ('20260903_30178833', 'q5'): '同篇；两个按时间写的例子之后的古语收束，“持续向前看、向上攀、向智转”的共同点是变，“不畏浮云遮望眼”贴着“向前看、向上攀”却只有眼界',
 # D12 ① 南方日报·评论 2026-09-11《奋力把新时代经济特区办得更好办得水平更高》
 ('nf20260911_10181143', 'q1'): '南方日报评论员文章2026-09-11（深圳经济特区）；段首对句“昔日滩涂渔火，今日＿”的后半，要接住前半“火”与“光”的意象，“高楼林立”是写深圳的熟套（与q2同段，互相遮蔽）',
 ('nf20260911_10181143', 'q2'): '同篇；“国家战略＿”“人才红利＿”两处主谓搭配，第一空看上一句三重定位落在同一座城，第二空“红利”配“释放”，D项只把两个词对调',
 ('nf20260911_10181143', 'q3'): '同篇；“把扩内需、＿的工作摆在更加重要位置”，并列空要看紧跟的展开（扩大有效投资、促进消费、夯实制造业家底），“稳外贸”是与“扩内需”连用的熟搭配',
 ('nf20260911_10181143', 'q4'): '同篇；末段段首诗句填空，要领起下一句“永葆‘闯’的精神、‘创’的劲头、‘干’的作风”，四句都有风浪或新旧意象，A项调子最像、却是对将来的信心',
 # D12 ② 人民日报·大家谈 2026-04-22《以实干成效检验学习成效》（三篇来稿）
 ('20260422_30152558', 'q1'): '人民日报大家谈2026-04-22（以实干成效检验学习成效，三篇来稿）；四个都能与“开”搭配的说法（空头支票、绿灯、小灶、先例），要靠并列的“不吊高胃口”和前句“华而不实的目标”定意思',
 ('20260422_30152558', 'q2'): '同篇；第一篇来稿的收尾引语，四项都是讲干部的熟语，只有一项是“贪大求快、急于求成”做过头的后果；题干加第5段（开头的事例：盲目上马项目、设备闲置浪费）作上下文',
 ('20260422_30152558', 'q3'): '同篇；“把精力用在＿上，而非真抓实干上”，“走过场”同属形式主义、最像，却与“把精力用在”相矛盾，线索是“包装出政绩”“干得好不如总结得好”',
 ('20260422_30152558', 'q4'): '同篇；带引号的群众话，四句都是便民服务的老毛病，只有一句与后面的对症办法（工作日延时2小时、周末预约）咬合，“门难进、脸难看、事难办”最出名',
 ('20260422_30152558', 'q5'): '同篇；引号里的心态要由紧跟的“满足于完成规定动作、工作不出差错”来验证，“事不关己、高高挂起”贴着前句“不管不顾”却解释不了后半',
 # D12 ③ 人民日报·评论员观察 2026-01-26《立足生活激发文化之力》
 ('20260126_30135630', 'q1'): '人民日报评论员观察2026-01-26（文化赋能）；“宏观视角与微观感受＿”四个“相×”成语，要分清两样东西之间是佐证、依存、衬托还是成趣',
 ('20260126_30135630', 'q2'): '同篇；“从来不喝咖啡的人……尝试之后发现‘＿’，逐渐形成……习惯”，“逐渐”与“培养”管住分寸，“欲罢不能”说过了头（与q3同段，互相遮蔽）',
 ('20260126_30135630', 'q3'): '同篇；与“和睦礼让”并列的四字格，要由“谦让墙”的做法（先想到行人会被磕着，再改自家墙角）来定，“舍己为人”分量过重',
 ('20260126_30135630', 'q4'): '同篇；“之所以陷入＿的窠臼，一个重要原因是只模仿古街镇之形”，空里是毛病的表现而不是原因，下一句的“生搬硬套”是现成陷阱',
 ('20260126_30135630', 'q5'): '同篇；“嫦娥奔月的古老传说，＿，助力缔造新时代登月传奇”，要补上传说到成就之间“人心”这一环并接住段尾“没有什么梦想不能实现”，B项说的是真事却构不成助力',
 ('20260126_30135630', 'q6'): '同篇；例子与下一句之间的回环句，下一句“既能让赋能对象焕发新生，也将助推文化繁荣发展”是两个方向，C项只讲融合的方式',
}

# Read, accepted, NOT used this round (claims released): value lines kept for the editor who places it later.
# Placement constraints: q5 answers 大局 / 准头 / 定力 - no earlier stem of that day (YY*B 片段 included) may carry
# “定力” or “大局”; q2 offers “一把钥匙开一把锁” as a distractor (so does 基层减负 q3, used on D10).
HTML_VALUE_RESERVE = {
 # 人民日报·评论员观察 2026-08-17《练好“钉钉子”的功夫》（2选3语，五题都只看本段即可作答）
 ('20260817_30175302', 'q1'): '人民日报评论员观察2026-08-17（钉钉子与抓落实）；引号里是一种错误认识，要选能推出后半句“大政方针事不关己”的说法，“最后一公里”是基层工作高频词却推不出懈怠',
 ('20260817_30175302', 'q2'): '同篇；俗语填空，前一句给事（“样样都缺”时率先解决三大问题）、后一句给理（把资源集中到最紧要的点上），“一把钥匙开一把锁”讲对症而不是取舍',
 ('20260817_30175302', 'q3'): '同篇；“看似在敲，＿”要把“换一任就兜底翻”翻回钉钉子的比喻，四项都是“实则是……”的另一种敲法，只有一项对上“换一任”',
 ('20260817_30175302', 'q4'): '同篇；引文中夹在“实干精神”与“希图侥幸成功的投机心理”之间的俗语，前一头只能排掉一半，要靠“侥幸”“投机”定（与q5同段，互相遮蔽）',
 ('20260817_30175302', 'q5'): '同篇；“胸中有＿、手上有＿、心里有＿”三词换序的排列题，每个词被一个身体部位管着（同一种出法见 D10 广东题 GD2019X-6）',
}

EXTRA_NOTES = {
 ('nf20260212_10163099', 'q5'): '【数据】三个空都是单字（翼、基、魂）。泄题检查不按单字子串查（单字几乎见于任何题干），改查“为翼”“为基”“为魂”搭配，本日前面题干中无。',
 ('nf20261008_10182982', 'q3'): '【编排】A项“可识别、可展示、可消费”见于本组第1题（q1）题干，是源数据原有的设计（作者在该段批评过的标签），照录未改。',
 ('nf20261008_10182982', 'q4'): '【编排】答案“连续性”在本日后面的 H2 第2题题干中出现（“连续性和稳定性”），在后不在前，不算泄题；H1、H2 两组不得对调。另：南方日报评论员文章 2026-05-08（nf20260508_10169767，未用）第1题答案也是“连续性”，后续不要排在 D11 的相邻日。',
 ('20260508_30155603', 'q2'): '【编排】本题题干含“连续性和稳定性”，“连续性”是本日前一组（H1）第4题的答案；该题在前，本题在后，不算泄题。',
 ('20260422_30152558', 'q2'): '【上下文】题干加第5段：原站解析以开头的事例（某县盲目上马施肥项目、设备闲置浪费）作为本空依据，第8段本身只有一句；第5段不含本篇其他题的答案。',
}
GD_EXTRA_NOTES = {
 ('GD2023X', 16): '【编排】留作后用的广东语句题 GD2019X-12 题干含“久久为功”，与本题相隔多日，无碍。',
 ('GD2019X', 6): '【编排】本日 HTML 有两道同组词换序题（H1 第5题、H2 第4题），本题是同一种出法的广东原题，放在同日 GX 作锚。题干含“坚实基础”：GD2019X-3、GD2017-6（答案都含“坚实”）不得与本题同日（本轮未用）。',
 ('GD2020X', 4): '【编排】GD2021Z-5（＝GD2021X-3，答案“一脉相承 诠释”）与本题共用“一脉相承”“相辅相成”两个选项词，且“诠释”是 D08 GD2020Z-4 的答案，后续不要排在 D12、D13，宜放 D18 以后。GD2017-1（反腐题材，答案“决心 勇气”）与本题同题材，不排相邻日。',
 ('GD2018', 9): '【编排】关联词按“隔天1道”放在 D11（上两道在 D07、D09），其后 D13、D15……D23 各1道，剩余6道正好用完。',
 ('GD2020Z', 1): '【编排】GD2018-6（答案“因地制宜 扩大 提高”）与本题答案重合，不得排在 D12 的相邻日（D13），建议隔5天以上。“因地制宜”在 D01、D02、D05、D09 的题干里出现过（常用语，非答案）。',
 ('GD2018', 5): '【编排】题干含“体现民情”：GD2018-1（答案“章程 体现”）不得与本题同日（本轮未用）。',
}

# evidence crops made by mk_assets4.py (question region at 200 dpi, other printings of the same item, analysis lines)
_ev = os.path.join(OUT, 'assets/src/_index.json')
EVID = json.load(open(_ev)) if os.path.exists(_ev) else {}

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


def load_prev():
    """Answers (blank by blank) and stems of every question delivered for D01-D09, plus the HTML articles already used."""
    prev_ans, prev_stems, prev_articles = [], [], set()
    for tag, path in PREV_Q:
        for l in open(path):
            if not l.strip():
                continue
            q = json.loads(l)
            day = q.get('official_day') or q['day']
            where = f"{tag} {day} {q['id']} {q['source']['paper']}-{q['source']['qno']}"
            if q['source']['paper'].startswith('HTML'):
                aid = q['source']['article_id']
                prev_articles.add(aid)
                a = ART[aid]
                qq = [x for x in a['q'] if x['id'] == str(q['source']['qno']).split(':')[1]][0]
                t = ptext(a['paras'][qq['p'] - 1])
                fills = [t[b['b']:b['e']] for b in qq['blanks']]
            elif q.get('answer_text'):
                fills = list(q['answer_text'])
            else:
                opt = q['options'][q['checked_answer']]
                fills = opt.split(' ') if q['topic'] == '选词填空' else [opt]
            for f in fills:
                prev_ans.append((f, where))
            prev_stems.append((q['stem'], where))
    for l in open(CLAIMS):
        if not l.strip():
            continue
        c = json.loads(l)
        if c['key'].startswith('HTML:') and c['owner'] != PREFIX:
            prev_articles.add(c['key'].split(':')[1])
    return prev_ans, prev_stems, prev_articles


def main():
    os.makedirs(OUT, exist_ok=True)
    prev_ans, prev_stems, prev_articles = load_prev()
    questions, articles = [], []
    n = 0

    def nid():
        nonlocal n
        n += 1
        return f'{PREFIX}-{n:03d}'

    for day in DAYS:
        # ---- GD group: GX (选词, 按年份由近及远). No GD 语句 this round (the 3 remaining ones are kept for D13/14, D18, D22/23).
        gd_x = sorted([g for g in GD if g['day'] == day and g['topic'] == '选词填空'], key=lambda g: g['pos'])
        assert not [g for g in GD if g['topic'] != '选词填空'], 'no GD 语句 this round'
        assert [g['pos'] for g in gd_x] == list(range(1, len(gd_x) + 1)), (day, [g['pos'] for g in gd_x])
        yrs = [int(g['paper'][2:6]) for g in gd_x]
        assert yrs == sorted(yrs, reverse=True), (day, 'GX title says 按年份由近及远', yrs)
        gname, gtitle = f'{day}-GX', '广东真题·选词填空（按年份由近及远）'
        for order, it in enumerate(gd_x, 1):
            aid = f"ART-GD-{it['paper']}-{it['qno']}"
            restored = gd_restore(it)
            stem = it['stem'] + (('\n' + it['prompt']) if it['prompt'] else '')
            yr = int(it['paper'][2:6])
            assert 2017 <= yr <= 2023, it['paper']                       # never GD2024-2026, never 2013-2016 this round
            ans_letter = it['answer']
            ans_opt = it['options']['ABCD'.index(ans_letter)]
            assert ' '.join(it['fills']) == ans_opt, (it['paper'], it['qno'], it['fills'], ans_opt)
            if yr <= 2021:
                ans_how = '扫描件，出图目读'
            else:
                ans_how = '文字层，并与 answers/%s.json、xingce 版同一解析一致' % it['paper']
            q = dict(
                id=nid(), module='言语', day=day, official_day=day, group=gname, group_title=gtitle,
                topic=it['topic'], order=order,
                source=dict(paper=it['paper'], file=it['file'], page=it['page'], qno=it['qno'],
                            ans_file=it['ans_file'], ans_page=it['ans_page'], version_note=it['version_note'],
                            same_as=list(it.get('same_as') or [])),
                source_kind='真题原题（广东省考）',
                done_status='已做情况未知', stem=stem,
                options={k: v for k, v in zip('ABCD', it['options'])},
                material_or_article=aid, assets=[],
                source_answer=ans_letter, checked_answer=ans_letter, brief_solution='',
                selection_value=it['value'], variant_of=None, check_status='已核验',
                flags=list(it['flags']),
                notes=('言语只做数据完整性与原文对应检查：题面已对原卷页图（200dpi 题区截图）逐字核对，并与文字层逐字比对一致；'
                       '原参考答案取自解析第%s页（%s）。' % (it['ans_page'], ans_how)
                       + (f"解析载全站正确率{it['rate']}、易错项{it['yicuo']}。" if it.get('rate') else '解析未载正确率。')
                       + (f"解析所载文段出处：{it['chuchu']}。" if it.get('chuchu') else '解析未载文段出处。')
                       + '原卷无争议标记。原文为据参考答案回填的恢复文段，非外部原文；外部原文' + ('待补（有出处、无正文）。' if it.get('chuchu') else '无出处可查。')
                       + f"供给段：{it['seg']}（{it['kind']}）。"
                       + GD_EXTRA_NOTES.get((it['paper'], it['qno']), '')),
                source_rate=it.get('rate'), source_yicuo=it.get('yicuo'), source_passage_title=it.get('chuchu'),
                claim_key=f"{it['paper']}-{it['qno']}",
                source_image=EVID.get(f"{it['paper']}-{it['qno']}", []),     # evidence crops, for checking only (not in `assets`)
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
                    ans_letter, (f"解析所载文段出处：{it['chuchu']}；外部原文待补（只有出处、没有正文；本会话未放行外网报刊站点，未检索、未仿写）。"
                                 if it.get('chuchu') else '解析未载文段出处，外部原文无从查找。'))))
        # ---- HTML article groups
        for hidx, (aid_src, qmap) in enumerate(PLAN[day], 1):
            a = ART[aid_src]
            assert aid_src not in prev_articles, (aid_src, 'article already used in D01-D09 or claimed by another editor')
            assert a['kind'] != 'cs', (aid_src, '常识类文章不用')
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
                assert len(q['options']) == 4 and len(set(q['options'])) == 4, (aid_src, q['id'], 'options')
                ctx_desc = '仅本段' if len(pnos) == 1 else ('本段＋' + '、'.join(f'第{x}段' for x in pnos if x != q['p']))
                qq = dict(
                    id=nid(), module='言语', day=day, official_day=day, group=gname, group_title=gtitle,
                    topic=q['kind'], order=order,
                    source=dict(paper='HTML盖句精读', file=HTML_FILE, page=None, qno=f"{aid_src}:{q['id']}",
                                ans_file=HTML_FILE, ans_page=None,
                                version_note=f"HTML 内嵌 JSON（script#data）文章 {aid_src} 的 q 列表 {q['id']}；空在第{q['p']}段，字符位置 " +
                                             '；'.join(f"{b['b']}–{b['e']}" for b in q['blanks']),
                                article_id=aid_src, para=q['p'], blanks=q['blanks'], context_paras=pnos),
                    source_kind='用户HTML题（%s·%s）' % (a['src'], a['col']),
                    done_status='已做情况未知', stem=stem,
                    options={k: v for k, v in zip('ABCD', q['options'])},
                    material_or_article=aid, assets=[],
                    source_answer=letter, checked_answer=letter, brief_solution='',
                    selection_value=HTML_VALUE[(aid_src, q['id'])], variant_of=None, check_status='已核验',
                    flags=(['多空'] if len(q['blanks']) > 1 else []) + (['同段另题遮蔽'] if has_other else [])
                          + (['加上下文段'] if len(pnos) > 1 else []),
                    notes=('言语只做数据完整性与原文对应检查：已用程序核对该段拼接原文在空缺位置的文字＝选项%s（%s）。题干上下文：%s，原文照录未改写；同篇其他入选题的空缺以“（另题）”遮蔽。原文 %s 须待本组各题做完再看。原站解析存于 source_note（原始备份，不进训练答案册）。源数据无争议标记。' % (
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
                                       why='本会话网络不能访问报刊原站（paper.people.com.cn、epaper.southcn.com 不在会话放行域名内：curl 经代理 CONNECT 返回 403，WebFetch 报域名不可解析；11-09 重测仍然如此），未与外部原文逐字比对'),
                note=('据用户 HTML 源数据（paras 中 t/m 片段按序拼接）还原的原文段落，未改写；各题空缺处的原文用词即在段中。未与报刊原站逐字比对。'
                      f"本篇入选题：{'、'.join(sorted(sel, key=lambda x: int(x[1:])))}；本篇全部题目均入选。"
                      '原文须待本篇各题做完后再看。原站解析（note）不随原文展示。')))

    # ---------------- checks ----------------
    log = []
    by_day = collections.defaultdict(list)
    for q in questions:
        by_day[q['day']].append(q)
    # (1) leak check: no answer string of a question appears in any EARLIER stem of the same day
    leaks, one_char = [], []
    for day, qs in by_day.items():
        for i, q in enumerate(qs):
            for f in q['_fills']:
                if len(f) == 1:
                    one_char.append((q['id'], f))
                    if f not in '但而也更又却才就':        # function words of a 关联词 item cannot be "leaked" by a stem
                        for p in qs[:i]:
                            if ('为' + f) in p['stem']:
                                leaks.append((day, q['id'], '为' + f, 'earlier stem (single-character answer, collocation)', p['id']))
                    continue
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
    log.append(f'[info] single-character answers (content words searched as “为X”, 关联词 function words not searched): {len(one_char)}')
    for x in one_char:
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
    #      the key, but the word has been seen; listed for information)
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
    # (2c) the same option string offered by two questions of the same day (information)
    same_opt = []
    for day, qs in by_day.items():
        seen = {}
        for q in qs:
            for k, v in q['options'].items():
                for w in v.split(' ') if q['topic'] == '选词填空' else [v]:
                    if len(w) < 2:
                        continue
                    if w in seen and seen[w] != q['id']:
                        same_opt.append((day, w, seen[w], q['id']))
                    seen.setdefault(w, q['id'])
    log.append(f'[info] option words offered by two questions of the same day: {len(same_opt)}')
    for x in same_opt:
        log.append('   ' + repr(x))
    ZW = re.compile('[​‌‍⁠﻿]')
    zw = [(q['id'], 'stem' if ZW.search(q['stem']) else 'options') for q in questions
          if ZW.search(q['stem']) or any(ZW.search(v or '') for v in q['options'].values())]
    log.append(f'[info] zero-width characters in stems/options: {len(zw)}')
    for x in zw:
        log.append('   ' + repr(x))
    zwa = [(a['aid'], i + 1) for a in articles for i, p in enumerate(a.get('paras') or []) if ZW.search(p)]
    log.append(f'[info] zero-width characters in article paragraphs outside the stems (copied verbatim): {len(zwa)}')
    for x in zwa:
        log.append('   ' + repr(x))
    # (2d) answers repeated inside this round
    seen = {}
    rep_in = []
    for q in questions:
        for f in q['_fills']:
            if len(f) < 2:
                continue
            if f in seen and seen[f][0] != q['id']:
                rep_in.append((f, seen[f], (q['id'], q['day'])))
            seen.setdefault(f, (q['id'], q['day']))
    log.append(f'[info] answers used twice inside this round (D10-D12): {len(rep_in)}')
    for x in rep_in:
        log.append('   ' + repr(x))
    # (3) cross-round repeats: answers equal to / containing / contained in an answer of D01-D09 (YY-A, YY2A, YY3A)
    rep_eq, rep_sub = [], []
    for q in questions:
        for f in q['_fills']:
            if len(f) < 2:
                continue
            for pf, where in prev_ans:
                if len(pf) < 2:
                    continue
                if f == pf:
                    rep_eq.append((q['id'], q['day'], f, where))
                elif f in pf or pf in f:
                    rep_sub.append((q['id'], q['day'], f, pf, where))
    log.append(f'[repeat] answers identical to a D01-D09 answer: {len(rep_eq)}')
    for x in rep_eq:
        log.append('   ' + repr(x))
    log.append(f'[info] answers that contain / are contained in a D01-D09 answer (common words inside sentence answers): {len(rep_sub)}')
    for x in rep_sub:
        log.append('   ' + repr(x))
    seen_prev = []
    for q in questions:
        for f in q['_fills']:
            if len(f) < 3:
                continue
            for st, where in prev_stems:
                if f in st:
                    seen_prev.append((q['id'], f, where))
    log.append(f'[info] answers (3+ characters) that were visible in a D01-D09 stem: {len(seen_prev)}')
    for x in seen_prev:
        log.append('   ' + repr(x))
    log.append(f'[repeat] HTML articles already used in D01-D09 or claimed by others: 0 of {sum(len(v) for v in PLAN.values())} (asserted; {len(prev_articles)} articles on the used list)')
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
        nf = [aid for aid, _ in PLAN[day] if ART[aid]['src'] == '南方日报']
        assert len(PLAN[day]) == 3 and len(nf) == 1, (day, 'three articles a day, one of them 南方日报')
        log.append(f'[count] {day}: 选词 {tc["选词填空"]} 语句 {tc["语句填空"]}；HTML 3 篇（南方日报 {len(nf)}）')
    ctx = sum(1 for q in questions if len(q['source'].get('context_paras') or []) > 1)
    log.append(f'[count] questions {len(questions)} articles {len(articles)}; HTML questions with an added context paragraph: {ctx}')
    assert all(q['brief_solution'] == '' and q['checked_answer'] == q['source_answer'] for q in questions)
    assert len({q['id'] for q in questions}) == len(questions) == 54

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

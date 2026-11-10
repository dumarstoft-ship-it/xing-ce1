import json, re, os, sys, shutil
SP = '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/yyb'
OUT = '/home/user/work/out/YY-B'
sys.path.insert(0, SP + '/tools'); sys.path.insert(0, SP)
from qx import get, raw, crop
from clean import clean
from patches import P
plan = json.load(open(f'{SP}/plan.json'))
REPLACED = json.load(open(f'{SP}/replaced.json'))
drafts = json.load(open(f'{SP}/drafts.json'))
scan = {}
for l in open(f'{SP}/scan_answers.jsonl'):
    if l.strip():
        r = json.loads(l); scan[r['key']] = r
CIRC = '①②③④⑤⑥⑦⑧'
ANSF = {
 'GD20131': 'xing-ce1/答案解析/2013年广东公务员考试《行测》一卷答案及解析.pdf',
 'GD20133': 'xing-ce1/答案解析/2013年广东公务员考试《行测》三卷答案及解析.pdf',
 'GD2014X': 'xing-ce1/答案解析/2014年广东公务员考试《行测》真题（县级以上卷）答案及解析.pdf',
 'GD2014Z': 'xing-ce1/答案解析/2014年广东省公务员录用考试《行测》题（乡镇）答案及解析.pdf',
 'GD2015X': 'xing-ce1/答案解析/2015年广东公务员考试《行测》真题县级卷答案及解析.pdf',
 'GD2015Z': 'xing-ce1/答案解析/2015年广东公务员考试《行测》真题乡镇卷答案及解析.pdf',
 'GD2016X': 'xing-ce1/答案解析/2016年广东公务员考试《行测》真题（县级卷）答案及解析.pdf',
 'GD2016Z': 'xing-ce1/答案解析/2016年广东公务员考试《行测》真题（乡镇卷）答案及解析.pdf',
 'GD2017': 'xing-ce1/答案解析/2017年广东公务员考试《行测》真题答案及解析.pdf',
 'GD2018': 'xing-ce1/答案解析/2018年广东省公务员录用考试《行测》真题（县级、乡镇统一卷）答案及解析.pdf',
 'GD2019X': 'xing-ce1/答案解析/2019年广东公务员考试《行测》真题（县级）答案及解析.pdf',
 'GD2019Z': 'xing-ce1/答案解析/2019年广东公务员考试《行测》真题（乡镇级）答案及解析.pdf',
 'GD2020X': 'xing-ce1/答案解析/2020年0809广东公务员考试《行测》真题（县级以上）参考答案及解析.pdf',
 'GD2020Z': 'xing-ce1/答案解析/2020年0809广东公务员考试《行测》真题（乡镇）参考答案及解析.pdf',
 'GD2021Z': 'xing-ce1/答案解析/2021年0314广东公务员考试《行测》真题（乡镇）参考答案及解析.pdf',
 'GD2021X': 'xing-ce1/答案解析/2021年0314广东公务员考试《行测》真题（县级）参考答案及解析.pdf',
 'GD2022X': 'xing-ce1/答案解析/2022年广东公务员考试行测试题（县级）答案解析.pdf',
 'GD2022Z': 'xing-ce1/答案解析/2022年广东公务员考试行测试题（乡镇）答案解析.pdf',
 'GD2023X': 'xing-ce1/答案解析/2023年广东省公务员录用考试《行测》题（县级卷）答案解析.pdf',
 'GD2023Z': 'xing-ce1/答案解析/2023年广东省公务员录用考试《行测》题（乡镇卷）答案解析.pdf',
 'GD2024': 'xing-ce1/答案解析/2024年广东省公务员录用考试《行测》答案及解析.pdf',
 'GD2025': 'xing-ce1/答案解析/2025年广东省公务员录用考试《行测》答案及解析.pdf',
 'GK2025D': 'xing-ce1/国考/答案解析/2025年国考《行测》（地市级）答案+解析.pdf',
 'GK2024F': 'xing-ce1/国考/答案解析/2024年国考《行测》（副省级）答案+解析.pdf',
 'GK2023F': 'xing-ce1/国考/答案解析/2023年国家公务员录用考试《行测》真题（副省级）（解析）.pdf',
 'GK2022D': 'xing-ce1/国考/答案解析/2022年国家公务员考试《行测》真题（市地级）【答案+解析】...pdf',
 'GK2022F': 'xing-ce1/国考/答案解析/2022年国家公务员考试《行测》真题（副省级）【答案+解析】...pdf',
 'SD2024': 'xingce/2024年山东省公务员录用考试《行测》答案+解析_decrypted.pdf',
 'JS2023A': 'xingce/2023年江苏公务员考试《行测》真题（A类）解析.pdf',
 'ZJ2025A': 'xingce/2025年浙江省公务员录用考试《行测》题（A类）（网友回忆版）解析.pdf',
 'SC2025': 'xingce/2025年四川省考_选调公务员录用考试《行测》答案及解析.pdf',
 'GK2021D': 'xing-ce1/国考/答案解析/2021年国家公务员考试《行测》真题（市地级）参考答案及解析...pdf',
 'SD2022': 'xingce/2022年山东省公务员录用考试《行测》答案+解析_decrypted.pdf',
}
# text-layer answers verified against analysis text in this session
TXT = {
 'GD2022X-8': ('D', 4, '《实现平台经济更加规范更有活力更高质量发展》'),
 'GD2022X-9': ('B', 4, '《赶时间的人，永远没时间》'),
 'GD2022Z-7': ('D', 3, '《脱贫攻坚精神的价值意蕴》'),
 'GD2023X-22': ('C', 7, '求是网《坚持党的全面领导推进一流大学建设》'),
 'GD2023X-25': ('C', 8, '《构建新发展格局要处理好辩证关系》《经济日报》（2021年12月29日10版）'),
 'GD2023Z-9': ('A', 3, '《善于运用网络了解民意开展工作》'),
 'GD2024-21': ('A', 6, '《讲述多姿多彩的中国故事》'),
 'GD2024-26': ('D', 7, '新华网《布局更完善 科创力更足——粤港澳大湾区建设纵深推进一线扫描》'),
 'GD2025-21': ('A', 11, '人民日报《完善城乡融合发展体制机制 形成城乡融合发展新格局》'),
 'GD2025-22': ('B', 11, '人民日报《着力提升抓好改革落实的能力（思想纵横）》'),
 'GD2025-24': ('C', 12, '人民网《增进中马合作深化“稻水之情”（大使随笔·推动构建人类命运共同体）》'),
 'GD2024-30': ('C', 8, '《挖掘好利用好工业文化资源（新论）》'),
 'GD2022X-10': ('B', 5, '《要让孩子懂得“愁”滋味》'),
 'GK2025D-55': ('A', 19, '学习时报《建立行政执法与刑事司法“无缝衔接”机制》'),
 'GK2024F-47': ('C', 16, '《习近平：加快建设农业强国 推进农业农村现代化》'),
 'GK2023F-41': ('D', '13-14', '《重建中华五千年气候史》'),
 'GK2022D-47': ('C', 17, '求是网《南水北调事关战略全局、长远发展、人民福祉》'),
 'GK2022F-40': ('D', 14, '求是网《习近平总书记“考古公开课”的15个要点》'),
 'SD2024_xc-49': ('D', 16, '人民网《推动北斗加速融入千行百业》'),
 'JS2023A_xc-30': ('C', 16, None),
 'ZJ2025A_xc-33': ('D', 15, '光明网《刘斌：良渚文化与中华五千年文明》'),
 'SC2025_xc-45': ('A', 24, '中国非物质遗产网《老字号遗产资源的转化及其价值》'),
 # 11-08 replacements (user has done GD2024-2026 papers)
 'GD2023Z-8': ('C', 3, '人民网《强化烈士纪念设施的教育功能（新论）》'),
 'GD2022Z-8': ('A', 3, '《强镇兴村，探索乡村全面振兴广东路径》'),
 'GD2023X-23': ('A', 8, '新华社《城市更新要建好历史文化传承体系》'),
 'GD2022Z-10': ('C', 4, '《大数据与生态史信息化时代中国灾害史料整理与数据库建设》'),
 'GK2021D-51': ('C', 15, None, 78, 'A'),
 'SD2022_xc-33': ('D', 10, '《人民日报连发五篇文章谈“共同富裕”，都在这里面》'),
}
TOPIC = {
 'GD2023Z-9':'意图判断','GD20131-26':'意图判断','GD2017-11':'意图判断','GD2014X-21':'细节判断','GD2020X-7':'标题填入','GD20133-35':'意图判断','GD2018-13':'主旨概括','GD2014Z-52':'意图判断','GD2021Z-8':'主旨概括','GD20131-27':'词句理解','GD2019X-11':'主旨概括','GD2015X-11':'意图判断','GD2022X-8':'主旨概括','GD2016X-26':'意图判断','GD20131-32':'意图判断','GD2014Z-54':'主旨概括','GD2024-26':'标题填入','GD2025-21':'主旨概括',
 'GD2022X-9':'细节判断','GD20131-29':'主旨概括','GD2017-14':'主旨概括','GD2014X-34':'意图判断','GD2018-15':'意图判断','GD20133-43':'主旨概括','GD2019X-15':'细节判断','GD2014Z-51':'主旨概括','GD2020X-8':'意图判断','GD2016Z-12':'细节判断','GD2021X-10':'标题填入','GD2015X-13':'意图判断','GD2023X-25':'主旨概括','GD20131-42':'主旨概括','GD2014Z-53':'细节判断','GD2016X-28':'意图判断','GD2014X-37':'下文推断','GD2024-21':'意图判断',
 'GD2022Z-7':'主旨概括','GD20131-38':'意图判断','GD2019Z-7':'主旨概括','GD2014X-38':'主旨概括','GD2020Z-10':'意图判断','GD20133-45':'主旨概括','GD2021X-9':'意图判断','GD2015Z-11':'词句理解','GD2020X-10':'细节判断','GD2014X-39':'意图判断','GD2021Z-10':'意图判断','GD20131-45':'主旨概括','GD2023X-22':'标题填入','GD2015X-17':'意图判断','GD20133-42':'下文推断','GD2016X-35':'主旨概括','GD2014Z-55':'标题填入','GD2025-22':'主旨概括',
 'GD2023Z-8':'主旨概括','GD2022Z-8':'主旨概括','GD2023X-23':'意图判断','GD2022Z-10':'主旨概括'}
PAPER_CN = {'GD20131':'2013年度广东一卷','GD20133':'2013年度广东三卷','GD2014X':'2014年度广东县级以上卷','GD2014Z':'2014年度广东乡镇卷','GD2015X':'2015年度广东县级卷','GD2015Z':'2015年度广东乡镇卷','GD2016X':'2016年度广东县级卷','GD2016Z':'2016年度广东乡镇卷','GD2017':'2017年度广东卷','GD2018':'2018年度广东县乡统一卷','GD2019X':'2019年度广东县级卷','GD2019Z':'2019年度广东乡镇卷','GD2020X':'2020年度广东县级以上卷','GD2020Z':'2020年度广东乡镇卷','GD2021X':'2021年度广东县级卷','GD2021Z':'2021年度广东乡镇卷','GD2022X':'2022年度广东县级卷','GD2022Z':'2022年度广东乡镇卷','GD2023X':'2023年度广东县级卷','GD2023Z':'2023年度广东乡镇卷','GD2024':'2024年度广东卷','GD2025':'2025年度广东卷',
 'GK2025D':'2025年度国考地市级','GK2024F':'2024年度国考副省级','GK2023F':'2023年度国考副省级','GK2022D':'2022年度国考地市级','GK2022F':'2022年度国考副省级','SD2024':'2024年度山东卷','JS2023A':'2023年度江苏A类','ZJ2025A':'2025年度浙江A类','SC2025':'2025年度四川卷','GK2021D':'2021年度国考地市级','SD2022':'2022年度山东卷'}

JUNK = [r'免费获取更多考公资料[^\n]*', r'(?m)^\s*\d+\s*/\s*\d+\s*$', r'·\s*本试卷由粉笔用户[^\n]*', r'\d{4}年广东省公务员录用考试《行测》题[（(]网友回忆版[)）]', r'【[^】]*资料库】[^\n]*',
        r'第\s*\d+\s*页[，,]?\s*共\s*\d+\s*页']
def parse_px(t):
    for j in JUNK: t = re.sub(j, '', t)
    t = t.replace('　', ' ').replace('\xa0', ' ')
    # drop stray page-number / qno-only lines and broken vertical page footers
    lines = [l for l in t.split('\n') if l.strip() and not re.fullmatch(r'\s*(\d{1,3}\.?|页|共|，|第|\d)\s*', l)]
    t = '\n'.join(lines)
    t = re.sub(r'^\s*\d{1,3}\s*[、\.．]\s*(?=[①-⑧将])', '', t.strip())
    t = re.sub(r'^\s*\d{1,3}\s*[、\.．]?\s*\n', '', t)
    t = t.replace('（单选题）', '')
    om = list(re.finditer(r'([A-D])\s*[\.．、]\s*([①-⑧]{4,8})', t))
    opts = {m.group(1): m.group(2) for m in om}
    body = t[:om[0].start()]
    pm = re.search(r'(将(?:以上|下列|以下|上述)[^\n]*?(?:是|为)[^\n]*)', body)
    prompt = re.sub(r'\s+', '', pm.group(1)) if pm else ''
    prompt_first = bool(pm) and body.find(pm.group(1)) < body.find('①')
    body2 = body.replace(pm.group(1), '') if pm else body
    chunks = [c for c in re.split(r'(?=[①-⑧])', body2) if c.strip() and c.strip()[0] in CIRC]
    sents = [re.sub(r'\s+', '', c) for c in chunks]
    return sents, prompt, prompt_first, opts

def flags_notes(key):
    f, n = [], []
    if key == 'GD20131-26': f.append('争议(原标)')
    if key == 'GD2014X-34':
        f.append('原文疑似笔误(未改)'); n.append('原题本作“妻子的发型是么时候换了”“将跌到的老人搀扶起来”，疑为“什么时候”“跌倒”之误；照录未改。')
    if key == 'GD2014Z-55':
        f.append('原文疑似脱字(未改)'); n.append('原题本末句作“得分也要高于运动的对照组”，疑脱“不”字；照录未改。')
    if key == 'GD2019Z-7': n.append('首句“但这样不是促使农业农村的‘消亡’”语句如原题本，照录。')
    if key == 'GD2020X-10': n.append('“讲述自己的故事、身边的故事、我们就能……”中第二个顿号如原题本，照录。题本文字层把选项B、C排在同一行，已按原页拆分。')
    if key in ('GD2020X-8', 'GD2014X-21', 'GD2015X-11', 'GD2016X-28'): n.append('题本文字层选项换行错位，已按原页图像逐项拆分核对。')
    if key == 'GD2025-22':
        f.append('版本差异')
        n.append('两个题本措辞不同：xing-ce1《2025年广东省公务员录用考试《行测》题》作“又要打破传统定义，跳出路径依赖，干前人没干过的事。根据实践需要……”（与 xing-ce1 配套解析引文一致）；xingce 网友回忆版作“又要打破思维定式、跳出路径依赖，干前人没干过的事，根据实践需要……”，并有“经验主义”“硬骨头”加引号等差异。D项用语为“打破思维定式”，与后者一致，本包采用 xingce 版文字。两版选项、答案（B）相同。')
    if key == 'GD2025-21': n.append('xingce 网友回忆版“不掉队、逐步赶上来”为顿号，其余与 xing-ce1 题本一致。')
    if key == 'GD2025-24':
        f.append('版本差异')
        n.append('xing-ce1 题本④句作“帮助当地民众园粮食自给自足之梦”（“圆”误作“园”）；采用 xingce 网友回忆版“圆”。两版选项、答案（C）相同。')
    if key.startswith('GD2021X'):
        f.append('扫描件人工录入')
        n.append('该题本为扫描件、无文字层；题干与选项由编者据原页图像逐字录入并复核，未改动用字。')
    if key in ('GD2024-21', 'GD2024-26', 'GD2024-30'): f.append('网友回忆版')
    if key in ('GD2025-22', 'GD2025-24', 'ZJ2025A_xc-33'): f.append('网友回忆版')
    DUP = {'GD2020X-7': 'GD2020Z-7（乡镇卷同题，原解析答案同为B）', 'GD20131-29': 'GD20133-33（三卷同题，答案同为A）', 'GD20131-42': 'GD20133-26（三卷同题）',
           'GD20131-45': 'GD20133-34（三卷同题，答案同为D）', 'GD2019X-11': 'GD2019Z-10（乡镇卷同题，答案同为A）', 'GD2019X-15': 'GD2019Z-8（乡镇卷同题，答案同为A）',
           'GD2022X-9': 'GD2022Z-9（乡镇卷同题，答案同为B）', 'GD2023X-22': 'GD2023Z-10（乡镇卷同题，答案同为C）', 'GD2015X-17': 'GD2015Z-16（乡镇卷同题）',
           'GD2016X-26': 'GD2016Z-14（乡镇卷同题，答案同为C）', 'GK2024F-47': 'GK2024D-57、GK2024X-52（三卷同题，答案同为C）', 'GK2025D-55': 'GK2025X-62（同题，答案同为A）',
           'GK2022D-47': 'GK2022X-51（同题）'}
    if key in DUP: n.append('同题亦见 ' + DUP[key] + '；已一并登记占用。')
    if key == 'GD2022Z-7': n.append('同日（YY03）YY-A 用 HTML《“精准”的要义》（精准扶贫主题），与本题主题相近；已核对双方题干与选项，本题文段不含对方任何设问答案，对方材料也不提供本题选项间的区分信息，判为非泄题；如求稳可与别日主旨题对调。')
    if key == 'GD2022Z-8': n.append('原拟放 YY01，因同日 YY-A-007（GD2023Z-6）的干扰项D含“绿水青山就是金山银山”，为免互相提示改放 YY03。')
    if key == 'GD2020Z-10': n.append('注意：GD2020Z-9（政务公开）与 GD2020X-2（选词）同一文段，后续排题勿同日使用。')
    return f, n

def norm_text(s):
    s = s.replace('　', ' ').replace('\xa0', ' ')
    s = re.sub(r'(?<=[0-9A-Za-z%])\s+(?=[一-鿿“”（）])', '', s)
    s = re.sub(r'(?<=[一-鿿，。、”“])\s+(?=[0-9A-Za-z])', '', s)
    s = re.sub(r'[（(]\s*[）)]', '（    ）', s)
    s = re.sub(r'（\s+）', '（    ）', s)
    s = s.replace('······', '……').replace('......', '……')
    return s.strip()

def outlet(cc):
    if not cc: return None
    for o in ['人民日报', '人民网', '求是网', '新华网', '新华社', '光明网', '光明日报', '经济日报', '半月谈', '学习时报', '南方日报', '中国青年报']:
        if o in cc: return o
    return None

def page_list(segs): return sorted({s[0] + 1 for s in segs})

def selval(key, pid, topic, rate, yicuo, cc, kind):
    base = f"{PAPER_CN.get(pid, pid)}原题（{topic}）"
    ex = []
    if key == 'GD20131-26': ex.append('原解析标注为争议题，保留原答案与原备注，供体会广东卷“递进重点”取向')
    if rate is not None: ex.append(f"原解析全站正确率{rate}%、易错项{yicuo}")
    if key in ('GD2020X-7', 'GD2024-26'): ex.append('广东本地题材')
    if key == 'GD2022Z-8': ex.append('原解析出处为广东乡村振兴报道')
    o = outlet(cc)
    if o and kind == 'pd': ex.append(f"文段出自{o}")
    if pid in ('GD2024', 'GD2025') and kind == 'pd': ex.append('2024年度起90题新卷型的片段')
    if kind == 'px':
        PXT = {'GD2025-24': '广东卷4句短排序（2024年度起新卷出现的形式），援外农业合作题材',
               'GD2024-30': '广东卷6句排序，工业文化资源题材', 'GD2022X-10': '广东卷6句排序，家庭教育题材',
               'GK2024F-47': '国考补量；粮食节约减损，党政时评取材', 'SD2024_xc-49': '外省补量；北斗应用，科技成就类时评（人民网）',
               'GK2022F-40': '国考补量；考古与历史文化遗产（求是网）', 'GK2022D-47': '国考补量；水资源与南水北调（求是网）',
               'JS2023A_xc-30': '外省补量；非遗纪录片，文化类', 'GK2023F-41': '国考补量；气候史与文明演变，文化科普类',
               'GK2025D-55': '国考补量；行政执法与刑事司法衔接，法治类（学习时报）', 'ZJ2025A_xc-33': '外省补量；良渚文化与中华文明，文化类（光明网）',
               'SC2025_xc-45': '外省补量；老字号文化，文化类',
               'GK2021D-51': '国考补量；垃圾分类与城市治理，社会治理类；原解析全站正确率78%、易错项A',
               'SD2022_xc-33': '外省补量；共同富裕，党政理论类（出处为人民日报系列文章）'}
        return f"{PAPER_CN.get(pid, pid)}原题；{PXT[key]}。"
    return base + ('；' + '；'.join(ex) if ex else '') + '。'

def ans_info(key, pid):
    if key in TXT:
        t = TXT[key]; a, pg, cc = t[:3]; rt, yc = (t[3], t[4]) if len(t) > 3 else (None, None)
        return dict(ans=a, ans_page=pg, chuchu=cc, rate=rt, yicuo=yc, dispute=None)
    sk = key if key in scan else None
    r = scan[sk]
    return dict(ans=r['ans'], ans_page=r.get('ans_page'), chuchu=r.get('chuchu'), rate=r.get('rate'), yicuo=r.get('yicuo'), dispute=r.get('dispute'))


EXT = {  # WebSearch results (links only; page bodies could not be fetched in this session)
 'GD2025-21': ('https://paper.people.com.cn/rmrb/html/2024-10/16/nw.D110000renmrb_20241016_4-09.htm', '人民日报2024年10月16日第9版，上官子健《完善城乡融合发展体制机制 形成城乡融合发展新格局》'),
 'GD2025-22': ('https://paper.people.com.cn/rmrb/html/2024-08/16/nw.D110000renmrb_20240816_2-09.htm', '人民日报2024年8月16日第9版，黎春秋《着力提升抓好改革落实的能力（思想纵横）》'),
 'GD2024-21': ('https://paper.people.com.cn/rmrb/html/2023-11/07/nw.D110000renmrb_20231107_2-18.htm', '人民日报2023年11月7日，《讲述多姿多彩的中国故事（新语）》（检索摘要显示原文与题干个别措辞或有出入，未核对）'),
 'GD2024-26': ('https://szb.nanhaitoday.com/epaper/zjsb/html/2023-10/04/content_7414.htm', '检索到的是2023年10月4日南海网电子报转载页《布局更完善 科创力更足》，非新华网原页'),
 'GD2025-24': ('https://world.huanqiu.com/article/4JFEsqQTkr2', '检索到的是环球网转载的“大使随笔”《增进中马合作 深化“稻水之情”》（作者季平），非人民网原页'),
}
SEARCHED_NOT_FOUND = {'GD2021X-10', 'GD2023X-22', 'GD2024-30', 'GD2019X-11'}
NETNOTE = '本会话网络不允许访问 paper.people.com.cn、www.nopss.gov.cn 等原文站点（WebFetch 被拒），无法抓取正文逐字核对，故不照录外部原文；题干文段未作任何改写。'
def ext_note(key):
    if key in EXT: return EXT[key][0], f'外部原文：经 WebSearch 检索到链接——{EXT[key][1]}；正文未抓取、未逐字核对。' + NETNOTE
    if key in SEARCHED_NOT_FOUND: return None, '外部原文：已用 WebSearch 按出处标题检索，未找到对应原文。' + NETNOTE
    return None, '外部原文：未检索。' + NETNOTE

QFILE_2021X = 'xing-ce1/真题/2021年0314广东公务员考试《行测》真题（县级）.pdf'
recs, arts = [], []
os.makedirs(OUT + '/assets/src', exist_ok=True)
n = 0
DAYMAP = {'YY01': 'D01', 'YY02': 'D02', 'YY03': 'D03'}
from PIL import Image
for day in ['YY01', 'YY02', 'YY03']:
    for gk, glabel in (('pd', '片段阅读'), ('px', '语句排序')):
        for order, key in enumerate(plan[day][gk], 1):
            n += 1; rid = f'YY-B-{n:03d}'
            tag, q = key.rsplit('-', 1); q = int(q); pid = tag.replace('_xc', '')
            pkey = f'{pid}-{q}'
            use_alt = key in ('GD2025-22',)
            if gk == 'pd':
                if pid == 'GD2021X':
                    stem, opts = P[key]['stem'], P[key]['options']; qfile = QFILE_2021X
                    pages = [1, 2] if q == 9 else [2]; crop_src = None
                else:
                    d = drafts[key]
                    if use_alt:
                        qa = get('GD2025_xc', q); stem, opts = clean(raw(qa)); qfile = qa['file']; pages = page_list(qa['segs'])
                        crop_src = f'{SP}/crops/GD2025_xc-{q}.png'
                    else:
                        stem, opts = d['stem'], d['options']; qfile = d['file']; pages = page_list(d['segs']); crop_src = f'{SP}/crops/{key}.png'
                    if key in P:
                        stem = P[key].get('stem', stem); opts = P[key].get('options', opts)
                stem = norm_text(stem); opts = {k: norm_text(v) for k, v in opts.items()}
                assert opts and set(opts) == set('ABCD'), key
                topic = TOPIC[key]
            else:
                qtag = 'GD2025_xc' if key == 'GD2025-24' else tag
                qq = get(qtag, q); sents, prompt, pf, opts = parse_px(raw(qq)); qfile = qq['file']; pages = page_list(qq['segs'])
                crop_src = f'{SP}/crops/{qtag}-{q}.png'
                prompt = norm_text(prompt)
                stem = (prompt + '\n' + '\n'.join(sents)) if pf else ('\n'.join(sents) + '\n' + prompt)
                topic = f'语句排序（{len(sents)}句）'
            ai = ans_info(key if key in TXT else pkey, pid)
            if ai['ans'] is None: raise SystemExit('no ans ' + key)
            flags, notes = flags_notes(key)
            replaced_from = REPLACED.get(key)
            if replaced_from:
                notes.append(f'11-08 原位替换：原题 {replaced_from} 出自用户已做的广东 2024–2026 年度卷，按“已做情况记录.md”换为本题，编号与组内位置不变。')
            if pid == 'GD2021X' and gk == 'pd': pass
            aid = f'YYA-{pid}-{q}'
            # crop asset
            dst = f'assets/src/{rid}.png'
            if pid == 'GD2021X':
                a = Image.open(f'{SP}/crops/GD2021X-9a.png'); b = Image.open(f'{SP}/crops/GD2021X-9b10.png')
                if q == 9:
                    c = Image.new('RGB', (max(a.width, b.width), a.height + b.height), 'white'); c.paste(a, (0, 0)); c.paste(b, (0, a.height)); c.convert('L').save(f'{OUT}/{dst}', optimize=True)
                else:
                    b.convert('L').save(f'{OUT}/{dst}', optimize=True)
            else:
                Image.open(crop_src).convert('L').save(f'{OUT}/{dst}', optimize=True)
            vnote = None
            if 'xingce/' in qfile and '网友回忆版' in qfile: vnote = '网友回忆版'
            elif '网友回忆版' in qfile: vnote = '网友回忆版'
            if pid == 'GD2021X': vnote = '扫描件（无文字层），编者据原页图像录入'
            src = {'paper': pid, 'file': qfile, 'page': pages[0], 'pages': pages, 'qno': q,
                   'ans_file': ANSF.get(pid), 'ans_page': ai['ans_page'], 'version_note': vnote}
            rec = {'id': rid, 'module': '言语', 'day': day, 'day_official': DAYMAP[day],
                   'group': f'{day}-{"PD" if gk == "pd" else "PX"}', 'group_title': f'{glabel}·{"广东真题" if gk == "pd" else "广东真题与公考真题"}',
                   'topic': topic, 'order': order, 'source': src, 'done_status': '已做情况未知',
                   'stem': stem, 'options': opts, 'material_or_article': aid, 'assets': [], 'source_crop': dst,
                   'source_answer': ai['ans'], 'checked_answer': ai['ans'], 'source_rate': ai['rate'], 'source_yicuo': ai['yicuo'],
                   'source_chuchu': ai['chuchu'], 'dispute_note': ai['dispute'],
                   'brief_solution': '', 'selection_value': selval(key, pid, topic, ai['rate'], ai['yicuo'], ai['chuchu'], gk),
                   'variant_of': None, 'check_status': '已核验', 'flags': flags, 'notes': '；'.join(notes) if notes else '',
                   'replaced_from': replaced_from}
            recs.append(rec)
            # article object
            if gk == 'pd':
                cc = ai['chuchu']
                url, en = ext_note(key)
                art = {'aid': aid, 'kind': 'source_ref' if cc else 'no_source',
                       'source': {'paper': pid, 'qno': q, 'chuchu_from_analysis': cc, 'ans_file': ANSF.get(pid), 'ans_page': ai['ans_page'], 'external_url': url},
                       'title': (re.sub(r'^.*?《', '《', cc) if cc else None), 'text': None,
                       'note': (f'原解析【文段出处】：{cc}。' if cc else '原解析未给文段出处，原标题无从恢复。') + en}
            else:
                order_str = opts[ai['ans']]
                smap = {s[0]: s[1:] for s in sents}
                seq = [smap[c] for c in order_str]
                joined = ''.join(s if s.endswith(('。', '！', '？', '”', '；')) else s + '。' for s in seq)
                added = any(not s.endswith(('。', '！', '？', '”', '；')) for s in seq)
                cc = ai['chuchu']
                art = {'aid': aid, 'kind': 'restored_from_answer',
                       'source': {'paper': pid, 'qno': q, 'chuchu_from_analysis': cc, 'ans_file': ANSF.get(pid), 'ans_page': ai['ans_page'], 'external_url': ext_note(key)[0]},
                       'title': (re.sub(r'^.*?《', '《', cc) if cc else None), 'order': order_str, 'text': joined,
                       'note': f'还原文段：按原参考答案 {ai["ans"]}（{order_str}）排列原句，句子用字未改' + ('；原句无句末标点处由编者补“。”以连成段' if added else '') + '。' + (f'原解析【文段出处】：{cc}。' if cc else '原解析未给文段出处。') + ext_note(key)[1]}
            arts.append(art)
with open(OUT + '/questions.jsonl', 'w') as f:
    for r in recs: f.write(json.dumps(r, ensure_ascii=False) + '\n')
with open(OUT + '/articles.jsonl', 'w') as f:
    for a in arts: f.write(json.dumps(a, ensure_ascii=False) + '\n')
print(len(recs), len(arts))

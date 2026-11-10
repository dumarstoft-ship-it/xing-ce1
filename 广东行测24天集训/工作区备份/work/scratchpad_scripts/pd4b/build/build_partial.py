# -*- coding: utf-8 -*-
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g1 import G1
from g2 import G2
S = '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/pd4b'
OUT = '/home/user/work/out4/PD4B'
M = json.load(open(f'{S}/meta.json'))
IN42 = json.load(open(f'{S}/in42.json'))
claims = [json.loads(l) for l in open('/home/user/work/out/claims.jsonl') if l.strip()]
mine = {c['key']: c for c in claims if c['owner'] == 'PD4B'}
TITLE = {'D12-B1': '逻辑·论证A组：质疑与支持', 'D12-B2': '逻辑·论证B组：前提与解释'}
def vnote(f):
    if f.startswith('xingce/'):
        return '网友回忆版' if '网友回忆版' in f else 'xingce 版（文件名未标回忆版）'
    return 'xing-ce1 题本'
recs = []; n = 0
for grp, G in (('D12-B1', G1), ('D12-B2', G2)):
    for r in sorted(G, key=lambda x: x['order']):
        n += 1; key = r['key']; pid, q = key.rsplit('-', 1); q = int(q)
        m = M[key]; ver = r.get('ver') or list(m['versions'])[0]; v = m['versions'][ver]
        if 'stem' in r: stem = r['stem']
        else:
            s = v['stem']
            for a, b in r.get('repl', []):
                assert a in s, (key, a); s = s.replace(a, b, 1)
            i = s.rfind(r['ps']); assert i > 0, key
            stem = s[:i].rstrip() + '\n' + s[i:]
        stem = stem.replace('（）', '（　）').replace('......', '……')
        opts = r.get('options') or v['options']
        assert sorted(opts) == ['A', 'B', 'C', 'D'] and all(opts.values()), key
        ans_file = r.get('ans_file') or m['ans_file']; ans_page = r.get('ans_page') or m['ans_page_auto']
        assert ans_file and ans_page, key
        flags = list(r.get('flags', []))
        if '网友回忆版' in v['file'] and '网友回忆版' not in flags: flags.append('网友回忆版')
        notes = r['notes']
        if key in IN42:
            notes += f' 见于42天习题本{"、".join(IN42[key][1])}（{IN42[key][0]}）；用户只做过前三天，按“已做情况未知”使用。'
            flags.append('42天习题本第4天以后有此题')
        c = mine.get(key); same = sorted(set(c['dups']) - {key}) if c else []
        rec = {'id': f'PD4B-{n:03d}', 'module': '判断', 'day': 'D12', 'group': grp, 'group_title': TITLE[grp],
               'topic': r['topic'], 'order': r['order'],
               'source': {'paper': pid, 'file': v['file'], 'page': v['pages'][0], 'pages': v['pages'], 'qno': q,
                          'ans_file': ans_file, 'ans_page': ans_page, 'version_note': vnote(v['file'])},
               'done_status': '已做情况未知', 'stem': stem, 'options': opts, 'material_or_article': None, 'assets': [],
               'source_answer': r['src'], 'checked_answer': r['chk'], 'brief_solution': r['sol'], 'selection_value': r['val'],
               'variant_of': None, 'check_status': '已核验', 'flags': flags, 'notes': notes,
               'source_key': key, 'source_rate': r.get('rate'), 'source_yicuo': r.get('yicuo'),
               'difficulty': r['diff'], 'same_item_in': same, 'replaced_from': None}
        if r.get('source_images'): rec['source_images'] = r['source_images']
        recs.append(rec)
with open(f'{OUT}/questions.partial.jsonl', 'w', encoding='utf-8') as fo:
    for rec in recs: fo.write(json.dumps(rec, ensure_ascii=False) + '\n')
print(len(recs), 'partial records written;', [r['source_key'] for r in recs if '·····' in r['stem']])

OK = '已独立判断并与原解析一致'; CF = '冲突待复核'; GU = '放弃'
P = []
def add(key, sub, grp, st, ans, src, diff, note, written=False): P.append(dict(key=key, subtype=sub, planned_group=grp, status=st, answer=ans, source_answer=src, difficulty=diff, note=note, record_written=written))
W = {r['source_key'] for r in recs}
# ---- B1 ----
for key, sub, a, d, note in [
 ('GD2017-58','削弱','D','中','媒体B把病因归为缺乏锻炼；D游泳运动员不缺锻炼仍增多=反例。解析扫描件p10。'),
 ('GK2021F-111','加强','B','中','缺“麦角硫因—认知障碍”一环，B补；D只讲来源。解析扫描件p29，正确率58%易错D。题本用xing-ce1版，破折号按xc版。'),
 ('ZJ2019A-108','削弱','A','难','选非。长期停滞理论三环；B/C/D各打一环，A只复述现象。解析p20-21（称A为加强）。'),
 ('SD2023-69','削弱','A','中','缺全体基数；A：全体也九成打游戏，两组不及格率相等（已程序核）。解析p22-23。'),
 ('ZJ2024A-104','加强','D','中','限定“通过实验得到的论据”；A是机理非实验结果。解析p35。'),
 ('SC2024-78','削弱','B','难','B须与题干“男性不论血压高低风险都较高”合用才成反例；D强干扰。解析p34。'),
 ('GD2019X-55','缺陷','A','中','选非。三步递推各一缺口（C/D/B），A“并存”是论证自己的立场。解析扫描件p10。同题GD2019Z-44。'),
 ('SD2023-72','削弱','D','中','时间线上杀虫剂本身与飞行行为同步，D直接他因；解析称B话题不一致，编者认为B有间接他因作用（定性不同）。解析p24。'),
 ('GK2025D-102','加强','C','中','选非。B要把20~194微米与两类细胞范围比对；C“大多数…只有个别”留口子。解析p34称C无关（定性略不同）。同题GK2025X-103。'),
 ('ZJ2018A-35','削弱','A','中','三条带限定词的断言；D不“在外公开销售”、B是“假冒官网”，都不在范围内。解析p7称D加强（定性不同）。'),
 ('HB2025-104','削弱','D','中','先由秋冬蓄水推出浅水环境减少，再对D。解析p61。'),
 ('JS2025A-101','评价','A','中','两头代入法；B外部旁证。盲解时在A、B间比较过。解析p50。'),
 ('ZJ2024A-108','削弱','C','中','“绝大部分”推“只取决于”；C只高约10%说明父亲也相关。解析p37（C>D）。'),
 ('ZJ2018A-36','削弱','B','中','选非。A打稳定性，C/D打“通过≠同等智能”，B未否定测试结果。解析p7。'),
 ('JS2025A-97','加强','A','中','缺“固碳为何紧迫”；B重复论据，C/D另起好处（解析称C/D无关，定性略不同）。解析p48。'),
 ('GD2014X-81','削弱','A','中','A否定“销量过少”；D规模效应在销量少时用不上。解析扫描件p18，正确率55%易错D。老卷按正确率入选；非盲解（先看到了答案）。'),
 ('JS2024A-100','削弱','B','中','“缓解担忧”；B切断“社区商业替代网购”，A只是场所关联。解析p31（A、B对比后选B）。原卷“·····”排作省略号。')]:
    add(key, sub, 'D12-B1', OK, a, a, d, note, key in W)
# ---- B2 ----
for key, sub, a, d, note in [
 ('GD2019X-56','前提','B','中','论据落点“风险”、结论落点“预防”，B搭桥；A搭的是已给的一环。解析扫描件p10。'),
 ('GD2018-55','解释','C','中','措施副作用（塞车）。原PD3B备选，已release后由PD4B登记。解析扫描件p10。'),
 ('GDXD2020SW-27','前提','C','难','B县平均<天天<A县平均 => ②③必需；①“都低”④“普遍”过强（已程序核）。圈码①-④文字层丢失，已按原页补。解析p6-7。'),
 ('GDXD2019SW-3','解释','A','易','选非。主体已限定为“需要备考的白领”，A讲要不要考证。解析p1。'),
 ('HB2025-106','前提','D','中','否定代入：D必要；B只是支持（解析称B不明确）。解析p62。'),
 ('JS2025A-102','解释','D','中','选非。D只是现象的延伸。解析p51。'),
 ('ZJ2023A-109','前提','C','难','题干背景“两极无冰川”暴露缺口“在极地≠寒冷”；A复述论据。解析p32。'),
 ('SD2021-72','削弱','D','难','因果倒置（患病时间越长萎缩越重）。解析扫描件p20-21，正确率36%易错C（原卷C、D同行）。题干句末缺句号已补。'),
 ('GK2016D-104','前提','A','中','“补充后可以得出”型：A成因 > B类比 > C相似。解析p15。2016老卷，无正确率；同题GK2016F-107。'),
 ('GD2018-60','解释','D','中','选非。占比=分子/分母；D讲数量不讲销售额。解析扫描件p11。与GDXD2020SW-17同模板勿同日。'),
 ('JS2019A-92','前提','A','中','把焦虑还原成“能回而不回”，A是“能回”；B只加重。解析p19（附“查证原文答案为A”）。'),
 ('GDXD2020SW-19','解释','A','易','外地户籍仍可买一套，外来人口增加；B方向相反。解析p5。'),
 ('HB2023-108','前提','C','中','定义拆环，缺“裸地吸热”。解析p37。'),
 ('JS2019A-98','削弱','C','中','“担心不必要”；C须与题干“生命只可能在行星上”合用；D只推迟。解析p20-21。原卷A/B、C/D同行，已按原页分项。'),
 ('GD2014X-80','前提','D','中','统计口径35岁以上 vs 结论范围；C只排除更年长。解析扫描件p18，正确率69%易错C。老卷按正确率入选。'),
 ('ZJXD2020-23','解释','B','易','选非。B停在“条件差”未到“数量减少”。解析p5。'),
 ('JS2017A-95','前提','D','难','缺“东方的X=逊于X”的称呼含义；A把论据说过头。解析扫描件p30，正确率45%易错A。'),
 ('GDXD2020SW-18','前提','B','中','害虫不迁移；C“始终”“各种”过强。解析p4-5。')]:
    add(key, sub, 'D12-B2', OK, a, a, d, note, key in W)
# ---- B3（记录未写）----
for key, sub, a, d, note in [
 ('JS2018A-94','结构','D','中','计划序1。题干：P→Q，Q ⊢ P（肯定后件，无效，确定判断）；A结论是新项，B肯前（带“往往”），C否后（有效），D肯后。已程序核唯一同形。解析p20-21（称A为否后，定性不同）。'),
 ('SD2024-99','归纳','A','中','计划序2。A由末句可得（“某些”留余地）；B多了“此前”无依据；C“一直高于”无比较。解析p34。'),
 ('GDXD2019SW-46','结构','B','中','计划序3。题干：非P→非Q ⊢ P→Q（必要当充分）；A多一事实前提且由非Q推非P（肯后）；C逆否有效。已程序核。解析p12。'),
 ('JS2018A-96','归纳','B','中','计划序4。B来自“很多人不缺常识而缺自律”；A倒置、C同时取反、D把两个并列结果连成条件。解析p21。'),
 ('JS2023A-94','结构','C','中','计划序5。论证链题：①←⑤←④←②←③。圈码和下划线文字层丢失，题干须按 assets/src/JS2023A-94.png 补“①…②…③…④…⑤”，“......”改“……”，设问末补冒号；选项为 ⑤←①←②←③←④ 等。解析p52。'),
 ('SD2022-74','归纳','D','难','计划序6。利率↑⇔美元↑，利率↑⇒黄金↓；C把“同步”用错；注意GPT审核第1条：负相关是整体关系，D说“下行压力”与之相容，“显著”是选项措辞。解析p24。'),
 ('SC2022S-76','结构','D','中','计划序7。A→B，B→C ⊢ A→C；C是A→B、C→B（共用后件，无效）强干扰。已程序核。索引把选项并进了题干，须按 assets/src/SC2022S-76.png 分出A-D（原卷字母后无标点）。解析扫描件p29-30。'),
 ('HB2022-108','归纳','B','中','计划序8。两处器官各识别一类味道；C“触碰”是字眼陷阱（靠味觉）。题干“β-谷甾醇”的β文字层缺，须补。解析p52。同题ZJ2022A-105。'),
 ('GK2016D-105','归纳','C','中','计划序9。“没法回答，除非…”=只有…才能回答；B对调前后件，D近义替换加原因。解析p15。2016老卷；同题ZJ2016A-102正确率52%（浙江卷答案项为D，文字略异）、GK2016F-110。'),
 ('JS2024A-102','归纳','D','难','计划序10。定义计算：A难度1则D=0；B可为负；C最大为1；D恒等（已程序核）。公式是图片：题干须写“D＝PH－PL，其中PH为高分组…，PL为低分组…”（H、L下标），公式截图已存 assets/JS2024A-102_formula.png。解析p32。')]:
    add(key, sub, 'D12-B3', OK, a, a, d, note)
# ---- BR（已核验备选，记录未写）----
for key, sub, a, d, note in [
 ('HB2024-109','削弱','D','中','D否定“向上力”的实际作用；解析p36以“话题不一致”排除B，理由弱，B有迷惑性，故留备选。'),
 ('GK2017F-108','削弱','D','中','D：其他氨基酸争抢通道；解析p17把B归为加强，编者认为B是带条件的部分削弱。'),
 ('SD2021-67','削弱','C','易','驳斥解释：C否定“撑开胃部”机制；A解释的是体重减轻。解析扫描件p19，正确率87%易错A，偏易故备选。'),
 ('HB2023-102','归纳','A','中','A是对心脏、胃肠两组事实的概括，表述较绕。解析p35。'),
 ('GD2022X-75','结构','B','中','P→Q(坏结果)，为避免Q应避免P；D肯后。广东所剩无几的无争议结构题，建议留给靠后的广东模拟日。D项“看特”按xc版作“看待”。解析p39-40。')]:
    add(key, sub, 'D12-BR', OK, a, a, d, note)
# ---- BX（冲突）----
for key, sub, a, s, note in [
 ('SC2024-83','削弱','D','B','解析p36-37选B（地球河流侵蚀=他因），以“话题不一致”排除D；编者认为D（相似星体有因无果）不弱于B。两可。'),
 ('GDXD2020SW-25','削弱','A','D','解析p6：A削弱论据、D削弱论点，优选D；编者认为A（全球森林面积逐年增加）更直接，D“找到办法”未必实施。两可。'),
 ('GDXD2020SW-45','缺陷','D','A','解析p11选A（不可降解是主要类别），称D话题不一致；编者认为“只有…才”默认其他办法都不行=D。两可。'),
 ('JS2025A-98','削弱','B','A','解析p49选A（合理安排、尽量避免排队）；编者认为B（接诊患者不会明显增多）是事实而A是承诺。两可。'),
 ('SD2022-73','削弱','D','B','解析p23-24选B（英语结论在前）；编者盲解D（威尔士语动词信息多），复核后认为解析有道理（D未交代动词位置），但D可辩护。初判不一致，不入包。'),
 ('SD2022-72','前提','C','B','选非。解析p23把甲的断定读成“之前已有雷神”，故B不是假设；编者按归谬读法B恰是假设。答案随读法变。'),
 ('GDXD2020SW-29','前提','A','B','选非。解析p7称B与题干无关；编者认为B是“要改变”所需的价值前提，A与C重复且换了概念。两可。'),
 ('HB2025-107','前提','A','B','解析p63选B（β-淀粉样蛋白是元凶）；编者认为题干已暗示β淀粉样蛋白有害，缺的是皮质醇一环（A），B“元凶”偏强。两可。题干β须按原页补。')]:
    add(key, sub, 'D12-BX', CF, a, s, None, note)
# ---- 放弃（未登记，供接手者参考）----
for key, sub, a, s, note in [
 ('SC2021H-84','解释','A','A','A与C（台阶集中在前半段）两可，PD2B也列过风险。'),
 ('GDXD2020SW-51','解释','B','B','B与D（10月气温降低）两可。'),
 ('GDXD2020SW-31','解释',None,None,'A、D两可（PD2B列过风险），未对解析。'),
 ('GDXD2020SW-44','解释',None,None,'A、D两可（PD2B列过风险），未对解析。'),
 ('GD20131-83','解释','B','B','B、C、D三项都能解释，老卷，不用。'),
 ('JS2017A-91','削弱','B','B','C（他因）也能削弱，正确率63%易错C，两可。'),
 ('ZJ2024A-105','削弱','B','B','解析自述A、B、C都可削弱、“择优定为B”，答案不够确定。'),
 ('ZJ2024A-109','削弱',None,'A','A与C两可。'),
 ('GD2014X-76','前提','D','D','正确率88%，偏易。'),
 ('GD2020X-60','结构',None,None,'前几轮已列风险（解析A，正确率32%，C同为传递），未用。'),
 ('GDXD2020SW-42','结构',None,None,'A、B两项同形，要靠句式定，未对解析。'),
 ('ZJ2026A-100','削弱',None,None,'浙江2026卷库内无解析（ZJ2026A-101/104/105同），无法对照，均不用。'),
 ('GK2024X-103','削弱',None,'B','B、C两可（答案取自PD2B报告）。')]:
    add(key, sub, None, GU, a, s, None, note)
json.dump(P, open(f'{OUT}/progress.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(P), 'progress entries;', sum(p['record_written'] for p in P), 'records written')

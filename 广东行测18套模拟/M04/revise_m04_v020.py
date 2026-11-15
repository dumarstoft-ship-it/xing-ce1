#!/usr/bin/env python3
"""Apply M04 v0.2.0 and rebuild without editing source banks or prior papers.
This is an editor revision, not an independent review or final PDF.
"""
from __future__ import annotations
import copy
import hashlib
import itertools
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
PROJECT = P.parent
VERSION = '0.2.0'
CLAUDE = 'd539f18064e429e3e002f9c9315546c942618e8b'
JZ = '江浙行测_AI题库/questions.jsonl'
JA = '江浙行测_AI题库/answers.jsonl'
MOCK = '模考/2026下半年广东卷_16-33季_AI可读/全部题目.jsonl'
HISTORY = P/'历史版本/v0.1.0'


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def dump(p, obj):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def jsonl(p):
    return [json.loads(s) for s in Path(p).read_text(encoding='utf-8').splitlines() if s.strip()]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def text(p, value):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(value.rstrip()+'\n', encoding='utf-8')


def compact(s):
    return re.sub(r'\s+', '', s)


def format_source_text(s):
    """Whitespace only: preserve generic speaker, question and condition boundaries."""
    out = ''
    last = ''
    boundary = re.compile(r'^(?:[\u4e00-\u9fff]{1,4}[：:]|[（(]\d+[）)]|[①②③④⑤⑥⑦⑧⑨⑩]|以下|下列|根据|由此|依次|这段|上述|如果体型|将以上)')
    for line in s.splitlines():
        line = line.strip()
        if not line:
            if out and not out.endswith('\n'):
                out += '\n'
            last = ''
            continue
        sep = '\n' if out and (boundary.match(line) or last.endswith(('：', '？', '。', '；', '?'))) else ''
        if out.endswith('\n'):
            sep = ''
        out += sep + line
        last = line
    out = re.sub(r'(?<=[\u4e00-\u9fff\d]) +(?=[\u4e00-\u9fff])', '', out)
    out = re.sub(r'\s*(_{2,})\s*', r'\1', out)
    assert compact(out) == compact(s), 'Formatting changed characters or punctuation'
    return out.strip()


def edit(q, description, typ='editor_revision'):
    q.setdefault('edits', []).append({'type': typ, 'description': description, 'version': VERSION})


def patch_file(path, old, new):
    s = path.read_text(encoding='utf-8')
    if old not in s:
        raise AssertionError(f'Expected old text missing: {path}: {old[:100]}')
    text(path, s.replace(old, new))


def archive(rel):
    src = P/rel
    if src.exists():
        dest = HISTORY/rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)


def visible_numeric(q):
    s = q['source_question']
    return {'number': q['number'], 'source_id': q['source_id'],
            'stem': q.get('stem_override', s['stem']), 'options': q.get('options', s['options']),
            'materials': q.get('materials', [s['material']] if s['material'] else [])}


def numeric_hash(q):
    return hashlib.sha256(json.dumps(visible_numeric(q), ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def run(script):
    subprocess.run([sys.executable, str(P/script)], check=True, cwd=ROOT)


def main():
    cfg = load(P/'paper.json')
    if cfg['version'] == VERSION:
        assert load(P/'核验记录/修订核验_v020.json')['status'] == 'PASS'
        print('M04 v0.2.0 already built; no mutation.'); return
    assert cfg['version'] == '0.1.0', 'Refuse to overwrite a different revision'
    source_paths = [ROOT/JZ, ROOT/JA, ROOT/MOCK, ROOT/'国考/言语理解/2016-2025/all.jsonl',
                    ROOT/'学习资料/政治理论常识/颜培天广东政治理论常识.pages.jsonl']
    protected = {str(f.relative_to(ROOT)): sha(f) for f in source_paths}
    for paper in ['M01', 'M02', 'M03']:
        for f in (PROJECT/paper).rglob('*'):
            if f.is_file() and '__pycache__' not in str(f):
                protected[str(f.relative_to(ROOT))] = sha(f)
    before = load(P/'selection.json')
    Q = {r['number']: copy.deepcopy(r) for r in before}
    assert sorted(Q) == list(range(1, 91)) and Q[48]['answer'] == 'C'
    assert Q[57]['source_id'] == 'gd-mock-2026h2-s24-q62'
    for rel in ['selection.json', 'paper.json', '核验报告.json', 'README.md', '交接_Claude.md',
                '核验记录/graphical_second_review.json', '核验记录/reasoning_science_verification.json',
                '核验记录/交付核验.json', '核验记录/verify_m04.py',
                '编辑底稿/quant_data_check.json', '编辑底稿/quant_data_input_contract.json',
                '核验记录/assembly_manifest.json']:
        archive(rel)
    HISTORY.mkdir(parents=True, exist_ok=True)
    text(HISTORY/'README.md', '# M04 0.1.0历史记录\n\n仅用于回溯，不作当前答案、题本或核验依据。第48题旧答案C已由0.2.0更正为B；旧核验中的PASS不能覆盖此次纠错。原始独立盲答记录保留，不回写成新一轮盲答。')

    jz = {q['question_id']: q for q in jsonl(ROOT/JZ)}
    ja = {q['question_id']: q for q in jsonl(ROOT/JA)}
    used = {r['source_id'] for r in jsonl(PROJECT/'用题登记.jsonl')}
    excluded = set(load(P/'编辑底稿/excluded_source_ids.json'))
    new_id = 'JS2023-A类-104'
    assert new_id not in used | excluded, 'Replacement already used or withdrawn'
    source = copy.deepcopy(jz[new_id]); ans = ja[new_id]
    assert ans['correct_answer'] == 'A' and not source.get('quality_flags')
    needles = [new_id, '没有一道菜四人都点，也没有一道菜四人都不点']
    exposure_hits = []
    for folder in ['广东行测24天集训', '习题本/图推']:
        for f in (ROOT/folder).rglob('*'):
            if f.suffix in {'.md', '.json', '.jsonl', '.txt', '.html'} and f.is_file():
                content = compact(f.read_text(encoding='utf-8', errors='replace'))
                if any(compact(n) in content for n in needles):
                    exposure_hits.append(str(f.relative_to(ROOT)))
    assert not exposure_hits, 'New Q57 exposed in earlier deliverables: '+str(exposure_hits)
    replacement = copy.deepcopy(Q[51])
    replacement.update(number=57, source_id=new_id, source_question=source, source_answer='A', answer='A',
        stem_override=format_source_text(source['stem']),
        options={k: format_source_text(v) for k,v in source['options'].items()},
        materials=[dict(m, content=format_source_text(m['content'])) for m in source['materials']],
        analysis='选A。先由条件（4）反推：若丙不点清蒸鲈鱼，就既不点芹菜肉丝，也不点毛豆仔鸡，只剩糖醋排骨，无法点满两道。因此丙必点清蒸鲈鱼；由（2），乙、丁也都点清蒸鲈鱼。又因没有一道菜四人都点，甲不能点清蒸鲈鱼，只能从芹菜肉丝、毛豆仔鸡、糖醋排骨中选两道，故前两道至少选一道，A必然成立。乙既点清蒸鲈鱼，由（3）还须点毛豆仔鸡，B反而不成立。丙可以点清蒸鲈鱼与芹菜肉丝，丁可以点清蒸鲈鱼与糖醋排骨，所以C、D均不一定成立。检验所有6⁴种点菜组合后，只有A在每个合法组合中成立。',
        selection_reason='保留完整原题，以必要条件的逆向约束、每人恰点两道和禁止四人同点共同推断；不替考生展开条件。替换的是投诉率口径不稳的原题，不改写该题。',
        source_locators={'original_number':104, 'pages':source['source']['pdf_pages'], 'source':source['source']},
        source_answer_reference={'file':JA, 'source':ans['source'], 'quality_flags':ans.get('quality_flags', [])},
        source_notice='题干、四个选项和完整共用材料取自仓库江苏2023年A卷第104题，除排版空白外不改文字和标点。源参考答案为A；本轮用穷举独立核验，尚待Claude增量审读。',
        edits=[{'type':'source_replacement','version':VERSION,'description':'撤下投诉率存在不同分母读法的旧57题，换用完整原题；不以改写原题消歧。'},
               {'type':'layout_only','version':VERSION,'description':'仅处理PDF句内硬换行与排版空白，保留完整条件、材料和设问。'}])
    replacement['verification'] = {'status':'editor_rechecked_pending_incremental_claude', 'checked_version':VERSION,
        'method':'先推导必要结论，再枚举6^4个组合；与仓库参考答案对照。非新一轮隔离盲审。',
        'source_answer_available':True, 'source_answer_agreement':True, 'report':'核验记录/修订核验_v020.json'}
    Q[57] = replacement
    retired = [{'paper_id':'M04','number':n,'source_id':before[n-1]['source_id'], 'retired_in':VERSION,
                'reason':reason,'replacement_source_id':newid}
               for n,reason,newid in [(2,'与前卷及撤题的主次矛盾题重复，改用量变质变的另一考点。','M04-ORIG-002-v020'),
                                      (57,'投诉率分母不同读法会改变判断；按不实质改写原则换题。',new_id)]]
    dump(P/'撤题记录_v020.json', retired)
    dump(P/'编辑底稿/excluded_source_ids.json', sorted(excluded | {r['source_id'] for r in retired}))

    for n in list(range(16,31)) + list(range(51,66)):
        q=Q[n]; s=q['source_question']
        if isinstance(s['stem'],str):
            q['stem_override']=format_source_text(s['stem']) if q['source_id'].startswith(('JS','ZJ')) else s['stem']
            q['options']={k:format_source_text(v) if q['source_id'].startswith(('JS','ZJ')) else v for k,v in s['options'].items()}
        elif n != 63:
            q['stem_override']=copy.deepcopy(s['stem']); q['options']=copy.deepcopy(s['options'])
        if n != 57:
            q['edits']=[e for e in q.get('edits',[]) if e.get('type') in ['layout_only']]
        if n == 63:
            q['edits']=[{'type':'source_table_render','version':VERSION,'description':'依据源库结构化表格重建示意图；原扫描图未取得。文字条件、选项和表内位置不变，不称原图像素复核。'}]
        elif n in [28,58,61]:
            edit(q, '恢复源题选项、文字及标点，仅处理排版空白；未改变论证边界或干扰项。', 'restore_source')
    Q[58]['source_notice'] += ' 0.2.0撤销无原PDF点位证据的标点润色，保留转写标点；源稿设问问号位置需Claude对原卷核对，不能把润色称为原文复原。'
    Q[59]['stem_override'][0]['text']=Q[59]['stem_override'][0]['text'].replace('下列选项最有可能', '\n下列选项最有可能')
    edit(Q[59], '仅将设问独立成行；文字、标点和选项保持源题。', 'layout_only')
    Q[28]['analysis']='选B。文段说江南新茶通常取早春茶芽，却专门举出罗岕茶是初夏新茶这一例外，故“都用早春新茶”与文意不符。A需连读“明清两代一直以江南炒青或蒸青的新茶为尚”及开头的炒青绿茶，说明江南的绿茶风尚延续。C须结合开头“原先遵循江南”与后文“到了清初……开始喝陈茶”的时间转换，理解清初变化以前的影响。D承接“清初的武夷山地区”这一语境，概括当地出现的新的饮茶风尚，而非声称全国历史上的一切发酵茶均始于清初。保留原C、D，使考生仍须跨句判断时间与语境范围，不把答案线索改成直接复述。源参考答案同为B。'
    Q[19]['analysis']='选A。第一、二空不能独立排除D：“预设／既定”的研究主题与旅行中“鲜活／实际”的问题在语境中均可理解，不能靠前两空硬分胜负。关键是第三空：组织者要善于“捕捉”孩子感兴趣的研究主题，动宾搭配自然；“引导研究主题”不当，通常引导的是研究活动或学习者，D据此排除。“激发”宜接兴趣、热情等，“善于延伸……主题”也不及“捕捉”符合发现儿童兴趣并鼓励探究的语境。三个空整体回读，A最恰当。'
    Q[17]['analysis'] += ' 第一空单独看，“龙争虎斗”也可以描述竞争激烈，不能凭这一空直接排除D；D后两空中，“变幻莫测”不能概括所列具体事件，“死灰复燃”通常指已经消失的坏事重新出现，带贬义。'

    for n in [46,47,49,50,66,67]:
        q=Q[n]; s=q['source_question']; oldstem=q.get('stem_override',s['stem'])
        if n <= 50:
            q.pop('stem_override',None); q.pop('options',None)
        else:
            original_figs=iter(copy.deepcopy([b for b in s['stem'] if b['type']=='figure']))
            q['stem_override']=[next(original_figs) if b['type']=='figure' else b for b in oldstem]
        q['edits']=[e for e in q.get('edits',[]) if e.get('type')!='diagram_redraw']
    Q[48]['answer']='B'
    Q[48]['analysis']='选B。是否为同一图符，应对所有摆放方向使用同一标准：比较完整图形，尤其是完整椭圆所表示的可见端面。转过180°后，可见端面换到另一端，即为不同图符。题干第1与6位、第2与3位、第4与7位分别相同，第5、8位各为另一种，结构为a-b-b-c-d-a-c-e。B具有完全相同的重复位置。A第5与8位还相同，重复过多；C第2、3位互为转180°，并非同一图符；D第1与6位不同，第6位又和第2、3位相同。因此只有B符合。旧解析把斜放图形的相反端面合并，却区分平放图形的相反端面，判断口径不一致，已撤销。'
    edit(Q[48], '原图重新读图后更正编辑答案C→B；不修改题干、选项或题图。', 'answer_correction')
    Q[49]['analysis'] += ' 具体说，①对应右块图案的镜像，不能靠空间正旋转与之重合；②折成左块时，V形所在面处于与右块粘合的一侧，因而不可见。'
    Q[50]['analysis'] += ' 题干左侧立柱后还有一块被完全遮挡的小正方体；结合整体连通性补出它，不能只数所有露出的面。'
    Q[62]['analysis'] += ' C最接近“寓教于乐”，但其描述是孩子在上课场景玩耍、家长认为效率下降，不能直接证明产品本身不具备这一功能；A则用质量事实直接反驳限定人群内“都可以安全使用”的全称承诺。'
    Q[66]['analysis']=Q[66]['analysis'].replace('B没有水平加速趋势，所受水平摩擦力为0','B静止，水平方向只可能受到A的摩擦力，由平衡条件可知该摩擦力为0').replace('摩擦力f=m_Ba','摩擦力f_B=m_Ba')
    Q[67]['analysis']=Q[67]['analysis'].replace('V₃跨接电源两端，示数为U','A₁为理想电流表，其两端等电势，所以V₃左端与电源一端等电势；V₃等效测量电源两端电压，示数为U').replace('所以V₁=V₂=U/2','V₁实际测L₁两端电压，所以V₁=V₂=U/2')

    Q[2].update(source_id='M04-ORIG-002-v020',
        stem='某系统在要素种类、数量不变的情况下，仅通过调整内部排列结构便发生了性质变化，因此这次变化不需要量变作为准备。', answer='错误',
        analysis='错误。量变不仅包括数量的增减，还包括组成要素排列次序的变动。要素种类、数量不变，并不等于没有量变；内部排列变化达到一定限度，也可能导致性质变化。题干用“数量未变”直接否定量变的准备作用，缩小了量变的内涵。',
        selection_reason='替换与前卷重复的主次矛盾情境；考查量变是否只指数量增减，以及量变与质变的区分。')
    Q[2]['provenance'].update(book_pages=[41], book_scope='讲义第41页直接列出量变包括组成要素排列次序变动；新情境为编辑原创，不称真题改编。', references=[])
    edit(Q[2], '换掉重复考点情境，旧题源ID进入撤题登记；新题保持判断题形式。','question_replacement')
    Q[6]['options']['D']='出台出口奖励政策，按新增出口订单给予财政补贴'
    Q[6]['analysis']='选C。制度型开放着重于规则、规制、管理、标准等制度层面的对接，C以政府采购、知识产权保护为具体落点，直接符合题意。A扩大运输能力，B增加商品订单，侧重货物流量与贸易规模；D虽然也是政府出台的政策，但直接作用是奖励出口订单，未体现制度与国际高标准的对接。不能见到“政策”就等同于制度型开放。'
    Q[6]['provenance'].update(book_pages=[74],book_scope='讲义第74页直接涉及制度型开放、自贸试验区提升及规则机制软联通；四项具体工作为编辑原创情境。')
    edit(Q[6], '用出口奖励政策替换弱干扰项，避免凭“有没有政策字样”排除，答案C不变。','distractor_improvement')
    Q[12]['options']['B']=Q[12]['options']['B'].replace('冰川侵蚀形成的冰斗湖','火山喷发形成的火山口湖')
    Q[12]['analysis']='选A。丹霞山以红色砂砾岩经侵蚀形成的赤壁丹崖为主要特征；七星岩属于石灰岩地区的喀斯特地貌，溶蚀形成峰林、溶洞；湖光岩玛珥湖与火山喷发有关。B的丹霞山和湖光岩两格正确，错误仅在把七星岩说成火山成因；C混淆丹霞与喀斯特，D混淆丹霞山及湖光岩的成因。不能只靠丹霞与火山两端的明显词语锁定答案，还须判断七星岩。'
    Q[12]['provenance'].update(book_pages=[70,104],book_scope='讲义第70页为广东地貌概况，第104页提及碳酸钙、石灰石与喀斯特地貌；三处景区讲义未收录，具体岩性与成因以已列官方介绍为直接依据。')
    edit(Q[12], '改正依据页码；B第三格改为正确的火山成因，必须分辨七星岩才能排除B。','provenance_and_distractor')
    Q[14]['options']['D']='终端完成无源定位时，需要先向卫星发出测距请求，再由卫星返回位置结果'
    Q[14]['analysis']='选C。无源定位指终端接收卫星信号并据此计算位置，不表示终端无需供电，A错误；它不以地面移动通信网络为必要条件，B错误。仅支持接收定位，不等于具备向卫星发送短报文的设备与功能，C正确。D把需要终端发送请求的交互方式混入无源定位；本题定位不以向卫星提出测距请求为前提。'
    Q[14]['provenance']['book_pages']=[106]
    edit(Q[14], '以有源与无源定位的具体混淆替换绝对化弱干扰项；答案C不变。','distractor_improvement')
    pages={x['pdf_page']:x for x in jsonl(source_paths[-1])}
    assert '排列次序' in pages[41]['text'] and '地貌' in pages[70]['text'] and '喀斯特' in pages[104]['text']
    assert '制度型开放' in pages[74]['text'] and '北斗' in pages[106]['text']

    Q[34]['analysis']=Q[34]['analysis'].replace('前两项的二分之一','前第二项（隔一项）的二分之一')
    Q[37]['analysis'] += ' 利润率以成本为分母，应算35/115≈30.4%，较25%增加约5.4个百分点；若误以售价作分母，会算成20%→约23.3%，误选B。'
    Q[38]['analysis'] += ' 三边24、45、51米均为3米的整数倍，分别是8、15、17段，合计40段，三个顶点均可落在传感器位置上。'
    Q[40].pop('stem_override',None)
    Q[40]['edits']=[e for e in Q[40]['edits'] if e.get('type')!='model_clarification']
    Q[40]['analysis'] += ' 严格下界：给螺丝钉记2单位、螺丝帽记1单位，总任务为7200单位。A每小时至多完成80单位，B每小时至多60单位，所以T≥7200/140=360/7小时。再结合可行安排与不足1小时按1小时计，得52小时。生产对象如何安排留给考生识别，不在题干额外提示切换模型。'
    edit(Q[40], '撤销非必要的分时切换模型提示，恢复原题题干；保持原难度和答案。','restore_source')
    Q[41]['analysis']='选D。设六单六折后的金额合计为S。六单中恰有两单不足25元，满减最多作用于另四单，合计最多减4×3=12元；五天每天使用一张4元优惠券，最多再减20元。因此实付148元意味着S≤148+12+20=180元，原价合计最多180÷0.6=300元。这个上界可以取到：六单原价设为40、40、55、55、55、55元，对应六折价24、24、33、33、33、33元，把两笔24元安排在同一天、其余四笔分在其余四天，六单中恰有两单不满25元，四笔满减共12元，五天优惠券共20元，实付180−12−20=148元。所有原价均为整数元，当然可以按分计价。'
    edit(Q[41], '修正上界可达的价格构造；旧构造反推原价不能按分计价。题干、选项、答案和优化难度不变。','analysis_correction')
    for b in Q[43].get('stem_override',[]):
        if b.get('type')=='text':
            b['text']=b['text'].replace('现在从中等可能随机选出2名男性和2名女性去演出','现从中随机选出2名男性和2名女性去演出（各种选法可能性相同）')
    old_contract=load(P/'编辑底稿/quant_data_input_contract.json')
    numeric=[Q[n] for n in list(range(31,46))+list(range(71,91))]
    hashes={str(q['number']):numeric_hash(q) for q in numeric}
    changed_inputs=[int(k) for k,v in hashes.items() if old_contract['sha256'][k]!=v]
    assert set(changed_inputs)<= {40,43}, changed_inputs
    old_contract.update(sha256=hashes, checked_version=VERSION,
        revision_notes={'40':'恢复原题，生产能力、需求量、整数小时口径均不变；枚举与下界复跑。', '43':'等可能抽样表述调整；样本空间及2/5干扰项不变，组合枚举复跑。'},
        changed_input_numbers=changed_inputs, not_claimed='模型由编辑复核，不是新的隔离盲审。')
    dump(P/'编辑底稿/quant_data_input_contract.json',old_contract)
    numeric_script=P/'编辑底稿/quant_data_check.py'
    patch_file(numeric_script, 'discounted=[20,20,35,35,35,35]; days=[1,1,2,3,4,5]',
        "discounted=[24,24,33,33,33,33]; days=[1,1,2,3,4,5]\noriginal_prices=[F(v)/F('0.6') for v in discounted]\nassert original_prices==list(map(F,[40,40,55,55,55,55]))\nassert all(p.denominator==1 and (100*p).denominator==1 for p in original_prices)")
    patch_file(numeric_script, "'discounted_values_witness':discounted,'days_witness':days,", "'discounted_values_witness':discounted,'original_prices_witness':original_prices,'days_witness':days,")
    for q in numeric:
        q['verification']['method']='对本题精确分数或有限模型复算；原始趋势选项图核对只适用于第90题，不扩称其他题也做过此检查。' if q['number']!=90 else '原始趋势图四个选项在0.1.0时已实际查看；本轮复跑数值与选项匹配，不称新一轮图片盲审。'

    builder=P/'build_m04.py'
    patch_file(builder, "('caption','asset_id','source_asset_id','source_pages','source_spans','svg_path')", "('caption','source_pages','source_spans','svg_path')")
    patch_file(builder, "head.append(f'### 材料：回答第{min(members)}—{max(members)}题')", "head.append(f'### 材料：回答第{members[0]}题' if len(members)==1 else f'### 材料：回答第{min(members)}—{max(members)}题')")
    for name, nums in [('politics',range(1,16)),('verbal',range(16,31)),('quant_data',list(range(31,46))+list(range(71,91))),('reasoning_science',range(46,71))]:
        dump(P/f'编辑底稿/{name}.json',[Q[n] for n in nums])
        generator=P/f'编辑底稿/build_{name}.py'
        archive(f'编辑底稿/build_{name}.py')
        text(generator, '#!/usr/bin/env python3\n"""Export current canonical revision; never regenerate obsolete v0.1 content."""\nimport json\nfrom pathlib import Path\np=Path(__file__).resolve().parent\nrows=json.loads((p.parent/"selection.json").read_text())\nnums='+repr(list(nums))+'\nassert json.loads((p.parent/"paper.json").read_text())["version"]=="0.2.0"\n(p/"'+name+'.json").write_text(json.dumps([q for q in rows if q["number"] in nums],ensure_ascii=False,indent=2)+"\\n")\n')
    formatter_source=Path(__file__).read_text(encoding='utf-8')
    start=formatter_source.index('def compact('); end=formatter_source.index('\n\ndef edit(',start)
    text(P/'编辑底稿/source_layout.py','"""Whitespace-only source layout; no rewriting."""\nimport re\n\n'+formatter_source[start:end])
    for n in [60,61,64]:
        q=Q[n]; s=q['source_question']
        assert compact(q['stem_override'])==compact(s['stem'])
    assert all('\n' in Q[61]['options'][k] for k in 'ABCD')
    assert '\n小李：' in Q[64]['stem_override']
    assert '\n如果体型' in Q[60]['stem_override']
    for q in Q.values():
        q['verification']['checked_version']=VERSION
        q['verification']['status']='editor_revision_pending_incremental_claude'
    rows=[Q[n] for n in range(1,91)]
    dump(P/'selection.json',rows)
    for name, nums in [('politics',range(1,16)),('verbal',range(16,31)),('quant_data',list(range(31,46))+list(range(71,91))),('reasoning_science',range(46,71))]:
        dump(P/f'编辑底稿/{name}.json',[Q[n] for n in nums])
    cfg.update(version=VERSION, status='revised_pending_incremental_claude',
        external_review='v0.1.0_review_received_v0.2.0_incremental_pending', printing_status='old_v010_pdf_obsolete_current_pdf_pending',
        display_status='0.2.0审核意见处理稿，90题。已更正第48题答案、恢复原题和原图并替换不宜改写的题；本轮改动待Claude增量复核，旧32页PDF已归档，不是本版打印稿。',
        review_handoff='交接_Claude_修订复核.md', date_timezone='Asia/Taipei',review_source_commit=CLAUDE)
    dump(P/'paper.json',cfg)

    verifier=P/'核验记录/check_reasoning_science.py'
    patch_file(verifier,"len(source_key_rows), 10", "len(source_key_rows), 11")
    patch_file(verifier,"'B':[0,1,1,2,2,0,2,3],\n               'C':[0,1,1,2,3,0,2,4], 'D':[0,0,0,1,2,0,1,2]", "'B':[0,1,1,2,3,0,2,4],\n               'C':[0,1,2,3,4,0,3,5], 'D':[0,1,1,2,3,1,2,4]")
    patch_file(verifier,'in [46,47,49,50,63,66,67]', 'in [63]')
    patch_file(verifier,"check('exact_redraw_asset_count', len(owned_assets), 14)", "check('active_reconstructed_asset_count', len(owned_assets), 2)")
    patch_file(verifier,"'status':'editor_checks_passed_text_cross_review_passed_graphics_pending_parent_review'", "'status':'v020_editor_rechecked_pending_incremental_claude'")
    patch_file(verifier,"'scope':'Q51–70; reviewer saved answers before seeing editorial keys; all 20 agreed.'", "'scope':'Historical v0.1.0 review only; replaced Q57 and revised explanations are not covered by that old agreement.'")
    patch_file(verifier,"'followups_closed':'Q60 global rule separated from Ding dialogue; Q64 speakers separated; Q67 lamp labels moved above wires.'", "'followups_closed':'Current layout is verified separately; Q67 now uses the original figure.'")
    patch_file(verifier,"'source_images_actually_viewed':[46,47,48,49,50,66,67]", "'historical_v010_source_images_viewed':[46,47,48,49,50,66,67],\n        'current_revision_image_read_again':[48]")
    patch_file(verifier,"'redrawn_pngs_actually_viewed':[46,47,49,50,63,66,67]", "'historical_v010_redrawn_pngs_viewed':[46,47,49,50,63,66,67],\n        'currently_active_reconstruction':[63]")
    patch_file(verifier,'Ten Jiangzhe items have repository reference keys; fifteen mock items have editorial keys only.', 'Eleven Jiangzhe items have repository reference keys; fourteen mock items have editorial keys only.')
    patch_file(verifier,'The initial q57 answer D belongs to rejected wheat-history source JS2022-A类-100; final q57 is a different question and answer A.', 'The current q57 is JS2023-A类-104 (answer A); previous candidates and the v0.1 complaint-rate question are retired and do not supply its proof.')
    run('assemble_m04.py'); run('build_m04.py'); run('编辑底稿/quant_data_check.py'); run('核验记录/check_reasoning_science.py')

    old=load(HISTORY/'核验记录/graphical_second_review.json')
    old.update(checked_version=VERSION,method='0.1.0人工记录保全在历史版本；本轮重读第48题、统一图符标准并复算模型。其余原图按源路径和哈希恢复，不称新一轮五题盲审。')
    for row in old['results']:
        n=row['number']; row['answer']=Q[n]['answer']
        row['final_images']=copy.deepcopy(row['original_images'])
        if n==48:
            row.update(review_reason=Q[n]['analysis'],result='CORRECTED_C_TO_B')
        else:
            row['result']='ORIGINAL_ASSET_RESTORED_MODEL_RECHECKED'
    dump(P/'核验记录/graphical_second_review.json',old)
    old_pdf=P/'审阅排版/M04_题本_打印版.pdf'
    if old_pdf.exists():
        shutil.move(str(old_pdf),str(HISTORY/'M04_题本_旧版勿用.pdf'))
    text(P/'审阅排版/README.md','# M04打印状态\n\n当前内容为0.2.0，尚待Claude增量复核与重新排版。原0.1.0的32页PDF已移至[历史版本](../历史版本/v0.1.0/M04_题本_旧版勿用.pdf)，不得作为本版打印稿。\n\n定稿时使用已修订的通用排版工具，原图按原卷尺寸排印，必要时仅放大；不要调用旧审阅排版脚本覆盖本版状态。')
    archive('build_review_print.py')
    text(P/'build_review_print.py', '#!/usr/bin/env python3\nraise SystemExit("旧审阅排版入口已停用；0.2.0先经Claude增量复核，再由通用打印工具生成新PDF。")')

    choices=list(itertools.combinations(range(4),2)); models=[]
    for sets in itertools.product(choices,repeat=4):
        a,b,c,d=map(set,sets)
        if not all(0<sum(k in s for s in [a,b,c,d])<4 for k in range(4)):continue
        if (0 in d and 1 not in a) or (1 in c and not(1 in b and 1 in d)):continue
        if ((0 in b or 1 in b) and 2 not in b) or ((0 in c or 2 in c) and 1 not in c):continue
        models.append(sets)
    truths=[[0 in a or 2 in a,0 in b or 3 in b,2 in c or 3 in c,0 in d or 2 in d] for a,b,c,d in models]
    universal=['ABCD'[i] for i in range(4) if all(t[i] for t in truths)]
    assert models and universal==['A']
    fidelity=[]
    for n in list(range(16,31))+list(range(46,66)):
        q=Q[n]; s=q['source_question']; effective=q.get('stem_override',s['stem'])
        if isinstance(s['stem'],str):
            assert compact(effective)==compact(s['stem']), n
            assert all(compact(q.get('options',s['options'])[k])==compact(s['options'][k]) for k in 'ABCD'), n
        else:
            original_text=[compact(b['text']) for b in s['stem'] if b['type']=='text']
            current_text=[compact(b['text']) for b in effective if b['type']=='text']
            assert original_text==current_text,n
            assert q.get('options',s['options'])==s['options'],n
            if n !=63:
                assert [b['path'] for b in effective if b['type']=='figure']==[b['path'] for b in s['stem'] if b['type']=='figure'],n
        fidelity.append({'number':n,'source_id':q['source_id'],'source_text_and_options':'PASS_EXCEPT_WHITESPACE',
                         'figure_boundary':'Q63 structured-table rendering; no original scan' if n==63 else 'original if present'})
    assert all(compact(a['content'])==compact(b['content']) for a,b in zip(Q[57]['materials'],Q[57]['source_question']['materials']))
    assert protected=={p:sha(ROOT/p) for p in protected}, 'Source bank or prior paper mutated'
    ledger=jsonl(PROJECT/'用题登记.jsonl'); assert len([x for x in ledger if x['paper_id']=='M04'])==90
    assert not ({r['source_id'] for r in retired} & {q['source_id'] for q in rows})
    assert load(P/'核验报告.json')['content_validation']=='PASS'
    output_files=['paper.json','selection.json','题目.jsonl','题本_待审.md','答案与解析_待审.md','来源登记.jsonl']
    report={'paper_id':'M04','version':VERSION,'status':'PASS','kind':'editor_revision_checks_not_external_review',
        'question_count':90,'q48_answer':'B','answer_key_changes':[48], 'replacement_numbers':[2,57],
        'retired_ids':[r['source_id'] for r in retired], 'verbal_reasoning_fidelity':fidelity,
        'q57_source_answer':'A','q57_enumerated_models':models,'q57_universal_options':universal,
        'source_id_and_old_delivery_exposure_hits':exposure_hits,
        'q41_original_prices':[40,40,55,55,55,55],'q41_discounted_prices':[24,24,33,33,33,33],
        'quantitative_changed_visible_inputs':changed_inputs,'protected_source_and_prior_paper_hashes':protected,
        'output_sha256':{f:sha(P/f) for f in output_files},
        'limits':['本轮是编辑处理和复算，Claude增量审核未完成。','第58题保留源转写标点，原PDF点位待核。',
                  '第63题只有结构化表格，未取得原扫描图。','资料第78、84题敏感表格单元格仍缺原PDF核对。',
                  '2025年国考言语8题用户是否做过未知；不把无曝光检索命中当作从未做过。','未生成本版打印PDF，旧32页PDF归档。']}
    dump(P/'核验记录/修订核验_v020.json',report)
    text(P/'核验记录/verify_m04.py', '#!/usr/bin/env python3\n"""Check saved outputs; semantic proofs are in the versioned report."""\nimport hashlib,json\nfrom pathlib import Path\np=Path(__file__).resolve().parents[1]\nr=json.loads((p/"核验记录/修订核验_v020.json").read_text())\nassert r["status"]=="PASS" and json.loads((p/"paper.json").read_text())["version"]==r["version"]\nfor f,h in r["output_sha256"].items():\n assert hashlib.sha256((p/f).read_bytes()).hexdigest()==h,f\nprint("M04 v0.2.0 output fingerprints verified; incremental external review pending")')
    text(P/'核验记录/README.md','# 核验记录的版本边界\n\n当前看`修订核验_v020.json`、重跑后的`reasoning_science_verification.json`与`编辑底稿/quant_data_check.json`。Claude初审看`claude_review/`，对象为0.1.0。\n\n文件名含independent、blind或before_compare的记录属于0.1.0历史过程，不代表0.2.0重新盲解通过。旧`交付核验.json`已归档，不能据它声称本版PDF已完成。第48题的旧人工PASS被纠正，旧证据保全在`历史版本/v0.1.0`。')
    stale=P/'核验记录/交付核验.json'
    if stale.exists():stale.unlink()
    write_docs()
    run('核验记录/verify_m04.py')
    fingerprints={f:sha(P/f) for f in output_files}
    run('assemble_m04.py');run('build_m04.py')
    assert fingerprints=={f:sha(P/f) for f in output_files}, 'Non-deterministic rebuild'
    print(json.dumps({'version':VERSION,'status':'PASS','questions':90,'new_q57_models':len(models),'q48':'B','external_review':'incremental_pending'},ensure_ascii=False))


def write_docs():
    text(PROJECT/'选编意图与改题边界.md','''# 选编意图与改题边界

本文件记录用户已确定的意图，是接续工作的入口，不是另造一套题型配额。“指月之指非月”：以实际训练价值检验选题和加工，不以加工量、文件数或审核项数证明质量。

## 训练目标
用用户指定的、尽量陌生的题源组成有真实取舍压力的整卷，训练识别卡题、跳过、推进和回收。广东近年卷用于校准题型、设问与纸面体验，不是难度上限。不塞简单题保底，不为答案字母、来源比例或题型配额换题；同时看单题价值和整卷作用。

## 用户2026-11-15明确的边界
数量、资料、科学等可客观核验的题，可以适度改写，但不能降低难度。难度包括识别隐藏关系、梳理条件、找数据和判断边界，不仅是计算量。修正真实错误可以，替考生揭示模型、削弱干扰项不可以。

言语与判断推理不作实质改写：保留原题题干、选项和题图。原文支持的转写纠错，以及分行、字号、原图放大等排版处理可以做；解析可独立推导和讲清楚。原题疑点解决不了就换题，不以重写选项或添条件消歧。原图清晰可用就直接用；只有无原图的结构化转写才考虑据原数据重建，并写明证据边界。

## 接续和审核
新窗口先读本文件、协作原则、当前卷README及实际成品，不能只继承上一轮口头总结。Claude意见是待核证据，不是照单执行的命令；采纳与否看实际作用。保留旧证据、撤题ID和使用记录；用户已做状态未知就写未知。新增与改动须增量复核，审核前不称最终定稿。
''')
    text(P/'GPT审核意见处理.md','''# M04 0.2.0｜审核意见处理

依据：Claude对0.1.0的审核及用户本轮明确的改题边界。当前为处理稿，不是Claude已经通过的定稿。

## 已落实
- 第48题原图重读并统一图符标准，编辑答案C改B，解析、答案表、模型与当前核验记录同步；旧错判保全，不回写成历史上一直正确。
- 第46、47、49、50、66、67题恢复源库原图；题面保留asset_id以便按原尺寸排印。第63题仅有结构化表格，保留据表重建，明确没有扫描原图。
- 言语15题、判断20题逐项检查文字和选项。第28题恢复原C、D；第58题撤销无原PDF证据的标点润色；第61题四个选项恢复对话分行。通用排版清洗函数按说话人和设问边界保留换行，旧生成脚本不再生成已否决的改写。
- 旧第57题投诉率存在不同分母读法：不再加定义，撤下并更换为江苏2023年A卷第104题。完整材料、条件、设问和选项原样保留，仅整理空白；源答案A，并枚举所有点菜方案核验。
- 第41题上界构造改用可按分计价的整数原价40、40、55、55、55、55元；数学脚本加入整元/整分断言，答案300不变。
- 第12题讲义依据页改70、104，并明确景区成因不在讲义内；第6题采用第74页，第14题删无关第107页。
- 换掉第2题重复的主次矛盾情境，改考量变包含要素排列变化；第6、12、14题改善原创干扰项。第40题撤掉额外模型提示，恢复原题；数量题不以提前给模型降低难度。
- 第17、19、28、34、37、38、40、41、49、50、62、66、67题等解析补充或纠正。未改题干和选项的解释性补充不算改写原题。

## 没有机械采纳
不为答案均衡改键，不按形式结构题、古语题等配额补题，不继续重绘清晰原图。第57题不采纳继续补分子的方案，因为用户已明确判推不作实质改写。第28题不保留“消歧”名义下的降难改写。

## 仍有边界
第58题转写标点需对原PDF核对；第63题缺扫描原图；第78、84题敏感数据仍需原PDF逐格核验。2025年国考言语8题用户是否做过未知。旧32页PDF移入历史目录，当前没有0.2.0打印定稿。旧盲答记录只覆盖旧版，不声称本轮重新盲审。

答案字母仅第48题C→B；第2、57题虽换题，答案类型/字母分别仍为“错误”和A。所有结果待Claude增量复核。
''')
    text(P/'交接_Claude_修订复核.md','''# M04 0.2.0｜增量复核

先读[选编意图与改题边界](../选编意图与改题边界.md)，再看当前题本，不把本交接答案当作盲审输入。原审核档案在`Claude审核意见.md`与`核验记录/claude_review/`，原样保留。

优先重新解：新第2、57题；更正第48题；恢复原选项的28题；调整原创干扰项的6、12、14题。另检查61、60、64说话者分行、59设问、58源标点，及六张原图的尺寸。第41题重新验上界与整分构造；第40题现为原题题干，不再提示分时切换。35道言语/判推的字符保真检查仅忽略空白，不抹去标点；63图是源表重建的单独边界。

新增57题不是投诉率题，旧57的任何盲答/模型均不能沿用。新增57源题ID为JS2023-A类-104，使用完整共用材料。源参考答案与穷举记录在解析/修订核验中，先解再看。

第78施工面积−4.4／−4.3，第84四月6.1／409.4原表图未取得；不得把一致性复算说成原图核对。2025国考言语8题熟题状态仍未知。

处理记录见`GPT审核意见处理.md`；当前可复跑`核验记录/verify_m04.py`、`编辑底稿/quant_data_check.py`和`核验记录/check_reasoning_science.py`。旧模块生成器已改为导出当前canonical selection，避免重跑把旧改写带回来。

增量审核后，再用当前通用打印工具排版。旧审阅PDF已归档，不是本版PDF。保留原图，必要时放大；不为了配额或表面整齐再改题。
''')
    text(P/'README.md','''# M04｜0.2.0审核意见处理稿

**90题、90分钟。已完成本轮修订与编辑复算，待Claude增量复核；尚无本版打印定稿。**

[题本](题本_待审.md)｜[答案解析](答案与解析_待审.md)｜[处理意见](GPT审核意见处理.md)｜[Claude增量交接](交接_Claude_修订复核.md)｜[核验报告](核验记录/修订核验_v020.json)

接续工作先读[选编意图与改题边界](../选编意图与改题边界.md)及[协作原则](../../协作原则_指月之指非月.md)。

本轮重点：第48题更正B；六题恢复原图；第28题原选项恢复；第61题对话分行恢复；第57题不再改写消歧而换完整原题；第41题改正可达构造；第12题改正依据页码；第2题换掉重复考点。题本与解析、source登记和用题台账一并重建。撤题ID见[撤题记录](撤题记录_v020.json)。

Claude原审核保存在[审核意见](Claude审核意见.md)和`核验记录/claude_review/`，审核对象仍为0.1.0。本轮编辑核验不冒称外部通过。第63题无扫描原图，第78、84题原表待核；国考2025言语8题用户已做状态未知。

原0.1.0的32页PDF、旧底稿与错误核验已[归档](历史版本/v0.1.0/README.md)，不能作为本版打印或答案依据。打印状态见[这里](审阅排版/README.md)。

重建：先运行`assemble_m04.py`，再运行`build_m04.py`；运行`核验记录/verify_m04.py`确认当前文件指纹。任何再次变更均需同步模块、selection、报告和增量审核范围。
''')
    top=PROJECT/'README.md'; s=top.read_text(encoding='utf-8')
    s=re.sub(r'\*\*最新更新（2026-11-15）：[^\n]*', '**最新更新（2026-11-15）：[M04 0.2.0](M04/README.md)已按Claude审核及用户最新边界修订，待增量复核；旧32页PDF已归档。** [处理意见](M04/GPT审核意见处理.md)｜[接续意图与改题边界](选编意图与改题边界.md)', s, count=1)
    s=re.sub(r'^\| M04 \|.*$', '| M04 | [0.2.0审核意见处理稿](M04/README.md)，90题已重建 | [Claude增量复核](M04/交接_Claude_修订复核.md)，再打印；旧PDF归档 |', s, flags=re.M)
    s=s.replace('M04另有待审PDF','M04旧待审PDF已归档，本版待增量复核后重新排版')
    text(top,s)
    root=ROOT/'README.md'; s=root.read_text(encoding='utf-8')
    text(root,'## 当前进度：M04 0.2.0修订稿待增量复核\n\n[第四套入口](广东行测18套模拟/M04/README.md)｜[修改处理](广东行测18套模拟/M04/GPT审核意见处理.md)｜[选编意图与改题边界](广东行测18套模拟/选编意图与改题边界.md)\n\n以下历史进度保留，当前状态以各卷README和paper.json为准。\n\n'+s)


if __name__=='__main__':
    main()

#!/usr/bin/env python3
"""Reproducible, source-bound revision of Xingce first-round packages.
Inputs are immutable main/Claude snapshots. No network calls and no source scripts executed.
"""
from __future__ import annotations
import argparse, ast, copy, csv, hashlib, html, itertools, json, math, re, shutil
from collections import Counter, OrderedDict
from fractions import Fraction as F
from pathlib import Path
from bs4 import BeautifulSoup

PROJECT='广东行测24天集训'
REPO='https://github.com/dumarstoft-ship-it/xing-ce1'
MAIN_REF='5882576d04abd39d80e32fdb2ec5de181d866682'
CLAUDE_REF='dc3056ce7ad1c856be89bb031f0778226ef1a7da'
VERSION='2026-11-08-v2'

def readj(p): return [json.loads(l) for l in p.read_text(encoding='utf-8').splitlines() if l.strip()]
def writej(p, rows): p.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows),encoding='utf-8')
def write(p,s): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(s,encoding='utf-8')
def section(s,id):
    m=re.search(r'^### [^\n]*\b'+re.escape(id)+r'\b[^\n]*\n[\s\S]*?(?=^### |^## |^---\s*$|\Z)',s,re.M)
    assert m, ('section missing',id)
    return m.group(0)
def putsection(s,id,new):
    old=section(s,id); assert s.count(old)==1
    return s.replace(old,new.rstrip()+'\n\n',1)
def subst(s,old,new,required=True):
    if required: assert old in s, ('not found',old)
    return s.replace(old,new)
def label_for(kind):
    if kind=='新编': return ' · 新编'
    if kind.startswith('原题整理'): return ' · 原题整理'
    if kind.startswith('改编'): return ' · 改编'
    return ''
def qblock(id,stem,opts,kind='原题选编'):
    return f'### {id}{label_for(kind)}\n\n{stem}\n\n'+'  \n'.join(f'{k}. {v}' for k,v in zip('ABCD',opts))+'\n'
def parse_q(s,id):
    block=section(s,id)
    lines=block.splitlines()[1:]
    opts={}
    stem=[]
    for line in lines:
        m=re.match(r'^([ABCD])\.\s+(.*)',line)
        if m: opts[m[1]]=m[2].strip()
        elif not opts: stem.append(line)
    assert set(opts)==set('ABCD'),(id,opts)
    return '\n'.join(stem).strip(),opts

def revise_d01(src,out,source_dir):
    shutil.copytree(src,out,dirs_exist_ok=True)
    names={
      'q1':'D01_数学运算001-060_题本.md','a1':'D01_数学运算001-060_答案与核验.md',
      'q2':'D01_数学运算061-105_题本.md','a2':'D01_数学运算061-105_答案与核验.md',
      'qn':'D01_数字推理001-030_题本.md','an':'D01_数字推理001-030_答案与核验.md'}
    docs={k:(src/v).read_text() for k,v in names.items()}
    idx1=readj(src/'D01_数学运算001-060_编制记录.jsonl')
    idx2=readj(src/'D01_补充075题_编制记录.jsonl')
    idx={x['id']:x for x in idx1+idx2}
    changes={}
    specs={
    'D01-M017':dict(kind='改编', answer='A', result='252',
      stem='甲、乙、丙、丁四家公司原有汽车数量之比为5∶4∶3∶2。甲向丙调度若干辆，丁向乙调度若干辆，两次均至少调度1辆且合计不超过20辆，没有其他车辆增减。调度后甲、乙的可用汽车数量相同，丙的数量恰为丁的2.5倍。四家公司原有汽车总数最多是多少辆？',
      opts=['252','266','280','294'],
      sol='设原数量为5k、4k、3k、2k，两次调度量分别为x、y。甲乙相等给出x+y=k；丙丁比例给出2(3k+x)=5(2k−y)。消元得x=k/3、y=2k/3，因此k必须为3的正整数倍。又x+y≤20，所以k≤20，最大k=18，总量14k=252。\n\n可行验证：原数量90、72、54、36，分别调6辆和12辆后为84、84、60、24，全部条件成立。266对应k=19、280对应k=20，均不能使调度量同时为整数；294超出调度总量限制。',
      source='结构改编自[2024国考副省级第62题，PDF第11页][GK2024F]，不是原题。',
      value='把已知调度量改为未知量，必须先取得比例关系，再用整数性和调度上限求最值并验证可达。',
      change='撤下原来的两类职工简单比例变式，保留四对象调度结构，改为整数约束下的总量最大值；题干、选项和答案均重做。',
      check='14*18==252 and 5*18-6==4*18+12 and F(3*18+6,2*18-12)==F(5,2)'),
    'D01-M019':dict(kind='改编',answer='B',result='120',
      stem='甲、乙两单位职工总人数在160至190人之间（含端点）。甲单位60%、乙单位75%的职工参加项目A；随后分别从各自未参加项目A的职工中，抽调50%和1/3参加项目B。参加项目B的共30人，各类人数均为整数。参加项目A的职工最多有多少人？',
      opts=['114','120','126','132'],
      sol='设甲、乙原人数分别为5x、12y，则参加B的人数分别为x、y，因此x+y=30。总人数5x+12y=150+7y，在160至190之间，故整数y只能取2、3、4、5。参加A的总人数为3x+9y=90+6y，最大120。\n\n取y=5、x=25：甲125人、乙60人，共185人；参加A为75+45=120人，参加B为25+5=30人，达到上界。第二次抽调必须以各单位剩余人数为基数，不能直接再乘原总数。',
      source='结构改编自[2021国考地市级第63题，PDF第9页][GK2021D]，不是原题。',
      value='剩余量百分比、人数整除和总量范围共同约束，不再退化为给定总比的一元一次计算。',
      change='改为已知总人数区间及第二次抽调总量，询问第一次抽调人数的最大值；增加可行性筛选，选项重新设计。',
      check='F(3,5)*125+F(3,4)*60==120 and F(1,2)*F(2,5)*125+F(1,3)*F(1,4)*60==30'),
    'D01-M051':dict(kind='改编',answer='A',result='25%',
      stem='现有250克浓度为4%的食盐水。先加入10克食盐并完全溶解，再倒出所得溶液的一半，最后从剩余溶液中蒸发90克水。除随倒出的溶液移走的食盐外，无其他食盐损失；蒸发时食盐不析出。最终溶液的浓度为多少？',
      opts=['25%','50%','20%','约11.8%'],
      sol='加盐后盐20克、溶液260克；倒出一半后盐10克、溶液130克；蒸发90克水后溶液40克，浓度10/40=25%。\n\n50%是倒出时只减溶液质量、不减盐量；20%沿用了上一版本或母题结果；约11.8%是漏掉倒出步骤，按20/(260−90)计算。',
      source='改编自[2020广东乡镇第38题，PDF第6页][GD2020Z]，不是原题。',
      value='倒出均匀溶液同时减少盐和水，蒸发只减少水；新参数不再让新增步骤恰好抵消。',
      change='保留加盐、倒出、蒸发顺序，将旧版蒸发80克改为90克；答案由20%改为25%，干扰项对应三种具体错误。',
      check='((F(250)*F(1,25)+10)/2)/((250+10)/2-90)==F(1,4)'),
    'D01-M056':dict(kind='新编',answer='B',result='80',
      stem='甲、乙两车间生产同一种产品，各季度各车间的产量均为正数。第一季度甲、乙的单位生产成本分别为80元、100元，第二季度分别为60元、90元。合并两个季度后，甲的平均单位成本为70元，乙为96元；第一季度两车间合计的平均单位成本为95元。第二季度两车间合计的平均单位成本是多少元？（平均单位成本＝总生产成本÷总产量）',
      opts=['75','80','82.5','85'],
      sol='甲的两个季度单位成本80、60，合计均值70，故甲两季产量相同，记为a、a。乙两季100、90，合计均值96，故乙两季产量之比为3∶2，记为3b、2b。\n\n第一季度合计均值95，按80和100混合可得甲∶乙产量=1∶3，所以a=b。第二季度产量比为a∶2b=1∶2，平均单位成本=(60+2×90)/3=80元。不能直接对60和90取算术平均；季度权重和车间权重是两层不同的权重。',
      source='GPT新编。仅以[2024国考副省级第64题][GK2024F]的分期成本关系作范围参照；题干、数据和设问均为新编，不声称该真题含有本题。',
      value='利用两组跨期平均数确定各自的季度权重，再用同季度平均数连接两个车间，最后更新权重。',
      change='撤下原来单步求现期比重的变式，改为两层加权平均的独立新题。',
      check='F(80+60,2)==70 and F(3*100+2*90,5)==96 and F(80+3*100,4)==95 and F(60+2*90,3)==80')}
    for id,sp in specs.items():
        docs['q1']=putsection(docs['q1'],id,qblock(id,sp['stem'],sp['opts'],sp['kind']))
        ans=f"### {id}｜{sp['answer']}．{sp['result']}\n\n{sp['sol']}\n\n来源：{sp['source']}\n\n入选价值：{sp['value']}\n\n修订说明：{sp['change']}"
        docs['a1']=putsection(docs['a1'],id,ans)
        rec=idx[id]; rec['previous_answer']=rec['answer']
        rec.update({k:sp[k] for k in ['kind','answer','result','check']})
        rec['revision']=sp['change']; rec['revision_version']=VERSION
        if id=='D01-M056':
            rec['structure_reference']={'paper':rec['paper'],'qno':rec['qno'],'pdf_page':rec['pdf_page']}
            rec.update(paper='GPT新编',qno=None,pdf_page=None,source_answer=None)
        changes[id]=sp['change']
    # Small option improvements; no answer changes.
    for id,old,new,note in [
       ('D01-M012','A. 100—120万元之间  \nB. 不到100万元','A. 不到100万元  \nB. 100—120万元之间','区间选项恢复自然顺序，答案C不变'),
       ('D01-M031','C. 168','C. 174','干扰项174对应漏掉收回10份'),
       ('D01-M033','C. 6','C. 4','干扰项4对应把临时工误当全程'),
       ('D01-M054','B. 120','B. 95','干扰项95对应先减价再打折')]:
        docs['q1']=putsection(docs['q1'],id,subst(section(docs['q1'],id),old,new))
        changes[id]=note
    # M094: remove leakage from another problem in this same booklet.
    id='D01-M094';old=section(docs['q2'],id)
    assert '64' in old
    old=old.replace('64元','55元')
    # Keep the full existing prose; replace exactly the options with the new threshold.
    old=re.sub(r'^([ABCD])\. .+$',lambda m:f"{m[1]}. {dict(zip('ABCD',['16','17','18','19']))[m[1]]}  ",old,flags=re.M)
    docs['q2']=putsection(docs['q2'],id,old)
    docs['a2']=putsection(docs['a2'],id,
      '### D01-M094｜C．18\n\n原价每件利润100−55=45元，原20天利润45×40×20=36000元。八折后每件利润80−55=25元，因此需售出1440件。前5天销量50+60+70+80+90=350件；第6天起每天90件，还需1090件，必须再经过13天，共18天。\n\n边界核验：第17天累计1430件、利润35750元，不足；第18天累计1520件、利润38000元，达到目标。\n\n来源：[GK2025F]原第76题，题本PDF第12—13页。改编。\n\n改编说明：保留折后销量先增长后封顶的设定，成本改为55元，避免题干直接给出同组M085所求的64%成本比例；选项改为16、17、18、19，答案C对应18天。')
    idx[id].update(result='18',revision='成本64元改55元，消除对M085的答案泄露；首次达到日改为18',revision_version=VERSION)
    changes[id]=idx[id]['revision']
    # Rewrite M089 in an unambiguous reading order.
    id='D01-M089'; stem,ops=parse_q(docs['q2'],id)
    stem='便携包单价18元，买2送1；小哑铃单价12元，买3送1（即每满3个包只付2个包的钱，每满4个哑铃只付3个哑铃的钱，不足一组的按单价付款）。小王连同赠品共得到这两种物品56个，共花费606元。小哑铃共得到多少个？'
    docs['q2']=putsection(docs['q2'],id,qblock(id,stem,list(ops.values()),'原题整理'))
    changes[id]='计价规则移到设问前，去掉冗余结算措辞，答案不变'
    docs['q2']=putsection(docs['q2'],'D01-M078',subst(section(docs['q2'],'D01-M078'),'合计生产口罩3万只','每天合计生产口罩3万只'))
    # Fix typography only, with exact-match assertions.
    corrections={
      '取A15、B24、C21、D12':'取A=15、B=24、C=21、D=12',
      '得b20、c16':'得b=20、c=16',
      '也可先解a1250、b2500':'也可先解得a=1250、b=2500',
      '得N40':'得N=40','取y0、x2，则仅A22、仅B16':'取y=0、x=2，则仅参与A的22人、仅参与B的16人',
      'x2300':'x=2300','x28利润10040，x29利润9970':'x=28时利润10040，x=29时利润9970',
      'P60时':'P=60时','v80':'v=80','v10':'v=10'}
    for old,new in corrections.items(): docs['a2']=subst(docs['a2'],old,new)
    sec=section(docs['a2'],'D01-M091').rstrip()+'\n\n选项重新设计为2200、2300、2400、2600。\n'
    docs['a2']=putsection(docs['a2'],'D01-M091',sec)
    # Honest editing labels rather than counting clarifications as high-value variants.
    organized=[12,15,20,21,37,68,69,71,75,77,82,84,87,88,89,100,105]
    for n in organized:
        id=f'D01-M{n:03}'; key='q1' if n<=60 else 'q2'; ak='a1' if n<=60 else 'a2'
        sec=section(docs[key],id);sec=sec.replace(' · 改编',' · 原题整理')
        docs[key]=putsection(docs[key],id,sec)
        sec=section(docs[ak],id).replace('改编说明：','整理说明：').replace('。改编。','。原题整理。')
        docs[ak]=putsection(docs[ak],id,sec)
        idx[id]['kind']='原题整理／表述澄清'
    # Remove the unverifiable blanket option-reordering statement everywhere.
    for ak in ['a1','a2']:
        docs[ak]=docs[ak].replace('；训练选项顺序重排。','。').replace('，训练选项顺序重排。','。')
    for n in [57,59]:
        id=f'D01-M{n:03}';rec=idx[id]
        rec['structure_reference']={'paper':rec['paper'],'qno':rec['qno'],'pdf_page':rec['pdf_page']}
        rec.update(kind='新编',paper='GPT新编',qno=None,pdf_page=None,source_answer=None)
        docs['q1']=putsection(docs['q1'],id,section(docs['q1'],id).replace(' · 改编',' · 新编'))
        sec=section(docs['a1'],id)
        sec=re.sub(r'^来源：(.+)$',r'结构参照：\1 本题为GPT新编，不是该来源题的原文。',sec,flags=re.M)
        sec=sec.replace('改编说明：','新编说明：').replace('属于结构改编','属于同一考试范围内的新编')
        docs['a1']=putsection(docs['a1'],id,sec)
    # Source answer evidence is attributed to Claude's page check, not GPT's direct PDF inspection.
    source_keys={2:'A',21:'C',22:'A',23:'B',42:'A',48:'B',53:'B',31:'D',33:'A',34:'D',38:'A',39:'D',47:'B',51:'C',52:'C'}
    for n,ans in source_keys.items():
        id=f'D01-M{n:03}';idx[id]['source_answer']=ans
        idx[id]['source_answer_evidence']='Claude给GPT_D01数量复核意见.md；Claude对原题/解析页的核对，本轮GPT未亲自逐页核PDF'
    sec=section(docs['a1'],'D01-M042')
    sec=re.sub(r'按题意将16800元理解为扣除赔偿后的实收[^。]*。','按原参考解析的列式，16800元为扣除赔偿后的净收款。',sec)
    sec=sec.rstrip()+'\n\n题源同题锁定：GD2021X第38题与GD2021Z第41题。按Claude对扫描原解析的核对，原参考答案也是A。若把16800元仅理解为完好件运费，完好件840对应总件数840/0.936≈897.44，非整数，因此不符合本题的件数条件。\n'
    docs['a1']=putsection(docs['a1'],'D01-M042',sec)
    idx['D01-M042']['source_aliases']=['GD2021X-38','GD2021Z-41']
    # Four replacement series. Full source text must contain each distinctive sequence before selection.
    replacements={
    5: ('ZJ2021A_xc',53,'9','80，70，62，58，（　），70',['59','60','61','63'],'B','60','以前项减后项得10、8、4、−2、−10。相邻差的差为2、4、6、8，因此中间项60同时满足58−60=−2及60−70=−10。中间空缺必须核对两侧。'),
    14:('ZJ2023A_xc',53,'11','163，47，22，−19，79，（　）',['−256','−115','181','223'],'A','−256','从第3项起，每项=前面第2项−前面第1项的3倍：163−3×47=22，47−3×22=−19，22−3×(−19)=79。所求−19−3×79=−256。注意负数的乘减。'),
    20:('JS2020A_xc',46,'6','7.003，13.009，19.027，25.081，31.243，（　）',['36.568','36.729','37.568','37.729'],'D','37.729','整数部分7、13、19、25、31依次加6，下一项37；小数点后三位003、009、027、081、243依次乘3，下一段729。合起来为37.729。两部分须同时满足，不能只看整数部分。'),
    28:('SZ2023_xc',48,'11','5，6，9，13，15，18，19，（　）',['27','26','25','24'],'C','25','相邻两项分成四组，组内和依次11、22、33、44。末组19+x=44，因此x=25。其余选项分别使末组和为46、45、43。')}
    for n,(paper,no,page,stem,opts,ans,res,sol) in replacements.items():
        id=f'D01-N{n:03}';source=(source_dir/(paper+'.md')).read_text()
        assert re.search(r'## 原题\s+'+str(no)+r'\b',source),(paper,no)
        docs['qn']=putsection(docs['qn'],id,qblock(id,stem,opts))
        docs['an']=putsection(docs['an'],id,f'### {id}｜{ans}．{res}\n\n{sol}\n\n来源：[{paper}]原第{no}题，题本PDF物理第{page}页。替换已做广东卷原题，题号保留。原参考答案{ans}；本轮GPT独立验证上述规则，扫描页核对情况另见复核记录。')
        rec=idx[id];rec['replaced_source']={'paper':rec['paper'],'qno':rec['qno']}
        rec.update(paper=paper,qno=no,pdf_page=page,answer=ans,result=res,source_answer=ans,revision_version=VERSION,kind='选编')
        rec['selection_value']=sol
        changes[id]=f'替换已做卷原题，改用{paper}-{no}；答案{ans}，结果{res}'
        if f'[{paper}]:' not in docs['an']:
            docs['an']+=f'\n[{paper}]: {REPO}/blob/{CLAUDE_REF}/{PROJECT}/共享输入/数量原文/{paper}.md\n'
    for n in [27,30]:
        id=f'D01-N{n:03}';idx[id]['source_answer']='B'
        idx[id]['source_answer_evidence']='Claude扫描版解析核对；本轮GPT独立规则检查'
        docs['an']=putsection(docs['an'],id,section(docs['an'],id).replace('该共享输入未附原参考答案，本答案为独立核验结果。','初次输入未附原答案；本次Claude核对扫描版原解析亦为B，GPT独立规则检查一致。'))
    idx['D01-N019'].update(source_answer='D', source_answer_header='B', source_answer_body='D', source_conflict='原解析标题B、正文D；独立全序列检查D，Claude核页同样发现冲突')
    sec=section(docs['an'],'D01-N019')
    sec=sec.rstrip()+'\n\n交叉复核补注：Claude已核对原页，选项D确为38，解析标题B与正文D自相矛盾；GPT按全序列差分规则取D。此处不将错位标题当作答案依据。\n'
    docs['an']=putsection(docs['an'],'D01-N019',sec)
    # Update tables from canonical index, preserving all IDs.
    for ak in ['a1','a2','an']:
        docs[ak]=re.sub(r'(\|\s*(?:D01-)?([MN]\d{3})\s*\|\s*)[ABCD](\s*\|)',lambda m:m[1]+idx['D01-'+m[2]]['answer']+m[3],docs[ak])
    # Replace stale historical package claims with version-specific verification limits.
    docs['q1']=subst(docs['q1'],'这是首日数量日包中的 **60道数学运算题**，分为三个完整的20题组。**不是完整135道日包**：本批未包含30道数字推理及余下45道数学运算。','这是D01完整135题日包中的前60道数学运算，分为三个20题组。其余题本见[总入口](README.md)。本册已更新到v2，请勿与旧版答案混用。')
    docs['q1']=docs['q1'].replace('标“改编”的题不是原卷原文；其余选编题仅整理标点、断行和非题目页眉。','“改编”指实质改变条件或设问；“原题整理”仅精简或澄清原口径；“新编”明确不是某年原题。')
    docs['q2']=docs['q2'].replace('“改编”含明确的口径补充或条件、设问调整','“原题整理”只作口径澄清；“改编”作实质条件、设问调整')
    for k in docs:
        if k.startswith('a'):
            docs[k]=docs[k].replace('**尚未经Claude交叉复核，也未逐页对照原PDF。**','**旧版已收到Claude交叉复核；本轮改动另由GPT独立重算，未再次交给Claude盲审。GPT未逐页对照原PDF。**')
    docs['a1']=docs['a1'].replace('这不等于已经由另一模型复核，也不等于逐页对照了原PDF。','旧版其中40题已由Claude交叉复核，20道选编未抽到；本轮新改动不冒称已再次交叉复核。GPT未逐页对照原PDF。')
    missing=[f"{i:03}" for i in range(1,61) if idx[f'D01-M{i:03}'].get('source_answer') is None and idx[f'D01-M{i:03}']['kind']!='新编']
    docs['a1']=re.sub(r'## 原参考答案的缺失情况[\s\S]*?(?=## 已发现)',
        '## 原参考答案的缺失情况\n\n现有题源记录尚无原参考答案：'+ '、'.join(missing)+'。新编题本来就没有原题答案，不列作“缺失”。补录的扫描原答案依据Claude复核记录，未声称GPT亲自核过原PDF；改编题的母题答案与训练答案可以不同。\n\n',docs['a1'])
    docs['a1']=re.sub(r'## 完成边界[\s\S]*?(?=## 来源链接)',
       '## 完成边界\n\n本册60题属于完整D01的105道运算；另有30道数推。旧版交叉复核覆盖本册40题，余20题未抽查。本轮实质修订已独立计算和程序核验，尚未经Claude二次盲审；难度未做考生实测。\n\n',docs['a1'])
    for k,name in names.items():
        docs[k]=docs[k].replace('原官方','原参考').replace('官方答案','原参考答案')
        write(out/name,docs[k])
    writej(out/'D01_数学运算001-060_编制记录.jsonl',idx1)
    writej(out/'D01_补充075题_编制记录.jsonl',idx2)
    # Consolidate actual current text, options, explanations and provenance.
    full=[]
    for id,rec in idx.items():
        n=int(id[-3:]); qk='qn' if '-N' in id else ('q1' if n<=60 else 'q2')
        ak={'qn':'an','q1':'a1','q2':'a2'}[qk]
        stem,opts=parse_q(docs[qk],id)
        an=section(docs[ak],id)
        assert re.search(r'｜'+rec['answer']+'[．.]',an),(id,'heading answer')
        full.append(dict(rec,stem=stem,options=opts,solution_markdown=an.strip(),version=VERSION))
    assert len(full)==135 and len({q['id'] for q in full})==135
    assert Counter('N' if '-N' in q['id'] else 'M' for q in full)=={'N':30,'M':105}
    assert all(x.get('paper') not in ['GD2024','GD2024_xc','GD2025','GD2025_xc','GD2026'] for x in full)
    keys=[(x['paper'],x['qno']) for x in full if '-N' in x['id']];assert len(keys)==len(set(keys))
    writej(out/'D01_完整135题_v2.jsonl',full)
    # Explicit used-source lockfile, including duplicate aliases, not repeated question counts.
    with (out/'D01_已用题锁定_v2.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['training_id','kind','source_key','notes'])
        for x in full:
            if x['paper']=='GPT新编': w.writerow([x['id'],x['kind'],'GPT新编','结构参照见JSONL，非真题'])
            else:
                for key in sorted(set(x.get('source_aliases',[])+[f"{x['paper']}-{x['qno']}"])):
                    w.writerow([x['id'],x['kind'],key,'稳定题号；原题及同源改编均作重复识别'])
    result=verify_quantity(full)
    write(out/'D01_v2_核验结果.json',json.dumps(result,ensure_ascii=False,indent=2))
    log=['# D01 v2 修订记录','',f'版本：{VERSION}。旧版main快照：`{MAIN_REF}`。保持135题及所有题号，不计新增训练题量。','',
      '## 题目与答案的实质变化','', '| 题号 | 变化 |','|---|---|']
    log += [f'| {id} | {desc} |' for id,desc in sorted(changes.items())]
    log += ['', '## 同步修正','',
      '修复答案册漏等号；M020删除不存在的选项重排说明；口径补写统一标“原题整理”，不再与实质改编混计。M056、M057、M059明确为新编或结构参照新编，不冒称原卷改写。M042锁定GD2021X-38/GD2021Z-41同题。参考答案补录归因于Claude扫描页复核。', '',
      '## 核验边界','',
      'Claude旧版复核覆盖115/135，其中4道数推现已换题；不能把旧版115题一致转写成当前135题全部盲审通过。本轮新题、改题由GPT独立解算，数推30题在所述规则下逐个选项验证；改动的运算题采用方程及整数穷举核验。未逐页重核原PDF，也未再次调用Claude盲审。',
      '', '核验结果见 [D01_v2_核验结果.json](D01_v2_核验结果.json)。完整当前数据见 [D01_完整135题_v2.jsonl](D01_完整135题_v2.jsonl)。']
    write(out/'D01_v2_修订记录.md','\n'.join(log)+'\n')
    write(out/'README.md',f'''# D01 数量专项｜完整135题 · v2

版本：{VERSION}。105道数学运算＋30道数字推理；每日另外40道言语不计入这里。**已处理Claude反馈，使用本目录当前题本与当前答案，不要与旧版混用。**

| 内容 | 题量 | 题本 | 答案（两遍后再看） |
|---|---:|---|---|
| 数字推理 N001—N030 | 30 | [打开题本](D01_数字推理001-030_题本.md) | [打开答案](D01_数字推理001-030_答案与核验.md) |
| 运算 M001—M060 | 60 | [打开题本](D01_数学运算001-060_题本.md) | [打开答案](D01_数学运算001-060_答案与核验.md) |
| 运算 M061—M105 | 45 | [打开题本](D01_数学运算061-105_题本.md) | [打开答案](D01_数学运算061-105_答案与核验.md) |

四道已做广东2024—2026原题已换；M094不再泄露M085答案；M017、M019、M051、M056已实质重做，其他笔误和干扰项按复核意见修订。编号不变，不把修订当额外新题。

[修订记录](D01_v2_修订记录.md)｜[当前135题结构化数据](D01_完整135题_v2.jsonl)｜[程序核验结果](D01_v2_核验结果.json)

**核验口径：**Claude复核的是旧版115题；本轮新改动由GPT独立计算与程序核验，未再经Claude盲审。未抽到的旧版20道选编仍未跨模型复核。数推按列出的常见规则验证，不声称排除所有人为规律。GPT没有逐页重核原PDF。

[第一轮三天总入口](../../第1轮_使用入口.md)
''')
    return full,changes,result


def verify_quantity(full):
    ix={q['id']:q for q in full}; reports=[]
    def check(id,ok,evidence):
        assert ok,(id,evidence);reports.append({'id':id,'passed':True,'evidence':evidence})
    # Independent enumerations directly reflect current word problems.
    feas=[]
    for k in range(1,101):
        for x in range(1,20):
            for y in range(1,21-x):
                if 5*k-x==4*k+y and 2*(3*k+x)==5*(2*k-y) and 2*k-y>=0:feas.append((14*k,k,x,y))
    check('D01-M017',max(feas)[0]==252,{'feasible':feas,'max_total':252})
    feas=[]
    for a in range(1,191):
        for b in range(1,191-a):
            nums=[F(3,5)*a,F(3,4)*b,F(1,5)*a,F(1,12)*b]
            if 160<=a+b<=190 and all(v.denominator==1 for v in nums) and nums[2]+nums[3]==30:
                feas.append((a,b,int(nums[0]+nums[1])))
    check('D01-M019',max(x[2] for x in feas)==120,{'all_feasible_totals':feas})
    salt=F(250)*F(4,100);salt+=10;salt/=2;mass=F(260,2)-90
    check('D01-M051',salt/mass==F(1,4),{'salt':str(salt),'solution_mass':str(mass),'concentration':str(salt/mass)})
    check('D01-M056',F(80+60,2)==70 and F(3*100+2*90,5)==96 and F(80+3*100,4)==95 and F(60+2*90,3)==80,{'witness_quarter_volumes':{'甲':[1,1],'乙':[3,2]},'second_average':80})
    costs=[]
    for dumb in range(57):
        bag=56-dumb;cost=36*(bag//3)+18*(bag%3)+36*(dumb//4)+12*(dumb%4)
        if cost==606:costs.append(dumb)
    check('D01-M089',costs==[25],{'all_dumbbell_counts_meeting_cost':costs})
    profits={d:25*sum(min(40+10*i,90) for i in range(1,d+1)) for d in range(1,30)}
    first=min(d for d,v in profits.items() if v>=36000)
    check('D01-M094',first==18,{'target':36000,'profit_day17':profits[17],'profit_day18':profits[18]})
    # Verify changed distractors and stems without evaluating untrusted source code.
    check('D01-M031',((F(144)*F(2,3)-8)/2-6+10)*F(3,4)==36 and ((F(174)*F(2,3)-8)/2-6)*F(3,4)==36,'144满足题干；174对应漏掉收回10份')
    check('D01-M033',400-80-200-40==8*10 and (400-80)//10-20-8==4,'8为正确增员；4为把临时工按10天计的干扰')
    check('D01-M054',5*(F(7,10)*170-5)==(3*F(4,5)+2*F(1,2))*170-8 and 5*F(7,10)*(95-5)==F(34,10)*95-8,'170正确；95对应先减5元再打七折')
    def conv(t):
        t=t.replace('−','-')
        if '√' in t:
            a,b=t.split('√');return float(a or 1)*math.sqrt(float(b))
        return F(t)
    rules={
      1:lambda s:all(s[i]==2*(s[i-1]+s[i-2]) for i in range(2,len(s))),
      2:lambda s:all((s[i+1]-s[i])==F(3,2)*(s[i]-s[i-1]) for i in range(1,len(s)-1)),
      3:lambda s:all(str(s[i])==f'{i+1}{(i+1)**2+1}' for i in range(len(s))),
      4:lambda s:all(s[i+1]/s[i]==F(5,2)-i for i in range(len(s)-1)),
      5:lambda s: [s[i]-s[i+1] for i in range(5)]==[10,8,4,-2,-10],
      6:lambda s:all(s[i]==3+F(6,i+1) for i in range(len(s))),
      7:lambda s:all(s[i]+s[i+1]==s[i+2] for i in range(0,len(s)-2,2)),
      8:lambda s:all(abs(float(s[i])**2-[4,9,16,27,46,81][i])<1e-7 for i in range(len(s))),
      9:lambda s:[s[i+2]-2*s[i+1]+s[i] for i in range(len(s)-2)]==[9,6,3,0],
      10:lambda s:[sum(map(int,str(v))) for v in s]==[3,5,7,9,11,13],
      11:lambda s:all(s[i]+s[i+1]==(i+1)**3 for i in range(len(s)-1)),
      12:lambda s:all(s[i]==s[i-1]+s[i-2]+1 for i in range(2,len(s))),
      13:lambda s:all(s[i+1]/s[i]==F(i+1,3) for i in range(len(s)-1)),
      14:lambda s:all(s[i]==s[i-2]-3*s[i-1] for i in range(2,len(s))),
      15:lambda s:all(s[i+1]/s[i]==F(1,3)+F(i,2) for i in range(len(s)-1)),
      16:lambda s:[s[i+1]-s[i] for i in range(len(s)-1)]==[-1,1,4,-1,1,4,-1],
      18:lambda s:[s[i+1]-s[i] for i in range(len(s)-1)]==[2,12,22,32,42],
      19:lambda s:all(s[i+1]-s[i]==-2*(s[i]-s[i-1]) for i in range(1,len(s)-1)),
      21:lambda s:[s[i+2]-2*s[i+1]+s[i] for i in range(len(s)-2)]==[6,12,18,24],
      23:lambda s:all(s[i]==(i+1)**3-(i+1) for i in range(len(s))),
      25:lambda s:all(s[i]==i*(i-1) for i in range(len(s))),
      26:lambda s:all(s[i]==F(2**(i+1)-1,math.factorial(i)) for i in range(len(s))),
      27:lambda s:all(s[i]==s[i-1]+s[i-2]/2 for i in range(2,len(s))),
      28:lambda s:[s[i]+s[i+1] for i in range(0,len(s),2)]==[11,22,33,44],
      30:lambda s:[s[i+2]-2*s[i+1]+s[i] for i in range(len(s)-2)]==[1,2,3,4]}
    def stringrule(n,ts):
        parts=[tuple(map(int,t.split('.'))) for t in ts]
        if n==17:return all(b-a==12+3*i for i,(a,b) in enumerate(parts))
        if n==20:return all(a==7+6*i and b==3**(i+1) for i,(a,b) in enumerate(parts))
        if n==22:return all(a+b==5*2**i for i,(a,b) in enumerate(parts))
        if n==24:
            f=[v for ab in parts for v in ab];return f[:2]==[1,1] and all(f[i]==f[i-1]+f[i-2] for i in range(2,len(f)))
        if n==29:
            a=[ab[0] for ab in parts];b=[ab[1] for ab in parts]
            return all(F(a[i+1],a[i])==1+3*i for i in range(len(a)-1)) and all(b[i]==b[i-1]+b[i-2] for i in range(2,len(b)))
        raise ValueError(n)
    for n in range(1,31):
        id=f'D01-N{n:03}';q=ix[id]
        ts=q['stem'].replace('，',',').split(',');ts=[x.strip() for x in ts]
        blank=[i for i,t in enumerate(ts) if '（' in t];assert len(blank)==1,(id,ts)
        matching=[]
        for key,val in q['options'].items():
            filled=ts[:];filled[blank[0]]=val
            ok=stringrule(n,filled) if n in [17,20,22,24,29] else rules[n]([conv(t) for t in filled])
            if ok:matching.append(key)
        check(id,matching==[q['answer']],{'options_matching_stated_rule':matching,'all_known_terms_checked':True})
    return {'version':VERSION,'question_count':len(full),'structural_checks':'135 IDs unique; 105M+30N; booklet/index/answer-heading aligned; four prohibited original sources absent; 30 number-series source IDs unique',
       'new_math_check_count':9,'series_option_check_count':30,'checks':reports,'limits':'本轮对新改运算及全部数推作上述独立检查；未重做全部105道运算，不将旧版Claude复核套用于新题。'}

def verify_claude(qs, materials):
    ix={q['id']:q for q in qs};mi={m['mid']:m for m in materials};result=[]
    def add(id,ans,evidence,method='独立计算'):
        assert ix[id]['checked_answer']==ans,(id,ix[id]['checked_answer'],ans)
        result.append({'id':id,'answer':ans,'passed':True,'method':method,'evidence':evidence})
    battery=F('9635.6')/F('1.061')/6/10000
    add('D02-ZL-018','C',{'expression':'9635.6/1.061/6/10000','value':float(battery),'unit':'亿千伏安时','source_material':'ZLM-GK2022F_xc-3'})
    series={'A':(191,203,206),'B':(40050,45957,50623),'C':(59050,59443,60803),'D':(F('279.9'),F('372.4'),F('386.9'))}
    thresholds={}
    for key,(b19,b22,b23) in series.items():
        rate=F(b23,b22);target=2*b19;n=0;v=F(b23)
        while v<target:v*=rate;n+=1
        thresholds[key]={'further_whole_years':n,'growth_rate':float(rate-1),'preceding_year_value':float(F(b23)*rate**(n-1)),'first_reaching_value':float(v),'target':float(target)}
    assert min(thresholds,key=lambda k:thresholds[k]['further_whole_years'])=='B'
    add('D02-ZL-075','B',thresholds)
    q2=(F('450.8')-F('228.6'))-(F('50.2')-F('24.2'))
    assert q2==F('196.2');add('D02-ZL-083','A',{'Q2_excluding_wind':float(q2),'unit':'亿千瓦时'})
    gap=(F(167)/F('155.4')-F('17.4')/F('13.4'))*100
    assert gap<-10;add('D02-ZL-084','D',{'total_minus_wind_growth_pp':float(gap)})
    rates=[F(x) for x in ['2.5','0.2','0.7','2.8','3.1','3.8','3.6','5.3','5.5','6.2','5.9']]
    months=[i+3 for i in range(10) if rates[i+1]>rates[i]]
    assert months==[4,5,6,7,9,10,11]
    add('D02-ZL-085','C',{'months':months,'count':7,'reason':'累计增速是前期累计与本月增速按基期量加权；本月快于当期累计等价于累计增速较上月上升。'})
    m=mi[ix['D02-ZL-101']['material_or_article']]['text']
    for fragment in ['社区公园','居广东省首位','比上年增加4','比上年增加14']:assert fragment in m
    add('D02-ZL-101','D',{'A':'500米对应社区公园，不是城市公园','B':'达标列举为绿化覆盖率等，不是绿地率','C':'材料只称广东省首位','D':'4+4+14=22>20'},'逐项对照完整材料')
    m=mi[ix['D02-ZL-114']['material_or_article']]['text']
    for fragment in ['环比增加49','首次正增长','比7月底上涨','回落24.1']:assert fragment in m
    add('D02-ZL-114','D',{'A':'同比首次转正不等于月度产量最高','B':'给的是比7月底，不是同比','C':'风电增速回落24.1个百分点','D':'原煤日均产量环比增加49万吨'},'逐项对照完整材料')
    people='甲乙丙丁戊己庚';feasible=[]
    for comb in itertools.combinations(people,4):
        s=set(comb)
        if len(s&{'甲','丁'})>1:continue
        if s&{'丙','戊'} and not ('甲' in s and '己' not in s):continue
        if s&{'乙','庚'} and not ('丁' in s and '甲' not in s):continue
        feasible.append(comb)
    assert feasible==[('乙','丁','己','庚')]
    add('D03-PD-102','A',{'all_feasible_selections':feasible,'examined':35},'C(7,4)全部枚举')
    bureaus=['教育','住建','交通','农业','人社','财政'];base=[]
    for perm in itertools.permutations(bureaus):
        p={x:i+1 for i,x in enumerate(perm)}
        if p['财政']==p['人社']+1 and p['住建']-p['财政']>=2 and abs(p['教育']-p['交通'])==2:base.append(p)
    groups={103:[p for p in base if abs(p['教育']-p['财政'])==1],104:[p for p in base if p['住建']==6],105:[p for p in base if p['交通']==3]}
    predicates={
     103:[lambda p:p['交通']>p['教育'],lambda p:p['住建']==5,lambda p:p['人社']==1,lambda p:abs(p['农业']-p['交通'])==1],
     104:[lambda p:p['教育']==3,lambda p:abs(p['交通']-p['住建'])==1,lambda p:p['农业']==4,lambda p:abs(p['农业']-p['财政'])==1],
     105:[lambda p:abs(p['农业']-p['财政'])==1,lambda p:p['住建']==4,lambda p:p['教育']==4,lambda p:p['人社']==2]}
    for n,ss in groups.items():
        truth={key:sum(fn(p) for p in ss) for key,fn in zip('ABCD',predicates[n])}
        matching=[k for k,c in truth.items() if (c>0 if n==105 else c==len(ss))]
        expected={103:'A',104:'C',105:'B'}[n];assert matching==[expected]
        add(f'D03-PD-{n}',expected,{'feasible_count':len(ss),'option_true_counts':truth,'all_feasible_orders':[sorted(p,key=p.get) for p in ss]},'6!排列全枚举；明确按题面左到右定方向')
    depts=['生产','销售','研发','人事','财务','法务'];ss=[]
    for perm in itertools.permutations(depts):
        p={x:i+1 for i,x in enumerate(perm)}
        if p['销售']<min(p['财务'],p['生产']) and p['人事']-1 in [p['研发'],p['生产']] and p['法务']+1 in [p['研发'],p['销售']]:ss.append(p)
    queries={
      106:(ss,[lambda p:sorted(p,key=p.get)==['法务','研发','销售','财务','生产','人事'],lambda p:sorted(p,key=p.get)==['财务','法务','研发','人事','销售','生产'],lambda p:sorted(p,key=p.get)==['法务','销售','研发','生产','财务','人事'],lambda p:sorted(p,key=p.get)==['研发','人事','销售','法务','财务','生产']],'possible'),
      107:([p for p in ss if p['研发']==1],[lambda p:p['法务']==4,lambda p:p['人事']==6,lambda p:p['财务']==2,lambda p:p['生产']==3],'possible'),
      108:([p for p in ss if p['法务']==5],[lambda p:p['销售']==3,lambda p:p['销售']==4,lambda p:p['销售']==1,lambda p:p['销售']==2],'all'),
      109:([p for p in ss if p['销售']==1],[lambda p:p['财务']==6,lambda p:p['研发']==2,lambda p:p['法务']==4,lambda p:p['人事']==3],'impossible'),
      110:(ss,[lambda p:p['法务']==3 and p['销售']==4,lambda p:p['研发']==3 and p['财务']==4,lambda p:p['人事']==3 and p['研发']==4,lambda p:p['财务']==3 and p['法务']==4],'impossible')}
    for n,(states,preds,mode) in queries.items():
        truth={k:sum(fn(p) for p in states) for k,fn in zip('ABCD',preds)}
        match=[k for k,c in truth.items() if (c>0 if mode=='possible' else c==0 if mode=='impossible' else c==len(states))]
        ans={106:'A',107:'B',108:'C',109:'B',110:'C'}[n];assert match==[ans]
        add(f'D03-PD-{n}',ans,{'base_feasible_count':len(ss),'conditional_feasible_count':len(states),'option_true_counts':truth,'reading':'条件(3)陈述法务后紧接的部门确实存在，因此法务不能排最后；不是另加任意限制。'},'6!排列全枚举')
    return result


def md_assets(paths): return '\n\n'.join(f'![原题图或材料图]({p})' for p in dict.fromkeys(paths or []))
def escape_md(t): return str(t or '').replace('|','\\|')
def image_paths(q):
    # Only assets declared as part of the question are rendered, not unrelated original crops.
    return [p for p in q.get('assets',[]) if isinstance(p,str)]
def material_md(m):
    # Source page crops preserve all table/graph content. Text follows in a collapsed accessible block.
    if m.get('assets'):
        return md_assets(m['assets'])+'\n\n<details><summary>材料文字（图表以原图为准）</summary>\n\n'+m.get('text','')+'\n\n</details>'
    return m.get('text','')

def render_md(qs,materials,articles,day,module,answers=False):
    mm={m['mid']:m for m in materials};aa={a['aid']:a for a in articles}
    suffix='答案原文册' if module=='言语' and answers else '答案册' if answers else '题目册'
    lines=[f'# {day} {module}｜{suffix} · v2','', '[返回第一批入口](README.md)','',
      '言语只做一遍；本册不写解析，参考答案与对照原文保留原口径。' if module=='言语' else '专项每组做完首遍、二刷后再核对答案。', '']
    if module=='资料':lines+=['同一材料的入选设问连续排列，稳定题号不变；135问实际涉及76份材料，不等同于27篇五题材料。','']
    shown=set();current=None
    for q in qs:
        id=q['id'];mid=q.get('material_or_article')
        if module=='资料' and mid!=current:
            current=mid;lines += [f'## 材料 {q["material_display_order"]:02} · {mid}','']
            if not answers:lines +=[material_md(mm[mid]),'']
        lines += [f'### {id}','']
        if not answers:
            lines +=[q['stem'],'']
            paths=image_paths(q)
            if paths:lines += [md_assets(paths),'']
            if any(v!='见图' for v in q['options'].values()):lines +=[f'{k}. {v}  ' for k,v in q['options'].items()]+['']
            if q.get('variant_of'):lines+=['（改编题；与同组其他题的附加条件分别独立使用。）','']
        else:
            lines +=[f'**参考答案：{q["checked_answer"]}**','']
            if module=='言语':
                art=aa[mid]
                dispute=q.get('dispute_note')
                flags=[f for f in q.get('flags',[]) if '争议' in str(f)]
                if dispute or flags:lines += ['原有争议标记：'+str(dispute or '；'.join(flags)),'']
                if mid not in shown:
                    shown.add(mid)
                    kindlabels={'exam_passage':'原题文段（不是外部文章全文）','restored_from_answer':'按原参考答案恢复的文段（非外部原文）','html_original':'用户HTML题库提供的原文（按交付文本照录）'}
                    lines +=[f'**{kindlabels[art["kind"]]}**','']
                    if art.get('title'):lines+=[str(art['title']),'']
                    lines +=[art['text'],'']
                else: lines += ['本篇原文已在本册前面的同篇题下完整列出，请按文章标题对照。','']
            else:
                lines +=[q.get('brief_solution',''),'']
                if q.get('gpt_reading_note'):lines +=['口径提示：'+q['gpt_reading_note'],'']
            src=q['source'];lines +=[f'题源：{src.get("paper_key",src["paper"])} · 原第{src.get("qno")}题 · 题本页{src.get("page",src.get("pages","未记录"))}。','']
    return '\n'.join(lines)+'\n'


def revise_claude(src,out):
    shutil.copytree(src,out,dirs_exist_ok=True)
    # Original handoff reports are retained for provenance, but segregated from current entrypoints.
    historical=out/'原交付记录';historical.mkdir(exist_ok=True)
    for name in ['handoff.md','给用户的交付说明.md','复核清单.md']:
        if (out/name).exists():shutil.move(str(out/name),str(historical/name))
    qs=readj(src/'questions.jsonl'); materials=readj(src/'materials.jsonl');articles=readj(src/'articles.jsonl')
    old_qs=copy.deepcopy(qs);old_by={q['id']:q for q in old_qs};by={q['id']:q for q in qs}
    priority=verify_claude(qs,materials)
    for r in priority:
        q=by[r['id']];q['gpt_audit']={'version':VERSION,'passed':True,'method':r['method'],'evidence':r['evidence']}
    for n in [103,104,105]:
        q=by[f'D03-PD-{n}']
        q['stem']=q['stem'].replace('财政局在人社局的右手边并与之相邻，在住建局的左手边但与之不相邻','财政局在人社局的右侧并与之相邻，在住建局的左侧但与之不相邻（左右均按题面从左到右的排列方向理解）')
        q['gpt_reading_note']='本题已在条件中明确左右坐标；各问附加条件独立，不继承上一问。'
    for n in range(106,111):by[f'D03-PD-{n}']['gpt_reading_note']='“紧接在法务部后面的是……”陈述后继部门存在，因此法务部不能在最后一栋。不是允许末位时把条件当作自动成立。'
    q=by['D03-PD-039']
    q['brief_solution']='答案C。给定立体的两臂由下方实体连成整体，任何观察方向的整体投影轮廓都不会分裂成C所画的两个彼此分开的矩形。题面说“任一角度”，不能只限定为正面、侧面、顶面六个正视方向。D需按原题示意允许斜向观看；不再将D解释为严格的正上方俯视。'
    q['gpt_reading_note']='原图为示意图，D的比例不宜作精确量度；保留原图及参考答案C。'
    reading={
      7:'原图清晰度有限但主要图元可辨；没有用重绘或插值伪造细节。本轮只核对已提供图片。',
      16:'按原图接触点区分相切与相交；该题对线条接触画法敏感，保留图像敏感标记，不声称消除了原图精度问题。',
      19:'只计圆内部的交点，落在圆周上的点不计作圆内；边界读法在答案中明示。',
      21:'只计图形内部的90°角，不把270°凹内角也记成直角。',
      35:'保留原参考答案B。按截面边界而非结构示意理解：穿过空腔的切面不能画成以完整上、下边封住的实心大矩形。原图椭圆及线条比例并不精确；仍有作图约定风险，本轮不将其标成无歧义几何证明。',
      40:'左图是两块方形薄板，不是两个正方体；题问“最不可能”。解释依原题常规摆放示意，不推广为对任意支撑、倾斜状态的物理不可能性证明。',
      61:'按题干语境保留C；“生态系统崩溃”与讨论中的变暖后果相联系。A也具有部分反驳作用，保留原复核中等信心，不冒称形式逻辑唯一性。',
      76:'保留A：它补上课堂安排转化为实际锻炼的联系；D近于复述题干所述效果。仍记录必要前提读法上的争议风险。'}
    for n,note in reading.items():by[f'D03-PD-{n:03}']['gpt_reading_note']=note
    # Lock the actually used source version, avoiding the known misaligned answer file.
    for n in [18,83,84,85]:
        q=by[f'D02-ZL-{n:03}'];q['source']['paper_key']='GK2022F_xc';q['source']['source_commit']=CLAUDE_REF
        q['gpt_reading_note']='使用xingce网友回忆版的本材料原图；不使用另一套GK2022F材料的同题号答案。版本身份未据此判真伪。'
    # A complete audit of verbal ID mapping and available text, not regrading language answers.
    aa={a['aid']:a for a in articles};filled=[];html_matches=[];restored_checks=[]
    verbal=[q for q in qs if q['module']=='言语']
    for q in verbal:
        assert q['checked_answer']==q['source_answer'],q['id']
        a=aa[q['material_or_article']]
        if not a.get('text','').strip():
            assert a['kind'] in ['no_source','source_ref'],(q['id'],a['kind'])
            passage,sep,prompt=q['stem'].rpartition('\n');assert sep and passage.strip() and prompt.strip(),q['id']
            a['original_kind']=a['kind'];a['kind']='exam_passage';a['text']=passage
            a['note']='逐字取自本题题干中设问前的原题文段；未补写、未改写。不是核实到的报刊文章全文，出处若有仅沿用原交付记录。'
            a['extracted_from']=q['id'];filled.append(q['id'])
        if a['kind']=='html_original':
            source=q['source'];para=a['paras'][source['para']-1]
            blank_texts=[para[b['b']:b['e']] for b in source['blanks']]
            norm=lambda s:re.sub(r'\s+','',s)
            expected=q['options'][q['source_answer']]
            assert norm(''.join(blank_texts))==norm(expected),(q['id'],blank_texts,expected)
            html_matches.append({'id':q['id'],'blank_texts':blank_texts,'answer':q['source_answer'],'checked_against':'交付articles.jsonl中的HTML原文段落与字符区间，不冒称访问报刊原站'})
        elif a['kind']=='restored_from_answer':
            assert a['text'].strip()
            choice=q['options'][q['source_answer']]
            if q['topic'].startswith('语句排序'):
                segments={m[1]:m[2] for m in re.finditer(r'^([①②③④⑤⑥⑦⑧])\s*(.*)$',q['stem'],re.M)}
                assert len(segments)==6 and set(choice)==set(segments),q['id']
                a['text']='\n'.join(segments[k] for k in choice)
                a['note']='按原参考答案次序排列原题句段，各句另起一行，保留各句已有标点，不自行补句号；非外部文章原文。'
                a['restoration_method']='sentence_reordering_preserve_punctuation'
                check_evidence='6句全部出现且各一次，按原参考答案重排，句段文字逐字保留'
            else:
                lines=q['stem'].splitlines()
                passage='\n'.join(lines[:-1]) if len(lines)>1 else q['stem']
                pattern=r'_{2,}|＿{2,}|（\s*）|\(\s*\)'
                count=len(re.findall(pattern,passage))
                words=choice.split() if count>1 else [choice]
                assert count==len(words),q['id']
                it=iter(words); restored=re.sub(pattern,lambda m:next(it),passage)
                assert re.sub(r'\s+','',restored)==re.sub(r'\s+','',a['text']),q['id']
                check_evidence='逐空填入原参考答案后，与交付恢复文段逐字相符（仅忽略空白）'
            restored_checks.append({'id':q['id'],'kind':'原参考答案回填/排序文段','text_present':True,'evidence':check_evidence})
        assert not q['brief_solution'].strip(),(q['id'],'verbal explanation unexpectedly present')
        q['gpt_audit']={'version':VERSION,'scope':'题号/原文对象映射、文本非空、参考答案未改；HTML空缺逐字对应另有检查记录','passed':True}
    assert len(filled)==54 and len(html_matches)==31 and len(restored_checks)==35
    assert len(verbal)==120 and all(aa[q['material_or_article']]['text'].strip() for q in verbal)
    # Reorder by material, without altering stable IDs or discarding selected questions.
    data=[q for q in qs if q['module']=='资料'];groups=OrderedDict()
    for q in data:groups.setdefault(q['material_or_article'],[]).append(q)
    assert len(groups)==76 and sum(map(len,groups.values()))==135
    reordered=[];mapping=[]
    for k,(mid,items) in enumerate(groups.items(),1):
        for q in items:
            q['original_group']=q['group'];q['original_order']=q['order']
            q['material_display_order']=k;q['display_order']=len(reordered)+1
            q['group']=f'ZL01-M{k:02}';q['group_title']=f'材料{k:02}';q['order']=len(reordered)+1
            mapping.append([q['id'],old_qs.index(old_by[q['id']])+1,q['display_order'],mid,k,q['topic']]);reordered.append(q)
    qs=[q for q in qs if q['module']!='资料']+reordered
    qs.sort(key=lambda q:(q['day'], {'资料':0,'判断':0,'言语':1}[q['module']],q.get('display_order',int(q['id'].rsplit('-',1)[1]))))
    # Verify declared assets and one-to-one mappings.
    missing_assets=[]
    for obj in qs+materials:
        for p in obj.get('assets',[]):
            if isinstance(p,str) and not (src/p).is_file():missing_assets.append(p)
    assert not missing_assets,missing_assets
    assert len(qs)==390 and len({q['id'] for q in qs})==390
    assert all(q['checked_answer']==old_by[q['id']]['checked_answer'] for q in qs)
    assert all(q['options']==old_by[q['id']]['options'] for q in qs)
    prohibited=[q['id'] for q in qs if re.fullmatch(r'GD202[456](?:X|Z)?(?:_xc)?',q['source']['paper']) and not q.get('variant_of')]
    assert not prohibited,prohibited
    # Reorder the source HTML nodes so the original image embedding and original text are preserved.
    for answers in [False,True]:
        name='D02_资料_'+('答案册' if answers else '题目册')+'.html'
        soup=BeautifulSoup((src/name).read_text(),'html.parser')
        qnodes={n.get('id') or n.select_one('.qid').get_text(strip=True):n for n in soup.select('.q')};assert len(qnodes)==135
        for qid,node in qnodes.items():node['id']=qid
        mnodes={}
        for n in soup.select('.mat'):
            mt=n.select_one('.mt')
            if mt:
                match=re.search(r'ZLM-[A-Za-z0-9_-]+',mt.get_text())
                if match:mnodes.setdefault(match[0],n)
        main=soup.find('main');h=main.find('h1');meta=main.find('div',class_='meta')
        content=[h.extract()]
        if meta:content.append(meta.extract())
        scripts=[x.extract() for x in main.find_all('script')]
        main.clear()
        for node in content:main.append(node)
        n=soup.new_tag('p');n.string='v2：按同一材料连续作答，稳定题号不变。135问、76份独立材料；技能标签仅留在结构化索引。';main.append(n)
        for k,(mid,items) in enumerate(groups.items(),1):
            head=soup.new_tag('h2');head.string=f'材料{k:02} · {mid}';main.append(head)
            if not answers:
                assert mid in mnodes,mid
                main.append(mnodes[mid].extract())
            for q in items:main.append(qnodes[q['id']].extract())
        for node in scripts:main.append(node)
        assert len(soup.select('.q'))==135
        assert len(soup.select('.mat'))==(0 if answers else 76)
        write(out/name,str(soup))
    # Direction and view explanations are reflected in the HTML too.
    for answers in [False,True]:
        name='D03_判断_'+('答案册' if answers else '题目册')+'.html'
        soup=BeautifulSoup((src/name).read_text(),'html.parser')
        for node in soup.select('.q'):
            if not node.get('id'):node['id']=node.select_one('.qid').get_text(strip=True)
        for id in [f'D03-PD-{n:03}' for n in ([39]+list(reading)+list(range(106,111)) if answers else [103,104,105])]:
            node=soup.find(id=id);assert node,id
            if not answers:
                old=old_by[id]['stem'];new=by[id]['stem']
                # The first direct div in a question card is its stem.
                target=node.find('div',recursive=False);assert target
                target.clear()
                for i,line in enumerate(new.split('\n')):
                    if i:target.append(soup.new_tag('br'))
                    target.append(line)
            else:
                if id=='D03-PD-039':
                    # Replace only the solution text, retain answer and source metadata.
                    texts=list(node.find_all(string=True))
                    old=old_by[id]['brief_solution']
                    found=False
                    for t in texts:
                        if old in str(t):t.replace_with(str(t).replace(old,by[id]['brief_solution']));found=True
                    if not found:
                        # Some line breaks split the paragraph; remove exact solution containers only.
                        for div in node.find_all('div'):
                            if div.get_text().strip()==old:div.clear();div.string=by[id]['brief_solution'];found=True;break
                    assert found,('could not replace PD039 solution',str(node)[:500])
                if by[id].get('gpt_reading_note'):
                    note=soup.new_tag('p');note['class']='meta';note.string='v2口径提示：'+by[id]['gpt_reading_note'];node.append(note)
        write(out/name,str(soup))
    writej(out/'questions.jsonl',qs);writej(out/'articles.jsonl',articles)
    with (out/'D02_材料连续编排对照.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['stable_id','original_dataset_line','new_display_order','material_id','material_number','skill_tag']);w.writerows(mapping)
    # Markdown online editions and clean verbal HTML answer/original editions.
    css='body{font-family:system-ui,sans-serif;line-height:1.8;color:#222;background:#fafafa;margin:0}main{max-width:900px;padding:24px;margin:auto}h1,h2{line-height:1.4}.q{padding:20px 0;border-bottom:1px solid #ddd}.original{white-space:pre-wrap;margin:12px 0}.meta{font-size:.9rem;color:#555}img{max-width:100%}'
    for day,module in [('D01','言语'),('D02','资料'),('D02','言语'),('D03','判断'),('D03','言语')]:
        subset=[q for q in qs if q['day']==day and q['module']==module]
        for answers in [False,True]:
            suffix='答案原文册' if module=='言语' and answers else '答案册' if answers else '题目册'
            write(out/f'{day}_{module}_{suffix}.md',render_md(subset,materials,articles,day,module,answers))
        if module=='言语':
            chunks=[f'<h1>{day} 言语｜答案原文册 v2</h1><p>只列原参考答案和原文，不加解析。题库恢复文段不冒充外部文章全文。</p>'];shown=set()
            for q in subset:
                art=aa[q['material_or_article']];chunks.append(f'<section class="q" id="{q["id"]}"><h2>{q["id"]} · 参考答案 {q["source_answer"]}</h2>')
                dispute=q.get('dispute_note') or '；'.join(str(f) for f in q.get('flags',[]) if '争议' in str(f))
                if dispute:chunks.append('<p class="meta">原有争议标记：'+html.escape(str(dispute))+'</p>')
                if art['aid'] not in shown:
                    shown.add(art['aid']);kind={'exam_passage':'原题文段（非外部文章全文）','restored_from_answer':'按原参考答案恢复的文段（非外部原文）','html_original':'用户HTML题库提供的原文（按交付文本照录）'}[art['kind']]
                    chunks.append('<p class="meta">'+kind+'</p><div class="original">'+html.escape(art['text'])+'</div>')
                else:chunks.append('<p class="meta">本篇原文已在前面的同篇题下列出。</p>')
                chunks.append('</section>')
            write(out/f'{day}_言语_答案原文册.html','<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+day+'言语答案原文</title><style>'+css+'</style><body><main>'+''.join(chunks)+'</main></body></html>')
    oldverbal=[q for q in verbal if re.search(r'201[3-6]',q['source']['paper'])]
    data_hist=Counter(len(items) for items in groups.values())
    audit={'version':VERSION,'source_commit':CLAUDE_REF,'total_questions':390,'counts':dict(Counter(q['day']+'-'+q['module'] for q in qs)),
      'priority_11':priority[:11],'additional_enumerated_5':priority[11:],
      'data_grouping':{'questions':135,'unique_materials':76,'old_rendered_material_blocks':100,'new_rendered_material_blocks':76,'removed_duplicate_blocks':24,'questions_per_material_histogram':dict(data_hist)},
      'verbal':{'questions':120,'answer_keys_unchanged':120,'all_article_ids_resolve':True,'original_blank_article_texts':54,'filled_with_exact_exam_passage':filled,'external_full_articles_still_unverified':54,'html_blank_matches':html_matches,'answer_restored_passages':restored_checks,'new_explanations_added':0},
      'structural':{'unique_ids':390,'no_missing_declared_assets':True,'prohibited_originals_present':prohibited,'original_answer_options_unchanged':True},
      'old_verbal_source_years':[{'id':q['id'],'source':q['source']['paper'],'topic':q['topic']} for q in oldverbal],
      'limits':['这不是390题逐题重解：实体复核为11道重点题、5道组合题及定点图像/口径审阅。','原题片段、参考答案回填段落与用户HTML原文分别标示；未获得的外部文章全文不假称已补齐。','10道原解析争议逻辑题仍隔离；图像作图约定风险保留。','36道言语原题来自2013—2016，沿用原交付但明列，不计入近十年原题统计，不据此自动扩展后续范围。']}
    write(out/'GPT_复核结果_v2.json',json.dumps(audit,ensure_ascii=False,indent=2))
    rows=['# 第一批 v2 审核报告','',f'源：Claude分支快照`{CLAUDE_REF}`。本目录是GPT审核副本，不覆盖Claude分支。','',
      '## 实际完成','',
      '- 390题及关联资产完整性检查；所有原参考答案、全部选项保持不变。',
      '- 11道重点题独立核验通过；另对PD106—110穷举复核。',
      '- 资料135问按76份材料连续编排，原100次材料插入减为76次，减少24次重复展示；题量与题号不变。76份材料的阅读负荷仍然存在，不能表述成27篇。',
      '- 言语120题全部有对照文本：35题为参考答案恢复文段，31题对应6篇用户HTML原文，54题补上原题文段。HTML的31题空缺均与所附原文字符区间及参考答案逐字对应；另逐字核对23个填空恢复段，并将12个排序段按原句逐行重排、保留已有标点。不添加解析，不改争议标记或标答。',
      '- 3道座位改编明确左右方向；5道办公楼组合题注明法务必须有后继部门；PD039去掉“D为正上方俯视”的不当解释。', '',
      '## 重点核验','', '| 题号 | 结果 | 证据摘要 |','|---|---|---|']
    evidence={
      'D02-ZL-018':'9635.6÷1.061÷6÷10000≈0.1514亿，单位转换与基期回推均已核。',
      'D02-ZL-075':'按2023/2022逐年外推至2019两倍：A需43年、B需5年、C需30年、D需10年（均为2023之后的整年数）。',
      'D02-ZL-083':'(450.8−228.6)−(50.2−24.2)=196.2亿。',
      'D02-ZL-084':'总发电增速减风电增速约−22.39个百分点。',
      'D02-ZL-085':'累计增速上升月份4、5、6、7、9、10、11月，共7个月。',
      'D02-ZL-101':'类别、范围和指标分清；公园新增4+4+14=22个。',
      'D02-ZL-114':'日均原煤环比增加49万吨；同比/环比及增速/产量不可互换。',
      'D03-PD-102':'35个四人组合枚举，唯一乙、丁、己、庚。',
      'D03-PD-103':'6!全枚举，3个可行排列，仅A必然。',
      'D03-PD-104':'6!全枚举，2个可行排列，仅C必然。',
      'D03-PD-105':'6!全枚举，2个可行排列，仅B可能。'}
    # Use computed values in report, never assume rounded year thresholds.
    ys={k:v['further_whole_years'] for k,v in priority[1]['evidence'].items()}
    evidence['D02-ZL-075']='从2023年起按当年增速逐年外推，首次达到2019年两倍的额外整年数：'+ '、'.join(f'{k}={ys[k]}' for k in 'ABCD')+'；B最早。'
    rows += [f'| {r["id"]} | {r["answer"]}，通过 | {evidence[r["id"]]} |' for r in priority[:11]]
    rows += ['', 'PD106—110独立枚举得到A、B、C、B、C。详细状态数、选项真值次数及精确计算见[机器核验记录](GPT_复核结果_v2.json)。','',
      '## 仍须如实保留的限制','',
      '**不是390题全量重解通过。** 其余题沿用Claude原有核验，本轮只做结构检查和必要抽查。图像题PD016、PD035等依赖画法和接触约定；PD039斜视比例不严，保留提示，不能用程序通过冒充原图无歧义。', '',
      '**54题外部文章全文并未补得。** 已补的是题干里原有的完整考试文段，逐字照录，不是网上原文章全文。用户HTML31题的文章按交付数据照录并核空缺，本轮未访问人民日报原站重新比对整篇。', '',
      '**题源年份例外：**原交付中36道言语来自广东2013—2016年，其题型为选词、主旨、意图、细节、词句理解等已在当前框架中的结构。本轮没有新增这些老卷，也不把它们写成“近十年真题”。下表列明，后续选题不能据此自动扩张年份范围。','',
      '| 题号 | 原卷 | 题型 |','|---|---|---|']
    rows += [f'| {q["id"]} | {q["source"]["paper"]} | {q["topic"]} |' for q in oldverbal]
    rows += ['', '**版本与冲突：**GK2022F_xc四道重点题使用其材料原图独立解算，未使用已知错位的另一版本答案键；两个同名年份卷未据此判真伪。PD-B-X01～X10继续隔离，不作为正式题量，也未为了裁决争论而重新入包。','',
      '资料的76份材料全部有入选设问；题号沿用原ID，新的显示顺序见[D02材料编排对照](D02_材料连续编排对照.csv)。']
    write(out/'GPT_审核报告_v2.md','\n'.join(rows)+'\n')
    rows=['# Claude第一批｜GPT审核副本 v2','', '390题：D02资料135、D03判断135、D01—D03言语120。题号不变；下列Markdown可直接在GitHub在线阅读，图形使用原题图片。','',
          '| 日程 | 内容 | 题本 | 答案／原文 |','|---|---|---|---|']
    for day,module in [('D01','言语'),('D02','资料'),('D02','言语'),('D03','判断'),('D03','言语')]:
        suffix='答案原文册' if module=='言语' else '答案册'
        rows +=[f'| {day} | {module} | [打开]({day}_{module}_题目册.md) | [两遍后看]({day}_{module}_{suffix}.md) |' if module!='言语' else f'| {day} | {module} | [打开]({day}_{module}_题目册.md) | [做完后看]({day}_{module}_{suffix}.md) |']
    rows +=['', '[审核范围、结果和遗留限制](GPT_审核报告_v2.md)｜[核验数据](GPT_复核结果_v2.json)｜[第一轮总入口](../../第1轮_使用入口.md)','',
      '**注意：**资料135问实际涉及76份材料；已合并同材料问题，但未把材料数伪装成27篇。言语35题为答案回填文段、31题为用户HTML原文、54题为原题文段；后者不是外部文章全文。原交付中的36道2013—2016言语另列在审核报告。','',
      '11道重点题及5道办公楼组合题已经GPT独立复核；其余题不冒称全量二次盲审。原争议逻辑备选仍隔离，不计入390题。']
    write(out/'README.md','\n'.join(rows)+'\n')
    return audit


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--main',required=True,type=Path);ap.add_argument('--claude',required=True,type=Path);ap.add_argument('--out',required=True,type=Path)
    args=ap.parse_args();root=args.out/PROJECT;root.mkdir(parents=True,exist_ok=True)
    d01,changes,qr=revise_d01(args.main/PROJECT/'GPT_数量/D01',root/'GPT_数量/D01',args.claude/PROJECT/'共享输入/数量原文')
    ca=revise_claude(args.claude/PROJECT/'Claude_资料判断言语/第1批',root/'GPT_复核/第1批')
    write(root/'第1轮_使用入口.md',f'''# 第1轮三天训练｜当前入口

版本：{VERSION}。实际题量 **525题**：D01数量135、D02资料135、D03判断135，加三天言语120。没有增加你的日计划，也没有把二刷或修订计作新题。

| 日程 | 专项（135题） | 当天言语（40题） |
|---|---|---|
| D01 | [数量v2：题本与答案入口](GPT_数量/D01/README.md) | [言语题本](GPT_复核/第1批/D01_言语_题目册.md) · [答案原文](GPT_复核/第1批/D01_言语_答案原文册.md) |
| D02 | [资料题本](GPT_复核/第1批/D02_资料_题目册.md) · [答案](GPT_复核/第1批/D02_资料_答案册.md) | [言语题本](GPT_复核/第1批/D02_言语_题目册.md) · [答案原文](GPT_复核/第1批/D02_言语_答案原文册.md) |
| D03 | [判断题本](GPT_复核/第1批/D03_判断_题目册.md) · [答案](GPT_复核/第1批/D03_判断_答案册.md) | [言语题本](GPT_复核/第1批/D03_言语_题目册.md) · [答案原文](GPT_复核/第1批/D03_言语_答案原文册.md) |

## 本轮已处理

D01四道已做数推换题；修复M094对M085的泄题；弱变式重做、答案笔误及来源说明同步修订。Claude首批11道重点题和5道办公楼组合题独立核验；资料按材料连续重排；言语补齐实际可用的对照文段，不加解析，不改标答。

## 使用前需知道的边界

资料135问仍来自76份材料，不是27篇；仅减少同材料跨组重复阅读。言语54题补的是原题文段，外部文章全文未核得；原交付36道言语为2013—2016老卷，来源明列，并未冒称近十年。图像约定与部分逻辑前提的风险仍在答案册提示中保留。

[数量修订记录](GPT_数量/D01/D01_v2_修订记录.md)｜[Claude第一批审核报告](GPT_复核/第1批/GPT_审核报告_v2.md)

Claude原分支未修改；本入口引用的是已同步的审核副本。修订未被再次送给Claude盲审，不能把旧版复核或局部抽查写成525题全部双盲通过。
''')
    write(root/'交接/GPT给Claude_第1轮修订与审核完成_v2.md',f'''# GPT → Claude｜第一轮修订及审核落地回执

版本{VERSION}。读取你的快照`{CLAUDE_REF}`，并在main原快照`{MAIN_REF}`上构建。你的源分支未覆盖。

## 已落地
- D01同题号135题已修订，详见`../GPT_数量/D01/D01_v2_修订记录.md`；N005/N014/N020/N028分别换为ZJ2021A-53、ZJ2023A-53、JS2020A-46、SZ2023-48。未采用GD2023Z-33的小数尾零选项。
- M017、M019重写为带整数可行域的变式，M051蒸发90g、结果25%，M056重写为两层加权平均新编；M057/M059改标新编结构参照。M094成本55、结果18天，不再泄露M085。已修M089及等号、选项说明。
- 你交付的390题复制为`../GPT_复核/第1批/`审核副本：原键/选项不改。11道优先复核＋PD106—110独立复核一致；方向表述和PD039视图解释作明示修订。
- 资料统一按材料连续排列，135问/76材料，从100次材料展示降至76次；不能报告成27篇。稳定题号保留。
- 言语54个空正文对象补为原题文段，非外部文章全文；31个HTML空缺与交付原文逐字对应；23个填空恢复段逐字核对、12个排序段按原参考顺序保留原句标点。不输出你的source_note解析，不改争议标答。
- 数据/题本/答案/在线Markdown/编排表已同步，核验范围与图像风险详见审核报告。

## 接续注意
1. 以当前v2题本、答案和完整JSONL为准；不要用旧键覆盖N005/N014/N020/N028、M017/M019/M051/M056的新键。
2. GD2021X-38与GD2021Z-41已同题锁定。GK2022F_xc独立版本键保留，勿再以另一卷同号解析覆盖。
3. 10道争议逻辑继续隔离，不为裁决争论放回正式包。
4. 36道2013—2016言语在原交付中已存在，本轮明列来源且未新增；不要把它们算成近十年，也不要据此自动放开后续年份。54道片段外部文章全文仍未核得，不能把原题段落当外部全文。
5. 全量390只是结构检查；实体复核是指定重点及定点抽查。旧版115/135复核不能套给新改动。需要再次盲审的重点是新M017/M019/M051/M056和4道新数推。

用户无需逐题转述。本回执是已写回内容的索引，不表示已经通知到另一个模型。
''')
    summary={'version':VERSION,'quantity':135,'claude_batch':390,'total':525,'d01_changed_ids':list(changes),'quantity_checks':len(qr['checks']),'claude_priority':len(ca['priority_11']),'claude_additional_enumerated':len(ca['additional_enumerated_5']),'source_refs':{'main':MAIN_REF,'claude':CLAUDE_REF}}
    write(root/'GPT_复核/第1批/构建摘要.json',json.dumps(summary,ensure_ascii=False,indent=2))
    # Content checksums make the locally reviewed output comparable to the repository-built output.
    manifest={str(p.relative_to(args.out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(args.out.rglob('*')) if p.is_file() and p.name!='release_manifest.json'}
    write(args.out/'release_manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2))
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':main()

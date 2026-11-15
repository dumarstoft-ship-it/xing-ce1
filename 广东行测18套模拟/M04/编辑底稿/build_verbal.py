#!/usr/bin/env python3
"""M04言语编辑底稿。只读取原库；编选、解析和消歧记录在此。"""
import copy, json, re
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
JZ='江浙行测_AI题库/questions.jsonl'
GK='国考/言语理解/2016-2025/all.jsonl'
questions={q.get('question_id',q.get('id')):q for fn in [JZ,GK] for q in map(json.loads,(ROOT/fn).read_text(encoding='utf-8').splitlines())}
jz_answers={q['question_id']:q for q in map(json.loads,(ROOT/'江浙行测_AI题库/answers.jsonl').read_text(encoding='utf-8').splitlines())}
pdf_checks={r['number']:r for r in json.loads((HERE.parent/'核验记录/verbal_pdf_sources.json').read_text(encoding='utf-8'))}
# 编者先答记录单独留存，未把候选阶段的异议删掉。
choices=[
(16,'GKYY-2025-040','B','逻辑填空'),
(17,'ZJ2025-A类-032','B','逻辑填空'),
(18,'GKYY-2025-055','D','逻辑填空'),
(19,'ZJ2026-A类-028','A','逻辑填空'),
(20,'GKYY-2025-036','D','逻辑填空'),
(21,'GKYY-2025-020','D','意图判断'),
(22,'GKYY-2024-052','D','意图判断'),
(23,'ZJ2025-A类-034','A','标题选择'),
(24,'ZJ2024-A类-045','C','语句填空'),
(25,'GKYY-2025-044','C','细节理解（正向）'),
(26,'GKYY-2025-062','C','语句排序'),
(27,'GKYY-2025-048','A','语句填空'),
(28,'ZJ2024-A类-046','B','细节理解（选非）'),
(29,'GKYY-2024-066','A','意图判断'),
(30,'GKYY-2025-059','D','细节理解（选非）'),
]
analyses={
16:'文段肯定借鉴，但反对忽略当地条件地照原样搬用。第一空“照搬”准确表达后一层意思；“效仿”本身不必然忽略条件，与文段的批评不完全对应。第二空说主产区、主销区的情况差别大，“大相径庭”合适，“背道而驰”偏重方向、目标相反。第三空紧扣外地经验不适合本地条件，应是“水土不服”；“功亏一篑”要求接近成功却未能完成，“物极必反”要求事物发展到极点，题面均无此意。三空合看选B。不要把所有近义词都说成第一眼即可排除：第一空的“套用”“复制”也有迷惑性，须结合后两空判断。',
17:'前两句说明多国已相继采取行动，第一空“风起云涌”可概括多种活动兴起的态势。第二空随后拿“当前太空竞赛”与“冷战期间的美苏太空竞赛”比较，重点是新一轮竞赛再度出现，“卷土重来”与此衔接；“箭在弦上”侧重尚待行动的紧迫状态，与前文已经发生的行动不合，“愈演愈烈”侧重程度不断加剧，而题面突出的是再次出现及特点变化。第三空“冲击现有太空秩序”也与亟须规范相接。选B。“卷土重来”在此是借用其再次兴起的意思，不必另造题面没有的某国曾经失败这一事实。',
18:'第一空承接“既需要政府……也需要市场……”，强调两者都发挥作用，“共同”准确；“系统”“有序”分别侧重整体性、秩序性，没有直接照应双方共同参与。第二空“束缚发展”与“堵点卡点”相配，第三空“顺畅流动”又与前面的“打通”照应，构成消除阻碍、促进要素流动的完整关系。A的“联合”虽有迷惑性，但“竞相流动”额外突出争先竞争，题面没有这一层；B的“自由”、C的“高效”不如“顺畅”直接回应流动中的堵点。三空合看选D，不必仅凭一个词就把其他组合说成绝对不能使用。',
19:'文段把研学中的两类问题相对照：一类在出发前安排好，一类在旅行现场由孩子提出。第一空“预设”与这种事先安排相符，第二空“鲜活”突出来自现场的具体问题。第三空的宾语是“孩子们感兴趣的研究主题”，组织者要善于发现、抓住这些主题，“捕捉”恰当；“延伸主题”是进一步扩展已有主题，“激发”通常搭配兴趣、思考等，“引导主题”也没有准确表达发现兴趣所在。A三空最协调。此题源库未提供参考答案，A为本卷编辑推导，待独立复核。',
20:'第二空由“更湿润且波动更大”约束，降水并非更加均匀、持续，而是分布波动增强，“极端性”最合适；“偶然性”指偶发，“持续性”强调延续，“集中性”只强调聚集，均不能像D那样概括题给的两种变化。第一空描述人们欢迎雨量丰盈又温和均匀的状态，“喜闻乐见”合适。“望眼欲穿”“翘首以盼”侧重急切等待，“津津乐道”侧重谈论兴趣，与这里直接评价某种变化型的语意不如D贴切。选D。',
21:'文段先交代企业发展是银行持续盈利的基础，再解释当前净息差降低的作用：企业获得低成本贷款，减轻负担并投入创新升级；实体经济发展又为银行发展奠定基础。D将“降低净息差”这一具体机制与企业、银行共同受益的结果完整连接起来。A和B所说的金融与实体经济相互关系是文段的理论前提，未概括中间重点展开的息差变化及其作用；C提出“保持合理水平”，题面没有讨论合理水平的界限或维持它的办法。选D。这里依据的是文段给出的推理，不是向外推断净息差越低越好。',
22:'前半段说明村落中的历史信息经过积累、遮蔽，并非真的没有传统；后半段回答如何发现这些信息，明确提出长时间田野调查、与原住民交流，进而寻找当地人能接受的艺术形式。D覆盖这一实际主张。A只说发掘整理信息，未指出艺术乡建中的调查路径；B把着力点限定为“复原村落特色”，文段还强调理解当代居民的审美，并未主张照旧恢复；C将对象扩大为传统村落振兴，又把历史细节说成基础。选D。田野调查在这里包含与居民的深入交流，不只是清点旧建筑。',
23:'前两句列出发现脉冲星和高效处理海量数据的成绩，后文解释原因：自研AI算法等智能计算技术，让研究人员摆脱繁重分析、提高科研效率。A的“金刚钻”对应具备的技术能力，“瓷器活”对应由此能够承担的研究工作，保留了“能力支撑成果”的关系。B的“遥遥领先”、C的“成功源于细节”、D的“经历艰苦磨炼”均不是题面提供的成就依据。选A。这不是在几句好听的赞语中挑最响亮的一句，而是要看比喻能否对应事实之间的关系。',
24:'横线前比较文化产业发展的动力：过去是文化消费市场化，现在是数字平台及数字技术；横线后说“同样的逻辑亦能解释”文化产业数字化为何强烈需要前沿技术。C点明数字技术成为新的发展动力，既承接前文，也解释后文的技术需求。A转向企业选择平台，没有概括产业动力变化；B的技术创新与后文相关，但泛化为必要对策，弱化了前后的数字技术这一具体关系；D额外引入政府“有形之手”，题面没有这层讨论。选C。',
25:'题干明确给出了“月球没有大气层、磁场很弱→太阳风能够直射月面→氦-3注入月壤”的解释链，正对应C。A问储量“如何换算”，材料只给出了换算结果；B问低温“如何”促进吸附，材料只陈述低温能促进吸附，没有继续解释微观机制；D问开采方法，材料没有涉及。选C。出现某个概念或给出一个结论，不等于已经解释了它的计算过程、作用机制或实施办法。',
26:'③介绍电工技术发展初期，普通天然材料即可满足绝缘要求；⑤用“因而”“当时”紧接，解释没有专用材料、工艺和结构概念的原因。②再写经济效益、性能稳定性要求提高，专门绝缘材料由此分离出来；⑥进一步写电压、应用领域和环境因素带来更高要求，①承接说明一般材料和简单工艺已不足，需要专门材料及结构。④的“这样一来”总结前面的解决路径，落到组合绝缘结构的开发与新阶段。顺序为③⑤②⑥①④，选C。④必须放在①提出特定材料和结构之后，不能先出现开发结果再补写需要。',
27:'横线之前从两方面说明新业态扩大就业：一是创造高技能新岗位，二是通过传统产业转型再造原有职业和岗位；紧接着用超2亿灵活就业人员提供规模佐证。结尾应总括其吸纳就业的作用，A合适。B新增跨区域资源互补，题面没有讨论；C只保留高技能劳动力，漏掉岗位再造等另一面；D限定为“重点群体”，文段未界定这一群体，也未围绕某一特定群体的压力展开。选A。',
28:'B把“江南炒青或蒸青”概括为都用早春新茶，与明确的例外冲突：蒸青的罗岕茶使用初夏新茶，仍有春天气息，但不是早春新茶。A对应明清饮用江南炒青、蒸青新茶的总体风尚；C对应武夷茶农原先遵循江南绿茶风尚；D对应文段所述清初武夷山开始饮用发酵陈茶。选B。判断全称表述时，只需一个题面明示的例外即可否定。本卷给C、D补足语境边界，避免把地区风尚变化误读为全国最早出现发酵茶的断言。',
29:'行政复议处于管理链条末端，案件却能反映前端制度或执行中的问题；机关应利用这些反馈纠正个案、完善制度、规范新问题。A概括了“通过复议发现和修正问题，从而改进管理”的完整主张。B只概括后半段分类处置的方法；C停留在链条关系，D停留在案件反映问题，二者都没有包含作者要求机关采取的改进动作。选A。这里不是只把一件复议案办结，而是让末端反馈促进整个管理过程改进。',
30:'材料比较的是两种成像技术提取图像信息的机制：传统技术依据确定性理论、利用一阶关联信息，量子技术依据量子统计不确定性理论、利用高阶关联信息；后者因此有更高的成像分辨能力。A对应量子技术获取图像的方式，B对应传统技术的理论基础，C对应高阶关联信息与分辨能力的联系。D问两种雷达发射的信息载体有何不同，文段并未说明发射载体差异，不能把获取、提取信息的机制差异改写成发射载体的差异。选D。题目无需考生补充量子物理知识，只须准确定位材料解释了什么。',
}
reasons={
16:'把借鉴与照搬区分开，并以第三空检验外地经验不适用的因果关系。',
17:'同一主题下区分再次兴起、程度加剧和尚待行动，三空相互校验。',
18:'从既要又要、打通堵点到要素流动的连贯关系校验三空，不只凭政策熟词作答。',
19:'在真实研学情境中辨别预设主题与现场问题，再以动宾搭配收束。',
20:'将材料描述的变化翻译成恰当词义，不只凭欢迎雨水的感情色彩选项。',
21:'区分金融与经济关系这一背景总论，和净息差变化带来共赢的具体论证中心。',
22:'理解材料由历史信息到乡建方法的递进，防止主旨停留在漂亮的背景概括。',
23:'把标题中的比喻还原为“技术能力支撑科研成果”的因果关系。',
24:'跨空观察前后的动力与需求关系，检验候选句能否同时承接两边。',
25:'区分“提及结论”与“解释机制”，科学材料无需外部专业知识即可作答。',
26:'按初期条件、专门材料分离、更高要求及结构创新组织六句，同时核查因果与指代。',
27:'总结两条就业机制，防止熟悉的政策词语造成主体或范围偷换。',
28:'历史叙述中的地区、时间与全称边界；保留早春与初夏这一可证伪点。',
29:'从末端案件反馈到前端治理改进，区分事实、方法与总主张。',
30:'在较密的科学说明中区分理论基础、信息提取机制、性能结果与未涉及的发射载体。',
}
def clean_stem(s):
    lines=[v.strip() for v in s.splitlines() if v.strip()]
    if lines and lines[0].startswith('①'):
        return '\n'.join(lines)
    if len(lines)>1:
        s=''.join(lines[:-1])+'\n'+lines[-1]
    else:s=lines[0]
    return re.sub(r'[ \t]*(_+)[ \t]*',r'\1',s)
rows=[]
for n,sid,answer,subtype in choices:
    sq=questions[sid];is_gk=sid.startswith('GKYY-');sf=GK if is_gk else JZ
    source_answer=sq.get('answer') if is_gk else jz_answers[sid].get('correct_answer')
    opts=copy.deepcopy(sq['options']);stem=clean_stem(sq['stem'])
    edits=[]
    if stem!=sq['stem']:
        edits.append({'type':'layout_only','description':'合并源PDF行末硬换行，保留设问独立成段；填空线两侧删除排版空格；六句排序逐句保留换行。不删减正文与限定条件。','version':'0.1.0'})
    if n==28:
        before={k:opts[k] for k in ['C','D']}
        opts['C']='改变饮茶风尚前，武夷茶农曾受江南影响'
        opts['D']='清初的武夷山地区开始兴起饮用发酵茶'
        edits.append({'type':'disambiguation','description':'C不再把未明示的“原先”严格固定为明代；D补武夷山地域，避免将地区风尚变化扩大成全国饮用发酵茶的最早起源。原有正确答案及早春/初夏考点不变。','before':before,'after':{k:opts[k] for k in ['C','D']},'version':'0.1.0'})
    check=pdf_checks[n]
    assert check['source_id']==sid, f'第{n}题PDF核验仍指向旧题源'
    loc={'original_number':check['original_number'],'pages':check['pdf_pages'],'source':copy.deepcopy(sq.get('source')) if not is_gk else {'repository':check['source_repository'],'commit':check['source_commit'],'file':check['source_file'],'blob_sha':check['source_blob_sha'],'pdf_pages':check['pdf_pages'],'page_numbering':'PDF physical page, 1-based'}}
    notice=('题面取自仓库国考言语整理库，已取得对应原PDF并补录卷别、原题号、物理页码和git blob。GKYY序号是整理库编号，不冒称原卷题号；参考答案是原资料答案，不冒称官方答案。' if is_gk else '题面取自江浙整理库，已取得source中列出的原PDF并核对文字及选项，文件git blob与记录一致。浙江试题保留网友回忆版身份，参考答案是配套资料答案，不冒称官方答案。')
    if n==19: notice+='此题源库未提供参考答案，A是本卷编辑推导，不登记为源参考答案。'
    row={'number':n,'section':'言语理解与表达','subtype':subtype,'question_type':'single_choice','source_bank':'national_verbal' if is_gk else 'jiangzhe','source_file':sf,'source_id':sid,'source_question':copy.deepcopy(sq),'stem_override':stem,'options':opts,'source_answer':source_answer,'answer':answer,'analysis':analyses[n],'selection_reason':reasons[n],'edits':edits,'verification':{'status':'editor_checked_pending_cross_review','independent_answer':answer,'source_answer_available':bool(source_answer),'source_answer_agreement':answer==source_answer if source_answer else None,'method':'编者先读无答案题面作答并留存记录，再比对源参考答案；这是编者自核，不冒称隔离盲审或Claude外审。','checked_on':'2026-11-15','completeness':'题干与四选项完整，无共用文章及缺题标记；国考氦-3题两处嵌图负温度已目检原PDF。','source_check':'已下载对应原PDF，git blob哈希一致，比较题干与四选项；仅记录已查阅页面，不推断其他卷别。详见核验记录/verbal_pdf_sources.json。','source_pdf_review':{'reviewer':'GPT言语编辑','reviewed_version':'0.1.0','report':'核验记录/verbal_pdf_sources.json','pdf_file':check['source_file'],'pdf_git_blob_sha':check['source_blob_sha'],'blob_match':check['download_blob_match'],'pdf_pages':check['pdf_pages']},'prior_output_check':{'method':'排除M01–M03现用及撤题源ID；跨卷正文相似项另由整卷核验。','previous_project_source_id_match':False,'limit':'不据此声称用户从未做过。'}},'source_locators':loc,'source_notice':notice}
    if not is_gk:
        ar=jz_answers[sid]
        row['source_answer_reference']={'file':'江浙行测_AI题库/answers.jsonl','source':copy.deepcopy(ar.get('source')),'quality_flags':copy.deepcopy(ar.get('quality_flags',[]))}
    if n in {18,21,26,30}:
        row['replacement_history']={'reason':'整卷登记去重发现原题已用于M01/M02，撤下后换为未用题。','archive':'编辑底稿/历史内部核验/verbal_before_duplicate_replacements','independent_editor_answers':'编辑底稿/verbal_replacements_initial_answers.json','new_blind_input':'编辑底稿/verbal_replacements_blind.json','prior_review_does_not_cover_current_question':True}
    rows.append(row)
def previous_source_ids():
    """从实际旧卷与登记重新建集，避免稀疏检出未完成时的缓存漏项。"""
    found=set()
    def scan(value):
        if isinstance(value,dict):
            for key,item in value.items():
                if key in {'source_id','question_id','id','material_id','source_material_id'} and isinstance(item,str):
                    found.add(item)
                scan(item)
        elif isinstance(value,list):
            for item in value:scan(item)
    base=HERE.parents[1]
    for paper in ('M01','M02','M03'):
        for fn in (base/paper).rglob('*'):
            if fn.suffix=='.json':scan(json.loads(fn.read_text(encoding='utf-8')))
            elif fn.suffix=='.jsonl':
                for line in fn.read_text(encoding='utf-8').splitlines():
                    if line.strip():scan(json.loads(line))
    for line in (base/'用题登记.jsonl').read_text(encoding='utf-8').splitlines():
        if line.strip():
            item=json.loads(line)
            if item.get('paper_id')!='M04':scan(item)
    return found
excluded=previous_source_ids()
assert len(rows)==15 and not (excluded&{r['source_id'] for r in rows})
assert all(len(r['options'])==4 and r['answer'] in r['options'] and r['analysis'] for r in rows)
assert all(r['source_question']==questions[r['source_id']] for r in rows)
(HERE/'verbal.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
blind=[{'number':r['number'],'stem':r['stem_override'],'options':r['options']} for r in rows]
(HERE/'verbal_blind.json').write_text(json.dumps(blind,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('M04言语15题已生成；14题有源键且一致，1题无源键；源对象逐题保全。')

#!/usr/bin/env python3
"""Apply the M02 review once, preserving sources, withdrawn rows and baseline audits."""
from pathlib import Path
import copy,hashlib,importlib.util,json,re,subprocess,sys
H=Path(__file__).resolve().parent;ROOT=H.parents[1];PROJECT=H.parent
REVIEW='b4b4d07ded2e7c2eb0e18523eef1d35252dc9048';VERSION='0.2.0'
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def jl(p):return [json.loads(s) for s in p.read_text(encoding='utf-8').splitlines() if s.strip()]
def save(p,x):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def canonical(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def ref(title,url,locator):return dict(title=title,url=url,locator=locator,checked_on='2026-11-15')
def imp(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
 cfg=load(H/'paper.json')
 if cfg['version']==VERSION:
  print('Revision already applied; selection preserved.');return
 assert cfg['version']=='0.1.0'
 rows=load(H/'selection.json');before=copy.deepcopy(rows);by={r['number']:r for r in rows}
 assert canonical(before)=='c1e1caf8ff62db5016b330277946dc8cb754879a85f843e035cf62ec21b3a6ef','Baseline changed: reconcile first'
 before_map={r['number']:r for r in before};core=imp('m02_original_core',H/'build_m02.py')
 banks={p:{q.get('id',q.get('question_id')):q for q in jl(ROOT/p)} for p in sorted({r['source_file'] for r in rows if r.get('source_file')})}
 bank_sha={p:sha(ROOT/p) for p in banks}
 history=H/'核验记录/历史_v0.1.0';history.mkdir(parents=True,exist_ok=True)
 for name in ['交付核验.json','source_answer_comparison.json','numeric_checks.json','layout_log.json','verify_delivery.py','check_numeric.py','politics_references.json']:
  p=H/'核验记录'/name
  if p.exists():(history/name).write_bytes(p.read_bytes())
 changes=[];retired=[]
 def note(n,reason,kind='review_revision'):
  by[n].setdefault('edits',[]).append({'type':kind,'description':reason,'revision':VERSION});changes.append({'number':n,'reason':reason,'type':kind})
 def stem(n,t):
  r=by[n];raw=r.get('stem_override',r.get('stem',(r.get('source_question') or {}).get('stem')))
  r['stem_override']=[{'type':'text','text':t}]+[b for b in core.clean_blocks(raw,'') if b['type']!='text']
 def options(n,d):by[n]['options']={k:[{'type':'text','text':v}] for k,v in d.items()}
 def addref(n,r):by[n].setdefault('provenance',{}).setdefault('references',[]).append(r)
 def replace(n,sid,answer,analysis,reason):
  old=by[n];sf=next(p for p,b in banks.items() if sid in b);q=copy.deepcopy(banks[sf][sid])
  retired.append({'number':n,'source_id':old['source_id'],'reason':reason,'old_record':copy.deepcopy(old),'status':'withdrawn_from_M02','user_done':'unknown','do_not_auto_reuse':True})
  r={k:copy.deepcopy(v) for k,v in old.items() if k in ['number','section','subsection','question_type']}
  r.update(source_bank='guokao_verbal' if sid.startswith('GK') else 'guangdong_mock',source_file=sf,source_id=sid,source_question=q,source_answer=q.get('answer'),answer=answer,analysis=analysis,selection_reason=reason,edits=[],verification={'status':'editor_replacement_pending_delta_review','method':'先按题面独立判断，再核对现存源答案（如有）；不沿用撤下题的外审状态。','source_answer_available':q.get('answer') is not None,'source_answer_agreement':q.get('answer')==answer if q.get('answer') else None,'checked_on':'2026-11-15'},source_locators={'original_number':q.get('number',q.get('original_number')),'source':q.get('source'),'pages':q.get('source_pages')})
  assert r['source_answer'] is None or r['source_answer']==answer
  rows[n-1]=r;by[n]=r;note(n,reason,'source_replacement')
 by[1]['provenance']['book_pages']=[6,9]
 by[1]['provenance']['references'][0]['locator']='公报“增强党性”段、“从严治吏”段；均已读取全文核实。讲义分别见第6、9页。'
 note(1,'核对讲义原页，将从严治吏定位由第10页更正为第9页；公报全文两项表述成立。','source_correction')
 stem(3,'“第二个结合”的前提是马克思主义与中华优秀传统文化互相成就，其结果是二者彼此契合。')
 by[3]['answer']='错误';by[3]['selection_reason']='区分结合之所以可能的基础与结合后产生的成果，不用极端否定词提示判断。'
 by[3]['analysis']='错误。题干把结合的前提和结果颠倒了：二者在价值追求等方面原本具有契合性，才有有机结合的基础；在结合过程中相互激活、促进，才实现互相成就。不能把结合带来的成果前置为结合发生的条件。依据为2023年6月2日文化传承发展座谈会讲话关于“两个结合”的论述。'
 note(3,'去掉极端否定的送分提示，改考前提与结果的关系；答案随题意调整，不为打乱对错顺序。')
 by[5]['options']['B']='党的各级组织承担全面从严治党的主体职责，组织建设须贯通不同层级与领域'
 by[5]['options']['C']='在党内监督中，党委（党组）履行监督责任，纪检监察机关履行主体责任'
 by[5]['analysis']='B正确，公报全文明确各级组织的主体地位及各层级、各领域组织建设要求。A把政治建设的统领地位换成组织建设；C将党委（党组）主体责任与纪检监察机关监督责任对调；D将党章的根本规范地位换成具体党内法规。公报引用经全文核实，无须因审核时未取得全文而改为另一文件。C中的区分是党内监督职责任务，不否认纪检机关作为党组织对本单位也承担全面从严治党主体责任。'
 addref(5,ref('《中国共产党纪律检查机关监督执纪工作规则》第十三条释义','https://www.ccdi.gov.cn/djfg/fgsy/202003/t20200326_214284.html','党委（党组）主体责任与纪检监察机关监督责任'))
 note(5,'保留已核实的公报依据；用两类监督责任对调替换“代替”的明显提示。')
 stem(6,'《广东省推动制造业与服务业协同融合发展2026年行动方案》提出，促进制造业服务化和服务业制造化。下列对有关举措的归类，正确的是（　）。')
 options(6,{'A':'装备制造企业面向用户提供设备全生命周期运维方案——服务业制造化','B':'工业设计企业委托工厂生产其自主设计的品牌产品——制造业服务化','C':'原材料生产企业由单纯供货转向提供产品及专业解决方案——制造业服务化','D':'电商企业利用用户数据推出自有品牌产品并委托制造——制造业服务化'})
 by[6]['analysis']='C正确。制造业服务化是在制造能力基础上向设计、运维、解决方案等服务延伸；服务业制造化是研发设计、电商等服务主体利用技术、数据或渠道优势向产品制造环节拓展。A也是制造业服务化，标签反了；B、D则是服务业制造化，并不要求服务企业必须自建工厂，委托制造同样可以完成这种拓展。四项均涉及制造与服务，必须判断主体及延伸方向，不能只找同时出现两个产业名称的一项。'
 by[6]['selection_reason']='四项均涉及制造与服务，须根据主体及延伸方向区分制造业服务化和服务业制造化。'
 by[6]['provenance']['references']=[ref('广东省推动制造业与服务业协同融合发展2026年行动方案','https://www.gzwxb.gov.cn/context/contextId/215610','第十项制造业服务化、第十一项服务业制造化；实际读取全文')]
 note(6,'接受弱干扰项问题，但不改成孤立背诵讲话原句；用双向延伸的概念归类检验理解。')
 stem(7,'某企业改造传统生产线时，保留仍具精度和稳定性优势的机械结构，淘汰落后的控制模块，并结合数字技术重新组织生产流程。对这种改造方式的理解，最符合辩证否定观的是（　）。')
 options(7,{'A':'发展主要体现为更新部分的增加，新技术的采用意味着原有技术已经失去合理性','B':'否定不是把新旧事物截然割裂，而是在克服局限时保留和发展合理因素','C':'肯定与否定相互联系，因而应按照相同的比例保留和替换原有技术','D':'旧事物中仍有积极因素，说明此次改造属于原有状态的延续，而不是发展环节'})
 by[7]['analysis']='B正确。辩证否定的实质是扬弃，即克服旧事物的局限，同时保留并发展其中有生命力的因素。题干不是简单给旧生产线加设备，也不是把旧结构清空后全部重建。A将新技术出现等同于旧技术全部失去合理性；C把辩证关系误写为数量上的平均分配；D因为存在继承便否认发展，割裂了发展与联系。改造的合理性取决于各部分实际作用，不取决于保留与淘汰的固定比例。'
 by[7]['selection_reason']='在生产改造情境中理解扬弃，不把继承与创新、保留与克服互相割裂。'
 by[7]['provenance']['book_pages']=[41]
 by[7]['provenance']['references']=[ref('学习运用否定之否定规律','https://www.jssjw.gov.cn/art/2024/4/23/art_435_28914.html','关于辩证否定既克服又保留、扬弃的说明；辅以用户讲义第41页')]
 note(7,'不再重复M01同题位的矛盾主次情境，改为扬弃的机制辨析；不强制全套政治题位重排。')
 by[8]['options']['D']=by[8]['options']['D'].replace('政府再分配','再分配')
 by[8]['analysis']=by[8]['analysis'].replace('D把经营收益分配错归政府再分配','D把经营收益分配错归再分配')
 note(8,'删去干扰项自带的“政府”提示，保留分配机制辨别。')
 for x in by[9]['provenance']['references']:
  if '二十大报告' in x['title']:x['locator']='第三部分“新时代新征程中国共产党的使命任务”：分两步走战略安排；非第十一部分。'
 note(9,'将两步走战略对应的报告章节更正为第三部分。','source_correction')
 by[11]['analysis']+=' 依《最高人民法院关于适用〈中华人民共和国民法典〉继承编的解释（一）》第三十一条，胎儿出生后死亡的，为其保留的遗产份额由其继承人继承；娩出时是死体的，则由原被继承人的继承人继承。'
 addref(11,ref('最高人民法院关于适用《中华人民共和国民法典》继承编的解释（一）','https://www.court.gov.cn/fabu/xiangqing/282091.html','第三十一条；已核对最高法全文'))
 note(11,'补齐活体出生后死亡时预留份额的继承后果。','analysis_revision')
 for x in by[12]['provenance']['references']:x['locator']='东隧西桥，深圳一侧出发向西跨珠江口、在中山登陆。仅用于稳定区位，不引用其早期距离数据。'
 note(12,'删除来源定位中的过时距离，不把同一省情主题视为用户一定做过本题。','source_correction')
 replace(25,'GKYY-2022-057','B','B对应文段完整机制：药物提高CMA关键成分的受体水平，恢复CMA效率，进而在小鼠中改善记忆表现。A把“显示治疗潜力”扩大为已经证实能够减缓疾病发展；C把CMA活性降低扩大为CMA过程被抑制发生；D把特定药物、特定模型下的结果概括成一般因果。应按文段区分作用机制、已观察结果和应用潜力，不把动物试验中的效果直接外推为临床疗效。','替换逆向下文推断为正向细节判断，训练机制、结果与证据边界；不因旧题有错而撤下。')
 replace(32,'gd-mock-2026h2-s17-q35','D','把每个四位数拆成前、后两个两位数并求和：10+15=25，18+16=34，22+21=43，19+33=52，结果依次增加9，所以下一组之和应为61。四个候选拆分之和分别为106、89、63、61，只有4615符合，选D。识别的对象是两个两位数，而不是四个数位分别运算；这一规律统一解释了全部已知项。','用多位数分组替代一条常规二级差数列，增加识别计数对象的变化，不为答案配平。')
 replace(61,'gd-mock-2026h2-s25-q61','A','题干把“勤劳则不匮乏”作为前提，以“匮乏”否定后件，推出“不勤劳”，形式为P→非Q，Q，所以非P。A同样是否定后件：牡丹→芬芳，非芬芳，所以非牡丹。B由退步反推没有前进，是肯定后件；C的前提只涉及边牧，结论却换成更宽的“牧羊犬”，未维持同一概念；D否定前件后直接否定后件，不成立。故A在概念范围不变的条件下复现了题干的逆否结构。本题只检验给定命题之间的关系，不把“勤劳与匮乏”的前提推广为现实社会中的无条件因果。','撤下B、D均可支持结论的争议题，换成结构相似题；按同一谓词、否定方向和论证形式独立核验。')
 q27=by[27].get('stem_override');assert isinstance(q27,str) and '对比。”从这些' in q27
 by[27]['stem_override']=q27.replace('对比。”从这些','对比。”\n从这些',1)
 note(27,'恢复最后一条留言与设问之间的换行，撤回原格式日志对此处的硬换行误判。','layout_correction')
 for n in [16,17,27]:
  by[n]['source_notice']='浙江2025年网友回忆版；本轮未取得可逐字核对的原卷，不将题库参考答案称为官方答案。'
  note(n,'在解析与来源登记中明确标注网友回忆版的证据边界。','source_correction')
 by[28]['analysis']+=' 本题按段落中心与选项适配作判断，不以某句话是否恰为原讲话引语替代文本分析。'
 note(28,'补明名句填空仍须依据全文重点，不以回忆原讲话代替判断。','analysis_revision')
 for n in [31,36]:
  q=by[n].get('source_question') or {};blocks=copy.deepcopy(by[n].get('stem_override',q.get('stem')))
  for b in blocks:
   if b.get('type')=='text':b['text']=b['text'].replace('-','−') if n==31 else b['text'].replace('ml','毫升')
  by[n]['stem_override']=blocks;note(n,'规范负号。' if n==31 else '将题干ml统一写为毫升，数值和单位含义不变。','layout_correction')
 by[38]['analysis']+=' 第二次相遇前不会发生追及：0—30分钟相向至首次相遇，30—55分钟仍向各自目标端点走；55—66分钟甲已从B折返，乙仍向A行进，虽同向但尚未追上；66分钟乙到A折返后，两人相向，90分钟再相遇。乙到A用时为66分钟，因为速度比为6∶5、甲走完全程需55分钟。'
 note(38,'补充各折返时刻，核对第二次相遇前不会先发生同向追及。','analysis_revision')
 raw=core.clean_blocks(by[44].get('stem_override',by[44]['source_question']['stem']),'')
 for b in raw:
  if b['type']=='text':b['text']=b['text'].replace('排名第七和第八月份','排名第七、第八的两个月份')
 by[44]['stem_override']=raw
 by[44]['analysis']='设九个月销售额按降序为b₁>b₂>…>b₉，最低值b₉=x，则b₁=3x，b₇+b₈=3x。为使给定x下总额尽量大，b₂至b₆分别不超过3x−2、3x−4、3x−6、3x−8、3x−10。因此总额≤3x+(15x−30)+3x+x=22x−30。由234≤22x−30得x≥12。取降序36、34、32、30、28、26、20、16、12，总和234，第七与第八为20、16，相加36，所有相邻差至少2，故12可达，选B。下界与可行方案共同证明最小值。'
 note(44,'使用与排名方向一致的降序记号，并补足题干月份表达；解法与答案不变。')
 by[47]['analysis']=by[47]['analysis'].replace('相同位置的两枚三角形相消','相同位置的三块三角形（包括黑色和白色块）相消')
 note(47,'实际放大查看原图第二行，修正共同消去的三角形块数为三块。','analysis_revision')
 by[51]['analysis']=by[51]['analysis'].replace('④把否定结论当成否定前件的依据','④否定前件后，直接推得必要条件不成立')
 by[51]['analysis']+=' 就F→(H且P)而言，④的错误形式是否定前件，并非逆否推理；非F时H且P仍可能成立。'
 note(51,'修正形式逻辑术语，保留用于排除错误命题的反例。','analysis_revision')
 by[53]['analysis']=by[53]['analysis'].replace('均支持这一结论','其中有方案满足A的可能性，而其余三个选项在全部合法方案中均不成立')
 note(53,'把可能项与必然项分开：A只需有可行方案，不表述为两方案都实现A。','analysis_revision')
 for n in [54,58,60,65]:
  r=by[n];sq=r['source_question'];blocks=core.clean_blocks(r.get('stem_override',sq['stem']),'');opts={k:core.clean_blocks(v,'') for k,v in r.get('options',sq['options']).items()}
  for b in blocks+sum(opts.values(),[]):
   if b['type']!='text':continue
   t=b['text']
   if n in [58,65]:t=t.replace('?','？')
   if n==60:t=re.sub(r'APP\s+','APP',t)
   if n==54 and t.endswith('。。'):t=t.rstrip('。')+'。'
   b['text']=t
  r['stem_override']=blocks;r['options']=opts;note(n,'统一问号、英文名称后空格或重复句末标点；不改命题含义。','layout_correction')
 note(56,'补全旧编辑说明：删去“由于表现较好”“正式”等背景措辞，将“将分到”整理为“分别入职”，并改写猜测引语为编号陈述；互不相同条件已在0.1.0明确，本轮不再改题面。','provenance_completion')
 for b in by[67]['stem_override']:
  if b['type']=='text':b['text']=b['text'].replace('P位于中间位置','P位于图示位置（不在两端）')
 by[67]['analysis']='初始S₂、S₃均断开，设变阻器左端至滑片电阻为a>0，滑片至右端为b>0，R₁=R₂=R。初始总电阻为a+R，滑片右移使a增大，电流变小，所以A错误。图中滑片引线与上方导线交叉点未画连接黑点，不能把相连作为唯一读法：若相连，闭合S₂后总电阻为a+R/2；若不相连，总电阻为a+R(R+b)/(2R+b)。两式都小于a+R，故B均正确。单独闭合S₃短接a，总电阻变为R；同时闭合两开关时，总电阻分别为R/2或R(R+b)/(2R+b)，均小于初始值，C、D正确。因此两种交点读法都唯一选A。各操作仍分别从相同初始状态开始。图示滑片并非精确中点，题干仅要求它不在端点。'
 note(67,'滑片改为图示非端点位置，并对交点相连、不相连两种接线分别给出推导；不靠未标黑点补接线。')
 opts=copy.deepcopy(by[69].get('options',by[69]['source_question']['options']));opts['B']=[{'type':'text','text':'在高温强光下，叶片面临较大的失水压力，植物可能出现暂时水分亏缺'}];by[69]['options']=opts
 by[69]['analysis']='正午外界高温强光可带来较大的失水压力，气孔缩小或关闭使实际蒸腾通量下降，这是环境压力与生理调节共同作用的结果，二者不矛盾。B表达的是可能的水分亏缺，不再断言测量时刻的实际失水速率必然增加。C把蒸腾下降归因于光合作用消耗大量水，未解释气孔调节且混淆主要失水途径，错误；A、D分别说明主要散失通道和调节作用。选C。'
 note(69,'把B项改为失水压力与水分亏缺，避免与测得正午蒸腾最低的事实形成字面冲突。')
 raw=copy.deepcopy(by[70].get('stem_override',by[70]['source_question']['stem']))
 for b in raw:
  if b['type']=='table' and b.get('notes')=='差值方向依题干：白昼时长减黑夜时长。':b.pop('notes')
 by[70]['stem_override']=raw;note(70,'移除重复的源库转写备注，题干仍保留昼长减夜长的定义。','layout_correction')
 stem(71,'根据资料，下列对2024年广东省有关外汇管理举措的理解，正确的是（　）。')
 options(71,{'A':'外贸企业名录登记取消行政许可后，改为在境内银行直接办理','B':'“科汇通”试点支持境内企业将科研开办资金直接汇往境外科研机构','C':'跨境贸易高水平开放重点加大大型国有企业和上市公司的推荐力度','D':'跨境资金池试点的3002亿美元，指相关企业已经实际收到的跨境资金'})
 by[71]['answer']='A';by[71]['selection_reason']='保留文字检索的独立训练价值，区分办理方式、资金方向、受益对象及额度与实流，不重复第74题的离岸基期计算。'
 by[71]['analysis']='A与材料一致：取消的是名录登记的行政许可，登记改由境内银行直接办理，不是登记本身取消。B把境外资金汇入广州外资非企业科研机构，改成境内企业资金汇往境外，方向与对象均不符。C把优质中小企业、“专精特新”企业换成另一类企业。D把集中外债、境外放款额度合计误当成已经发生的资金收付。该题须定位材料并核对政策行为及对象，无须重复计算离岸贸易的基期规模。'
 note(71,'接受恢复文字检索价值的建议，但重写实质干扰项，不原样恢复易凭“大规模降低关税”排除的旧题。','adapted_question_revision')
 by[75]['analysis']='D可推出：QFLP试点累计10家、QDLP累计5家，前者是后者2倍。B的103/1213约8.49%，不足10%；C将全省扩围误说为全国。A的“首次”没有足够历史资料支持。若将展示数值按精确数计算，上一年约为2.3/1.161=1.981万亿美元；但2.3只有一位小数，若按通常四舍五入处理，现期可能在[2.25,2.35)，以1.161为增长倍数得到上年约[1.938,2.024)万亿美元，连上年是否低于2万亿也不能确定。即便忽略这项精度问题，只知道上一年仍不足以判断更早年份，从而不能证明“首次”。'
 note(75,'补充展示精度带来的区间，避免把近似反推值写成已证实的历史事实。','analysis_revision')
 body=[];explanations=[];provenance=[]
 for r in rows:
  n=r['number'];old=before_map[n];changed=core.normalize(old)!=core.normalize(r)
  if changed:body.append(n)
  elif old['analysis']!=r['analysis']:explanations.append(n)
  elif old!=r:provenance.append(n)
  r['verification']['external_review']={'reviewer':'Claude','reviewed_version':'0.1.0','review_commit':REVIEW,'review_finding':'withdrawn_ambiguous' if n==61 else 'initial_disagreement_resolved' if n in [17,28] else 'baseline_answer_agreement','current_revision':VERSION,'delta_recheck':'pending' if changed or old['analysis']!=r['analysis'] else 'no_answer_or_question_change'}
  r['verification']['status']='editor_revised_pending_delta_review' if changed or old['analysis']!=r['analysis'] else 'claude_reviewed_baseline_retained'
 save(history/'selection_before_revision.json',before);save(H/'撤题记录.json',retired);save(H/'核验记录/审核处理变更.json',changes);save(H/'selection.json',rows)
 save(H/'核验记录/politics_references.json',{'version':VERSION,'by_question':{str(r['number']):r['provenance'] for r in rows if r['source_bank']=='editor_original'}})
 cfg.update(version=VERSION,status='editor_revised_after_claude_review',external_review='claude_reviewed_v0.1.0_revisions_pending_recheck',printing_status='not_started',display_status='Claude已审核0.1.0；本稿为意见处理后的0.2.0，新增与改动项待增量复核，尚非打印定稿。')
 cfg['review_baseline']={'version':'0.1.0','commit':REVIEW,'initial_answer_agreement':87,'initial_disagreements':[17,28,61],'resolved_after_review':[17,28],'withdrawn_ambiguous':[61]};cfg['revision_recheck_numbers']=sorted(set(body+explanations));save(H/'paper.json',cfg)
 logs=load(H/'核验记录/layout_log.json')
 for e in logs:
  if e.get('题号')==27:e.update(status='superseded',correction='v0.2.0恢复最后留言与设问间换行；旧硬换行合并判断错误。')
 save(H/'核验记录/layout_log.json',logs)
 p=H/'build_m02.py';s=p.read_text();needle='        out.append(b)\n    return out';assert s.count(needle)==1
 s=s.replace(needle,"        for key in ('caption','asset_id','source_asset_id','source_pages','source_spans'):\n            b.pop(key,None)\n"+needle,1)
 old="answer_lines.append('编辑处理：'+'；'.join(e.get('description', e.get('text', e.get('type',''))) if isinstance(e,dict) else str(e) for e in r['edits']))"
 new="answer_lines.append('编辑处理：'+'；'.join((e.get('description', e.get('text', e.get('type',''))) if isinstance(e,dict) else str(e)).rstrip('。；;') for e in r['edits'])+'。')"
 assert old in s;s=s.replace(old,new,1);needle="        if r.get('edits'):";assert s.count(needle)==1
 s=s.replace(needle,"        if r.get('source_notice'):\n            answer_lines.append('题源说明：'+r['source_notice'])\n"+needle,1)
 s=s.replace("'selection_reason':r['selection_reason'],'asset_paths':asset_paths(q),","'selection_reason':r['selection_reason'],'asset_paths':asset_paths(q),'source_notice':r.get('source_notice'),")
 p.write_text(s);subprocess.run([sys.executable,str(p)],check=True)
 matched=[dict(number=r['number'],source_id=r['source_id'],source_answer=r['source_answer'],editor_answer=r['answer'],match=r['source_answer']==r['answer']) for r in rows if r.get('source_answer')]
 assert len(matched)==27 and all(x['match'] for x in matched)
 save(H/'核验记录/source_answer_comparison.json',{'version':VERSION,'matched_count':27,'comparisons':matched,'limits':'参考答案比对不等于独立审题。旧版28题比对已归档，撤掉争议源题后为27。'})
 p=H/'核验记录/check_numeric.py';s=p.read_text()
 s=s.replace("put(32,{'first_differences':[6,11,17,24,32],'second_differences':[5,6,7,8],'answer_value':102})","pairs=[(x//100,x%100) for x in [1015,1816,2221,1933]]\nassert [a+b for a,b in pairs]==[25,34,43,52]\ncandidates=[2977,5831,3726,4615];totals=[x//100+x%100 for x in candidates]\nassert totals==[106,89,63,61]\nput(32,{'pairs':pairs,'sums':[a+b for a,b in pairs],'option_sums':totals,'answer_value':4615})")
 old="put(71,{'web_increment':inc_web,'offshore_increment':inc_off,'difference':inc_web-inc_off});assert abs(inc_web-inc_off-230.05347084)<1e-7";assert old in s
 s=s.replace(old,"put(71,{'kind':'text_retrieval','option_checks':{'A':'matches_bank_registration','B':'reverses_direction_and_subject','C':'changes_target_enterprises','D':'confuses_quota_and_flow'},'editor_answer':'A','limit':'人工语义核验，不伪称数值程序证明政策理解'})")
 s=s.replace("put(67,{'initial':'U/(Rp+R)','S2':'U/(Rp+R/2)','S3':'U/R','both':'2U/R','parameter_cases':8})","cases=0\nfor u,r,a,b in product([2,6],[1,4],[1,5],[2,7]):\n for joined in [False,True]:\n  parallel=F(r,2) if joined else F(r*(r+b),2*r+b)\n  initial=F(u,a+r)\n  assert F(u,a+r+1)<initial and F(u,1)/(a+parallel)>initial and F(u,r)>initial and F(u,1)/parallel>initial\n  cases+=1\nput(67,{'initial':'U/(a+R)','joined_parallel':'R/2','unjoined_parallel':'R(R+b)/(2R+b)','both_topologies_parameter_cases':cases,'false_option':'A'})")
 s=s.replace("report={'status':'PASS'","put(61,{'premise_form':'P -> not Q; Q','conclusion':'not P','matched_option':'A','option_B':'affirming_consequent','option_C':'predicate_scope_shift','option_D':'denying_antecedent','logic_check':all(not((not p or not q) and q) or not p for p,q in product([False,True],repeat=2))})\nreport={'version':'0.2.0','status':'PASS'",1)
 p.write_text(s);subprocess.run([sys.executable,str(p)],check=True)
 (H/'核验记录/verify_delivery.py').write_text(VALIDATOR,encoding='utf-8')
 save(H/'核验记录/修订基线.json',{'version':VERSION,'source_bank_sha256':bank_sha,'review_commit':REVIEW,'baseline_selection_sha256':canonical(before),'current_selection_sha256':canonical(rows),'body_changed_numbers':body,'analysis_only_numbers':explanations,'provenance_only_numbers':provenance,'expected_replacements':{str(x['number']):{'old':x['source_id'],'new':by[x['number']]['source_id']} for x in retired},'answer_changes':[{'number':r['number'],'old':before_map[r['number']]['answer'],'new':r['answer']} for r in rows if r['answer']!=before_map[r['number']]['answer']]})
 write_docs(changes);subprocess.run([sys.executable,str(H/'核验记录/verify_delivery.py')],check=True)

VALIDATOR=r'''from pathlib import Path
import json,hashlib,subprocess,sys,re
H=Path(__file__).resolve().parents[1];ROOT=H.parents[1];P=H.parent
load=lambda p:json.loads(p.read_text())
def jl(p):return [json.loads(s) for s in p.read_text().splitlines() if s.strip()]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def canon(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
r=load(H/'selection.json');q=jl(H/'题目.jsonl');b=load(H/'核验记录/修订基线.json')
assert len(r)==len(q)==90 and [x['number'] for x in r]==list(range(1,91))
assert canon(r)==b['current_selection_sha256']
assert len({x['source_id'] for x in r})==90
assert not {x['source_id'] for x in r}&{x['source_id'] for x in load(P/'M01/selection.json')}
for path,digest in b['source_bank_sha256'].items():assert sha(ROOT/path)==digest
for path in b['source_bank_sha256']:
 bank={x.get('id',x.get('question_id')):x for x in jl(ROOT/path)}
 for x in r:
  if x.get('source_file')==path:assert x['source_question']==bank[x['source_id']]
assert len(load(H/'撤题记录.json'))==3
ledger=jl(P/'用题登记.jsonl');mine=[x for x in ledger if x['paper_id']=='M02']
assert len(mine)==90 and {x['source_id'] for x in mine}=={x['source_id'] for x in r}
old=load(H/'核验记录/历史_v0.1.0/selection_before_revision.json')
assert all(r[i]['source_question']==old[i]['source_question'] for i in range(90) if i+1 not in [25,32,61])
assert all('answer' not in x for x in q)
leaks=[]
def walk(x):
 if isinstance(x,dict):
  for k,v in x.items():
   if k in ['caption','asset_id','source_asset_id','source_pages','source_spans']:leaks.append(k)
   walk(v)
 elif isinstance(x,list):
  for v in x:walk(v)
walk(q);assert not leaks
assert '\n从这些留言' in r[26]['stem_override']
assert '相同位置的三块三角形' in r[46]['analysis']
assert '第二次相遇' in r[37]['analysis'] and '66分钟' in r[37]['analysis']
assert '不在两端' in json.dumps(r[66]['stem_override'],ensure_ascii=False)
assert '实际收到' in json.dumps(r[70]['options'],ensure_ascii=False)
text=(H/'答案与解析_待审.md').read_text();assert '。；' not in text
count=len(re.findall(r'^\| (?:\d+ \| ?)+\n\| (?:--- \| ?)+\n\|',text,re.M));assert count==9
ref=load(H/'核验记录/source_answer_comparison.json');assert ref['matched_count']==27 and all(x['match'] for x in ref['comparisons'])
names=['selection.json','paper.json','题目.jsonl','题本_待审.md','答案与解析_待审.md','来源登记.jsonl','核验报告.json']
hashes=lambda:{n:sha(H/n) for n in names}
before=hashes();other=[x for x in ledger if x['paper_id']!='M02']
subprocess.run([sys.executable,str(H/'build_m02.py')],check=True)
assert hashes()==before and [x for x in jl(P/'用题登记.jsonl') if x['paper_id']!='M02']==other
cfg=load(H/'paper.json');assert cfg['version']=='0.2.0'
report={'status':'PASS','version':'0.2.0','question_count':90,'source_replacements':[25,32,61],'preserved_other_source_records':87,'reference_answers_matched':27,'M01_id_collisions':[],'other_papers_ledger_preserved_on_rebuild':True,'answer_table_blocks':count,'student_metadata_leaks':leaks,'rebuild_identical':True,'body_changed_numbers':b['body_changed_numbers'],'analysis_only_numbers':b['analysis_only_numbers'],'answer_changes':b['answer_changes'],'output_sha256':before,'external_review':cfg['external_review'],'print_ready':False,'limits':['本次新增与修改项尚待Claude增量复核。','语义判断由编辑逐项论证；程序通过不证明语言或政策命题正确。','原PDF与原图完整复核边界仍保留；未重绘、未制作打印定稿。']}
(H/'核验记录/交付核验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['status','question_count','source_replacements','reference_answers_matched','rebuild_identical']},ensure_ascii=False))
'''

def write_docs(changes):
 lines=['# M02｜GPT对Claude审核意见的处理','内容版本0.2.0；审核基线为0.1.0，Claude提交`'+REVIEW+'`，原意见不改写。','## 本轮实质处理','争议第61题撤下，改为逻辑结构题；第25题改为正向细节判断；第32题改为多位数分组。旧记录完整归档，已曝光与是否做过分开，不自动投入后续套卷。第71题恢复文字检索功能，但重写实质干扰项，不照搬原来容易排除的关税项。','第3题区分结合的前提和结果；第6题辨析制造业服务化与服务业制造化；第7题转为扬弃的机制。不是单纯挪题位、配答案字母或背一句原话。','## 逐项记录','|题号|处理|','|---|---|']
 lines.extend(f'|{x["number"]}|{x["reason"]}|' for x in changes)
 lines.extend(['','## 保留与暂不采纳','第17、28题保留答案。17按第二空排除“不绝如缕”；28依全文中心，不靠记忆原讲话。浙江回忆版来源明确标注。','第1、5题的公报依据已实际读取全文，主体地位表述确实存在，不因审核时拿不到全文就改换文件。第1题讲义页码改为6、9；第9题两步走战略出处改为二十大报告第三部分。','不设某个字母不超过30%、不许连续四个同字母等硬指标，不为配平打乱升序选项。每卷结构题2—3道、单源最多3道等建议保留为检查方向，不变成机械配额。','题源集中、主题轮换在后续选编时关注；不据来源推断用户已做，不把本卷全面推倒重选。第12题只删旧定位中的距离，第15题保留制度理解价值。第41、43、49不作低收益措辞替换；第68保留不分解边界；科推不为混合设问方向而翻转问题。','## 核验和打印边界','当前27题有源参考答案且吻合，旧28题比对与原记录归档；新题不继承被撤题的外审结论。第27题设问分段已恢复，旧格式日志误判明确撤回。考生JSON去掉图注原题号、页码和转写来源元数据，解析与来源登记仍可溯源。','原始源对象和现有13幅题图未改。第49题矢量重绘、第50题放大仍交Claude按既定流程处理，本轮未生成M02打印定稿。程序通过不等于新增题已经完成独立审题。','本轮保留Claude分支已有的M01排版成果和通用排版工具，不改其内容，也不将其记为本轮重新核验成果。'])
 (H/'GPT审核意见处理.md').write_text('\n\n'.join(lines[:6])+'\n\n'+'\n'.join(lines[6:8+len(changes)])+'\n\n'+'\n\n'.join(lines[8+len(changes):])+'\n')
 (H/'交接_Claude_修订复核.md').write_text('# M02 0.2.0｜增量复核交接\n\n先读GPT审核意见处理.md。重点盲解新第25、32、61题及改写后的第3、5、6、7、8、69、71题；第27题只恢复设问分段。\n\n再核对第38题相遇时序（乙66分钟到A，90分钟再相遇）、44降序界限、47三块消去、51否定前件、53可能性、第67题两种交点接线公式、第75题近似数据范围。\n\n公报全文已核到各级组织主体地位，无须假设只在决定出现。第6题用2026行动方案第十、十一项的两类延伸，第11题补充继承司法解释第三十一条。\n\n撤下三题的记录单独保留，不再把它们的旧答案比对当当前成果。程序检查不等于模型独立审核。打印前仍需完成49题重绘、50题放大并查看新版分页；本轮未制作M02打印定稿。通用工具和M01成果沿用你的分支，未覆盖。\n')
 (H/'README.md').write_text('''# M02｜0.2.0审核意见处理稿

当前90题齐全。Claude已审核0.1.0；本版处理了争议题、训练类型缺口和明确的题面/解析问题。**新增与改动项待增量复核，尚非打印定稿。**

|入口|用途|
|---|---|
|[当前题本](题本_待审.md)|完整90题，答案与来源后置|
|[答案与解析](答案与解析_待审.md)|按当前题面重建|
|[Claude原意见](Claude审核意见.md)|0.1.0审核原文|
|[GPT处理说明](GPT审核意见处理.md)|采纳、改造采纳、暂不采纳及理由|
|[增量复核交接](交接_Claude_修订复核.md)|新题、改动重点与打印待办|
|[当前核验](核验记录/交付核验.json)|90题、27题源答案比对、源库保全、重建一致性|
|[撤题记录](撤题记录.json)|三道被替换题完整历史，不自动投入后续卷|

selection.json为当前唯一整卷底稿。两个旧断点、编辑底稿目录、assemble_m02.py是0.1.0生成资料，不能覆盖修订后的选择。

```bash
python3 广东行测18套模拟/M02/build_m02.py
python3 广东行测18套模拟/M02/核验记录/check_numeric.py
python3 广东行测18套模拟/M02/核验记录/verify_delivery.py
```

最后一个检查器针对本次固定修订快照；后续修订要更新版本与修订基线，不能只改校验值掩盖差异。旧报告位于核验记录/历史_v0.1.0/，不会冒称对当前新题生效。

原图未变，原PDF全面逐页复核未完成。资料按题给数据理解，题源年份或已上传不代表用户已做。打印沿用Claude更新的工具，49重绘、50放大仍待完成。
''')
 for path,link in [(PROJECT/'README.md','M02/README.md'),(ROOT/'README.md','广东行测18套模拟/M02/README.md')]:
  if path.exists():
   text=path.read_text();heading='## M02最新状态：0.2.0审核意见处理稿\n\n[当前入口]('+link+')：已处理Claude意见，新增与改动项待增量复核，打印待重绘与排版。以下早期状态保留作历史，发生冲突时以M02当前入口和paper.json为准。\n\n'
   if heading not in text:path.write_text(heading+text)
if __name__=='__main__':main()

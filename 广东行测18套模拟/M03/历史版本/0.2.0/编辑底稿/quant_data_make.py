from __future__ import annotations
import copy,json,re,hashlib,subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SOURCE='模考/2026下半年广东卷_16-33季_AI可读/全部题目.jsonl'
BANK={q['id']:q for q in map(json.loads,(ROOT/SOURCE).read_text().splitlines())}
ROWS=[]
def textblock(t):return [{'type':'text','text':t}]
def add(number,season,snum,answer,analysis,reason,subtype='',stem=None,options=None,edits=None,material=None):
 q=copy.deepcopy(BANK[f'gd-mock-2026h2-s{season}-q{snum}'])
 r={'number':number,'section':'数量关系' if number<46 else '资料分析','subsection':subtype,'question_type':'single_choice','source_bank':'guangdong_mock','source_file':SOURCE,'source_id':q['id'],'source_question':q,'source_answer':None,'answer':answer,'analysis':analysis,'selection_reason':reason,'edits':edits or [],'verification':{'status':'editor_solved_pending_independent_review','method':'编辑独立推导；源库未提供答案。整数与概率题另用穷举/精确分数核对，资料各项计算见quant_data_check.py；图形选项已实际查看。程序核验不替代Claude独立审核。','source_answer_available':False,'source_answer_agreement':None,'checked_on':'2026-11-15'},'source_locators':{'original_number':q['number'],'pages':q['source_pages'],'source':q['source']}}
 if stem is not None:r['stem_override']=textblock(stem) if isinstance(stem,str) else stem
 if options is not None:r['options']={k:textblock(v) if isinstance(v,str) else v for k,v in options.items()}
 if material is not None:r['materials']=[copy.deepcopy(material)]
 # Correct corpus serialization of TeX commands, without changing values or mathematical meaning.
 def fix(v):
  if isinstance(v,str):return v.replace('\\\\','\\')
  if isinstance(v,list):return [fix(x) for x in v]
  if isinstance(v,dict):return {k:fix(x) for k,x in v.items()}
  return v
 effective_stem=r.get('stem_override',q['stem']);effective_options=r.get('options',q['options'])
 if fix(effective_stem)!=effective_stem or fix(effective_options)!=effective_options:
  r['stem_override']=fix(effective_stem);r['options']=fix(effective_options)
  r['edits'].append({'type':'math_serialization_correction','description':'将源库数学命令中的双反斜杠改为单反斜杠，恢复标准TeX显示；不改变数值或符号含义。'})
 ROWS.append(r);return r

def edit(kind,description):return {'type':kind,'description':description}

add(31,19,31,'A',
 '每三个数为一组，前两个数的平方和等于第三个数的平方：3²+2²=13，8²+6²=100。因此第三组满足10²+3²=109，缺项为√109，选A。这里先确定三项为一个整体，再找组内关系。',
 '根号与九项长度提示分组，训练先识别计数/观察单位。','数字推理')
add(32,29,35,'A',
 '将奇数位与偶数位分别观察。奇数位为28、30、36、54、（　），相邻差为2、6、18，依次乘3，下一差为54，故缺项为108。偶数位17、29、46、75满足前两项相加得后一项，作为隔项分组的交叉验证，选A。',
 '同一数列内两条规律并行，避免把相邻数强行拟合成单链。','数字推理')
add(33,27,34,'D',
 '依次把分母写成1、3、9、27、81，即3/1、7/3、15/9、27/27、43/81。分子3、7、15、27、43的相邻差是4、8、12、16，下一差为20，故下一项是63/243=7/27，选D。应统一比较层次，不能只盯着约分后的表面分子。',
 '约分隐藏了统一分母结构，检验把分数恢复到同一生成方式。','数字推理')
add(34,25,34,'A',
 '相邻差为29、18、11、7、4。从第三个差开始，每个差等于前两个差之差：29−18=11，18−11=7，11−7=4，所以下一个差为7−4=3。缺项为81+3=84，选A。',
 '差数列内部的递推关系，不只是再求一次等差。','数字推理')

# Exact, code-drawn numerical diagram reconstructed from the source table.
vals=[['25','3','7','−4'],['14','8','6','34'],['51','9','4','−15'],['22','8','7','？']]
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="720" height="180" viewBox="0 0 720 180"><rect width="720" height="180" fill="white"/>']
scale=3
im=Image.new('RGB',(720*scale,180*scale),'white');draw=ImageDraw.Draw(im)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',28*scale)
for j,vs in enumerate(vals):
 cx=90+j*180;cy=90;r=70
 svg.append(f'<g fill="none" stroke="black" stroke-width="1.8"><circle cx="{cx}" cy="{cy}" r="{r}"/><path d="M {cx-r} {cy} H {cx+r} M {cx} {cy-r} V {cy+r}"/></g>')
 draw.ellipse(((cx-r)*scale,(cy-r)*scale,(cx+r)*scale,(cy+r)*scale),outline='black',width=5)
 draw.line(((cx-r)*scale,cy*scale,(cx+r)*scale,cy*scale),fill='black',width=5)
 draw.line((cx*scale,(cy-r)*scale,cx*scale,(cy+r)*scale),fill='black',width=5)
 for v,dx,dy in zip(vs,[-29,29,-29,29],[-28,-28,28,28]):
  shown='?' if v=='？' else v
  svg.append(f'<text x="{cx+dx}" y="{cy+dy}" text-anchor="middle" dominant-baseline="central" font-family="DejaVu Serif,serif" font-size="28">{shown}</text>')
  draw.text(((cx+dx)*scale,(cy+dy)*scale),shown,font=font,fill='black',anchor='mm')
svg.append('</svg>')
(HERE/'quant_data_number_grid.svg').write_text(''.join(svg))
im.save(HERE/'quant_data_number_grid.png')
figure_rel='../../广东行测18套模拟/M03/编辑底稿/quant_data_number_grid.png'
add(35,19,35,'B',
 '每个圆中，右上数×左下数−左上数=右下数：3×7−25=−4，8×6−14=34，9×4−51=−15。因此第四个圆的问号为8×7−22=34，选B。四个圆使用同一位置关系。',
 '用位置固定的数阵关系，补充线性数列之外的观察方式。','数字推理',
 stem=[{'type':'text','text':'观察下列各圆内数字的关系，问号处应填入的数是：'},{'type':'figure','path':figure_rel,'width_px':2160,'height_px':540}],
 edits=[edit('diagram_reconstruction','源库以四行位置表转写原圆形数阵，原题图文件未保留。本题依转写表的左上、右上、左下、右下顺序绘制清晰数阵；数字和方位均不改，未冒称与原PDF逐像素一致。')])
add(36,30,37,'B',
 '设总盒数为T。黑色占总数3/7，蓝色占3/8，故红色占1−3/7−3/8=11/56。各色盒数均为整数，T应为56的倍数，因此红色盒数为11的倍数。30多盒中只有33符合，T=33×56/11=168，选B。注意“其他颜色”作分母，不是总数。',
 '把部分与其余的比转换为部分占总数，再用整数约束锁定。','数学运算')
add(37,32,37,'C',
 '设公司人数为100a+10b+c。交换百、十位少270，得90(a−b)=270，即a−b=3；交换百、个位少594，得99(a−c)=594，即a−c=6。人数不足700且c≥0，只能a=6、b=3、c=0，总人数630。设大巴x辆、小巴y辆，则50x+40y=630，即5x+4y=63，故x≡3（mod 4）。最小非负可行x为3，此时y=12，选C。',
 '位值关系与整数分配串联，边界和同余都须保留。','数学运算')
add(38,27,42,'D',
 '售价上涨20%使单件利润增加30元，故原售价为30/20%=150元。进价120元，原、新单件利润分别为30、60元。总利润变为原来的80%，故销量变为0.8×30/60=0.4倍；新售价为1.2倍，总收入变为1.2×0.4=0.48倍，即减少52%，选D。不能把总利润降幅直接当作销售收入降幅。',
 '同一变动同时作用于单价、单件利润、销量、总收入，考查指标转换。','数学运算')
add(39,25,42,'D',
 '设第一次风速为w，往返路程相等，逆风与顺风用时之比等于顺风与逆风速度之比，(36+w)/(36−w)=2，得w=12米/分。第二次风速18米/分，顺、逆风速度分别为54、18米/分。设风场长度L，L/54+L/18=4，解得L=54米，选D。',
 '先由时间比恢复速度比，再求第二次往返的调和平均；题型自然变化。','数学运算')
add(40,19,40,'B',
 '圆锥底面朝上，露出部分是上方的圆台，留在水下的是与原圆锥相似的小圆锥。要露出至少37/64，水下体积至多为27/64；相似体积比等于高度比的立方，因此水下高度至多为7×∛(27/64)=7×3/4=5.25米。原水面恰好淹没整个圆锥，至少下降7−5.25=1.75米，选B。不能把37/64直接当作高度比例。',
 '底面朝上决定应对水下小圆锥取补集，检验几何对象选择。','数学运算')
add(41,22,40,'A',
 '总工程量设为1，甲效率为1/20。甲先做5天完成1/4；计划提前5天，即计划共15天，甲乙随后合作10天完成3/4，因此甲乙合效率3/40，乙效率1/40。实际工程做到2/5时，甲乙合作的时间为(2/5−1/4)/(3/40)=2天，此时从开工起共7天。实际总用时17天，甲丙再合作10天完成3/5，合效率3/50，丙效率3/50−1/20=1/100。故乙∶丙=(1/40)∶(1/100)=5∶2，选A。',
 '计划与实际两条时间线相互约束，关键是换队时刻而非机械套公式。','数学运算')
add(42,27,39,'B',
 '老张的周期为12天，1月1日是第1个工作日。若是平年，3月30日为第89天，在周期中是第5个工作日；若是闰年，则为第90天，恰为第6个工作日，故这一年是闰年。老陈从1月2日开始，至3月30日是其排班第89天。89=9×9+8，在“上8天休1天”的周期中是第8个工作日，即休息前上班的最后一天，选B。锚定开始日为第1天，避免间隔与天数混用。',
 '从周期位置反推闰年，再换另一个起点计数；覆盖锚点与边界。','数学运算',
 stem='某物业公司的保安可选择的排班方案有两种：①上10天休2天；②上8天休1天。老张选择方案①，从1月1日开始第1天上班，3月30日是他休息后上班的第6天。若老陈选择方案②并从1月2日开始第1天上班，那么3月30日这天他处于：',
 edits=[edit('layout_correction','合并源库“方案”与“①”之间的抽取换行，不改变排班和日期。')])
add(43,19,41,'D',
 '最终恰好3人合格，只可能有两类互斥情形。①首次恰好3人合格，剩下1人补考不合格：C(4,3)×0.8³×0.2×0.6=0.24576。②首次恰好2人合格，剩下2人补考恰好1人合格：C(4,2)×0.8²×0.2²×C(2,1)×0.4×0.6=0.073728。首次少于2人会取消补考，不可能最终达到3人；首次4人合格也不符合。两类相加为0.319488，约0.32，选D。',
 '补考启动门槛与最终恰好人数共同作用，按最终事件反推首次结果。','数学运算',
 stem='某公司招聘时，4名应届毕业生同时参加笔试。每人首次笔试合格的概率均为0.8，且未合格者有一次补考机会，补考合格的概率均为0.4。各人的考试结果相互独立，补考结果也与首次考试结果独立。若首次笔试合格人数不足参加笔试总人数的一半，则取消补考。恰好有3名应届毕业生最终笔试合格的概率约为：',
 edits=[edit('condition_clarification','明确不同考生及首次/补考结果的独立性，并在设问中加入“最终”，使概率模型由题面完整给出；概率、补考门槛与选项不变。')])
add(44,23,43,'D',
 '设只学过舞蹈的有x人，则两者都学过的为1.7x人；只学过乐器的比两者都学过的少3人，为1.7x−3人。加上两者都未学过的6人，全班共4.4x+3人。因x和1.7x均为整数，x是10的倍数；人数为40多，只有x=10可行。于是三块人数分别为10、17、14，加6共47人，选D。直接按互不重叠的四块计数即可，不必先写冗长容斥式。',
 '百分比的比较对象嵌在集合内部，要先把交叠区和独有区分清。','数学运算')
add(45,31,45,'B',
 '一个最终方案由三家产业园各自收到哪些人决定。先确定甲园的3人，有C(7,3)=35种；余下4人中，乙园至少2人且丙园至少1人，因此乙园只可能收2人或3人，分别有C(4,2)=6种、C(4,3)=4种。共35×(6+4)=350种，选B。产业园有名称，无须除以分组顺序；也不能把同一组人员的内部排列重复计入。',
 '以最终人员分组为计数对象，辨别有标号容器和至少人数约束。','数学运算')

# Four intact materials; paragraph breaks restore readable subject grouping only.
def material(season,number):return copy.deepcopy(BANK[f'gd-mock-2026h2-s{season}-q{number}']['material'])
m1=material(19,71)
t=m1['blocks'][0]['text']
for marker in ['超高清视频产业规模领先的势头在今年得以延续。','超高清视频产业龙头企业增势强劲，','截止到目前（2026年4月29日），','根据规划，']:
 t=t.replace(marker,'\n\n'+marker)
m1['blocks'][0]['text']=t
m1edit=edit('material_paragraphs','按产业总规模、当期产出、龙头企业、存量能力和规划五个语义段落分段；文字、数据与顺序保持不变。')
add(71,19,71,'A',
 '材料末段直接列出四大板块：产品端促销、产业链对接、内容制播、AI赋能，只有A与其完整对应。其余选项把产品研发、招商、渠道等相关词替换进来，行业相关不等于材料列举的四大板块。',
 '保留广东资料中的文字检索；训练定位并逐项比对名词范围。',material=m1,edits=[m1edit])
add(72,19,72,'C',
 '材料只说“符合国标的4K节目量超2.3万小时”，没有提供8K节目量，更没有8K的全国排名，因此C不能推出。A对应“全国唯一”的试验区，B对应2025年规模10803亿元、成为第十个万亿级集群，D对应国家级制造业创新中心及总投资超4000亿元的一批重大项目，均有原文依据。',
 '区分材料支持与背景想当然，核对4K/8K及全国排名等边界。',
 stem='根据材料，关于广东省超高清视频产业，下列说法不能推出的是：',material=m1,
 edits=[m1edit,edit('question_clarification','将“错误的是”改为“不能推出的是”：未给8K节目数量和排名只能判为材料不支持，不能仅凭缺信息断言现实事实为假。选项和检索对象不变。')])
add(73,19,73,'D',
 '广东面板月产能105万片，占全国25%，全国月产能为105÷25%=420万片。题设各月产能不变且满负荷生产，全年产量为420×12=5040万片，选D。1260只将广东月产能乘12，遗漏全国与广东的范围转换。',
 '连续完成地区范围和月度/年度两个转换，同时补足产能转换产量的必要条件。',
 stem='假设2026年全国各月面板产能均保持材料所述目前水平，且各月均按该产能满负荷生产，则2026年全国面板产量为多少万片？',material=m1,
 edits=[m1edit,edit('condition_clarification','源题只规定月产能不变却直接求实际产量。本题明确全年各月保持该水平且满负荷生产，使5040万片成为由题面可推出的产量；不改数据或选项。')])
add(74,19,74,'D',
 '设2024年一季度手机产量为1，则2026年一季度为1.044；又因2026年比2025年增长9.4%，2025年为1.044/1.094。因此2025年同比增速为1.044/1.094−1=−5/109.4≈−4.57%，是下降不到5%，选D。两年合计增长4.4%不能与下一年9.4%直接相减当作精确结果。',
 '由两年累计增长和后一年的增长反推前一年，守住比较基期。',material=m1,edits=[m1edit])
add(75,19,75,'B',
 '逐项核对。A：107.9%−22.4%=85.5个百分点，不是75.5。B：电视用户总量约2905/89%=3264万户，超过3000万户，能推出。C：60.3%和44.7%的分母分别是全国彩电产量与全国手机产量，不能跨分母比较广东两种产量。D：“较2017年增长2.5倍”表示2025年为2017年的3.5倍，增量约10803×2.5/3.5=7716亿元，超过7500亿元。因此选B。',
 '综合识别百分点、部分反推总体、不同分母、增长几倍四类边界。',material=m1,edits=[m1edit])

m2=material(17,81)
add(76,17,81,'C',
 '按注释，亏损面是亏损企业数占全部企业数的比重。2022年为4469/17517≈25.51%，2016年为1584/14133≈11.21%，两者相差约14.30个百分点，故为扩大14.3个百分点，选C。比较的是两个比重之差，不是亏损企业数的增长率。',
 '表内双分母计算与百分点方向判断。',material=m2)
add(77,17,82,'B',
 '各指标跨度均为2013—2023年，共10个增长间隔。比较年均增长率只需比较2023/2013的倍数：利润约0.996，亏损总额约6.524，亏损企业数约3.154，企业数约1.595。因此亏损总额年均增长最快，选B，无须逐项开十次方。',
 '同跨度年均增长排序化为终期/基期比，减少不必要的开方计算。',material=m2)
add(78,17,83,'B',
 '主营业务利润率=主营业务利润/主营业务收入，利润同比增速高于收入同比增速时，利润率上升。逐年比较2013—2018年两列增速：2013年25.6%>19.8%，2014年17.3%>10.1%，其后四年均不满足。因此有2年，选B。2013年虽然未列2012年总额，但已给同比增速，仍可判断。',
 '用分子分母增速判平均数方向，并注意首年也可由给定同比判断。',material=m2)
add(79,17,84,'D',
 '2022年平均每家亏损企业亏损额为1223.9/4469亿元，2021年为1020.4/3581亿元。相减约−0.0110839亿元；1亿元=10000万元，故约减少110.84万元，即减少111万元，选D。分母应使用亏损企业数，不能使用全部企业数。',
 '双平均数作差、条件分母与亿元/万元转换叠加。',material=m2)
add(80,17,85,'C',
 '①“十三五”为2016—2020年，亏损总额最大为2020年的1088.9亿元，最小为2016年的311.5亿元，1088.9>3×311.5，成立。②2013年利润同比增量=5107.7×25.6%/125.6%≈1041.1亿元，超过1000亿元，成立。③1412.4−1223.9=188.5亿元是2023年全年的亏损额同比增量，材料不能据此推出12月当月增量，不能推出。共2项，选C。',
 '综合检验规划期边界、增长量和全年/单月统计口径。',
 stem='根据上述材料，下列说法可以推出的有几项？\n①“十三五”期间，我国汽车制造业亏损总额最多的年份，其亏损总额超过亏损总额最少年份的3倍\n②2013年，我国汽车制造业主营业务利润总额同比增加超过1000亿元\n③2023年12月，我国汽车制造业当月亏损额同比增加约188.5亿元',material=m2,
 edits=[edit('question_clarification','将“说法正确的有几项”明确为“说法可以推出的有几项”，使第③项按材料缺少月度数据判定，而不把未知月度事实当作已证伪。各判断内容不变。')])

m3=material(22,71)
m3['blocks'][0]['notes']='表中各月数值均为当年年初至该月的累计值；2023年1—2月为两个月合计。'
m3edit=edit('material_clarification','补明累计口径随自然年重新起算，1—2月为合计；这是原表标题及数值的既有含义，不改数值。')
add(81,22,71,'A',
 '2022年下半年=2022年全年−2022年上半年。2022年全年累计22247万台；由2023年6月累计14060万台、同比增长16.6%，反推2022年上半年为14060/1.166≈12058.32万台。相减约10188.68万台，即10189万台，选A。C项约12058是上半年，而不是下半年。',
 '从次年累计同比反推缺失上半年，再与全年相减。',material=m3,edits=[m3edit])
add(82,22,72,'D',
 '表中数值是累计量。2022年9月当月产量=17492−15722=1770万台，10月当月产量=18960−17492=1468万台。10月环比增速=(1468−1770)/1770≈−17.06%，约下降17%，选D。直接用18960与17492作比，会算成累计量之比。',
 '先还原两个月当月量，再计算环比，不被累计表的列名牵走。',material=m3,edits=[m3edit])
add(83,22,73,'D',
 '2023年6月当月产量=14060−11425=2635万台。2022年1—6月约为14060/1.166=12058.32万台，1—5月约为11425/1.142=10004.38万台，故2022年6月约2053.94万台。6月当月同比增速≈2635/2053.94−1=28.29%，选D。16.6%是1—6月累计增速，不能直接用于6月当月。',
 '两组现期累计量与两组同比需要分别还原，考查累计转单月的完整链条。',material=m3,edits=[m3edit])
add(84,22,74,'B',
 '出口单价=出口金额/出口数量。2023年7月金额同比下降15.4%、数量增长1.3%，因此单价同比增速=(1−15.4%)/(1+1.3%)−1=−16.7%/1.013≈−16.49%，即下降16.5%，选B。金额与数量一降一升，单价降幅应大于金额降幅。',
 '平均数增长率，先用方向和幅度关系作合理性检查。',material=m3,edits=[m3edit])
add(85,22,75,'A',
 '先将累计量还原为当月量：9月1770、10月1468、11月1489、12月1798万台。10—12月的“环比增量”依次是−302、21、309万台，逐月增加，所以折线应持续向上，选A。这里画的是增量，不是产量本身；原选项未给零线，只判断三点的先后高低。',
 '从累计量到当月量再到环比增量，两次作差后识别图形趋势。',material=m3,edits=[m3edit])

m4=material(25,76)
add(86,25,76,'D',
 '“其他能源”生产量四个同比增速依次约为：(75490−68953)/68953=9.48%，(80237−75490)/75490=6.29%，(87985−80237)/80237=9.66%，(92872−87985)/87985=5.55%。最慢为2022年，选D。2020年的增量虽略小于2022年，但基数也更小，不能只比增量。',
 '相近增量下比较增长率，避免只看差值。',material=m4)
add(87,25,77,'D',
 '使用消费表。2021年原煤消费增量=293976−283541=10435万吨标准煤，原油消费增量=97817−93683=4134万吨标准煤，倍数为10435/4134≈2.52，最接近2.5，选D。不能混用生产表，也不能拿两个现期量直接相除。',
 '生产与消费两表同名指标并列，训练守住表和统计口径。',material=m4)
add(88,25,78,'B',
 '2022年消费量中，原煤304042/540956≈56.20%，原油96839/540956≈17.90%，天然气45444/540956≈8.40%，其他能源94631/540956≈17.49%。应表现为灰色略过一半、白色不到一成、黑白格与黑色均接近18%且黑白格略大，只有B符合。A、C灰色约七成；D白色与黑色比例也不符合，选B。',
 '把数表转换为组成关系，比较大小、近似相等和扇区量级。',material=m4)
add(89,25,79,'C',
 '2018—2022年共5个年份，天然气生产量总和为20458+22250+24438+25627+27494=120267万吨标准煤，年均为120267/5=24053.4万吨标准煤，处于24000—25000之间，选C。平均量用5年作除数；若求年均增长率才对应4个增长间隔。',
 '年均量与年均增长的期数区别；数值靠近区间边界，粗估须留足精度。',material=m4)
add(90,25,80,'C',
 'A：2018—2022年原煤消费量减生产量依次为16266、9119、8617、9090、−10042万吨标准煤；按两量相差的绝对值，超过10000的有2018、2022两年，不是1年。B：2022年原油消费96839低于2021年97817，天然气45444也低于46279，不成立。C：2021年三者消费量之和=293976+97817+46279=438072，占525896的约83.30%，超过80%，成立。D：2022年总消费量较2020年增长(540956−498314)/498314≈8.56%，不到10%。故选C。',
 '综合检验差值绝对方向、跨年下降、结构比重和隔年增长。',material=m4)

# Provenance and old-exposure search. A corpus upload is not proof of prior practice.
used=set();withdrawn=set()
for name in ['M01','M02']:
 used|={r['source_id'] for r in json.loads((ROOT/'广东行测18套模拟'/name/'selection.json').read_text())}
 w=ROOT/'广东行测18套模拟'/name/'撤题记录.json'
 if w.exists():withdrawn.update(re.findall(r'gd-mock-2026h2-s\d+-q\d+',w.read_text()))
assert not (used|withdrawn)&{r['source_id'] for r in ROWS}
old_dirs=[ROOT/'广东行测24天集训',ROOT/'习题本',ROOT/'答案解析']
old_files=[p for d in old_dirs if d.exists() for p in d.rglob('*') if p.is_file() and p.suffix in {'.md','.txt','.json','.jsonl','.csv'}]
def normalize(s):return re.sub(r'[^0-9A-Za-z\u4e00-\u9fff]+','',s)
old_contents=[(str(p.relative_to(ROOT)),normalize(p.read_text(errors='replace'))) for p in old_files]
exposure=[]
for r in ROWS:
 q=r['source_question'];stem=''.join(b.get('text','') for b in q['stem'])
 # Only long, distinctive stems; generic data question stems are supplemented by complete material openings.
 distinctive=normalize(stem)
 patterns=[]
 if len(distinctive)>=28 and len(re.findall('[\u4e00-\u9fff]',stem))>=18:patterns.append(distinctive[:45])
 if q.get('material'):
  mt=''.join(b.get('text',b.get('title','')) for b in q['material']['blocks']);patterns.append(normalize(mt)[:60])
 hits=[path for path,txt in old_contents if any(pat and pat in txt for pat in patterns)]
 r['exposure_check']={'checked_m01_m02_ids':True,'checked_withdrawn_ids':True,'old_corpus_files_scanned':len(old_files),'old_corpus_matches':hits[:10],'limitations':'仅核对仓库内旧专项/习题本/解析的文本文件；没有匹配不证明用户未在别处做过。纯数列及短泛化设问不能仅靠短句匹配确认未曝光。'}
 if hits:exposure.append({'number':r['number'],'source_id':r['source_id'],'files':hits})
(HERE/'quant_data.json').write_text(json.dumps(ROWS,ensure_ascii=False,indent=2)+'\n')
(HERE/'quant_data_exposure.json').write_text(json.dumps({'row_count':len(ROWS),'source_ids_unique':len({r['source_id'] for r in ROWS}),'m01_m02_overlap':[],'withdrawn_overlap':[],'old_files_scanned':len(old_files),'old_text_matches':exposure,'source_file_sha256':hashlib.sha256((ROOT/SOURCE).read_bytes()).hexdigest()},ensure_ascii=False,indent=2)+'\n')
print('saved',len(ROWS),'rows; old exposure matches',exposure)

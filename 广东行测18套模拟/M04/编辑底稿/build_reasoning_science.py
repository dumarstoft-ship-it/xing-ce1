#!/usr/bin/env python3
from pathlib import Path
import json,copy,re,hashlib
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
JZ='江浙行测_AI题库/questions.jsonl'
MOCK='模考/2026下半年广东卷_16-33季_AI可读/全部题目.jsonl'
def rows(p):return [json.loads(x)for x in (ROOT/p).read_text().splitlines()]
jz={q['question_id']:q for q in rows(JZ)}
mock={q['id']:q for q in rows(MOCK)}
answers={q['question_id']:q for q in rows('江浙行测_AI题库/answers.jsonl')}
ids={46:'gd-mock-2026h2-s21-q46',47:'gd-mock-2026h2-s25-q46',48:'gd-mock-2026h2-s23-q48',49:'gd-mock-2026h2-s22-q50',50:'gd-mock-2026h2-s26-q48',51:'JS2023-A类-091',52:'JS2022-A类-093',53:'ZJ2024-A类-104',54:'gd-mock-2026h2-s22-q52',55:'gd-mock-2026h2-s25-q55',56:'JS2022-A类-103',57:'gd-mock-2026h2-s24-q62',58:'JS2022-A类-094',59:'gd-mock-2026h2-s26-q59',60:'JS2023-A类-103',61:'JS2022-A类-102',62:'ZJ2024-A类-109',63:'gd-mock-2026h2-s26-q55',64:'JS2023-A类-101',65:'ZJ2024-A类-101',66:'gd-mock-2026h2-s33-q68',67:'gd-mock-2026h2-s17-q67',68:'gd-mock-2026h2-s31-q68',69:'gd-mock-2026h2-s22-q69',70:'gd-mock-2026h2-s32-q70'}
keys=dict(zip(range(46,71),'BBCACACDBCCABC D D A C B A D A D C A'.replace(' ','')))
assert len(keys)==25
analyses={
46:'选B。把每幅图看作同一张9×9网格上的图案：每一步，所有黑格整体向上、向左各平移一格，越过上边界的格从最下行接回，越过左边界的格从最右列接回。前五幅均符合这一循环平移；对第五幅再做一次，所得图形是B。四个选项黑格总数相同，单数黑格不能定项，应跟踪局部形状及越界后的接续位置。',
47:'选B。黑格构成一条连续折线：从前一幅到后一幅，折线尾部退去1格，头部沿现有路线继续前进2格，因此黑格数量依次为5、6、7、8、9。下一幅须从第五幅左下角的尾端去掉1格，并从右上角的头端向下添2格，得到B。只看数量还不够，新增和删去的位置也必须同时满足。',
48:'选C。比较的是相同图符出现的位置，而不是要求各行使用同一种图符。把题干从左到右的不同图符依次记作a、b、c、d、e，原串是a-b-b-c-d-a-c-e，即第1与6位相同，第2与3位相同，第4与7位相同，第5与8位分别是另外两种图符。C完整保留这种对应关系。A的第5与8位相同；B的第4、5、7位出现额外重复；D的第1、2、3位相同，均不符合。',
49:'选A，即②和④。需同时检查图案所在面和面内方向。左边小正方体的黑色小方块位于正面左下角，空心小方块位于顶面左前角；折叠②可以得到这一关系。右边小正方体的黑色块与空心块分别位于顶面、右面，并在同一顶点相接，同时正面的折线尖端朝上；折叠④可同时满足这三项。①虽然也能使两个小方块在同一顶点相接，但三角折线与这两面的相对方向不符；③不能符合左侧所需的两个角的位置关系。用六面局部坐标折叠，再枚举24种正旋转，左侧仅②匹配，右侧仅④匹配。',
50:'选C。先找由4个小正方体组成的2×2方片，再看方片外接出的部分。题干的方片外有两条支臂，每条各含2个小正方体；A、B、D保持这一连接结构，只是整体转动。C的方片外却是一条含3块的支臂和一条含1块的支臂，转动不能改变连接关系，因此不可能与题干相同。按图中可见面与连通关系还原8块坐标，枚举24种空间正旋转，也只有C不等价。这里利用的是整体连接结构，不要求所有立柱都落在同一水平面上。',
51:'选A。“欲事立，须是心立”只给出事立→心立；不想事立，并不能据此推出无须心立，A否定了前件后直接否定后件。B是“信念坚定→骨头硬”的逆否；C沿着信念缺失→缺钙→软骨病推出；D由不易迷失方向，反推并非“信念缺失或者不坚定”，即信念不缺失且坚定。B、C、D均可据题干推出。',
52:'选C。题干要证明的是中国对“全球变绿”的相对贡献，而不仅是中国自己变绿。C同时给出中国在全球植被面积中的占比和在全球净增量中的贡献：以6.6%的存量占比贡献25%的净增长，直接支撑“最重要力量之一”。B补充了中国变绿的事实，却没有说明其在全球增量中的分量；A谈木材进口，D谈其他地区毁林，均不及C直接。',
53:'选D。设问限定为研究人员通过题述长期对比实验“最有可能得到的论据”。D报告了实验组的实际发病情况，且唯一病例被题设归因为遗传因素，最贴合这一研究过程及所得结论。A提供发声机制，能反驳原先的“关节摩擦”解释，但不是这项长期发病对比实验所直接报告的结果；B谈握力和关节强度，不等于手指关节炎；C仅给出年龄相关性。D在这里是四项中最合适的实验观察，不应据一项有限观察宣称任何人掰手指都绝无风险，也不能把未给出的对照组数据补造出来。',
54:'选B。学者用“一次性给定剂量后未升高”推到“短期狂饮不会引起升高”，同时把两组差异归因于饮酒时间长短。B指出实验剂量并未达到所声称的狂饮程度，因此短期实验没有真正检验短期大量饮酒的作用，不能排除剂量差异造成结果不同。A、D与长期大量饮酒后激素升高相容；C说明代谢机制，但未说明这种机制足以区分短期与长期，削弱不如B直接。',
55:'选C。论据说明完整地被层有助于防止侵蚀，结论却把它提升为“只有具备这一条件，才能遏制水土流失”的必要条件。C给出地被层缺失、通过人工生态毯仍可遏制水土流失的反例，直接否定必要性。B经过自然修复后，地被层可能已经恢复完整，不能稳定构成“没有该条件但仍实现结果”的反例；A质疑证据基础，D说其他因素也有影响，均不如C切中结论。',
56:'选C。共有3名党员，而乙、丙的党员身份相同，所以乙、丙都为党员；由丙、丁不全为党员可知丁不是党员，甲是党员。若甲、乙都是男性，则丙、丁都是女性，丁只能靠“教授”满足至少一个特征，唯一教授就成了既非男性又非党员的丁，无法产生题设要求的组长。因此甲、乙都是女性，丙、丁是男性；丁不是党员，能同时具备男性、党员、教授三项特征的只可能是丙。',
57:'选A。需要解释的是投诉率上升，即投诉量相对于餐饮消费人次的比例上升。A只说消费人次增加，因而投诉绝对数增加；分子、分母可以同比例增加，投诉率完全可能不变，故不能解释题干的比例变化。B的菜品质量下降、C的投诉更便利、D的隐性收费增加，都可能提高每次消费引发投诉的概率，与菜单标价降低并不矛盾。',
58:'选B。专家把学习、使用方言的热潮视为对普通话使用推广的挤占，隐含二者主要竞争同一使用空间。B说明方言多用于家庭等非正式场合，普通话仍用于公共等正式场合，切断“方言兴起→损害普通话应用”的推断。A、D说明方言的价值，不直接回答会不会损害普通话推广；C讨论恢复活力的短期可行性，也没有像B那样直接解释两种语言可以并存。',
59:'选C。已知条件是厨余垃圾预处理后的热值一般仅为3—4MJ/kg，要据此判断它不适合焚烧发电，还须知道发电所需的最低热值高于这个水平。C把题给数值与适用门槛连接起来。A只是泛泛说有些垃圾不适合，B谈预处理作用，D谈另一处理方式，均不能直接补足“为什么这个热值不足以适用”的缺口。',
60:'选D。若乙偏瘦，则乙的话真，丙为1.72米且偏瘦；丙的话也真，丁为1.68米且偏胖。此时甲、丁应是两名偏胖者。丁的话假，且乙确实偏瘦，所以乙不为1.65米，只能为1.70米；于是甲为1.65米，他说“不到1.70米”却为真，与甲偏胖矛盾。故乙偏胖。丁若偏瘦，则他的话又要求乙偏瘦，也矛盾，所以丁偏胖。两名偏瘦者只能是甲、丙，丙的话为真，得丁身高1.68米、偏胖。完整唯一安排为甲1.65米偏瘦、乙1.72米偏胖、丙1.70米偏瘦、丁1.68米偏胖。注意“身高……且偏瘦”是假，不代表两个分句都假。',
61:'选D。甲的问题预先认定乙读过这本小说，乙通过说明自己没读过，否定提问所依赖的事实前提。D中商户预先认定顾客买了冰箱，顾客说明买的是洗衣机，同样否定了问题的事实前提。A质疑努力的效果，B表示全部赞成，C说两种情况都可锻炼，均未否定提问赖以成立的对象事实。',
62:'选A。商家的说法包含“学龄以上孩子都可以安全使用”。A所述重金属超标风险直接涉及使用者，包括学龄以上孩子，质疑这一安全性承诺。D虽然有严重伤害，但对象是4岁儿童，不在商家限定的人群内；C的听课效率下降不是对安全性、开发智力或爱上写字的直接检验；B的无聊评价也不能直接否定这些承诺。应同时看损害内容和对象范围，不能仅按后果严重程度选择。',
63:'选C。任意连续4节颜色不同，意味着编号相差不超过3的两节不能同色。第17节与已知的第14蓝、第16黄、第18橙、第20绿都相距不超过3，故第17节只能是红；第15节据第14蓝、第16黄、第17红、第18橙，只能是绿；第13节据第10红、第14蓝、第15绿、第16黄，只能是橙；第12节据第10红、第13橙、第14蓝、第15绿，只能是黄，C成立。完整约束枚举只有1个合法着色，第2、9、19节分别为黄、橙、蓝，A、B、D均不成立。',
64:'选B。小李把“没有发现某件事存在的证据”直接当成“这件事不存在”的依据。B把“我没看到他们出去”直接用于断定他们没有出去，论证方式相同。A依据当前天气预测，D依据当前积分预测；C由亲眼见到的不聪明事例推出“有时不聪明”，有具体观察支持，且不与“有时聪明”必然矛盾。B相似的是证据缺失到事实否定的跳跃，不要求双方结论的语气强度逐字相同。',
65:'选A。易燃品、易爆品都属于危险品，把具体类别与包含它们的上位类别并列，是分类层级混用。A的鸡、鸭属于家禽，也把下位类别和上位类别并列。B混用的是绘画技法与内容分类，造成交叉分类；C是颜色类别的并列；D用“等学习用品”统括前面的例子，没有把学习用品当作与铅笔、橡皮、小刀并列的另一类。',
66:'选D。静止时，B没有水平加速趋势，所受水平摩擦力为0；A受到向右的拉力和地面向左的静摩擦力。开始运动后，A、B始终相对静止，A通过向右的静摩擦力带动B，故B受到的仍是静摩擦而非动摩擦。地面粗糙程度均匀、正压力不变，运动阶段的地面滑动摩擦力不变；持续增大的拉力使整体加速度a增大，B所需静摩擦力f=m_Ba随之增大。A、B、C三项分别混淆了静止不受水平摩擦、A与地面的摩擦、以及是否发生相对滑动。',
67:'选A。先把理想电流表视作导线、理想电压表视作断路，真正的通电结构是L₁、L₂串联后与L₃并联。相同灯泡L₁、L₂分得相等电压，所以V₁=V₂=U/2；V₃跨接电源两端，示数为U，最大而不是最小。A₁与A₂都在串联支路中，示数相等；A₃在L₃单灯支路中，电流比两灯串联支路大。故只有A错误。题图看起来有许多横线，但经过电压表的线不能当作理想导线去短接灯泡。',
68:'选D，②⑤⑥属于物理性质。②难溶于水描述溶解性，⑤可拉成细丝描述延展性，⑥干冰在常温常压下消失体现升华，均不以生成新物质为前提。①稳定指不易发生化学反应；③碳酸钙与酸反应而溶解；④氨使湿润试纸变色涉及酸碱作用；⑦烧焦产生臭味涉及燃烧和分解；⑧熟石灰改良酸性土壤涉及中和，均为化学性质的表现。不能一概把“溶解”两个字当成物理性质，须看有没有反应生成新物质。',
69:'选C。两个长翅亲本生出残翅子代，说明长翅为显性、残翅为隐性；残翅个体为aa，父母都须提供a，且自身均为长翅，因此亲本基因型均为Aa。Aa×Aa的子代基因型理论比例为AA∶Aa∶aa=1∶2∶1，长翅理论比例为3/4。A把一个亲本写成aa，与亲本均为长翅矛盾；B漏了AA；D把3/4误作1/2。这里的3/4是孟德尔模型下的理论概率，不意味着每一窝恰好按这个比例分配。',
70:'选A。白天陆地升温一般较海洋快，陆地近地面空气受热上升，近地面形成相对低压，海面上较冷空气流向陆地，形成海风。近地面风通常由高压区流向低压区，B方向相反。夜晚陆地降温快，通常更容易形成由陆地吹向海洋的陆风，C把温度关系和风向都反了。海陆风的能量来源于太阳辐射造成的差异加热，不是地热能，D错误。'
}
reasons={46:'循环边界中的整体平移；黑格数不能替代位置核验。',47:'同时跟踪头部、尾部和净增量，单纯计数不足。',48:'用等同关系抽象图符序列，考查可迁移的结构识别。',49:'两块拼合与面内方向共同约束，练习折叠后的角与边对应。',50:'以2×2方片外的连接结构排除，避免凭视觉旋转相似感。',51:'自然语言中的必要条件、逆否与否前错误。',52:'区分局部增量与对全球增量的相对贡献。',53:'区分实验观察、作用机制及结论适用边界。',54:'发现对照实验中时间与剂量混杂。',55:'有用条件被提升为必要条件时寻找反例。',56:'人数、双条件与组长存在性共同约束。',57:'投诉绝对数上升不等于投诉率上升，防止分母遗漏。',58:'通过适用场景区分打断替代关系。',59:'用门槛将材料中的热值数据与适用性结论连接。',60:'两真两假中的合取命题整体真假与唯一配置。',61:'通过否定提问预设比较对话结构。',62:'安全性论证中的对象范围，排除严重但越界的事例。',63:'把局部连续约束转成距离约束，从已定颜色密集处回推。',64:'缺乏存在证据与存在反面证据的区别。',65:'上位与下位并列、交叉分类及例举统括的区别。',66:'动起来仍可为静摩擦，摩擦大小由整体加速度决定。',67:'复杂表路先按理想电表还原真实通电支路。',68:'按是否形成新物质区分性质，尤其避免见溶解就机械归类。',69:'由表型反推亲本基因型，再检查子代概率。',70:'从海陆热力差异贯通温度、气压与近地面风向。'}

def clean_jz(s):
 s=re.sub(r'(?<=[\u4e00-\u9fff]) +(?=[\u4e00-\u9fff])','',s)
 s=re.sub(r'(?<=\d) +(?=[\u4e00-\u9fff])','',s)
 parts=re.split(r'\n(?=(?:以下|根据|由此|甲：|乙：|丙：|丁：|（\d）))',s)
 return '\n'.join(re.sub(r'\s*\n\s*','',x).strip()for x in parts)
result=[]
for n,id in ids.items():
 source=copy.deepcopy(jz[id]if id in jz else mock[id]); bank='jiangzhe'if id in jz else 'guangdong_mock';sa=answers[id]['correct_answer']if id in answers else None
 q={'number':n,'section':'判断推理'if n<=65 else '科学推理','subsection':'图形推理'if n<=50 else('逻辑判断'if n<=65 else ['受力与摩擦','电路与电表','物理与化学性质','遗传规律','海陆风'][n-66]),'question_type':'single_choice','source_bank':bank,'source_file':JZ if id in jz else MOCK,'source_id':id,'source_question':source,'source_answer':sa,'answer':keys[n],'analysis':analyses[n],'selection_reason':reasons[n],'edits':[],'verification':{'status':'editor_checked_pending_cross_review','method':'编者先读题面推导，江浙题随后比较源参考答案；不称隔离盲审或Claude审核。图题实际查看，确定性约束另用穷举和几何不变量复算。','checked_on':'2026-11-15','source_answer_available':sa is not None,'source_answer_agreement':sa==keys[n]if sa else None,'figure_visual_inspection':n in [46,47,48,49,50,66,67],'report':'核验记录/reasoning_science_verification.json'},'options_mode':'in_figure'if n in [46,47,48,50]else'text_or_mixed'}
 if id in jz:
  q['stem_override']=clean_jz(source['stem']);q['options']={k:clean_jz(v)for k,v in source['options'].items()}
  q['edits'].append({'type':'layout_only','description':'合并PDF句内硬换行，去掉汉字间排版空格，保留设问、条件和逐人陈述分段。'})
  q['source_locators']={'original_number':source['original_number'],'pages':source['source'].get('pdf_pages',[]),'source':source['source']}
  q['source_answer_reference']={'file':'江浙行测_AI题库/answers.jsonl','source':answers[id]['source'],'quality_flags':answers[id].get('quality_flags',[])}
  q['source_notice']='题面与参考答案来自本仓库江浙整理库，保留原PDF定位及源对象；本次尚未从来源仓库重新下载原PDF逐字核对，参考答案不冒称官方答案。'
 else:
  q['source_locators']={'original_number':source['number'],'pages':source['source_pages'],'source':source['source']}
  q['source_notice']='来自仓库广东模考转写题库；源题参考答案为空，本卷答案由编者独立推导。源PDF文件信息与页码保留，但本次未取得原PDF重新逐字校对。'
 result.append(q)
D={q['number']:q for q in result}
# Keep each speaker and the global truth rule in their own paragraph.
D[60]['stem_override']=D[60]['stem_override'].replace('偏瘦。如果体型','偏瘦。\n如果体型')
D[60]['edits'].append({'type':'layout_only','description':'将真假话的全题规则与丁的发言分段，避免被误读为丁所说的话。'})
D[64]['stem_override']=D[64]['stem_override'].replace('小李：','\n小李：')
D[64]['edits'].append({'type':'layout_only','description':'将小朱、小李的发言分别起段，恢复说话者边界。'})
# Source OCR punctuation correction, clearly separated from mere wrapping.
D[58]['stem_override']='普通话是国家通用语言，除普通话外，还有粤语、吴语等方言。近年来，用各种方言演绎的段子大量涌入影视作品、短视频和网络综艺节目。这些作品生动有趣，让那些即使是从小生长在普通话环境里的人，也会觉得亲切，兴起了一股学习方言的热潮。据此，有专家认为，各种方言作品大行其道，其实不利于普通话在全国范围内的使用和推广。\n以下哪项如果为真，最能质疑上述专家的观点？'
D[58]['edits'].append({'type':'punctuation_normalization','description':'修复转写稿逗号、句号及“以下哪项？如果为真”的问号错位；保留论证内容、选项顺序。'})
D[57]['stem_override']=copy.deepcopy(D[57]['source_question']['stem'])
old='然而，该市同期关于餐饮消费的投诉率却不降反升，涨幅达30%。'
new='然而，该市同期的投诉量占餐饮消费人次的比例（下称投诉率）却不降反升，涨幅达30%。'
D[57]['stem_override'][0]['text']=D[57]['stem_override'][0]['text'].replace(old,new)
D[57]['edits'].append({'type':'clarify_denominator','description':'明示投诉率为投诉量占消费人次的比例，锁定原题分子/分母辨析，避免投诉率分母不明。','before':old,'after':new})
D[66]['stem_override']=copy.deepcopy(D[66]['source_question']['stem'])
D[66]['stem_override'][0]['text']=D[66]['stem_override'][0]['text'].replace('物块A受到一个从零开始逐渐增大的水平拉力F','物块A受到一个从零开始、在整个过程中持续逐渐增大的水平拉力F')
D[66]['edits'].append({'type':'clarify_condition','description':'明确拉力在运动阶段仍持续增大，避免把增力阶段误读为仅限起动前；不改变原拟考关系。'})
D[67]['stem_override']=copy.deepcopy(D[67]['source_question']['stem'])
D[67]['stem_override'][0]['text']=D[67]['stem_override'][0]['text'].replace('闭合开关S后','电流表、电压表均按理想电表处理。闭合开关S后')
D[67]['edits'].append({'type':'clarify_model','description':'把通常隐含的理想电表模型写入题干，确保等电势与示数关系的条件充分。'})
# Replace selected displays only after generated assets exist. Raw source_question is never edited.
for n,fn in [(46,'q46_pixel_shift.png'),(47,'q47_growing_path.png'),(49,'q49_cube_nets.png'),(50,'q50_solids.png'),(63,'q63_snake.png'),(66,'q66_blocks.png'),(67,'q67_circuit.png')]:
 asset=HERE.parent/'assets'/fn
 if not asset.exists():continue
 stem=copy.deepcopy(D[n].get('stem_override',D[n]['source_question']['stem']))
 for i,b in enumerate(stem):
  if b['type']in ['figure','table']:
   from PIL import Image
   w,h=Image.open(asset).size
   stem[i]={'type':'figure','path':str(asset.relative_to(ROOT)),'path_base':'repository','width_px':w,'height_px':h}
 D[n]['stem_override']=stem
 D[n]['edits'].append({'type':'diagram_redraw','description':'依据源图可见格位、形状或源库结构化图表重绘，提高打印清晰度；原始源对象和原图路径保留。','asset':str(asset.relative_to(ROOT))})
for q in result:
 assert q['answer']in'ABCD'
 if q['source_answer']is not None:assert q['source_answer']==q['answer'],(q['number'],q['source_answer'],q['answer'])
(HERE/'reasoning_science.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('Wrote',len(result),'questions',[(q['number'],q['answer'])for q in result])

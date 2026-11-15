#!/usr/bin/env python3
"""独立于选编脚本的数量复核：先只读取无答案题面，由第二审阅者自行建模。"""
from fractions import Fraction as F
from itertools import combinations, permutations
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
answers={31:'A',32:'B',33:'A',34:'C',35:'B',36:'A',37:'A',38:'D',39:'D',40:'B',41:'D',42:'A',43:'D',44:'B',45:'C'}
reasons={
31:'一次差25、26、29、38、65；二次差1、3、9、27，下一个81；下一次差146，下一项343。',
32:'统一分母96，分子40、43、48、55、64；差3、5、7、9，下一差11，分子75，得25/32。',
33:'按小数点分组：整数差3、6、9，下一差12得32；右侧04、12、36、108按数值乘3，下一组324。选32.324。',
34:'前项的一半加后项得到第三项：26/2+12=25；12/2+25=31；25/2+31=43.5；31/2+43.5=59。',
35:'各项取正平方根4、2、6、8、14，后项为前两项之和；下一根22，平方484。',
36:'外省人数须为7的倍数且占总人数1/8，因此总人数为56的倍数；100以内正值只有56。全班女生8，外省女生3，本省女生5；外省男生4，差1。',
37:'原成本100、售价125；新成本115、新成交价125×1.5×0.8=150；新利润率35/115=30.4348%，较25%高5.4348个百分点。',
38:'24米边含两个端点，9个传感器对应8段，间隔3；环形40点对应40段，周长120。另两边之和96，平方差24²=576，故两边之差6；斜边51。',
39:'原甲速v，路程4(v+60)。实际甲行1小时+维修后1.5小时，路程2.8v；乙300千米。解4(v+60)=2.8v+300得v50、总路程440。甲到B总耗时1+2.5+(440-50)/60=10小时。',
40:'螺丝钉数量N满足N/30-N/40=20，得2400；螺丝帽也需2400。给钉权重2、帽权重1，总工作量7200；A每小时最多贡献80，B最多60，时间至少7200/140=360/7>51。52小时可由A产2080钉，B用10又2/3小时产320钉、40小时产2400帽，故向上取整52。',
41:'恰有4单满25，满减总额12；5天同一账号最多领取5个4元红包，最多减20。折后总价最多148+12+20=180，原价300。可实现：4单各36元、2单各18元，分布5天使用5个红包。',
42:'四项不满意户数20、160、24、32，合计236；最多让236户各不满意一项且彼此不重叠，因此至少400-236=164户全满意。',
43:'总样本C(5,2)C(4,2)=60。指定一对夫妻后，余男4选1、余女3选1，共12种，其中1种会选入另一整对夫妻，应扣除；两对任选其一，共2×11=22，概率11/30。',
44:'左侧1485/15+1=100，右侧1485/33+1=46。中间重合点为165的1至8倍，共8处；首尾不在合并范围，故146-8=138。',
45:'甲乙内部2种。两侧紧邻者必须从另外4人中有序选2人，12种；把“左邻-甲乙-右邻”看成一块，与剩余4人共5个对象排列，5!种。总2×12×120=2880。',
}
rows=[{'number':n,'independent_answer':a,'derivation':reasons[n]} for n,a in answers.items()]
# 可行性与穷举独立检验，不从选编答案反推结论。
assert 197+(65+81)==343
assert F(75,96)==F(25,32)
assert F(35,115)-F(25,100)>F(5,100)
assert 24**2+45**2==51**2 and 24+45+51==120
assert F(2400,30)-F(2400,40)==20
assert F(360,7)>51 and F(320,30)+F(2400,60)<=52
men=list(range(5));women=list(range(4));pairs={(0,0),(1,1)}
counts={'total':0,'exactly_one':0}
for ms in combinations(men,2):
 for ws in combinations(women,2):
  counts['total']+=1
  if sum(m in ms and w in ws for m,w in pairs)==1:counts['exactly_one']+=1
assert counts=={'total':60,'exactly_one':22}
left=set(range(0,1486,15));right=set(range(0,1486,33));overlap=(left&right)-{0,1485}
assert len(left)+len(right)-len(overlap)==138
valid=0
for order in permutations(range(8)):
 pos={x:order.index(x) for x in range(4)}
 if pos[0] in (0,7) or pos[1] in (0,7) or abs(pos[0]-pos[1])!=1:continue
 if any(abs(pos[x]-pos[y])==1 for x in (2,3) for y in (0,1)):continue
 valid+=1
assert valid==2880
report={'reviewer':'GPT第二审阅者（言语编者）','scope':'M04数量31—45；先读取quant_blind_input.json，仅含题面，未读取answer/analysis后形成答案。','rows':rows,'independent_enumeration':{'q43':counts,'q44_common_interior_points':sorted(overlap),'q45_valid_queues':valid},'issues':[{'number':43,'severity':'distractor_quality','finding':'B为14/5，大于1，不可能是概率；不影响D唯一正确，但削弱干扰质量，建议核原图。若无原图，可明确作为编辑改编换成2/5，正好对应忘扣另一对夫妻的常见错误。'},{'number':40,'severity':'analysis_precision','finding':'精确连续最优360/7小时会产生非整数零件数量；本题只问整小时取整，可用51小时不够、52小时给出整数零件可行方案证明，避免宣称分数零件是实体可行方案。'}]}
(HERE/'quant_independent_answers_before_compare.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('独立作答15题完成；43、45已穷举，40已给52小时整数产量方案。')

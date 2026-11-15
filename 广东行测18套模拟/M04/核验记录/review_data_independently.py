#!/usr/bin/env python3
"""资料20题的第二读者核验；初始判断先记录，再读取编辑答案比较。

审读过程：root先抽出题面、材料、选项独立作答并查看第90题四幅原图，
随后把判断与数值写入此文件。比较步骤不参与生成独立答案。
"""
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
spec = importlib.util.spec_from_file_location('build_m04', PAPER/'build_m04.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
rows = json.loads((PAPER/'编辑底稿/quant_data.json').read_text())
questions = [b.normalize(r) for r in rows if r['number'] >= 71]

# 以下答案及理由在打开本模块编辑答案之前形成。算法只依题面数值。
findings = [
 (71,'D','原文四项工程不含红树林生态修复专项工程；不可由沿海地理常识补入材料未列项目。'),
 (72,'C','材料涉及十四五及十五五，不能推出十三五已达到给定阶段目标。题干采用“不能由材料支持”以容纳信息缺失。'),
 (73,'A',f'新增量占新增后总量：2682/(4931+2682)={2682/(4931+2682):.8f}，约35.2%。'),
 (74,'B',f'五年平均活动数：7.39/5={7.39/5:.3f}万场/年。'),
 (75,'B','首批30个不是整个十五五时期总计30个；其余项分别对应提高6个百分点、3市、每年不低于5%。'),
 (76,'A',f'本期份额×(部分增速-整体增速)/(1+部分增速)：823.05/1168.53×(-0.006-0.008)/0.994={823.05/1168.53*(-.006-.008)/.994:.8f}，下降约1.0个百分点。'),
 (77,'C',f'上年非住宅施工面积为15375.68/0.956−10467.79/0.957={15375.68/.956-10467.79/.957:.5f}万平方米。'),
 (78,'B','住宅增速高于总增速等价于高于非住宅增速（两部分基期均为正）。仅施工面积、竣工面积两项满足。'),
 (79,'A',f'非住宅销售额增量：(1167.46−989.70)−(1167.46/1.321−989.70/1.294)={(1167.46-989.70)-(1167.46/1.321-989.70/1.294):.6f}亿元。'),
 (80,'C','①2022年非住宅销售面积占商品房销售面积的比重可还原；②2022年商品房单位面积销售额可由基期销售额/基期销售面积计算；③2022年住宅单位面积销售额的同比增速还需2021年对应数据。因此可推出2项。'),
 (81,'A','1—6月出口数量合计2074.5万个，月均345.75万个。'),
 (82,'D',f'出口单价增速：3.95/6.869−1={3.95/6.869-1:.8f}，约下降42.5%。'),
 (83,'B',f'二季度金额/一季度金额−1：(6.1+5.6+7.6)/(3.5+3.2+3.8)−1={(6.1+5.6+7.6)/(3.5+3.2+3.8)-1:.8f}，约增长83.8%。'),
 (84,'C','按题目明确指定的表内显示值计算，3、4、5、6月均价≤150元/个，共4个月。4月显示值约149.00，不能把已舍入统计量理解为未显示真值来作边界判断。'),
 (85,'D','6月数量553.3、金额7.6均为六个月最大。A上年5—6月金额约7.615<10；B上年2月数量约215.40>1月188.94；C上年对越南/香港数量约2.386倍。'),
 (86,'C',f'2023年全年石油运量比粮食运量多13050−6847=6203万吨；全年含12个月，月均差为6203/12={(13050-6847)/12:.6f}万吨。这里的12是月数，单位是万吨。'),
 (87,'B','平均运距=货物周转量/货运量。国家铁路周转量增速−0.1%低于货运量0.2%，平均运距下降；其他铁路16.6%高于3.9%，平均运距上升。'),
 (88,'C',f'2022年国家铁路周转量占比：(32638.50/0.999)/(36460.39−514.70)={(32638.50/.999)/(36460.39-514.70):.8f}，约90.9%。'),
 (89,'D',f'2020—2023年共3个间隔，年均货运增量(503535−455236)/3/10000={(503535-455236)/3/10000:.8f}亿吨。'),
 (90,'A','由表中数量计算，2019—2022年增速约7.805%、3.178%、4.863%、4.410%，走势为大降、回升、小降。逐幅查看四张原图后，只有A匹配。'),
]
assert [n for n,_,_ in findings] == list(range(71,91))
hashes = {q['number']: hashlib.sha256(json.dumps(q,ensure_ascii=False,sort_keys=True).encode()).hexdigest() for q in questions}
independent = {
 'paper_id':'M04', 'reviewer':'GPT第二读者（root）',
 'method':'先只读考生题面、材料和选项独立作答；第90题逐幅核对原图；落盘后再对编辑键。',
 'scope':'71—90；核对单位、基期、同比/环比、完整时间间隔、信息缺失与表内舍入边界。',
 'answers':[{'number':n,'answer':a,'reason':reason,'input_sha256':hashes[n]} for n,a,reason in findings],
 'limitations':'内部交叉核验不等于Claude外部审读；题设数据按给定材料作答，不将其当作外部事实背书。',
}
initial = HERE/'data_independent_answers_before_compare.json'
if not initial.exists():
 initial.write_text(json.dumps(independent,ensure_ascii=False,indent=2)+'\n')
else:
 previous=json.loads(initial.read_text())
 assert [(x['number'],x['answer']) for x in previous['answers']] == [(n,a) for n,a,_ in findings], '不得静默覆盖初始盲答'

# 初始判断已持久化，以下才对编辑答案。
editor={r['number']:r['answer'] for r in rows if r['number'] >= 71}
comparison=[{'number':n,'independent_answer':a,'editor_answer':editor[n],'match':a==editor[n],'input_unchanged':hashes[n]==next(x['input_sha256'] for x in json.loads(initial.read_text())['answers'] if x['number']==n)} for n,a,_ in findings]
previous=json.loads(initial.read_text())
corrections=[]
for n,a,reason in findings:
 old=next(x for x in previous['answers'] if x['number']==n)
 if old['reason']!=reason:
  corrections.append({'number':n,'initial_reason':old['reason'],'corrected_reason':reason,'answer_unchanged':True,'identified_at':'最终PDF逐页人工核对','explanation':'第二读者的初始理由记述有误：第80题把面积份额记成销售额份额，第86题误写成年度间隔及辆。对应计算和答案不变；编辑原解析本来正确，题面和解析无需修改。初始记录不覆盖。'})
(HERE/'data_independent_reasoning_corrections.json').write_text(json.dumps(corrections,ensure_ascii=False,indent=2)+'\n')
report={'paper_id':'M04','total':20,'matching':sum(r['match'] for r in comparison),'all_inputs_unchanged':all(r['input_unchanged'] for r in comparison),'results':comparison,'reviewer_reason_corrections':'data_independent_reasoning_corrections.json','corrected_reason_numbers':[r['number'] for r in corrections]}
(HERE/'data_independent_comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
assert report['matching']==20, report
print('资料第二读者：20/20同键；初始判断与当前输入均已记录。')

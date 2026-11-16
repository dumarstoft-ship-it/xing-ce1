#!/usr/bin/env python3
"""Assemble selected originals from immutable banks; never rewrite source prose."""
import collections,copy,hashlib,json,re
from pathlib import Path
D=Path(__file__).resolve().parent
R=D.parents[1]
P=D.parent
JZ='江浙行测_AI题库/questions.jsonl'
JA='江浙行测_AI题库/answers.jsonl'
MOCK='模考/2026下半年广东卷_16-33季_AI可读/全部题目.jsonl'
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def jl(p):return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def h(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
def main():
 banks={'jiangzhe':{q['question_id']:q for q in jl(R/JZ)},'guangdong_mock':{q['id']:q for q in jl(R/MOCK)}}
 refs={q['question_id']:q for q in jl(R/JA)}
 choices=load(D/'choices.json'); E=load(D/'editorial.json'); rows=load(D/'originals.json')
 excluded=set(load(D/'excluded_ids.json'))
 arrangements=[('verbal',16,'言语理解与表达'),('quant',31,'数量关系'),('graph',46,'判断推理'),('logic',51,'判断推理'),('science',66,'科学推理'),('data',71,'资料分析')]
 for cat,start,sec in arrangements:
  for n,sid in enumerate(choices[cat],start):
   assert sid not in excluded,(n,sid,'used/retired/exposed')
   bank='guangdong_mock' if sid.startswith('gd-mock-') else 'jiangzhe'
   s=copy.deepcopy(banks[bank][sid]); e=E[str(n)]
   ref=refs.get(sid); provided=ref.get('correct_answer') if ref else None
   if provided: assert provided==e['answer'],(n,provided,e['answer'])
   q={'number':n,'source_id':sid,'source_bank':bank,'source_file':MOCK if bank=='guangdong_mock' else JZ,
      'section':sec,'subtype':('数字推理' if n<36 else '数学运算') if cat=='quant' else {'verbal':'言语','graph':'图形推理','logic':'逻辑判断','science':'科学推理','data':'资料分析'}[cat],
      'question_type':'single_choice','source_question':s,'source_answer':provided,
      'answer':e['answer'],'analysis':e['analysis'],'selection_reason':e['selection_reason'],
      'edits':[],'source_locators':{'id':sid,'original_number':s.get('original_number',s.get('number')),
       'source':s.get('source'),'source_pages':s.get('source_pages')},
      'verification':{'status':'editor_checked_pending_claude','method':'本编辑先作答，再与源参考答案或本题复算/原图读取对照；不是隔离的第二读者审核。','reference_answer_available':bool(provided),'reference_answer_agreement':True if provided else None},
      'source_notice':'原题文字、标点、选项及现有原图保留；源卷为用户确认未做过的题源，仍排除既有整卷与旧专项曝光。'}
   if ref:q['source_answer_reference']={'file':JA,'source':ref.get('source'),'quality_flags':ref.get('quality_flags',[])}
   if cat in ['quant','science','data']:q['source_notice']+=' 未为降低难度而补写提示或重构选项。'
   if n==20:q['source_notice']+=' 当前源转写四个选项内部未分词留空，本稿保留所接收文本，未自行造称原卷空格；打印时可对原卷检查排版。'
   if n in [24,65]:q['source_notice']+=' 解析已说明最佳选项与其他表述之间的边界，列为独立审核重点；不以改写选项处理主观判断。'
   if cat=='data':q['source_notice']+=' 材料表格按源库结构化转写呈现，未取得其原PDF表格图片，不冒称逐格原图核验。'
   if 76<=n<=80:
    q['materials']=[copy.deepcopy(s['material'])]
    note=q['materials'][0]['blocks'][0].pop('notes')
    assert note=='同比增长列为绝对增量，原表未标百分号。'
    q['edits']=[{'type':'remove_transcription_hint','description':'仅去掉转写附注“同比增长列为绝对增量，原表未标百分号。”；题目、表头、单位、数字均不变，不提前替考生判断增量/增长率。原附注仍完整保存在source_question。'}]
   rows.append(q)
 rows.sort(key=lambda q:q['number']);assert [q['number'] for q in rows]==list(range(1,91))
 # 0.2.0：Claude审核后的修订（用户授权Claude直接修改）。只改空白的覆盖须与源题去空白后逐字相同。
 rev=load(D/'revisions_v020.json') if (D/'revisions_v020.json').exists() else None
 if rev:
  byn={q['number']:q for q in rows};C=lambda t:re.sub(r'\s','',t)
  T=lambda v:v if isinstance(v,str) else ''.join(b.get('text','') for b in v)
  for n,r in rev['layout_only'].items():
   q=byn[int(n)];src=q['source_question']
   if 'stem_block' in r:
    stem=copy.deepcopy(src['stem'])
    if isinstance(stem,str):assert stem==r['from'];stem=r['to']
    else:assert stem[r['stem_block']]['text']==r['from'];stem[r['stem_block']]['text']=r['to']
    assert C(r['from'])==C(r['to']);q['stem_override']=stem
   if 'options' in r:
    assert all(C(T(src['options'][k]))==C(v) for k,v in r['options'].items()) and set(r['options'])==set(src['options'])
    q['options']=dict(r['options'])
   q['edits'].append({'type':'layout_only','version':rev['version'],'description':r['description']})
  for n,r in rev['options'].items():
   q=byn[int(n)];q['options']=dict(r['options'])
   q['edits'].append({'type':'distractor_revision','version':rev['version'],'description':r['description']})
  for n,r in rev['notices'].items():
   q=byn[int(n)];assert r['drop'] in q['source_notice']
   q['source_notice']=(q['source_notice'].replace(' '+r['drop'],'').replace(r['drop'],'')+(' '+r['add'] if r['add'] else '')).strip()
  for q in rows:
   q['verification']['status']='claude_reviewed_v010_revised_v020'
 assert len({q['source_id'] for q in rows})==90
 cfg={'paper_id':'M05','version':rev['version'] if rev else '0.1.0','date':'2026-11-16','date_timezone':'Asia/Taipei',
 'source_snapshot':'8b37121d4f486e364b8f76826cf8de651021f4b2','policy_snapshot':'cabcf30f8f26e7daa49f80b836212ee1efbbeccb',
 'target_question_count':90,'minutes':90,'missing_numbers':[],
 'completed_section_counts':dict(collections.Counter(q['section'] for q in rows)),
 'status':'claude_reviewed_revised' if rev else 'editor_checked_pending_claude',
 'external_review':'claude_review_v010_done' if rev else 'not_started',
 'printing_status':'final_print_by_claude' if rev else 'pending_external_review',
 'display_status':('90题完整卷0.2.0：Claude审核后已按审核意见修订（用户授权Claude直接修改），正式打印版见打印版/。' if rev else
                   '90题完整待审稿；题本、编辑解析与复算记录已齐，尚未经过Claude独立审核，不是正式打印定稿。'),
 'structure_basis':'沿用项目90题结构；并非对2027公告题量作预测。',
 'source_exposure':'用户已确认源卷未做过；与已用、撤题和旧专项曝光排重。',
 'canonical_source':'selection.json','review_handoff':'交接_Claude.md',
 'editorial_inputs':['originals.json','choices.json','editorial.json'],
 'answer_counts':{'source_reference':sum(bool(q.get('source_answer')) for q in rows),'editor_without_source_key':sum(not q.get('source_answer') for q in rows)}}
 dump(D/'selection.json',rows);dump(D/'paper.json',cfg)
 print(json.dumps({'prepared':90,'source_reference':cfg['answer_counts']['source_reference']},ensure_ascii=False))
if __name__=='__main__':main()

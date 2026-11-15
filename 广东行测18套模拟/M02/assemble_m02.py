#!/usr/bin/env python3
"""One-time assembly from preserved source banks and the editorial layer.
After assembly, edit selection.json and use build_m02.py; never reset reviewed work.
"""
from pathlib import Path
import json,copy,importlib.util,hashlib,runpy
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROJECT=HERE.parent
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
def jl(p):return [json.loads(s) for s in p.read_text(encoding='utf-8').splitlines() if s.strip()]
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if (HERE/'selection.json').exists():
 print('M02 selection already exists: preserved. Rebuild with build_m02.py.')
 raise SystemExit(0)
checkpoint=load(HERE/'选编断点_75题.json')
paths=['江浙行测_AI题库/questions.jsonl','模考/2026下半年广东卷_16-33季_AI可读/全部题目.jsonl','国考/言语理解/2016-2025/all.jsonl']
lookup={};filemap={}
for p in paths:
 for q in jl(ROOT/p):
  sid=q.get('id',q.get('question_id'));assert sid not in lookup
  lookup[sid]=q;filemap[sid]=p
sources=[]
for n,sid,ans in checkpoint['rows_number_source_answer']:
 sources.append({'number':n,'source_id':sid,'checkpoint_answer':ans,'source_file':filemap[sid],'source_question':lookup[sid]})
assert len(sources)==75 and {s['number'] for s in sources}==set(range(16,91))
E={}
for p in sorted((HERE/'编辑底稿').glob('*.jsonl')):
 for e in jl(p):
  n=e.pop('n');assert str(n) not in E;E[str(n)]=e
assert set(map(int,E))==set(range(16,91))
write(HERE/'editorial.json',E)
runpy.run_path(str(HERE/'编辑底稿/politics_original.py'),run_name='__main__')
original=load(HERE/'politics_original.json')
am={r['question_id']:r for r in jl(ROOT/'江浙行测_AI题库/answers.jsonl')}
spec=importlib.util.spec_from_file_location('printtools',PROJECT/'打印排版/build_print.py');pr=importlib.util.module_from_spec(spec);spec.loader.exec_module(pr)
log=pr.Log()
def clean_blocks(b,n,loc):
 if isinstance(b,str):return '\n'.join(pr.reflow(b,n,loc,log))
 if isinstance(b,list):
  ret=copy.deepcopy(b)
  for x in ret:
   if x.get('type')=='text':x['text']='\n'.join(pr.reflow(x['text'],n,loc,log))
  return ret
 return b
rows=copy.deepcopy(original);sc=[]
for s in sources:
 n=s['number'];sid=s['source_id'];q=s['source_question'];e=E[str(n)];sf=s['source_file'];sq=copy.deepcopy(q)
 assert s['checkpoint_answer']==e['answer'],(n,'checkpoint answer changed')
 source_ans=am[sid]['correct_answer'] if sid in am else q.get('answer')
 r={'number':n,'section':('言语理解与表达' if n<=30 else '数量关系' if n<=45 else '判断推理' if n<=65 else '科学推理' if n<=70 else '资料分析'),'subsection':('数字推理' if 31<=n<=35 else '数学运算' if 36<=n<=45 else '图形推理' if 46<=n<=50 else '逻辑判断' if 51<=n<=65 else ''),'question_type':'single_choice','source_bank':'guangdong_mock' if sid.startswith('gd-mock') else 'jiangzhe' if sid.startswith(('JS','ZJ')) else 'guokao_verbal','source_file':sf,'source_id':sid,'source_question':sq,'source_answer':source_ans,'answer':e['answer'],'analysis':e['analysis'],'selection_reason':e['selection_reason'],'edits':[],
 'verification':{'status':'editor_checked_pending_claude','method':'本轮对已保存断点作题面、解法及答案复核；已见断点答案，不冒称本轮盲解。数值与枚举另见可重复核验脚本，图形题实际查看。','source_answer_available':source_ans is not None,'source_answer_agreement':None if source_ans is None else source_ans==e['answer'],'checked_on':'2026-11-15','external_review':'pending_claude'}}
 if source_ans:
  assert source_ans==e['answer'],(n,sid,source_ans,e['answer']);sc.append({'number':n,'source_id':sid,'source_answer':source_ans,'editor_answer':e['answer'],'match':True})
 stem=q['stem']
 if 'stem_text' in e:
  extras=[copy.deepcopy(b) for b in stem if b.get('type')!='text'] if isinstance(stem,list) else []
  text=e['stem_text'].replace('R₁','$R_1$').replace('R₂','$R_2$').replace('S₁','$S_1$').replace('S₂','$S_2$').replace('S₃','$S_3$')
  r['stem_override']=[{'type':'text','text':text}]+extras
  r['edits'].append({'type':'stem_clarification' if n not in [71,72] else 'adapted_question','description':e['edit_reason']})
 else:
  fixed=clean_blocks(stem,n,'题干')
  if fixed!=stem:r['stem_override']=fixed
 opts=q['options']
 if 'options_text' in e:r['options']={k:[{'type':'text','text':v}] for k,v in e['options_text'].items()}
 else:
  fixed={k:clean_blocks(v,n,'选项'+k) for k,v in opts.items()}
  if fixed!=opts:r['options']=fixed
 if 46<=n<=50:r['options_mode']='in_figure'
 if q.get('material'):
  m=copy.deepcopy(q['material']);mid=m['id']
  for b in m['blocks']:
   if b.get('type')=='text':
    if mid=='gd-mock-2026h2-s16-m3':
     for phrase in ['2024年，广东省在稳外贸方面','2024年，广东省在稳外资方面']:b['text']=b['text'].replace(phrase,'\n\n'+phrase)
    if mid=='gd-mock-2026h2-s20-m3':
     phrase='2024年，全国民航运输机场完成货邮吞吐量';b['text']=b['text'].replace(phrase,'\n\n'+phrase)
  if m!=q['material']:
   r['materials']=[m];r['edits'].append({'type':'material_paragraphs','description':'依据源库保存的行首缩进坐标和材料语义恢复真实分段；不改材料字符、数值和顺序。未声称已逐页查看原PDF。'})
 if any(x['题号']==n for x in log.items):r['edits'].append({'type':'layout_only','description':'合并源PDF行末硬换行，保留列举、对话、设问分段；详见格式核验日志。'})
 r['source_locators']={'original_number':q.get('number',q.get('original_number')),'pages':q.get('source_pages',q.get('source',{}).get('pdf_pages')),'source':q.get('source')}
 if sid in am:r['source_answer_reference']={'file':'江浙行测_AI题库/answers.jsonl','source':am[sid].get('source'),'quality_flags':am[sid].get('quality_flags',[])}
 rows.append(r)
assert len(rows)==90 and len(sc)==28
rows.sort(key=lambda r:r['number'])
assert not {r['source_id'] for r in rows}&{r['source_id'] for r in load(PROJECT/'M01/selection.json')}
write(HERE/'selection.json',rows)
write(HERE/'核验记录/source_answer_comparison.json',{'matched_count':len(sc),'comparisons':sc,'limits':'有源参考答案的28题另行比对；参考答案不等于官方答案，不以相同字母代替解题核验。'})
write(HERE/'核验记录/layout_log.json',log.items)
cfg={'paper_id':'M02','version':'0.1.0','source_snapshot':'5800414d9cb40bfcfe66888eb87bb44631eac38f','target_question_count':90,'missing_numbers':[],
 'completed_section_counts':{'政治理论':10,'常识应用':5,'言语理解与表达':15,'数量关系':15,'判断推理':20,'科学推理':5,'资料分析':20},'date':'2026-11-15','date_timezone':'Asia/Shanghai','status':'editor_checked_review_draft','external_review':'pending_claude','printing_status':'not_started',
 'display_status':'90题已编齐并经编辑核验；待Claude独立审核，尚非打印定稿。','structure_basis':'沿用项目近年广东90题结构；不承诺未来考试固定题量。'}
write(HERE/'paper.json',cfg)
core=(PROJECT/'M01/build_m01_core.py').read_text(encoding='utf-8').replace('M01','M02')
core=core.replace('审核范围与本次修订状态见paper.json及审核意见处理说明。','本稿尚待Claude独立审核，打印状态见paper.json。')
(HERE/'build_m02.py').write_text(core,encoding='utf-8')
print(json.dumps({'assembled':90,'source_answers_matched':len(sc),'layout_log_entries':len(log.items)},ensure_ascii=False))

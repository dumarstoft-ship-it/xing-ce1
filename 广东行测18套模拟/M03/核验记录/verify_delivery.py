#!/usr/bin/env python3
"""Verify M03 from its canonical selection and record actual executions.

Does not modify source banks or selection.json. Rebuilds generated deliverables,
executes existing numeric/reasoning checks, compares sources, checks pupil JSON
metadata, and checks deterministic rebuilds and project ledger preservation.
"""
from __future__ import annotations
import collections
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

HERE=Path(__file__).resolve().parent
PAPER=HERE.parent
PROJECT=PAPER.parent
ROOT=PROJECT.parent
OUT=HERE/'交付核验.json'
ERRORS=[]
REPORT={'paper_id':'M03','checked_on':'2026-11-15','date_timezone':'Asia/Taipei','canonical_source':'selection.json','checks':{},'executions':[],'limitations':['本检查是结构、来源、计算和重建一致性核验，不是90题答案正确性的自动证明。','GPT内部交叉复核与Claude独立审核分开；本稿尚待Claude审核及之后的打印排版。','未声称原PDF全部逐题核对；缺失原图的重建依据及边界另有编辑记录。','不重复既有源ID或仓库文本未匹配，不等于用户从未在其他材料中做过。','题目JSON保留必要图片寻址路径，路径可能含源库目录名；它们不作为考生可见题源说明。']}

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def lines(p):return [json.loads(l) for l in p.read_text(encoding='utf-8').splitlines() if l.strip()]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def stable_hash(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def rel(p):return str(p.relative_to(ROOT))
def ensure(ok,message):
 if not ok:ERRORS.append(message)
 return bool(ok)
def execute(script):
 proc=subprocess.run([sys.executable,str(script)],cwd=ROOT,text=True,capture_output=True)
 record={'command':[sys.executable,rel(script)],'exit_code':proc.returncode,'stdout':proc.stdout.strip(),'stderr':proc.stderr.strip(),'script_sha256':sha(script)}
 REPORT['executions'].append(record)
 ensure(proc.returncode==0,f'Execution failed: {rel(script)}')
 return record

def walk(x,path=''):
 if isinstance(x,dict):
  for k,v in x.items():
   loc=f'{path}.{k}' if path else k
   yield loc,k,v
   yield from walk(v,loc)
 elif isinstance(x,list):
  for i,v in enumerate(x):yield from walk(v,f'{path}[{i}]')

def effective(r):
 s=r.get('source_question') or {}
 return {'source_id':r['source_id'],'answer':r['answer'],
  'stem':r.get('stem_override',r.get('stem',s.get('stem'))),
  'options':r.get('options',s.get('options')),
  'figures':r.get('figures',s.get('figures')),
  'materials':r.get('materials',r.get('material',s.get('material',s.get('materials')))),
  'question_type':r['question_type']}


def main():
 cfg=read(PAPER/'paper.json');rows=read(PAPER/'selection.json');by={r['number']:r for r in rows}
 REPORT['version']=cfg['version']
 start_inputs={name:sha(PAPER/name) for name in ['selection.json','paper.json','build_m03.py']}
 REPORT['input_sha256']=start_inputs
 # The canonical builder is intentionally invoked first, before examining outputs.
 execute(PAPER/'build_m03.py')
 qs=lines(PAPER/'题目.jsonl');qmap={q['number']:q for q in qs}
 ranges=[('政治理论',1,10),('常识应用',11,15),('言语理解与表达',16,30),('数量关系',31,45),('判断推理',46,65),('科学推理',66,70),('资料分析',71,90)]
 expected_sections={name:end-start+1 for name,start,end in ranges}
 actual_sections=dict(collections.Counter(r['section'] for r in rows))
 types=dict(collections.Counter(r['question_type'] for r in rows))
 ensure(len(rows)==90 and sorted(by)==list(range(1,91)) and len(by)==len(rows),'Canonical question numbering is not exactly 1—90')
 ensure(len(qs)==90 and sorted(qmap)==list(range(1,91)) and len(qmap)==len(qs),'Generated question numbering is not exactly 1—90')
 ensure(actual_sections==expected_sections,'Section counts differ from 90-question structure')
 ensure(types=={'true_false':4,'single_choice':84,'multiple_choice':2},'Question-type counts differ from 4 TF + 84 single + 2 multiple')
 for section,start,end in ranges:
  ensure(all(by[n]['section']==section and qmap[n]['section']==section for n in range(start,end+1)),f'Section positions wrong: {section}')
 for n in range(1,91):
  expected_type='true_false' if n<=4 else ('multiple_choice' if n in [9,10] else 'single_choice')
  ensure(by[n]['question_type']==qmap[n]['question_type']==expected_type,f'Question {n}: wrong type at position')
  answer=by[n]['answer'];options=qmap[n]['options']
  if expected_type=='true_false':ensure(answer in ['正确','错误'] and not options,f'Question {n}: invalid true/false key')
  else:
   ensure(set(options)==set('ABCD') and all(options.values()),f'Question {n}: incomplete ABCD options')
   ensure(set(answer)<=set('ABCD') and len(set(answer))==len(answer),f'Question {n}: invalid choice key')
   ensure((len(answer)>=2)==(expected_type=='multiple_choice'),f'Question {n}: single/multiple answer mismatch')
  ensure(bool(qmap[n]['stem']) and bool(by[n].get('analysis')),f'Question {n}: missing stem or analysis')
 md_numbers=[int(x) for x in re.findall(r'^### (\d+)\.$',(PAPER/'题本_待审.md').read_text(),re.M)]
 ensure(md_numbers==list(range(1,91)),'Markdown booklet question sequence is not 1—90')
 REPORT['checks']['structure']={'question_count':len(rows),'question_types':types,'section_counts':actual_sections,'markdown_numbers_complete':md_numbers==list(range(1,91)),'missing_numbers':cfg['missing_numbers']}

 groups=collections.defaultdict(list);materials={}
 for q in qs:
  if q['section']=='资料分析':ensure(len(q['materials'])==1,f'Data question {q["number"]}: not exactly one material')
  for m in q['materials']:
   if m['id'] in materials:ensure(m==materials[m['id']],f'Inconsistent normalized material {m["id"]}')
   materials[m['id']]=m;groups[m['id']].append(q['number'])
 ensure(len(groups)==4 and sorted(groups.values())==[list(range(n,n+5)) for n in [71,76,81,86]],'Data groups are not four complete consecutive five-question groups')
 ensure(sorted(materials)==['M03-M01','M03-M02','M03-M03','M03-M04'],'Normalized material IDs leak source or are not local M03 identifiers')
 REPORT['checks']['data_groups']={'count':len(groups),'members':dict(groups),'all_shared_material_records_identical':True}

 # Read original source records once per bank and compare exact objects.
 non_original=[r for r in rows if r['source_bank']!='editor_original']
 original=[r for r in rows if r['source_bank']=='editor_original']
 ensure(len(non_original)==75 and len(original)==15,'Expected 75 sourced and 15 original questions')
 banks={};source_preserved=[]
 for r in non_original:
  sf=r['source_file']
  if sf not in banks:banks[sf]={x.get('question_id',x.get('id')):x for x in lines(ROOT/sf)}
  same=r.get('source_question')==banks[sf].get(r['source_id'])
  ensure(same,f'Source object altered or missing: Q{r["number"]} {r["source_id"]}')
  if same:source_preserved.append(r['number'])
 ensure(all(r.get('source_question') is None for r in original),'An original question has an undeclared source object')
 REPORT['checks']['source_preservation']={'sourced_questions':len(non_original),'original_questions':len(original),'exact_source_object_matches':len(source_preserved),'matched_numbers':source_preserved,'bank_sha256':{sf:sha(ROOT/sf) for sf in banks}}

 jz_answers={x['question_id']:x for x in lines(ROOT/'江浙行测_AI题库/answers.jsonl')}
 comparisons=[];missing=[]
 for r in non_original:
  sq=banks[r['source_file']][r['source_id']]
  if r['source_file']=='江浙行测_AI题库/questions.jsonl':
   source_key=jz_answers.get(r['source_id'],{}).get('correct_answer');keyfile='江浙行测_AI题库/answers.jsonl'
  else:source_key=sq.get('answer');keyfile=r['source_file']
  ensure(r.get('source_answer')==source_key,f'Q{r["number"]}: saved source_answer differs from source answer bank')
  if source_key:
   same=source_key==r['answer'];ensure(same,f'Q{r["number"]}: source key {source_key} differs from editor key {r["answer"]}')
   comparisons.append({'number':r['number'],'source_id':r['source_id'],'source_key':source_key,'editor_key':r['answer'],'answer_file':keyfile,'matches':same})
  else:missing.append(r['number'])
 REPORT['checks']['reference_answer_comparison']={'available_count':len(comparisons),'matching_count':sum(x['matches'] for x in comparisons),'unavailable_sourced_count':len(missing),'unavailable_numbers':missing,'comparisons':comparisons,'notice':'来源参考答案比对；不是官方答案认证，也不替代对改写题面的独立求解。'}

 current_ids={r['source_id'] for r in rows};ensure(len(current_ids)==90,'Duplicate source IDs inside M03')
 prior_ids=set();prior_counts={}
 for paper_id in ['M01','M02']:
  previous=read(PROJECT/paper_id/'selection.json');prior_counts[paper_id]=len(previous);prior_ids|={r['source_id'] for r in previous}
 withdrawn_ids=set();withdrawn_files=[]
 for paper_id in ['M01','M02']:
  path=PROJECT/paper_id/'撤题记录.json'
  if path.exists():
   withdrawn_files.append(rel(path))
   for loc,key,value in walk(read(path)):
    if key=='source_id' and isinstance(value,str):withdrawn_ids.add(value)
 overlap=sorted(current_ids&prior_ids);withdrawn_overlap=sorted(current_ids&withdrawn_ids)
 ensure(not overlap,'M03 overlaps current M01/M02 sources');ensure(not withdrawn_overlap,'M03 reuses withdrawn/exposed sources')
 REPORT['checks']['deduplication']={'current_unique_ids':len(current_ids),'prior_question_counts':prior_counts,'M01_M02_overlap':overlap,'withdrawn_files':withdrawn_files,'withdrawn_id_count':len(withdrawn_ids),'withdrawn_overlap':withdrawn_overlap,'user_done':'unknown'}

 # Source and answer metadata must not reach the pupil question projection.
 forbidden={'answer','correct_answer','answer_candidates','analysis','explanation','source','source_id','source_file','source_bank','source_question','source_answer','source_answer_reference','source_metadata','source_pages','source_spans','source_asset_id','asset_id','caption','original_number','original_pages','provenance','provenance_note','verification','edits','selection_reason','source_question_numbers','svg_path'}
 metadata_leaks=[];visible_leaks=[];figures=set();visible_patterns=[r'gd-mock-2026h2-',r'GKYY-\d{4}-',r'(?:JS|ZJ)\d{4}-A类-\d+',r'原卷第\d+页',r'【(?:答案|解析)】',r'参考答案[:：]',r'正确答案[:：]']
 for q in qs:
  for loc,key,value in walk(q):
   if key in forbidden:metadata_leaks.append({'number':q['number'],'path':loc,'key':key})
   if key in ['text','title','notes'] and isinstance(value,str):
    if '\ufffd' in value:visible_leaks.append({'number':q['number'],'path':loc,'reason':'replacement character'})
    for pattern in visible_patterns:
     if re.search(pattern,value):visible_leaks.append({'number':q['number'],'path':loc,'pattern':pattern})
   if key=='type' and value=='figure':pass
  blocks=list(q['stem'])+sum(q['options'].values(),[])+[b for m in q['materials'] for b in m['blocks']]
  for b in blocks:
   if b.get('type')=='figure':
    path=Path(b['path']);figures.add(path.as_posix())
    ensure(not path.is_absolute() and '..' not in path.parts,f'Q{q["number"]}: unnormalized figure path')
    ensure((ROOT/path).is_file(),f'Q{q["number"]}: missing figure {path}')
 ensure(not metadata_leaks,'Pupil JSON contains answer/source metadata')
 ensure(not visible_leaks,'Pupil visible blocks contain detected answer/source markers or replacement glyphs')
 REPORT['checks']['pupil_projection']={'question_count':len(qs),'forbidden_metadata_leaks':metadata_leaks,'visible_source_or_answer_markers':visible_leaks,'unique_existing_figure_files':len(figures),'figure_paths':sorted(figures),'asset_addressing_note':'图片path是必要资源地址，可含源库目录名；没有把其当作题面来源说明。'}

 # Ensure the source banks and source assets are clean relative to checked-out git HEAD.
 source_dirs=['模考','江浙行测_AI题库','国考','广东/行测/2022-2026','学习资料/政治理论常识']
 git_status=subprocess.run(['git','status','--porcelain','--untracked-files=all','--',*source_dirs],cwd=ROOT,text=True,capture_output=True)
 ensure(git_status.returncode==0 and not git_status.stdout.strip(),'Source-bank directories have tracked or untracked modifications')
 REPORT['checks']['source_git_status']={'checked_directories':source_dirs,'command_exit_code':git_status.returncode,'changes':git_status.stdout.splitlines(),'unmodified':git_status.returncode==0 and not git_status.stdout.strip(),'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()}

 # Actually execute the existing checks; qualify their input scope accurately.
 execute(PAPER/'编辑底稿/quant_data_check.py')
 quant=read(PAPER/'编辑底稿/quant_data_check.json')
 ensure(quant['input_file']==rel(PAPER/'selection.json'),'Numeric check did not read canonical selection')
 ensure(quant['summary']['question_count']==35 and quant['summary']['passed'],'35-question numeric check did not pass')
 REPORT['checks']['numeric_execution']={'input':quant['input_file'],'scope_numbers':list(range(31,46))+list(range(71,91)),'summary':quant['summary'],'report_file':rel(PAPER/'编辑底稿/quant_data_check.json'),'report_sha256':sha(PAPER/'编辑底稿/quant_data_check.json')}
 execute(PAPER/'编辑底稿/reasoning_verify.py')
 reasoning=read(PAPER/'编辑底稿/reasoning_verification.json')
 module=read(PAPER/'编辑底稿/reasoning.json')
 equivalent=[r['number'] for r in module if effective(r)==effective(by[r['number']])]
 full_equal=[r['number'] for r in module if r==by[r['number']]]
 changed=[r['number'] for r in module if r['number'] not in equivalent]
 ensure(reasoning.get('result')=='PASS','Reasoning verification did not pass')
 ensure(not changed,'Reasoning verification module payload differs from canonical; cannot transfer its result')
 REPORT['checks']['reasoning_execution']={'actual_input':rel(PAPER/'编辑底稿/reasoning.json'),'actual_input_scope':'独立模块稿，不是直接读取selection.json','module_sha256':sha(PAPER/'编辑底稿/reasoning.json'),'canonical_full_row_equal_numbers':full_equal,'canonical_effective_question_and_answer_equal_numbers':equivalent,'canonical_payload_differences':changed,'meaning':'已运行模块核验，且另比对模块稿与当前统一稿的题面、答案、源ID；相等部分可对应当前稿。脚本自身只对选定逻辑/图形题作枚举或像素/构造验证，不能称20题全部完成程序穷举。','programmed_content_check_keys':[k for k in reasoning['checks'] if k!='integrity'],'report_file':rel(PAPER/'编辑底稿/reasoning_verification.json'),'report_sha256':sha(PAPER/'编辑底稿/reasoning_verification.json'),'result':reasoning['result']}

 # Supplement the initial D-only witness with explicit four-option geometry.
 execute(HERE/'q50_spatial_review.py')
 spatial=read(HERE/'q50_spatial_review.json')
 possible=[key for key,value in spatial['options'].items() if value['solution_count']>0]
 ensure(spatial['source_id']==by[50]['source_id'] and possible==[by[50]['answer']],'Q50 spatial supplement disagrees with canonical question/answer')
 ensure(spatial['image_sha256']==sha(ROOT/'江浙行测_AI题库/images/original/352.png'),'Q50 supplement image fingerprint mismatch')
 REPORT['checks']['Q50_spatial_supplement']={'source_id':spatial['source_id'],'rotation_count':spatial['rotation_count'],'solutions_by_option':{k:v['solution_count'] for k,v in spatial['options'].items()},'canonical_answer':by[50]['answer'],'unique_viable_option':possible,'report_file':rel(HERE/'q50_spatial_review.json'),'report_sha256':sha(HERE/'q50_spatial_review.json'),'interpretation_limit':spatial['image_interpretation_limit']}

 # Retain other papers' ledger entries exactly, including their unknown practice status.
 ledger_path=PROJECT/'用题登记.jsonl';ledger=lines(ledger_path)
 ledger_previous={p:[x for x in ledger if x['paper_id']==p] for p in ['M01','M02']}
 head_ledger_raw=subprocess.check_output(['git','show','HEAD:'+rel(ledger_path)],cwd=ROOT,text=True)
 head_ledger=[json.loads(l) for l in head_ledger_raw.splitlines() if l.strip()]
 preserved={p:ledger_previous[p]==[x for x in head_ledger if x['paper_id']==p] for p in ['M01','M02']}
 ensure(all(preserved.values()),'M01/M02 ledger entries changed from HEAD')
 own=[x for x in ledger if x['paper_id']=='M03']
 ensure(len(own)==90 and sorted(x['number'] for x in own)==list(range(1,91)),'M03 ledger does not contain exactly 90 unique question numbers')
 for entry in own:
  n=entry['number'];q=qmap[n]
  payload=json.dumps({'stem':q['stem'],'options':q['options'],'materials':q['materials']},ensure_ascii=False,sort_keys=True)
  ensure(entry['source_id']==by[n]['source_id'] and entry['content_sha256']==hashlib.sha256(payload.encode()).hexdigest(),f'Ledger content mismatch Q{n}')
  ensure(entry['status']=='reserved_for_review' and entry['user_done']=='unknown',f'Ledger practice/review state inappropriate Q{n}')
 REPORT['checks']['ledger']={'total_records':len(ledger),'paper_counts':dict(collections.Counter(x['paper_id'] for x in ledger)),'M01_M02_entries_preserved_from_HEAD':preserved,'M03_count':len(own),'M03_status':'reserved_for_review','user_done':'unknown','content_fingerprints_match':True}

 source_registry=lines(PAPER/'来源登记.jsonl')
 ensure(len(source_registry)==90 and [r['number'] for r in source_registry]==list(range(1,91)),'Source registry numbering incomplete')
 for r in source_registry:
  n=r['number'];ensure(r['source_id']==by[n]['source_id'] and r['editor_answer']==by[n]['answer'] and r.get('source_answer')==by[n].get('source_answer'),f'Source registry inconsistent Q{n}')
 REPORT['checks']['source_registry']={'count':len(source_registry),'keys_match_canonical':True}

 # Re-run builder after all checks and compare bytes, not just row counts.
 outputs=[PAPER/name for name in ['题本_待审.md','题目.jsonl','答案与解析_待审.md','来源登记.jsonl','选题记录.md','核验报告.json']]+[ledger_path]
 before={rel(p):sha(p) for p in outputs}
 execute(PAPER/'build_m03.py')
 after={rel(p):sha(p) for p in outputs}
 changed_outputs=[p for p in before if before[p]!=after[p]]
 ensure(not changed_outputs,'Builder outputs differ between repeated runs')
 ensure(all(sha(PAPER/name)==digest for name,digest in start_inputs.items()),'Canonical input or builder changed during verification')
 build_report=read(PAPER/'核验报告.json')
 ensure(build_report['content_validation']=='PASS' and not build_report['errors'],'Canonical build report is not PASS')
 REPORT['checks']['reproducible_build']={'output_files_checked':len(outputs),'changed_outputs':changed_outputs,'byte_identical':not changed_outputs,'output_sha256':after,'canonical_inputs_unchanged_during_check':all(sha(PAPER/name)==digest for name,digest in start_inputs.items())}
 REPORT['checks']['current_review_status']={'external_review':cfg.get('external_review'),'printing_status':cfg.get('printing_status'),'print_ready':build_report['print_ready'],'science_Q70_corrected_answer':by[70]['answer'],'independent_reports_are_internal':True}
 ensure(by[70]['answer']=='B','The reviewed Q70 correction has not reached canonical selection')
 REPORT['errors']=ERRORS
 REPORT['result']='PASS' if not ERRORS else 'FAIL'
 OUT.write_text(json.dumps(REPORT,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'result':REPORT['result'],'questions':len(rows),'exact_source_objects':len(source_preserved),'source_keys_available':len(comparisons),'source_keys_matching':sum(x['matches'] for x in comparisons),'numeric_questions':quant['summary']['question_count'],'reasoning_canonical_payload_matches':len(equivalent),'unique_figures':len(figures),'rebuild_byte_identical':not changed_outputs,'errors':ERRORS},ensure_ascii=False))
 if ERRORS:raise SystemExit(1)

if __name__=='__main__':
 try:main()
 except Exception as exc:
  REPORT['errors']=ERRORS+[f'{type(exc).__name__}: {exc}'];REPORT['result']='FAIL'
  OUT.write_text(json.dumps(REPORT,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  raise

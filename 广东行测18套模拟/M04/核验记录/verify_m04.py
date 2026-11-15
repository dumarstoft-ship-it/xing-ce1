#!/usr/bin/env python3
"""交付门槛：绑定当前题面、溯源、旧卷保全、内部审读及最终PDF。"""
import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

HERE=Path(__file__).resolve().parent
PAPER=HERE.parent
PROJECT=PAPER.parent
REPO=PROJECT.parent
def read(path):return json.loads(path.read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def lines(path):return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO).decode()

cfg=read(PAPER/'paper.json')
rows=read(PAPER/'selection.json')
q=lines(PAPER/'题目.jsonl')
assert [r['number'] for r in rows]==list(range(1,91))
assert [r['number'] for r in q]==list(range(1,91))
assert len({r['source_id'] for r in rows})==90
assert dict(collections.Counter(x['section'] for x in q))==cfg['completed_section_counts']
assert [x['question_type'] for x in q[:10]]==['true_false']*4+['single_choice']*4+['multiple_choice']*2
allowed={'id','number','section','subtype','question_type','stem','options','options_mode','materials'}
assert all(set(x)==allowed for x in q)
assert all(not any(k in x for k in ('answer','analysis','source_id','difficulty','selection_reason')) for x in q)

assembly=read(HERE/'assembly_manifest.json')
assert assembly['selection_sha256']==sha(PAPER/'selection.json')
for rec in assembly['inputs']:
 assert rec['sha256']==sha(PAPER/rec['path']),rec['path']

spec=importlib.util.spec_from_file_location('m04_builder',PAPER/'build_m04.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
banks={}
for r in rows:
 sf=b.source_file(r)
 if sf and sf not in banks:
  banks[sf]={z.get('id',z.get('question_id')):z for z in lines(REPO/sf)}
 if sf:
  assert banks[sf][r['source_id']]==r['source_question'],r['source_id']
 else:
  assert r['source_bank']=='editor_original' and r.get('source_question') is None
 if r.get('source_answer'):
  assert r['source_answer']==r['answer'],r['number']

baseline=cfg['source_snapshot']
old_ledger=[json.loads(x) for x in git('show',baseline+':广东行测18套模拟/用题登记.jsonl').splitlines() if x.strip()]
new_ledger=lines(PROJECT/'用题登记.jsonl')
assert [x for x in new_ledger if x['paper_id']!='M04']==old_ledger
assert len([x for x in new_ledger if x['paper_id']=='M04'])==90
assert {x['source_id'] for x in old_ledger}.isdisjoint(r['source_id'] for r in rows)
assert all(x.get('user_done')=='unknown' and x['status']=='reserved_for_review' for x in new_ledger if x['paper_id']=='M04')
changed=git('diff','--name-only',baseline).splitlines()
allowed_tracked={'广东行测18套模拟/README.md','广东行测18套模拟/用题登记.jsonl'}
# --name-only默认转义中文；用-z读取原路径，避免把转义输出当成文件名。
changed_z=git('-c','core.quotePath=false','diff','--name-only','-z',baseline).split('\0')
assert all(not p or p in allowed_tracked or p.startswith('广东行测18套模拟/M04/') for p in changed_z),changed_z

exposure=read(HERE/'prior_exposure_full90_scan.json')
assert exposure['question_count']==90 and exposure['baseline_commit']==baseline
for name,digest in exposure['module_file_sha256'].items():
 assert sha(PAPER/'编辑底稿'/name)==digest,name
for result in exposure['results']:
 assert not result['reserved_source_id_matches']
 assert not result['old_graphic_source_id_match']
 assert not result['source_id_reference_matches']
 assert not result['text_matches']

by_number={r['number']:r for r in rows}
reviewed={}
for filename,key,answerkey in [
 ('politics_independent_review.json','comparisons','independent_answer'),
 ('verbal_current_second_reader.json','items','independent_answer'),
 ('quant_independent_comparison.json','comparisons','independent_answer'),
 ('reasoning_science_independent_review.json','results','independent_answer'),
 ('data_independent_comparison.json','results','independent_answer')]:
 for result in read(HERE/filename)[key]:
  n=result['number'];assert result[answerkey]==by_number[n]['answer'],(filename,n)
  if 'source_id' in result:assert result['source_id']==by_number[n]['source_id']
  reviewed[n]=filename
assert set(reviewed)==set(range(1,91))-set(range(46,51))
assert read(HERE/'verbal_current_second_reader.json')['current_module_sha256']==sha(PAPER/'编辑底稿/verbal.json')
graphics=read(HERE/'graphical_second_review.json')
assert [x['number'] for x in graphics['results']]==list(range(46,51))
for x in graphics['results']:
 assert x['answer']==by_number[x['number']]['answer'] and x['result']=='PASS'
 for f in x['original_images']+x['final_images']:assert sha(REPO/f['path'])==f['sha256']
assert read(HERE/'data_material_consistency.json')['material_internal_contradiction_found'] is False
assert read(HERE/'reasoning_science_verification.json')['module_sha256']==sha(PAPER/'编辑底稿/reasoning_science.json')

printed=read(PAPER/'审阅排版/打印核验.json')
pdf=PAPER/'审阅排版/M04_题本_打印版.pdf'
assert printed['pdf_sha256']==sha(pdf)
assert printed['question_jsonl_sha256']==sha(PAPER/'题目.jsonl')
assert printed['all_pages_actually_viewed'] and not printed['open_visual_issues']
assert set().union(*(set(v) for v in printed['actual_visual_coverage'].values()))==set(range(1,33))
for name in ['pdf_verbal_visual_review.json','pdf_reasoning_visual_review.json']:
 assert printed['pdf_sha256'] in (HERE/name).read_text(),name
assert cfg['external_review']=='not_started' and not printed['formal_finalized']
for md in [PAPER/'README.md',PAPER/'题本_待审.md',PAPER/'答案与解析_待审.md',PAPER/'审阅排版/README.md']:
 for target in re.findall(r'\]\(([^)]+)\)',md.read_text()):
  if not target.startswith(('https:','http:','#')):assert (md.parent/target).exists(),(md.name,target)

outputs=['selection.json','题目.jsonl','题本_待审.md','答案与解析_待审.md','来源登记.jsonl','选题记录.md','核验报告.json']
before={name:sha(PAPER/name) for name in outputs}
subprocess.run(['python',str(PAPER/'build_m04.py')],check=True,capture_output=True)
assert before=={name:sha(PAPER/name) for name in outputs},'同一底稿重复构建不稳定'
report={
 'paper_id':'M04','version':cfg['version'],'result':'PASS','question_count':90,
 'source_objects_preserved':75,'original_questions':15,'source_keys_available_and_matching':24,
 'second_reader_answers_matching':85,'graphic_review_count':5,'source_exposure_hits':0,
 'exposure_corpus_files':exposure['corpus_files'],'prior_ledger_rows_unchanged':len(old_ledger),
 'source_snapshot':baseline,'old_papers_and_source_banks_modified':False,
 'deterministic_build':True,'print_pages':32,'print_pdf_sha256':sha(pdf),'student_data_sha256':sha(PAPER/'题目.jsonl'),
 'external_review':'not_started','formal_finalized':False,
 'editorial_followups':[
  '第11题A按独立审阅建议去掉可机械排除的绝对化表述；不改变法条适用和C答案。',
  '第43题B明确改编为2/5；原始对象及改前独立核验保留，当前样本空间枚举已重新通过。',
  '第60、64题分段和第67题图注位置只改善呈现，独立推理结论不变。',
  '资料第二读者80、86初始理由的对象/单位误记另有勘误，源编辑解析及答案原本正确。',
 ],
 'limitations':['内部答案一致不是外部审核','广东模考原始PDF本轮未取得','曝光检查不覆盖仓库外所有做题历史'],
 'output_sha256':before,
}
(HERE/'交付核验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('M04交付核验PASS：90题，75源对象保全，85题二读同键+5图推复核，旧270行登记不变，32页PDF已核对。')

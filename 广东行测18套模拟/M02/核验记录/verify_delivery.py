#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,re,subprocess,sys,copy
HERE=Path(__file__).resolve().parents[1];PROJECT=HERE.parent;ROOT=HERE.parents[1]
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def jl(p):return [json.loads(s) for s in p.read_text(encoding='utf-8').splitlines() if s.strip()]
def sha(b):return hashlib.sha256(b).hexdigest()
def canon(x):return sha(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
rows=load(HERE/'selection.json');questions=jl(HERE/'题目.jsonl');m01=load(PROJECT/'M01/selection.json')
assert len(rows)==len(questions)==90 and [r['number'] for r in rows]==list(range(1,91))
assert canon(load(HERE/'editorial.json'))=='a8e362a6f502f4f9ae2024975d45ae0b0b691ad5630b87b7089d22ba8bc374d9','Editorial transport mismatch'
assert canon(load(HERE/'politics_original.json'))=='1237f5bee873a4fe3e1069c2474fbaad42ce9a0e468e100f18a722fa90f256c7','Politics transport mismatch'
assert canon(rows)=='c1e1caf8ff62db5016b330277946dc8cb754879a85f843e035cf62ec21b3a6ef','Assembled selection differs from locally checked 90-question draft'
assert len({r['source_id'] for r in rows})==90
collisions=sorted({r['source_id'] for r in rows}&{r['source_id'] for r in m01});assert not collisions
banks={};hashes={}
for p in {r['source_file'] for r in rows if r.get('source_file')}:
 hashes[p]=sha((ROOT/p).read_bytes());banks[p]={x.get('id',x.get('question_id')):x for x in jl(ROOT/p)}
assert all(r['source_question']==banks[r['source_file']][r['source_id']] for r in rows if r.get('source_question'))
checkpoint=load(HERE/'选编断点_75题.json')['rows_number_source_answer']
assert all((n,sid,a)==(rows[n-1]['number'],rows[n-1]['source_id'],rows[n-1]['answer']) for n,sid,a in checkpoint)
assert sum(r.get('source_answer') is not None for r in rows)==28
assert all(r['source_answer']==r['answer'] for r in rows if r.get('source_answer'))
assert all('answer' not in q for q in questions)
assets=set()
def strip_block(b):
 if b['type']=='figure':
  assets.add(b['path']);return {'type':'figure','sha256':sha((ROOT/b['path']).read_bytes())}
 if b['type']=='text':return {'type':'text','text':re.sub(r'\s+','',b['text'])}
 return {k:v for k,v in b.items() if k in ['type','title','headers','rows','notes']}
def signature(q):
 return canon({'stem':[strip_block(b) for b in q['stem']],'options':{k:[strip_block(b) for b in v] for k,v in q['options'].items()},'materials':[[strip_block(b) for b in m['blocks']] for m in q['materials']]})
sigs={signature(q):q['number'] for q in questions};m02assets=set(assets);assert len(sigs)==90
m01sigs={signature(q):q['number'] for q in jl(PROJECT/'M01/题目.jsonl')}
exact_matches=[{'M02':sigs[k],'M01':m01sigs[k]} for k in set(sigs)&set(m01sigs)];assert not exact_matches
assert len(m02assets)==13
ledger=jl(PROJECT/'用题登记.jsonl');m2ledger=[r for r in ledger if r['paper_id']=='M02'];assert len(m2ledger)==90
old=subprocess.check_output(['git','show','HEAD:广东行测18套模拟/用题登记.jsonl'],cwd=ROOT,text=True)
old=[json.loads(s) for s in old.splitlines() if s.strip()]
assert [r for r in ledger if r['paper_id']!='M02']==[r for r in old if r['paper_id']!='M02'],'Other paper ledger changed'
subprocess.run(['git','diff','--exit-code','--','广东行测18套模拟/M01'],cwd=ROOT,check=True)
files=['selection.json','paper.json','题目.jsonl','题本_待审.md','答案与解析_待审.md','来源登记.jsonl','核验报告.json','选题记录.md']
def outputhashes():return {n:sha((HERE/n).read_bytes()) for n in files}
before=outputhashes();subprocess.run([sys.executable,str(HERE/'build_m02.py')],check=True);assert before==outputhashes()
structure=load(HERE/'核验报告.json');assert structure['content_validation']=='PASS' and not structure['missing_numbers']
assert structure['actual_count']==90 and structure['external_review']=='pending_claude' and not structure['print_ready']
text=(HERE/'答案与解析_待审.md').read_text(encoding='utf-8')
count=len(re.findall(r'^\| (?:\d+ \| ?)+\n\| (?:--- \| ?)+\n\|',text,re.M));assert count==9
numeric=load(HERE/'核验记录/numeric_checks.json');assert numeric['status']=='PASS' and len(numeric['checks'])==43
diagrams=load(HERE/'核验记录/diagram_checks.json');assert diagrams['Q48_enclosed_regions']==[5,4,5,4,5,5,4,4,5]
source_edits=[r['number'] for r in rows if any(e.get('type') in ['stem_clarification','adapted_question'] for e in r['edits'])]
assert source_edits==[38,43,56,67,68,71,72]
report={'status':'PASS','paper_id':'M02','version':'0.1.0','question_count':90,'original_politics_and_knowledge':15,'selected_source_records_preserved':75,'checkpoint_ids_and_answers_preserved':75,'source_reference_answers_matched':28,'M01_source_id_collisions':collisions,'M01_exact_normalized_question_matches':exact_matches,'M01_files_unchanged':True,'other_papers_ledger_preserved':True,'M02_ledger_entries':90,'material_group_count':4,'unique_question_figures':13,'numeric_logical_check_groups':43,'answer_table_blocks':count,'source_edit_questions':source_edits,'rebuild_identical':True,'output_sha256':outputhashes(),'source_file_sha256':hashes,'figure_sha256':{p:sha((ROOT/p).read_bytes()) for p in sorted(m02assets)},'external_review':'pending_claude','print_ready':False,'limits':['编辑已见断点答案，本轮不是盲解；Claude尚未独立审核。','同ID与规范化题面重复检查不等于掌握用户完整做题史，也不等于语义相似题检测。','题库保留的13幅题图已实际查看；未逐页核对全部原始PDF。','资料原图转写成表格的部分尚未还原为原印刷图；经济材料按题给口径作答，不冒称已审核统计报告。']}
(HERE/'核验记录/交付核验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ['status','question_count','source_reference_answers_matched','unique_question_figures','rebuild_identical','external_review','print_ready']},ensure_ascii=False))

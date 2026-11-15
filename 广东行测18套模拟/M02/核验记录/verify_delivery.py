from pathlib import Path
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

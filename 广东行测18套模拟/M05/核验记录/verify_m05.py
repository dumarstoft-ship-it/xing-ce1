#!/usr/bin/env python3
"""Source fidelity, reservation/exposure checks and executable delivery manifest."""
from pathlib import Path
import json,hashlib,re,collections,subprocess,sys
D=Path(__file__).resolve().parents[1];P=D.parent;R=D.parents[1]
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def jl(p):return [json.loads(s) for s in p.read_text(encoding='utf-8').splitlines() if s.strip()]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def norm(s):return re.sub(r'\s+','',s)
def textvalue(x):
 if isinstance(x,str):return x
 if isinstance(x,list):return '\n'.join(b['text'] for b in x if b.get('type')=='text')
 return ''
rows=load(D/'selection.json');Q={q['number']:q for q in rows};students=jl(D/'题目.jsonl');cfg=load(D/'paper.json')
assert len(rows)==90 and [q['number'] for q in rows]==list(range(1,91))
assert len({q['source_id'] for q in rows})==90 and cfg['version']=='0.1.0'
assert len(students)==90 and all('answer' not in q for q in students)
assert load(D/'核验报告.json')['content_validation']=='PASS'
excluded=set(load(D/'excluded_ids.json'));assert not (excluded&{q['source_id'] for q in rows})
JZ='江浙行测_AI题库/questions.jsonl';MOCK='模考/2026下半年广东卷_16-33季_AI可读/全部题目.jsonl';JA='江浙行测_AI题库/answers.jsonl'
banks={JZ:{q['question_id']:q for q in jl(R/JZ)},MOCK:{q['id']:q for q in jl(R/MOCK)}}
answers={q['question_id']:q['correct_answer'] for q in jl(R/JA)}
sys.path.insert(0,str(D));import build_m05 as builder
checks=[];references=[];images={}
for q,student in zip(rows,students):
 n=q['number'];sf=q['source_file']
 if sf:
  raw=banks[sf][q['source_id']];assert raw==q['source_question'],(n,'raw source changed')
  assert 'stem_override' not in q and 'options' not in q,(n,'source prose overridden')
  # Material differences allowed only the recorded transcription hint removal.
  if 76<=n<=80:
   import copy
   expected=copy.deepcopy(raw['material']);note=expected['blocks'][0].pop('notes')
   assert note=='同比增长列为绝对增量，原表未标百分号。' and q['materials']==[expected]
  else:assert 'materials' not in q,(n,'unexpected material override')
  normal=builder.normalize(q)
  assert normal['stem']==student['stem'] and normal['options']==student['options'],(n,'student/source mismatch')
  assert [m['blocks'] for m in normal['materials']]==[m['blocks'] for m in student['materials']],n
  if q['source_id'] in answers:
   assert answers[q['source_id']]==q['answer'];references.append({'number':n,'source_id':q['source_id'],'reference':answers[q['source_id']]})
  checks.append({'number':n,'source_object_exact':True,'stem_options_exact_after_asset_path_normalization':True,'internal_spaces_and_newlines_retained':True,'material_exception':'remove_transcription_hint_only' if 76<=n<=80 else None})
 for path in builder.asset_paths(student):images[path]=sha(R/path)
assert len(references)==20 and len(images)==12
# Complete material sets and exact number/type counts.
groups=collections.defaultdict(list)
for q in students:
 if q['section']=='资料分析':
  assert len(q['materials'])==1
  groups[q['materials'][0]['id']].append(q['number'])
assert sorted(groups.values())==[list(range(71,76)),list(range(76,81)),list(range(81,86)),list(range(86,91))]
assert [Q[n]['question_type'] for n in range(1,11)]==['true_false']*4+['single_choice']*4+['multiple_choice']*2
# Prior-paper shared materials cannot reappear through an adjacent question ID.
prior=[]
for number in range(1,5):
 for f in (P/f'M{number:02d}').rglob('selection.json'):
  prior.extend(load(f))
prior_ids={x['source_id'] for x in prior};assert not(prior_ids & {x['source_id'] for x in rows})
for q in rows[15:]:
 for m in q['source_question'].get('materials',[]):assert not(set(m.get('question_ids',[]))&prior_ids),(q['number'],'shared material already used')
# Exact long-prose comparison to earlier paper/historical selections.
prior_text=[]
for q in prior:
 s=q.get('source_question') or {};st=q.get('stem_override',q.get('stem',s.get('stem','')))
 t=norm(textvalue(st))
 if len(t)>=65:prior_text.append((q['source_id'],t))
prior_hits=[]
for q in rows[15:]:
 t=norm(textvalue(q['source_question']['stem']))
 if len(t)>=65:
  for sid,s in prior_text:
   if t==s or (len(t)>120 and t[:100] in s):prior_hits.append([q['number'],sid])
assert not prior_hits,prior_hits
# User-facing old drill text: do not scan source banks as exposure.
old_files=[]
for folder in ['广东行测24天集训','习题本/图推']:
 for f in (R/folder).rglob('*'):
  if f.is_file() and f.suffix in {'.md','.txt','.json','.jsonl','.html'} and '/核验记录/' not in str(f):old_files.append(f)
texts=[(str(f.relative_to(R)),norm(f.read_text(encoding='utf-8',errors='replace'))) for f in old_files]
hits=[]
for q in rows[15:]:
 s=q['source_question'];needle=norm(textvalue(s['stem']));needles=[q['source_id']]
 if len(needle)>70 and not 46<=q['number']<=50:needles.append(needle[:65])
 for m in s.get('materials',[]):
  t=norm(m.get('content',''))
  if len(t)>65:needles.append(t[:65])
 for fn,body in texts:
  if any(n in body for n in needles):hits.append({'number':q['number'],'source_id':q['source_id'],'path':fn})
assert not hits,hits
# Source image byte reuse check against prior source registrations.
prior_image_hashes=set()
for number in range(1,5):
 f=P/f'M{number:02d}'/'来源登记.jsonl'
 for q in jl(f):
  for path in q.get('asset_paths',[]):
   if (R/path).is_file():prior_image_hashes.add(sha(R/path))
assert not(set(images.values())&prior_image_hashes),'exact image already used in prior paper'
ledger=jl(P/'用题登记.jsonl');current=[q for q in ledger if q['paper_id']=='M05'];assert len(current)==90
assert len(ledger)==450 and {q['source_id'] for q in current}=={q['source_id'] for q in rows}
# Never infer independent review from one editor's several scripts.
math=load(D/'核验记录/数学逻辑复算.json');graphics=load(D/'核验记录/图形核验.json')
assert math['status']=='PASS' and math['quantitative_and_data_questions']==35 and graphics['status']=='PASS'
keyfiles=['paper.json','selection.json','originals.json','choices.json','editorial.json','题目.jsonl','题本_待审.md','答案与解析_待审.md','来源登记.jsonl']
report={'paper_id':'M05','version':'0.1.0','status':'PASS','question_count':90,'source_reference_count':20,
 'editor_without_source_key_count':70,'source_fidelity':checks,'reference_matches':references,'material_groups':dict(groups),
 'exclude_id_count':len(excluded),'old_drill_text_files_scanned':len(old_files),'old_exposure_hits':hits,'prior_paper_text_hits':prior_hits,
 'original_asset_count':len(images),'original_asset_sha256':images,'source_file_sha256':{sf:sha(R/sf) for sf in [JZ,JA,MOCK]},
 'output_sha256':{f:sha(D/f) for f in keyfiles},'use_ledger_rows_after_local_build':len(ledger),
 'external_review':'not_started','print_ready':False,
 'limits':['没有独立第二读者；20题参考键一致不等于其余70题官方有键。','原模考PDF未取得；表格转写仅做内部计算和单位核验。','第80题D只有122辆艘余量，表格原图须优先检查。','第24、65题按源参考键取最佳项，解释边界保留给外审。','第50题截面判断的原图到模型环节须人工复核。','没有最终PDF；不借用前卷打印检查。','用户已确认源卷未做过；旧专项扫描仅覆盖本地可读文本与已登记图推索引。']}
dump(D/'核验记录/交付核验.json',report)
print(json.dumps({'status':'PASS','questions':90,'reference_matches':20,'old_drill_files':len(old_files),'source_fidelity':75,'original_assets':len(images)},ensure_ascii=False))

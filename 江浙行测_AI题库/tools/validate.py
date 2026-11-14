"""Validate the delivered corpus using only Python's standard library."""
from pathlib import Path
import json,re,collections,hashlib
ROOT=Path(__file__).resolve().parents[1]
def read(name):return [json.loads(s) for s in (ROOT/name).read_text().splitlines() if s.strip()]
def main():
 qs=read('questions.jsonl');answers=read('answers.jsonl');materials=read('materials.jsonl');manifest=json.loads((ROOT/'manifest.json').read_text())
 qmap={q['question_id']:q for q in qs};amap={a['question_id']:a for a in answers};mmap={m['material_id']:m for m in materials}
 assert len(qmap)==len(qs)==1215
 assert len(amap)==len(answers)==len(qs) and set(amap)==set(qmap)
 assert len(mmap)==18 and len(manifest['papers'])==14
 excluded={(x['paper_id'],x['original_number']) for x in manifest['excluded_questions']}
 assert excluded=={('ZJ2024',41),('ZJ2025',38),('ZJ2026',40)}
 assert not any((q['paper_id'],q['original_number']) in excluded for q in qs)
 for q in qs:
  assert q['stem'].strip(),q['question_id']
  assert set(q['options'])==set('ABCD'),q['question_id']
  assert all(v.strip() for v in q['options'].values()),q['question_id']
  assert q['section'] in ('数量关系','言语理解与表达','判断推理')
  assert not(q['section']=='言语理解与表达' and q['figures']),q['question_id']
  assert q['source']['pdf_pages'] and min(q['source']['pdf_pages'])>=1
  assert set(q['material_ids'])<=set(mmap)
  assert [m['material_id'] for m in q['materials']]==q['material_ids']
  assert q['source']['commit']==manifest['source_commit']
  a=amap[q['question_id']]
  assert a['correct_answer'] in [None,'A','B','C','D']
  if 'source_missing' in q['quality_flags']:assert a['correct_answer'] is None
  if 'source_answer_conflict' in a['quality_flags']:assert a['correct_answer'] is None
 for paper in manifest['papers']:
  qq=[q for q in qs if q['paper_id']==paper['paper_id']]
  assert len(qq)==paper['question_slots']
  assert dict(collections.Counter(q['section'] for q in qq))==paper['section_counts']
  path=ROOT/'papers'/paper['province']/f'{paper["year"]}_{paper["paper_type"]}'
  assert read(str((path/'questions.jsonl').relative_to(ROOT)))==qq
  assert read(str((path/'answers.jsonl').relative_to(ROOT)))==[amap[q['question_id']] for q in qq]
 allrecords=qs+answers+materials
 for r in allrecords:
  for f in r.get('figures',[]):
   assert (ROOT/f['path']).is_file(),f
   if f.get('code_hd'):
    for key in ['path','svg_path']:assert (ROOT/f['code_hd'][key]).is_file()
  text=json.dumps(r,ensure_ascii=False)
  assert '[[FIGURE' not in text and '[[CROP' not in text
  assert '\ufffd' not in text
  assert not any(0xE000<=ord(c)<=0xF8FF for c in text)
  assert '/Users/' not in text
 for md in ROOT.rglob('*.md'):
  for link in re.findall(r'\]\(([^)]+)\)',md.read_text()):
   if re.match(r'https?://|#',link):continue
   assert (md.parent/link.split('#')[0]).resolve().is_file(),(md,link)
 # Regressions checked against actual source pages: figure-at-number boundaries,
 # inline fractions, explicit answer conflicts, and shared passage associations.
 assert '|1|8|18|14|4|' in qmap['ZJ2020-B卷-006']['stem']
 assert '|1|1|2|3|9|' in qmap['ZJ2020-B卷-010']['stem']
 assert '2，1，1，3/2，3，15/2' in qmap['ZJ2025-A类-052']['stem']
 assert '√3，√18，√81，√324' in amap['JS2024-A类-049']['analysis']
 assert '32/7' not in amap['JS2020-A类-049']['analysis']
 assert '32/7' in amap['JS2020-A类-050']['analysis']
 assert qmap['JS2022-A类-104']['material_ids']==qmap['JS2022-A类-105']['material_ids']!=[]
 assert amap['JS2023-A类-033']['correct_answer'] is None
 assert amap['JS2024-A类-046']['correct_answer'] is None
 assert sum('source_missing' in q['quality_flags'] for q in qs)==11
 assert sum('source_omission' in q['quality_flags'] for q in qs)==14
 assert sum(a['correct_answer'] is not None for a in answers)==1118
 print(json.dumps({'status':'PASS','questions':len(qs),'answers':len(answers),'materials':len(materials),'papers':14,'excluded_verbal_image_questions':3,'missing_question_placeholders':11,'source_answer_conflicts':2,'answers_with_choice':1118},ensure_ascii=False,indent=2))
if __name__=='__main__':main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate completeness, answer semantics, material links and all PNG hashes."""
import collections,hashlib,json,re,struct
from pathlib import Path
ROOT=Path(__file__).parent
EXPECTED={'GD2022-XZ':100,'GD2022-XJ':100,'GD2023-XZ':100,'GD2023-XJ':100,'GD2024':90,'GD2025':90,'GD2026':90}

def read(p):return [json.loads(s) for s in p.read_text(encoding='utf8').splitlines() if s.strip()]
def main():
 records=read(ROOT/'all.jsonl');assert len(records)==670
 assert len({r['id'] for r in records})==670
 assets=json.loads((ROOT/'assets-manifest.json').read_text());manifest={a['id']:a for a in assets};assert len(manifest)==154
 assert collections.Counter(a['method'] for a in assets)=={'pdf_render_crop':147,'code_redraw':7}
 assert len([a for a in assets if a['transcription']])==33
 assert collections.Counter(r['answer']['status'] for r in records)=={'known':578,'disputed':2,'missing':90}
 refs=set();materials={};paper_concat=[]
 for paper,count in EXPECTED.items():
  rs=read(ROOT/(paper+'.jsonl'));paper_concat.extend(rs)
  assert len(rs)==count and [r['question_number'] for r in rs]==list(range(1,count+1))
  md=(ROOT/(paper+'.md')).read_text();assert len(re.findall(r'^### 第 \d+ 题$',md,re.M))==count
  assert all(r['paper_id']==paper for r in rs)
  for r in rs:
   assert r['stem'] and r['stem'] in md and '\ufffd' not in json.dumps(r,ensure_ascii=False)
   assert r['source']['question_pages'] and all(p>0 for p in r['source']['question_pages'])
   a=r['answer'];typ=r['question_type']
   assert a['status'] in ['known','disputed','missing']
   assert (a['status']=='missing')==(r['year']==2026)
   assert len(a['values'])==({'known':1,'disputed':2,'missing':0}[a['status']])
   if typ=='true_false':
    assert r['options']==[]
    assert all(v in [['正确'],['错误']] for v in a['values'])
   else:
    assert [o['label'] for o in r['options']]==list('ABCD')
    for o in r['options']:assert o['text'] or o['image_refs']
    for val in a['values']:
     assert val and len(set(val))==len(val) and all(x in 'ABCD' for x in val)
     assert len(val)>1 if typ=='multiple_choice' else len(val)==1
   images=list(r['figures']);material=r['material']
   if r['section']=='资料分析':assert material and r['question_number'] in material['question_numbers']
   if material:
    if material['id'] in materials:assert material==materials[material['id']]
    else:materials[material['id']]=material
    assert material['content'] and material['source_pages']
    images.extend(b for b in material['content'] if b['type']=='image')
   for image in images:
    asset=manifest[image['image_id']];assert image['path']==asset['path'] and image['method']==asset['method']
    assert image['path'] in md and image['transcription']==asset['transcription'];refs.add(image['image_id'])
   for option in r['options']:
    for ref in option['image_refs']:
     assert ref['image_id'] in {i['image_id'] for i in r['figures']}
     assert ref['label_in_image'] in [None,option['label']]
   assert not any('待用户' in n for n in r['notes'])
  for target in re.findall(r'\]\(([^)]+)\)',md):
   if not target.startswith(('https:','#')):assert (ROOT/target).exists(),target
 assert paper_concat==records and len(materials)==24
 assert sum(r['material'] is not None for r in records)==120
 assert refs==set(manifest)
 for a in assets:
  f=ROOT/a['path'];raw=f.read_bytes();assert raw[:8]==b'\x89PNG\r\n\x1a\n'
  assert hashlib.sha256(raw).hexdigest()==a['sha256'],a['id']
  assert struct.unpack('>II',raw[16:24])==(a['width'],a['height'])
 assert {str(f.relative_to(ROOT)) for f in (ROOT/'assets').rglob('*.png')}=={a['path'] for a in assets}
 disputed={r['id']:r['answer']['values'] for r in records if r['answer']['status']=='disputed'}
 assert disputed=={'GD2022-XZ-Q052':[['D'],['B']],'GD2022-XJ-Q047':[['D'],['B']]}
 print(json.dumps({'status':'PASS','papers':7,'questions':670,'materials':24,'questions_with_material':120,'images':154,'code_redrawn_images':7,'known_answers':578,'disputed_answers':2,'missing_answers':90},ensure_ascii=False))
if __name__=='__main__':main()

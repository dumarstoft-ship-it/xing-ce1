#!/usr/bin/env python3
"""Check the actual revision against its archived, independently reviewed base.

The diagram checks read the SVG, not just the renderer's intended inventory.
This does not replace human review of wording or final printed figures.
"""
from collections import Counter
from pathlib import Path
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent
PAPER=HERE.parent
ROOT=PAPER.parents[1]
NS={'s':'http://www.w3.org/2000/svg'}
def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def stable(v): return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def texts(blocks): return '\n'.join(b.get('text','') for b in blocks if b['type']=='text')

def main():
    baseline=read(PAPER/'历史版本/0.1.0/selection.json')
    rows=read(PAPER/'selection.json'); qs=[json.loads(l) for l in (PAPER/'题目.jsonl').read_text().splitlines()]
    by={r['number']:r for r in rows}; qb={r['number']:r for r in qs}
    manifest=read(HERE/'v020_revision_manifest.json')
    assert sha(PAPER/'历史版本/0.1.0/selection.json')==manifest['baseline_selection_sha256']
    assert sha(PAPER/'selection.json')==manifest['current_selection_sha256']
    for name,digest in manifest['patch_sha256'].items():
        assert sha(PAPER/'修订底稿'/name)==digest,name
    assert len(rows)==len(baseline)==len(manifest['questions'])==90
    for old,new,entry in zip(baseline,rows,manifest['questions']):
        assert old['number']==new['number']==entry['number']
        assert stable(old)==entry['before_sha256'] and stable(new)==entry['after_sha256']
        for key in ['answer','source_id','source_file','source_question','source_answer','section','question_type']:
            assert old.get(key)==new.get(key),(new['number'],key)
    checks={'baseline_and_revision_hashes':'PASS','all_90_answer_keys_unchanged':True,
            'source_objects_and_identifiers_unchanged':True}
    # These are regressions in the delivered, answer-free projection, not just
    # assertions about text sitting in an unapplied patch file.
    assert '，____，' in texts(qb[55]['stem'])
    t60=texts(qb[60]['stem']);t65=texts(qb[65]['stem'])
    assert '丁：乙不会成为大学教师。\n现在看来' in t60
    assert '正确的。\n根据上述信息' in t60
    assert '我还是不去了。”\n以下哪项' in t65
    assert '4 位' not in t60 and '30 年' not in t60
    # The current reasoning questions only change presentation, not any words,
    # numeric conditions or options used by the existing enumerations.
    def semantic_form(q):
        value=json.loads(json.dumps(q,ensure_ascii=False))
        def clean(v):
            if isinstance(v,str):
                return re.sub(r'\s','',v).replace('____','').replace('：',':').replace('—','-').replace('；','。')
            if isinstance(v,list): return [clean(x) for x in v]
            if isinstance(v,dict): return {k:clean(x) for k,x in v.items()}
            return v
        return clean(value)
    import importlib.util
    spec=importlib.util.spec_from_file_location('builder',PAPER/'build_m03.py');builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
    reasoning_equal=[]
    for n in range(46,66):
        assert semantic_form(builder.normalize(baseline[n-1]))==semantic_form(builder.normalize(by[n])),n
        reasoning_equal.append(n)
    checks['current_reasoning_conditions_and_options_preserved_numbers']=reasoning_equal
    checks['delivered_Q55_Q60_Q65_layout']='PASS'

    # Q35 geometry has its own measured audit; the figure chosen by the current
    # student payload must actually be the revision, not the historical image.
    f35=next(b for b in qb[35]['stem'] if b['type']=='figure')
    assert f35['path']=='广东行测18套模拟/M03/assets/q35_number_grid_v020.png'
    checks['Q35_revised_image_is_delivered']=True

    diagram=read(HERE/'v020_science_diagrams.json')
    for n in [67,68]:
        d=diagram[f'question_{n}']
        assert sha(ROOT/d['svg'])==d['svg_sha256'] and sha(ROOT/d['png'])==d['png_sha256']
        assert next(b for b in qb[n]['stem'] if b['type']=='figure')['path']==d['png']
    root67=ET.parse(ROOT/diagram['question_67']['svg']).getroot()
    root_old=ET.parse(ROOT/diagram['question_67']['source_svg']).getroot()
    wall=lambda root:next(p.attrib['d'] for p in root.findall('s:path',NS))
    assert wall(root67)==wall(root_old)
    launch=lambda root:next((float(c.attrib['cx']),float(c.attrib['cy'])) for c in root.findall('s:circle',NS))
    assert launch(root67)==launch(root_old)==(195,13)
    paths={p.attrib.get('id'):p.attrib['d'] for p in root67.findall('.//s:path',NS)}
    trajectories={}
    for letter in ['A','B']:
        coordinates=list(map(float,re.findall(r'-?\d+(?:\.\d+)?',paths['trajectory-'+letter])))
        x0,y0,cx,cy,x1,y1=coordinates
        assert cy==y0 and cx==(x0+x1)/2
        trajectories[letter]={'horizontal':x0-x1,'fall':y1-y0,'end':[x1,y1]}
    assert trajectories['A']['end']==[117,69] and trajectories['B']['end']==[137,84]
    assert trajectories['A']['fall']<trajectories['B']['fall'] and trajectories['A']['horizontal']>trajectories['B']['horizontal']
    # B stays to the right of the wall corner until after passing top height.
    x_at_top=195-58*((69-13)/(84-13))**0.5
    assert x_at_top>137
    assert by[67]['answer']=='B'
    checks['Q67_geometry']={'horizontal_initial_tangents':True,'same_landings_and_wall':True,'B_x_at_wall_top':x_at_top,'answer':'B'}

    root68=ET.parse(ROOT/diagram['question_68']['svg']).getroot()
    actual={'before':Counter(),'after':Counter()};atoms={'before':Counter(),'after':Counter()}
    for g in root68.findall('s:g',NS):
        stage=g.attrib.get('data-stage')
        if stage:
            composition=Counter()
            for c in g.findall('s:circle',NS):
                radius=float(c.attrib['r']);fill=c.attrib['fill']
                element='H' if radius==12 and fill=='white' else 'C' if radius==22 and fill=='white' else 'O' if radius==22 and fill=='url(#oxygen-hatch)' else None
                assert element is not None
                composition[element]+=1
            actual[stage][tuple(sorted(composition.items()))]+=1;atoms[stage].update(composition)
    expected={'before':Counter(),'after':Counter()};names={'碳':'C','氢':'H','氧':'O'}
    table=next(b for b in by[68]['source_question']['stem'] if b['type']=='table')
    for stage,composition,count in table['rows']:
        counts=tuple(sorted((names[element],int(n)) for n,element in re.findall(r'(\d+) 个(碳|氢|氧)原子',composition)))
        expected['before' if stage=='反应前' else 'after'][counts]+=int(count)
    assert actual==expected
    assert atoms['before']==atoms['after']==Counter(C=1,H=4,O=6)
    assert all(sum(count.values())==4 for count in actual.values())
    assert by[68]['answer']=='C'
    checks['Q68_visual_particle_inventory']={'matches_source_table':True,'before_atoms':dict(atoms['before']),'after_atoms':dict(atoms['after']),'molecules_per_stage':4,'remaining_O2':1,'answer':'C'}
    assert '箭头从被捕食者指向捕食者' in texts(qb[69]['stem'])
    assert '第五营养级' in texts(qb[69]['options']['B'])
    assert any('箭头从被捕食者指向捕食者' in e.get('description','') for e in by[69]['edits'])
    assert all(word in by[70]['analysis'] for word in ['400米','300米','200米','指北针','区域界'])
    checks['Q69_added_direction_is_logged']=True;checks['Q70_elevation_evidence_is_recorded']=True

    # Preserve the external review itself byte-for-byte, including its original
    # blind disagreements and limitations. Never rewrite a reviewer into assent.
    review_paths=['广东行测18套模拟/M03/Claude审核意见.md','广东行测18套模拟/M03/核验记录/claude_review']
    listing=subprocess.check_output(['git','ls-tree','-r','-z',manifest['claude_review_commit'],'--',*review_paths],cwd=ROOT)
    preserved=0
    for record in listing.split(b'\0'):
        if not record:continue
        metadata,path=record.split(b'\t',1);expected_sha=metadata.split()[2].decode();local=ROOT/path.decode()
        git_blob=hashlib.sha1(b'blob '+str(local.stat().st_size).encode()+b'\0'+local.read_bytes()).hexdigest()
        assert git_blob==expected_sha,str(local)
        preserved+=1
    assert preserved>1
    checks['original_claude_review_files_preserved']=preserved
    result={'paper_id':'M03','version':'0.2.0','result':'PASS','checks':checks,
            'limitations':['答案不变、来源保全和条件保全不等于自动证明90题正确。','图像已人工查看；本脚本不代替最终方正字体实尺寸排版检查。','当前修订尚待Claude增量复核。']}
    (HERE/'v020_revision_check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'result':'PASS','answers_unchanged':90,'reasoning_conditions_preserved':len(reasoning_equal),'claude_files_unchanged':preserved,'science_figures_verified':[67,68]},ensure_ascii=False))

if __name__=='__main__':main()

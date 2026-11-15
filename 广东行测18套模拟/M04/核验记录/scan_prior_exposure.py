#!/usr/bin/env python3
"""Scan fixed pre-M04 repository texts against the latest four M04 modules.

The old24 blob cache is an intermediate read-only mirror of the baseline Git
objects, not a new source bank. Source-ID references, actual reserved/selected
records and text matches are distinguished; a common policy sentence or generic
question instruction is not automatically a repeated question.
"""
from pathlib import Path
from bisect import bisect_right
import collections
import hashlib
import html
import json
import re
import subprocess
import unicodedata

HERE=Path(__file__).resolve().parent
M04=HERE.parent
ROOT=HERE.parents[2]
BASE='6aecdb088169c4c8b0c393046a77e483910aaf7d'
CACHE=ROOT.parent/'m04_exposure_cache'
EXT={'.md','.json','.jsonl','.txt','.py','.html'}
PREFIXES=['广东行测24天集训','广东行测18套模拟/M01','广东行测18套模拟/M02','广东行测18套模拟/M03']
MODULES=['politics.json','verbal.json','quant_data.json','reasoning_science.json']
INDEX_PATH='广东行测18套模拟/M01/核验记录/old_graphic_source_ids.json'

def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT)

def norm(s):
    s=html.unescape(unicodedata.normalize('NFKC',str(s)))
    s=re.sub(r'<[^>\n]{0,500}>','',s)
    s=re.sub(r'\\[nrt](?=[^A-Za-z]|$)',' ',s)
    return re.sub(r'[\W_]+','',s,flags=re.UNICODE)

manifest=[]
for prefix in PREFIXES:
    for item in git('ls-tree','-rz',BASE,'--',prefix).decode().split('\0'):
        if not item: continue
        meta,path=item.split('\t',1);mode,kind,sha=meta.split()
        if kind=='blob' and Path(path).suffix in EXT:
            manifest.append({'path':path,'git_blob_sha':sha,'prefix':prefix})
ledger='广东行测18套模拟/用题登记.jsonl'
manifest.append({'path':ledger,'git_blob_sha':git('rev-parse',BASE+':'+ledger).decode().strip(),'prefix':'project_registry'})

corpus=[]
for m in manifest:
    p=CACHE/m['git_blob_sha']
    if p.exists(): raw=p.read_bytes()
    else: raw=git('show',m['git_blob_sha'])
    assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==m['git_blob_sha']
    text=raw.decode('utf-8')
    starts=[];parts=[];n=0
    for line in text.splitlines():
        starts.append(n);piece=norm(line);parts.append(piece);n+=len(piece)
    m.update({'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'lines':len(starts)})
    corpus.append({**m,'text':text,'normalised':''.join(parts),'line_starts':starts})

module_files={name:M04/'编辑底稿'/name for name in MODULES}
module_sha={name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in module_files.items()}
rows=[]
for name,path in module_files.items():
    for q in json.loads(path.read_text()):
        q['_module']=name;rows.append(q)
rows.sort(key=lambda x:x['number'])
assert [q['number'] for q in rows]==list(range(1,91))

def walk_ids(x):
    out=set()
    if isinstance(x,dict):
        for k,v in x.items():
            if k in {'source_id','id','original_source_id','replaced_source_id'} and isinstance(v,str):out.add(v)
            out.update(walk_ids(v))
    elif isinstance(x,list):
        for v in x:out.update(walk_ids(v))
    return out

reserved={};reserved_paths=[]
for c in corpus:
    path=Path(c['path']);low=path.name.lower()
    strong=(path.name=='用题登记.jsonl' or '撤题' in path.name or 'selection' in low or path.name=='review_v3_changes.json')
    if not strong:continue
    try:
        data=[json.loads(l) for l in c['text'].splitlines() if l.strip()] if path.suffix=='.jsonl' else json.loads(c['text'])
    except (ValueError,TypeError):continue
    # BASE predates M04. Keep this guard for future reuse of the scanner.
    if path.name=='用题登记.jsonl':
        data=[r for r in data if not any(str(r.get(k,''))=='M04' for k in ['paper','paper_id','set_id'])]
    reserved_paths.append(c['path'])
    for sid in walk_ids(data):reserved.setdefault(sid,[]).append(c['path'])

graphic=json.loads(next(c['text'] for c in corpus if c['path']==INDEX_PATH))
old_graphic_ids=set(graphic.get('recognized_jz_source_ids',[]))|set(graphic.get('matched_current_bank_source_ids',[]))

def block_text(bs):
    if isinstance(bs,str):return bs
    if isinstance(bs,dict):bs=[bs]
    out=[]
    for b in bs or []:
        if not isinstance(b,dict):continue
        if b.get('type')=='text':out.append(b.get('text',''))
        elif b.get('type')=='table':
            out.extend([b.get('title',''),' '.join(map(str,b.get('headers',[])))])
            out.extend(' '.join(map(str,r)) for r in b.get('rows',[]))
    return '\n'.join(out)

def content_inputs(q):
    sq=q.get('source_question') or {}
    out=[('current_stem',block_text(q.get('stem_override',q.get('stem',sq.get('stem',[])))))]
    orig=block_text(sq.get('stem',[]))
    if orig and orig!=out[0][1]:out.append(('source_stem',orig))
    mats=q.get('materials')
    if mats is None:
        mat=q.get('material',sq.get('material'))
        mats=[mat] if mat else sq.get('materials',[])
    for i,m in enumerate(mats or []):
        out.append((f'material_{i+1}',block_text(m.get('blocks',m.get('content',m.get('text',[]))))))
    return out

def patterns_for(label,text):
    x=norm(text);cjk=len(re.findall(r'[\u3400-\u9fff]',x))
    generic=bool(re.search('从所给的四个选项中选择最合适|从所给选项中选择最合适|选择最合适的一个填入问号',x))
    pats=[]
    if generic and len(x)<70:return []
    if len(x)>=30 and cjk>=10:pats.append(('complete_'+label,x))
    elif label.endswith('stem') and len(x)>=12 and cjk<5:
        pats.append(('short_numeric_expression',x))
    if len(x)>=64:
        width=48 if not label.startswith('material') else 64
        step=24 if width==48 else 96
        for pos in range(0,max(1,len(x)-width+1),step):
            piece=x[pos:pos+width]
            if len(piece)==width:pats.append(('long_fragment_'+label,piece))
        pats.append(('long_fragment_'+label,x[-width:]))
    return list(dict.fromkeys(pats))

results=[]
for q in rows:
    sid=q['source_id'];ref_hits=[];text_hits=[]
    patterns=[]
    for label,txt in content_inputs(q):patterns.extend(patterns_for(label,txt))
    patterns=list(dict.fromkeys(patterns))
    for c in corpus:
        if c['path']==INDEX_PATH:continue  # It also contains UNMATCHED candidates.
        if sid in c['text']:
            i=c['text'].find(sid);line=c['text'].count('\n',0,i)+1
            ref_hits.append({'path':c['path'],'line':line,'category':'old24_reference' if c['prefix']=='广东行测24天集训' else 'prior_paper_reference','snippet':c['text'][max(0,i-60):i+len(sid)+120]})
        hits=[]
        for kind,p in patterns:
            at=c['normalised'].find(p)
            if at>=0:
                line=bisect_right(c['line_starts'],at)
                hits.append({'kind':kind,'line':line,'matched_chars':len(p),'pattern':p,'context':c['normalised'][max(0,at-50):at+len(p)+80]})
        if hits:
            hits.sort(key=lambda h:(not h['kind'].startswith('complete'),-h['matched_chars']))
            text_hits.append({'path':c['path'],'prefix':c['prefix'],'match_count':len(hits),'examples':hits[:4]})
    results.append({'number':q['number'],'module':q['_module'],'source_id':sid,
                    'reserved_source_id_matches':reserved.get(sid,[]),
                    'old_graphic_source_id_match':sid in old_graphic_ids,
                    'source_id_reference_matches':ref_hits,'text_matches':text_hits,
                    'text_pattern_count':len(patterns),
                    'input_kind_limitations':(['no_distinctive_text_pattern; rely on source ID and graphic provenance'] if not patterns else [])})

assert module_sha=={n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in module_files.items()}, 'Modules changed during scan; rerun against one snapshot.'

summary={}
for module in MODULES:
    items=[r for r in results if r['module']==module]
    summary[module]={'question_count':len(items),
        'reserved_source_hits':[r['number'] for r in items if r['reserved_source_id_matches']],
        'old_graphic_source_hits':[r['number'] for r in items if r['old_graphic_source_id_match']],
        'old24_source_reference_hits':[r['number'] for r in items if any(h['category']=='old24_reference' for h in r['source_id_reference_matches'])],
        'text_candidate_hits':[r['number'] for r in items if r['text_matches']]}

report={'baseline_commit':BASE,'module_file_sha256':module_sha,'question_count':90,
        'corpus_files':len(corpus),'old24_text_files':sum(c['prefix']=='广东行测24天集训' for c in corpus),
        'corpus_bytes':sum(c['bytes'] for c in corpus),'corpus_lines':sum(c['lines'] for c in corpus),
        'strong_source_record_paths':reserved_paths,'old_graphic_reference_count':len(old_graphic_ids),
        'methods':['literal source IDs','reserved/withdrawn/history source IDs','old delivered graphic source index','complete normalised stem text','48-character overlapping stem fragments','64-character material fragments'],
        'limitations':['A common policy quotation, common topic or generic instruction is not by itself a duplicate question; text candidate hits require interpretation.',
                       'Normalisation removes whitespace and punctuation; short numeric-expression matches are candidates, not proof of complete identity.',
                       'No all-pairs perceptual image matching, no OCR of old PDFs lacking text-side artifacts, and no assertion that the user never encountered an unhit question elsewhere.',
                       'Source objects read from the fixed baseline Git commit; current temporary M04 registry rows are excluded by construction.'],
        'module_summary':summary,'results':results}
(HERE/'prior_exposure_full90_scan.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(HERE/'prior_exposure_corpus_manifest.json').write_text(json.dumps({'baseline_commit':BASE,'files':manifest},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'baseline':BASE,'corpus_files':len(corpus),'old24_text_files':report['old24_text_files'],'corpus_bytes':report['corpus_bytes'],'summary':summary},ensure_ascii=False,indent=2))

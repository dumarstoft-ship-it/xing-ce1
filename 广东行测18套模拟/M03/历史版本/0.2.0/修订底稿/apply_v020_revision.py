#!/usr/bin/env python3
"""Apply the reviewed 0.2.0 edits once, refusing an unexpected starting draft.

The immutable 0.1.0 snapshot is the comparison base. This is an audit/migration
script, not an alternative generator for the current selection.json.
"""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
BASE = PAPER/'历史版本/0.1.0'
BASE_COMMIT = '887670327a0706f75830dd05241900be48b747a2'
REVIEW_COMMIT = 'ec1e3e6abf30caba6144c9397709f068d80ea8b3'
BASE_SHA256 = '5a265f7c6278eaa3c7ec5eb9c26e2964593182c3a6bcc1d60d28dfb5c3af05a7'

def read(path): return json.loads(path.read_text(encoding='utf-8'))
def write(path,value): path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def stable(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def main():
    assert sha(PAPER/'selection.json') == sha(BASE/'selection.json') == BASE_SHA256, 'Expected the exact reviewed 0.1.0 selection; do not overwrite later work.'
    old=read(BASE/'selection.json'); rows=copy.deepcopy(old); by={r['number']:r for r in rows}
    patch_files=[HERE/f'v020_{part}_patch.json' for part in ['verbal_politics','quant_data','reasoning','science']]
    applied={}
    for path in patch_files:
        for patch in read(path):
            n=patch['number']; assert n not in applied, f'Conflicting patch owners: {n}'
            r=by[n]
            assert not set(patch['updates']) & {'source_id','source_file','source_question','source_answer','answer','number','section','question_type'}
            r.update(copy.deepcopy(patch['updates']))
            for edit in r.get('edits',[]):
                if isinstance(edit,dict) and 'version' not in edit:
                    # A replacement of an inaccurate historical description is
                    # a current correction; untouched earlier entries are 0.1.0.
                    edit['version']='0.2.0' if 'edits' in patch['updates'] else '0.1.0'
            for edit in patch.get('added_edits',[]):
                item=copy.deepcopy(edit);item.setdefault('version','0.2.0')
                r.setdefault('edits',[]).append(item)
            applied[n]={'patch_file':path.name,'reason':patch['reason']}
    spec=importlib.util.spec_from_file_location('m03_builder',PAPER/'build_m03.py')
    builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
    manifest=[]
    for prior,current in zip(old,rows):
        n=current['number']; assert n==prior['number']
        for key in ['source_id','source_file','source_question','source_answer','answer','question_type','section']:
            assert current.get(key)==prior.get(key), (n,key)
        fields=sorted(k for k in prior.keys()|current.keys() if prior.get(k)!=current.get(k))
        payload_changed=builder.normalize(prior)!=builder.normalize(current)
        v=current['verification']
        v.setdefault('initial_editor_check_version','0.1.0')
        v['status']='claude_reviewed_v010_revisions_pending_recheck' if n in applied else 'claude_reviewed_v010_unchanged'
        v['claude_review']={'reviewed_version':'0.1.0','review_commit':REVIEW_COMMIT,
                            'report':'Claude审核意见.md','final_answer':current['answer'],
                            'key_result':'accepted_after_review'}
        if n in applied:
            v['revision_020']={'status':'editor_revised_pending_claude_recheck',
                               'report':'GPT审核意见处理.md','changed_fields':fields}
        manifest.append({'number':n,'source_id':current['source_id'],
                         'before_sha256':stable(prior),'after_sha256':stable(current),
                         'changed_fields_excluding_review_metadata':fields,
                         'normalized_question_payload_changed':payload_changed,
                         **applied.get(n,{})})
    write(PAPER/'selection.json',rows)
    cfg=read(BASE/'paper.json')
    cfg.update({'version':'0.2.0','status':'editor_revised_after_claude_review',
                'external_review':'claude_reviewed_v0.1.0_revisions_pending_recheck',
                'printing_status':'pending_revision_recheck',
                'display_status':'90题修订稿；已处理Claude对0.1.0的审核意见，当前改动待Claude复核后打印排版。',
                'reviewed_baseline_commit':BASE_COMMIT,'claude_review_commit':REVIEW_COMMIT,
                'revision_recheck_numbers':sorted(applied),
                'revision_report':'GPT审核意见处理.md','revision_manifest':'核验记录/v020_revision_manifest.json'})
    write(PAPER/'paper.json',cfg)
    record={'paper_id':'M03','from_version':'0.1.0','to_version':'0.2.0',
            'baseline_commit':BASE_COMMIT,'claude_review_commit':REVIEW_COMMIT,
            'baseline_selection_sha256':BASE_SHA256,'current_selection_sha256':sha(PAPER/'selection.json'),
            'patch_sha256':{path.name:sha(path) for path in patch_files},
            'revised_numbers':sorted(applied),
            'normalized_question_payload_changed_numbers':[x['number'] for x in manifest if x['normalized_question_payload_changed']],
            'answer_keys_changed':[], 'source_objects_changed':[],
            'mandatory_numbers':[35,55,60,65,69,70], 'questions':manifest,
            'status':'editor_changes_applied_not_claude_recheck_approval'}
    write(PAPER/'核验记录/v020_revision_manifest.json',record)
    print(json.dumps({k:record[k] for k in ['revised_numbers','normalized_question_payload_changed_numbers','answer_keys_changed','source_objects_changed']},ensure_ascii=False))

if __name__=='__main__': main()

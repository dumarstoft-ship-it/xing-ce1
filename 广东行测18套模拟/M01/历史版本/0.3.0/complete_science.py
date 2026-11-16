"""Merge only the five newly reviewed science slots; retain existing 85 rows."""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROJECT = HERE.parent
SLOTS = set(range(66, 71))
BASELINE_BLOB = 'bc3efa6f62abf94540606c369a52d0cc0a794a2a'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def digest(obj):
    raw=json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(raw).hexdigest()


def load_lines(path):
    return [json.loads(s) for s in path.read_text(encoding='utf-8').splitlines() if s.strip()]


def prepare():
    plan=load(HERE/'science_selection_v2.json')
    rows=load(HERE/'selection.json')
    numbers=[r['number'] for r in rows]
    assert len(numbers)==len(set(numbers)), 'Duplicate existing question numbers'
    assert set(numbers) in (set(range(1,91))-SLOTS, set(range(1,91))), 'Unexpected paper slots'
    old_rows=copy.deepcopy([r for r in rows if r['number'] not in SLOTS])
    old_q={q['number']:q for q in load_lines(HERE/'题目.jsonl') if q['number'] not in SLOTS}
    assert len(old_rows)==85 and len(old_q)==85
    assert {r['number'] for r in plan['rows']}==SLOTS
    assert len({r['source_id'] for r in plan['rows']})==5
    checks=load(HERE/'核验记录/science_model_checks.json')
    assert checks['status']=='PASS'
    assert {str(r['number']):r['answer'] for r in plan['rows']}==checks['answers']
    source_path=ROOT/plan['source_file']
    wanted={r['source_id'] for r in plan['rows']}
    source={}
    for line in source_path.read_text(encoding='utf-8').splitlines():
        q=json.loads(line)
        if q['id'] in wanted:
            assert q['id'] not in source, 'Duplicate source record'
            source[q['id']]=q
    assert set(source)==wanted
    inserted=[]
    for p in plan['rows']:
        q=source[p['source_id']]
        assert q['section']=='科学推理' and set(q['options'])==set('ABCD')
        assert q.get('answer') is None, 'Source now has answers: independently reconcile first'
        assert all(q['options'].values())
        assert all(b['type']!='table' for b in q['stem']), 'Do not silently replace missing figure with a table'
        for b in q['stem']:
            if b['type']=='figure':
                assert (source_path.parent/b['path']).is_file(), b['path']
        r=copy.deepcopy(p)
        r.update(section='科学推理', question_type='single_choice', source_bank='guangdong_mock',
                 source_file=plan['source_file'], source_question=copy.deepcopy(q), source_answer=None)
        r['verification']['checked_on']=plan['date']
        r['source_locators']={'source_name':q['source']['source_name'], 'source_pages':q['source_pages'],
                              'source_sha256':q['source']['source_sha256']}
        inserted.append(r)
    initial_blob=None
    if not SLOTS.intersection(numbers):
        raw=(HERE/'selection.json').read_bytes()
        initial_blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        assert initial_blob==BASELINE_BLOB, 'Existing 85-question baseline changed: review before merging'
        rows=sorted(rows+inserted, key=lambda r:r['number'])
        save(HERE/'selection.json', rows)
    else:
        # A rebuild never overwrites an already edited science question.
        existing={r['number']:r for r in rows if r['number'] in SLOTS}
        for r in inserted:
            assert existing[r['number']]['source_id']==r['source_id'], 'Science selection changed: reconcile plan'
    cfg=load(HERE/'paper.json')
    cfg.setdefault('prior_source_snapshot', cfg['source_snapshot'])
    cfg.update(version='0.2.0', source_snapshot=plan['source_snapshot'], missing_numbers=[],
               status='review_draft_complete', external_review='pending_claude', printing_status='not_started')
    cfg['completed_section_counts']['科学推理']=5
    save(HERE/'paper.json', cfg)
    assert [r for r in rows if r['number'] not in SLOTS]==old_rows
    return {'old_rows':old_rows, 'old_q':old_q, 'initial_blob':initial_blob,
            'source_sha256':hashlib.sha256(source_path.read_bytes()).hexdigest()}


def finish(before, core):
    rows=load(HERE/'selection.json')
    rest=[r for r in rows if r['number'] not in SLOTS]
    qmap={q['number']:q for q in load_lines(HERE/'题目.jsonl')}
    assert rest==before['old_rows'], 'An original question record changed'
    assert {n:q for n,q in qmap.items() if n not in SLOTS}==before['old_q'], 'An original question body changed'
    report=load(HERE/'核验报告.json')
    assert report['content_validation']=='PASS' and report['actual_count']==90 and report['missing_numbers']==[]
    assert report['is_complete_paper'] and not report['print_ready']
    ledger=[x for x in load_lines(PROJECT/'用题登记.jsonl') if x['paper_id']=='M01']
    assert len(ledger)==90 and {r['number'] for r in ledger}==set(range(1,91))
    sci=sorted([r for r in rows if r['number'] in SLOTS], key=lambda r:r['number'])
    question_text=['# M01｜科学推理第66—70题（待审题面）','答案与解析另册；这是重新选编稿，不是此前丢失清单的恢复。']
    answer_text=['# M01｜科学推理第66—70题：编辑解析与来源','源库没有参考答案；以下为编辑独立推导。Claude外部审核与打印版仍待完成。']
    for r in sci:
        question_text.append(core.render_question(qmap[r['number']]))
        q=r['source_question']
        answer_text.extend([f'## 第{r["number"]}题　{r["answer"]}',r['analysis'],
          f'题源：{r["source_id"]}；{q["source"]["source_name"]}，原题{q["number"]}，PDF第'+ '、'.join(map(str,q['source_pages']))+'页。',
          '选编价值：'+r['selection_reason']])
        ref=r['verification'].get('supporting_reference')
        if ref:
            answer_text.append('知识核对依据：'+ref+'（非原题答案来源）。')
    (HERE/'科推5题_题本.md').write_text('\n\n'.join(question_text)+'\n',encoding='utf-8')
    (HERE/'科推5题_解析与来源.md').write_text('\n\n'.join(answer_text)+'\n',encoding='utf-8')
    audit_path=HERE/'核验记录/科推重选核验.json'
    prior=load(audit_path) if audit_path.exists() else {}
    audit={'status':'PASS','date':'2026-11-15','scope':'Only M01-Q066 through M01-Q070',
           'added_science_count':5,'total_count':90,'unchanged_existing_question_records':85,
           'unchanged_existing_question_bodies':85,'existing_85_canonical_sha256':digest(rest),
           'initial_85_selection_blob':before['initial_blob'] or prior.get('initial_85_selection_blob'),
           'science_source_sha256':before['source_sha256'],
           'new_source_ids':[r['source_id'] for r in sci],
           'unique_science_figures':sorted({p for r in sci for p in core.asset_paths(qmap[r['number']])}),
           'all_90_ledger_entries_present':True,'structure_validation':report['content_validation'],
           'source_answers_available':False,'external_review':'pending_claude','print_ready':False,
           'limits':['Original PDF pages were not available for a full transcription comparison.',
                     'Model checks and manual derivation are not a separate-model review.']}
    save(audit_path,audit)
    plan=load(HERE/'science_selection_v2.json')
    plan['status']='integrated_90_question_review_draft_pending_claude'
    save(HERE/'science_selection_v2.json',plan)
    recovery=HERE/'科推5题_恢复候选.json'
    if recovery.exists():
        archive=load(recovery)
        archive['status']='SUPERSEDED_NOT_FOR_USE'
        archive['superseded_by']='science_selection_v2.json'
        archive['note']='保留为历史恢复候选；本轮正式重选替换其中两题。不得据此覆盖selection.json。'
        save(recovery,archive)
    print(json.dumps({k:audit[k] for k in ['status','total_count','unchanged_existing_question_records','unchanged_existing_question_bodies','external_review','print_ready']},ensure_ascii=False))

#!/usr/bin/env python3
"""Build the M01 review package from one versioned selection; standard library only.

Run from any directory. The script never changes source banks. Missing slots are
declared in paper.json and are not counted as completed questions.
"""
from __future__ import annotations
import collections
import copy
import hashlib
import json
import os
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
ROOT = HERE.parents[1]
JZ = '江浙行测_AI题库/questions.jsonl'
MOCK = '模考/2026下半年广东卷_16-33季_AI可读/全部题目.jsonl'
GK = '国考/言语理解/2016-2025/all.jsonl'


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def write_jsonl(path, rows):
    path.write_text(''.join(json.dumps(r, ensure_ascii=False, separators=(',', ':'))+'\n' for r in rows), encoding='utf-8')


def source_file(row):
    if row.get('source_file'):
        return row['source_file']
    if row['source_bank'].endswith('.jsonl'):
        return row['source_bank']
    if row['source_id'].startswith(('JS', 'ZJ')):
        return JZ
    if row['source_id'].startswith('gd-mock-'):
        return MOCK
    if row['source_id'].startswith('GKYY-'):
        return GK
    return None


def rel_link(repo_path):
    return Path(os.path.relpath(ROOT/repo_path, HERE)).as_posix()


def clean_blocks(value, base=''):
    """Keep text/table/figure order; change asset paths, never question content."""
    if not value:
        return []
    if isinstance(value, str):
        # These are corpus navigation annotations, not components of the item.
        value = re.sub(r'\[代码描摹高清 PNG\]\([^)]*\)\s*·\s*\[SVG\]\([^)]*\)（原图为准）', '', value)
        out = []
        pos = 0
        for m in re.finditer(r'!\[[^\]]*\]\(([^)]+)\)', value):
            if value[pos:m.start()].strip():
                out.append({'type': 'text', 'text': value[pos:m.start()].strip()})
            out.append({'type': 'figure', 'path': (Path(base)/m.group(1)).as_posix()})
            pos = m.end()
        if value[pos:].strip():
            out.append({'type': 'text', 'text': value[pos:].strip()})
        return out
    if isinstance(value, dict):
        value = [value]
    out = []
    for b in value:
        b = copy.deepcopy(b)
        if b.get('type') in ('figure', 'image'):
            b['type'] = 'figure'
            b['path'] = (Path(base)/b['path']).as_posix()
        out.append(b)
    return out


def normalize(row):
    sq = row.get('source_question') or {}
    sf = source_file(row)
    base = str(Path(sf).parent) if sf else ''
    stem = row.get('stem_override', row.get('stem', sq.get('stem')))
    blocks = clean_blocks(stem, base)
    opts = row.get('options', sq.get('options', {}))
    options = {k: clean_blocks(v, base) for k, v in opts.items()}
    materials = []
    raw_materials = row.get('materials')
    if raw_materials is None:
        m = row.get('material', sq.get('material'))
        raw_materials = [m] if m else sq.get('materials', [])
    if not raw_materials and sq.get('passage'):
        raw_materials = [{'id':row['source_id']+'-passage','text':sq['passage']}]
    for m in raw_materials:
        materials.append({
            'id': m.get('id', m.get('material_id')),
            'blocks': clean_blocks(m.get('blocks', m.get('content', m.get('text'))), base),
            'source_question_numbers': m.get('question_numbers', []),
        })
    # Some source records list option images in the same figures registry as
    # stem images. Keep their original position instead of repeating them above.
    displayed_blocks = blocks + sum(options.values(), [])
    displayed_blocks += [b for m in materials for b in m['blocks']]
    existing = {b['path'] for b in displayed_blocks if b.get('type') == 'figure'}
    for f in row.get('figures', sq.get('figures', [])):
        path = (Path(base)/(f.get('original_path') or f['path'])).as_posix()
        if path not in existing:
            blocks.append({'type':'figure', 'path':path})
            existing.add(path)
    return {
        'id':f'M01-Q{row["number"]:03d}', 'number':row['number'],
        'section':row['section'],
        'subtype':row.get('subtype', row.get('subsection', '')),
        'question_type':row.get('question_type', 'single_choice'),
        'stem':blocks, 'options':options,
        'options_mode':row.get('options_mode', sq.get('options_mode', 'text_or_mixed')),
        'materials':materials,
    }


def render_blocks(blocks):
    out = []
    for b in blocks:
        typ = b['type']
        if typ == 'text':
            out.append(b['text'].strip())
        elif typ == 'figure':
            out.append(f'![题图]({rel_link(b["path"])})')
        elif typ == 'table':
            if b.get('title'):
                out.append('**'+b['title']+'**')
            headers=b['headers']
            cell=lambda x:str(x).replace('|', '\\|').replace('\n', ' ')
            table=['| '+' | '.join(map(cell,headers))+' |', '| '+' | '.join(['---']*len(headers))+' |']
            table.extend('| '+' | '.join(map(cell,r))+' |' for r in b['rows'])
            out.append('\n'.join(table))
            if b.get('notes'):
                out.append(b['notes'])
        else:
            raise ValueError(f'Unknown block type: {typ}')
    return '\n\n'.join(out)


def plain_text(blocks):
    return ' '.join(b.get('text', '') for b in blocks)


def render_question(q):
    text=[f'### {q["number"]}.', render_blocks(q['stem'])]
    if q['question_type']=='true_false':
        text.append('（　）')
    elif q['options_mode'] != 'in_figure':
        for k,v in q['options'].items():
            text.append(f'**{k}.** '+render_blocks(v))
    return '\n\n'.join(text)


def asset_paths(q):
    parts=list(q['stem'])
    for o in q['options'].values():
        parts.extend(o)
    for m in q['materials']:
        parts.extend(m['blocks'])
    return [b['path'] for b in parts if b.get('type')=='figure']


def main():
    cfg=read_json(HERE/'paper.json')
    rows=sorted(read_json(HERE/'selection.json'), key=lambda r:r['number'])
    questions=[normalize(r) for r in rows]
    by_number={r['number']:r for r in rows}
    qmap={q['number']:q for q in questions}
    missing=cfg['missing_numbers']
    errors=[]
    expect=set(range(1,cfg['target_question_count']+1))-set(missing)
    if len(by_number)!=len(rows) or set(by_number)!=expect:
        errors.append('Question numbers do not match declared complete/missing slots')
    if len({r['source_id'] for r in rows}) != len(rows):
        errors.append('Duplicate source IDs in this paper')
    materials={}
    group_members=collections.defaultdict(list)
    assets=set()
    for q,r in zip(questions,rows):
        n=q['number']
        answer=r['answer']
        if not q['stem'] or not r.get('analysis'):
            errors.append(f'{n}: missing stem or analysis')
        if q['question_type']=='true_false':
            if answer not in ('正确','错误') or q['options']:
                errors.append(f'{n}: invalid true/false representation')
        else:
            if set(q['options'])!=set('ABCD') or not all(q['options'].values()):
                errors.append(f'{n}: incomplete options')
            if not answer or any(c not in 'ABCD' for c in answer):
                errors.append(f'{n}: invalid answer')
            if (len(answer)>1)!=(q['question_type']=='multiple_choice'):
                errors.append(f'{n}: answer count/type mismatch')
        for m in q['materials']:
            if not m['id'] or not m['blocks']:
                errors.append(f'{n}: missing material identity or content')
            if m['id'] in materials and materials[m['id']]!=m:
                errors.append(f'{n}: inconsistent shared material {m["id"]}')
            materials[m['id']]=m
            group_members[m['id']].append(n)
        if q['section']=='资料分析' and len(q['materials'])!=1:
            errors.append(f'{n}: data question must have one shared material')
        for path in asset_paths(q):
            assets.add(path)
            if not (ROOT/path).is_file():
                errors.append(f'{n}: missing figure {path}')
        displayed = q['stem']+sum(q['options'].values(),[])
        displayed += [b for m in q['materials'] for b in m['blocks']]
        for block in displayed:
            if block.get('type')=='text' and '\ufffd' in block['text']:
                errors.append(f'{n}: replacement character in displayed text')
        sf=source_file(r)
        if sf and not (ROOT/sf).is_file():
            errors.append(f'{n}: missing source bank {sf}')
    data_groups=[(k,v) for k,v in group_members.items() if any(qmap[n]['section']=='资料分析' for n in v)]
    if len(data_groups)!=4 or any(len(v)!=5 for k,v in data_groups):
        errors.append('Data analysis must retain four complete five-question groups')
    actual_counts=dict(collections.Counter(q['section'] for q in questions))
    for section,count in cfg['completed_section_counts'].items():
        if actual_counts.get(section,0)!=count:
            errors.append(f'Section count mismatch: {section}')

    missing_note = '第66—70题科学推理待补，本稿尚不能用于完整整卷计时。' if missing else '题面已补齐，仍待独立审核与打印排版。'
    head=[f'# 广东行测模拟 M01｜选编待审稿',
          f'当前实有 **{len(rows)}题**；全卷目标{cfg["target_question_count"]}题。**{missing_note}**',
          '按近两年广东题本顺序编排。题目不标来源、难度或建议跳题位置；答案与解析另册。',
          '政治理论第1—4题为判断题，第5—8题为单项选择题，第9—10题为多项选择题；其余已编题目为单项选择题。',
          '---']
    sections=[('一、政治理论',1,10),('二、常识应用',11,15),('三、言语理解与表达',16,30),('四、数量关系',31,45),('五、判断推理',46,65),('六、科学推理',66,70),('七、资料分析',71,90)]
    seen_materials=set()
    for title,start,end in sections:
        head.append('## '+title)
        if start==66 and all(n in missing for n in range(66,71)):
            head.append('第66—70题待补。当前题源缺少广东粉笔模考科学推理题面；本节没有计入已完成题量。')
            continue
        for n in range(start,end+1):
            if n not in qmap:
                continue
            q=qmap[n]
            if n in [1,5,9,31,36,46,51]:
                titles={1:'判断题',5:'单项选择题',9:'多项选择题',31:'数字推理',36:'数学运算',46:'图形推理',51:'逻辑判断'}
                head.append('### '+titles[n])
            for m in q['materials']:
                if m['id'] not in seen_materials:
                    members=group_members[m['id']]
                    head.append(f'### 材料：回答第{min(members)}—{max(members)}题')
                    head.append(render_blocks(m['blocks']))
                    seen_materials.add(m['id'])
            head.append(render_question(q))
    (HERE/'题本_待审.md').write_text('\n\n'.join(head)+'\n',encoding='utf-8')
    write_jsonl(HERE/'题目.jsonl',questions)

    answer_lines=['# M01｜答案与解析（待审）',
                  f'本文件含{len(rows)}题的编辑答案。{missing_note}原参考答案、编辑独立解答、内部复核和Claude外部审核是不同状态；本稿尚未经Claude审核。',
                  '## 答案速查']
    for start in range(1,91,10):
        ns=list(range(start,min(start+10,91)))
        answer_lines.extend(['| '+' | '.join(map(str,ns))+' |','| '+' | '.join(['---']*len(ns))+' |','| '+' | '.join(by_number[n]['answer'] if n in by_number else '待补' for n in ns)+' |',''])
    answer_lines.append('## 逐题解析与来源')
    source_rows=[]
    file_hashes={}
    for r,q in zip(rows,questions):
        sf=source_file(r)
        if sf and sf not in file_hashes:
            file_hashes[sf]=hashlib.sha256((ROOT/sf).read_bytes()).hexdigest()
        source=r.get('source_question') or {}
        origin='原创；依讲义主题及所列依据命题' if r['source_bank']=='editor_original' else ('原参考答案已存在，另经编辑独立解答' if r.get('source_answer') else '源库无参考答案；本卷给出编辑独立解答')
        answer_lines += [f'### 第{r["number"]}题　{r["answer"]}',r['analysis']]
        if sf:
            answer_lines.append(f'来源：[{r["source_id"]}]({rel_link(sf)})。{origin}。')
        else:
            p=r['provenance']
            pages='、'.join(map(str,p['book_pages']))
            answer_lines.append(f'命题主题：讲义第{pages}页。{origin}。')
            for ref in p.get('references',[]):
                answer_lines.append(f'- [{ref["title"]}]({ref["url"]})：{ref["locator"]}。')
        if r.get('edits'):
            answer_lines.append('编辑处理：'+json.dumps(r['edits'],ensure_ascii=False))
        source_rows.append({
            'paper_id':'M01','number':r['number'],'source_id':r['source_id'],
            'source_bank':r['source_bank'],'source_file':sf,'source_file_sha256':file_hashes.get(sf),
            'source_snapshot':cfg['source_snapshot'],'source_metadata':source.get('source'),
            'original_number':source.get('number',source.get('original_number')),
            'original_pages':source.get('source_pages',source.get('source',{}).get('pdf_pages')),
            'locators':r.get('source_locators'), 'provenance':r.get('provenance'),
            'source_answer':r.get('source_answer'),'editor_answer':r['answer'],
            'answer_origin':origin,'verification':r['verification'],'edits':r.get('edits',[]),
            'selection_reason':r['selection_reason'],'asset_paths':asset_paths(q),
        })
    (HERE/'答案与解析_待审.md').write_text('\n\n'.join(answer_lines)+'\n',encoding='utf-8')
    write_jsonl(HERE/'来源登记.jsonl',source_rows)
    editorial=['# M01｜逐题选编记录','用于编辑和审核，不放进考生题本。选题理由是编者判断，供独立质疑。','| 题号 | 题源ID | 选择的价值 |','| --- | --- | --- |']
    editorial.extend(f'| {r["number"]} | {r["source_id"]} | {r["selection_reason"].replace(chr(10)," ").replace("|","／")} |' for r in rows)
    (HERE/'选题记录.md').write_text('\n'.join(editorial)+'\n',encoding='utf-8')

    # Register reservations; retain other papers and never label them as user-completed.
    ledger_path=PROJECT/'用题登记.jsonl'
    old=[]
    if ledger_path.exists():
        old=[json.loads(l) for l in ledger_path.read_text().splitlines() if l.strip()]
    ledger=[x for x in old if x['paper_id']!='M01']
    for r,q in zip(rows,questions):
        payload=json.dumps({'stem':q['stem'],'options':q['options'],'materials':q['materials']},ensure_ascii=False,sort_keys=True)
        ledger.append({'paper_id':'M01','number':r['number'],'source_id':r['source_id'],'source_file':source_file(r),'status':'reserved_for_review','user_done':'unknown','content_sha256':hashlib.sha256(payload.encode()).hexdigest()})
    write_jsonl(ledger_path,sorted(ledger,key=lambda x:(x['paper_id'],x['number'])))
    cross=[r['source_id'] for r in rows if any(x['paper_id']!='M01' and x['source_id']==r['source_id'] for x in ledger)]
    if cross:
        errors.append('Source IDs already reserved in other papers: '+','.join(cross))

    # The generated question JSONL deliberately has no answer field.
    if any('answer' in q for q in questions):
        errors.append('Answer leaked into question JSONL')
    for name in ['题本_待审.md','答案与解析_待审.md']:
        for target in re.findall(r'\]\(([^)]+)\)',(HERE/name).read_text()):
            if not target.startswith(('http:','https:','#')) and not (HERE/target).exists():
                errors.append(f'{name}: broken local link {target}')
    report={
        'paper_id':'M01','checked_version':cfg['version'],'content_validation':'PASS' if not errors else 'FAIL',
        'target_count':cfg['target_question_count'],'actual_count':len(rows),'missing_numbers':missing,
        'completed_section_counts':actual_counts,'material_groups':dict(group_members),
        'unique_figure_files':len(assets),'errors':errors,'is_complete_paper':not missing,
        'print_ready':False,'external_review':'pending_claude',
        'source_file_sha256':file_hashes,
        'limits':[
            '结构检查不是答案正确性证明；逐题推导与内部复核记录另存。',
            '粉笔原始PDF未在当前仓库找到，转写题面与原PDF尚未逐页复核。',
            '所有原始资料答案只称参考答案；编辑答案不冒称官方答案。',
            '已交付与用户已做不同，旧专项匹配只用于减少已曝光重复。',
        ],
    }
    write_json(HERE/'核验报告.json',report)
    if errors:
        raise SystemExit('\n'.join(errors))
    print(json.dumps({k:report[k] for k in ['content_validation','actual_count','missing_numbers','unique_figure_files','is_complete_paper','print_ready']},ensure_ascii=False))


if __name__=='__main__':
    main()

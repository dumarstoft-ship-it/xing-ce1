#!/usr/bin/env python3
"""Apply the 2026-11-15 review revision once. Source-bank records remain immutable."""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import itertools
import json
import re
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROJECT = HERE.parent
SPEC = HERE/'review_v3_changes.json'
REPORT = HERE/'核验记录/Claude意见处理核验.json'
STATUS = 'claude_reviewed_v0.2.0_revisions_pending_recheck'

def load(p):
    return json.loads(p.read_text(encoding='utf-8'))

def save(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def canonical(x):
    return sha(json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())

def import_path(name, path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def replace_once(text, old, new):
    assert text.count(old)==1, f'Expected one patch target: {old[:100]}'
    return text.replace(old,new,1)

def patch_builder():
    path=HERE/'build_m01_core.py'
    text=path.read_text(encoding='utf-8')
    text=replace_once(text,"out.append(b['text'].strip())", "out.append(b['text'].strip().replace('\\n', '  \\n'))")
    text=replace_once(text,
        "missing_note = '第66—70题科学推理待补，本稿尚不能用于完整整卷计时。' if missing else '题面已补齐，仍待独立审核与打印排版。'",
        "missing_note = ('第66—70题科学推理待补，本稿尚不能用于完整整卷计时。' if missing else cfg.get('display_status', '题面已补齐，仍待独立审核与打印排版。'))")
    text=replace_once(text,'本稿尚未经Claude审核。',"审核范围与本次修订状态见paper.json及审核意见处理说明。")
    old="answer_lines.extend(['| '+' | '.join(map(str,ns))+' |','| '+' | '.join(['---']*len(ns))+' |','| '+' | '.join(by_number[n]['answer'] if n in by_number else '待补' for n in ns)+' |',''])"
    new="answer_lines.append('\\n'.join(['| '+' | '.join(map(str,ns))+' |','| '+' | '.join(['---']*len(ns))+' |','| '+' | '.join(by_number[n]['answer'] if n in by_number else '待补' for n in ns)+' |]))"
    text=replace_once(text,old,new)
    text=replace_once(text,"answer_lines.append('编辑处理：'+json.dumps(r['edits'],ensure_ascii=False))",
        "answer_lines.append('编辑处理：'+'；'.join(e.get('description', e.get('text', e.get('type',''))) if isinstance(e,dict) else str(e) for e in r['edits']))")
    text=replace_once(text,"'print_ready':False,'external_review':'pending_claude',", "'print_ready':False,'external_review':cfg.get('external_review','pending_claude'),\n        'printing_status':cfg.get('printing_status','not_started'),")
    path.write_text(text,encoding='utf-8')
    # The old science-completion migration must not reset new versions or review states.
    (HERE/'build_m01.py').write_text('''#!/usr/bin/env python3
"""Rebuild the complete M01 without rerunning the historical science migration."""
from pathlib import Path
import subprocess
import sys
import build_m01_core as core

if __name__ == '__main__':
    here=Path(__file__).resolve().parent
    subprocess.run([sys.executable,str(here/'核验记录/check_science.py')],check=True)
    core.main()
''',encoding='utf-8')

def check_math():
    weights={'R':55,'J':80,'S':120}
    seq=[s for k in range(1,5) for s in itertools.product(weights,repeat=k) if sum(weights[t] for t in s)>=360]
    limited=[s for s in seq if not any(s[i]==s[i+1]==s[i+2] for i in range(len(s)-2))]
    assert len(seq)==32 and len(limited)==24
    def calendar(step):
        result=[]
        for end in range(7):
            a=[(end+d-31)%7 for d in range(2,32,step)]
            b=[(end+d-31)%7 for d in range(3,32,step)]
            if a.count(5)==a.count(6)==b.count(6)==1 and b.count(5)==0:
                result.append(end)
        return result
    assert calendar(5)==[3] and calendar(4)==[]
    assert 847.1 < min(11355.7,9745.3)
    return {'Q45':{'unlimited':len(seq),'three_sessions':sum(len(s)==3 for s in seq),'four_sessions':sum(len(s)==4 for s in seq),'at_most_two_identical_consecutive':len(limited)},
            'Q40':{'weekday31_mon0_step5':calendar(5),'weekday31_mon0_step4':calendar(4)},
            'Q85':{'unreported_components_upper_bound':847.1,'transport_import':11355.7,'transport_export':9745.3}}

def apply():
    spec=load(SPEC)
    cfg=load(HERE/'paper.json')
    if cfg['version']==spec['to_version']:
        assert REPORT.exists(), 'Revision marked applied but report missing'
        print('Revision already applied; use build_m01.py to regenerate outputs.')
        return
    assert cfg['version']==spec['from_version'], 'Unexpected baseline version'
    rows=load(HERE/'selection.json')
    assert len(rows)==90 and {r['number'] for r in rows}==set(range(1,91))
    before=copy.deepcopy(rows)
    before_by={r['number']:r for r in before}
    source_paths={r.get('source_file') for r in rows if r.get('source_file')}
    source_hashes={p:sha((ROOT/p).read_bytes()) for p in sorted(source_paths)}
    old_q=load_lines(HERE/'题目.jsonl')
    core=import_path('m01_core_pre_revision',HERE/'build_m01_core.py')
    printer=import_path('m01_print_reflow',PROJECT/'打印排版/build_print.py')
    layout_log=printer.Log()
    explicit=set(map(int,spec['changes']))
    changed_fields={}
    for r in rows:
        n=r['number']
        edits=spec['changes'].get(str(n))
        if edits:
            for k,v in edits['set'].items():
                if k=='references':
                    r.setdefault('provenance',{})['references']=copy.deepcopy(v)
                else:
                    r[k]=copy.deepcopy(v)
            r.setdefault('edits',[]).append({'type':'claude_review_revision','description':edits['reason'],'revision':'0.3.0'})
            changed_fields[str(n)]=list(edits['set'])
        sq=r.get('source_question') or {}
        raw=r.get('stem_override',r.get('stem',sq.get('stem')))
        stem=core.clean_blocks(raw,'')
        cleaned=clean_text_blocks(stem,n,'题干',printer,layout_log)
        if cleaned!=stem:
            r['stem_override']=cleaned
        rawopts=r.get('options',sq.get('options',{}))
        opts={k:core.clean_blocks(v,'') for k,v in rawopts.items()}
        normopts={k:clean_text_blocks(v,n,'选项'+k,printer,layout_log) for k,v in opts.items()}
        if normopts!=opts:
            r['options']=normopts
        if cleaned!=stem or normopts!=opts:
            r.setdefault('edits',[]).append({'type':'layout_only','description':'合并原PDF行末硬换行，保留列表、对话及设问分段；省略号和空括号规范化。详见本次格式修订日志。','revision':'0.3.0'})
        ver=r.setdefault('verification',{})
        ver['external_review']={'reviewer':'Claude','reviewed_version':'0.2.0','review_commit':spec['review_commit'],'answer_agreement':True,
            'current_revision':'0.3.0','revision_recheck':'pending' if n in explicit else 'no_substantive_change'}
        ver['status']='editor_revised_pending_delta_review' if n in explicit else 'claude_reviewed_no_substantive_change'
    by={r['number']:r for r in rows}
    overlay={'method':'复核原图与Claude对比图；第二行的白条排除黑色并集，采用后图含白色部分的不透明覆盖。',
             'independent_answer':'C','operation':'second_shape_opaque_overlay',
             'visual_caveat':'核对轮廓及重叠区域，像素相似度仅为辅助证据；答案一致不等于旧解析成立。',
             'corrected_on':'2026-11-15','supersedes':'此前black union记录错误，现撤回。'}
    by[50]['verification']['independent_check']=copy.deepcopy(overlay)
    jpath=HERE/'核验记录/judgment_verification.json'
    judgment=load(jpath); judgment['ZJ2021-A类-080']=overlay; save(jpath,judgment)
    notespath=HERE/'核验记录/judgment_notes.md'
    notes=notespath.read_text(encoding='utf-8')
    notes=notes.replace('原库未改，未执行git提交。','原库未改；本文件为早期编排记录，2026-11-15依Claude复核更正第50题说明。')
    notes=notes.replace('第50题先由图片做叠加判断，再用原图像素对齐辅助比较并集/异或，之后才读取源答案。','第50题早期误写为黑色并集；2026-11-15根据第二行白条与第三行覆盖关系复核，改为后图整体覆盖前图（含白色区域），原答案不变。')
    notes=notes.replace('黑色叠加','后图不透明覆盖前图')
    notespath.write_text(notes,encoding='utf-8')
    assert all(r.get('source_question')==before_by[r['number']].get('source_question') for r in rows)
    assert all(r['source_id']==before_by[r['number']]['source_id'] and r['answer']==before_by[r['number']]['answer'] and r.get('source_answer')==before_by[r['number']].get('source_answer') for r in rows)
    save(HERE/'selection.json',rows)
    cfg.update(version='0.3.0', status='editor_revised_after_claude_review', external_review=STATUS,
               printing_status='v0.3.0_not_rebuilt_v0.2.0_archived',
               display_status='Claude已审核0.2.0；本稿为意见处理后的0.3.0，改动项待增量复核，打印版待重排。')
    cfg['review_baseline']={'version':'0.2.0','commit':spec['review_commit'],'blind_answer_agreement':90}
    cfg['revision_recheck_numbers']=sorted(explicit)
    save(HERE/'paper.json',cfg)
    patch_builder()
    core=import_path('m01_core_v3',HERE/'build_m01_core.py')
    core.main()
    new_q=load_lines(HERE/'题目.jsonl')
    substantive=[n for n,c in spec['changes'].items() if set(c['set']) & {'stem','stem_override','options'}]
    assert len(new_q)==90
    assert all(q['materials']==old['materials'] for q,old in zip(new_q,old_q)), 'Shared material changed'
    assert {p:sha((ROOT/p).read_bytes()) for p in sorted(source_paths)}==source_hashes
    report={'status':'PASS','version':'0.3.0','reviewed_baseline':'0.2.0','review_commit':spec['review_commit'],
            'date':spec['date'],'question_count':len(rows),'unchanged_answer_letters':90,'unchanged_source_objects':90,
            'unchanged_source_ids':90,'unchanged_source_answer_objects':90,'unchanged_shared_materials':True,
            'source_bank_hashes_unchanged':source_hashes,'baseline_selection_canonical_sha256':canonical(before),
            'revised_selection_canonical_sha256':canonical(rows),'editorial_changes':changed_fields,
            'substantive_question_body_revision_numbers':sorted(map(int,substantive)),
            'format_change_count':len(layout_log.items),'format_change_questions':sorted({x['题号'] for x in layout_log.items}),
            'numerical_rechecks':check_math(),'Q50_operation':overlay['operation'],
            'answer_table_blocks':len(re.findall(r'^\| (?:\d+ \| ?)+\n\| (?:--- \| ?)+\n\|', (HERE/'答案与解析_待审.md').read_text(),re.M)),
            'external_review':STATUS,'print_ready':False,
            'limits':['Claude的90题一致结论属于0.2.0；本轮改动未冒称已通过Claude复核。','政策概念题按所列一手依据编辑核对；知识判断不能由程序或答案字母不变代替。','原PDF逐页复核边界仍按Claude审核意见保留。']}
    assert report['answer_table_blocks']==9
    save(HERE/'核验记录/格式修订日志_v0.3.0.json',layout_log.items)
    save(REPORT,report)
    archive_print()
    write_docs(spec,report)
    print(json.dumps({k:report[k] for k in ['status','question_count','unchanged_answer_letters','substantive_question_body_revision_numbers','format_change_count','answer_table_blocks']},ensure_ascii=False))

def load_lines(p):
    return [json.loads(s) for s in p.read_text(encoding='utf-8').splitlines() if s.strip()]

def clean_text_blocks(blocks,n,where,printer,log):
    out=copy.deepcopy(blocks)
    for b in out:
        if b.get('type')=='text':
            old=b['text']
            new='\n'.join(printer.reflow(old,n,where,log))
            new=re.sub(r'·{3,}','……',new)
            new=re.sub(r'（\s*）','（　）',new)
            strip=lambda t:re.sub(r'·{3,}','……',re.sub(r'\s+','',t)).rstrip('：:')
            assert strip(old)==strip(new),f'Unexpected textual normalization Q{n}: {old} -> {new}'
            if old!=new and not any(x['题号']==n and x['位置']==where for x in log.items):
                log.add(n,where,'标点或空括号规范化',old,new)
            b['text']=new
    return out

def archive_print():
    folder=HERE/'打印版'
    archive=folder/'历史版本'
    archive.mkdir(parents=True,exist_ok=True)
    for name,new in [('M01_题本_打印版.pdf','M01_题本_v0.2.0_旧版勿打印.pdf'),('排版日志.json','排版日志_v0.2.0.json')]:
        if (folder/name).exists():
            assert not (archive/new).exists()
            shutil.move(str(folder/name),str(archive/new))
    (folder/'README.md').write_text('# M01打印版状态\n\n当前内容版本为 **0.3.0**。**尚未使用完整的原指定字体重新生成PDF，当前没有0.3.0打印定稿。**\n\n旧0.2.0题本含第45题旧措辞，已移入`历史版本/`并标注“旧版勿打印”；其排版日志一并保留。不要把历史PDF当作本次修订结果。\n\n完整字体环境下使用：\n\n```bash\npython3 广东行测18套模拟/打印排版/build_print.py M01 --font-dir <字体目录>\n```\n\n重新生成后应检查第1—15题、45题和分段密集题的分页，并核对PDF与当前题目.jsonl的内容指纹。字体文件不入库、不对外提供。\n',encoding='utf-8')

def write_docs(spec,report):
    lines=['# M01｜GPT对Claude审核意见的处理','版本：0.3.0。审核基线：Claude分支提交`'+spec['review_commit']+'`的0.2.0，原意见文件保持不改。',
      '## 处理结论','两项必须修改均落实。90题答案字母和题源ID不变，90条记录中保留的源题对象、源参考答案（含原本空值）均未改动，四组资料材料不变；答案一致不是新题面已经完成外部审核的证明。',
      '## 逐项处理','|题号|落实内容|','|---|---|']
    lines += [f'|{n}|{c["reason"]}|' for n,c in spec['changes'].items()]
    lines += ['','第45题明确顺序和连续次数不限，并将C项30换为31，专门检验漏计三段全游泳的情况。枚举得到32；旧措辞另一读法得到24。第50题修正的是解题规则，不只是换个说法；原图、答案和选项未动，底稿与两份判断核验记录同步更正。',
      '## 格式与构建','源PDF行末硬换行、省略号和空括号在编辑层修正，原始源对象保留；真实列表、对话、设问分段仍保留。Markdown使用显式换行，答案速查生成9个真正的表格，编辑说明改为文字，不直接打印JSON。具体逐处处理见`核验记录/格式修订日志_v0.3.0.json`。',
      '构建入口不再反复执行旧的五题合入迁移，防止把版本回退至0.2.0、把审核状态改回“尚未审核”。原`complete_science.py`和旧保全核验保留为历史，未改写为本轮成绩。',
      '## 未机械采纳的建议']
    lines += ['\n'+x for x in spec['deferred']]
    lines += ['\n第6题保留情境识别，只清理选项，不把命题方式一律改成背原句；第15题保留封弥、誊录的机制辨析，只修干扰项。第1题更正出处及主语，但与第5题仍有主题联系，不为了完全消除重叠把整套推倒重编。第61、64题原设问措辞不改，只保证分段清楚。',
      '## 当前交接边界','Claude对旧0.2.0的90题盲解一致结论保留。本轮16题有内容或解析处理，其中11题题面/选项有实质修订，应做增量复核；其余是格式处理。政治常识修订依据记录在各题provenance，未经Claude二次审题。',
      '打印代码已保留。当前环境缺少原指定完整字体，未生成新版本PDF；旧PDF移入历史版本并标明旧版勿打印。不能用旧PDF或旧排版日志冒充当前0.3.0成果。',
      '建议Claude先盲解本次改动的题面，再复核第19、40、50、83、85题解析，处理意见后使用原字体重排。无需把未改的题目再从零编写。']
    (HERE/'GPT审核意见处理.md').write_text('\n\n'.join(lines[:5])+'\n\n'+'\n'.join(lines[5:7+len(spec['changes'])])+'\n\n'+'\n\n'.join(lines[7+len(spec['changes']):])+'\n',encoding='utf-8')
    (HERE/'交接_Claude_修订复核.md').write_text('# M01 0.3.0｜增量复核交接\n\n请先读`GPT审核意见处理.md`，再按当前`题本_待审.md`盲解第1、5、6、8、9、10、12、13、14、15、45题；其余题面只作格式规范化。答案与来源在另册，避免先看答案后确认。\n\n解析重点：第19题引文、第40题周期口径的反证、第50题后图覆盖（尤其白区）、第83题基期比值、第85题缺省格的上界。第50题原图与候选不变。\n\n结构性配比建议留到后续套卷统筹，不设置机械简单题比例或固定小类配额。不据来源猜测用户已做过。\n\n`核验记录/Claude意见处理核验.json`只记录本轮实际完成的编辑核验；0.2.0审核稿和脚本保留。政策/常识修订仍请独立判断，不因答案字母未变而跳过。\n\n本次没有0.3.0打印定稿。旧0.2.0 PDF归档为旧版勿打印；请处理增量审核后按原字体重跑排版，并检查新内容分页和题号覆盖。\n',encoding='utf-8')
    readme='''# M01｜0.3.0审核意见处理稿

当前90题齐全。Claude已完成0.2.0的独立审核；GPT已处理两项必须修改，并落实选定的质量与格式改进。**新改动待Claude增量复核，不冒称0.3.0已通过第二轮审核。打印版待原字体重排。**

|入口|内容|
|---|---|
|[题本](题本_待审.md)|当前90题，答案、题源与编辑提示后置|
|[答案与解析](答案与解析_待审.md)|修正后的解释与9张答案速查表|
|[Claude原审核意见](Claude审核意见.md)|对0.2.0的独立审题结论，原文未改|
|[GPT处理说明](GPT审核意见处理.md)|哪些采纳、怎样改、哪些不机械采纳|
|[增量复核交接](交接_Claude_修订复核.md)|需复核的改动项及打印事项|
|[本轮核验](核验记录/Claude意见处理核验.json)|题量、源对象与答案保全、枚举及格式检查|
|[整卷结构检查](核验报告.json)|当前0.3.0构建结果|
|[打印状态](打印版/README.md)|旧PDF已归档，不是当前打印定稿|

原题库未修改；selection.json为唯一整卷底稿。review_v3_changes.json保留本轮修订指令，apply_claude_review_v3.py只执行一次有版本保护的迁移；后续编辑应改selection.json再构建，不重复覆盖审核后的判断。

```bash
python3 广东行测18套模拟/M01/build_m01.py
```

complete_science.py、science_selection_v2.json及原85题保全报告是0.2.0历史记录，不再每次构建执行。已看源库图片不等于已逐页核原PDF，题库答案亦不等于官方答案；具体边界见Claude原意见与本轮处理说明。
'''
    (HERE/'README.md').write_text(readme,encoding='utf-8')
    for path in [PROJECT/'README.md',ROOT/'README.md']:
        if path.exists():
            text=path.read_text(encoding='utf-8')
            prefix=('# 当前修订提示（2026-11-15）\n\nM01已完成Claude审核意见处理，内容版本为 **0.3.0**；改动项待增量复核，旧打印版已归档。以[M01当前入口]('+ ('M01/README.md' if path.parent==PROJECT else '广东行测18套模拟/M01/README.md')+')及其打印状态为准。下方旧进度描述仅供回溯，不作最新完成状态。\n\n')
            path.write_text(prefix+text,encoding='utf-8')

if __name__=='__main__':
    apply()

#!/usr/bin/env python3
"""Build one paper with tools/extract.py, plus three corrections keys the current script cannot express.

tools/extract.py is NOT modified: it is imported as a module, two of its functions (segment,
parse_question) are wrapped, build() is called, and per-option figures are filled in afterwards.
Only the paper's own output files are written (the same files build() writes).

Extra keys in tools/corrections/<paper>.json (ignored by the unpatched script, which therefore stops
with an error instead of writing wrong output for these papers):

  figure_questions  {"p05-i03": 35, ...}
        Assign a figure (non-inline image) to the given question, overriding the automatic
        assignment (segment() orders figures by their bottom edge; an image object whose white margin
        reaches below the next question's first line is otherwise given to the next question; in
        资料分析, an option image that follows the "C、 D、" label line otherwise starts a new material).
        A material left with no header and no items afterwards is dropped and its questions join the
        preceding material.
  option_splits     [{"q": 10, "label": "D", "reason": "..."}]
        Split option <label> out of the previous option's text at " <label>、" (the label sits on the
        previous option's wrapped continuation line; the script joins that whole line to the previous
        option and its re-split rule does not allow a space before the label).
  option_figures    {"89": {"A": "p13-i02", "B": "p13-i03", "C": "p13-i04", "D": "p13-i05"}}
        One image per option (as in the 2022—2026 library): each image gets role "option" (set it in
        figures.<key>.role) and option_label, and each option's image_refs points to its image with
        label_in_image null. The options' text stays empty.

usage: build_patched.py <paper> [--work DIR]
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

EXTRACT = Path('/home/user/xing-ce1/广东/行测/2013-2021/tools/extract.py')
spec = importlib.util.spec_from_file_location('extract', EXTRACT)
ex = importlib.util.module_from_spec(spec)
sys.modules['extract'] = ex
spec.loader.exec_module(ex)

paper = sys.argv[1]
work = Path(sys.argv[sys.argv.index('--work') + 1]) if '--work' in sys.argv else None
CFG, CORR = ex.load_cfg(paper)

_orig_segment = ex.segment
_orig_parse_question = ex.parse_question


def segment(pages, expected, inline_text, missing=()):
    seg = _orig_segment(pages, expected, inline_text, missing)
    fq = CORR.get('figure_questions', {})
    if not fq:
        return seg
    qmap = {q.number: q for q in seg['questions']}
    for key, qn in fq.items():
        found = None
        for q in seg['questions']:
            for im in list(q.figures):
                if im.key == key:
                    q.figures.remove(im)
                    found = im
        for m in seg['materials']:
            for it in list(m.items):
                if it[0] == 'fig' and it[1].key == key:
                    m.items.remove(it)
                    found = it[1]
        for im in list(seg['orphans']):
            if im.key == key:
                seg['orphans'].remove(im)
                found = im
        if found is None:
            ex.die(f'figure_questions：找不到题图 {key}')
        if qn not in qmap:
            ex.die(f'figure_questions：没有第{qn}题')
        qmap[qn].figures.append(found)
        qmap[qn].figures.sort(key=lambda im: (im.page, im.top, im.x0))
    kept = []
    for m in seg['materials']:
        if not m.header and not m.items:
            if not kept:
                ex.die('figure_questions：第一组材料被清空，无法并入前一组')
            kept[-1].questions.extend(m.questions)
        else:
            kept.append(m)
    for k, m in enumerate(kept, 1):
        m.k = k
        for n in m.questions:
            qmap[n].material = k
    seg['materials'] = kept
    return seg


def parse_question(q, left, right, autofix):
    r = _orig_parse_question(q, left, right, autofix)
    n = r['number']
    for sp in CORR.get('option_splits', []):
        if sp['q'] != n:
            continue
        L = sp['label']
        if not r['options'] or r['options'][-1]['label'] != chr(ord(L) - 1):
            ex.die(f'option_splits：第{n}题最后一个选项不是{chr(ord(L) - 1)}项')
        o = r['options'][-1]
        ms = list(re.finditer(rf'\s({L})\s*[、.．]', o['text']))
        if len(ms) != 1:
            ex.die(f'option_splits：第{n}题{o["label"]}项中“ {L}、”出现 {len(ms)} 次（应为 1 次）')
        m = ms[0]
        r['options'].append({'label': L, 'text': o['text'][m.end():].strip()})
        o['text'] = o['text'][:m.start()].strip()
        r['labels_raw'].append(m.group(0).strip())
        autofix.append(f'第{n}题：{sp["reason"]}')
    if str(n) in CORR.get('option_figures', {}):
        if any(o['text'] for o in r['options']):
            ex.die(f'option_figures：第{n}题有文字选项')
        r['options'] = [{'label': L, 'text': ''} for L in 'ABCD']
    return r


ex.segment = segment
ex.parse_question = parse_question

records = ex.build(paper, work)

of_all = CORR.get('option_figures', {})
if of_all:
    for rec in records:
        of = of_all.get(str(rec['question_number']))
        if not of:
            continue
        ids = {L: f'{paper}-{key}' for L, key in of.items()}
        figs = {f['image_id']: f for f in rec['figures']}
        for L, iid in ids.items():
            if iid not in figs:
                ex.die(f'option_figures：第{rec["question_number"]}题没有题图 {iid}')
            if figs[iid]['role'] != 'option':
                ex.die(f'option_figures：{iid} 的 role 应在 figures 中设为 option')
            figs[iid]['option_label'] = L
        for o in rec['options']:
            o['image_refs'] = [{'image_id': ids[o['label']], 'label_in_image': None}]
    files = ex.paper_files(paper)
    files['jsonl'].write_text(''.join(json.dumps(r, ensure_ascii=False, separators=(',', ':')) + '\n'
                                      for r in records), encoding='utf-8')
    files['md'].write_text(ex.render_md(records, CFG, paper, ex.source_commit(CFG, paper)), encoding='utf-8')
    print(f'已按 option_figures 写入选项图：{sorted(of_all)}')

ex.cmd_verify([paper])
print('本卷已生成并校验（build_patched）；汇总根目录文件请运行：python3 tools/extract.py index')

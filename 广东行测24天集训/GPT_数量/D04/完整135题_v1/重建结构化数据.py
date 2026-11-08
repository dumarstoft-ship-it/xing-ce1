#!/usr/bin/env python3
"""从本目录的权威 Markdown 题本/答案及 CSV 索引重建 JSONL。
仅做结构一致性检查，不宣称重新证明数学答案；不执行核验记录中的表达式。
Python 3.9+，无第三方依赖。运行：python 重建结构化数据.py
"""
from __future__ import annotations
import csv
import json
import re
from pathlib import Path

PAIRS = [
    ('D04_数学运算001-040_题本.md', 'D04_数学运算001-040_答案.md'),
    ('D04_数学运算041-080_题本.md', 'D04_数学运算041-080_答案.md'),
    ('D04_数学运算081-105_题本.md', 'D04_数学运算081-105_答案.md'),
    ('D04_数字推理001-030_题本.md', 'D04_数字推理001-030_答案.md'),
]

def sections(text: str) -> list[tuple[str, str, str]]:
    pat = re.compile(r'^### (D04-[MN]\d{3})([^\n]*)\n', re.M)
    hits = list(pat.finditer(text))
    return [(m[1], m[2], text[m.end():hits[i+1].start() if i+1 < len(hits) else len(text)].strip())
            for i, m in enumerate(hits)]

def build(base: Path) -> Path:
    with (base / 'D04_编制索引.csv').open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    index = {r['id']: r for r in rows}
    if len(rows) != 135 or len(index) != 135:
        raise ValueError('索引应含135个不同题号。')
    report = json.loads((base / 'D04_核验记录.json').read_text(encoding='utf-8'))
    checks = {r['id']: r for k in ('math_checks', 'series_checks') for r in report[k]}
    result = []
    for qfile, afile in PAIRS:
        questions = sections((base / qfile).read_text(encoding='utf-8'))
        answers = {qid: (heading, body) for qid, heading, body in sections((base / afile).read_text(encoding='utf-8'))}
        if set(answers) != {q[0] for q in questions}:
            raise ValueError(f'{qfile}与{afile}题号不一致。')
        for qid, _, body in questions:
            opts = list(re.finditer(r'^([A-D])\.\s*(.+)$', body, re.M))
            if [m[1] for m in opts] != list('ABCD'):
                raise ValueError(f'{qid}缺少唯一的A—D选项。')
            heading, solution = answers[qid]
            key = re.fullmatch(r'｜([A-D])．(.+)', heading)
            if not key or index[qid]['answer'] != key[1]:
                raise ValueError(f'{qid}答案标题与索引不一致。')
            kind = re.search(r'\*\*类型：\*\*([^。\n]+)', solution)
            if not kind or kind[1] != index[qid]['kind']:
                raise ValueError(f'{qid}类型标签不一致。')
            if qid not in checks or checks[qid].get('passed') is not True:
                raise ValueError(f'{qid}缺少通过的既有核验记录。')
            options = {m[1]: m[2].strip() for m in opts}
            result.append({
                'id': qid, 'version': report['version'],
                'stem': body[:opts[0].start()].strip(), 'options': options,
                'answer': key[1], 'answer_display': key[2],
                'kind': index[qid]['kind'],
                'source_references': index[qid]['source_references'].split(';'),
                'solution_markdown': solution,
                'question_file': qfile, 'answer_file': afile,
                'recorded_verification': checks[qid],
            })
    ids = [r['id'] for r in result]
    expected = {f'D04-M{i:03}' for i in range(1,106)} | {f'D04-N{i:03}' for i in range(1,31)}
    if len(ids) != 135 or set(ids) != expected:
        raise ValueError('题本题号必须恰好为M001—105、N001—030且不重复。')
    target = base / '_derived' / 'D04_完整135题.jsonl'
    target.parent.mkdir(exist_ok=True)
    target.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in result), encoding='utf-8')
    print(f'结构检查通过：105道数学运算＋30道数字推理。输出：{target}')
    print('此操作只重建数据，不构成新的一次数学复核或Claude盲审。')
    return target

if __name__ == '__main__':
    try:
        build(Path(__file__).resolve().parent)
    except (OSError, ValueError, KeyError) as exc:
        raise SystemExit(f'重建失败：{exc}') from exc

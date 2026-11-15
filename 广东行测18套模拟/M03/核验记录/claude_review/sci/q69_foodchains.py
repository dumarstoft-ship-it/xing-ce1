#!/usr/bin/env python3
"""Q69 food-web check (M03, 0.1.0).

Compares three edge sets and enumerates every food chain for each:
  1. FIGURE  - edges read by eye from assets/q69_foodweb.png (reviewer's blind reading)
  2. DOT     - visible edges parsed from assets/q69_foodweb.dot (what the PNG was rendered from)
  3. SOURCE  - edges parsed from the source table in selection.json (Q69 source_question),
               if that file is reachable; otherwise skipped.
Then reports: edge differences, number of chains, every chain, trophic levels of
each species, and which options A-D hold.

Run:  python3 q69_foodchains.py [repo_root]
Read-only with respect to the repository.
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/home/user/xing-ce1')
M03 = REPO / '广东行测18套模拟' / 'M03'

# 1. Reviewer's reading of the PNG (prey -> predator), recorded before opening any answer file.
FIGURE = {
    ('茶树', '茶毛虫'), ('茶树', '茶尺蠖'), ('草', '茶毛虫'), ('草', '茶尺蠖'),
    ('茶毛虫', '蜘蛛'), ('茶毛虫', '蛙'), ('茶尺蠖', '蜘蛛'), ('茶尺蠖', '鸟'),
    ('蜘蛛', '蛙'), ('蛙', '蛇'), ('鸟', '蛇'),
}


def parse_dot(path):
    edges = set()
    for line in path.read_text(encoding='utf-8').splitlines():
        m = re.match(r'\s*"([^"]+)"\s*->\s*"([^"]+)"\s*(\[.*\])?\s*;', line)
        if m and 'invis' not in (m.group(3) or ''):
            edges.add((m.group(1), m.group(2)))
    return edges


def chains(edges):
    nodes = {a for a, _ in edges} | {b for _, b in edges}
    preds = {n: sorted(b for a, b in edges if a == n) for n in nodes}
    has_prey = {b for _, b in edges}
    producers = sorted(n for n in nodes if n not in has_prey)
    out = []

    def dfs(path):
        nxt = preds[path[-1]]
        if not nxt:
            out.append(path)
            return
        for n in nxt:
            if n in path:
                raise ValueError('cycle: ' + '->'.join(path + [n]))
            dfs(path + [n])
    for p in producers:
        dfs([p])
    return producers, out


def report(name, edges):
    producers, cs = chains(edges)
    levels = {}
    for c in cs:
        for i, n in enumerate(c, 1):
            levels.setdefault(n, set()).add(i)
    longest = max(len(c) for c in cs)
    print(f'== {name}: {len(edges)} edges, producers={producers}')
    for i, c in enumerate(cs, 1):
        print(f'   {i:2d}. ' + ' → '.join(c) + f'   ({len(c)} 个营养级)')
    print(f'   食物链条数 = {len(cs)} ; 最长链营养级数 = {longest}')
    print('   各物种所处营养级: ' + '；'.join(f'{n}{sorted(v)}' for n, v in sorted(levels.items(), key=lambda kv: min(kv[1]))))
    print(f'   选项A(7条食物链) {"成立" if len(cs) == 7 else "不成立"} ; 选项B(最高营养级为第五营养级) {"成立" if longest == 5 else "不成立"}')
    return cs


def diff(a_name, a, b_name, b):
    only_a, only_b = sorted(a - b), sorted(b - a)
    rev = sorted((x, y) for (x, y) in only_a if (y, x) in b)
    print(f'-- {a_name} vs {b_name}: 仅{a_name}有 {only_a or "无"} ; 仅{b_name}有 {only_b or "无"} ; 方向相反 {rev or "无"}')


def source_edges():
    """Parse the source table of Q69 in selection.json (prey row/column layout is detected)."""
    sel = M03 / 'selection.json'
    if not sel.exists():
        return None, None
    data = json.loads(sel.read_text(encoding='utf-8'))
    q = next((o for o in data if o.get('number') == 69 or str(o.get('id', '')).endswith('Q069')), None)
    if q is None:
        return None, None
    return q, q.get('source_question')


if __name__ == '__main__':
    dot = parse_dot(M03 / 'assets' / 'q69_foodweb.dot')
    report('FIGURE(审读者读图)', FIGURE)
    report('DOT(出图源文件)', dot)
    diff('FIGURE', FIGURE, 'DOT', dot)
    q, src = source_edges()
    if src is None:
        print('selection.json 中未找到第69题源题，跳过源表比对')
        sys.exit(0)
    tables = [b for b in src['stem'] if b.get('type') == 'table']
    assert len(tables) == 1, 'expected exactly one source table'
    t = tables[0]
    print(f"源表: {t['title']} ; 表头 {t['headers']} ; {len(t['rows'])} 行 ; 注: {t.get('notes')}")
    src_edges = {(r[0].strip(), r[1].strip()) for r in t['rows']}
    assert len(src_edges) == len(t['rows']), 'duplicate rows in source table'
    report('SOURCE(selection.json 源表)', src_edges)
    diff('FIGURE', FIGURE, 'SOURCE', src_edges)
    diff('DOT', dot, 'SOURCE', src_edges)
    edges_json = json.loads((M03 / '核验记录' / 'q69_foodweb_edges.json').read_text(encoding='utf-8'))
    diff('q69_foodweb_edges.json', {tuple(e) for e in edges_json['edges']}, 'SOURCE', src_edges)
    # current displayed stem vs source stem
    cur = q.get('stem_override') or []
    cur_txt = ''.join(b.get('text', '') for b in cur if b.get('type') == 'text')
    src_txt = ''.join(b.get('text', '') for b in src['stem'] if b.get('type') == 'text')
    print('源题干文字  :', src_txt)
    print('当前题干文字:', cur_txt)
    print('当前选项与源选项是否逐字相同:', {k: q['options'].get(k) == src['options'].get(k) for k in 'ABCD'} if 'options' in q else '（当前无 options 覆盖，沿用源选项）')
    print('编辑答案:', q['answer'], '; source_answer:', q.get('source_answer'))
    nodes_src = {a for a, _ in src_edges} | {b for _, b in src_edges}
    print('源表节点数:', len(nodes_src), sorted(nodes_src))

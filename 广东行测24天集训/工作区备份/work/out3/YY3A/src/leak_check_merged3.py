# -*- coding: utf-8 -*-
"""Cross-editor check for the merged verbal days D07-D09 (YY3A 选词/语句 + YY3B 片段/排序). Adapted from YY2A's
leak_check_merged.py. Two merged orders are checked, because the coordinator has used both:
    order R2 (round-2 assemble_cfg_r2): YY3A GX -> YY3A GY -> YY3A H1..H3 -> YY3B PD (片段) -> YY3B PX (排序)
    order R1 (round-1 assemble_cfg):    YY3A GX -> YY3B PD -> YY3A GY -> YY3B PX -> YY3A H1..H3
Checks
  1. leak: an answer text of a YY3A item (answer_text, blank by blank) appears in any EARLIER stem of the merged day;
     for YY3B items, the text of the keyed option (片段) appears in an EARLIER YY3A stem (10-char pieces);
  2. shared material: a YY3B stem shares >= 3 ten-character pieces with a YY3A passage/article (same day = problem,
     other day = listed for information);
  3. the known pair GD2020X-2 (YY3A, D07) / GD2020Z-9 (片段 whose passage contains that answer): where is GD2020Z-9?
Usage: python3 leak_check_merged3.py [path/to/YY3B/questions.jsonl]"""
import json, re, sys, os, unicodedata

A_Q = '/home/user/work/out3/YY3A/questions.jsonl'
A_ART = '/home/user/work/out3/YY3A/articles.jsonl'
B_Q = sys.argv[1] if len(sys.argv) > 1 else '/home/user/work/out3/YY3B/questions.jsonl'
DAYS = ['D07', 'D08', 'D09']


def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s_（）()　,，。.、；;：:“”"‘’\'！!？?—…\-]', '', s)


def grams(s, n=10):
    return {s[i:i + n] for i in range(len(s) - n + 1)}


def day_of(r):
    return r.get('official_day') or r.get('day_official') or r.get('day')


def main():
    A = [json.loads(l) for l in open(A_Q) if l.strip()]
    ART = {a['aid']: a for a in (json.loads(l) for l in open(A_ART) if l.strip())}
    if not os.path.exists(B_Q):
        print('YY3B questions not found:', B_Q, '-> only YY3A internal order can be checked (see checks.txt).')
        return
    B = [json.loads(l) for l in open(B_Q) if l.strip()]
    problems = 0
    for day in DAYS:
        a = [q for q in A if day_of(q) == day]
        b = [q for q in B if day_of(q) == day]
        b_sort = [q for q in b if '排序' in (q.get('topic') or '')]
        b_other = [q for q in b if q not in b_sort]
        gx = [q for q in a if q['group'].endswith('-GX')]
        gy = [q for q in a if q['group'].endswith('-GY')]
        hh = [q for q in a if '-H' in q['group']]
        orders = {'R2': gx + gy + hh + b_other + b_sort, 'R1': gx + b_other + gy + b_sort + hh}
        for oname, seq in orders.items():
            for i, q in enumerate(seq):
                if q in a:
                    for f in q.get('answer_text') or []:
                        for p in seq[:i]:
                            if f and f in (p.get('stem') or ''):
                                problems += 1
                                print(f'[leak {oname}] {day} {q["id"]} answer “{f}” appears in earlier stem {p["id"]}')
                else:
                    key = (q.get('checked_answer') or q.get('source_answer') or '')
                    opt = (q.get('options') or {}).get(key) if len(key) == 1 else None
                    if opt and '排序' not in (q.get('topic') or ''):
                        g = grams(norm(opt))
                        for p in seq[:i]:
                            if p in a and g and (g & grams(norm(p.get('stem')))):
                                problems += 1
                                print(f'[leak {oname}] {day} {q["id"]} keyed option text overlaps earlier YY3A stem {p["id"]}')
        # 2. shared material
        mats = {}
        for q in a:
            art = ART.get(q['material_or_article'])
            if art:
                mats[art['aid']] = grams(norm(art['text']))
        for q in b:
            g = grams(norm(q.get('stem')))
            for aid, gg in mats.items():
                k = len(g & gg)
                if k >= 3:
                    problems += 1
                    print(f'[same material, same day] {day} YY3B {q["id"]} shares {k} ten-char pieces with {aid}')
        print(f'{day}: YY3A {len(a)}, YY3B {len(b)} (排序 {len(b_sort)}); merged orders R2 and R1 checked')
    # 2b. shared material on other days (information only)
    allmats = {}
    for q in A:
        art = ART.get(q['material_or_article'])
        if art:
            allmats[(art['aid'], day_of(q))] = grams(norm(art['text']))
    info = 0
    for q in B:
        g = grams(norm(q.get('stem')))
        for (aid, d), gg in allmats.items():
            if d != day_of(q) and len(g & gg) >= 3:
                info += 1
                print(f'[info: same material, other day] YY3B {q["id"]} ({day_of(q)}) ~ {aid} ({d})')
    # 3. the known GD2020X-2 / GD2020Z-9 pair
    hit = [q for q in B if (q.get('claim_key') == 'GD2020Z-9') or (q.get('source', {}).get('paper') == 'GD2020Z' and q.get('source', {}).get('qno') == 9)]
    print('[pair] GD2020Z-9 (passage contains the answer of YY3A GD2020X-2, D07):',
          'not used by YY3B' if not hit else ', '.join(f"{q['id']} {day_of(q)}" for q in hit))
    print('problems:', problems, ' info(other-day shared material):', info)


if __name__ == '__main__':
    main()

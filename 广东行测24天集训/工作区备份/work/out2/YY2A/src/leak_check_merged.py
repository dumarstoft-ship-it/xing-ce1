# -*- coding: utf-8 -*-
"""Cross-editor check for the merged verbal day (YY2A 选词/语句 + YY2B 片段/排序), D04-D06.
Assumed merged order per day (same pattern as the round-1 assemble_cfg):
    YY2A <day>-GX (广东选词) -> YY2B non-排序 items -> YY2A <day>-GY (广东语句) -> YY2B 排序 items -> YY2A <day>-H1..H3 (HTML)
Checks
  1. leak: an answer text of a YY2A item appears in any EARLIER stem of the merged day (YY2B stems included);
  2. shared material: a YY2B stem shares >= 3 ten-character pieces with a YY2A passage/article on the SAME day
     (the coordinator asked that items from the same material not sit on the same day).
Usage: python3 leak_check_merged.py [path/to/YY2B/questions.jsonl]"""
import json, re, sys, os, unicodedata

A_Q = '/home/user/work/out2/YY2A/questions.jsonl'
A_ART = '/home/user/work/out2/YY2A/articles.jsonl'
B_Q = sys.argv[1] if len(sys.argv) > 1 else '/home/user/work/out2/YY2B/questions.jsonl'


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
        print('YY2B questions not found:', B_Q, '-> only YY2A internal order can be checked (see checks.txt).')
        return
    B = [json.loads(l) for l in open(B_Q) if l.strip()]
    problems = 0
    for day in ['D04', 'D05', 'D06']:
        a = [q for q in A if day_of(q) == day]
        b = [q for q in B if day_of(q) == day]
        b_sort = [q for q in b if '排序' in (q.get('topic') or '')]
        b_other = [q for q in b if q not in b_sort]
        seq = ([q for q in a if q['group'].endswith('-GX')] + b_other + [q for q in a if q['group'].endswith('-GY')]
               + b_sort + [q for q in a if '-H' in q['group']])
        # 1. leak
        for i, q in enumerate(seq):
            for f in q.get('answer_text') or []:
                for p in seq[:i]:
                    if f and f in (p.get('stem') or ''):
                        problems += 1
                        print(f'[leak] {day} {q["id"]} answer “{f}” appears in earlier stem {p["id"]}')
        # 2. shared material on the same day
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
                    print(f'[same material?] {day} YY2B {q["id"]} shares {k} ten-char pieces with {aid}')
        print(f'{day}: YY2A {len(a)}, YY2B {len(b)} (排序 {len(b_sort)}), merged order checked')
    print('problems:', problems)


if __name__ == '__main__':
    main()

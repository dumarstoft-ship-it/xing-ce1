# -*- coding: utf-8 -*-
"""Cross-editor check for the merged verbal days D10-D12 (YY4A 选词/语句 + YY4B 片段/排序). Adapted from YY3A's
leak_check_merged3.py. Two merged orders are checked, because the coordinator has used both:
    order R2 (round-2 assemble):  YY4A GX -> YY4A H1..H3 -> YY4B PD (片段) -> YY4B PX (排序)
    order R1 (round-1 assemble):  YY4A GX -> YY4B PD -> YY4B PX -> YY4A H1..H3
Mode FULL (YY4B/questions.jsonl exists)
  1. leak: an answer text of a YY4A item (answer_text, blank by blank; single characters skipped) appears in any
     EARLIER stem of the merged day; for YY4B 片段 items, the text of the keyed option overlaps an EARLIER YY4A stem
     (10-character pieces);
  2. shared material: a YY4B stem shares >= 3 ten-character pieces with a YY4A passage / article
     (same day = problem; other day = listed; a 片段 that shares its passage with a YY4A 广东选词 item must not come
     BEFORE that item - an earlier day is a problem);
  3. cross-day preview (information): a YY4A answer of 4+ characters that stands in a YY4B stem of an EARLIER day.
Mode PRELIMINARY (YY4B has registered its claims but not yet written questions.jsonl)
  the source text of every key claimed by YY4B is taken from the index; days are unknown, so the output lists
  (a) shared material with any YY4A passage / article, and (b) every YY4A H-group answer (2+ characters) found in a
  YY4B source text: such a pair must not sit on the same day if the day is assembled in order R1 (片段 before H).
  GX answers are not listed: GX precedes 片段 in both orders.
Usage: python3 leak_check_merged4.py [path/to/YY4B/questions.jsonl]   (appends nothing; redirect to checks_merged.txt)"""
import json, re, sys, os, unicodedata, glob

A_Q = '/home/user/work/out4/YY4A/questions.jsonl'
A_ART = '/home/user/work/out4/YY4A/articles.jsonl'
B_Q = sys.argv[1] if len(sys.argv) > 1 else '/home/user/work/out4/YY4B/questions.jsonl'
CLAIMS = '/home/user/work/out/claims.jsonl'
IDX = '/home/user/work/index'
DAYS = ['D10', 'D11', 'D12']


def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s_（）()　,，。.、；;：:“”"‘’\'！!？?—…\-]', '', s)


def grams(s, n=10):
    return {s[i:i + n] for i in range(len(s) - n + 1)}


def day_of(r):
    return r.get('official_day') or r.get('day_official') or r.get('day')


def is_gd_item(q):
    return str(q['source']['paper']).startswith('GD')


def full(A, ART):
    import time
    B = [json.loads(l) for l in open(B_Q) if l.strip()]
    print(f'YY4A: {A_Q} ({len(A)} questions, file time {time.strftime("%m-%d %H:%M", time.localtime(os.path.getmtime(A_Q)))}); '
          f'YY4B: {B_Q} ({len(B)} questions, file time {time.strftime("%m-%d %H:%M", time.localtime(os.path.getmtime(B_Q)))})')
    problems = info = 0
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
                        if len(f) < 2:
                            continue
                        for p in seq[:i]:
                            if f in (p.get('stem') or ''):
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
                                print(f'[leak {oname}] {day} {q["id"]} keyed option text overlaps earlier YY4A stem {p["id"]}')
        # information: YY4A answers (2+ characters) that stand in a YY4B stem of the same day. With the GX group first
        # (both orders) such a word only turns up AFTER the item has been answered; it would become a leak if a 片段 /
        # 排序 group were ever placed before the YY4A group concerned.
        for q in a:
            for f in q.get('answer_text') or []:
                if len(f) < 2:
                    continue
                hit = [p['id'] for p in b if f in (p.get('stem') or '')]
                if hit:
                    info += 1
                    print(f'[info: answer reappears in a YY4B stem of the same day] {day} {q["id"]} ({q["group"]}) “{f}” in {", ".join(hit)}')
        print(f'{day}: YY4A {len(a)}, YY4B {len(b)} (排序 {len(b_sort)}); merged orders R2 and R1 checked')
    # 2. shared material (any pair of days)
    mats = {}
    for q in A:
        art = ART.get(q['material_or_article'])
        if art:
            mats.setdefault(art['aid'], dict(g=grams(norm(art['text'])), day=day_of(q), gd=is_gd_item(q)))
    for q in B:
        g = grams(norm(q.get('stem')))
        for aid, m in mats.items():
            k = len(g & m['g'])
            if k < 3:
                continue
            db, da = day_of(q), m['day']
            if db == da:
                problems += 1
                print(f'[same material, same day] {db} YY4B {q["id"]} shares {k} ten-char pieces with {aid}')
            elif m['gd'] and db < da:
                problems += 1
                print(f'[same passage, 片段 BEFORE 选词] YY4B {q["id"]} ({db}) ~ {aid} ({da})')
            else:
                info += 1
                print(f'[info: same material, other day] YY4B {q["id"]} ({db}) ~ {aid} ({da})')
    # 3. cross-day preview
    for q in A:
        for f in q.get('answer_text') or []:
            if len(f) < 4:
                continue
            for p in B:
                if day_of(p) < day_of(q) and f in (p.get('stem') or ''):
                    info += 1
                    print(f'[info: answer visible on an earlier day] {q["id"]} ({day_of(q)}) “{f}” in YY4B {p["id"]} ({day_of(p)})')
    print('problems:', problems, ' info:', info)


def preliminary(A, ART):
    keys = []
    for l in open(CLAIMS):
        if l.strip():
            c = json.loads(l)
            if c['owner'] == 'YY4B':
                keys.append(c['key'])
    print(f'YY4B questions.jsonl not found ({B_Q}); preliminary check on the {len(keys)} keys YY4B has registered (days unknown).')
    src = {}
    for key in keys:
        pid, qno = key.rsplit('-', 1)
        for tag in (pid, pid + '_xc'):
            f = f'{IDX}/{tag}.json'
            if not os.path.exists(f):
                continue
            for x in json.load(open(f)):
                if x.get('kind') == 'q' and x['qno'] == int(qno):
                    src[key] = x['text']
            if key in src:
                break
    miss = [k for k in keys if k not in src]
    print(f'source text found for {len(src)} keys' + (f'; NOT found: {miss}' if miss else ''))
    mats = {}
    for q in A:
        art = ART.get(q['material_or_article'])
        if art:
            mats.setdefault(art['aid'], grams(norm(art['text'])))
    shared = 0
    for key, t in src.items():
        g = grams(norm(t))
        for aid, gg in mats.items():
            k = len(g & gg)
            if k >= 3:
                shared += 1
                print(f'[shared material] YY4B {key} shares {k} ten-char pieces with {aid}')
    print(f'shared material between a YY4B source question and a YY4A passage/article: {shared}')
    pairs = 0
    for q in A:
        if not '-H' in q['group']:
            continue
        for f in q.get('answer_text') or []:
            if len(f) < 2:
                continue
            hit = [k for k, t in src.items() if f in t]
            if hit:
                pairs += len(hit)
                print(f'[order R1 only: not on the same day] {q["id"]} ({day_of(q)}, {q["group"]}) answer “{f}” stands in the text of YY4B {", ".join(hit)}')
    print(f'H-group answers found in a YY4B source text: {pairs} pair(s). In order R2 (H before 片段) none of them is a leak; '
          f'in order R1 (片段 before H) a pair is a leak only if both items sit on the same day.')


def main():
    A = [json.loads(l) for l in open(A_Q) if l.strip()]
    ART = {a['aid']: a for a in (json.loads(l) for l in open(A_ART) if l.strip())}
    if os.path.exists(B_Q):
        full(A, ART)
    else:
        preliminary(A, ART)


if __name__ == '__main__':
    main()

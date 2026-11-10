# -*- coding: utf-8 -*-
"""Independent re-check of the delivered YY4A files against the sources (reads questions.jsonl / articles.jsonl only,
does not import build4.py or gd_items4.py).
  GD items
    G1  stem + prompt + options == text layer of the question paper (index/<tag>.json), character by character after
        normalising width, whitespace, blank markers and quote shapes; GD2023X-16 is compared with BOTH copies
        (xing-ce1: no prompt line; xingce 网友回忆版: with the prompt line that the delivered stem borrows);
    G2  source.page == page of the index segment; 2022-2023 answers == answers/<tag>.json;
    G3  restored passage == stem with the blanks filled by answer_text; options[checked] == ' '.join(answer_text);
    G4  the item printed in another paper (source.same_as) has the same canonical text.
  HTML items
    H1  options and answer letter == source data;
    H2  the stem (prompt line removed) with every blank put back == the source paragraph(s), character by character;
        blanks marked （另题） are put back with the other question's text;
    H3  the text at the blank positions == the keyed option (order kept for multi-blank items);
    H4  article objects: paragraphs == source paragraphs; every question of the article is delivered;
    H5  no 常识类 (kind == 'cs') article; three articles a day, one from 南方日报.
  All
    A1  brief_solution empty, checked_answer == source_answer, required fields, ids, counts 12 + 6 per day.
Run: python3 verify4.py  -> prints the result and appends it to checks.txt"""
import json, re, unicodedata, collections, sys

OUT = '/home/user/work/out4/YY4A'
HTML_PATH = '/home/user/xing-ce1/学习资料/盖句精读（词句新版·全151篇·手机版）(2).html'
IDX = '/home/user/work/index'
ANS = '/home/user/work/answers'
BL, LL, OTHER = '______', '____________', '______（另题）'
REQ = ['id', 'module', 'day', 'group', 'group_title', 'topic', 'order', 'source', 'done_status', 'stem', 'options',
       'material_or_article', 'assets', 'source_answer', 'checked_answer', 'brief_solution', 'selection_value',
       'variant_of', 'check_status', 'flags', 'notes']


def canon(s):
    s = unicodedata.normalize('NFKC', s or '')
    s = re.sub(r'\s+', '', s)
    s = re.sub(r'_{2,}', '▁', s)
    s = s.replace('()', '▁')
    for a, b in (('“', '"'), ('”', '"'), ('‘', "'"), ('’', "'")):
        s = s.replace(a, b)
    return s


def canon_index(text):
    s = canon(text)
    s = re.sub(r'^\d+[、.]', '', s)
    return re.sub(r'([ABCD])[、.]', r'\1', s)


def canon_mine(q, with_prompt=True):
    lines = q['stem'].split('\n')
    body = lines[0] if not with_prompt else ''.join(lines)
    s = canon(body) + ''.join(k + canon(q['options'][k]) for k in 'ABCD')
    return s


def index_text(tag, qno):
    for x in json.load(open(f'{IDX}/{tag}.json')):
        if x.get('kind') == 'q' and x['qno'] == qno:
            return x
    return None


def ptext(para):
    return ''.join(sg.get('t', sg.get('m', '')) for sg in para)


def main():
    Q = [json.loads(l) for l in open(f'{OUT}/questions.jsonl') if l.strip()]
    A = {a['aid']: a for a in (json.loads(l) for l in open(f'{OUT}/articles.jsonl') if l.strip())}
    raw = open(HTML_PATH, encoding='utf-8').read()
    D = json.loads(re.search(r'<script id="data" type="application/json">(.*?)</script>', raw, re.S).group(1))
    ART = {a['id']: a for a in D}
    bad, log, notes = [], [], []
    ok = collections.Counter()

    # ---------- A1
    assert len(Q) == 54 and [q['id'] for q in Q] == [f'YY4A-{i:03d}' for i in range(1, 55)]
    for q in Q:
        miss = [k for k in REQ if k not in q]
        if miss: bad.append((q['id'], 'missing fields', miss))
        if q['brief_solution'] != '': bad.append((q['id'], 'brief_solution not empty'))
        if q['checked_answer'] != q['source_answer'] or q['checked_answer'] not in 'ABCD': bad.append((q['id'], 'answer'))
        if sorted(q['options']) != ['A', 'B', 'C', 'D']: bad.append((q['id'], 'options keys'))
        if q['material_or_article'] not in A: bad.append((q['id'], 'article object missing'))
        if q['done_status'] != '已做情况未知' or q['variant_of'] is not None: bad.append((q['id'], 'status'))
        ok['A1'] += 1
    for day in ('D10', 'D11', 'D12'):
        tc = collections.Counter(q['topic'] for q in Q if q['day'] == day)
        if tc != {'选词填空': 12, '语句填空': 6}: bad.append((day, 'counts', dict(tc)))

    # ---------- GD
    for q in Q:
        s = q['source']
        if not s['paper'].startswith('GD'):
            continue
        yr = int(s['paper'][2:6])
        if not 2017 <= yr <= 2023: bad.append((q['id'], 'GD year out of range', yr))
        x = index_text(s['paper'], s['qno'])
        if x is None:
            bad.append((q['id'], 'not in index')); continue
        ci = canon_index(x['text'])
        has_prompt_in_index = True
        if '提示语取自xingce版' in q['flags']:
            # xing-ce1 copy: no prompt line; xingce copy: prompt line present
            if canon_mine(q, with_prompt=False) != ci: bad.append((q['id'], 'G1 xing-ce1 text differs', canon_mine(q, False), ci))
            xc = index_text(s['paper'] + '_xc', s['qno'])
            cxc = canon_index(xc['text'])
            # In the xingce copy the underline is a drawn line, not characters (text layer: "锲而不舍,      ,就一定…"),
            # so the blank marker is dropped on both sides for this one comparison; the page image shows the underline
            # (looked at: scratch render GD2023X_xc_q16.png). The copy's text also carries the page footer after option D.
            if not cxc.replace('▁', '').startswith(canon_mine(q, with_prompt=True).replace('▁', '')):
                bad.append((q['id'], 'G1 xingce text differs', canon_mine(q), cxc))
            notes.append(f"{q['id']} {s['paper']}-{s['qno']}: xingce 版文字层里横线是图形、不成字符，该版按去掉空缺标记后比较（页图已目视核对）")
            ok['G1 (both copies)'] += 1
        else:
            if canon_mine(q) != ci: bad.append((q['id'], 'G1 text differs', canon_mine(q), ci))
            ok['G1'] += 1
        if x['segs'][0][0] + 1 != s['page']: bad.append((q['id'], 'G2 page', x['segs'][0][0] + 1, s['page']))
        if x['file'] != s['file']: bad.append((q['id'], 'G2 file', x['file'], s['file']))
        ok['G2 page/file'] += 1
        if yr >= 2022:
            for tag in (s['paper'], s['paper'] + '_xc'):
                a = json.load(open(f'{ANS}/{tag}.json'))
                aa = (a.get('answers') or a)[str(s['qno'])]['ans']
                if aa != q['checked_answer']: bad.append((q['id'], 'G2 answers json', tag, aa))
                ok['G2 answers/*.json'] += 1
        art = A[q['material_or_article']]
        body = q['stem'].split('\n')[0]
        fills = list(q['answer_text'])
        toks = re.findall(r'_{6,}|（\s*）', body)
        if len(toks) != len(fills): bad.append((q['id'], 'G3 blank count', toks, fills))
        rest = body
        for f in fills:
            m = re.search(r'_{6,}|（\s*）', rest)
            rest = rest[:m.start()] + f + rest[m.end():]
        if rest != art['text']: bad.append((q['id'], 'G3 restored text', rest, art['text']))
        if ' '.join(fills) != q['options'][q['checked_answer']]: bad.append((q['id'], 'G3 fills vs option'))
        if art['kind'] != 'restored_from_answer' or art['external_original']['text'] is not None: bad.append((q['id'], 'G3 article kind'))
        ok['G3'] += 1
        for other in s.get('same_as') or []:
            tag, qno = other.rsplit('-', 1)
            y = index_text(tag, int(qno))
            if y is None or canon_index(y['text']) != ci: bad.append((q['id'], 'G4 same_as text differs', other))
            ok['G4 same_as'] += 1

    # ---------- HTML
    by_art = collections.defaultdict(list)
    for q in Q:
        s = q['source']
        if not s['paper'].startswith('HTML'):
            continue
        aid, qid = s['qno'].split(':')
        a = ART[aid]
        by_art[aid].append(qid)
        sq = [x for x in a['q'] if x['id'] == qid][0]
        if [q['options'][k] for k in 'ABCD'] != sq['options'] or 'ABCD'[sq['answer']] != q['checked_answer']:
            bad.append((q['id'], 'H1 options/answer'))
        if q['topic'] != sq['kind']: bad.append((q['id'], 'H1 kind'))
        ok['H1'] += 1
        lines = q['stem'].split('\n')
        paras, prompt = lines[:-1], lines[-1]
        if not prompt.startswith(('填入画横线部分', '依次填入画横线部分')): bad.append((q['id'], 'H2 prompt line', prompt))
        pnos = s['context_paras']
        if len(paras) != len(pnos): bad.append((q['id'], 'H2 paragraph count', len(paras), pnos)); continue
        delivered = set(x.split(':')[1] for x in (qq['source']['qno'] for qq in Q if qq['source']['paper'].startswith('HTML') and qq['source']['qno'].startswith(aid + ':')))
        for stem_p, pno in zip(paras, pnos):
            src = ptext(a['paras'][pno - 1])
            # blanks of this paragraph in text order: (begin, end, marker)
            spans = []
            for x in a['q']:
                if x['p'] != pno or x['id'] not in delivered: continue
                for b in x['blanks']:
                    mark = (LL if x['kind'] == '语句填空' else BL) if (x['id'] == qid and pno == sq['p']) else OTHER
                    spans.append((b['b'], b['e'], mark))
            spans.sort()
            # rebuild the expected stem paragraph from the source and compare; then restore and compare the other way
            exp, pos = '', 0
            for b, e, mark in spans:
                exp += src[pos:b] + mark; pos = e
            exp += src[pos:]
            if exp != stem_p: bad.append((q['id'], 'H2 stem paragraph differs from source', pno))
            rest, cur = '', stem_p
            for b, e, mark in spans:
                i = cur.find(mark)
                if i < 0: bad.append((q['id'], 'H2 marker not found', mark)); break
                # OTHER starts with BL: make sure an own BL is not matched inside OTHER
                if mark == BL and cur[i:i + len(OTHER)] == OTHER: bad.append((q['id'], 'H2 marker order')); break
                rest += cur[:i] + src[b:e]; cur = cur[i + len(mark):]
            rest += cur
            if rest != src: bad.append((q['id'], 'H2 restored paragraph differs from source', pno))
            ok['H2 paragraphs'] += 1
        fills = [ptext(a['paras'][sq['p'] - 1])[b['b']:b['e']] for b in sq['blanks']]
        if fills != q['answer_text'] or ' '.join(fills) != q['options'][q['checked_answer']]: bad.append((q['id'], 'H3 blank text vs option', fills))
        if s['blanks'] != sq['blanks'] or s['para'] != sq['p']: bad.append((q['id'], 'H3 positions'))
        ok['H3'] += 1
    for aid, qids in by_art.items():
        a = ART[aid]
        art = A['ART-HTML-' + aid]
        if art['paras'] != [ptext(p) for p in a['paras']]: bad.append((aid, 'H4 article paragraphs differ'))
        if qids != [x['id'] for x in a['q']]: bad.append((aid, 'H4 not every question delivered / order', qids))
        if a['kind'] == 'cs': bad.append((aid, 'H5 常识类'))
        if art['kind'] != 'html_original': bad.append((aid, 'H4 kind'))
        if art['text'].split('\n')[4:] != art['paras']: bad.append((aid, 'H4 text body'))
        ok['H4 articles'] += 1
    for day in ('D10', 'D11', 'D12'):
        arts = []
        for q in Q:
            if q['day'] == day and q['source']['paper'].startswith('HTML'):
                aid = q['source']['qno'].split(':')[0]
                if aid not in arts: arts.append(aid)
        nf = [x for x in arts if ART[x]['src'] == '南方日报']
        if len(arts) != 3 or len(nf) != 1: bad.append((day, 'H5 articles per day', arts))
        ok['H5 days'] += 1

    # ---------- C1 claim registry: every key (and same_as key) is held by YY4A under the question's id; nothing else is held
    held = {}
    for l in open('/home/user/work/out/claims.jsonl'):
        if l.strip():
            c = json.loads(l)
            if c['owner'] == 'YY4A':
                held.setdefault(c['key'], []).append(c.get('note', ''))
    want = {}
    for q in Q:
        for key in [q['claim_key']] + list(q['source'].get('same_as') or []):
            want[key] = q['id']
    for key, qid in want.items():
        if key not in held: bad.append((qid, 'C1 key not registered', key))
        elif not any(qid in n for n in held[key]): bad.append((qid, 'C1 registry note does not carry the id', key, held[key]))
        ok['C1 claims'] += 1
    extra = sorted(set(held) - set(want))
    if extra: bad.append(('registry', 'C1 keys held by YY4A but not delivered', extra))
    for q in Q:
        ck = q['claim_key']
        if q['source']['paper'].startswith('GD') and ck != f"{q['source']['paper']}-{q['source']['qno']}": bad.append((q['id'], 'C1 claim_key'))
        if q['source']['paper'].startswith('HTML') and ck != 'HTML:' + q['source']['qno']: bad.append((q['id'], 'C1 claim_key'))

    log.append('[verify4] independent re-check from the delivered files: ' + ('0 mismatches' if not bad else f'{len(bad)} MISMATCHES'))
    log.append('[verify4] checks passed: ' + '; '.join(f'{k} {v}' for k, v in ok.items()))
    for x in notes:
        log.append('   note: ' + x)
    for b in bad:
        log.append('   ' + repr(b)[:600])
    print('\n'.join(log))
    if '--no-log' not in sys.argv:
        open(f'{OUT}/checks.txt', 'a').write('\n'.join(log) + '\n')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())

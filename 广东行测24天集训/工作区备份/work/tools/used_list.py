import json, csv, sys, collections
PKG = sys.argv[1]
qs = [json.loads(l) for l in open(f'{PKG}/questions.jsonl')]
res = [json.loads(l) for l in open(f'{PKG}/备选与冲突待复核.jsonl')]
def skey(q):
    s = q['source']; p = str(s.get('paper') or '')
    if p.startswith('HTML'): return f"HTML:{s.get('article_id') or ''}:{str(s.get('qno')).split(':')[-1]}"
    return f"{p.replace('_xc','')}-{s.get('qno')}"
inpkg = {skey(q): q['id'] for q in qs}
inres = {skey(r): r['id'] for r in res}
claims = [json.loads(l) for l in open('/home/user/work/out/claims.jsonl')]
import os
R1_OWNERS = {'ZL-A', 'ZL-B', 'PD-A', 'PD-B', 'PD-C', 'YY-A', 'YY-B'}
R1PKG = os.environ.get('R1PKG', '/home/user/work/build/pkg2')
r1pkg = {skey(q): q['id'] for q in (json.loads(l) for l in open(f'{R1PKG}/questions.jsonl'))} if PKG.rstrip('/') != R1PKG.rstrip('/') else {}
import re as _re
R2PKG = os.environ.get('R2PKG', '/home/user/work/build/pkg_r2')
r2pkg = {skey(q): q['id'] for q in (json.loads(l) for l in open(f'{R2PKG}/questions.jsonl'))} if (PKG.rstrip('/') != R2PKG.rstrip('/') and os.path.exists(f'{R2PKG}/questions.jsonl')) else {}
R3PKG = os.environ.get('R3PKG', '/home/user/work/build/pkg_r3')
r3pkg = {skey(q): q['id'] for q in (json.loads(l) for l in open(f'{R3PKG}/questions.jsonl'))} if (PKG.rstrip('/') != R3PKG.rstrip('/') and os.path.exists(f'{R3PKG}/questions.jsonl')) else {}
CUR = os.environ.get('CUR_ROUND', '3')
def round_of(o):
    if o in R1_OWNERS: return '第1轮'
    m = _re.match(r'^(ZL|PD|YY)(\d)[A-Z]$', o)
    if m and m.group(2) != CUR: return f'第{m.group(2)}轮'
    if o.startswith('GPT-'): return f"GPT {o.split('-',1)[1]} 数量"
    if o.startswith('已做'): return '用户已做（42天习题本前三天）'
    return '本轮'
rows = []; seen = set()
for q in qs:
    k = skey(q); seen.add(k)
    rows.append(dict(key=k, status='入包', final_id=q['id'], editor=q['editor'], note=''))
for r in res:
    k = skey(r); seen.add(k)
    why = r.get('why_not_in_package') or ''
    st = '未入包·冲突待复核' if '冲突' in why else ('未入包·超出配额（登记已释放）' if '配额' in why else ('未入包·备选' if '备选' in why else '未入包'))
    rows.append(dict(key=k, status=st, final_id='', editor=r['editor'], note=r['id']))
for c in claims:
    for k in [c['key']] + [d for d in c.get('dups', []) if d != c['key']]:
        kk = k.replace('_xc', '')
        if kk in seen: continue
        seen.add(kk)
        ck = c['key'].replace('_xc', '')
        o = c['owner']
        rnd = round_of(o)
        if k != c['key']: st = rnd + '·同题锁定'
        elif k.startswith('MAT:'): st = rnd + '·材料登记'
        elif rnd == '第1轮': st = '第1轮·入包' if ck in r1pkg else '第1轮·登记未入包'
        elif rnd == '第2轮': st = '第2轮·入包' if ck in r2pkg else '第2轮·登记未入包'
        elif rnd == '第3轮': st = '第3轮·入包' if ck in r3pkg else '第3轮·登记未入包'
        elif rnd == '本轮': st = '本轮·登记未入包'
        elif rnd.startswith('用户已做'): st = rnd + '·锁定'
        else: st = rnd + '·已用'
        fid = inpkg.get(ck) or r1pkg.get(ck) or r2pkg.get(ck) or r3pkg.get(ck, '')
        rows.append(dict(key=kk, status=st, final_id=fid, editor=c['owner'], note=(c.get('note') or '')[:60]))
with open(f'{PKG}/已用题登记.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=['key', 'status', 'final_id', 'editor', 'note']); w.writeheader(); w.writerows(rows)
print(collections.Counter(r['status'] for r in rows))

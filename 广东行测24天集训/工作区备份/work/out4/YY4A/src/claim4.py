# -*- coding: utf-8 -*-
"""Register every source key of YY4A in the shared claim registry: `claim.py check <key>` first, then `take <key> YY4A <note>`.
Idempotent: a key already held by YY4A is reported and not taken twice. Writes claims_log.txt next to questions.jsonl.
Extra keys (same item printed in a paper that qindex does not group with it) come from source.same_as."""
import json, subprocess, sys
OUT = '/home/user/work/out4/YY4A'
CL = '/home/user/work/tools/claim.py'
mine = set()
for l in open('/home/user/work/out/claims.jsonl'):
    if l.strip():
        c = json.loads(l)
        if c['owner'] == 'YY4A':
            mine.add(c['key'])
log, bad = [], 0
for l in open(f'{OUT}/questions.jsonl'):
    q = json.loads(l)
    keys = [q['claim_key']] + [k for k in (q['source'].get('same_as') or [])]
    kind = '选词' if q['topic'] == '选词填空' else '语句'
    for j, key in enumerate(keys):
        note = f"{q['day']}{kind}-{q['id']}" + ('（HTML一文多题）' if key.startswith('HTML:') else '') + ('（同题他卷，随 %s 一并登记）' % q['claim_key'] if j else '')
        chk = subprocess.run([sys.executable, CL, 'check', key], capture_output=True, text=True).stdout.strip()
        if key in mine:
            log.append(f'{key}\tcheck: {chk}\talready held by YY4A, not taken again'); continue
        if chk != 'FREE' and 'TAKEN by YY4A' not in chk:
            bad += 1; log.append(f'{key}\tcheck: {chk}\tNOT TAKEN - conflict'); continue
        tk = subprocess.run([sys.executable, CL, 'take', key, 'YY4A', note], capture_output=True, text=True).stdout.strip()
        if not tk.startswith('OK'):
            bad += 1
        log.append(f'{key}\tcheck: {chk}\ttake: {tk}\t{note}')
log.append(f'conflicts: {bad}')
open(f'{OUT}/claims_log.txt', 'a').write('\n'.join(log) + '\n')
print('\n'.join(log))

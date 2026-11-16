# Compare source records (全部题目.jsonl) with M05 selection.json / 题目.jsonl entries for Q46-50 (read-only)
import json, hashlib, os
REPO = '/home/user/xing-ce1'
SRC = REPO + '/模考/2026下半年广东卷_16-33季_AI可读/全部题目.jsonl'
M05 = REPO + '/广东行测18套模拟/M05/'
nums = {46: 'gd-mock-2026h2-s19-q46', 47: 'gd-mock-2026h2-s27-q47', 48: 'gd-mock-2026h2-s31-q48', 49: 'gd-mock-2026h2-s20-q50', 50: 'gd-mock-2026h2-s23-q49'}
src = {}
for line in open(SRC, encoding='utf-8'):
    line = line.strip()
    if not line: continue
    r = json.loads(line)
    if r.get('id') in nums.values(): src[r['id']] = r
sel = {q['number']: q for q in json.load(open(M05 + 'selection.json', encoding='utf-8'))}
tim = {}
for line in open(M05 + '题目.jsonl', encoding='utf-8'):
    line = line.strip()
    if not line: continue
    r = json.loads(line)
    n = r.get('number')
    if n in nums: tim[n] = r
def norm(blocks):
    out = []
    for b in blocks:
        if b.get('type') == 'text': out.append(('text', b['text']))
        elif b.get('type') == 'figure': out.append(('figure', b.get('asset_id')))
        else: out.append((b.get('type'), json.dumps(b, ensure_ascii=False)))
    return out
print('source sha256(全部题目.jsonl)=', hashlib.sha256(open(SRC, 'rb').read()).hexdigest())
for n, sid in nums.items():
    s = src[sid]; q0 = sel[n]; q = q0.get('source_question', q0)
    print('==== Q%d  %s  source answer field: %r' % (n, sid, s.get('answer')))
    print('  stem equal (selection vs source):', norm(q['stem']) == norm(s['stem']))
    print('  options equal (selection vs source):', {k: norm(v) for k, v in q['options'].items()} == {k: norm(v) for k, v in s['options'].items()})
    print('  edits:', q0.get('edits'))
    print('  source_question deep-equal to source record (ignoring path prefix):', json.dumps(q, ensure_ascii=False, sort_keys=True) == json.dumps(s, ensure_ascii=False, sort_keys=True))
    if n in tim:
        t = tim[n]
        print('  题目.jsonl keys:', list(t.keys()))
        print('  stem equal (题目.jsonl vs source):', norm(t.get('stem', [])) == norm(s['stem']))
        print('  options equal (题目.jsonl vs source):', {k: norm(v) for k, v in t.get('options', {}).items()} == {k: norm(v) for k, v in s['options'].items()})
        figs = [b for b in t.get('stem', []) if b.get('type') == 'figure']
        print('  题目.jsonl figure blocks:', [(b.get('asset_id'), b.get('path')) for b in figs])
    print('  source stem text:', [b['text'] for b in s['stem'] if b['type'] == 'text'])
    print('  source options:', {k: [b.get('text') for b in v] for k, v in s['options'].items()})
    print('  source keys:', list(s.keys()))
    # asset hash
    for b in s['stem']:
        if b['type'] == 'figure':
            p = REPO + '/模考/2026下半年广东卷_16-33季_AI可读/' + b['path']
            print('  asset', b['asset_id'], 'sha256=', hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16], 'size', os.path.getsize(p))

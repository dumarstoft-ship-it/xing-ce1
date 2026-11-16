# Read-only: compare M05 Q66-70 (selection.json source_question / 题目.jsonl) with bank 全部题目.jsonl
import json
BANK = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/全部题目.jsonl'
SEL = '/home/user/xing-ce1/广东行测18套模拟/M05/selection.json'
TJ = '/home/user/xing-ce1/广东行测18套模拟/M05/题目.jsonl'
bank = {}
with open(BANK) as fh:
    for line in fh:
        line = line.strip()
        if not line: continue
        o = json.loads(line)
        bank[o['id']] = o
sel = {it['number']: it for it in json.load(open(SEL))}
tj = {}
with open(TJ) as fh:
    for line in fh:
        line = line.strip()
        if not line: continue
        o = json.loads(line)
        tj[o.get('number')] = o
print("题目.jsonl keys:", list(next(iter(tj.values())).keys()))
def norm(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True)
for n in range(66, 71):
    s = sel[n]
    sid = s['source_id']
    b = bank.get(sid)
    print('=' * 90)
    print(n, sid, 'in bank:', b is not None)
    if b is None: continue
    print('bank keys:', list(b.keys()))
    print('bank answer field:', {k: b.get(k) for k in b if 'answer' in k or 'analysis' in k})
    sq = s['source_question']
    # compare text parts
    for part in ('stem', 'options'):
        same = norm(sq[part]) == norm(b[part])
        print(f'  selection.source_question.{part} == bank.{part}: {same}')
    t = tj.get(n)
    if t:
        for part in ('stem', 'options'):
            if part in t:
                # compare only text payloads
                def texts(x):
                    out = []
                    def walk(y):
                        if isinstance(y, dict):
                            if y.get('type') == 'text': out.append(y['text'])
                            elif y.get('type') == 'figure': out.append('[FIG ' + str(y.get('asset_id')) + ']')
                            else:
                                for v in y.values(): walk(v)
                        elif isinstance(y, list):
                            for v in y: walk(v)
                    walk(x); return out
                same = texts(t[part]) == texts(b[part])
                print(f'  题目.jsonl.{part} texts == bank: {same}')
                if not same:
                    print('    M05:', texts(t[part]))
                    print('    BANK:', texts(b[part]))
        for k in t:
            if k not in ('stem', 'options'):
                v = t[k]
                vs = json.dumps(v, ensure_ascii=False)
                print(f'  题目.jsonl[{k}] = {vs[:300]}')

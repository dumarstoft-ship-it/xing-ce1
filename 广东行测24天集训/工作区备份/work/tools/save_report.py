"""从子编者的会话记录里取出它最后交回的报告，另存成文件（省得主编重抄）。
用法：python3 save_report.py <agentId> <输出路径> ["首行说明"]"""
import json, sys
T = '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/tasks/'
aid, out = sys.argv[1], sys.argv[2]
head = sys.argv[3] if len(sys.argv) > 3 else '> 子编者没有写 report.md，由主编按其交回原文另存。'
txt = None
for l in open(T + aid + '.output'):
    try: r = json.loads(l)
    except Exception: continue
    c = (r.get('message') or {}).get('content')
    if isinstance(c, list):
        for x in c:
            if x.get('type') == 'tool_use' and x.get('name') == 'SubagentHandback':
                inp = x.get('input') or {}
                cand = max((v for v in inp.values() if isinstance(v, str)), key=len, default=None)
                if cand: txt = cand
if not txt: sys.exit('no handback found')
lines = txt.split('\n')
if lines and lines[0].startswith('# '): txt = lines[0] + '\n\n' + head + '\n' + '\n'.join(lines[1:])
else: txt = head + '\n\n' + txt
open(out, 'w', encoding='utf-8').write(txt.rstrip() + '\n')
print(out, len(txt), 'chars;', lines[0][:60])

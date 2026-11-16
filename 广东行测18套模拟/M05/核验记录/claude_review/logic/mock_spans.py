# For each mock-bank source question used in M05 Q51-65, list per-line source_spans (PDF pt bboxes)
# to infer which line breaks in the original are hard (new paragraph) vs soft wraps. Read-only.
import json
REPO='/home/user/xing-ce1'
sel={q['number']:q for q in json.load(open(f'{REPO}/广东行测18套模拟/M05/selection.json',encoding='utf-8')) if 51<=q['number']<=65}
gd={}
for l in open(f'{REPO}/模考/2026下半年广东卷_16-33季_AI可读/全部题目.jsonl',encoding='utf-8'):
    r=json.loads(l); gd[r['id']]=r
for n in range(51,66):
    sid=sel[n]['source_id']
    if sid not in gd: continue
    r=gd[sid]
    print('='*8, 'M05', n, sid, 'pages', r['source_pages'])
    stem=''.join(b.get('text','') for b in r['stem'])
    print('  stem text lines:', [ln for ln in stem.split('\n')])
    xs=[s['bbox_pt'][0] for s in r['source_spans']]; xe=[s['bbox_pt'][2] for s in r['source_spans']]
    right=max(xe)
    for s in r['source_spans']:
        x0,y0,x1,y1=s['bbox_pt']
        print(f"   p{s['pdf_page']} x0={x0:7.2f} y0={y0:7.2f} x1={x1:7.2f} y1={y1:7.2f} width={x1-x0:6.1f} {'FULL' if x1>right-6 else ''}")

# 只读：核对来源登记.jsonl中第1—15题的 provenance/答案与 selection.json 是否一致，并列出编辑“原创题依据核对.json”
import json
M = '/home/user/xing-ce1/广东行测18套模拟/M05/'
sel = {q['number']: q for q in json.load(open(M + 'selection.json', encoding='utf-8')) if q['number'] <= 15}
reg = {r['number']: r for r in (json.loads(l) for l in open(M + '来源登记.jsonl', encoding='utf-8') if l.strip()) if r['number'] <= 15}
for n in range(1, 16):
    s, r = sel[n], reg.get(n)
    if r is None:
        print(n, '来源登记缺此题'); continue
    same_prov = s['provenance'] == r['provenance']
    same_ans = s['answer'] == r['editor_answer']
    print(n, s['source_id'], '答案', s['answer'], '| 登记答案一致', same_ans, '| provenance一致', same_prov, '| edits', s['edits'], '| 状态', s['verification']['status'])
print()
print(json.dumps(json.load(open(M + '编辑记录/原创题依据核对.json', encoding='utf-8')), ensure_ascii=False, indent=1))

#!/usr/bin/env python3
"""核对 selection.json 中第31-45题的 source_question 与源库 全部题目.jsonl 同ID对象逐字段相等；
并检查这些题使用的公式图片在源库转写记录中：同一图片哈希是否始终转写为同一文本（跨季交叉印证）。只读仓库。"""
import json, sys, collections
from pathlib import Path
ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/home/user/xing-ce1')
bank = ROOT/'模考/2026下半年广东卷_16-33季_AI可读'
src = {}
with open(bank/'全部题目.jsonl', encoding='utf-8') as fh:
    for line in fh:
        if line.strip():
            q = json.loads(line); src[q['id']] = q
sel = [x for x in json.load(open(ROOT/'广东行测18套模拟/M03/selection.json', encoding='utf-8')) if 31 <= x['number'] <= 45]
out = {}
for x in sel:
    sq = x['source_question']; b = src.get(x['source_id'])
    out[x['number']] = {'source_id': x['source_id'], 'equal_to_bank': b == sq, 'bank_answer': None if b is None else b.get('answer'),
                        'assets': sq.get('source_asset_ids')}
    print(x['number'], x['source_id'], 'source_question==源库对象:', b == sq, '源库answer:', None if b is None else b.get('answer'))
# 公式图片哈希一致性
recs = json.load(open(bank/'转写核验记录.json', encoding='utf-8'))
by_hash = collections.defaultdict(set); by_asset = {}
for r in recs:
    h = r.get('source_image_sha256')
    if h:
        by_hash[h].add(json.dumps(r.get('text') or r.get('rows'), ensure_ascii=False))
    by_asset[r['asset_id']] = r
print('\n本模块题用到的转写资产：')
for n, v in out.items():
    for aid in v['assets'] or []:
        r = by_asset.get(aid)
        if not r: print(' ', n, aid, '无转写记录'); continue
        h = r.get('source_image_sha256'); same = [a for a, rr in by_asset.items() if rr.get('source_image_sha256') == h and a != aid]
        print(f"  第{n}题 {aid}: {r.get('text') or r.get('title')}  同哈希其他资产: {same}  同哈希文本是否唯一: {len(by_hash[h]) == 1}")
conflicts = {h: t for h, t in by_hash.items() if len(t) > 1}
print('\n全源库同一图片哈希对应不同转写文本的数量:', len(conflicts))
json.dump({'per_question': out, 'hash_conflicts_in_bank': len(conflicts)}, open(Path(__file__).resolve().parent/'source_fidelity_check.json', 'w'), ensure_ascii=False, indent=1)

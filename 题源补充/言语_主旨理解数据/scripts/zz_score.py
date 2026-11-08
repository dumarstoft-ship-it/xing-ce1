"""主旨题对答案：python3 -I zz_score.py <卷名，如 ZP3>   读 zz/keys/卷_<卷名>.key.json 和 zz/answers/卷_<卷名>_s*.json
打印每位作答者对了多少、把握分布，以及选错的题、把握低的题（附理由和疑问）。"""
import json, sys, os, glob, collections
SP = '/tmp/claude-0/-home-user-xingce/c27c4f14-7f89-5a62-8e0a-9c6994ddaec0/scratchpad'
tag = sys.argv[1]
key = json.load(open(f'{SP}/zz/keys/卷_{tag}.key.json'))
# 出题人标了争议题的，对答案时标出来（选了别项不一定退回）
cont = set()
try:
    for art in json.load(open(f'{SP}/zz/out/Z_{tag}.json'))['articles']:
        cont |= {f"{art['id']}#{i}" for i, q in enumerate(art['questions'], 1) if q.get('contested')}
except Exception: pass
if cont: print('出题人标的争议题：', len(cont), '道')
for f in sorted(glob.glob(f'{SP}/zz/answers/卷_{tag}_s*.json')):
    s = json.load(open(f))
    ok = sum(s.get(k, {}).get('pick') == a for k, a in key.items())
    print(f'{os.path.basename(f)}：{ok}/{len(key)}，把握', dict(collections.Counter(v.get('sure') for v in s.values())))
    for k, a in key.items():
        v = s.get(k, {})
        if v.get('pick') != a or v.get('sure') == '低':
            print(f"  {'■ 选错' if v.get('pick') != a else '□ 低把握'}{'【争议题】' if k in cont else ''} {k} 答案 {a}，选 {v.get('pick')}（{v.get('sure')}）：{v.get('why','')} ｜疑问：{v.get('doubt','')}")
    if cont: print('  争议题里选中', sum(s.get(k, {}).get('pick') == key[k] for k in cont), '/', len(cont))

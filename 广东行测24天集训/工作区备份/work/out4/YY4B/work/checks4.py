import json, collections, re, os, subprocess, time
OUT='/home/user/work/out4/YY4B'
Q=[json.loads(l) for l in open(f'{OUT}/questions.jsonl')]
A=[json.loads(l) for l in open(f'{OUT}/articles.jsonl')]
L=[]
v=subprocess.run(['python3','/home/user/work/tools/validate.py','YY4B'],capture_output=True,text=True,env=dict(os.environ,OUT_DIR='/home/user/work/out4')).stdout.strip().split('\n')
L.append(f'[validate] OUT_DIR=/home/user/work/out4 tools/validate.py YY4B: {v[-1] if "issues" in v[-1] else v}  （{v[0]}）')
scan=[q for q in Q if '答案取自扫描件' in q['flags']]
txt=[q for q in Q if '答案取自扫描件' not in q['flags']]
tw=[q for q in txt if '同题他卷解析' in q['notes']]
L.append(f'[answers] {len(txt)} 道有文字层解析：答案句逐题提取，全部与 answers/ 自动抽取一致；其中 {len(tw)} 道另与同题他卷的文字层解析交叉核对，0 处不一致')
L.append(f'[answers] {len(scan)} 道解析为扫描件，出图目读：' + '、'.join(f"{q['id']} {q['claim_key']}（{q['checked_answer']}" + (f"，{q['source_rate']}%" if q['source_rate'] else '') + '）' for q in scan))
L.append('[answers] 扫描件旁证：GD2016Z-15（GD2016X-27 的乡镇卷同题）目读亦为 D；GD2015Z-20（GD2015X-20 的乡镇卷同题，选项次序不同）目读为 C，所指选项内容与县级卷 D 相同；GK2021F 解析同页第44题“B，64%”与 GK2021D-52 文字层解析一致')
d=[q for q in Q if q['dispute_note']]
L.append(f'[answers] 原标争议 {len(d)} 道' + ('：' + '、'.join(q['id'] for q in d) if d else '（66 道及其同题他卷解析的题段内均无“争议”字样）'))
pat=[q for q in Q if any(f in q['flags'] for f in ('文字层缺字已据原页补录','文字层码位已据原页改正'))]
L.append(f'[text] 66 题题干与选项逐题对原页截图核对（assets/src/YY4B-xxx.png；核对时每 2—4 题拼一图目读，见 work/vb/）；据原页改正 {len(pat)} 题：' + '；'.join(f"{q['id']} {q['claim_key']}" for q in pat) + '；另 YY4B-013 删去粘连的下一部分标题尾巴、YY4B-038 恢复选项内空格、YY4B-018 半角冒号改全角、YY4B-051“排他心里”原卷如此照录')
L.append('[text] 与同题他卷文字层逐字比对 33 对：仅 2 处不同且均在预期内（GD2016X-27 与 GD2016Z-15 设问句标点不同；GK2016F-52 已把“―”改回“一”）')
def cn(q):
    p=q['source']['paper']
    return '广东省考' if p.startswith('GD') and not p.startswith('GDXD') else '广东选调' if p.startswith('GDXD') else '国考' if p.startswith('GK') else '外省'
for day in ['D10','D11','D12']:
    for g in ['PD','PX']:
        qs=[q for q in Q if q['day']==day and q['group'].endswith(g)]
        a=collections.Counter(q['checked_answer'] for q in qs); s=collections.Counter(cn(q) for q in qs)
        y=collections.Counter(re.search(r'\d{4}',q['source']['paper']).group() for q in qs if q['source']['paper'].startswith('GK'))
        t=collections.Counter(q['topic'] for q in qs)
        L.append(f'[dist] {day} {g}: 答案 {dict(sorted(a.items()))} 来源 {dict(s)} 国考年度 {dict(sorted(y.items()))} 题型 {dict(t)}')
tot=collections.Counter(q['topic'] for q in Q if q['group'].endswith('PD'))
L.append(f'[dist] 片段 54 题型合计 {dict(tot)}；答案合计 {dict(sorted(collections.Counter(q["checked_answer"] for q in Q if q["group"].endswith("PD")).items()))}')
gk=[q for q in Q if q['group'].endswith('PD') and q['source']['paper'].startswith('GK')]
new=[q for q in gk if int(q['source']['paper'][2:6])>=2017]
L.append(f'[dist] 国考片段 {len(gk)}：2017—2025 年度 {len(new)}（其中科技说明文 3，每天 1），2013—2016 年度 {len(gk)-len(new)}')
claims=[json.loads(l) for l in open('/home/user/work/out/claims.jsonl') if l.strip()]
mine=[c for c in claims if c['owner']=='YY4B']
L.append(f'[claims] 66 题逐题 claim.py check（均 FREE）后 take；现登记 {len(mine)} 条，同题他卷一并锁定 {len({d for q in Q for d in q["dup_keys"]})} 个键；中途改选 1 次（GD2014Z-49 release，改取 GD2014X-32），记录见 work/claim_log.txt')
L.append('[sim] 全库文段相似度查重（work/simcheck.py，4-gram 包含度≥0.45，覆盖 index 全部卷、全部分区）：66 题除已一并登记的同题他卷外无其他相似文段，结果见 work/sim_out.txt')
L.append('[sim] 与此前各轮言语成品（YY-A、YY-B、YY2A、YY2B、YY3A、YY3B，共 360 题）及用户 HTML《盖句精读》全文比对（work/prevcheck.py）：0 处重合')
lk=open(f'{OUT}/work/leak_out.txt').read().strip().split('\n')
L.append(f'[leak] 同日泄题检查（work/leak4.py，含 YY4A 当时的 questions.jsonl）：{lk[-1]}；逐条判读见报告“与 YY4A 的协调”')
L.append('[leak] 跨日：本包与 YY4A 54 题两两比对，共享文本（≥9 字）0 处；本包内部仅 YY4B-029 与 YY4B-061 共有政策套语“市场在资源配置中起决定性作用”，分属 D11、D12，不构成提示')
ext=collections.Counter(a['external_original']['status'] for a in A)
L.append(f'[articles] 66 条：exam_passage {sum(1 for a in A if a["kind"]=="exam_passage")}、restored_from_answer {sum(1 for a in A if a["kind"]=="restored_from_answer")}；原解析载有出处 {ext["待补"]} 条（external_original=待补），未载 {ext["无出处"]} 条')
open(f'{OUT}/checks.txt','w').write('\n'.join(L)+'\n')
print('\n'.join(L))

import json
OUT='/home/user/work/out/YY-B'
qs=[json.loads(l) for l in open(f'{OUT}/questions.jsonl')]
arts={json.loads(l)['aid']:json.loads(l) for l in open(f'{OUT}/articles.jsonl')}
CN={'YY01':'D01','YY02':'D02','YY03':'D03'}
import re as _re
_b=open('/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/yyb/build.py').read()
PAPER_CN=eval(_re.search(r"PAPER_CN = (\{.*?\})\n", _b, _re.S).group(1))
def src(r):
    s=r['source']; return f"{PAPER_CN.get(s['paper'], s['paper'])}第{s['qno']}题"
qb=['# 言语题目册（YY-B 部分：片段阅读 + 语句排序）','',
    '> 由 questions.jsonl 自动生成。每日另有选词、语句填空（YY-A 部分），合并后每日 40 题。作答前不看答案原文册。','']
ab=['# 言语答案与原文册（YY-B 部分）','',
    '> 只列原参考答案、原解析附带的正确率/易错项与争议标记、文段出处（原标题）和排序还原文段；不写解析。','']
for day in ['YY01','YY02','YY03']:
    qb += [f'## {day}（正式日号 {CN[day]}）','']
    ab += [f'## {day}（正式日号 {CN[day]}）','',
           '| 序 | 题号 | 来源 | 题型 | 原参考答案 | 原解析正确率/易错项 | 标记 |','|---|---|---|---|---|---|---|']
    n=0
    for g,title in (('PD','片段阅读'),('PX','语句排序')):
        items=[r for r in qs if r['day']==day and r['group'].endswith(g)]
        qb += [f'### {title}（{len(items)} 题）','']
        for r in items:
            n+=1
            stem=r['stem'].replace('\n','\n\n')
            qb += [f"**{n}.** （{r['id']}｜{src(r)}）", '', stem, '']
            qb += ['  '.join(f"{k}. {v}" for k,v in r['options'].items()), '']
            rate=f"{r['source_rate']}% / {r['source_yicuo']}" if r.get('source_rate') is not None else ''
            mark='；'.join(r['flags'])
            ab += [f"| {n} | {r['id']} | {src(r)} | {r['topic']} | {r['source_answer']} | {rate} | {mark} |"]
    ab += ['', '### 原文与出处', '']
    n=0
    for g in ('PD','PX'):
        for r in [r for r in qs if r['day']==day and r['group'].endswith(g)]:
            n+=1; a=arts[r['material_or_article']]
            line=f"**{n}.（{r['id']}）** 原参考答案 {r['source_answer']}。"
            if r.get('dispute_note'): line+=f" 原解析争议标记（照录）：{r['dispute_note']}"
            ab += [line, '']
            ab += [f"- 文段出处（原标题）：{a['source']['chuchu_from_analysis'] or '原解析未给出处'}"]
            if a['source'].get('external_url'): ab += [f"- 外部链接（检索所得，正文未核对）：{a['source']['external_url']}"]
            if a['kind']=='restored_from_answer':
                ab += [f"- 还原文段（按参考顺序 {a['order']}）：{a['text']}"]
            ab += ['']
open(f'{OUT}/books/YY-B_题目册.md','w').write('\n'.join(qb))
open(f'{OUT}/books/YY-B_答案原文册.md','w').write('\n'.join(ab))
print('ok')

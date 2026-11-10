import json, sys
PKG = sys.argv[1]; BLIND = sys.argv[2] if len(sys.argv) > 2 else ''
qs = [json.loads(l) for l in open(f'{PKG}/questions.jsonl')]
loc = {(q['editor'], q['local_id']): q for q in qs}
res = [json.loads(l) for l in open(f'{PKG}/备选与冲突待复核.jsonl')]
def F(e, lid):
    q = loc.get((e, lid)); return q['id'] if q else f'{lid}（未入包）'
def src(q):
    s = q['source']; return f"{s.get('paper')}-{s.get('qno')}"
L = ['# 复核清单（第3批：D07—D09）', '', '> 题号用正式题号；括号内是原题（卷号-原题号）。“证据—分歧—建议”写给复核方直接处理。', '',
     '## 一、未进正式包的题', '', '| 编者题号 | 原题 | 原因 | 证据与建议 |', '|---|---|---|---|']
for r in res:
    ev = (r.get('brief_solution') or '').replace('\n', ' ')[:260] if r.get('check_status') == '冲突待复核' else (r.get('notes') or '').replace('\n', ' ')[:160]
    L.append(f"| {r['id']} | {src(r)} | {r.get('why_not_in_package','')} | {ev} |")
L += ['', '## 二、正式包中请优先抽查的题', '', '### 1. 没有原参考答案、由编者独立定答案（含改编）', '']
for q in qs:
    if q['module'] != '言语' and not q.get('source_answer'):
        L.append(f"- {q['id']}（{src(q)}{'，改编自 ' + q['variant_of'] if q.get('variant_of') else ''}）编者答案 {q['checked_answer']}")
L += ['', '### 2. 改编题（编者独立重解，答案唯一）', '']
for q in qs:
    if q.get('variant_of'): L.append(f"- {q['id']} 改编自 {q['variant_of']}，答案 {q['checked_answer']}")
extra = json.load(open(f'{PKG}/_review_extras.json')) if __import__('os').path.exists(f'{PKG}/_review_extras.json') else []
L += ['', '### 3. 读法、口径、图像或原文需留意的题', '']
for e, lid, t in extra: L.append(f"- {F(e, lid)}（{e} {lid}）：{t}")
L += ['', '## 三、抽查记录', '', BLIND or '- 盲审：结果待补。', '- 言语：只做数据完整性和原文对应检查，不论证唯一答案；同日泄题已跨编者检查。', '']
rep = [r for r in qs if r.get('replaced_from')]
if rep:
    L += ['## 四、原位替换', '',
          '题号和组内位置不变；新题已独立求解，并与原解析核对一致。', '',
          '| 正式题号 | 被替换的原题 | 新题 | 答案 | 考点 |', '|---|---|---|---|---|']
    for r in rep:
        s_ = r['source']
        L.append(f"| {r['id']} | {r['replaced_from']} | {str(s_.get('paper') or '').replace('_xc','')}-{s_.get('qno')} | {r['checked_answer']} | {r.get('topic','')} |")
    L.append('')
import os as _os
if _os.path.exists(f'{PKG}/_audit_fixes.json'):
    af = json.load(open(f'{PKG}/_audit_fixes.json'))
    L += [af['title'], ''] + af['intro'] + ['', '| 题号 | 审核意见 | 修订 | 答案 |', '|---|---|---|---|']
    for r in af['rows']: L.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} |")
    L += [''] + af.get('tail', []) + ['']
open(f'{PKG}/复核清单.md', 'w').write('\n'.join(L) + '\n')
print('ok', len(res))

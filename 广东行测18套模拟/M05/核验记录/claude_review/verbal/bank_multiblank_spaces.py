# 只读：统计源库中各卷“依次填入”多空题选项是否带词间空格（判断第20题的连写是否为该卷转写的系统性问题）
import json, collections
BANK = "/home/user/xing-ce1/江浙行测_AI题库/questions.jsonl"
stat = collections.defaultdict(lambda: [0, 0, []])
for line in open(BANK, encoding="utf-8"):
    q = json.loads(line)
    if "依次填入" not in (q.get("stem") or ""): continue
    opts = q.get("options") or {}
    if not opts: continue
    spaced = all((" " in v or "　" in v) for v in opts.values() if isinstance(v, str))
    s = stat[q["paper_id"] + "-" + str(q.get("paper_type"))]
    s[0] += 1
    if spaced: s[1] += 1
    else: s[2].append(q["question_id"])
for k in sorted(stat):
    tot, sp, nos = stat[k]
    print(f"{k}: 多空题{tot}道，选项带空格{sp}道；不带空格：{nos[:12]}{' …' if len(nos) > 12 else ''}")

# -*- coding: utf-8 -*-
"""第二阶段：来源登记.jsonl / selection.json / 答案与解析_待审.md / 题本 一致性（第71—90题，只读）。"""
import json, hashlib, re, subprocess, os
REPO = "/home/user/xing-ce1"
M05 = os.path.join(REPO, "广东行测18套模拟/M05")
SRCF = os.path.join(REPO, "模考/2026下半年广东卷_16-33季_AI可读/全部题目.jsonl")
HERE = os.path.dirname(os.path.abspath(__file__))
reg = {r["number"]: r for r in (json.loads(l) for l in open(os.path.join(M05, "来源登记.jsonl"), encoding="utf-8") if l.strip())}
sel = {r["number"]: r for r in json.load(open(os.path.join(M05, "selection.json"), encoding="utf-8"))}
md = open(os.path.join(M05, "答案与解析_待审.md"), encoding="utf-8").read()
blind = json.load(open(os.path.join(HERE, "blind_answers.json"), encoding="utf-8"))
sha_now = hashlib.sha256(open(SRCF, "rb").read()).hexdigest()
print("题源 全部题目.jsonl 当前 sha256 =", sha_now)
# 题源文件在 source_snapshot 提交时的 sha256
snap = reg[71]["source_snapshot"]
blob = subprocess.run(["git", "-C", REPO, "show", "%s:模考/2026下半年广东卷_16-33季_AI可读/全部题目.jsonl" % snap], capture_output=True).stdout
print("source_snapshot %s 时题源 sha256 = %s" % (snap[:8], hashlib.sha256(blob).hexdigest()))
# 答案速查表
quick = {}
for blk in re.findall(r"\| (\d+(?: \| \d+)*) \|\n\| [-| ]+\|\n\| ([^\n]+) \|", md):
    nums = [int(x) for x in blk[0].split(" | ")]
    ans = [x.strip() for x in blk[1].split(" | ")]
    quick.update(dict(zip(nums, ans)))
ok = True
for n in range(71, 91):
    r, s = reg[n], sel[n]
    head = re.search(r"### 第%d题　(\S+)" % n, md)
    body = md[head.end():].split("### 第")[0] if head else ""
    checks = {
        "登记.source_id==selection": r["source_id"] == s["source_id"],
        "登记.editor_answer==selection.answer": r["editor_answer"] == s["answer"],
        "解析标题答案==selection": bool(head) and head.group(1) == s["answer"],
        "速查表==selection": quick.get(n) == s["answer"],
        "解析首句'选X'==selection": body.strip().startswith("选%s" % s["answer"]),
        "解析正文==selection.analysis": s["analysis"] in body,
        "登记.edits==selection.edits": r["edits"] == s["edits"],
        "登记.source_file_sha256==当前题源": r["source_file_sha256"] == sha_now,
        "盲解==答案键": blind[str(n)]["answer"] == s["answer"],
    }
    bad = [k for k, v in checks.items() if not v]
    ok &= not bad
    print("第%d题 答案键=%s 盲解=%s %s" % (n, s["answer"], blind[str(n)]["answer"], "全部一致" if not bad else "不一致：" + "；".join(bad)))
print("总体：", "全部一致" if ok else "有不一致")
print("盲解与答案键一致数：%d/20" % sum(blind[str(n)]["answer"] == sel[n]["answer"] for n in range(71, 91)))

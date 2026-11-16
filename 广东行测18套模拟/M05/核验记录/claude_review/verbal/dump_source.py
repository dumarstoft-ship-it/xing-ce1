# 只读：导出第16—30题对应源题（questions.jsonl）与源参考答案（answers.jsonl）
import json
BANK = "/home/user/xing-ce1/江浙行测_AI题库"
M05 = "/home/user/xing-ce1/广东行测18套模拟/M05"
sel = json.load(open(f"{M05}/selection.json", encoding="utf-8"))
ids = {q["source_id"]: q["number"] for q in sel if 16 <= q["number"] <= 30}
qs, ans = {}, {}
for line in open(f"{BANK}/questions.jsonl", encoding="utf-8"):
    r = json.loads(line)
    if r["question_id"] in ids: qs[r["question_id"]] = r
for line in open(f"{BANK}/answers.jsonl", encoding="utf-8"):
    r = json.loads(line)
    if r["question_id"] in ids: ans[r["question_id"]] = r
for sid, n in sorted(ids.items(), key=lambda x: x[1]):
    q, a = qs[sid], ans.get(sid)
    print(f"### M05-{n}  {sid}")
    print("STEM repr:", repr(q["stem"]))
    print("OPTIONS repr:", {k: repr(v) for k, v in q["options"].items()})
    print("CONTENT repr:", repr(q["content"]))
    print("quality_flags:", q.get("quality_flags"), "notes:", q.get("notes"), "figures:", q.get("figures"))
    if a:
        print("SOURCE ANSWER:", a["correct_answer"], "| candidates:", [c["answer"] for c in a.get("answer_candidates", [])], "| answer quality:", a.get("quality_flags"))
        print("SOURCE ANALYSIS:", a.get("analysis"))
        print("answer source:", a["source"]["file"], a["source"].get("pdf_pages"))
    print("=" * 60)

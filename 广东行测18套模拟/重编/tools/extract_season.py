"""把某季模考第31—90题导出为解题用的输入文件（不含任何答案），另把旧卷里用过的同题答案单独存放。

用法：python3 extract_season.py M01 16
输出：重编/<套卷>/输入/{quant_sci,fig_logic,data}.{json,md} 与 prior.json
"""
import json, sys, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]          # 仓库根
BANK = ROOT / "模考/2026下半年广东卷_16-33季_AI可读"
SERIES = ROOT / "广东行测18套模拟"

def blocks_md(blocks):
    out = []
    for b in blocks:
        if b["type"] == "text":
            out.append(b["text"])
        elif b["type"] == "figure":
            out.append(f"[图：{BANK / b['path']}]")
        elif b["type"] == "table":
            t = [f"【表】{b.get('title','')}", "| " + " | ".join(b["headers"]) + " |",
                 "|" + "---|" * len(b["headers"])]
            t += ["| " + " | ".join(r) + " |" for r in b["rows"]]
            if b.get("notes"):
                t.append(f"（表注：{b['notes']}）")
            out.append("\n".join(t))
        else:
            out.append(json.dumps(b, ensure_ascii=False))
    return "\n".join(out)

def q_md(q, show_material=True):
    s = [f"### 第{q['number']}题　`{q['id']}`", blocks_md(q["stem"])]
    for k in "ABCD":
        if k in q["options"]:
            s.append(f"{k}. {blocks_md(q['options'][k])}")
    return "\n\n".join(s)

def main(paper, season):
    rows = [json.loads(l) for l in open(BANK / "全部题目.jsonl", encoding="utf-8")]
    items = [q for q in rows if q["season"] == season and 31 <= q["number"] <= 90]
    assert len(items) == 60, len(items)
    groups = {
        "quant_sci": [q for q in items if q["number"] <= 45 or 66 <= q["number"] <= 70],
        "fig_logic": [q for q in items if 46 <= q["number"] <= 65],
        "data": [q for q in items if q["number"] >= 71],
    }
    out = SERIES / "重编" / paper / "输入"
    out.mkdir(parents=True, exist_ok=True)
    for name, qs in groups.items():
        slim = []
        for q in qs:
            d = {k: q[k] for k in ("id", "season", "section", "number", "stem", "options")}
            if q.get("material_id"):
                d["material_id"] = q["material_id"]
            slim.append(d)
        mats = {}
        for q in qs:
            if q.get("material"):
                mats[q["material"]["id"]] = q["material"]
        (out / f"{name}.json").write_text(json.dumps({"questions": slim, "materials": list(mats.values())},
                                                     ensure_ascii=False, indent=1), encoding="utf-8")
        md = [f"# {paper} 输入：第{season}季 {name}（不含答案）\n"]
        done = set()
        for q in qs:
            mid = q.get("material_id")
            if mid and mid not in done:
                m = mats[mid]
                md.append(f"## 资料第{m['number']}组 `{mid}`（第{m['question_numbers'][0]}—{m['question_numbers'][-1]}题）\n\n" + blocks_md(m["blocks"]))
                done.add(mid)
            md.append(q_md(q))
        (out / f"{name}.md").write_text("\n\n".join(md) + "\n", encoding="utf-8")
    # 旧卷用过的同题：答案与解析单独存放，盲解完成后才打开
    prior = {}
    ids = {q["id"] for q in items}
    for p in ["M01", "M02", "M03", "M04", "M05"]:
        for q in json.load(open(SERIES / p / "selection.json", encoding="utf-8")):
            if q.get("source_id") in ids:
                prior[q["source_id"]] = {"old_paper": p, "old_number": q["number"], "answer": q.get("answer"),
                                         "analysis": q.get("analysis"), "edits": q.get("edits")}
    (out / "prior.json").write_text(json.dumps(prior, ensure_ascii=False, indent=1), encoding="utf-8")
    print(paper, season, {k: len(v) for k, v in groups.items()}, "prior", len(prior))

if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]))

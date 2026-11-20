"""专项（图推、数推、科推）：按 专项/分配.json 把专项题分组导出为解题输入（不含答案），来源答案另存 prior.json。

用法：python3 广东行测18套模拟/重编/tools/zx_extract.py
输出：重编/专项/输入/<组>.{json,md}，重编/专项/输入/prior.json
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import extract_sources as ex  # noqa: E402

R = ex.R
GROUPS = {
    "数推": lambda part, t: part == "数字推理",
    "图推_位置样式": lambda part, t: part == "图形推理" and t in ("规律类-位置", "规律类-样式"),
    "图推_数量属性其他": lambda part, t: part == "图形推理" and t in ("规律类-数量", "规律类-属性", "其他", "分类分组"),
    "图推_空间": lambda part, t: part == "图形推理" and (t or "").startswith("空间类"),
    "科推_力学": lambda part, t: part == "科学推理" and t == "力学",
    "科推_其他": lambda part, t: part == "科学推理" and t != "力学",
}


def main():
    plan = json.loads((R / "专项" / "分配.json").read_text(encoding="utf-8"))
    B = ex.bank()
    out = R / "专项" / "输入"
    out.mkdir(parents=True, exist_ok=True)
    prior, seen = {}, set()
    for name, ok in GROUPS.items():
        items, md = [], [f"# 专项输入：{name}（不含答案）\n"]
        k = 0
        for part, rows in plan["专项"].items():
            for r in rows:
                if not ok(part, r.get("type")):
                    continue
                k += 1
                seen.add(r["id"])
                d, q = B[r["id"]]
                x = {"id": q["id"], "number": k, "section": q["section"], "pool_type": r.get("type"),
                     "stem": q["stem"], "options": [{"label": o["label"], "text": o["text"]} for o in q["options"]],
                     "figures": [ex.fig(d, f) for f in q.get("figures") or []]}
                items.append(x)
                md.append(ex.q_md(x))
                a = q.get("answer") or {}
                prior[q["id"]] = {"answer": "".join(a["values"][0]) if a.get("values") and len(a["values"]) == 1 else a.get("values"),
                                  "status": a.get("status"), "answer_pdf": (q.get("source") or {}).get("answer_pdf"),
                                  "answer_pages": a.get("source_pages"), "note": a.get("note") or ""}
        (out / f"{name}.json").write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
        (out / f"{name}.md").write_text("\n\n".join(md) + "\n", encoding="utf-8")
        print(name, len(items))
    total = sum(len(v) for v in plan["专项"].values())
    if len(seen) != total:
        raise SystemExit(f"分组漏题：{total - len(seen)}题没有归组")
    (out / "prior.json").write_text(json.dumps(prior, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()

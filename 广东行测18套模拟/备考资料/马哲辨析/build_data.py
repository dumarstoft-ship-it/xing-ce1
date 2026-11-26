"""马哲辨析网页的数据：底稿（概念卡、342道判断题、附录、来源）＋核对过的新题 → site/ 下三份JSON。

用法：python3 广东行测18套模拟/备考资料/马哲辨析/build_data.py
- 底稿：学习资料/政治理论常识/马哲概念辨析训练底稿.json（用户提供，题目、答案原样保留）
- 新题：本目录 新题/W*.json，只收 核对/采用.json 里列为采用的题（盲做核对后的结果）
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DRAFT = ROOT / "学习资料/政治理论常识/马哲概念辨析训练底稿.json"
OUT = HERE / "site"


def lines(rows):
    """一个JSON数组，一条记录一行（便于阅读和比对）。"""
    return "[\n" + ",\n".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in rows) + "\n]\n"


def main():
    d = json.loads(DRAFT.read_text(encoding="utf-8"))
    cards, questions = [], []
    for c in d["cards"]:
        cards.append({k: c[k] for k in ("id", "module_id", "title", "priority", "correct_statement", "incorrect_statement",
                                        "explanation", "necessary_conditions_and_boundaries", "example_or_counterexample",
                                        "example_status", "source_refs")})
        for q in c["checks"]:
            assert q["type"] == "true_false"
            polarity = "正确句" if q["statement"] == c["correct_statement"] else "易错句" if q["statement"] == c["incorrect_statement"] else "?"
            assert polarity != "?" and (polarity == "正确句") == q["answer"], q["id"]
            questions.append({"id": q["id"], "src": "底稿", "kind": "基础判断", "type": "判断", "module": c["module_id"],
                              "cards": [c["id"]], "stem": q["statement"], "answer": "正确" if q["answer"] else "错误",
                              "polarity": polarity})
    assert len(cards) == d["statistics"]["concept_cards"] and len(questions) == d["statistics"]["true_false_questions"]

    # 核对后采用的新题（盲做与出题人一致，或经裁定修改后采用）
    keep_f = HERE / "核对" / "采用.json"
    keep = json.loads(keep_f.read_text(encoding="utf-8")) if keep_f.exists() else {}
    card_ids = {c["id"] for c in cards}
    n_new = 0
    for f in sorted((HERE / "新题").glob("W*.json")):
        for q in json.loads(f.read_text(encoding="utf-8")):
            k = keep.get(q["id"])
            if not k or k.get("status") != "采用":
                continue
            q = {**q, **(k.get("override") or {})}
            assert set(q["card_ids"]) <= card_ids, (q["id"], q["card_ids"])
            assert q["type"] in ("判断", "单选", "多选") and q["kind"] in ("仿真题", "拓展"), q["id"]
            if q["type"] == "判断":
                assert q["answer"] in ("正确", "错误") and not q.get("options"), q["id"]
            else:
                assert set(q["answer"]) <= set(q["options"]) and q["answer"] == "".join(sorted(q["answer"])), q["id"]
                assert len(q["answer"]) == 1 if q["type"] == "单选" else 2 <= len(q["answer"]) <= 4, q["id"]
            questions.append({"id": q["id"], "src": "新增", "kind": q["kind"], "type": q["type"], "module": q["module_id"],
                              "cards": q["card_ids"], "lead": q.get("lead") or "", "stem": q["stem"],
                              "options": q.get("options") or {}, "answer": q["answer"], "fix": q.get("fix") or "",
                              "analysis": q["analysis"], "trap": q.get("trap") or "", "basis": q.get("basis") or "",
                              "refs": q.get("source_refs") or [], "note": k.get("note") or ""})
            n_new += 1
    assert len({q["id"] for q in questions}) == len(questions)

    meta = {"title": d["title"], "prepared_on": d["prepared_on"],
            "modules": [{"id": m["id"], "title": m["title"]} for m in d["modules"]],
            "appendices": d["appendices"], "sources": d["sources"],
            "learning_context": d["learning_context"], "counts": {"cards": len(cards), "base": len(questions) - n_new, "new": n_new}}
    OUT.mkdir(exist_ok=True)
    (OUT / "cards.json").write_text(lines(cards), encoding="utf-8")
    (OUT / "questions.json").write_text(lines(questions), encoding="utf-8")
    (OUT / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("cards", len(cards), "questions", len(questions), "new", n_new)


if __name__ == "__main__":
    main()

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
DRAFT_FM = ROOT / "学习资料/政治理论常识/非马哲政治理论与广东常识训练底稿_2026-11-27.json"   # GPT整理的非马哲底稿
OUT = HERE / "site"


def lines(rows):
    """一个JSON数组，一条记录一行（便于阅读和比对）。"""
    return "[\n" + ",\n".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in rows) + "\n]\n"


def split_options(text):
    """选择题解析里各选项另起一行：句末（。；）后紧跟“X项”时断行。"""
    import re
    return re.sub(r"([。；])\s*(?=[A-D]项)", "\\1\n", text)


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

    # 底稿待核验（核对人审读底稿后由编辑裁定）：不改底稿答案，只加考场口径说明；答案不唯一的判断题不进自动选题
    fix_f = HERE / "核对" / "底稿处理.json"
    fixes = json.loads(fix_f.read_text(encoding="utf-8")) if fix_f.exists() else {}
    by_card = {c["id"]: c for c in cards}
    for cid, fx in fixes.items():
        by_card[cid]["review_note"] = fx["note"]
        for q in questions:
            if q["cards"] == [cid] and q["polarity"] in fx.get("hold", []):
                q["hold"] = fx.get("hold_reason") or fx["note"]

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
                              "analysis": split_options(q["analysis"]) if q["type"] != "判断" else q["analysis"], "trap": q.get("trap") or "", "basis": q.get("basis") or "",
                              "refs": q.get("source_refs") or [], "note": k.get("note") or ""})
            n_new += 1
    # 广东旧卷真题（答案来自答案解析PDF，解析由编辑写）
    n_real = 0
    real_f = HERE / "新题" / "真题.json"
    for q in (json.loads(real_f.read_text(encoding="utf-8")) if real_f.exists() else []):
        assert set(q["card_ids"]) <= card_ids and q["kind"] == "广东真题", q["id"]
        questions.append({"id": q["id"], "src": "真题", "kind": q["kind"], "type": q["type"], "module": q["module_id"],
                          "cards": q["card_ids"], "lead": q.get("lead") or "", "stem": q["stem"], "options": q.get("options") or {},
                          "answer": q["answer"], "fix": "", "analysis": q["analysis"], "trap": q.get("trap") or "",
                          "basis": q.get("basis") or "", "refs": q.get("source_refs") or [], "note": ""})
        n_real += 1
    assert len({q["id"] for q in questions}) == len(questions)

    # ---------- 政常（非马哲）：GPT底稿的知识块 ＋ 核对后的新题 ----------
    fm = json.loads(DRAFT_FM.read_text(encoding="utf-8"))
    blocks = [{"id": r["id"], "module_id": r["module"], "title": r["title"], "priority": r["priority"],
               "new": r.get("content_origin") == "new", "correct": r["correct"], "why": r.get("why") or "",
               "contrasts": r.get("contrasts") or [], "question_design": r.get("question_design") or "",
               "related_ids": r.get("related_ids") or [], "source_ids": r.get("source_ids") or [],
               "exam_eligible": r.get("exam_eligible", True)} for r in fm["records"]]
    block_ids = {b["id"] for b in blocks}
    fkeep_f = HERE / "非马哲" / "核对" / "采用.json"
    fkeep = json.loads(fkeep_f.read_text(encoding="utf-8")) if fkeep_f.exists() else {}
    n_fm = n_fm_pending = 0
    for f in sorted((HERE / "非马哲" / "新题").glob("F*.json")):
        for q in json.loads(f.read_text(encoding="utf-8")):
            k = fkeep.get(q["id"])
            if not k or k.get("status") not in ("采用", "待审"):
                continue
            q = {**q, **(k.get("override") or {})}
            assert set(q["knowledge_ids"]) <= block_ids, (q["id"], q["knowledge_ids"])
            t = q["type"]
            if t == "判断":
                assert q["answer"] in ("正确", "错误") and not q.get("options"), q["id"]
                assert q["answer"] == "正确" or q.get("fix"), q["id"]
            else:
                nc = sum(1 for o in q["options"] if o["correct"])
                assert t in ("单选", "多选") and (nc == 1 if t == "单选" else 2 <= nc <= 4) and all(o.get("why") for o in q["options"]), q["id"]
            review = (k.get("review") or q.get("review") or "") if k.get("status") == "待审" else ""
            questions.append({"id": q["id"], "bank": "fm", "src": "政常", "kind": "政常新题", "type": t, "form": q.get("form") or "",
                              "module": q["module"], "cards": q["knowledge_ids"], "lead": q.get("lead") or "", "stem": q["stem"],
                              "opts": [{"text": o["text"], "correct": bool(o["correct"]), "why": o["why"]} for o in (q.get("options") or [])],
                              "answer": q.get("answer") if t == "判断" else "", "fix": q.get("fix") or "", "explain": q.get("explain") or "",
                              "condition": q.get("condition") or "", "refs": q.get("source_ids") or [], "origin": q.get("origin") or "自编",
                              "review": review})
            n_fm += 1
            n_fm_pending += bool(review)
    assert len({q["id"] for q in questions}) == len(questions)

    meta = {"title": d["title"], "prepared_on": d["prepared_on"],
            "modules": [{"id": m["id"], "title": m["title"]} for m in d["modules"]],
            "appendices": d["appendices"], "sources": d["sources"],
            "learning_context": d["learning_context"],
            "counts": {"cards": len(cards), "base": len(questions) - n_new - n_real - n_fm, "new": n_new, "real": n_real,
                       "blocks": len(blocks), "fm": n_fm, "fm_pending": n_fm_pending},
            "fm_modules": [{"id": m, "title": fm["modules"][m]} for m in fm["module_order"]],
            "fm_sources": {k: {"title": v.get("title", k), "url": v.get("url", ""), "publication_date": v.get("publication_date", "")}
                           for k, v in fm["sources"].items()},
            "fm_profiles": {"new_focus": fm["training_profiles"]["new_focus"]["ids"], "all_core": fm["training_profiles"]["all_core"]["ids"]},
            "fm_cutoff": fm.get("evidence_cutoff", "")}
    OUT.mkdir(exist_ok=True)
    (OUT / "cards.json").write_text(lines(cards), encoding="utf-8")
    (OUT / "questions.json").write_text(lines(questions), encoding="utf-8")
    (OUT / "blocks.json").write_text(lines(blocks), encoding="utf-8")
    (OUT / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("cards", len(cards), "questions", len(questions), "new", n_new, "real", n_real, "blocks", len(blocks), "fm", n_fm, "fm_pending", n_fm_pending)


if __name__ == "__main__":
    main()

"""精选前的材料整理：往年广东卷政治常识题分片、知识点目录、题库分组。

用法：python3 广东行测18套模拟/备考资料/马哲辨析/精选/prep.py
产出（都在本目录下）：
- 真题/S1…S6.json   2013—2026年广东卷（含2019—2020选调卷）“常识判断”“政治理论”部分的题，去掉无关字段
- 知识点目录.md      题库的318个知识点：171张马哲概念卡、147个政常知识块
- 题库/G1…G8.json    题库按模块分8组，每个知识点下列出它的全部题目
"""
import glob
import json
import os
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SITE = HERE.parent / "site"
PAST = ROOT / "广东/行测"
DRAFT_FM = ROOT / "学习资料/政治理论常识/非马哲政治理论与广东常识训练底稿_2026-11-27.json"

SLICES = {
    "S1": ["GD2013-1", "GD2013-3", "GD2014-XJ", "GD2014-XZ", "GD2015-XJ", "GD2015-XZ"],
    "S2": ["GD2016-XJ", "GD2016-XZ", "GD2017", "GD2018"],
    "S3": ["GD2019-XJ", "GD2019-XZ", "GD2020-XJ", "GD2020-XZ", "GD2021-XZ"],
    "S4": ["GDXD2019-XC", "GDXD2020-ZH"],
    "S5": ["GD2022-XJ", "GD2022-XZ", "GD2023-XJ", "GD2023-XZ"],
    "S6": ["GD2024", "GD2025", "GD2026"],
}
GROUPS = {
    "G1": ("马哲：总论、物质与意识", ["M1", "M2"]),
    "G2": ("马哲：联系发展、范畴与思维方法", ["M3", "M5"]),
    "G3": ("马哲：矛盾分析、实践认识与真理", ["M4", "M6"]),
    "G4": ("马哲：唯物史观与道德", ["M7"]),
    "G5": ("政常：新思想、发展理论、党建、制度会议规划", ["P1", "P2", "P3", "P4"]),
    "G6": ("政常：党史、著作与改革节点", ["H"]),
    "G7": ("政常：法律", ["LAW"]),
    "G8": ("政常：2026广东重要事项", ["GD"]),
}
TYPE = {"true_false": "判断", "single_choice": "单选", "multiple_choice": "多选"}


def jl(path):
    return [json.loads(x.strip().rstrip(",")) for x in open(path, encoding="utf-8") if x.strip().startswith("{")]


def norm(s):
    return re.sub(r"[\s（）()：:，,。.、“”\"'？?！!·…—-]+", "", s)[:60]


def past():
    (HERE / "真题").mkdir(exist_ok=True)
    seen = {}
    total = 0
    for sid, papers in SLICES.items():
        out = []
        for pid in papers:
            f = next(p for p in glob.glob(str(PAST / "*" / f"{pid}.jsonl")))
            for line in open(f, encoding="utf-8"):
                if not line.strip():
                    continue
                q = json.loads(line)
                if q["section"] not in ("常识判断", "政治理论"):
                    continue
                key = (q["year"], norm(q["stem"]))
                dup = seen.get(key)
                seen.setdefault(key, q["id"])
                ans = q["answer"]
                out.append({
                    "id": q["id"], "year": q["year"], "paper": pid,
                    "exam": "选调生" if pid.startswith("GDXD") else "省考", "variant": q.get("paper_variant") or "",
                    "number": q["question_number"], "section": q["section"], "type": TYPE.get(q["question_type"], q["question_type"]),
                    "stem": q["stem"], "options": {o["label"]: o["text"] for o in q.get("options") or []},
                    "answer": "".join(sum(ans["values"], [])) if ans["status"] == "known" and ans["values"] else "（仓库无答案）",
                    "same_as": dup or "",      # 同年另一卷别的同一道题（统计时只算一次）
                })
        (HERE / "真题" / f"{sid}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        total += len(out)
        print(sid, papers, len(out), "重复", sum(1 for x in out if x["same_as"]))
    print("真题合计", total)


def bank():
    cards = jl(SITE / "cards.json")
    blocks = jl(SITE / "blocks.json")
    qs = jl(SITE / "questions.json")
    meta = json.loads((SITE / "meta.json").read_text(encoding="utf-8"))
    recs = {r["id"]: r for r in json.loads(DRAFT_FM.read_text(encoding="utf-8"))["records"]}
    mods = {m["id"]: m["title"] for m in meta["modules"] + meta["fm_modules"]}
    by_unit = {}
    for q in qs:
        for i, c in enumerate(q["cards"]):
            by_unit.setdefault(c, []).append((q, i == 0))

    # 知识点目录
    lines = ["# 题库知识点目录（318个）", "",
             "每行：编号｜档次｜标题｜要点。马哲概念卡编号形如 M4.07，政常知识块编号形如 LAW-008、GD-004、H12、P2-05、K-LAW-01（K 开头是按Codex原文证据新增的块）。", ""]
    cur = None
    for u in cards + blocks:
        m = u["module_id"]
        if m != cur:
            cur = m
            lines += ["", f"## {m}　{mods[m]}", ""]
        gist = u.get("correct_statement") or "；".join(u.get("correct") or [])
        lines.append(f"- {u['id']}｜{u['priority']}｜{u['title']}｜{gist[:70]}")
    (HERE / "知识点目录.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # 题库分组
    (HERE / "题库").mkdir(exist_ok=True)

    def qview(q, primary):
        v = {"id": q["id"], "primary": primary, "all_units": q["cards"], "kind": q.get("kind") or "", "type": q["type"]}
        if q.get("form"):
            v["form"] = q["form"]
        if q.get("lead"):
            v["lead"] = q["lead"]
        v["stem"] = q["stem"]
        if q.get("bank") == "fm":
            if q["type"] == "判断":
                v["answer"] = q["answer"]
                if q.get("fix"):
                    v["fix"] = q["fix"]
            else:
                v["options"] = [("✓ " if o["correct"] else "✗ ") + o["text"] for o in q["opts"]]
            if q.get("condition"):
                v["condition"] = q["condition"][:160]
            v["has_evidence"] = any(r.startswith("E-") for r in q.get("refs") or [])
        else:
            if q.get("options"):
                v["options"] = [f"{k}. {t}" for k, t in q["options"].items()]
            v["answer"] = q["answer"]
            if q.get("polarity"):
                v["polarity"] = q["polarity"]
            if q.get("trap"):
                v["trap"] = q["trap"]
            if q.get("hold"):
                v["hold"] = "暂停出题（答案不唯一）"
        return v

    for gid, (title, ms) in GROUPS.items():
        units = []
        for u in cards + blocks:
            if u["module_id"] not in ms:
                continue
            x = {"id": u["id"], "module": u["module_id"], "priority": u["priority"], "title": u["title"]}
            if "correct_statement" in u:
                x["correct_statement"] = u["correct_statement"]
                x["incorrect_statement"] = u["incorrect_statement"]
                if u.get("review_note"):
                    x["review_note"] = u["review_note"]
            else:
                x["correct"] = u["correct"]
                x["new_in_2026"] = bool(u.get("new"))
                x["from_codex_evidence"] = bool(u.get("candidate"))
                if u.get("question_design"):
                    x["question_design"] = u["question_design"]
                r = recs.get(u["id"]) or {}
                if r.get("prediction_rationale"):
                    x["gpt_prediction_rationale"] = r["prediction_rationale"]
                if r.get("teaching_status"):
                    x["teaching_status"] = r["teaching_status"]
                if u.get("review_note"):
                    x["review_note"] = u["review_note"]
            x["questions"] = [qview(q, p) for q, p in by_unit.get(u["id"], [])]
            units.append(x)
        nq = len({q["id"] for u in units for q in u["questions"]})
        (HERE / "题库" / f"{gid}.json").write_text(json.dumps({"group": gid, "title": title, "modules": ms, "units": units}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(gid, title, "知识点", len(units), "题", nq, "KB", (HERE / "题库" / f"{gid}.json").stat().st_size // 1024)


if __name__ == "__main__":
    past()
    bank()

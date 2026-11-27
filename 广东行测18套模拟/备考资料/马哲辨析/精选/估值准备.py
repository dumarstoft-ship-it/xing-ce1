"""给题库估值做准备：按题库分组（G1—G8）整理“真题对照”材料。

用法：python3 广东行测18套模拟/备考资料/马哲辨析/精选/估值准备.py
读：画像/merged.json（真题逐题归类）、真题/S1—S6.json（真题原文）、题库/G1—G8.json（题库分组）、../site/questions.json
写：估值/对照/<组>_题库.json（本组的知识点和题）、估值/对照/<组>_真题.json，后者包含
  - 不可选：本组里不参加精选的题（用户做过的2024—2026年真题、暂停出题的题）
  - unit_hits：本组每个知识点被哪些真题命中（直接、弱、同位）
  - items：上面提到的真题，以及本组对应领域2019年以后的全部真题（去重），带原文、答案和归类
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
# 估值分组：题库分组文件、只取哪些模块（None 为全部）、对应的真题领域
GROUPS = {
    "G1": ("G1", None, ["D1"]), "G2": ("G2", None, ["D1"]), "G3": ("G3", None, ["D1"]), "G4": ("G4", None, ["D1"]),
    "G5a": ("G5", ["P1", "P2"], ["D2", "D3"]), "G5b": ("G5", ["P3", "P4"], ["D4", "D5"]),   # G5 太大，拆成两份
    "G6": ("G6", None, ["D6"]), "G7": ("G7", None, ["D7"]), "G8": ("G8", None, ["D8"]),
}
ALL_YEARS = {"G1", "G2", "G3", "G4"}          # 马哲题少，全部年份都给


def main():
    merged = {r["id"]: r for r in json.loads((HERE / "画像" / "merged.json").read_text(encoding="utf-8"))}
    raw = {}
    for i in range(1, 7):
        for q in json.loads((HERE / "真题" / f"S{i}.json").read_text(encoding="utf-8")):
            raw[q["id"]] = q
    assert set(raw) == set(merged), (len(raw), len(merged))
    bank = json.loads((HERE.parent / "site" / "questions.json").read_text(encoding="utf-8"))
    hold = {q["id"]: q["hold"] for q in bank if q.get("hold")}
    done = {q["id"] for q in bank if q["id"][:6] in ("GD2024", "GD2025", "GD2026")}

    def item(qid):
        q, m = raw[qid], merged[qid]
        ans = q.get("answer")
        if not ans or "无答案" in str(ans):
            ans = m["my_answer"] + "（仓库无官方答案，两位归类人作答一致）"
        return {"id": qid, "year": m["year"], "exam": m["exam"], "number": m["number"], "type": m["type"], "weight": m["weight"],
                "same_as": m.get("same_as") or "", "stem": q["stem"], "options": q.get("options") or [], "answer": ans,
                "domain": m["domain"], "slot": m["slot"], "topic": m["topic"], "ask": m["ask"], "style": m["style"], "trap": m["trap"],
                "currency": m["currency"], "units": m["units"], "weak_units": m.get("weak_units") or [], "analog_units": m["analog_units"]}

    for g, (src, mods, doms) in GROUPS.items():
        d = json.loads((HERE / "题库" / f"{src}.json").read_text(encoding="utf-8"))
        if mods:
            d["units"] = [u for u in d["units"] if u["module"] in mods]
            d["modules"] = mods
            d["title"] = d["title"] + "（" + "、".join(mods) + "）"
        d["group"] = g
        (HERE / "估值" / "对照" / f"{g}_题库.json").write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        units = [u["id"] for u in d["units"]]
        uset = set(units)
        own = {q["id"] for u in d["units"] for q in u["questions"] if q["primary"]}
        hits = {u: [] for u in units}
        need = set()
        for qid, m in merged.items():
            if m.get("same_as"):
                continue
            weak = set(m.get("weak_units") or [])
            for u in m["units"]:
                if u in uset:
                    hits[u].append({"id": qid, "kind": "弱" if u in weak else "直接", "year": m["year"], "weight": m["weight"]})
                    need.add(qid)
            for u in m["analog_units"]:
                if u in uset:
                    hits[u].append({"id": qid, "kind": "同位", "year": m["year"], "weight": m["weight"]})
                    need.add(qid)
        for qid, m in merged.items():
            if m.get("same_as") or m["domain"] not in doms:
                continue
            if g in ALL_YEARS or m["year"] >= 2019:
                need.add(qid)
        for u in hits:
            hits[u].sort(key=lambda h: (-h["year"], h["id"]))
        out = {
            "group": g, "title": d["title"],
            "说明": "unit_hits 是归类人给出的“真题—知识点”对应，可能有错有漏，估值时要自己核对；items 里除被命中的题外，还有本组对应领域"
                    + ("全部年份" if g in ALL_YEARS else "2019年以后") + "的真题（同年两卷共用的只留一道）。weight 是年份权重（2024—2026年3，2022—2023年2，2019—2021年1，更早0.5，选调生卷减半）。",
            "不可选": {**{q: "用户已做过的近三年真题" for q in sorted(done & own)}, **{q: "暂停出题：" + hold[q] for q in sorted(set(hold) & own)}},
            "unit_hits": {u: h for u, h in hits.items() if h},
            "items": [item(q) for q in sorted(need, key=lambda x: (-merged[x]["year"], x))],
        }
        f = HERE / "估值" / "对照" / f"{g}_真题.json"
        f.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(g, d["title"], "| 知识点", len(units), "有命中", len(out["unit_hits"]), "| 本组题", len(own), "| 真题", len(out["items"]), "| 不可选", len(out["不可选"]),
              "| 真题KB", f.stat().st_size // 1024, "题库KB", (HERE / "估值" / "对照" / f"{g}_题库.json").stat().st_size // 1024)


if __name__ == "__main__":
    main()

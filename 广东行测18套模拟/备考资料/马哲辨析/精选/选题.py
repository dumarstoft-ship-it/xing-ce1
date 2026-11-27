"""从估值结果和命题蓝图定出精选名单：核心（先学）和备选，并排出先后顺序。

用法：python3 广东行测18套模拟/备考资料/马哲辨析/精选/选题.py [--write]
读：估值/G1…G8.json（每组的知识点估值和题目排序）、蓝图/B1—B3.json（三位预测人的蓝图）、
    校准/MZ.json、FM.json、ALL.json（校准人和总评人的加减分，可没有）、调整.json（最后的人工调整和网页上的说明文字，可没有）、
    ../site/questions.json
写（加 --write 时）：精选.json（网页构建脚本 build_data.py 读它）、精选清单.json（每道题的分数和理由，便于核对）

做法：
1. 每道题的基础分是估值人给的 gain（0—100，全题库同一把尺子：70以上应当留，50—69有余力再学）。
2. 蓝图加分：三位预测人给每个位置列了可能考到的知识点和概率，把一个知识点在15个位置上的概率加起来、三人取平均，
   就是它的“蓝图分量”；一道题涉及的知识点的分量之和乘20（最多加10分）。蓝图是跨模块的统一视角，用来拉平各组估值人的松紧。
   校准加减分：校准人拉平各组估值人的松紧（整组、整模块或单题加减），总评人按考试的15个位置查漏；这些都记在 校准/ 下，逐条有理由。
3. 按总分从高到低取核心；同一个知识点当主知识点的核心题不超过 CARD_CAP 道、被涉及不超过 ANY_CAP 次（免得一个知识点占太多）；其后是备选。
4. 蓝图里两位以上预测人列为“必须进核心”的知识点、估值人给到7分以上的知识点，核心里至少要有一道题，没有就把它排最前的题换进来。
5. 顺序：按总分从高到低，再在每10道里把同模块、同知识点的题错开。
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
GROUPS = ["G1", "G2", "G3", "G4", "G5a", "G5b", "G6", "G7", "G8"]
BLUEPRINTS = ["B1", "B2", "B3"]
N_CORE, N_BACKUP = 160, 40
CARD_CAP = 3            # 同一个知识点当“主知识点”（题目挂的第一个）的核心题上限
ANY_CAP = 5             # 同一个知识点被核心题涉及的次数上限（一道多选会带到四五个知识点）
BP_WEIGHT, BP_CAP = 20, 0.5
MODNAME = {"MZ": "马哲", "P1": "新思想概念", "P2": "发展理论与政策", "P3": "党的建设", "P4": "制度、会议与规划", "H": "党史", "LAW": "法律", "GD": "广东"}
MOD_ORDER = ["MZ", "P1", "P2", "P3", "P4", "H", "LAW", "GD"]


def mod_of(q):
    return "MZ" if q.get("bank") != "fm" else q["module"]


def load():
    bank = json.loads((HERE.parent / "site" / "questions.json").read_text(encoding="utf-8"))
    by_id = {q["id"]: q for q in bank}
    units, ranked, flags, missing = {}, {}, {}, []
    for g in GROUPS:
        f = HERE / "估值" / f"{g}.json"
        if not f.exists():
            missing.append(g)
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        for u in d["units"]:
            units[u["id"]] = {**u, "group": g}
        for i, r in enumerate(d["ranking"]):
            ranked[r["q"]] = {"gain": r["gain"], "why": r["why"], "group": g, "rank": i + 1}
        for x in d["flags"]:
            flags[x["q"]] = x["issue"]
    mass, must = defaultdict(float), Counter()
    nb = 0
    for b in BLUEPRINTS:
        f = HERE / "蓝图" / f"{b}.json"
        if not f.exists():
            missing.append(b)
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        nb += 1
        for p in d["positions"]:
            for c in p["cands"]:
                mass[c["unit"]] += c["p"]
        for u in d["must_units"]:
            must[u] += 1
    for u in mass:
        mass[u] /= max(nb, 1)
    adj_f = HERE / "调整.json"
    adj = json.loads(adj_f.read_text(encoding="utf-8")) if adj_f.exists() else {}
    calib = {}
    for name in ("MZ", "FM", "ALL"):
        cf = HERE / "校准" / f"{name}.json"
        if cf.exists():
            calib[name] = json.loads(cf.read_text(encoding="utf-8"))
        else:
            missing.append("校准/" + name)
    return bank, by_id, units, ranked, flags, dict(mass), must, nb, adj, missing, calib


def spread(chunk):
    """一小段里把同模块、同知识点的题尽量错开（不改变这一段包含哪些题）。"""
    out, rest = [], chunk[:]
    while rest:
        prev = out[-1] if out else None
        pick = None
        for cand in rest:
            if prev is None or (cand["mod"] != prev["mod"] and not set(cand["cards"]) & set(prev["cards"])):
                pick = cand
                break
        if pick is None:
            for cand in rest:
                if not set(cand["cards"]) & set(prev["cards"]):
                    pick = cand
                    break
        pick = pick or rest[0]
        rest.remove(pick)
        out.append(pick)
    return out


def main():
    write = "--write" in sys.argv
    bank, by_id, units, ranked, flags, mass, must, nb, adj, missing, calib = load()
    if missing:
        print("还缺：", "、".join(missing))
    banned = {q["id"] for q in bank if q.get("hold") or q.get("review") or q["id"][:6] in ("GD2024", "GD2025", "GD2026")}
    banned |= set(flags) | set(adj.get("drop") or {})
    # 校准：整组、整模块、单题的加减分相加；校准人补进来的题、剔掉的题
    group_delta, module_delta, delta, notes = Counter(), Counter(), defaultdict(list), {}
    for name, c in calib.items():
        for g, v in (c.get("group_delta") or {}).items():
            group_delta[g] += v
        for m, v in (c.get("module_delta") or {}).items():
            module_delta[m] += v
        for qid, (v, why) in (c.get("delta") or {}).items():
            delta[qid].append((v, f"{name}：{why}"))
        for qid, (g, why) in (c.get("add") or {}).items():
            if qid not in ranked and qid not in banned:
                ranked[qid] = {"gain": g, "why": f"（{name}补）{why}", "group": name, "rank": 99}
        for qid, why in (c.get("drop") or {}).items():
            banned.add(qid)
            notes[qid] = f"{name}剔除：{why}"
    for qid, (v, why) in (adj.get("delta") or {}).items():
        delta[qid].append((v, f"人工：{why}"))

    rows = []
    for qid, r in ranked.items():
        q = by_id[qid]
        if qid in banned:
            continue
        bp = sum(mass.get(c, 0) for c in q["cards"])
        m = mod_of(q)
        d = group_delta.get(r["group"], 0) + module_delta.get(m, 0) + sum(v for v, _ in delta.get(qid, []))
        rows.append({"id": qid, "mod": m, "module": q["module"], "cards": q["cards"], "type": q["type"], "kind": q.get("kind") or "",
                     "polarity": q.get("polarity") or "", "gain": r["gain"], "bp": round(bp, 3), "adj": d,
                     "score": round(r["gain"] + BP_WEIGHT * min(BP_CAP, bp) + d, 1), "group": r["group"], "rank": r["rank"],
                     "why": r["why"] + "".join(f"｜{w}（{v:+d}）" for v, w in delta.get(qid, []))})
    if calib:
        print("校准：整组", dict(group_delta), "整模块", dict(module_delta), f"单题 {len(delta)} 处，补 {sum(1 for r in ranked.values() if r['rank'] == 99)} 道，剔 {len(notes)} 道")
    rows.sort(key=lambda x: (-x["score"], -x["gain"], x["rank"], x["id"]))

    # 必须覆盖的知识点
    need = {u for u, n in must.items() if n >= 2} | {u for u, x in units.items() if x["p"] >= 7}
    core, rest, per_card, per_main = [], [], Counter(), Counter()
    for x in rows:
        if len(core) < N_CORE and per_main[x["cards"][0]] < CARD_CAP and all(per_card[c] < ANY_CAP for c in x["cards"]):
            core.append(x)
            per_card.update(x["cards"])
            per_main[x["cards"][0]] += 1
        else:
            rest.append(x)
    covered = {c for x in core for c in x["cards"]}
    promoted = []
    for u in sorted(need - covered, key=lambda u: -(mass.get(u, 0) * 10 + units.get(u, {}).get("p", 0))):
        cand = next((x for x in rest if u in x["cards"]), None)
        if not cand:
            continue
        # 换掉核心里分数最低、且换掉后不让别的必须覆盖的知识点落空的题
        for victim in reversed(core):
            others = {c for y in core if y is not victim for c in y["cards"]}
            if not (set(victim["cards"]) & need) - others:
                core.remove(victim)
                rest.append(victim)
                break
        rest.remove(cand)
        core.append(cand)
        promoted.append((u, cand["id"]))
        covered = {c for x in core for c in x["cards"]}
    core.sort(key=lambda x: (-x["score"], -x["gain"], x["rank"], x["id"]))
    rest.sort(key=lambda x: (-x["score"], -x["gain"], x["rank"], x["id"]))
    backup = rest[:N_BACKUP]

    def ordered(lst):
        out = []
        for i in range(0, len(lst), 10):
            out += spread(lst[i:i + 10])
        return out

    core_o, backup_o = ordered(core), ordered(backup)
    order = [x["id"] for x in core_o + backup_o]
    assert len(set(order)) == len(order)

    # ---- 报告 ----
    total = Counter(mod_of(q) for q in bank)
    cc, bc = Counter(x["mod"] for x in core), Counter(x["mod"] for x in backup)
    print(f"\n核心 {len(core)} 道（分数 {core[0]['score']}…{core[-1]['score']}），备选 {len(backup)} 道（{backup[0]['score'] if backup else '-'}…{backup[-1]['score'] if backup else '-'}）；蓝图 {nb} 份")
    print("模块        核心  备选  题库   蓝图分量")
    mm = defaultdict(float)
    for u, m in mass.items():
        mm["MZ" if re.match(r"M\d", u) else re.match(r"(K-)?([A-Z]+\d?)", u).group(0).replace("K-", "").rstrip("-")] += m
    def modkey(u):
        if re.match(r"M\d", u):
            return "MZ"
        u2 = u[2:] if u.startswith("K-") else u
        for k in ("LAW", "GD", "P1", "P2", "P3", "P4", "PT", "H"):
            if u2.startswith(k):
                return {"PT": "P3"}.get(k, k)
        return "?"
    mm = defaultdict(float)
    for u, m in mass.items():
        mm[modkey(u)] += m
    for m in MOD_ORDER:
        print(f"{MODNAME[m]:<10s} {cc[m]:4d} {bc[m]:5d} {total[m]:5d}   {mm[m]:.2f}")
    mz = [x for x in core if x["mod"] == "MZ"]
    print("马哲核心按模块：", dict(sorted(Counter(x["module"] for x in mz).items())), "｜按题型：", dict(Counter(x["type"] for x in mz)), "｜按来源：", dict(Counter(x["kind"] for x in mz)))
    pol = Counter(x["polarity"] for x in core if x["kind"] == "基础判断")
    print("核心里的基础判断：", dict(pol), "｜全部核心题型：", dict(Counter(x["type"] for x in core)))
    cut = [x for x in rows if x["id"] not in {y["id"] for y in core}][:8]
    print("核心最后8道：", [(x["id"], x["score"]) for x in core[-8:]])
    print("没进核心的前8道：", [(x["id"], x["score"]) for x in cut])
    if promoted:
        print("为覆盖必留知识点换进核心：", promoted)
    still = sorted(need - {c for x in core for c in x["cards"]})
    print("必留知识点仍没有核心题的：", [(u, units.get(u, {}).get("p"), round(mass.get(u, 0), 2)) for u in still])
    cov_all = sum(mass.values())
    cov_core = sum(m for u, m in mass.items() if u in {c for x in core for c in x["cards"]})
    cov_plan = sum(m for u, m in mass.items() if u in {c for x in core + backup for c in x["cards"]})
    print(f"蓝图分量覆盖：核心 {cov_core / cov_all:.0%}，核心加备选 {cov_plan / cov_all:.0%}（三位预测人列出的题库内知识点概率之和为 {cov_all:.1f}）")
    big = [(c, n) for c, n in Counter(c for x in core for c in x["cards"]).items() if n >= 4]
    print("核心里被涉及4次以上的知识点：", big)
    print("因上限没进核心的高分题：", [(x["id"], x["score"]) for x in rest if x["score"] > core[-1]["score"]][:12])

    if write:
        out = {"generated": adj.get("generated") or "", "order": order, "core": len(core),
               "basis": adj.get("basis") or [], "note": adj.get("note") or "",
               "modules": [{"name": MODNAME[m], "share": (adj.get("share") or {}).get(m, ""), "core": cc[m], "backup": bc[m], "total": total[m]} for m in MOD_ORDER]}
        (HERE / "精选.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        detail = [{"o": i, "tier": "核心" if i < len(core) else "备选", **{k: x[k] for k in ("id", "module", "cards", "type", "kind", "gain", "bp", "adj", "score", "why")}} for i, x in enumerate(core_o + backup_o)]
        (HERE / "精选清单.json").write_text(json.dumps(detail, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print("已写 精选.json、精选清单.json")


if __name__ == "__main__":
    main()

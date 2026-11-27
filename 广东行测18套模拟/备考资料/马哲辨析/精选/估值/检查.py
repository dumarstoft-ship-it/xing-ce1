"""检查估值人或蓝图预测人写出的文件格式是否合格。

用法：
  python3 检查.py 估值 G1        检查 估值/G1.json
  python3 检查.py 蓝图 B1        检查 蓝图/B1.json
  python3 检查.py 校准 MZ        检查 校准/MZ.json（MZ 马哲、FM 政常、ALL 总评）
合格时最后一行打印“合格”，否则逐条列出问题并以非零状态退出。
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent          # 精选/估值
BASE = HERE.parent                              # 精选
RANK_N = {"G1": 40, "G2": 40, "G3": 40, "G4": 40, "G5a": 28, "G5b": 22, "G6": 24, "G7": 30, "G8": 32}


def catalog():
    ids = set()
    for line in (BASE / "知识点目录.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"- ([^｜]+)｜", line)
        if m:
            ids.add(m.group(1))
    return ids


def check_value(g):
    errs = []
    f = HERE / f"{g}.json"
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return [f"读不了 {f}：{e}"]
    bank = json.loads((HERE / "对照" / f"{g}_题库.json").read_text(encoding="utf-8"))
    ref = json.loads((HERE / "对照" / f"{g}_真题.json").read_text(encoding="utf-8"))
    past = {r["id"] for r in json.loads((BASE / "画像" / "merged.json").read_text(encoding="utf-8"))}
    units = [u["id"] for u in bank["units"]]
    own = {q["id"] for u in bank["units"] for q in u["questions"] if q["primary"]}
    banned = set(ref["不可选"])
    for k in ("group", "units", "ranking", "flags", "notes"):
        if k not in d:
            errs.append(f"缺少字段 {k}")
    if errs:
        return errs
    got = [u.get("id") for u in d["units"]]
    if sorted(got) != sorted(units):
        miss = sorted(set(units) - set(got))
        extra = sorted(set(got) - set(units))
        dup = sorted({x for x in got if got.count(x) > 1})
        errs.append(f"units 应当恰好是本组 {len(units)} 个知识点各一条；缺 {miss[:10]}，多 {extra[:10]}，重复 {dup[:10]}")
    for u in d["units"]:
        uid = u.get("id")
        for k in ("p", "l"):
            if not isinstance(u.get(k), int) or not 0 <= u[k] <= 10:
                errs.append(f"{uid} 的 {k} 应为0—10的整数")
        if not isinstance(u.get("why"), str) or not u["why"].strip() or len(u["why"]) > 60:
            errs.append(f"{uid} 的 why 应为1—60字")
        h = u.get("hits")
        if not isinstance(h, dict) or any(not isinstance(h.get(k), list) for k in ("confirm", "reject", "add")):
            errs.append(f"{uid} 的 hits 应为含 confirm、reject、add 三个数组的对象")
        else:
            for k in ("confirm", "reject", "add"):
                bad = [x for x in h[k] if x not in past]
                if bad:
                    errs.append(f"{uid} 的 hits.{k} 里有不存在的真题编号 {bad[:5]}")
    flagged = {x.get("q") for x in d["flags"] if isinstance(x, dict)} if isinstance(d["flags"], list) else set()
    n = min(RANK_N[g], len(own - banned - flagged))      # 可选的题不够时，有多少排多少
    rk = d["ranking"]
    if len(rk) != n:
        errs.append(f"ranking 应当恰好 {n} 条，现在 {len(rk)} 条")
    hit = sorted(flagged & {r.get("q") for r in rk})
    if hit:
        errs.append(f"flags 里记了硬伤的题不要排进 ranking：{hit[:10]}")
    qs = [r.get("q") for r in rk]
    dup = sorted({x for x in qs if qs.count(x) > 1})
    if dup:
        errs.append(f"ranking 里有重复的题 {dup[:10]}")
    for i, r in enumerate(rk):
        q = r.get("q")
        if q not in own:
            errs.append(f"ranking 第{i + 1}条 {q} 不是本组的题")
        if q in banned:
            errs.append(f"ranking 第{i + 1}条 {q} 在“不可选”里（{ref['不可选'][q]}）")
        if not isinstance(r.get("gain"), int) or not 0 <= r["gain"] <= 100:
            errs.append(f"ranking 第{i + 1}条 {q} 的 gain 应为0—100的整数")
        if not isinstance(r.get("why"), str) or not r["why"].strip() or len(r["why"]) > 60:
            errs.append(f"ranking 第{i + 1}条 {q} 的 why 应为1—60字")
    gains = [r.get("gain") for r in rk if isinstance(r.get("gain"), int)]
    if any(a < b for a, b in zip(gains, gains[1:])):
        errs.append("ranking 的 gain 应当从高到低（可以相等）")
    if not isinstance(d["flags"], list) or any(not isinstance(x, dict) or "q" not in x or "issue" not in x for x in d["flags"]):
        errs.append("flags 应为数组，每条有 q 和 issue")
    else:
        allq = {q["id"] for u in bank["units"] for q in u["questions"]}
        bad = [x["q"] for x in d["flags"] if x["q"] not in allq]
        if bad:
            errs.append(f"flags 里有不是本组的题 {bad[:5]}")
    if not isinstance(d["notes"], str):
        errs.append("notes 应为字符串")
    return errs


def check_blueprint(b):
    errs = []
    f = BASE / "蓝图" / f"{b}.json"
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return [f"读不了 {f}：{e}"]
    cat = catalog()
    for k in ("lens", "positions", "must_units", "notes"):
        if k not in d:
            errs.append(f"缺少字段 {k}")
    if errs:
        return errs
    ps = d["positions"]
    if [p.get("n") for p in ps] != list(range(1, 16)):
        errs.append("positions 应当是第1到第15题各一条，按题号排")
    for p in ps:
        n = p.get("n")
        if p.get("type") not in ("判断", "单选", "多选"):
            errs.append(f"第{n}题 type 应为 判断/单选/多选")
        for k in ("slot", "what"):
            if not isinstance(p.get(k), str) or not p[k].strip():
                errs.append(f"第{n}题缺 {k}")
        if not isinstance(p.get("outside"), (int, float)) or not 0 <= p["outside"] <= 1:
            errs.append(f"第{n}题 outside 应为0—1的数")
        cs = p.get("cands")
        if not isinstance(cs, list):
            errs.append(f"第{n}题 cands 应为数组")
            continue
        tot = 0
        for c in cs:
            if c.get("unit") not in cat:
                errs.append(f"第{n}题 cands 里的 {c.get('unit')} 不在知识点目录里")
            if not isinstance(c.get("p"), (int, float)) or not 0 < c["p"] <= 1:
                errs.append(f"第{n}题 {c.get('unit')} 的 p 应为0—1之间的数（不含0）")
            else:
                tot += c["p"]
        us = [c.get("unit") for c in cs]
        if len(us) != len(set(us)):
            errs.append(f"第{n}题 cands 里有重复的知识点")
        if tot > 3.0001:
            errs.append(f"第{n}题 cands 的 p 之和是 {tot:.2f}，不应超过3")
    mu = d["must_units"]
    if not isinstance(mu, list) or len(mu) > 40 or any(x not in cat for x in mu) or len(mu) != len(set(mu)):
        errs.append("must_units 应为不超过40个、不重复、目录里存在的知识点编号")
    return errs


def check_calib(name):
    """校准文件：校准/MZ.json、校准/FM.json、校准/ALL.json。"""
    errs = []
    f = BASE / "校准" / f"{name}.json"
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return [f"读不了 {f}：{e}"]
    bank = {q["id"]: q for q in json.loads((BASE.parent / "site" / "questions.json").read_text(encoding="utf-8"))}
    mz = lambda q: bank[q].get("bank") != "fm"
    scope = {"MZ": lambda q: mz(q), "FM": lambda q: not mz(q), "ALL": lambda q: True}[name]
    groups = {"MZ": ["G1", "G2", "G3", "G4"], "FM": ["G5a", "G5b", "G6", "G7", "G8"], "ALL": []}[name]
    mods = ["MZ", "P1", "P2", "P3", "P4", "H", "LAW", "GD"]
    for k in ("group_delta", "module_delta", "delta", "add", "drop", "notes"):
        if k not in d:
            errs.append(f"缺少字段 {k}（没有内容也要给空对象，notes 给字符串）")
    if errs:
        return errs
    for g, v in d["group_delta"].items():
        if g not in groups or not isinstance(v, int) or abs(v) > 15:
            errs.append(f"group_delta 只能给 {groups} 里的组，值为绝对值不超过15的整数：{g}={v}")
    for m, v in d["module_delta"].items():
        if m not in mods or not isinstance(v, int) or abs(v) > 15 or (name == "MZ" and m != "MZ") or (name == "FM" and m == "MZ"):
            errs.append(f"module_delta 的模块应在 {mods} 里且属于你的范围，值为绝对值不超过15的整数：{m}={v}")
    for q, v in d["delta"].items():
        if q not in bank or not scope(q):
            errs.append(f"delta 里的 {q} 不是你范围内的题")
        elif not (isinstance(v, list) and len(v) == 2 and isinstance(v[0], int) and abs(v[0]) <= 25 and isinstance(v[1], str) and 0 < len(v[1]) <= 80):
            errs.append(f"delta 的 {q} 应为 [整数（绝对值不超过25）, 理由（80字以内）]")
    for q, v in d["add"].items():
        if q not in bank or not scope(q):
            errs.append(f"add 里的 {q} 不是你范围内的题")
        elif bank[q].get("hold") or bank[q].get("review") or q[:6] in ("GD2024", "GD2025", "GD2026"):
            errs.append(f"add 里的 {q} 不可选（暂停出题或用户已做过的近三年真题）")
        elif not (isinstance(v, list) and len(v) == 2 and isinstance(v[0], int) and 0 <= v[0] <= 100 and isinstance(v[1], str) and 0 < len(v[1]) <= 80):
            errs.append(f"add 的 {q} 应为 [gain（0—100的整数）, 理由（80字以内）]")
    for q, v in d["drop"].items():
        if q not in bank or not scope(q):
            errs.append(f"drop 里的 {q} 不是你范围内的题")
        elif not (isinstance(v, str) and 0 < len(v) <= 120):
            errs.append(f"drop 的 {q} 应给理由（120字以内）")
    if not isinstance(d["notes"], str):
        errs.append("notes 应为字符串")
    return errs


if __name__ == "__main__":
    kind, name = sys.argv[1], sys.argv[2]
    errs = check_value(name) if kind == "估值" else check_blueprint(name) if kind == "蓝图" else check_calib(name)
    for e in errs[:60]:
        print("✗", e)
    if errs:
        print(f"共 {len(errs)} 个问题")
        sys.exit(1)
    print("合格")

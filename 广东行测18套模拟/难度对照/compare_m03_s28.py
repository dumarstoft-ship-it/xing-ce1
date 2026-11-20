"""M03与粉笔第28季逐题难度对比（2026-11-20，用户问“M03和粉笔广东模考卷哪个难、难多少”）。

三位评分人各评一块，同一块里四张卷（或两张卷加锚点）由同一人评，卷与卷之间直接可比：
- M03-S28_数资.json：数学运算第36—45题、资料分析第71—90题，按 rubric.md；另评GD2025锚点，秒数按锚点换算到真题评分人的尺度。
- 推理_M03-S28.json：数字推理第31—35题、图形推理第46—50题、科学推理第66—70题，M03、S28、GD2025、GD2026四卷。
- 逻辑_M03-S28.json：逻辑判断第51—65题，四卷。
"""
import json
import statistics
from collections import Counter
from pathlib import Path

D = Path(__file__).resolve().parent


def load(f):
    p = D / f
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


def data_part():
    rows = load("M03-S28_数资.json")
    gd = load("GD.json")
    anch = set(range(36, 41)) | set(range(71, 81))
    base = sum(x["est_seconds"] for x in gd if x.get("paper") == "GD2025" and x.get("number") in anch)
    mine = sum(x["est_seconds"] for x in rows if x.get("paper") == "GD2025" and x.get("number") in anch)
    k = base / mine if mine else 1.0
    real = json.loads((D / "summary.json").read_text(encoding="utf-8"))
    real = [r for r in real if r["paper"].startswith("GD")]
    rd = statistics.mean(r["data_min"] for r in real)
    rm = statistics.mean(r["math_min"] for r in real)
    out = {}
    for p in ("M03", "S28"):
        qs = [x for x in rows if x.get("paper") == p and "number" in x]
        mats = [x for x in rows if x.get("paper") == p and "group" in x]
        data = [x for x in qs if 71 <= x["number"] <= 90]
        math = [x for x in qs if 36 <= x["number"] <= 45]
        modes = ["读", "一步", "两步", "三步及以上"]
        dm = Counter(x["mode"] for x in data)
        mm = Counter(x["mode"] for x in math)
        dmin = k * (sum(x["est_seconds"] for x in data) + sum(x["material_seconds"] for x in mats)) / 60
        mmin = k * sum(x["est_seconds"] for x in math) / 60
        out[p] = {"资料作答方式": [dm.get(m, 0) for m in modes], "资料分钟": round(dmin, 1),
                  "数学作答方式": [mm.get(m, 0) for m in modes], "数学分钟": round(mmin, 1),
                  "比真题平均多": round(dmin - rd + mmin - rm, 1)}
    return {"换算系数": round(k, 3), "真题平均资料": round(rd, 1), "真题平均数学": round(rm, 1), "卷": out}


def other_part(f, parts):
    rows = load(f)
    out = {}
    for paper in ("M03", "S28", "GD2025", "GD2026"):
        for part in parts:
            qs = [x for x in rows if x.get("paper") == paper and (x.get("part") or "逻辑") == part]
            if not qs:
                continue
            lv = Counter(x.get("level") for x in qs)
            out.setdefault(paper, {})[part] = {
                "题数": len(qs), "秒数": sum(x.get("est_seconds") or 0 for x in qs),
                "易/中/难": [lv.get("易", 0), lv.get("中", 0), lv.get("难", 0)],
                "规律少见或偏怪": sum(1 for x in qs if x.get("rule") in ("少见", "偏怪")),
                "科推超纲": sum(1 for x in qs if x.get("knowledge") == "超纲"),
                "强干扰项": sum(1 for x in qs if x.get("distractor") == "强"),
                "字数": sum(x.get("chars") or 0 for x in qs),
                "可商榷": sum(1 for x in qs if x.get("ambiguous")),
            }
    return out


if __name__ == "__main__":
    res = {"数资": data_part(), "推理": other_part("推理_M03-S28.json", ["数推", "图推", "科推"]),
           "逻辑": other_part("逻辑_M03-S28.json", ["逻辑"])}
    print(json.dumps(res, ensure_ascii=False, indent=1))
    (D / "M03-S28_汇总.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")

"""重建题源排除名单中“集训第1、2天用过的题”两项（M09起用广东真题组卷时排除）。

    python3 广东行测18套模拟/重编/tools/exclusions.py

依据三者合并：集训题册第1、2天每题登记的原卷题号；第1天数量题锁定表；题干、材料文字与题库比对
（顺带找出县级、乡镇两卷的相同题和相同材料）。题库新整理了卷子后重跑一次。其余各项（整卷排除、
习题本图推引用的原题）不动。
"""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DRILL = ROOT / "广东行测24天集训"
BANKS = ("广东/行测/2013-2021", "广东/行测/2022-2026")
OUT = ROOT / "广东行测18套模拟/重编/题源排除.json"


def norm(s):
    return re.sub(r"[\s\W_]+", "", s or "")


def pid(paper):
    m = re.match(r"GD(20\d\d)([XZ]?)$", paper or "")
    if not m:
        return None
    y, v = m.groups()
    return f"GD{y}-{'XJ' if v == 'X' else 'XZ'}" if v else f"GD{y}"


def main():
    bank = {}
    for d in BANKS:
        for f in sorted((ROOT / d).glob("GD20*.jsonl")):
            for line in open(f, encoding="utf-8"):
                q = json.loads(line)
                bank[q["id"]] = q
    idx = {}
    for i, q in bank.items():
        k = norm(q["stem"])[:30]
        if len(k) >= 12:
            idx.setdefault(k, []).append(i)
    qids, why = set(), {}
    drill_q = [json.loads(l) for l in open(DRILL / "GPT_复核/第1批/questions.jsonl", encoding="utf-8")]
    drill_q = [q for q in drill_q if q.get("day") in ("D01", "D02")]
    for q in drill_q:
        s = q.get("source") or {}
        p = pid(s.get("paper"))
        if p and s.get("qno"):
            i = f"{p}-Q{int(s['qno']):03d}"
            qids.add(i)
            why[i] = f"集训{q['id']}"
    for r in csv.DictReader(open(DRILL / "GPT_数量/D01/D01_已用题锁定_v2.csv", encoding="utf-8-sig")):
        m = re.match(r"(GD20\d\d[XZ]?)-(\d+)$", r["source_key"] or "")
        if m and pid(m.group(1)):
            i = f"{pid(m.group(1))}-Q{int(m.group(2)):03d}"
            qids.add(i)
            why.setdefault(i, f"集训{r['training_id']}")
    for i in list(qids):
        if i in bank:
            for j in idx.get(norm(bank[i]["stem"])[:30], []):
                if j not in qids:
                    qids.add(j)
                    why[j] = f"与{i}同题"
    for q in drill_q:
        for j in idx.get(norm(q.get("stem"))[:30], []):
            if j not in qids:
                qids.add(j)
                why[j] = f"题干与集训{q['id']}相同"
    mats = set()
    for r in csv.DictReader(open(DRILL / "GPT_复核/第1批/D02_材料连续编排对照.csv", encoding="utf-8-sig")):
        m = re.match(r"ZLM-(GD20\d\d[XZ]?)-(\d+)$", r["material_id"])
        if m and pid(m.group(1)):
            mats.add(f"{pid(m.group(1))}-M{int(m.group(2))}")
    mtext = {}
    for q in bank.values():
        m = q.get("material")
        if m:
            t = norm("".join(b.get("text", "") for b in m.get("content") or [] if b.get("type") == "text"))
            if len(t) >= 30:
                mtext.setdefault(t[:40], set()).add(m["id"])
    for line in open(DRILL / "GPT_复核/第1批/materials.jsonl", encoding="utf-8"):
        t = norm(json.dumps(json.loads(line), ensure_ascii=False))
        for k, ids in mtext.items():
            if k[:30] in t:
                mats |= ids
    ex = json.loads(OUT.read_text(encoding="utf-8"))
    ex["集训第1_2天_广东真题"] = sorted(qids)
    ex["集训第1_2天_广东真题_依据"] = {i: why.get(i, "锁定表或题册登记") for i in sorted(qids)}
    ex["集训第2天_广东资料材料组"] = sorted(mats)
    OUT.write_text(json.dumps(ex, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"集训第1、2天：{len(qids)}题；资料组{len(mats)}组")


if __name__ == "__main__":
    main()

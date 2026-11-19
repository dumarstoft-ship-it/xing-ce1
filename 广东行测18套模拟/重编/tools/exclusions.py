"""重建题源排除名单里由程序算出的几项，并按名单刷新题池各题的“excluded”。

    python3 广东行测18套模拟/重编/tools/exclusions.py

题库新整理了卷子、题池新归了类，或手工改了名单里的“题目有问题”“近似题”后，重跑一次。

程序算的项：
- 集训第1_2天_广东真题（及_依据）：集训题册第1、2天每题登记的原卷题号、第1天数量题锁定表、
  题干与题库比对，三者合并；
- 集训第2天_广东资料材料组：编排对照表登记的材料，加材料文字与题库比对；
- 同题连带：上面各项和手工各项里的题（材料组），在别的卷里的同一题（同一材料）一并排除。
  同题按两种依据：题池归类时逐题比对记下的 dup_of；题干（短题干连同选项）文字相同，
  且这段文字在题库里不超过3处（排除“从所给的四个选项中……”这类通用题干）。

手工维护、程序不改的项：排除整卷、习题本两项、近似题、题目有问题。
"""
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DRILL = ROOT / "广东行测24天集训"
BANKS = ("广东/行测/2013-2021", "广东/行测/2022-2026", "广东/事业单位/结构化")
HERE = ROOT / "广东行测18套模拟/重编"
OUT = HERE / "题源排除.json"
POOLS = HERE / "题池"
MANUAL_Q = ("习题本平面图推200题_广东原题", "习题本固定题型178题_广东原题")
MANUAL_D = ("近似题", "题目有问题")


def norm(s):
    return re.sub(r"[\s\W_]+", "", s or "")


def pid(paper):
    m = re.match(r"GD(20\d\d)([XZ]?)$", paper or "")
    if not m:
        return None
    y, v = m.groups()
    return f"GD{y}-{'XJ' if v == 'X' else 'XZ'}" if v else f"GD{y}"


def paper_of(i):
    return re.sub(r"-(Q\d+|M\d+)$", "", i)


def text_key(q):
    """比对用文字：题干；题干太短（如数列）时连同选项。"""
    s = norm(q.get("stem"))
    if len(s) < 20:
        s += norm("".join(str(o.get("text") or "") for o in q.get("options") or []))
    return s


def windows(s, n=20, shifts=6):
    """前几个字可能有出入（如原卷多一个“为”字），取起点0—5的各段。"""
    return {s[i:i + n] for i in range(shifts) if len(s) >= i + n}


def load_bank():
    bank = {}
    for d in BANKS:
        for f in sorted(list((ROOT / d).glob("GD20*.jsonl")) + list((ROOT / d).glob("SYDW20*.jsonl"))):
            for line in open(f, encoding="utf-8"):
                q = json.loads(line)
                bank[q["id"]] = q
    return bank


def load_pools():
    qs, ms = {}, {}
    for f in sorted(POOLS.glob("*.json")):
        for r in json.loads(f.read_text(encoding="utf-8")):
            if "id" in r:
                qs[r["id"]] = (f, r)
            elif r.get("material_id"):
                ms[r["material_id"]] = (f, r)
    return qs, ms


class Same:
    """同题（同材料）关系：并查集。"""

    def __init__(self):
        self.p = {}

    def find(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        self.p[self.find(a)] = self.find(b)

    def group(self, x):
        r = self.find(x)
        return sorted(k for k in self.p if self.find(k) == r)


def main():
    bank = load_bank()
    pool_q, pool_m = load_pools()

    # 题干比对索引（只用在题库里不超过3处的文字段）
    win = defaultdict(set)
    for i, q in bank.items():
        for w in windows(text_key(q)):
            win[w].add(i)
    first = {}
    for i, q in bank.items():
        s = text_key(q)
        if len(s) >= 20:
            first[i] = s[:20]

    def same_text(i):
        """与题i题干相同的题（题干开头20字出现在对方开头5字以内，且不是通用题干）。"""
        out = set()
        for w in windows(text_key(bank[i])):
            ids = win.get(w, set())
            if len(ids) <= 3:
                out |= ids
        k = first.get(i)
        if k and len(win.get(k, ())) <= 3:
            out |= win.get(k, set())
        out.discard(i)
        return out

    same = Same()
    for i, (_, r) in pool_q.items():
        d = r.get("dup_of")
        if d and re.search(r"-Q\d+$", d):
            same.union(i, d)
    for m, (_, r) in pool_m.items():
        if r.get("dup_of"):
            same.union(m, r["dup_of"])
    for i in bank:
        for j in same_text(i):
            same.union(i, j)

    # 集训第1、2天用过的题
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
    for q in drill_q:
        s = norm(q.get("stem"))
        if len(s) < 20:
            continue
        for w in windows(s):
            ids = win.get(w, set())
            if len(ids) <= 3:
                for j in ids:
                    if j not in qids:
                        qids.add(j)
                        why[j] = f"题干与集训{q['id']}相同"

    # 集训第2天用过的资料材料
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

    # 同题连带
    base = {}
    for i in qids:
        base[i] = "集训第1、2天用过"
    for m in mats:
        base[m] = "集训第2天用过的资料材料"
    for k in MANUAL_Q:
        for i in ex.get(k) or []:
            base.setdefault(i, "习题本图推收录")
    for k in MANUAL_D:
        for i, r in (ex.get(k) or {}).items():
            base.setdefault(i, r)
    carried = {}
    for i in sorted(base):
        for j in same.group(i):
            if j not in base and j not in carried:
                carried[j] = f"与{i}同{'材料' if '-M' in i else '题'}（{i}：{base[i]}）"
    ex["同题连带"] = carried
    OUT.write_text(json.dumps(ex, ensure_ascii=False, indent=1), encoding="utf-8")

    # 刷新题池的 excluded
    reason = dict(base)
    reason.update(carried)
    whole = set(ex.get("排除整卷") or [])
    mat_of = {i: r.get("material_id") for i, (_, r) in pool_q.items()}
    changed = defaultdict(int)
    files = defaultdict(list)
    for f in sorted(POOLS.glob("*.json")):
        recs = json.loads(f.read_text(encoding="utf-8"))
        for r in recs:
            k = r.get("id") or r.get("material_id")
            e = None
            if paper_of(k) in whole:
                e = "整卷不作题源"
            elif k in reason:
                e = reason[k]
            elif r.get("id") and mat_of.get(k) in reason:
                e = f"资料组{mat_of[k]}：{reason[mat_of[k]]}"
            if (r.get("excluded") or None) != e:
                changed[f.name] += 1
            r["excluded"] = e
        f.write_text(json.dumps(recs, ensure_ascii=False, indent=1), encoding="utf-8")
        files[f.name] = recs
    print(f"集训第1、2天：{len(qids)}题；资料组{len(mats)}组；同题连带{len(carried)}项")
    for k, v in sorted(changed.items()):
        print(f"题池 {k}：excluded 改了{v}条")


if __name__ == "__main__":
    main()

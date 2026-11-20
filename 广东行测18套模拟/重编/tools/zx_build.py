"""专项（图推、数推、科推，2026-11-20起）：把解好的专项题按规律分组、分到每天，组成练习本。

    python3 广东行测18套模拟/重编/tools/zx_build.py plan     # 按解题记录和方法要点排出 专项/编排.json
    python3 广东行测18套模拟/重编/tools/zx_build.py build    # 按 专项/编排.json 输出每天的题目.jsonl、答案与解析

输入：重编/专项/分配.json（哪些题进专项）、专项/解题/*.json（答案、解析、规律细类）、专项/方法/*.json（方法要点卡）。
输出：广东行测18套模拟/专项/D1…D5/ 下的 题目.jsonl（排版用，不含答案）、答案.json、答案与解析.md、来源登记.jsonl。
排版：python3 广东行测18套模拟/打印排版/build_print.py 专项/D1 --font-dir <字体目录> --no-notice --title … --cover-tip …
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_paper as bp  # noqa: E402

R, S = bp.R, bp.S
ZX = R / "专项"
OUT = S / "专项"
DAYS = [(1, "11月21日"), (2, "11月22日"), (3, "11月23日"), (4, "11月24日"), (5, "11月25日")]
PART_SEC = {"数推": ("数量关系", "数字推理"), "图推": ("判断推理", "图形推理"), "科推": ("科学推理", None)}
PART_ORDER = ["数推", "图推", "科推"]
# 教的顺序：先易认的规律，后综合；空间放图推最后
PATTERN_ORDER = {
    "数推": ["多级差", "多重数列", "分数数列", "递推", "幂次", "图形数阵", "机械划分", "其他"],
    "图推": ["位置", "样式", "属性", "数量", "分类分组", "其他", "空间"],
    "科推": ["力学", "电学", "光热声", "化学", "生物", "地理"],
}
LEVEL = {"易": 0, "中": 1, "难": 2}
FRAC = re.compile(r"(?<![\d.$])(\d+)/(\d+)(?![\d.])")
CN = "一二三四五六七八九十"


def jload(p, default=None):
    return json.loads(Path(p).read_text(encoding="utf-8")) if Path(p).exists() else default


def records():
    out = {}
    for f in sorted((ZX / "解题").glob("*.json")):
        if f.stem.endswith("_blind") or f.stem.endswith("_second"):
            continue
        for r in jload(f, []):
            out[r["id"]] = dict(r, _group=f.stem)
    return out


def cards():
    out = []
    for f in sorted((ZX / "方法").glob("*.json")):
        for c in jload(f, []):
            out.append(dict(c, _group=f.stem))
    return out


def part_of(r):
    return r.get("category") or {"数字推理": "数推", "图形推理": "图推", "科学推理": "科推"}.get(r.get("section"), "")


def pattern_rank(part, pat):
    order = PATTERN_ORDER[part]
    for i, p in enumerate(order):
        if pat and pat.startswith(p):
            return i
    return len(order)


# ---------------------------------------------------------------- 排每天的题
def plan():
    alloc = jload(ZX / "分配.json")
    recs = records()
    want = [x["id"] for rows in alloc["专项"].values() for x in rows]
    missing = [i for i in want if i not in recs]
    if missing:
        raise SystemExit(f"还没有解题记录：{len(missing)}题，如 {missing[:5]}")
    use = [i for i in want if not recs[i].get("replace_recommended")]
    dropped = {i: recs[i].get("prior_note") or "解题人建议不用" for i in want if recs[i].get("replace_recommended")}
    cs = cards()
    # 每题归到第一张列了它的卡；没被任何卡列到的，按 规律 归到同规律的第一张卡，再没有就单列
    owner = {}
    for c in cs:
        for i in c.get("example_ids") or []:
            if i in recs and i in use:
                owner.setdefault(i, c["title"])
    by_title = {c["title"]: c for c in cs}
    for i in use:
        if i not in owner:
            r = recs[i]
            same = [c for c in cs if c.get("pattern") == r.get("pattern") and c["_group"] == r["_group"]]
            owner[i] = same[0]["title"] if same else f"{r.get('pattern') or '其他'}"
    # 各部分：卡按教的顺序排，卡内按难度、秒数
    blocks = {p: [] for p in PART_ORDER}
    groups = defaultdict(list)
    for i in use:
        groups[owner[i]].append(i)
    for title, ids in groups.items():
        r0 = recs[ids[0]]
        part = part_of(r0)
        c = by_title.get(title, {})
        ids.sort(key=lambda i: (LEVEL.get(recs[i].get("difficulty"), 1), recs[i].get("est_seconds") or 0, i))
        blocks[part].append({"part": part, "card": title, "pattern": c.get("pattern") or r0.get("pattern"),
                             "subpattern": c.get("subpattern"), "ids": ids})
    for part in PART_ORDER:
        blocks[part].sort(key=lambda b: (pattern_rank(part, b["pattern"]), b["card"]))
    # 每部分按题数切成5段（尽量不拆卡；拆开的卡次日重印方法要点并注“续”）
    days = [{"day": d, "date": dt, "blocks": []} for d, dt in DAYS]
    for part in PART_ORDER:
        flat = [(b, i) for b in blocks[part] for i in b["ids"]]
        n = len(flat)
        cuts = [round(n * k / len(DAYS)) for k in range(len(DAYS) + 1)]
        # 切点挪到最近的卡边界（前后各挪不超过2题）
        bounds = {k for k in range(n + 1) if k == 0 or k == n or flat[k][0] is not flat[k - 1][0]}
        for j in range(1, len(cuts) - 1):
            near = [b for b in bounds if abs(b - cuts[j]) <= 2 and cuts[j - 1] < b < cuts[j + 1]]
            if near:
                cuts[j] = min(near, key=lambda b: abs(b - cuts[j]))
        for d in range(len(DAYS)):
            seg = flat[cuts[d]:cuts[d + 1]]
            cur = None
            for b, i in seg:
                if cur is None or cur["card"] != b["card"]:
                    cont = any(x is b for x, _ in flat[:cuts[d]])
                    cur = {"part": part, "card": b["card"], "continued": cont, "ids": []}
                    days[d]["blocks"].append(cur)
                cur["ids"].append(i)
    for d in days:
        secs = sum(recs[i].get("est_seconds") or 60 for b in d["blocks"] for i in b["ids"])
        d["n"] = sum(len(b["ids"]) for b in d["blocks"])
        d["est_minutes"] = round(secs / 60)
        d["minutes"] = int(5 * round((secs / 60 * 1.5 + 2) / 5))   # 普通考生约为熟练考生的1.5倍，取整到5分钟
    out = {"说明": "专项每天一份：数推、图推、科推三部分，每部分按规律分组，组前印方法要点。"
                   "题目来自 分配.json 的专项部分；解题人建议不用的题不进专项。",
           "days": days, "不用": dropped}
    (ZX / "编排.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    for d in days:
        parts = defaultdict(int)
        for b in d["blocks"]:
            parts[b["part"]] += len(b["ids"])
        print(f"D{d['day']} {d['date']}：{d['n']}题 {dict(parts)} 熟练约{d['est_minutes']}分钟，建议{d['minutes']}分钟，{len(d['blocks'])}组")
    print("不用：", dropped)


# ---------------------------------------------------------------- 组练习本
def apply_record_edits(rec, r, n):
    for e in r.get("edits") or []:
        blocks = rec["stem"] if e["where"] == "stem" else rec["options"][e["where"]]
        hit = [b for b in blocks if b["type"] == "text" and e["old"] in b["text"]]
        if len(hit) != 1 or hit[0]["text"].count(e["old"]) != 1:
            raise SystemExit(f"第{n}题（{r['id']}）：改动原文未唯一命中：{e['old']}")
        hit[0]["text"] = hit[0]["text"].replace(e["old"], e["new"])


def source_label(sid):
    m = re.match(r"(GDXD|GD|SYDW)(20\d\d)-?(\w*?)-Q(\d+)$", sid)
    if not m:
        return sid
    k, y, v, q = m.groups()
    q = int(q)
    if k == "SYDW":
        return f"{y}年广东事业单位统考第{q}题"
    if k == "GDXD":
        return f"{y}年广东选调生考试第{q}题"
    var = {"XJ": "县级卷", "XZ": "乡镇卷", "1": "一卷", "3": "三卷"}.get(v, "")
    return f"{y}年广东省考{var}第{q}题"


def build(only=None):
    pl = jload(ZX / "编排.json")
    recs = records()
    cmap = {c["title"]: c for c in cards()}
    OUT.mkdir(parents=True, exist_ok=True)
    for d in pl["days"]:
        tag = f"D{d['day']}"
        if only and tag not in only:
            continue
        qs, ans, reg, md = [], {}, [], []
        n = 0
        per_part = defaultdict(list)
        for b in d["blocks"]:
            per_part[b["part"]].append(b)
        md += [f"# 专项第{CN[d['day'] - 1]}天（{d['date']}）答案与解析", "",
               f"共{d['n']}题，建议用时{d['minutes']}分钟（熟练考生约{d['est_minutes']}分钟）。题目都是广东真题，答案用来源答案，"
               "每题先由一人不看答案独立解出并写解析，再与来源答案对照。", ""]
        rows = []
        for pi, part in enumerate(p for p in PART_ORDER if per_part.get(p)):
            sec, sub = PART_SEC[part]
            md += [f"## 第{CN[pi]}部分　{ {'数推': '数字推理', '图推': '图形推理', '科推': '科学推理'}[part]}", ""]
            for b in per_part[part]:
                c = cmap.get(b["card"], {"title": b["card"], "points": []})
                title = c["title"] + ("（续）" if b.get("continued") else "")
                md += [f"### {title}", ""] + [f"- {p}" for p in c.get("points") or []] + [""]
                for k, sid in enumerate(b["ids"]):
                    n += 1
                    r = recs[sid]
                    d0, g = bp.GD_Q[sid]
                    if r["answer"] != bp.gd_answer(g):
                        raise SystemExit(f"{tag}第{n}题（{sid}）：解题答案{r['answer']}与来源答案{bp.gd_answer(g)}不一致")
                    stem, options = bp.gd_blocks(d0, g)
                    if r.get("stem_fill"):
                        stem = [{"type": "text", "text": r["stem_fill"]}] + [x for x in stem if x["type"] != "text"]
                    rec = {"id": f"ZX-{tag}-Q{n:03d}", "number": n, "section": sec, "subtype": sub,
                           "question_type": "single_choice", "stem": stem, "options": options,
                           "options_mode": "text_or_mixed", "materials": []}
                    if all(len(v) == 1 and v[0]["type"] == "text" and re.fullmatch(r"见题图中(?:标为)?的?\s*[A-D]\s*(?:的)?选项。?", v[0]["text"].strip())
                           for v in rec["options"].values()):
                        rec["options_mode"] = "in_figure"
                        rec["options"] = {x: [{"type": "text", "text": f"见题图中的 {x} 选项"}] for x in rec["options"]}
                    apply_record_edits(rec, r, n)
                    if part == "数推":   # 数列里的分数原卷都是上下排的，题库转写成斜线；按原卷排成分数
                        for blk in rec["stem"] + [x for v in rec["options"].values() for x in v]:
                            if blk["type"] == "text":
                                blk["text"] = FRAC.sub(r"$\\frac{\1}{\2}$", blk["text"])
                    if k == 0:
                        rec["block"] = {"title": title, "points": c.get("points") or []}
                    qs.append(rec)
                    ans[n] = {"answer": r["answer"], "source_id": sid, "pattern": r.get("pattern"),
                              "subpattern": r.get("subpattern"), "analysis": r["analysis"]}
                    reg.append({"number": n, "source_id": sid, "source_desc": source_label(sid),
                                "edits": r.get("edits") or [], "stem_fill": r.get("stem_fill")})
                    rows.append((n, r["answer"]))
                    md += [f"**第{n}题**　答案 **{r['answer']}**　（{source_label(sid)}；{r.get('subpattern') or r.get('pattern') or ''}）", "",
                           r["analysis"].replace("\n", "\n\n"), ""]
        table = ["## 答案速查", "", "| 题号 | " + " | ".join(str(i) for i in range(1, 11)) + " |",
                 "| --- |" + " --- |" * 10]
        for s0 in range(0, len(rows), 10):
            chunk = rows[s0:s0 + 10]
            table.append(f"| {chunk[0][0]}—{chunk[-1][0]} | " + " | ".join(a for _, a in chunk) + " |" + " |" * (10 - len(chunk)))
        md = md[:4] + table + [""] + md[4:]
        od = OUT / tag
        od.mkdir(parents=True, exist_ok=True)
        (od / "题目.jsonl").write_text("".join(json.dumps(q, ensure_ascii=False) + "\n" for q in qs), encoding="utf-8")
        (od / "答案.json").write_text(json.dumps(ans, ensure_ascii=False, indent=1), encoding="utf-8")
        (od / "来源登记.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in reg), encoding="utf-8")
        (od / "答案与解析.md").write_text("\n".join(md) + "\n", encoding="utf-8")
        print(tag, d["date"], len(qs), "题")


def typeset(font_dir, only=None):
    """逐天排版：封面写题数、建议用时；各部分接着排。"""
    import subprocess
    pl = jload(ZX / "编排.json")
    for d in pl["days"]:
        tag = f"D{d['day']}"
        if only and tag not in only:
            continue
        cmd = [sys.executable, str(S / "打印排版" / "build_print.py"), f"专项/{tag}", "--font-dir", str(font_dir),
               "--no-notice", "--flow", "--subtitle", "广东行测18套模拟·专项",
               "--title", f"图推·数推·科推专项（第{CN[d['day'] - 1]}天）", "--minutes", str(d["minutes"]),
               "--cover-tip", f"{d['date']}练。本册题目都是广东真题，共{d['n']}题，建议用时{d['minutes']}分钟。",
               "--cover-tip", "每类题前印有方法要点：先读要点再做题。做完对照《答案与解析》，按题眼、推导、易错三段复盘，错题回到方法要点再看一遍。"]
        r = subprocess.run(cmd, capture_output=True, text=True)
        print(tag, (r.stdout or r.stderr).strip().splitlines()[-1] if (r.stdout or r.stderr) else r.returncode)
        if r.returncode:
            raise SystemExit(r.stderr)


def readme():
    pl = jload(ZX / "编排.json")
    recs = records()
    alloc = jload(ZX / "分配.json")
    rows = []
    for d in pl["days"]:
        parts = defaultdict(int)
        cardt = []
        for b in d["blocks"]:
            parts[b["part"]] += len(b["ids"])
            t = b["card"] + ("（续）" if b.get("continued") else "")
            cardt.append(t)
        tag = f"D{d['day']}"
        rows.append(f"| 第{CN[d['day'] - 1]}天 {d['date']} | {d['n']}（数推{parts['数推']}、图推{parts['图推']}、科推{parts['科推']}） | {d['minutes']}分钟 | "
                    f"[题本](D{d['day']}/打印版/{tag}_题本_打印版.pdf)、[答案与解析]({tag}/答案与解析.md) | {'；'.join(cardt)} |")
    used = [i for d in pl["days"] for b in d["blocks"] for i in b["ids"]]
    src = defaultdict(int)
    for i in used:
        src["省考2017—2023年" if i.startswith("GD20") and int(i[2:6]) >= 2017 else "省考2013—2016年" if i.startswith("GD20")
            else "选调2019、2020年" if i.startswith("GDXD") else "事业编2022—2026年"] += 1
    n_blind_diff = sum(1 for i in used if recs[i].get("blind_answer") and recs[i]["blind_answer"] != recs[i]["answer"])
    lines = [
        "# 图推·数推·科推专项（2026-11-21至11-25）", "",
        "用户说图推、数推、科推比较弱，想专门练，并且“尽可能把广东比较有价值的真题安排进去”（2026-11-20），选了每天约30—40题、25日前练完。"
        "题目全部是广东真题：剩下没用过的广东题先给M12—M18、S03—S07每类留够60题（每套5题），其余全部编进专项，"
        f"共{len(used)}题（{'、'.join(f'{k}{v}题' for k, v in src.items())}）。都不在24天集训第1、2天和习题本图推里，也不与M01—M11、S01—S02重复。", "",
        "## 每天的量", "",
        "| 天 | 题数 | 建议用时 | 文件 | 规律分组（每组前印方法要点） |", "| --- | --- | --- | --- | --- |", *rows, "",
        "## 怎么用", "",
        "- 每册按数推、图推、科推三部分排，每部分按规律分组，组前方框里是这类题的方法要点：怎么认、怎么做、常见变化、易错。先读要点，再做这一组题。",
        "- 计时做完再对答案。《答案与解析》每题写来源卷别、规律细类，解析分题眼（题面上哪个特征提示用这条规律）、推导、易错三段；做错的题回到方法要点再读一遍。",
        "- 建议用时按熟练考生的估计秒数乘1.5取整；做不完不要紧，专项重在把规律认熟。", "",
        "## 答案是怎么核的", "",
        f"- 每题先由一人不看答案独立解出，写下答案后再与来源答案（答案解析PDF）对照；{len(used)}题中{len(used) - n_blind_diff}题盲解与来源答案一致，"
        f"{n_blind_diff}题盲解不一致，复核后都认来源答案，解析里写明了盲解为什么错（这几道正是容易想偏的题）。",
        f"- 来源答案可商榷（两条规律都说得通、指向不同选项）或题目本身有毛病的{len(pl.get('不用') or {})}题不放进专项，理由见 [编排.json](../重编/专项/编排.json) 的“不用”。",
        "- 原卷的错字、漏字、多余标点照来源改正，题干只印了图的补上通行设问；数列里的分数按原卷排成上下分数。逐题改动见各天的 来源登记.jsonl。", "",
        "## 文件", "",
        "- 各天目录：打印版/（题本PDF）、答案与解析.md、题目.jsonl（排版用）、答案.json、来源登记.jsonl。",
        "- 底稿：[重编/专项/](../重编/专项/)（分配.json：哪些题进专项、哪些留给模考；解题/：逐题答案和解析；方法/：方法要点卡；编排.json：每天的分组）。",
        "- 重新生成：`python3 广东行测18套模拟/重编/tools/zx_build.py plan`（排分组）→ `zx_build.py build` → `zx_build.py typeset <字体目录>`。字体文件不入库。", "",
    ]
    (OUT / "README.md").write_text("\n".join(lines), encoding="utf-8")
    print("README", len(lines))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    if cmd == "plan":
        plan()
    elif cmd == "typeset":
        typeset(Path(sys.argv[2]), set(sys.argv[3:]) or None)
    elif cmd == "readme":
        readme()
    else:
        build(set(sys.argv[2:]) or None)

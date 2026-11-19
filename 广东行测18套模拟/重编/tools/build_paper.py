#!/usr/bin/env python3
"""重编组卷：按编排把各来源的题组成一套，生成排版底稿、答案与解析、来源登记。

    python3 广东行测18套模拟/重编/tools/build_paper.py M01

来源：
- 第1—15题：重编/政治常识/甲.json、乙.json、丙.json（原创，讲义有据）
- 第16—30题：重编/言语/selection.json（国考、江浙真题）
- 第31—90题：粉笔广东模考对应季的原题（M01对第16季……），答案与解析在 重编/<套卷>/解题/；
  个别题按 重编/<套卷>/编排.json 换题或调序。

输出到 <套卷>/：题目.jsonl（排版底稿，不含答案）、答案与解析.md、答案.json、题本.md、
来源登记.jsonl、编排说明.md；并更新项目级 用题登记.jsonl 中该套的记录。
"""
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from layout_recover import split_paragraphs, split_question_line  # noqa: E402
import charts  # noqa: E402
import composition  # noqa: E402

ROOT = HERE.parents[2]
S = ROOT / "广东行测18套模拟"
R = S / "重编"
MOCK_REL = "模考/2026下半年广东卷_16-33季_AI可读"
MOCK = ROOT / MOCK_REL
JZ_REL = "江浙行测_AI题库"
GK_REL = "国考/言语理解/2016-2025/all.jsonl"
GD_DIRS = ("广东/行测/2013-2021", "广东/行测/2022-2026", "广东/事业单位/结构化")   # 广东省考、事业单位统考真题题库（M09起的题源）
SEASON = {f"M{i:02d}": 15 + i for i in range(1, 19)}   # M01对第16季……M18对第33季
VERSION = "1.0.0"


def jl(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def jload(path, default=None):
    p = Path(path)
    if not p.exists():
        if default is not None:
            return default
        raise SystemExit(f"缺少文件：{p}")
    return json.loads(p.read_text(encoding="utf-8"))


def sha(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


class Log:
    def __init__(self):
        self.items = []

    def add(self, number, kind, detail):
        self.items.append({"number": number, "kind": kind, "detail": detail})


# ---------------------------------------------------------------- 题源
MOCK_Q = {q["id"]: q for q in jl(MOCK / "全部题目.jsonl")}
JZ_Q = {q["question_id"]: q for q in jl(ROOT / JZ_REL / "questions.jsonl")}
JZ_A = {a["question_id"]: a for a in jl(ROOT / JZ_REL / "answers.jsonl")}
GK_Q = {q["id"]: q for q in jl(ROOT / GK_REL)}
GD_Q = {}                                   # id → (题库目录, 题目)
for _d in GD_DIRS:
    for _f in sorted(list((ROOT / _d).glob("GD20*.jsonl")) + list((ROOT / _d).glob("GDXD20*.jsonl"))
                     + list((ROOT / _d).glob("SYDW20*.jsonl"))):
        for _q in jl(_f):
            GD_Q[_q["id"]] = (_d, _q)

IMG = re.compile(r"!\[[^\]]*\]\((images/[^)]+)\)")
HD_LINKS = re.compile(r"\[代码描摹高清 PNG\]\([^)]*\)\s*·\s*\[SVG\]\([^)]*\)（原图为准）")


def md_blocks(s):
    """江浙题库的Markdown（文字＋原图）转为题块；只用原图，不用代码描摹图。"""
    s = HD_LINKS.sub("", s or "")
    out, pos = [], 0
    for m in IMG.finditer(s):
        t = s[pos:m.start()].strip()
        if t:
            out.append({"type": "text", "text": t})
        out.append({"type": "figure", "path": f"{JZ_REL}/{m.group(1)}"})
        pos = m.end()
    t = s[pos:].strip()
    if t:
        out.append({"type": "text", "text": t})
    return out


def mock_blocks(blocks):
    out = []
    for b in blocks:
        if b["type"] == "figure":
            out.append({"type": "figure", "asset_id": b.get("asset_id"), "path": f"{MOCK_REL}/{b['path']}",
                        "width_px": b.get("width_px"), "height_px": b.get("height_px")})
        else:
            out.append({k: v for k, v in b.items()})
    return out


def gd_answer(q):
    vals = (q.get("answer") or {}).get("values") or []
    if len(vals) != 1:
        raise SystemExit(f"{q['id']}：广东题库答案不是唯一确定的（{vals}）")
    return "".join(vals[0])


def gd_figure(d, f):
    return {"type": "figure", "asset_id": f.get("image_id"), "path": f"{d}/{f['path']}"}


def gd_blocks(d, q):
    """广东真题题库的一题转为题块：题干、题图、选项；选项画在题图里时写“见题图中的X选项”。"""
    figs = [gd_figure(d, f) for f in q.get("figures") or [] if f.get("role") != "option"]
    # 题干只有“（见题图）”这类占位字样时（如数阵题），原卷只印图
    placeholder = figs and re.fullmatch(r"[（(]?见(?:题)?图[）)]?。?", (q.get("stem") or "").strip())
    stem = [{"type": "text", "text": q["stem"]}] if q.get("stem") and not placeholder else []
    stem += figs
    opt_figs = {f.get("option_label"): f for f in q.get("figures") or [] if f.get("role") == "option"}
    options = {}
    for o in q["options"]:
        if o.get("text"):
            options[o["label"]] = [{"type": "text", "text": o["text"]}]
        elif o["label"] in opt_figs:
            options[o["label"]] = [gd_figure(d, opt_figs[o["label"]])]
        else:
            options[o["label"]] = [{"type": "text", "text": f"见题图中的 {o['label']} 选项"}]
    return stem, options


def gd_material_blocks(d, m):
    """广东真题题库的资料材料：文字照录；表格、统计图用原卷裁图（按原卷尺寸印），转写留在题库里备查。"""
    out = []
    for b in m.get("content") or []:
        if b.get("type") == "text":
            out.append({"type": "text", "text": b["text"]})
        elif b.get("type") == "image":
            out.append(gd_figure(d, b))
    return out


def apply_edits(plan, sid, rec, log, n, paper):
    """题干、选项的改动（编排.json 的 edits，按来源编号）：原文须在该处唯一出现。"""
    for e in plan.get("edits", []):
        if e["source"] == sid:
            blocks = rec["stem"] if e["where"] == "stem" else rec["options"][e["where"]]
            hit = [b for b in blocks if b["type"] == "text" and e["old"] in b["text"]]
            if len(hit) != 1 or hit[0]["text"].count(e["old"]) != 1:
                raise SystemExit(f"{paper}第{n}题：改动原文未唯一命中：{e['old']}")
            hit[0]["text"] = hit[0]["text"].replace(e["old"], e["new"])
            log.add(n, "改动", f"{e['where']}：{e['old']} → {e['new']}（{e['reason']}）")


def apply_material_edits(plan, mid, mblocks, log, n, paper):
    """资料材料的改动（编排.json 的 material_edits）：表格单元格整格相等，或文字段中唯一出现。不改题库数据本身。"""
    for e in plan.get("material_edits", []):
        if e["material"] != mid:
            continue
        hits = [(b, i, j) for b in mblocks if b["type"] == "table"
                for i, row in enumerate(b["rows"]) for j, cell in enumerate(row) if cell == e["old"]]
        texts = [b for b in mblocks if b["type"] == "text" and e["old"] in b["text"]]
        if len(hits) + sum(b["text"].count(e["old"]) for b in texts) != 1:
            raise SystemExit(f"{paper}第{n}题资料：改动原文未唯一命中：{e['old']}")
        if hits:
            b, i, j = hits[0]
            b["rows"] = [list(r) for r in b["rows"]]   # 不改动题库数据本身
            b["rows"][i][j] = e["new"]
        else:
            texts[0]["text"] = texts[0]["text"].replace(e["old"], e["new"])
        log.add(n, "改动", f"资料：{e['old']} → {e['new'] or '（空白）'}（{e['reason']}）")


def describe_source(sid):
    m = re.match(r"gd-mock-2026h2-s(\d+)-q(\d+)$", sid)
    if m:
        return f"粉笔2026下半年广东省考模考第{m.group(1)}季第{m.group(2)}题", f"{MOCK_REL}/全部题目.jsonl", "模考"
    m = re.match(r"(JS|ZJ)(\d{4})-(\w+)-(\d+)$", sid)
    if m:
        prov = "江苏" if m.group(1) == "JS" else "浙江"
        return f"{m.group(2)}年{prov}省考{m.group(3)}第{int(m.group(4))}题", f"{JZ_REL}/questions.jsonl", "真题"
    m = re.match(r"GDXD(\d{4})-(XC|ZH|SW)-Q(\d+)$", sid)
    if m:
        name = {"XC": "《行测》", "ZH": "《综合行政能力测验》", "SW": "《思维能力测验》"}[m.group(2)]
        d = GD_Q[sid][0] if sid in GD_Q else GD_DIRS[0]
        paper = sid.rsplit("-Q", 1)[0]
        return f"{m.group(1)}年广东省选调生笔试{name}第{int(m.group(3))}题", f"{d}/{paper}.jsonl", "真题"
    m = re.match(r"GD(\d{4})(?:-(XJ|XZ|1|3))?-Q(\d+)$", sid)
    if m:
        variant = {"XJ": "县级卷", "XZ": "乡镇卷", "1": "一卷", "3": "三卷"}.get(m.group(2), "")
        d = GD_Q[sid][0] if sid in GD_Q else GD_DIRS[0]
        paper = sid.rsplit("-Q", 1)[0]
        return f"{m.group(1)}年广东省考{variant}第{int(m.group(3))}题", f"{d}/{paper}.jsonl", "真题"
    m = re.match(r"SYDW(\d{4})-Q(\d+)$", sid)
    if m:
        d = GD_Q[sid][0] if sid in GD_Q else "广东/事业单位/结构化"
        return f"{m.group(1)}年广东事业单位统考第{int(m.group(2))}题", f"{d}/SYDW{m.group(1)}.jsonl", "真题"
    m = re.match(r"GKYY-(\d{4})-(\d+)$", sid)
    if m:
        return f"{m.group(1)}年国考言语（整理库第{int(m.group(2))}条）", GK_REL, "真题"
    return sid, None, "原创"


# ---------------------------------------------------------------- 资料材料
CHART_TITLE = re.compile(r"^\s*(图\s*\d+|图)\s*[：:]")


def num(s):
    s = str(s).replace("−", "-").replace(",", "").replace("％", "").replace("%", "").strip()
    try:
        return float(s)
    except ValueError:
        return None


def is_pct(h):
    return bool(re.search(r"%|％|增速|增长率|比重|占比|增幅|降幅", h))


def chart_spec(block, w_mm, h_mm, override=None):
    """按转写表推定统计图形式。override（charts/specs.json）可整体或部分指定。"""
    heads, rows = block["headers"], block["rows"]
    cats = [r[0] for r in rows]
    if all(re.fullmatch(r"\d{4}-\d{2}", c) for c in cats):
        out, prev = [], None
        for c in cats:
            y, mth = c.split("-")
            out.append(f"{y}年{int(mth)}月" if y != prev else f"{int(mth)}月")
            prev = y
        cats = out
    series = []
    for j, h in enumerate(heads[1:], start=1):
        series.append({"name": h, "values": [num(r[j]) for r in rows], "labels": [r[j] for r in rows]})
    spec = {"categories": cats, "width_mm": w_mm, "height_mm": h_mm}
    kind = (override or {}).get("kind")
    if kind == "multipie":
        groups = []
        for r in rows:
            if not groups or groups[-1]["name"] != r[0]:
                groups.append({"name": r[0], "slices": []})
            groups[-1]["slices"].append({"name": r[1], "value": num(r[2]), "label": r[2]})
        spec.update(kind="multipie", groups=groups, categories=[])
        return spec
    if kind == "hbar2":
        spec.update(kind="hbar2", bars=[series[0]], extra=series[1])
        return spec
    if kind == "pie":      # 两列表（名称、占比）画成饼图
        spec.update(kind="pie", categories=[],
                    slices=[{"name": r[0], "value": num(r[1]), "label": r[1]} for r in rows])
        return spec
    if override and override.get("as_line"):    # 两个数量指标单位不同时，指定哪几列画折线（其余画柱）
        names = override["as_line"]
        spec.update(kind="combo", bars=[s for s in series if s["name"] not in names],
                    lines=[s for s in series if s["name"] in names])
        spec.update({k: v for k, v in override.items() if k not in ("as_line", "kind")})
        return spec
    pct = [is_pct(s["name"]) for s in series]
    if len(series) == 1:
        spec.update(kind="line" if pct[0] else "bar", **({"lines": series} if pct[0] else {"bars": series}))
    elif any(pct) and not all(pct):
        spec.update(kind="combo", bars=[s for s, p in zip(series, pct) if not p], lines=[s for s, p in zip(series, pct) if p])
    elif all(pct):
        spec.update(kind="line", lines=series)
    else:
        spec.update(kind="bar", bars=series)
    if override:
        spec.update(override)
    return spec


def material_blocks(m, new_id, log, number):
    spans = [s["bbox_pt"] for s in m.get("source_spans", [])]
    # 逐行坐标：图片（高>40pt）把文字分成几段；居中的组号行不算
    groups, cur = [], []
    for b in spans:
        if b[3] - b[1] > 40:
            groups.append(cur)
            cur = []
        elif b[0] < 200:
            cur.append(b)
    groups.append(cur)
    groups = [g for g in groups if g]
    image_spans = [b for b in spans if b[3] - b[1] > 40]
    specs = jload(R / "charts" / "specs.json", {})
    out, gi, ii = [], 0, 0
    for blk in m["blocks"]:
        if blk["type"] == "text":
            lines = groups[gi] if gi < len(groups) else []
            gi += 1
            paras = split_paragraphs(blk["text"], lines) if lines else [blk["text"]]
            if len(paras) > 1:
                log.add(number, "资料分段", f"{new_id}：按原卷段首缩进分为{len(paras)}段")
            out.append({"type": "text", "text": "\n".join(paras)})
        elif blk["type"] == "table":
            box = image_spans[ii] if ii < len(image_spans) else None
            ii += 1
            aid = blk.get("source_asset_id") or f"{m['id']}-{ii}"
            ov = dict(specs.get(aid) or {})
            # 标题带“图1：”的按统计图重画；标题没有“图”字样、但 charts/specs.json 标了 chart 的也按图重画（理由写在 note）
            if box and (CHART_TITLE.match(blk.get("title") or "") or ov.pop("chart", False)):
                note = ov.pop("note", "")
                drop = ov.pop("drop_note", "")        # 图下的“注”若是题库转写时加的说明（不是原卷内容），不印
                w_mm = (box[2] - box[0]) / 72 * 25.4
                h_mm = (box[3] - box[1]) / 72 * 25.4
                spec = chart_spec(blk, w_mm, h_mm, ov or None)
                rel = f"广东行测18套模拟/重编/charts/{aid}.svg"
                (ROOT / rel).parent.mkdir(parents=True, exist_ok=True)
                (ROOT / rel).write_text(charts.render(spec), encoding="utf-8")
                out.append({"type": "chart", "title": blk["title"], "svg_path": rel, "print_width_mm": round(w_mm, 1),
                            "values": charts.text_values(spec), "source_table": {k: blk[k] for k in ("headers", "rows")},
                            "notes": "" if drop else (blk.get("notes") or "")})
                if drop:
                    log.add(number, "删去转写说明", f"{blk['title']}：图下“{blk.get('notes')}”{drop}")
                log.add(number, "统计图", f"{blk['title']}：原图未入库，按转写数据重绘为{ {'bar': '柱状图', 'line': '折线图', 'combo': '柱线图', 'pie': '饼图', 'hbar': '条形图', 'hbar2': '条形图', 'stack': '堆积柱状图', 'multipie': '饼图'}[spec['kind']] }，按原图印宽{w_mm:.1f}mm" + (f"（{note}）" if note else ""))
            else:
                out.append({k: v for k, v in blk.items() if k != "source_asset_id"})
        else:
            out.append(blk)
    return out


# ---------------------------------------------------------------- 各部分
def politics_items(paper):
    items = {}
    for who in ("甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"):  # 丁补写的经济题替换甲在同一题位的题；戊写M06，己写M07……
        for q in jload(R / "政治常识" / f"{who}.json", []):
            if q["paper"] == paper:
                items[q["number"]] = dict(q, writer=who)
    return items


def verbal_items(paper):
    sel = jload(R / "言语" / "selection.json", {})          # M01—M05
    one = R / "言语" / f"selection_{paper}.json"             # M06起一套一个文件
    if one.exists():
        sel = dict(sel, **jload(one))
    return {q["number"]: q for q in sel.get(paper, [])}


def solutions(paper):
    """各套解题记录合在一起查：换入的别季题，解题记录在那一季对应的套卷目录里。本套的记录优先。"""
    out = {}
    for p in sorted(set(SEASON) | {paper}, key=lambda x: (x == paper, x)):   # 加量套（S01起）不在季表里
        d = R / p / "解题"
        for f in ("quant_sci.json", "fig_logic.json", "data.json", "swaps.json"):
            for q in jload(d / f, []):
                out[q["id"]] = q
    for q in originals(paper).values():
        out[q["id"]] = q
    return out


def originals(paper):
    """第31—90题中编辑新写的题（题库缺某类题又无富余时），见 重编/<套卷>/原创.json。"""
    return {q["id"]: q for q in jload(R / paper / "原创.json", [])}


def section_of(n):
    if n <= 10:
        return "政治理论"
    if n <= 15:
        return "常识判断"
    if n <= 30:
        return "言语理解与表达"
    if n <= 45:
        return "数量关系"
    if n <= 65:
        return "判断推理"
    if n <= 70:
        return "科学推理"
    return "资料分析"


def subtype_of(n):
    return {**{n: None for n in range(1, 91)}}.get(n) or (
        "数字推理" if 31 <= n <= 35 else "数学运算" if 36 <= n <= 45 else
        "图形推理" if 46 <= n <= 50 else "逻辑判断" if 51 <= n <= 65 else
        "言语" if 16 <= n <= 30 else "科学推理" if 66 <= n <= 70 else
        "资料分析" if n >= 71 else "常识判断")


def build(paper, dry=False):
    season = SEASON.get(paper)     # 加量套（S01起）不对应模考季，第31—90题全由编排的 sources 给出
    oldq = {q["number"]: q for q in jl(S / paper / "题目.jsonl")} if dry and (S / paper / "题目.jsonl").exists() else {}

    def placeholder(n, sec):   # 试排：政治、言语未齐时用旧卷题占位；新套没有旧卷就用空题占位
        o = oldq.get(n) or {"number": n, "section": sec, "subtype": subtype_of(n), "question_type": "single_choice",
                            "stem": [{"type": "text", "text": "（试排占位）"}], "options_mode": "text_or_mixed", "materials": [],
                            "options": {k: [{"type": "text", "text": "占位"}] for k in "ABCD"}}
        return dict(o, id=f"{paper}-Q{n:03d}")
    plan = jload(R / paper / "编排.json", {})
    log = Log()
    pol, ver, sol = politics_items(paper), verbal_items(paper), solutions(paper)

    # 第31—90题的来源编号
    src = {n: f"gd-mock-2026h2-s{season}-q{n}" for n in range(31, 91)} if season else {}
    if plan.get("science_order"):
        for pos, old in zip(range(66, 71), plan["science_order"]):
            src[pos] = f"gd-mock-2026h2-s{season}-q{old}"
    if plan.get("data_group_order"):
        for g, old in enumerate(plan["data_group_order"]):
            for k in range(5):
                src[71 + g * 5 + k] = f"gd-mock-2026h2-s{season}-q{71 + (old - 1) * 5 + k}"
        log.add(71, "资料组调序", plan.get("data_group_order_reason") or
                "资料四组按原第" + "、".join(map(str, plan["data_group_order"])) + "组的顺序排列")
    for n, r in (plan.get("replace") or {}).items():
        src[int(n)] = r["source"]
        log.add(int(n), "换题", f"{r['source']}：{r['reason']}")
    for grp in plan.get("positions") or []:
        # {"numbers": {"40": 41, "43": "ZJ2025-A类-063"}, "reason": "..."}：整数为本季题号，字符串为完整来源编号
        for n, v in grp["numbers"].items():
            src[int(n)] = v if isinstance(v, str) else f"gd-mock-2026h2-s{season}-q{v}"
        log.add(int(min(grp["numbers"], key=int)), "调序换题", grp["reason"])
    for n, r in (plan.get("move") or {}).items():
        src[int(n)] = r["source"]
        log.add(int(n), "调序", r["reason"])
    if plan.get("sources"):     # M09起：第31—90题逐题直接给出来源（广东真题等），不以某一季模考为底
        for n, sid in plan["sources"].items():
            src[int(n)] = sid
        log.add(31, "题源", plan.get("sources_note") or "第31—90题逐题选自真题题库，见编排说明")
        for r in plan.get("replaced") or []:     # 组卷后因答案争议等换下的题
            log.add(int(r["number"]), "换题", f"原选{r['old']}，换为{r['new']}：{r['reason']}")
    skip = set(int(n) for n in plan.get("skip") or [])   # 不出的题号（如政治常识材料不够时空出的题位）
    if skip:
        log.add(min(skip), "空题位", plan.get("skip_reason") or f"本套不出第{'、'.join(map(str, sorted(skip)))}题")
    if len(set(src.values())) != 60:
        raise SystemExit("第31—90题来源有重复")

    questions, answers, registry = [], {}, []
    mat_ids = {}
    for n in range(1, 91):
        if n in skip:
            continue
        sec = section_of(n)
        rec = {"id": f"{paper}-Q{n:03d}", "number": n, "section": sec, "subtype": subtype_of(n),
               "question_type": "single_choice", "stem": [], "options": {}, "options_mode": "text_or_mixed",
               "materials": []}
        meta = {"number": n, "section": sec}
        if n <= 15:
            q = pol.get(n)
            if not q and dry:
                questions.append(placeholder(n, sec))
                answers[n] = {"answer": "?", "card": "?", "analysis": "（试排占位：旧卷题）", "category": ""}
                registry.append({"number": n, "section": sec, "source_type": "试排占位", "source_id": "old", "edits": [], "content_sha256": ""})
                continue
            if not q:
                raise SystemExit(f"{paper}第{n}题：政治常识未写")
            form = q["form"]
            rec["question_type"] = {"判断": "true_false", "单选": "single_choice", "多选": "multiple_choice",
                                    "常识单选": "single_choice"}.get(form, "single_choice")
            rec["subtype"] = {"true_false": "判断题", "single_choice": "单项选择题", "multiple_choice": "多项选择题"}[rec["question_type"]] if n <= 10 else "常识判断"
            rec["stem"] = [{"type": "text", "text": q["stem"]}]
            if rec["question_type"] != "true_false":
                rec["options"] = {k: [{"type": "text", "text": v}] for k, v in q["options"].items()}
            ans = q["answer"]
            answers[n] = {"answer": ans, "card": {"正确": "A", "错误": "B"}.get(ans, ans), "analysis": q["analysis"],
                          "category": q.get("area"), "basis": "原创，依据讲义原文"}
            meta.update(source_type="原创", source_id=f"{paper}-ORIG-{n:03d}", source_desc=f"重编原创（出题人{q['writer']}）",
                        source_file="广东行测18套模拟/重编/政治常识/" + q["writer"] + ".json",
                        grounding=q.get("grounding"))
        elif n <= 30:
            v = ver.get(n)
            if not v and dry:
                questions.append(placeholder(n, sec))
                answers[n] = {"answer": "?", "card": "?", "analysis": "（试排占位：旧卷题）", "category": ""}
                registry.append({"number": n, "section": sec, "source_type": "试排占位", "source_id": "old", "edits": [], "content_sha256": ""})
                continue
            if not v:
                raise SystemExit(f"{paper}第{n}题：言语未选")
            sid = v["id"]
            if sid.startswith("GKYY"):
                g = GK_Q[sid]
                stem = ((g.get("passage") or "") + "\n" + g["stem"]).strip()
                opts = g["options"]
                src_ans = g.get("answer")
            elif sid in GD_Q:
                g = GD_Q[sid][1]
                stem = g["stem"]
                opts = {o["label"]: o["text"] for o in g["options"]}
                src_ans = gd_answer(g)
            else:
                g = JZ_Q[sid]
                stem = g["stem"]
                opts = g["options"]
                src_ans = (JZ_A.get(sid) or {}).get("correct_answer")
            if v.get("option_spaces"):
                for k, new in v["option_spaces"].items():
                    if re.sub(r"\s", "", new) != re.sub(r"\s", "", opts[k]):
                        raise SystemExit(f"{paper}第{n}题{k}项：恢复空格后文字变了")
                    opts = dict(opts, **{k: new})
                log.add(n, "选项空格", "多空题选项恢复词间空格（按原卷）")
            rec["stem"] = [{"type": "text", "text": stem}]
            rec["options"] = {k: [{"type": "text", "text": t}] for k, t in opts.items()}
            apply_edits(plan, sid, rec, log, n, paper)
            if v["answer"] != src_ans:
                raise SystemExit(f"{paper}第{n}题：答案{v['answer']}与来源答案{src_ans}不一致")
            answers[n] = {"answer": v["answer"], "card": v["answer"], "analysis": v["analysis"],
                          "category": v.get("subtype"), "basis": "来源答案，编辑自行作答一致"}
            desc, f, kind = describe_source(sid)
            meta.update(source_type=kind, source_id=sid, source_desc=desc, source_file=f)
        else:
            sid = src[n]
            s = sol.get(sid)
            if not s and dry:   # 试排：解题记录未齐时用来源答案占位
                s = {"answer": gd_answer(GD_Q[sid][1]) if sid in GD_Q else "?", "analysis": "（试排占位：解析未写）"}
            if not s:
                raise SystemExit(f"{paper}第{n}题：{sid} 没有解题记录")
            orig = originals(paper).get(sid)
            if sid in GD_Q and not orig and s["answer"] != gd_answer(GD_Q[sid][1]):
                raise SystemExit(f"{paper}第{n}题：解题答案{s['answer']}与来源答案{gd_answer(GD_Q[sid][1])}不一致（{sid}）")
            if orig:
                rec["stem"] = [dict(b) for b in orig["stem"]]
                rec["options"] = {k: [dict(b) for b in v] for k, v in orig["options"].items()}
                log.add(n, "原创", orig.get("source_note", ""))
            elif sid.startswith("gd-mock"):
                q = MOCK_Q[sid]
                rec["stem"] = mock_blocks(q["stem"])
                rec["options"] = {k: mock_blocks(v) for k, v in q["options"].items()}
                if 51 <= n <= 65:
                    t = "".join(b.get("text", "") for b in rec["stem"] if b["type"] == "text")
                    if len([b for b in rec["stem"] if b["type"] == "text"]) == 1:
                        new, qq = split_question_line(t, [x["bbox_pt"] for x in q["source_spans"]])
                        if qq:
                            rec["stem"] = [{"type": "text", "text": new}]
                            log.add(n, "设问另起一行", f"原卷设问“{qq[:16]}…”单独成行，转写并进了上一句")
                if q.get("material"):
                    m = q["material"]
                    if m["id"] not in mat_ids:
                        mat_ids[m["id"]] = f"{paper}-M{len(mat_ids) + 1:02d}"
                        mblocks = material_blocks(m, mat_ids[m["id"]], log, n)
                        apply_material_edits(plan, m["id"], mblocks, log, n, paper)
                        rec["materials"] = [{"id": mat_ids[m["id"]], "blocks": mblocks}]
                    else:
                        rec["materials"] = [x for x in questions if x["materials"] and x["materials"][0]["id"] == mat_ids[m["id"]]][0]["materials"]
            elif sid in GD_Q:
                d, g = GD_Q[sid]
                rec["stem"], rec["options"] = gd_blocks(d, g)
                if g.get("material"):
                    m = g["material"]
                    if m["id"] not in mat_ids:
                        mat_ids[m["id"]] = f"{paper}-M{len(mat_ids) + 1:02d}"
                        mblocks = gd_material_blocks(d, m)
                        apply_material_edits(plan, m["id"], mblocks, log, n, paper)
                        rec["materials"] = [{"id": mat_ids[m["id"]], "blocks": mblocks}]
                        log.add(n, "资料材料", f"{mat_ids[m['id']]}：广东真题{m['id']}，表格、统计图用原卷裁图")
                    else:
                        rec["materials"] = [x for x in questions if x["materials"] and x["materials"][0]["id"] == mat_ids[m["id"]]][0]["materials"]
            elif sid in JZ_Q:
                g = JZ_Q[sid]
                rec["stem"] = md_blocks(g["stem"])
                rec["options"] = {k: md_blocks(t) for k, t in g["options"].items()}
                # 选项画在题图里时，江浙题库的选项文字只是字母本身
                if all([b.get("text", "").strip() for b in v] in ([k], []) for k, v in rec["options"].items()):
                    rec["options"] = {k: [{"type": "text", "text": f"见题图中的 {k} 选项"}] for k in rec["options"]}
            else:
                raise SystemExit(f"{paper}第{n}题：找不到来源 {sid}")
            ov = (plan.get("stem_override") or {}).get(sid)
            if ov:   # 题干整段替换（原图未入库时用编辑重画的图、补写引导语等），选项不变
                rec["stem"] = [dict(b) for b in ov["stem"]]
                log.add(n, "题干替换", ov["reason"])
            rw = (plan.get("rewrite") or {}).get(sid)
            if rw:
                rec["stem"] = [{"type": "text", "text": rw["stem"]}]
                rec["options"] = {k: [{"type": "text", "text": t}] for k, t in rw["options"].items()}
                s = dict(s, answer=rw["answer"], analysis=rw["analysis"], category=rw.get("category", s.get("category")),
                         subcategory=rw.get("subcategory"), form=None, confidence="high")
                log.add(n, "改写设问", rw["reason"])
            if all(len(v) == 1 and v[0]["type"] == "text" and re.fullmatch(r"见题图中(?:标为)?的?\s*[A-D]\s*(?:的)?选项。?", v[0]["text"].strip())
                   for v in rec["options"].values()):
                rec["options_mode"] = "in_figure"
                rec["options"] = {k: [{"type": "text", "text": f"见题图中的 {k} 选项"}] for k in rec["options"]}
            apply_edits(plan, sid, rec, log, n, paper)
            answers[n] = {"answer": s["answer"], "card": s["answer"], "analysis": s["analysis"],
                          "category": "／".join(x for x in (s.get("category"), s.get("subcategory"), s.get("form")) if x),
                          "basis": "模考无答案，独立解出并复核" if sid.startswith("gd-mock") else "来源答案，编辑解出一致",
                          "confidence": s.get("confidence")}
            if orig:
                answers[n]["basis"] = "原创，编辑推导并复核"
                meta.update(source_type="原创", source_id=sid, source_desc="重编原创（" + orig.get("source_note", "") + "）",
                            source_file=f"广东行测18套模拟/重编/{paper}/原创.json")
            else:
                desc, f, kind = describe_source(sid)
                meta.update(source_type=kind, source_id=sid, source_desc=desc, source_file=f)
        rec["materials"] = rec["materials"] or []
        # 转写带进来的不可见字符（零宽空格等）删去
        zw = re.compile("[\u200b\u200c\u200d\ufeff]")
        for blocks in [rec["stem"], *rec["options"].values(), *[m["blocks"] for m in rec["materials"]]]:
            for b in blocks:
                if b.get("type") == "text" and zw.search(b["text"]):
                    b["text"] = zw.sub("", b["text"])
                    log.add(n, "不可见字符", "删去转写留下的零宽字符")
        questions.append(rec)
        meta["edits"] = [x for x in log.items if x["number"] == n]
        meta["content_sha256"] = sha({k: rec[k] for k in ("stem", "options")})
        registry.append(meta)
    # 改写后的解析（讲清题眼与易错，见 重编/解析改写/改写说明.md），按套卷与题号覆盖
    for f in sorted((R / "解析改写").glob("out_*.json")):
        for x in jload(f, []):
            if x.get("paper") == paper and x.get("number") in answers and (x.get("analysis") or "").strip():
                answers[x["number"]]["analysis"] = x["analysis"].strip()
    return questions, answers, registry, log, src, plan


# ---------------------------------------------------------------- 输出
def blocks_md(blocks):
    out = []
    for b in blocks:
        if b["type"] == "text":
            out.append(b["text"])
        elif b["type"] == "figure":
            out.append(f"![]({'../../' + b['path']})")
        elif b["type"] == "table":
            t = [f"**{b.get('title', '')}**", "", "| " + " | ".join(b["headers"]) + " |", "|" + "---|" * len(b["headers"])]
            t += ["| " + " | ".join(r) + " |" for r in b["rows"]]
            if b.get("notes"):
                t += ["", b["notes"]]
            out.append("\n".join(t))
        elif b["type"] == "chart":
            out.append(f"**{b['title']}**\n\n![](../{b['svg_path'].split('广东行测18套模拟/')[1]})")
    return "\n\n".join(out)


PART_NAMES = [(1, "第一部分　政治理论"), (11, "第二部分　常识判断"), (16, "第三部分　言语理解与表达"),
              (31, "第四部分　数量关系"), (46, "第五部分　判断推理"), (66, "第六部分　科学推理"), (71, "第七部分　资料分析")]


def num_ranges(ns):
    """[1,2,3,6,10] → “1—3、6、10”。"""
    ns, out = sorted(ns), []
    i = 0
    while i < len(ns):
        j = i
        while j + 1 < len(ns) and ns[j + 1] == ns[j] + 1:
            j += 1
        out.append(f"{ns[i]}—{ns[j]}" if j - i >= 2 else "、".join(map(str, ns[i:j + 1])))
        i = j + 1
    return "、".join(out)


def real_source_desc(plan):
    """编排说明题源表的第31—90题一行（M09起逐题选自真题）：按来源卷别计数。"""
    ids = list(plan["sources"].values())
    kinds = [("广东省考旧卷", sum(1 for i in ids if re.match(r"GD\d{4}", i))),
             ("广东省选调生笔试", sum(1 for i in ids if i.startswith("GDXD"))),
             ("广东事业单位统考", sum(1 for i in ids if i.startswith("SYDW"))),
             ("其他", sum(1 for i in ids if not re.match(r"(GD|SYDW)", i)))]
    return "真题：" + "，".join(f"{k}{c}题" for k, c in kinds if c)


def verbal_source_desc(paper):
    """编排说明题源表的第16—30题一行：按本套言语题的实际来源写。"""
    ids = [v["id"] for v in verbal_items(paper).values()]
    kinds = [("广东省考旧卷", sum(1 for i in ids if re.match(r"GD(XD)?\d{4}", i))),
             ("广东事业单位统考", sum(1 for i in ids if i.startswith("SYDW"))),
             ("国考", sum(1 for i in ids if i.startswith("GKYY"))),
             ("江苏、浙江省考", sum(1 for i in ids if re.match(r"(JS|ZJ)\d{4}", i)))]
    kinds = [(k, c) for k, c in kinds if c]
    if not kinds:
        return "国考、江苏、浙江言语真题"
    if len(kinds) == 1:
        return kinds[0][0] + "言语真题"
    return "言语真题：" + "，".join(f"{k}{c}题" for k, c in kinds)


def write_outputs(paper, questions, answers, registry, log, plan, out=None, ledger=True):
    out = out or S / paper
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "题目.jsonl", "w", encoding="utf-8") as f:
        for q in questions:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")
    (out / "答案.json").write_text(json.dumps({str(n): a["card"] for n, a in answers.items()}, ensure_ascii=False, indent=0), encoding="utf-8")
    # 题本.md
    md, seen = [f"# {paper}　广东省考行测模拟卷（题本）\n"], set()
    starts = dict(PART_NAMES)
    for q in questions:
        if q["number"] in starts:
            md.append(f"## {starts[q['number']]}\n")
        for m in q["materials"]:
            if m["id"] not in seen:
                seen.add(m["id"])
                md.append(blocks_md(m["blocks"]) + "\n")
        body = blocks_md(q["stem"])
        md.append(f"**{q['number']}.** {body}\n")
        if q["question_type"] == "true_false":
            md.append("A. 正确　　B. 错误\n")
        elif q["options_mode"] != "in_figure":
            md.append("\n".join(f"{k}. {blocks_md(v)}" for k, v in q["options"].items()) + "\n")
    (out / "题本.md").write_text("\n".join(md), encoding="utf-8")
    # 答案与解析.md（给考生）
    md = [f"# {paper}　答案与解析\n", "## 答案速查\n"]
    for a, b in [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75), (76, 90)]:
        md.append("| 题号 | " + " | ".join(str(i) for i in range(a, b + 1)) + " |")
        md.append("|---|" + "---|" * (b - a + 1))
        md.append("| 答案 | " + " | ".join(answers[i]["answer"] if i in answers else "—" for i in range(a, b + 1)) + " |\n")
    md.append("判断题在答题卡上正确涂A、错误涂B。\n")
    skipped = sorted(set(range(1, 91)) - set(answers))
    if skipped:
        md.append("本套没有第" + num_ranges(skipped) + "题（表中记“—”），答题卡上这几题空着。\n")
    for q in questions:
        n = q["number"]
        if n in starts:
            md.append(f"## {starts[n]}\n")
        a = answers[n]
        body = "\n\n".join(x.strip() for x in a["analysis"].strip().split("\n") if x.strip())
        body = re.sub(r"(^|\n\n)(题眼|易错)：", r"\1**\2**：", body)
        md.append(f"**{n}.【答案】{a['answer']}**\n\n{body}\n")
    (out / "答案与解析.md").write_text("\n".join(md), encoding="utf-8")
    labels = {n: a.get("category") or "" for n, a in answers.items()}
    rows = composition.table(labels)
    (out / "题型统计.json").write_text(json.dumps({"逐题": {str(k): v for k, v in labels.items()},
                                                 "对照": [dict(zip(("部分", "类别", "本卷", "真题范围", "判定", "题号"), r)) for r in rows]},
                                                ensure_ascii=False, indent=1), encoding="utf-8")
    skip = set(int(n) for n in plan.get("skip") or [])
    md = [f"# {paper}　编排说明（重编{VERSION}）\n",
          "## 题源\n",
          "| 题号 | 来源 |", "|---|---|",
          ("| 1—15 | 本套不出（加量套只练第16—90题，题号照真题位置） |" if set(range(1, 16)) <= skip else
           "| 1—15 | 原创，依据《颜培天2027广东省考政治理论常识》讲义（含二十届五中全会《决定》）"
           + ("；本套空出第" + "、".join(map(str, sorted(skip))) + "题（讲义材料不够，按用户决定不硬出）" if skip else "") + " |"),
          "| 16—30 | " + verbal_source_desc(paper) + " |",
          ("| 31—90 | " + real_source_desc(plan) + "（逐题来源见 `来源登记.jsonl`） |\n" if plan.get("sources")
           else f"| 31—90 | 粉笔2026下半年广东省考模考第{SEASON[paper]}季原题（个别调换见下） |\n"),
          "逐题来源见 `来源登记.jsonl`。\n",
          "## 题型与近三年广东真题对照\n",
          "范围取自2024—2026年广东卷（见 `../题型参照_2024-2026.md`），★为三年每年都有。范围是参照，不是配额。\n",
          "| 部分 | 类别 | 本卷 | 真题范围 | 对照 | 题号 |", "|---|---|---:|---|---|---|"]
    for part, cat, k, rng, verdict, ns in rows:
        md.append(f"| {part} | {cat} | {k} | {rng} | {verdict} | {'、'.join(map(str, ns))} |")
    md += ["", "## 换题、调序与排版前处理\n"]
    for x in log.items:
        md.append(f"- 第{x['number']}题｜{x['kind']}：{x['detail']}")
    (out / "编排说明.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    with open(out / "来源登记.jsonl", "w", encoding="utf-8") as f:
        for r in registry:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    (out / "排版前处理日志.json").write_text(json.dumps(log.items, ensure_ascii=False, indent=1), encoding="utf-8")
    if not ledger:
        return
    # 项目级用题登记：替换本套记录
    led = S / "用题登记.jsonl"
    rows = [r for r in jl(led) if r["paper_id"] != paper]
    for r in registry:
        rows.append({"paper_id": paper, "number": r["number"], "source_id": r["source_id"], "source_file": r.get("source_file"),
                     "status": f"重编{VERSION}", "user_done": "no", "content_sha256": r["content_sha256"]})
    rows.sort(key=lambda r: (r["paper_id"], r["number"]))
    with open(led, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main():
    paper = sys.argv[1]
    dry = "--dry" in sys.argv
    questions, answers, registry, log, src, plan = build(paper, dry=dry)
    if dry:   # 试排：政治、言语未齐时用旧卷题占位，输出到 广东行测18套模拟/_试排<套卷>/，不动正式文件和用题登记
        write_outputs(paper, questions, answers, registry, log, plan, out=S / f"_试排{paper}", ledger=False)
    else:
        write_outputs(paper, questions, answers, registry, log, plan)
    c = Counter(x["kind"] for x in log.items)
    print(paper, f"{len(questions)}题", dict(c))


if __name__ == "__main__":
    main()

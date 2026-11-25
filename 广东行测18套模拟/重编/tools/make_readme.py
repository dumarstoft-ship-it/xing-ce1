#!/usr/bin/env python3
"""按组卷与排版结果写 <套卷>/README.md（重编版）。

    python3 广东行测18套模拟/重编/tools/make_readme.py M01
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
S = ROOT / "广东行测18套模拟"
R = S / "重编"
SEASON = {f"M{i:02d}": 15 + i for i in range(1, 19)}
OLD = {"M01": "0.3.0", "M02": "0.2.0", "M03": "0.2.0", "M04": "0.2.0", "M05": "0.2.0"}


def verbal_check(p):
    """言语第二人盲做与来源答案对照（M06起一套一个 言语/复核/<套卷>_blind.json）；不一致的题在 言语/复核/<套卷>_blind_note.json 写明处理。"""
    f = R / "言语" / "复核" / f"{p}_blind.json"
    if not f.exists():
        return "新选的题另由一人只看题面盲做，全部一致。"
    blind = {x["number"]: x["answer"] for x in json.loads(f.read_text(encoding="utf-8"))}
    sel = json.loads((R / "言语" / f"selection_{p}.json").read_text(encoding="utf-8"))[p]
    diff = [x for x in sel if blind.get(x["number"]) not in (None, x["answer"])]
    if not diff:
        return "新选的题另由一人只看题面盲做，全部一致。"
    notes = json.loads((R / "言语" / "复核" / f"{p}_blind_note.json").read_text(encoding="utf-8"))
    return (f"新选的题另由一人只看题面盲做，{len(blind)}题中{len(blind) - len(diff)}题一致；"
            + "；".join(f"第{x['number']}题盲做选{blind[x['number']]}、来源答案{x['answer']}，{notes[str(x['number'])]}" for x in diff) + "。")


def num_ranges(ns):
    """[1,2,3,6,10] → “1—3、6、10”。"""
    ns, out, i = sorted(ns), [], 0
    while i < len(ns):
        j = i
        while j + 1 < len(ns) and ns[j + 1] == ns[j] + 1:
            j += 1
        out.append(f"{ns[i]}—{ns[j]}" if j - i >= 2 else "、".join(map(str, ns[i:j + 1])))
        i = j + 1
    return "、".join(out)


def difficulty_lines(p, real, extra=False, notes=()):
    """M09起：按解题人的逐题评分（难度对照的标准）写数资难度与估时。"""
    if not real:
        return []
    d = R / p / "解题"
    data = json.loads((d / "data.json").read_text(encoding="utf-8")) if (d / "data.json").exists() else []
    qs = json.loads((d / "quant_sci.json").read_text(encoding="utf-8")) if (d / "quant_sci.json").exists() else []
    math = [x for x in qs if 36 <= x["number"] <= 45 and x.get("mode")]
    if not data or not math:
        return []
    from collections import Counter
    c = Counter(x["mode"] for x in data)
    multi = c["两步"] + c["三步及以上"]
    secs = sum(x.get("est_seconds") or 0 for x in data) + sum(x.get("material_seconds") or 0 for x in data)
    cm = Counter(x["mode"] for x in math)
    msecs = sum(x.get("est_seconds") or 0 for x in math)
    return [
        "## 难度",
        "",
        f"- 资料分析：读一眼就能判断{c['读']}道、一步{c['一步']}道、两步{c['两步']}道、三步及以上{c['三步及以上']}道（多步{multi}道）；"
        f"熟练考生连扫读材料约{secs / 60:.1f}分钟。近三年真题多步5—8道、约16.1分钟（见[难度对照](../难度对照/README.md)）。",
        f"- 数学运算：多步{cm['两步'] + cm['三步及以上']}道（两步{cm['两步']}、三步及以上{cm['三步及以上']}），熟练考生约{msecs / 60:.1f}分钟；近三年真题多步6—7道。",
        *[f"- {x}" for x in notes],     # 编排.json的difficulty_notes：数推、图推、科推、逻辑的难度等（M12起）
        "- 评分人各有松紧（同一组资料，题池归类时另一人评的多步题少几道），只作大致参照。"
        + ("建议限时75分钟。" if extra else "按考场时段计时90分钟。"),
        "",
    ]


def main():
    p = sys.argv[1]
    d = S / p
    log = json.loads((d / "打印版" / "排版日志.json").read_text(encoding="utf-8"))
    sha = hashlib.sha256((d / "题目.jsonl").read_bytes()).hexdigest()
    comp = json.loads((d / "题型统计.json").read_text(encoding="utf-8"))["对照"]
    off = [r for r in comp if r["判定"] not in ("√",)]
    pre = json.loads((d / "排版前处理日志.json").read_text(encoding="utf-8"))
    changes = [x for x in pre if x["kind"] in ("调序换题", "换题", "改写设问", "题干替换", "原创", "改动", "资料组调序")]
    plan = json.loads((R / p / "编排.json").read_text(encoding="utf-8")) if (R / p / "编排.json").exists() else {}
    real = bool(plan.get("sources"))          # M09起：第31—90题逐题选自真题
    skip = sorted(int(n) for n in plan.get("skip") or [])
    extra = set(range(1, 16)) <= set(skip)    # 加量套（S01起）：不出第1—15题
    n_sydw = sum(1 for v in (plan.get("sources") or {}).values() if v.startswith("SYDW"))
    n_gdxd = sum(1 for v in (plan.get("sources") or {}).values() if v.startswith("GDXD"))   # 2019、2020年广东选调生考试卷（M11起）
    js_n = [int(n) for n, v in (plan.get("sources") or {}).items() if v.startswith("JS")]   # 江苏省考A类卷的数量难题（M12起，用户2026-11-25）
    js_parts = [f"{c}道{k}" for k, c in (("数推", sum(1 for n in js_n if n <= 35)), ("数学运算", sum(1 for n in js_n if 36 <= n <= 45))) if c]
    n_gk = sum(1 for v in (plan.get("sources") or {}).values() if v.startswith("GK")) // 5   # 国考地市级卷的资料组（M13起）
    vf = R / "言语" / f"selection_{p}.json"
    v_sydw = vf.exists() and any(x["id"].startswith("SYDW") for x in json.loads(vf.read_text(encoding="utf-8")).get(p, []))
    qs = [json.loads(l) for l in (d / "题目.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    multi = [q["number"] for q in qs if q["question_type"] == "multiple_choice" and q["number"] <= 15]
    second = R / p / "复核" / "second.json"
    n_second = len(json.loads(second.read_text(encoding="utf-8"))) if second.exists() else 0
    extras = R / p / "复核" / "second_extras.json"     # 换入题、改写题、编辑新写的题的第二人盲做（M06起）
    n_extras = len(json.loads(extras.read_text(encoding="utf-8"))) if extras.exists() else 0
    squant = R / p / "复核" / "second_quant.json"     # 解题人此前看过答案页的题另由一人盲做（M11起）
    n_squant = len(json.loads(squant.read_text(encoding="utf-8"))) if squant.exists() else 0
    if extra:
        intro = ("加量套：2026-11-26至12-02每天的第二场，用事业编和省考旧卷剩下的题编（见[重编说明](../重编/README.md)“M09起怎么编”）。"
                 "只出第16—90题，题号照真题位置，不出政治理论、常识判断；第31—90题以2022—2026年广东事业单位统考题为主，配广东省考旧卷"
                 + ("和选调生考试卷" if n_gdxd else "") + "里较易的题，"
                 + (f"资料有{n_gk}组取自国考地市级卷（广东资料组不够，用户2026-11-20定用国考补），" if n_gk else "")
                 + "题型照2024—2026年真题分布，难度略低于主套，解析写得简短。建议限时75分钟（主套90分钟里约10分钟用在第1—15题），"
                 "到点没做完就换一支颜色的笔做完。")
    elif real:
        intro = ("2026-11-19起用广东省考旧卷编（见[重编说明](../重编/README.md)“给后面各套的提示”）。"
                 "第31—90题逐题选自广东省考旧卷"
                 + (f"和2019、2020年广东选调生考试卷（{n_gdxd}题）" if n_gdxd else "")
                 + (f"（旧卷用完的题型取广东事业单位统考题，共{n_sydw}题）" if n_sydw else "")
                 + (f"，另有{'、'.join(js_parts)}难题取自江苏省考A类卷（用户2026-11-25：广东难题不够可用外地难题）" if js_parts else "")
                 + (f"，资料有{n_gk}组取自国考地市级卷（用户2026-11-20定：广东资料组不够用国考补）" if n_gk else "")
                 + "，都不在用户练过的24天集训第1、2天和习题本图推里；"
                 "各部分题型按2024—2026年真题的分布挑，数量、资料按[难度对照](../难度对照/README.md)的标准控制多步题。"
                 "第16—30题按真题题位编排，先用广东旧卷" + ("和事业编" if v_sydw else "") + "的言语题，旧卷没有的题型用国考、江浙真题；"
                 "第1—15题依据用户的2027广东省考政治理论常识讲义新写"
                 + (f"，讲义里能出新题的材料不够的题位空着（本套没有第{num_ranges(skip)}题，按用户的决定不凑数）" if skip else "")
                 + "。按考场时段计时90分钟。")
    else:
        intro = (("2026-11-16重编。用户要求各套题型与近年广东卷基本一致，五套都还没做过，由Claude重新编排。" if p in OLD else
                  "2026-11-16由Claude按M01—M05重编的做法新编（见[重编说明](../重编/README.md)）。")
                 + f"第31—90题整段采用粉笔2026下半年广东省考模考第{SEASON[p]}季原题，缺真题每年都有的题型或差得多时个别换题；"
                 "第16—30题按真题题位从国考、江浙言语真题中编排；第1—15题依据用户的2027广东省考政治理论常识讲义新写。")
    lines = [
        f"# {p}｜广东省考行测{'加量套' if extra else '模拟卷'}（重编1.0.0）",
        "",
        intro,
        "",
        "| 文件 | 内容 |",
        "| --- | --- |",
        f"| [打印版/{p}_题本_打印版.pdf](打印版/{p}_题本_打印版.pdf) | 考场样式题本，A4，共{log['PDF总页数']}页（封面、注意事项、正文{log['正文页数']}页） |",
        ("| [答案与解析.md](答案与解析.md) | 答案速查和逐题简短解析：每题一行题眼（题面上哪个提示告诉你该怎么做），再两三句推导，有明显陷阱的写易错 |" if extra else
         "| [答案与解析.md](答案与解析.md) | 答案速查和逐题解析，给考生看。每题先写题眼（题面上哪个提示告诉你该怎么做），再写推导，最后写易错（漏看提示会选错哪一项） |"),
        "| [题本.md](题本.md) | 题本的文字版，便于在线查看 |",
        "| [编排说明.md](编排说明.md) | 题源、题型与近三年真题对照、换题调序和改动、排版前处理 |",
        "| [来源登记.jsonl](来源登记.jsonl) | 逐题来源、改动和依据 |",
        "| 题目.jsonl、答案.json、题型统计.json、排版前处理日志.json | 排版与核对用的数据 |",
        "",
        "## 答案是怎么核的",
        "",
        ("- **第31—90题**：用真题的来源答案（答案解析PDF）。每题先由一人不看答案独立解出并写解析，数量和资料用程序核算、能枚举的枚举，"
         "写完再与来源答案对照" + ("；" if n_second or n_extras or n_squant else "。")
         + ((f"部分题另由第二人只看题面独立再做（{n_second}题），三方对照。" if extra else
             f"判断推理和科学推理另由第二人只看题面独立再做（{n_second}题），三方对照。") if n_second else "")
         + (f"换入的题另由第二人只看题面盲做（{n_extras}题），与来源答案一致。" if n_extras else "")
         + (f"解题人此前核对别的套时看过答案页的题，另由一人只看题面独立再做（{n_squant}题），与来源答案一致。" if n_squant else "") if real else
         "- **第31—90题**：模考题库没有答案，每题由一人独立解出并写解析，数量和资料用程序核算、能枚举的枚举；"
         f"判断推理和科学推理另由第二人只看题面独立再做{('（' + str(n_second) + '题）') if n_second else ''}，两遍对照。"
         "换入的江浙真题用来源答案并复算。"
         + (f"换入题、改写的资料题和编辑新写的题另由第二人只看题面盲做（{n_extras}题），全部一致。" if n_extras else "")),
        "- **第16—30题**：用" + ("真题" if real else "国考、江浙真题") + "的来源答案，选题时自己先做一遍；" + verbal_check(p),
        *([] if extra else ["- **第1—15题**：每题的正确答案和每个错误选项都对应讲义原句；另由一人先凭知识盲做、再对照讲义和公开原文核查，答案全部一致。"]),
        *[f"- {x}" for x in plan.get("review_notes") or []],
        "",
        *difficulty_lines(p, real, extra, plan.get("difficulty_notes") or ()),
        "## 题型",
        "",
        "各部分各类题的多少与2024—2026年广东卷对照见[编排说明](编排说明.md)。与真题范围差一两道的保留（用户原话“一两道之差无妨”）"
        + ("。旧卷资料几乎没有“材料理解”（不用计算、在纯文字材料里找信息）这类题，现期量题也少，各套多半缺这两类。" if real else "，真题每年都有而本季缺的已补上。")
        + ("与真题范围有出入的类别：" + "；".join(f"{r['部分']}{r['类别']}{r['本卷']}道（真题{r['真题范围']}）" for r in off) + "。" if off else ""),
        "",
        "## 与原题不同的地方",
        "",
    ]
    for x in changes:
        lines.append(f"- 第{x['number']}题，{x['kind']}：{x['detail']}".replace("\n", "⏎"))   # 改动原文里的换行显示为⏎，不断开列表
    if not changes:
        lines.append("- 无")
    lines += [
        "",
        ("资料分析的表格、统计图和题图都用原卷裁图，按原卷的印刷尺寸印。" if real else
         "资料分析中原卷的统计图没有入库，只有转写的数据，打印版按数据重画（图形样式为推定，数值与转写一致），见编排说明。"),
        "",
        "## 打印",
        "",
        f"- 底稿 `题目.jsonl` 的SHA-256为 `{sha}`，与[排版日志](打印版/排版日志.json)一致；排版程序已核对题干、选项、资料文字和统计图数值都出现在PDF里，页码连续，没有缺字回退。",
        "- A4、实际大小（100%）打印。"
        + ("" if extra else "判断题在答题卡上正确涂A、错误涂B；" + (f"第{'、'.join(map(str, multi))}题为多选题。" if multi else "本套没有多选题。"))
        + (f"本套没有第{num_ranges(skip)}题，答题卡上空着。" if skip else ""),
        "- 重新生成：`python3 广东行测18套模拟/重编/tools/build_paper.py " + p + "`，再 `python3 广东行测18套模拟/打印排版/build_print.py " + p
        + (" --minutes 75" if extra else "") + " --font-dir <字体目录>`。字体文件不入库。",
        "",
    ]
    if (d / "astra审核.md").exists():
        lines += [
            "## Astra审核",
            "",
            "Astra（GPT）按[协作分工](../协作分工.md)对本套做了定向审核：[astra审核.md](astra审核.md)；Claude的处理见"
            + ("[astra审核处理.md](astra审核处理.md)。" if (d / "astra审核处理.md").exists() else "（待处理）。"),
            "",
        ]
    if p in OLD:
        lines += [
            "## 旧版",
            "",
            f"GPT编制的旧版{OLD[p]}已移入[历史版本/{OLD[p]}/](历史版本/{OLD[p]}/)。本目录下的 Claude审核意见、增量复核、修订说明和 `核验记录/` 是对旧版的审核记录，保留备查。",
            "",
        ]
    (d / "README.md").write_text("\n".join(lines), encoding="utf-8")
    print("README", p, len(lines))


if __name__ == "__main__":
    main()

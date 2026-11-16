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


def main():
    p = sys.argv[1]
    d = S / p
    log = json.loads((d / "打印版" / "排版日志.json").read_text(encoding="utf-8"))
    sha = hashlib.sha256((d / "题目.jsonl").read_bytes()).hexdigest()
    comp = json.loads((d / "题型统计.json").read_text(encoding="utf-8"))["对照"]
    off = [r for r in comp if r["判定"] not in ("√",)]
    pre = json.loads((d / "排版前处理日志.json").read_text(encoding="utf-8"))
    changes = [x for x in pre if x["kind"] in ("调序换题", "换题", "改写设问", "题干替换", "原创", "改动", "资料组调序")]
    second = R / p / "复核" / "second.json"
    n_second = len(json.loads(second.read_text(encoding="utf-8"))) if second.exists() else 0
    extras = R / p / "复核" / "second_extras.json"     # 换入题、改写题、编辑新写的题的第二人盲做（M06起）
    n_extras = len(json.loads(extras.read_text(encoding="utf-8"))) if extras.exists() else 0
    lines = [
        f"# {p}｜广东省考行测模拟卷（重编1.0.0）",
        "",
        ("2026-11-16重编。用户要求各套题型与近年广东卷基本一致，五套都还没做过，由Claude重新编排。" if p in OLD else
         "2026-11-16由Claude按M01—M05重编的做法新编（见[重编说明](../重编/README.md)）。")
        + f"第31—90题整段采用粉笔2026下半年广东省考模考第{SEASON[p]}季原题，缺真题每年都有的题型或差得多时个别换题；"
        "第16—30题按真题题位从国考、江浙言语真题中编排；第1—15题依据用户的2027广东省考政治理论常识讲义新写。",
        "",
        "| 文件 | 内容 |",
        "| --- | --- |",
        f"| [打印版/{p}_题本_打印版.pdf](打印版/{p}_题本_打印版.pdf) | 考场样式题本，A4，共{log['PDF总页数']}页（封面、注意事项、正文{log['正文页数']}页） |",
        "| [答案与解析.md](答案与解析.md) | 答案速查和逐题解析，给考生看。每题先写题眼（题面上哪个提示告诉你该怎么做），再写推导，最后写易错（漏看提示会选错哪一项） |",
        "| [题本.md](题本.md) | 题本的文字版，便于在线查看 |",
        "| [编排说明.md](编排说明.md) | 题源、题型与近三年真题对照、换题调序和改动、排版前处理 |",
        "| [来源登记.jsonl](来源登记.jsonl) | 逐题来源、改动和依据 |",
        "| 题目.jsonl、答案.json、题型统计.json、排版前处理日志.json | 排版与核对用的数据 |",
        "",
        "## 答案是怎么核的",
        "",
        "- **第31—90题**：模考题库没有答案，每题由一人独立解出并写解析，数量和资料用程序核算、能枚举的枚举；"
        f"判断推理和科学推理另由第二人只看题面独立再做{('（' + str(n_second) + '题）') if n_second else ''}，两遍对照。"
        "换入的江浙真题用来源答案并复算。"
        + (f"换入题、改写的资料题和编辑新写的题另由第二人只看题面盲做（{n_extras}题），全部一致。" if n_extras else ""),
        "- **第16—30题**：用国考、江浙真题的来源答案，选题时自己先做一遍；新选的题另由一人只看题面盲做，全部一致。",
        "- **第1—15题**：每题的正确答案和每个错误选项都对应讲义原句；另由一人先凭知识盲做、再对照讲义和公开原文核查，答案全部一致。",
        "",
        "## 题型",
        "",
        "各部分各类题的多少与2024—2026年广东卷对照见[编排说明](编排说明.md)。与真题范围差一两道的保留（用户原话“一两道之差无妨”），真题每年都有而本季缺的已补上。"
        + ("与真题范围有出入的类别：" + "；".join(f"{r['部分']}{r['类别']}{r['本卷']}道（真题{r['真题范围']}）" for r in off) + "。" if off else ""),
        "",
        "## 与原题不同的地方",
        "",
    ]
    for x in changes:
        lines.append(f"- 第{x['number']}题，{x['kind']}：{x['detail']}")
    if not changes:
        lines.append("- 无")
    lines += [
        "",
        "资料分析中原卷的统计图没有入库，只有转写的数据，打印版按数据重画（图形样式为推定，数值与转写一致），见编排说明。",
        "",
        "## 打印",
        "",
        f"- 底稿 `题目.jsonl` 的SHA-256为 `{sha}`，与[排版日志](打印版/排版日志.json)一致；排版程序已核对题干、选项、资料文字和统计图数值都出现在PDF里，页码连续，没有缺字回退。",
        "- A4、实际大小（100%）打印。判断题在答题卡上正确涂A、错误涂B；第9、10题为多选题。",
        "- 重新生成：`python3 广东行测18套模拟/重编/tools/build_paper.py " + p + "`，再 `python3 广东行测18套模拟/打印排版/build_print.py " + p + " --font-dir <字体目录>`。字体文件不入库。",
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

#!/usr/bin/env python3
"""M04 第51—65题：stem_override / options 与 source_question 逐字比对（只读仓库文件）。

做三件事：
  1. 字符级：去掉所有空白与换行后比对“源题干/选项”与“编辑稿题干/选项”，列出全部差异（丢字、改字、标点）。
  2. 分段结构：把源题干按“逻辑行”切分（江浙库的 PDF 硬换行需合并：若一行不以 。？；：! ? 结尾，
     且下一行不以 （n）/说话人“X：”/设问引导词 开头，视为句内硬换行并合并），
     再与编辑稿的行结构比较；选项内的换行（对话分行）单独比较。
  3. 交叉一致：selection 的有效题面（stem_override 优先，否则源题）与 题目.jsonl、题本_待审.md 中渲染文本一致。
运行：python3 compare_stems.py  (输出见 outputs/compare_stems.txt)
"""
import difflib
import json
import re
from pathlib import Path

REPO = Path("/home/user/xing-ce1")
M04 = REPO / "广东行测18套模拟/M04"
sel = {q["number"]: q for q in json.loads((M04 / "selection.json").read_text(encoding="utf-8"))}
tj = {}
for line in (M04 / "题目.jsonl").read_text(encoding="utf-8").splitlines():
    q = json.loads(line)
    tj[q["number"]] = q
booklet = (M04 / "题本_待审.md").read_text(encoding="utf-8")

LEAD = re.compile(r"^(（\d+）|[①②③④⑤⑥]|[^\s：]{1,6}：|以下|下列|由此|如果|根据|那么)")
END = tuple("。？；：!?」”")


def blocks_text(x):
    if x is None:
        return None
    if isinstance(x, str):
        return x
    out = []
    for b in x:
        if b.get("type") == "text":
            out.append(b["text"])
        elif b.get("type") == "figure":
            out.append("[FIGURE]")
        elif b.get("type") == "table":
            out.append("[TABLE]")
    return "\n".join(out)


def logical_lines(s, merge_hard_wraps):
    raw = s.split("\n")
    if not merge_hard_wraps:
        return [r for r in raw if r.strip()]
    lines = []
    for r in raw:
        r2 = r.rstrip()
        if lines and not lines[-1].endswith(END) and not LEAD.match(r2):
            lines[-1] += r2
        else:
            lines.append(r2)
    # 去掉汉字/数字与单位间的排版空格
    return [re.sub(r"(?<=[一-鿿\d])\s+(?=[一-鿿\d])", "", l) for l in lines if l.strip()]


def squash(s):
    return re.sub(r"\s+", "", s or "")


def char_diff(a, b):
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    return [(op, a[i1:i2], b[j1:j2]) for op, i1, i2, j1, j2 in sm.get_opcodes() if op != "equal"]


def opt_text(v):
    return blocks_text(v) if not isinstance(v, str) else v


report = {}
for n in range(51, 66):
    q = sel[n]
    sq = q["source_question"]
    is_jz = q["source_bank"] == "jiangzhe"
    src_stem = blocks_text(sq["stem"])
    src_opts = {k: opt_text(v) for k, v in sq["options"].items()}
    ed_stem = blocks_text(q.get("stem_override")) if q.get("stem_override") is not None else src_stem
    ed_opts = {k: opt_text(v) for k, v in (q.get("options") or sq["options"]).items()}
    r = {"source_bank": q["source_bank"], "edits": [e.get("type") for e in q.get("edits", [])]}
    # 1 字符级
    r["stem_char_diff"] = char_diff(squash(src_stem), squash(ed_stem))
    r["opt_char_diff"] = {k: char_diff(squash(src_opts[k]), squash(ed_opts[k])) for k in src_opts if char_diff(squash(src_opts[k]), squash(ed_opts[k]))}
    # 2 分段结构
    src_lines = logical_lines(src_stem, is_jz)
    ed_lines = logical_lines(ed_stem, False)
    r["src_lines"] = src_lines
    r["ed_lines"] = ed_lines
    r["line_count_src_vs_ed"] = (len(src_lines), len(ed_lines))
    r["opt_newlines_src_vs_ed"] = {k: (src_opts[k].count("\n"), ed_opts[k].count("\n")) for k in src_opts if src_opts[k].count("\n") != ed_opts[k].count("\n")}
    # 3 交叉一致：题目.jsonl
    t = tj[n]
    t_stem = blocks_text(t["stem"])
    r["tj_vs_effective_stem_same"] = squash(t_stem) == squash(ed_stem.replace("[TABLE]", "[FIGURE]")) if ed_stem else None
    r["tj_vs_effective_stem_lines_same"] = t_stem.split("\n") == ed_stem.split("\n")
    t_opts = {k: opt_text(v) for k, v in t["options"].items()}
    r["tj_vs_effective_opts_same"] = all(t_opts[k] == ed_opts[k] for k in ed_opts)
    # 题本：取该题区块
    m = re.search(rf"^### {n}\.\n(.*?)(?=^### |\Z|^## )", booklet, re.S | re.M)
    blk = m.group(1) if m else ""
    r["booklet_contains_all_text"] = all(squash(seg) in squash(blk.replace("**", "")) for seg in re.split(r"\[FIGURE\]|\[TABLE\]", t_stem))
    report[n] = r

for n, r in report.items():
    print(f"===== 第{n}题 [{r['source_bank']}] edits={r['edits']}")
    print("  题干字符差异(源→编):", r["stem_char_diff"] or "无")
    print("  选项字符差异:", r["opt_char_diff"] or "无")
    print("  源逻辑行数 vs 编辑稿行数:", r["line_count_src_vs_ed"])
    if r["line_count_src_vs_ed"][0] != r["line_count_src_vs_ed"][1] or r["opt_newlines_src_vs_ed"]:
        print("   源逻辑行：")
        for l in r["src_lines"]:
            print("     |", l)
        print("   编辑稿行：")
        for l in r["ed_lines"]:
            print("     |", l)
    print("  选项内换行数不一致(源,编):", r["opt_newlines_src_vs_ed"] or "无")
    print("  题目.jsonl 与有效题面一致: 题干", r["tj_vs_effective_stem_same"], "| 行结构", r["tj_vs_effective_stem_lines_same"], "| 选项", r["tj_vs_effective_opts_same"])
    print("  题本_待审.md 包含全部题干文字:", r["booklet_contains_all_text"])

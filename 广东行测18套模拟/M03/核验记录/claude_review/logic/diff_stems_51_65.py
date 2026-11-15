#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
逐字比对 M03 第51—65题：源题（source_question.stem / options）与当前题面
（selection.json 的 stem_override / options，以及考生可见的 题目.jsonl）。

用法（在任意目录）：
    python3 diff_stems_51_65.py [M03目录]
默认 M03 目录为 /home/user/xing-ce1/广东行测18套模拟/M03

输出：
  1. 每题：源题干原文（换行显示为 ⏎）、当前题干、去掉换行后的逐字差异（difflib opcodes）
  2. 选项逐项差异
  3. 题目.jsonl 中显示的题干/选项是否与 stem_override/options 一致
  4. 汇总：哪些题去换行后完全一致（真正 layout_only），哪些有实字改动
"""
import difflib
import json
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/home/user/xing-ce1/广东行测18套模拟/M03")
RANGE = range(51, 66)


def show(s):
    return s.replace("\n", "⏎")


def ops(a, b):
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    out = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            out.append(f"{tag}: 源[{i1}:{i2}]「{show(a[i1:i2])}」 -> 现[{j1}:{j2}]「{show(b[j1:j2])}」")
    return out


def flatten_parts(parts):
    if isinstance(parts, str):
        return parts
    return "".join(p.get("text", "") if p.get("type") == "text" else f"[{p.get('type')}]" for p in parts)


sel = {q["number"]: q for q in json.loads((ROOT / "selection.json").read_text(encoding="utf-8"))}
vis = {}
with open(ROOT / "题目.jsonl", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            q = json.loads(line)
            vis[q["number"]] = q

SENT_END = set("。？！；：”?!;:")
PROMPT = re.compile(r"^(以下|下列|根据|要使|由此|据此|如果以下|上述)")
ARTIFACTS = [
    (r" {2,}", "连续空格（HTML/打印中会折叠为一个空格，若是填空线则不可见）"),
    (r"(?<=[一-鿿]):|:(?=\s*[一-鿿])", "半角冒号"),
    (r"(?<=[一-鿿])\?|\?$", "半角问号"),
    (r"(?<=\d) (?=[一-鿿])|(?<=[一-鿿]) (?=\d)", "数字与汉字间多余空格"),
    (r"(?<=[一-鿿]): ", "冒号后空格"),
    (r"^[、，。]", "开头孤立标点"),
    (r"(?<=\d)-(?=\d)", "数字间半角连字符（中文排版宜用“—”或“至”）"),
]
FLAGS = []

summary = []
for n in RANGE:
    q = sel[n]
    sq = q["source_question"]
    print("=" * 78)
    print(f"Q{n}  {q['source_id']}  edits={[e['type'] for e in q.get('edits', [])]}")
    src_stem = flatten_parts(sq.get("stem") or "") if sq else ""
    cur_stem = flatten_parts(q.get("stem_override") or "") or src_stem
    if sq and sq.get("instruction"):
        print("源 instruction:", show(sq["instruction"]))
    print("源题干:", show(src_stem))
    print("现题干:", show(cur_stem))
    a = src_stem.replace("\n", "")
    b = cur_stem.replace("\n", "")
    d = ops(a, b)
    print("去换行后题干差异:", "无" if not d else "")
    for x in d:
        print("   ", x)
    # 换行位置对照：源的硬换行中，哪些在现题面里保留为换行
    src_breaks = [i for i, ch in enumerate(src_stem) if ch == "\n"]
    cur_breaks = [i for i, ch in enumerate(cur_stem) if ch == "\n"]
    print(f"源换行数={len(src_breaks)}，现换行数={len(cur_breaks)}")
    # 标出源中每个换行前后的文字，并分类：
    #   “句末分隔”= 换行前一字是句末/分句标点（。？！；：” 及半角形式），通常是真实分段；
    #   “句中硬换行”= 其余，属于PDF行宽造成的折行，应合并。
    # 判断现题面中该处是否仍有换行：用去换行后的前后文在现题面中定位。
    cur_flat = cur_stem.replace("\n", "")
    flat_to_cur = [i for i, ch in enumerate(cur_stem) if ch != "\n"]  # 去换行下标 -> 现题面下标
    src_flat_pos = 0
    for i, ch in enumerate(src_stem):
        if ch != "\n":
            src_flat_pos += 1
            continue
        before = src_stem[max(0, i - 8):i]
        after = src_stem[i + 1:i + 9]
        kind = "句末分隔" if src_stem[i - 1:i] in SENT_END else "句中硬换行"
        key_b = before.replace("\n", "")
        key_a = after.replace("\n", "")
        pos = cur_flat.find(key_b + key_a)
        kept = "?(该处有实字改动)"
        if pos >= 0:
            cut = pos + len(key_b)  # 去换行串中的切点
            # 现题面中切点之前一字的位置之后是否紧跟换行
            ci = flat_to_cur[cut - 1] if cut - 1 < len(flat_to_cur) else None
            kept = "保留换行" if (ci is not None and cur_stem[ci + 1:ci + 2] == "\n") else "已合并"
        flag = "  <== 句末分隔被合并，需人工判断是否改变结构" if (kind == "句末分隔" and kept == "已合并") else ""
        print(f"   源换行[{kind}] …{show(before)}⏎{show(after)}…  -> {kept}{flag}")
        if flag:
            FLAGS.append((n, f"句末分隔被合并：…{show(before)}⏎{show(after)}…"))
    # 设问是否单独成行
    last = cur_stem.split("\n")[-1]
    if not PROMPT.match(last):
        FLAGS.append((n, f"设问未单独成行（末行：…{show(last[-30:])}）"))
    # 排版瑕疵扫描（现题面 + 选项）
    texts = [("题干", cur_stem)] + [(f"选项{k}", flatten_parts(v)) for k, v in (q.get("options") or sq.get("options", {})).items()]
    for where, t in texts:
        for pat, desc in ARTIFACTS:
            for m in re.finditer(pat, t):
                # 空括号内的空格由打印工具统一为“（　）”，不算瑕疵
                if pat == r" {2,}" and t[m.start() - 1:m.start()] in "（(" and t[m.end():m.end() + 1] in "）)":
                    continue
                FLAGS.append((n, f"{where} {desc}：…{show(t[max(0, m.start() - 6):m.end() + 6])}…"))
    diffs_opt = []
    so = sq.get("options", {}) if sq else {}
    co = q.get("options") or so  # options 为 null 表示沿用源选项
    for k in sorted(set(so) | set(co)):
        sa = so.get(k, "")
        ca = co.get(k, "")
        sa = flatten_parts(sa)
        ca = flatten_parts(ca)
        dd = ops(sa.replace("\n", ""), ca.replace("\n", ""))
        if dd or sa != ca:
            diffs_opt.append(k)
            print(f"选项{k} 源:「{show(sa)}」")
            print(f"选项{k} 现:「{show(ca)}」")
            for x in dd:
                print("   ", x)
    # 考生可见题面一致性
    v = vis[n]
    vstem = flatten_parts(v["stem"])
    same_stem = vstem == cur_stem
    vopts = {k: flatten_parts(val) for k, val in v["options"].items()}
    same_opts = vopts == {k: flatten_parts(val) for k, val in co.items()}
    print(f"题目.jsonl 题干与 stem_override 一致？{same_stem}；选项一致？{same_opts}")
    if not same_stem:
        for x in ops(cur_stem, vstem):
            print("   题目.jsonl差异:", x)
    summary.append((n, q["source_id"], not d, diffs_opt, same_stem and same_opts))

print("=" * 78)
print("汇总（题号｜源ID｜题干去换行后与源一致｜有改动的选项｜题本与底稿一致）")
for n, sid, same, dopt, consistent in summary:
    print(f"Q{n}｜{sid}｜{'一致' if same else '有实字改动'}｜{dopt or '无'}｜{consistent}")
print("=" * 78)
print("排版/转写提示（需人工判断，非自动判错）")
for n, msg in FLAGS:
    print(f"Q{n}｜{msg}")

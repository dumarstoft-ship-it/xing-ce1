#!/usr/bin/env python3
"""核对第71—90题：题目.jsonl（考生可见）、selection.json（编辑底稿）、
selection.json 中 source_question.material（源对象）与源库 全部题目.jsonl 四者的一致性。
- 文字段落：拼接后逐字比较（容忍段落切分差异），并列出差异位置；
- 表格：逐格比较；
- 题干/选项：stem_override 与源题干差异列出。
运行：python3 -I material_compare.py <仓库根目录>
"""
import difflib
import json
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else "/home/user/xing-ce1")
m04 = root / "广东行测18套模拟/M04"
bank_path = root / "模考/2026下半年广东卷_16-33季_AI可读/全部题目.jsonl"

visible = {r["number"]: r for r in map(json.loads, (m04 / "题目.jsonl").read_text().splitlines()) if r.strip() if False} if False else {}
for line in (m04 / "题目.jsonl").read_text().splitlines():
    if line.strip():
        r = json.loads(line)
        visible[r["number"]] = r
sel = {r["number"]: r for r in json.loads((m04 / "selection.json").read_text())}
bank = {}
for line in bank_path.read_text().splitlines():
    if line.strip():
        q = json.loads(line)
        bank[q["id"]] = q


def text_of(blocks):
    return "".join(b.get("text", "") for b in blocks if b.get("type") == "text")


def tables_of(blocks):
    return [b for b in blocks if b.get("type") == "table"]


def norm(s):
    return s.replace("\n", "").replace(" ", "").replace("　", "")


issues = []
seen_material = {}
for n in range(71, 91):
    v, s = visible[n], sel[n]
    sq = s["source_question"]
    b = bank.get(s["source_id"])
    # 1) 源对象与源库一致
    same_bank = (b == sq)
    # 2) 题干
    vis_stem = text_of(v["stem"])
    sel_stem = text_of(s.get("stem_override", sq["stem"]))
    src_stem = text_of(sq["stem"])
    # 3) 选项
    vis_opts = json.dumps(v["options"], ensure_ascii=False, sort_keys=True)
    src_opts = sq["options"]
    # 选项图 path 在题目.jsonl 中加了前缀，比较时只比较文件名与文本
    def opt_sig(opts):
        out = {}
        for k, blocks in opts.items():
            out[k] = [(bb.get("type"), bb.get("text") or Path(bb.get("path", "")).name) for bb in blocks]
        return out
    opts_same = opt_sig(v["options"]) == opt_sig(src_opts) == opt_sig(s.get("options", src_opts))
    # 4) 材料
    vis_mat = v["materials"][0]["blocks"]
    sel_mat = s.get("materials", [sq["material"]])[0]["blocks"]
    src_mat = sq["material"]["blocks"]
    t_vis, t_sel, t_src = norm(text_of(vis_mat)), norm(text_of(sel_mat)), norm(text_of(src_mat))
    tab_vis, tab_sel, tab_src = tables_of(vis_mat), tables_of(sel_mat), tables_of(src_mat)
    def tab_sig(tabs):
        return [(t.get("title"), t.get("headers"), t.get("rows"), t.get("notes")) for t in tabs]
    mat_text_same = (t_vis == t_sel == t_src)
    mat_tab_same = (tab_sig(tab_vis) == tab_sig(tab_sel) == tab_sig(tab_src))
    print(f"Q{n} 源对象=源库:{same_bank} | 题干改动:{'是' if vis_stem != src_stem else '否'}"
          f"(题本=底稿:{vis_stem == sel_stem}) | 选项一致:{opts_same} | 材料文字一致:{mat_text_same} | 表格一致:{mat_tab_same}"
          f" | 段落数 题本{len([x for x in vis_mat if x['type']=='text'])}/源{len([x for x in src_mat if x['type']=='text'])}")
    if vis_stem != src_stem:
        print("     源题干：", src_stem)
        print("     现题干：", vis_stem)
    if not mat_text_same:
        for a_name, a, b_name, bb in (("题本", t_vis, "源", t_src), ("底稿", t_sel, "源", t_src)):
            if a != bb:
                sm = difflib.SequenceMatcher(None, a, bb)
                for op in sm.get_opcodes():
                    if op[0] != "equal":
                        print(f"     {a_name} vs {b_name} {op[0]}: {a[op[1]:op[2]]!r} -> {bb[op[3]:op[4]]!r}")
    if not mat_tab_same:
        print("     表格差异：", tab_sig(tab_vis), tab_sig(tab_src))
    # 源材料块结构（只打印一次）
    mid = sq["material"]["id"]
    if mid not in seen_material:
        seen_material[mid] = n
        print(f"   源材料 {mid} 块类型：{[x['type'] for x in src_mat]}；source_asset_ids={sq['material'].get('source_asset_ids')}；页={sq['material'].get('source_pages')}")
        for x in src_mat:
            if x["type"] != "text" and x["type"] != "table":
                print("     非文字/表格块：", json.dumps(x, ensure_ascii=False)[:300])
            if x["type"] == "table":
                print("     表注 notes=", repr(x.get("notes")), " 表题=", x.get("title"))
        # 原始文字（便于人工比对特殊字符，如“注：”公式）
        for x in src_mat:
            if x["type"] == "text" and ("注" in x["text"] or "=" in x["text"]):
                print("     含公式/注文字：", repr(x["text"][-120:]))

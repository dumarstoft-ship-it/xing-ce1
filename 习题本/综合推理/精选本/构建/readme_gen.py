#!/usr/bin/env python3
"""生成精选本 README.md 与 选题清单.json。

python3 readme_gen.py <selection.json> <records.json> <layout.json> <输出目录> <PDF文件名> <原书相对路径> <notes.json>
notes.json：{"cut_table": [[大类, 删去的主要是]], "issues": [str], "issues_in": [str]}
"""
import json, re, sys
from collections import Counter

sel_p, rec_p, lay_p, out_dir, pdf_name, src_rel, notes_p = sys.argv[1:8]
sel = json.load(open(sel_p)); recs = {r["idx"]: r for r in json.load(open(rec_p))}
lay = json.load(open(lay_p)); pg = lay["pageno"]; notes = json.load(open(notes_p))

def short_src(s):
    s = re.sub(r"《[^》]*》", "", s); s = re.sub(r"（[^）]*）", "", s)
    s = re.sub(r"广东省(?!考)", "广东", s).replace("公开招聘", "").replace("工作人员", "")
    return re.sub(r"\s+", " ", s).strip()

rows, n = [], 0
for mod in sel["modules"]:
    for m in mod["models"]:
        for q in m["questions"]:
            n += 1
            r = recs[q["idx"]]
            rows.append(dict(seq=n, idx=q["idx"], module=f'{mod["no"]} {mod["name"]}', model=f'{m["no"]} {m["name"]}',
                             tier=q["tier"], move=q["move"], source=r["source"], answer=r["answer"],
                             page_new=pg[f'q:{q["idx"]}'], page_old=r["page"], original_group=r["group"],
                             original_category=r["category"]))
total = len(rows)
tiers = Counter(x["tier"] for x in rows)
nmodels = sum(len(mod["models"]) for mod in sel["modules"])
sel_ids = {x["idx"] for x in rows}
backup_ids = {b["idx"] for mod in sel["modules"] for b in mod.get("backup", [])}

L = []
L.append("# 综合推理精选本\n")
L.append(f"[打开精选本（PDF，{lay['pages']}页）](./{pdf_name})\n")
L.append(f"从[《综合推理二刷题本》]({src_rel})的337题中精选 **{total}** 题：核心 {tiers['核心']}、进阶 {tiers['进阶']}、避坑 {tiers['避坑']}。"
         f"按 {nmodels} 个推理模型分成 6 个模块。题面、选项和草稿解析页直接取自原书，题号沿用原书编号，方便两本对照。\n")
L.append("本册新增的是选题与分类、认知地图、各模块导读（每个模型的本质、信号、第一笔、易错）和突破口速查。\n")
L.append("## 怎么用\n")
L.append(f"1. 先读认知地图（第{pg['map']}页）：几种题型都可以用同一套五个动作来解，依次是表示、起点、传播、分支、收口。")
L.append("2. 每个模块先读导读，记住每个模型的“第一笔”，再按卡片顺序做题。")
L.append(f"3. 先做核心题，做对后再做进阶题；时间紧只做核心题（{tiers['核心']}道）。")
L.append("4. 练习页在正面，翻页看原书的草稿解析，重点看“收笔”和“容易错推”。")
L.append("5. 某个模型错两道以上，去原书做该模块导读页列出的加练备选。")
L.append(f"6. 全部做完后，用附录“突破口速查”（第{pg['app']}页）盖住右栏自测。\n")
L.append("A4 双面打印，选长边翻页：每题练习页在正面，解析在背面。PDF 目录、模型卡片里的题号和书签都可以点击跳转。\n")
L.append("## 六个模块\n")
L.append("| 模块 | 练什么 | 模型 | 题数 | 起始页 |")
L.append("| --- | --- | ---: | ---: | ---: |")
for mi, mod in enumerate(sel["modules"]):
    nq = sum(len(m["questions"]) for m in mod["models"])
    L.append(f'| {mod["no"]} {mod["name"]} | {mod["tagline"]} | {len(mod["models"])} | {nq} | {pg[f"mod:{mi+1}"]} |')
L.append("\n## 选题总表\n")
L.append("“精选”是本册顺序，“原题”是原书题号。突破口放在折叠栏里，做完再展开。\n")
for mi, mod in enumerate(sel["modules"]):
    L.append(f'### 模块 {mod["no"]} · {mod["name"]}\n')
    L.append("| 精选 | 原题 | 模型 | 级别 | 题源 | 页码 |")
    L.append("| ---: | ---: | --- | --- | --- | ---: |")
    mrows = [x for x in rows if x["module"] == f'{mod["no"]} {mod["name"]}']
    for x in mrows:
        L.append(f'| {x["seq"]:02d} | {x["idx"]:02d} | {x["model"]} | {x["tier"]} | {short_src(x["source"])} | {x["page_new"]} |')
    L.append("\n<details><summary>突破口（做完再看）</summary>\n")
    for x in mrows:
        L.append(f'- **{x["seq"]:02d}｜原{x["idx"]:02d}**：{x["move"]}')
    L.append("\n</details>\n")
L.append("## 怎么挑的\n")
for h in sel["cover"]["how"]:
    L.append(f"- {h}")
L.append("")
L.append("| 原书大类 | 原题数 | 入选 | 备选 | 删去的主要是 |")
L.append("| --- | ---: | ---: | ---: | --- |")
cats = ["对应与排序", "分组与名额", "复合条件与约束传播", "真假判断", "原题辨析"]
reasons = dict(notes["cut_table"])
for c in cats:
    ids = [i for i, r in recs.items() if r["category"] == c]
    L.append(f'| {c} | {len(ids)} | {sum(1 for i in ids if i in sel_ids)} | {sum(1 for i in ids if i in backup_ids)} | {reasons.get(c, "")} |')
L.append(f'| 合计 | 337 | {total} | {len(backup_ids)} | |')
L.append("\n各模块导读页列出的“加练备选”只给原书题号和页码，不占本册篇幅。\n")
L.append("## 重解时发现的答案与题面问题\n")
L.append("337题都重新独立解过一遍。下面这些题的参考答案或题面有问题；凡是影响作答的，都没有放进主线。\n")
for s in notes["issues"]:
    L.append(f"- {s}")
L.append("\n本册收入、但作答时要按惯常读法理解的题：\n")
for s in notes["issues_in"]:
    L.append(f"- {s}")
L.append("\n## 加练备选\n")
for mod in sel["modules"]:
    if mod.get("backup"):
        items = "、".join(f'原{b["idx"]:02d}（第{recs[b["idx"]]["page"]}页）' for b in mod["backup"])
        L.append(f'- **模块 {mod["no"]} {mod["name"]}**：{items}')
L.append("\n## 文件\n")
L.append("| 文件 | 内容 |")
L.append("| --- | --- |")
L.append(f"| [{pdf_name}](./{pdf_name}) | 本册，A4 双面 |")
L.append("| [选题清单.json](./选题清单.json) | 每题的模块、模型、级别、突破口、题源，以及在两本书中的页码 |")
L.append("| [构建/](./构建/) | 从原书重新生成本册的脚本与选题内容源 |")
open(f"{out_dir}/README.md", "w").write("\n".join(L) + "\n")
json.dump({"title": sel["title"], "source_book": src_rel, "total": total, "tiers": dict(tiers), "pages": lay["pages"],
           "questions": rows,
           "backup": [{"module": f'{mod["no"]} {mod["name"]}', "idx": b["idx"], "page_old": recs[b["idx"]]["page"]}
                      for mod in sel["modules"] for b in mod.get("backup", [])]},
          open(f"{out_dir}/选题清单.json", "w"), ensure_ascii=False, indent=1)
print("README 与选题清单已写出", total)

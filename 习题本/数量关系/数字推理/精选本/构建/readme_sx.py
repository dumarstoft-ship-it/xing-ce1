#!/usr/bin/env python3
"""生成数字推理精选本 README.md 与 选题清单.json。
python3 readme_sx.py <selection.json> <records.json> <layout.json> <输出目录> <PDF文件名> <原书相对路径>"""
import json, sys
from collections import Counter
sel_p, rec_p, lay_p, out_dir, pdf_name, src_rel = sys.argv[1:7]
sel = json.load(open(sel_p)); recs = {r["id"]: r for r in json.load(open(rec_p))}; lay = json.load(open(lay_p)); pg = lay["pageno"]
rows = []
for mi, mod in enumerate(sel["modules"]):
    for g in mod["groups"]:
        for q in g["questions"]:
            r = recs[q["id"]]
            rows.append(dict(seq=lay["seqno"][q["id"]], id=q["id"], module=f'{mod["no"]} {mod["name"]}', group=f'{g.get("id", "")} {g["name"]}'.strip(),
                             tier=q["tier"], move=q["move"], source=r["source"], selfmade=r["selfmade"], answer=f'{r["answer"]} {r["answer_value"]}',
                             page_new=pg[f'q:{q["id"]}'], page_old=r["page"]))
total = len(rows); tiers = Counter(x["tier"] for x in rows)
real = sum(1 for x in rows if not x["selfmade"])
L = ["# 数字推理精选本\n", f"[打开精选本（PDF，{lay['pages']}页）](./{pdf_name})\n",
     f"从[《广东数字推理 · 条件反射训练》]({src_rel})的249题中精选 **{total}** 题（{'全部是真题' if real == total else f'真题 {real} 道'}）：核心 {tiers.get('核心', 0)}、进阶 {tiers.get('进阶', 0)}。"
     f"按原书的模型编号分成 {len(sel['modules'])} 个模块，最后一个模块是不给提示的识别训练。题目和解析都从原书原样裁出，编号沿用原书（如 M01-04 指模型 M01 的第4题）。\n",
     "本册新增的是选题与分类、认知地图（看到什么就先写什么）、各模块导读（每个模型的本质、信号、首式、易错）和首式速查。\n",
     "## 怎么用\n"]
for i, s in enumerate(sel["cover"]["use"], 1): L.append(f"{i}. {s}")
L += ["", "## 模块一览\n", "| 模块 | 练什么 | 题数 | 起始页 |", "| --- | --- | ---: | ---: |"]
for mi, mod in enumerate(sel["modules"]):
    L.append(f'| {mod["no"]} {mod["name"]} | {mod["tagline"]} | {sum(len(g["questions"]) for g in mod["groups"])} | {pg[f"mod:{mi+1}"]} |')
L += ["", "## 选题总表\n", "首式放在折叠栏里，做完再展开。\n"]
for mi, mod in enumerate(sel["modules"]):
    L += [f'### 模块 {mod["no"]} · {mod["name"]}\n', "| 精选 | 原书编号 | 模型或组 | 级别 | 出处 | 页码 |", "| ---: | --- | --- | --- | --- | ---: |"]
    mrows = [x for x in rows if x["module"] == f'{mod["no"]} {mod["name"]}']
    for x in mrows:
        L.append(f'| {x["seq"]:02d} | {x["id"]} | {x["group"]} | {x["tier"]} | {x["source"]} | {x["page_new"]} |')
    L.append("\n<details><summary>首式（做完再看）</summary>\n")
    for x in mrows: L.append(f'- **{x["seq"]:02d}｜{x["id"]}**：{x["move"]}')
    L.append("\n</details>\n")
L += ["## 怎么挑的\n"] + [f"- {h}" for h in sel["cover"]["how"]] + ["",
      "| 原书部分 | 原题数 | 入选 | 删去的主要是 |", "| --- | ---: | ---: | --- |"]
for t in sel["appendix"]["table"]: L.append(f"| {t[0]} | {t[1]} | {t[2]} | {t[3]} |")
L += ["", "## 重算时发现的问题\n"] + [f"- {s}" for s in sel["appendix"]["issues"]]
if sel["appendix"].get("issues_in"):
    L += ["", "本册收入、但作答时要注意的题：\n"] + [f"- {s}" for s in sel["appendix"]["issues_in"]]
L += ["", "## 加练备选\n"]
for mod in sel["modules"]:
    if mod.get("backup"):
        L.append(f'- **模块 {mod["no"]} {mod["name"]}**：' + "、".join(f'{b}（第{recs[b]["page"]}页）' for b in mod["backup"]))
L += ["", "## 文件\n", "| 文件 | 内容 |", "| --- | --- |", f"| [{pdf_name}](./{pdf_name}) | 本册，A4 双面 |",
      "| [选题清单.json](./选题清单.json) | 每题的模块、模型、级别、首式、出处和答案，以及在两本书中的页码 |",
      "| [构建/](./构建/) | 从原书重新生成本册的脚本与选题内容源 |"]
open(f"{out_dir}/README.md", "w").write("\n".join(L) + "\n")
json.dump({"title": sel["title"], "source_book": src_rel, "total": total, "tiers": dict(tiers), "pages": lay["pages"], "questions": rows,
           "backup": [{"module": f'{m["no"]} {m["name"]}', "id": b, "page_old": recs[b]["page"]} for m in sel["modules"] for b in m.get("backup", [])]},
          open(f"{out_dir}/选题清单.json", "w"), ensure_ascii=False, indent=1)
print("README 与选题清单已写出", total)

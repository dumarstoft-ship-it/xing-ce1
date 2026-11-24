#!/usr/bin/env python3
"""生成图形推理精选本 README.md 与 选题清单.json。
python3 readme_tt.py <selection.json> <records.json> <layout.json> <输出目录> <PDF文件名> <原书目录相对路径>"""
import json, sys
from collections import Counter
import pages_tt as P

sel_p, rec_p, lay_p, out_dir, pdf_name, src_dir = sys.argv[1:7]
sel = json.load(open(sel_p)); recs = {r["id"]: r for r in json.load(open(rec_p))}; lay = json.load(open(lay_p)); pg = lay["pageno"]
B178, B200 = f"{src_dir}/固定题型178题_题后即看答案.pdf", f"{src_dir}/平面图推200题_题后即看答案.pdf"
book = lambda i: "178题" if i[0] == "S" else "200题"
rows = []
for mod in sel["modules"]:
    for g in mod["groups"]:
        for k, q in enumerate(g["questions"], 1):
            r = recs[q["id"]]
            rows.append(dict(seq=lay["seqno"][q["id"]], id=q["id"], book=book(q["id"]), module=f'{mod["no"]} {mod["name"]}',
                             group=f'{g.get("no", "")} {g["name"]}'.strip(), order_in_set=k if mod.get("kind") == "timed" else None,
                             tier=q["tier"], move=q["move"], note=q.get("note", ""), source=P.src_label(r), answer=r["answer"],
                             page_new=pg[f'q:{q["id"]}'], page_old=r["page"]))
total = len(rows); tiers = Counter(x["tier"] for x in rows)
timed = [m for m in sel["modules"] if m.get("kind") == "timed"]
n_timed = sum(len(g["questions"]) for m in timed for g in m["groups"])
n_sets = sum(len(m["groups"]) for m in timed)
n_sp = sum(1 for x in rows if x["module"][0] == "A"); n_pl = sum(1 for x in rows if x["module"][0] == "B")
L = ["# 图形推理精选本\n", f"[打开精选本（PDF，{lay['pages']}页）](./{pdf_name})\n",
     f"从[《固定题型178题》]({B178})和[《平面图推200题》]({B200})共378题中精选 **{total}** 题：训练模块 {n_sp + n_pl} 题（空间 {n_sp}、平面 {n_pl}；核心 {tiers.get('核心', 0)}、进阶 {tiers.get('进阶', 0)}），限时套卷 {n_sets} 套 {n_timed} 题。"
     "题目和解析都从原书原样裁出，编号沿用原书：S1-12 指178题第1章第12题，P001 指200题的第1题。\n",
     "本册新增的是：选题与分类、认知地图（看到什么，第一步做什么）、每组一张方法卡（方法、信号、最快路径、易错、限时）、每题一句最快路径、10套限时卷，以及对原解析的勘误。\n",
     "训练模块“题后即看答案”：每道题下面紧跟答案和解析，做题时先遮住。限时套卷先排5道题，答案在后一页。\n",
     "## 怎么用\n"]
for i, s in enumerate(sel["cover"]["use"], 1): L.append(f"{i}. {s}")
L += ["", "## 模块一览\n", "| 模块 | 练什么 | 题数 | 起始页 |", "| --- | --- | ---: | ---: |"]
for mi, mod in enumerate(sel["modules"]):
    L.append(f'| {mod["no"]} {mod["name"]} | {mod["tagline"]} | {sum(len(g["questions"]) for g in mod["groups"])} | {pg[f"mod:{mi+1}"]} |')
L += ["", "## 选题总表\n", "最快路径放在折叠栏里，做完再展开。页码指本册。\n"]
for mod in sel["modules"]:
    mrows = [x for x in rows if x["module"] == f'{mod["no"]} {mod["name"]}']
    if mod.get("kind") == "timed":
        L += [f'### 模块 {mod["no"]} · {mod["name"]}\n', "| 精选 | 原书编号 | 套卷 | 第几题 | 出处 | 页码 |", "| ---: | --- | --- | ---: | --- | ---: |"]
        for x in mrows: L.append(f'| {x["seq"]:03d} | {x["id"]} | {x["group"]} | {x["order_in_set"]} | {x["source"]} | {x["page_new"]} |')
    else:
        L += [f'### 模块 {mod["no"]} · {mod["name"]}\n', "| 精选 | 原书编号 | 组 | 级别 | 出处 | 页码 |", "| ---: | --- | --- | --- | --- | ---: |"]
        for x in mrows: L.append(f'| {x["seq"]:03d} | {x["id"]} | {x["group"]} | {x["tier"]} | {x["source"]} | {x["page_new"]} |')
    L.append("\n<details><summary>最快路径（做完再看）</summary>\n")
    for x in mrows: L.append(f'- **{x["seq"]:03d}｜{x["id"]}**：{x["move"]}')
    L.append("\n</details>\n")
L += ["## 怎么挑的\n"] + [f"- {h}" for h in sel["cover"]["how"]] + ["",
      "| 原书部分 | 原题数 | 入选 | 删去的主要是 |", "| --- | ---: | ---: | --- |"]
for t in sel["appendix"]["table"]: L.append(f"| {t[0]} | {t[1]} | {t[2]} | {t[3]} |")
L += ["", "入选数含限时套卷。", "", "## 核对时发现的问题\n"] + [f"- {s}" for s in sel["appendix"]["issues"]]
L += ["", "## 加练备选\n", "与训练模块的题动作重复，某类错得多时再练。页码指原书 PDF。\n"]
for mod in sel["modules"]:
    if mod.get("backup"):
        L.append(f'- **{mod["no"]} {mod["name"]}**：' + "、".join(f'{b}（{book(b)}第{recs[b]["page"]}页）' for b in mod["backup"]))
L += ["", "## 文件\n", "| 文件 | 内容 |", "| --- | --- |", f"| [{pdf_name}](./{pdf_name}) | 本册，A4 |",
      "| [选题清单.json](./选题清单.json) | 每题的模块、组、级别、最快路径、勘误、出处和答案，以及在本册和原书中的页码 |",
      "| [构建/](./构建/) | 从原书重新生成本册的脚本、逐题评估与选题内容源 |"]
open(f"{out_dir}/README.md", "w").write("\n".join(L) + "\n")
json.dump({"title": sel["title"], "source_books": [B178, B200], "total": total, "training": n_sp + n_pl, "spatial": n_sp, "plane": n_pl,
           "timed": n_timed, "timed_sets": n_sets, "tiers": dict(tiers), "pages": lay["pages"], "questions": rows,
           "backup": [{"module": f'{m["no"]} {m["name"]}', "id": b, "book": book(b), "page_old": recs[b]["page"]} for m in sel["modules"] for b in m.get("backup", [])]},
          open(f"{out_dir}/选题清单.json", "w"), ensure_ascii=False, indent=1)
print("README 与选题清单已写出", total)

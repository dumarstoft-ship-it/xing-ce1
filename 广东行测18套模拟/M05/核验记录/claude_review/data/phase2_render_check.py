# -*- coding: utf-8 -*-
"""第二阶段：题本_待审.md 与 阅览HTML 中第71—90题的呈现与 M05/题目.jsonl 是否一致（逐格），并确认已删附注未残留。只读。"""
import json, os, re, html
M05 = "/home/user/xing-ce1/广东行测18套模拟/M05"
m05 = {r["number"]: r for r in (json.loads(l) for l in open(os.path.join(M05, "题目.jsonl"), encoding="utf-8") if l.strip())}
md = open(os.path.join(M05, "题本_待审.md"), encoding="utf-8").read()
sec = md[md.index("## 七、资料分析"):]
htm = open(os.path.join(M05, "阅览/M05_题本_阅览.html"), encoding="utf-8").read()
htm_txt = html.unescape(re.sub(r"<[^>]+>", "|", htm))

# 1) markdown 表格逐格
md_tables = []
for m in re.finditer(r"((?:^\|.*\|\n)+)", sec, re.M):
    rows = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in m.group(1).strip().split("\n")]
    rows = [r for r in rows if not all(set(c) <= set("- ") for c in r)]
    md_tables.append(rows)
json_tables = []
for n in (71, 76, 81, 86):
    for mm in m05[n]["materials"]:
        for b in mm["blocks"]:
            if b["type"] == "table":
                json_tables.append([b["headers"]] + b["rows"])
print("题本表格数 %d，JSON表格数 %d" % (len(md_tables), len(json_tables)))
for i, (a, b) in enumerate(zip(md_tables, json_tables)):
    print("表%d：题本 == JSON 逐格：%s（%d 行 × %d 列）" % (i + 1, a == b, len(b), len(b[0])))
# 2) 材料文字、题干、选项文字在题本中均出现
miss = []
for n in range(71, 91):
    q = m05[n]
    for b in q["stem"]:
        if b["type"] == "text" and b["text"] not in sec:
            miss.append((n, "题干", b["text"][:30]))
    for k, v in q["options"].items():
        for b in v:
            if b["type"] == "text" and ("**%s.** %s" % (k, b["text"])) not in sec:
                miss.append((n, "选项" + k, b["text"][:30]))
            if b["type"] == "figure" and b["path"] not in sec:
                miss.append((n, "图" + k, b["path"]))
    for mm in q["materials"]:
        for b in mm["blocks"]:
            if b["type"] == "text" and b["text"] not in sec:
                miss.append((n, "材料文字", b["text"][:30]))
            if b["type"] == "table" and ("**%s**" % b["title"]) not in sec:
                miss.append((n, "表题", b["title"]))
print("题本中缺失/不一致的文字：", miss or "无")
# 3) 附注是否残留
for name, txt in (("题本_待审.md", md), ("阅览HTML", htm)):
    print("%s 含'原表未标百分号'：%s；含'绝对增量'：%s" % (name, "原表未标百分号" in txt, "绝对增量" in txt))
# 4) 阅览 HTML 中 76—80 表的全部数字是否出现
cells = [c for r in json_tables[1] for c in r]
print("阅览HTML 76—80 表 48+6 格是否全部出现：", all(c in htm_txt for c in cells))
import base64, hashlib
man = {x["id"]: x["sha256"] for x in json.load(open("/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/图片清单.json", encoding="utf-8"))}
inv = {v: k for k, v in man.items()}
seg = htm[htm.find("以下折线图中"):]
srcs = re.findall(r'<img[^>]+src="([^"]+)"', seg)[:4]
got = []
for s_ in srcs:
    if s_.startswith("data:image"):
        got.append(inv.get(hashlib.sha256(base64.b64decode(s_.split(",", 1)[1])).hexdigest(), "不在图片清单"))
    else:
        got.append(s_)
print("阅览HTML 第90题 A—D 内嵌图（按出现顺序，sha256 对照图片清单）：", got)

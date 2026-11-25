#!/usr/bin/env python3
"""生成 2016—2018 年国考地市级卷资料分析题库：GK2016-DS、GK2017-DS、GK2018-DS。

    python3 国考/资料分析/tools/gk2016_2018_build.py

每卷写出 <卷>.jsonl、<卷>.md、assets/<卷>/*.png 与 assets/<卷>/manifest.json；字段与
广东/行测/2013-2021/schema.json 一致（question_number 为国考原题号111—130，超出该 schema 为广东卷设的上限100）。

做法（同广东题库 tools/extract.py）：题本按 288 DPI 用 pdftoppm 渲染整页，图表在登记的搜索范围内收紧到墨迹处
（灰度<240）、四周留 6 像素白边、不碰正文文字后裁剪；不重画。材料、题干、选项文字取自题本文字层，
build 时逐段与文字层比对（gk2016_2018_spec.py 的 text_fixes 是仅有的几处改动）。
依赖：Python 3.10+、pdfplumber、Pillow、numpy、poppler-utils（pdftoppm）、git。
"""
import hashlib
import json
import logging
import math
import subprocess
import sys
import tempfile
import urllib.parse
from pathlib import Path

import numpy as np
import pdfplumber
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gk2016_2018_spec import COMMON, PAPERS  # noqa: E402

logging.getLogger("pdfminer").setLevel(logging.ERROR)
OUT = Path(__file__).resolve().parents[1]          # 国考/资料分析
REPO = OUT.parents[1]                              # 仓库根目录
DPI = 288
SCALE = DPI / 72.0
PAD_PX = 6
INK = 240
CN_NUM = "一二三四五六七八九十"


def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, check=True, capture_output=True, text=True).stdout.strip()


def render(pdf: Path, page: int, work: Path) -> Path:
    stem = work / f"{pdf.stem[:8]}-p{page:02d}"
    png = stem.with_suffix(".png")
    if not png.exists():
        subprocess.run(["pdftoppm", "-r", str(DPI), "-png", "-singlefile", "-f", str(page), "-l", str(page),
                        str(pdf), str(stem)], check=True, capture_output=True)
    return png


def page_chars(pdf: Path) -> dict:
    out = {}
    with pdfplumber.open(str(pdf)) as doc:
        for no, pg in enumerate(doc.pages, 1):
            out[no] = [c for c in pg.chars if c["text"] and not c["text"].isspace()]
    return out


def layer_text(chars: list) -> str:
    """一页文字层按行拼接（不留空白），去掉页脚页码。"""
    groups = []
    for c in sorted(chars, key=lambda c: ((c["top"] + c["bottom"]) / 2, c["x0"])):
        vc = (c["top"] + c["bottom"]) / 2
        if groups and abs(vc - groups[-1][0]) <= 3.0:
            groups[-1][1].append(c)
        else:
            groups.append([vc, [c]])
    lines = []
    for vc, cs in groups:
        t = "".join(c["text"] for c in sorted(cs, key=lambda c: c["x0"]))
        if cs[0]["size"] < 9.5 and t.strip("-").isdigit():      # 页脚“-13-”
            continue
        lines.append(t)
    return "".join(lines)


def crop_box(full: Image.Image, box_pt, chars):
    """在搜索范围内收紧到墨迹、留白边、不碰文字；返回像素框。"""
    W, H = full.size
    bx = (max(0, math.floor(box_pt[0] * SCALE)), max(0, math.floor(box_pt[1] * SCALE)),
          min(W, math.ceil(box_pt[2] * SCALE)), min(H, math.ceil(box_pt[3] * SCALE)))
    arr = np.asarray(full.crop(bx).convert("L"))
    ys, xs = np.where(arr < INK)
    if not len(xs):
        raise SystemExit(f"搜索范围内没有墨迹：{box_pt}")
    t = (bx[0] + int(xs.min()), bx[1] + int(ys.min()), bx[0] + int(xs.max()) + 1, bx[1] + int(ys.max()) + 1)
    box = [max(t[0] - PAD_PX, 0), max(t[1] - PAD_PX, 0), min(t[2] + PAD_PX, W), min(t[3] + PAD_PX, H)]
    for c in chars:
        cx0, cy0, cx1, cy1 = c["x0"] * SCALE, c["top"] * SCALE, c["x1"] * SCALE, c["bottom"] * SCALE
        if cx1 <= box[0] or cx0 >= box[2] or cy1 <= box[1] or cy0 >= box[3]:
            continue
        if cy1 <= t[1]:
            box[1] = max(box[1], math.ceil(cy1))
        elif cy0 >= t[3]:
            box[3] = min(box[3], math.floor(cy0))
        elif cx1 <= t[0]:
            box[0] = max(box[0], math.ceil(cx1))
        elif cx0 >= t[2]:
            box[2] = min(box[2], math.floor(cx0))
        else:
            raise SystemExit(f"图表范围内压着正文文字“{c['text']}”：{box_pt}")
    return tuple(int(v) for v in box)


def pages_txt(pages):
    pages = sorted(set(pages))
    if len(pages) == 1:
        return f"第 {pages[0]} 页"
    if pages == list(range(pages[0], pages[-1] + 1)) and len(pages) > 2:
        return f"第 {pages[0]}—{pages[-1]} 页"
    return "第 " + "、".join(str(p) for p in pages) + " 页"


def rel_link(repo_rel: str) -> str:
    """md 里指向原 PDF 的相对链接（自 国考/资料分析/ 起）。"""
    p = Path(repo_rel)
    return "../" + "/".join(urllib.parse.quote(x) for x in p.parts[1:])


def build(pid: str, P: dict, commit: str, work: Path):
    qpdf, apdf = REPO / P["question_pdf"], REPO / P["answer_pdf"]
    for f in (qpdf, apdf):
        if git("rev-parse", f"{commit}:{f.relative_to(REPO)}") != git("hash-object", str(f)):
            raise SystemExit(f"本地文件与提交 {commit[:7]} 中的不一致：{f}")
    chars = page_chars(qpdf)
    a0, a1 = P["q_pages"]
    layer = "".join(layer_text(chars[p]) for p in range(a0, a1 + 1))

    # ---- 文字逐段比对
    def check_text(s, where):
        t = s.replace("\n", "")
        for new, old in P["text_fixes"]:
            t = t.replace(new, old)
        if t not in layer:
            raise SystemExit(f"{pid} {where}：文字与题本文字层不一致：{s[:40]}…")

    for m in P["materials"]:
        for kind, v in m["content"]:
            if kind == "text":
                check_text(v, f"材料{m['k']}")
    for n, q in P["questions"].items():
        check_text(q["stem"], f"第{n}题题干")
        for lab, o in zip("ABCD", q["options"]):
            if isinstance(o, str):
                check_text(lab + "、" + o, f"第{n}题{lab}项")

    # ---- 裁图
    adir = OUT / "assets" / pid
    adir.mkdir(parents=True, exist_ok=True)
    for old in adir.glob(f"{pid}-p*.png"):
        old.unlink()
    manifest, fig = [], {}
    for key in sorted(P["figures"], key=lambda k: (P["figures"][k]["page"], k)):
        F = P["figures"][key]
        full = Image.open(render(qpdf, F["page"], work)).convert("RGB")
        box = crop_box(full, F["box"], chars[F["page"]])
        img_id = f"{pid}-{key}"
        path = f"assets/{pid}/{img_id}.png"
        im = full.crop(box)
        im.save(OUT / path, optimize=True)
        raw = (OUT / path).read_bytes()
        manifest.append({
            "id": img_id, "path": path, "paper_id": pid, "source_page": F["page"],
            "source_bbox_points": [round(v / SCALE, 2) for v in box], "method": "pdf_render_crop",
            "width": im.size[0], "height": im.size[1], "sha256": hashlib.sha256(raw).hexdigest(),
            "transcription": F["transcription"],
        })
        fig[key] = {"type": "image", "image_id": img_id, "path": path, "role": F["role"],
                    "option_label": F.get("option_label"), "method": "pdf_render_crop",
                    "alt": F["alt"], "transcription": F["transcription"]}
    (adir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    # ---- 题目
    mat_of, materials = {}, {}
    for m in P["materials"]:
        mid = f"{pid}-M{m['k']}"
        content = [{"type": "text", "text": v} if kind == "text" else fig[v] for kind, v in m["content"]]
        materials[mid] = {"id": mid, "question_numbers": m["qnums"], "source_pages": m["pages"], "content": content}
        for n in m["qnums"]:
            mat_of[n] = m
    rows = []
    for n in sorted(P["questions"]):
        q = P["questions"][n]
        m = mat_of[n]
        options, figures = [], []
        for lab, o in zip("ABCD", q["options"]):
            if isinstance(o, str):
                options.append({"label": lab, "text": o, "image_refs": []})
            else:
                f = fig[o[1]]
                assert f["option_label"] == lab, (n, lab)
                options.append({"label": lab, "text": "", "image_refs": [{"image_id": f["image_id"], "label_in_image": None}]})
                figures.append(f)
        rows.append({
            "id": f"{pid}-Q{n:03d}", "year": P["year"], "province": COMMON["province"], "exam": COMMON["exam"],
            "subject": COMMON["subject"], "paper_id": pid, "paper_variant": COMMON["paper_variant"],
            "source_edition": COMMON["source_edition"], "question_number": n, "section": "资料分析",
            "question_type": "single_choice", "stem": q["stem"], "options": options, "figures": figures,
            "material": materials[f"{pid}-M{m['k']}"],
            "answer": {"status": "known", "values": [[q["answer"]]], "source_pages": q["answer_pages"], "note": ""},
            "source": {"question_pdf": P["question_pdf"], "question_pages": q["pages"], "answer_pdf": P["answer_pdf"],
                       "repository_commit": commit},
            "notes": list(m["notes"]) + list(q.get("notes", [])),
        })
    with open(OUT / f"{pid}.jsonl", "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    # ---- Markdown
    b0, b1 = P["a_pages"]
    L = [f"# {P['title']}", "",
         "共 20 题（第 111—130 题，原题号保留），4 组材料。内容：材料、题干、选项、答案（不收解析）；共用材料置于所属题组前，"
         "JSONL 每条记录完整内嵌材料。表格、统计图为题本按 288 DPI 渲染后的裁图，图中文字和数字另有转写。", "",
         f"[结构化数据]({pid}.jsonl) · [图片清单](assets/{pid}/manifest.json)", "",
         f"原题来源：[{Path(P['question_pdf']).name}]({rel_link(P['question_pdf'])})（{pages_txt(range(a0, a1 + 1))}）。"
         f"答案来源：[{Path(P['answer_pdf']).name}]({rel_link(P['answer_pdf'])})（{pages_txt(range(b0, b1 + 1))}，只取答案）。", "",
         "## 资料分析", ""]
    for r in rows:
        n = r["question_number"]
        m = mat_of[n]
        mid = r["material"]["id"]
        if n == m["qnums"][0]:
            L += [f'<a id="{mid}"></a>', "", f"### 共用材料：第 {m['qnums'][0]}—{m['qnums'][-1]} 题", ""]
            for b in r["material"]["content"]:
                if b["type"] == "text":
                    L += [b["text"], ""]
                else:
                    L += [f"![{b['alt']}]({b['path']})", ""]
                    if b["transcription"]:
                        L += [b["transcription"], ""]
            for note in m["notes"]:
                L += [f"> 材料说明：{note}", ""]
        L += [f'<a id="{r["id"]}"></a>', "", f"### 第 {n} 题", "",
              f"`{r['id']}` · 单选 · 原卷{pages_txt(r['source']['question_pages'])}", "",
              f"[共用材料](#{mid})", "", r["stem"], ""]
        for f in r["figures"]:
            L += [f"![{f['alt']}]({f['path']})", ""]
        for o in r["options"]:
            if o["text"]:
                L += [f"**{o['label']}.** {o['text']}", ""]
            else:
                L += [f"**{o['label']}.** 见上方题图中 {o['label']} 项。", ""]
        L += [f"**答案：{r['answer']['values'][0][0]}**", ""]
        for note in P["questions"][n].get("notes", []):
            L += [f"> 转写说明：{note}", ""]
    (OUT / f"{pid}.md").write_text("\n".join(L).rstrip() + "\n", encoding="utf-8")
    return rows, manifest


def main():
    commit = git("rev-parse", "HEAD")
    with tempfile.TemporaryDirectory() as tmp:
        for pid, P in PAPERS.items():
            rows, manifest = build(pid, P, commit, Path(tmp))
            print(f"{pid}: {len(rows)} 题，{len({r['material']['id'] for r in rows})} 组材料，{len(manifest)} 张图")


if __name__ == "__main__":
    main()

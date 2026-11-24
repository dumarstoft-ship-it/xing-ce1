#!/usr/bin/env python3
"""综合推理精选本构建脚本。

python3 build.py <原书PDF> <selection.json> <records.json> <输出PDF> [--work DIR]

- 题页从原书 PDF 原样抽取（练习页＋解析页），只改两处：右下角页码换成新页码
  （同一字体、同一位置），练习页右上角加“精选 n / N”标签。
- 原书内部链接（分类目录、索引）在新书中失效，全部删去；指向仓库原卷与参考解析的
  外部链接保留。页脚“分类目录”重新指向本书目录。
- 导读、目录、附录用 Chromium 由 HTML 排版，字体 Noto Sans CJK SC。
"""
import argparse, html, json, os, re, subprocess, sys
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Link
from pypdf.generic import ArrayObject, NameObject, DecodedStreamObject

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE_W, PAGE_H = 595.2756, 841.8898
DIGIT_W = 4.986          # 原书页码字体 9pt 每位数字宽度
PNUM_RE = re.compile(rb"BT 1 0 0 1 ([\d.]+) 27 Tm /F3\+0 9 Tf 10\.8 TL \((\d+)\) Tj T\* ET")

E = lambda s: html.escape(str(s), quote=True)

CSS = r"""
@page { size: 595.28pt 841.89pt; margin: 0 }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body { font-family: "JX"; font-weight: 300; color: #192E32;
       -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.page { width: 595.28pt; height: 841.89pt; position: relative; overflow: hidden;
        page-break-after: always; break-after: page; background: #fff; }
.page:last-child { page-break-after: auto; break-after: auto; }
.hd-l { position: absolute; left: 48pt; top: 32.8pt; font: 500 10pt/14pt "JX"; color: #08635F; letter-spacing: .3pt; }
.hd-r { position: absolute; right: 48.28pt; top: 32.8pt; font: 300 10pt/14pt "JX"; color: #50656A; }
.rule-t { position: absolute; left: 48pt; width: 499.28pt; top: 54.7pt; border-top: .65pt solid #D2DDDB; }
.rule-b { position: absolute; left: 48pt; width: 499.28pt; top: 796.7pt; border-top: .65pt solid #D2DDDB; }
.ft-l { position: absolute; left: 48pt; top: 805.4pt; font: 300 9pt/13pt "JX"; color: #08635F; }
.ft-r { position: absolute; right: 48.28pt; top: 805.4pt; font: 300 9pt/13pt "JX"; color: #50656A; }
.fit { position: absolute; left: 48pt; width: 499.28pt; top: 66pt; height: 722pt; overflow: hidden; }
a { color: inherit; text-decoration: none; }
.teal { color: #08635F; } .muted { color: #50656A; } .med { font-weight: 500; }
h1 { font-weight: 500; font-size: 25pt; line-height: 34pt; margin: 8pt 0 6pt; color: #192E32; letter-spacing: .5pt; }
.sub { font-weight: 500; font-size: 13pt; line-height: 20pt; color: #08635F; margin: 0 0 12pt; }
p { font-size: 10.8pt; line-height: 19pt; margin: 0 0 8pt; text-align: justify; }
.lead { font-size: 11.2pt; line-height: 20pt; color: #50656A; }
h2 { font-weight: 500; font-size: 13pt; line-height: 18pt; color: #08635F; margin: 16pt 0 6pt; }
h2:first-child { margin-top: 2pt; }
.box { border: .5pt solid #A7B8B5; background: #F6FAF9; padding: 9pt 12pt; margin: 6pt 0 10pt; }
.box p:last-child { margin-bottom: 0; }
ul.plain { list-style: none; padding: 0; margin: 0 0 8pt; }
ul.plain li { font-size: 10.8pt; line-height: 19pt; padding-left: 14pt; position: relative; }
ul.plain li::before { content: "·"; position: absolute; left: 3pt; color: #08635F; font-weight: 500; }
/* 目录 */
.toc-mod { display: flex; justify-content: space-between; align-items: baseline; font-weight: 500;
           font-size: 13pt; line-height: 18pt; color: #08635F; margin: 12pt 0 2pt; padding-bottom: 5pt;
           border-bottom: .65pt solid #A7B8B5; }
.toc-mod:first-child { margin-top: 0; }
.toc-row { border-bottom: .65pt solid #D2DDDB; padding: 5.5pt 2pt 5.5pt 2pt; }
.toc-line { display: flex; justify-content: space-between; align-items: baseline; }
.toc-name { font-size: 11.2pt; line-height: 16pt; }
.toc-pg { font-size: 10.5pt; font-weight: 500; color: #08635F; }
.chips { font-size: 9.2pt; line-height: 14pt; color: #50656A; margin-top: 1.5pt; }
.chip { color: #08635F; margin-right: 7pt; white-space: nowrap; }
.chip.adv { color: #50656A; }
/* 模块导读 */
.modno { font-weight: 500; font-size: 11pt; color: #08635F; letter-spacing: 1pt; margin-top: 4pt; }
.card { border-top: .65pt solid #D2DDDB; padding: 6.5pt 0 5.5pt; }
.card h3 { margin: 0 0 2pt; font-weight: 500; font-size: 12pt; line-height: 16pt; color: #08635F; }
.card h3 .no { color: #50656A; font-weight: 300; margin-right: 6pt; }
.kv { display: grid; grid-template-columns: 40pt 1fr; column-gap: 6pt; row-gap: 1pt; }
.kv .k { font-size: 9.3pt; line-height: 15.6pt; font-weight: 500; color: #50656A; }
.kv .v { font-size: 10pt; line-height: 15.6pt; text-align: justify; }
.qlist { width: 100%; border-collapse: collapse; margin-top: 2pt; }
.qlist th { font-weight: 500; font-size: 9.6pt; color: #08635F; background: #EEF4F2; text-align: left;
            padding: 4pt 5pt; border-top: .5pt solid #A7B8B5; border-bottom: .5pt solid #A7B8B5; }
.qlist td { font-size: 9.8pt; line-height: 14pt; padding: 4.2pt 5pt; border-bottom: .5pt solid #D2DDDB; vertical-align: top; }
.qlist td.n { color: #08635F; font-weight: 500; white-space: nowrap; }
.qlist td.p { text-align: right; color: #08635F; white-space: nowrap; }
.tier { display: inline-block; font-size: 8.4pt; line-height: 12pt; padding: 0 4pt; border-radius: 2pt;
        border: .5pt solid #08635F; color: #08635F; }
.tier.adv { border-color: #A7B8B5; color: #50656A; }
.tier.trap { border-color: #B5651D; color: #8A4B12; }
.flowcol { display: flex; flex-direction: column; height: 100%; }
.notes { flex: 1 1 auto; min-height: 0; overflow: hidden; margin-top: 12pt; border-top: .65pt solid #A7B8B5;
         background-image: repeating-linear-gradient(to bottom, transparent 0, transparent 25.5pt, #D2DDDB 25.5pt, #D2DDDB 26pt);
         background-position: 0 22pt; }
.notes .nt { font-size: 9.6pt; line-height: 22pt; color: #50656A; background: #fff; }
.qchip { display: inline-block; margin: 0 9pt 0 0; white-space: nowrap; color: #08635F; font-size: 9.6pt; }
.qchip b { font-weight: 500; }
.qchip i { font-style: normal; font-size: 8pt; margin-left: 3pt; padding: 0 3pt; border: .5pt solid #08635F; border-radius: 2pt; }
.qchip.adv { color: #50656A; } .qchip.adv i { border-color: #A7B8B5; }
.qchip.trap { color: #8A4B12; } .qchip.trap i { border-color: #B5651D; }
.backup { font-size: 9.8pt; line-height: 16pt; color: #50656A; }
"""

def shell(page_no, hd_right, body, footer_label="目录", body_id=""):
    return (f'<div class="page"><div class="hd-l">综合推理 / 精选本</div>'
            f'<div class="hd-r">{E(hd_right)}</div><div class="rule-t"></div>'
            f'<div class="fit" id="{E(body_id)}">{body}</div>'
            f'<div class="rule-b"></div><a class="ft-l" data-link="toc">{E(footer_label)}</a>'
            f'<div class="ft-r">{page_no}</div></div>')

def tier_badge(t):
    cls = {"核心": "", "进阶": " adv", "避坑": " trap"}.get(t, " adv")
    return f'<span class="tier{cls}">{E(t)}</span>'

def short_src(s, n=26):
    s = re.sub(r"《[^》]*》", "", s)
    s = re.sub(r"（[^）]*）", "", s)
    s = re.sub(r"广东省(?!考)", "广东", s).replace("公开招聘", "").replace("工作人员", "")
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[:n - 1] + "…"

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        raise SystemExit(f"command failed: {' '.join(cmd)}")
    return r

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src_pdf"); ap.add_argument("selection"); ap.add_argument("records"); ap.add_argument("out_pdf")
    ap.add_argument("--work", default=os.path.join(HERE, "_work"))
    a = ap.parse_args()
    os.makedirs(a.work, exist_ok=True)
    sel = json.load(open(a.selection))
    recs = {r["idx"]: r for r in json.load(open(a.records))}
    import pages as P                      # 页面内容（同目录 pages.py）
    counts = P.default_counts(sel)
    for attempt in range(12):
        plan = P.plan_pages(sel, recs, counts)
        res = render_generated(a, plan, sel, recs, P)
        if res["ok"]: break
        grow = set()
        for o in res["overflow"]:
            name = o["id"].split("-")[0]
            if name in counts: grow.add(name)
            else: raise SystemExit(f"第 {o['page']+1} 个生成页内容溢出：{o}")
        for name in grow:
            counts[name] += 2 if name.startswith("m") else 1
        print("加页重排：", {k: counts[k] for k in grow})
    else:
        raise SystemExit("多次加页仍然溢出")
    seq, gen_specs, pageno, meta, gen_pdf = res["seq"], res["gen_specs"], res["pageno"], res["meta"], res["gen_pdf"]
    total = res["total"]; qids = res["qids"]
    ov_pdf = render_overlay(a, qids)
    finish(a, sel, recs, P, seq, gen_specs, pageno, meta, gen_pdf, ov_pdf, qids, total)

def render_generated(a, plan, sel, recs, P):
    # ---------- 1. 计算页码 ----------
    seq = []          # 最终顺序：("gen", k) 生成页 / ("q", idx, "practice"|"solution")
    gen_specs = []    # 生成页的 builder，按出现顺序
    for item in plan:
        if item[0] == "gen":
            seq.append(("gen", len(gen_specs))); gen_specs.append(item[1])
        else:
            _, idx = item
            seq.append(("q", idx, "practice")); seq.append(("q", idx, "solution"))
    pageno = {}       # 键 -> 1 起页码
    for i, s in enumerate(seq):
        if s[0] == "q" and s[2] == "practice": pageno[f"q:{s[1]}"] = i + 1
        if s[0] == "q": assert (i + 1) % 2 == (1 if s[2] == "practice" else 0), f"双面奇偶错位：{s} 在第 {i+1} 页"
    for i, s in enumerate(seq):
        if s[0] == "gen":
            for key in gen_specs[s[1]].get("keys", []): pageno.setdefault(key, i + 1)
    gen_pageno = [i + 1 for i, s in enumerate(seq) if s[0] == "gen"]
    # ---------- 2. 排生成页 ----------
    body = "".join(spec["build"](gen_pageno[k], pageno) for k, spec in enumerate(gen_specs))
    from fonts import build_fonts
    plain = html.unescape(re.sub(r"<[^>]+>", "", body)) + "精选 0123456789 / " + CSS
    fp = build_fonts(plain, os.path.join(a.work, "fonts"))
    global FONT_FACE
    FONT_FACE = "".join(f'@font-face {{ font-family: "JX"; src: url("file://{os.path.abspath(p)}"); font-weight: {w}; }}'
                        for w, p in fp.items())
    html_doc = f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><style>{FONT_FACE}{CSS}</style></head><body>{body}</body></html>'
    gen_html = os.path.join(a.work, "generated.html"); open(gen_html, "w").write(html_doc)
    gen_pdf = os.path.join(a.work, "generated.pdf"); gen_meta = os.path.join(a.work, "generated.json")
    r = subprocess.run(["node", os.path.join(HERE, "render.js"), gen_html, gen_pdf, gen_meta], capture_output=True, text=True)
    meta = json.load(open(gen_meta)) if os.path.exists(gen_meta) else None
    if r.returncode == 3 and meta:
        return {"ok": False, "overflow": meta["overflow"]}
    if r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr); raise SystemExit("渲染失败")
    assert meta["pageCount"] == len(gen_specs), (meta["pageCount"], len(gen_specs))
    qids = [s[1] for s in seq if s[0] == "q" and s[2] == "practice"]
    return {"ok": True, "seq": seq, "gen_specs": gen_specs, "pageno": pageno, "meta": meta, "gen_pdf": gen_pdf,
            "qids": qids, "total": len(qids)}

def render_overlay(a, qids):
    total = len(qids)
    ov = []
    for n, idx in enumerate(qids, 1):
        ov.append(f'<div class="page" style="background:transparent"><div class="tag">精选 {n:02d} / {total}</div></div>')
    ov_css = CSS + ('.tag { position: absolute; right: 48.28pt; top: 80pt; font: 500 11pt/14pt "JX";'
                    ' color: #08635F; letter-spacing: .5pt; } .page { background: transparent !important; }')
    ov_html = os.path.join(a.work, "overlay.html")
    open(ov_html, "w").write(f'<!doctype html><html><head><meta charset="utf-8"><style>{FONT_FACE}{ov_css}</style></head><body>{"".join(ov)}</body></html>')
    ov_pdf = os.path.join(a.work, "overlay.pdf"); ov_meta = os.path.join(a.work, "overlay.json")
    run(["node", os.path.join(HERE, "render.js"), ov_html, ov_pdf, ov_meta])
    return ov_pdf

def finish(a, sel, recs, P, seq, gen_specs, pageno, meta, gen_pdf, ov_pdf, qids, total):
    # ---------- 4. 拼合 ----------
    src = PdfReader(a.src_pdf); gen = PdfReader(gen_pdf); ovr = PdfReader(ov_pdf)
    w = PdfWriter()
    qn = 0
    for i, s in enumerate(seq):
        newno = i + 1
        if s[0] == "gen":
            w.add_page(gen.pages[s[1]])
            continue
        idx, kind = s[1], s[2]
        r = recs[idx]
        sp = r["page"] if kind == "practice" else r["spage"]       # 1 起
        page = src.pages[sp - 1]
        annots = page.get("/Annots")
        keep = ArrayObject()
        if annots:
            for an in annots:
                o = an.get_object(); act = o.get("/A")
                if act is not None and act.get_object().get("/S") == "/URI":
                    keep.append(an)
        page[NameObject("/Annots")] = keep
        wp = w.add_page(page)
        data = wp.get_contents().get_data()
        ms = [m for m in PNUM_RE.finditer(data) if int(m.group(2)) == sp]
        assert len(ms) == 1, f"第 {sp} 页页码定位失败"
        m = ms[0]
        digits = str(newno).encode()
        x = PAGE_W - 48 - DIGIT_W * len(digits)
        new_op = b"BT 1 0 0 1 %.4f 27 Tm /F3+0 9 Tf 10.8 TL (%s) Tj T* ET" % (x, digits)
        data = data[:m.start()] + new_op + data[m.end():]
        st = DecodedStreamObject(); st.set_data(data)
        wp[NameObject("/Contents")] = w._add_object(st)
        if kind == "practice":
            wp.merge_page(ovr.pages[qn]); qn += 1
    # ---------- 5. 链接 ----------
    toc_index = pageno["toc"] - 1
    def target_index(t):
        if t not in pageno: raise SystemExit(f"未知链接目标 {t}")
        return pageno[t] - 1
    gen_pos = [i for i, s in enumerate(seq) if s[0] == "gen"]
    for L in meta["links"]:
        pi = gen_pos[L["page"]]
        rect = (L["x0"], PAGE_H - L["bottom"], L["x1"], PAGE_H - L["top"])
        w.add_annotation(page_number=pi, annotation=Link(rect=rect, target_page_index=target_index(L["target"]), border=[0, 0, 0]))
    for i, s in enumerate(seq):
        if s[0] == "q":
            w.add_annotation(page_number=i, annotation=Link(rect=(48, 19, 114, 42), target_page_index=toc_index, border=[0, 0, 0]))
    # ---------- 6. 书签 ----------
    P.add_outline(w, sel, recs, pageno)
    w.add_metadata({"/Title": sel["title"], "/Subject": sel.get("subject", ""), "/Author": "公考真题练习"})
    w.page_mode = "/UseOutlines"
    with open(a.out_pdf, "wb") as f: w.write(f)
    json.dump({"pages": len(seq), "pageno": pageno, "questions": qids}, open(os.path.join(a.work, "layout.json"), "w"), ensure_ascii=False, indent=1)
    print(f"写出 {a.out_pdf}：{len(seq)} 页，{total} 题")

if __name__ == "__main__":
    sys.path.insert(0, HERE)
    main()

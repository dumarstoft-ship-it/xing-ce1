#!/usr/bin/env python3
"""数字推理精选本构建：python3 build_sx.py <原书PDF> <selection.json> <records.json> <models.json> <输出PDF> [--work DIR]

题块用 pdftocairo 从原书矢量裁出（只含该题内容与文字），贴到 HTML 排好的框架页上；
练习块在正面、同一组题的解析块在背面。真题出处链接平移后保留，“回练”改指本册页码。
"""
import argparse, html, json, os, re, subprocess, sys, unicodedata
from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.annotations import Link
from pypdf.generic import NameObject, DecodedStreamObject

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import CSS, PAGE_H, PAGE_W
from cliptools import crop
import pages_sx as P

RAD_EXTRA = {0x2EDA: "页", 0x2ED3: "长", 0x2EDB: "风", 0x2ED4: "长", 0x2ECD: "辶", 0x2EC4: "西", 0x2EC6: "角", 0x2EC5: "见",
             0x2EE0: "飞", 0x2EE2: "马", 0x2EA0: "民", 0x2EAA: "疋", 0x2EAE: "竹", 0x2EB6: "羊", 0x2EB7: "羊", 0x2EBC: "肉",
             0x2EC0: "艹", 0x2EC1: "虎", 0x2EC9: "贝", 0x2ECB: "车", 0x2ED1: "长", 0x2ED7: "雨", 0x2EDD: "食", 0x2EDE: "食",
             0x2EE5: "鱼", 0x2EE9: "黄", 0x2EEC: "齐", 0x2EF0: "龙", 0x2EF3: "龟", 0x2E8C: "小", 0x2E97: "幺", 0x2E9F: "母", 0x2E8E: "兀"}

def unrad(cp):
    if cp in RAD_EXTRA: return ord(RAD_EXTRA[cp])
    if 0x2E80 <= cp <= 0x2FDF:
        n = unicodedata.normalize("NFKC", chr(cp))
        if len(n) == 1 and n != chr(cp): return ord(n)
    return cp

def fix_tounicode(writer):
    """把文字层里的康熙部首、部首补充码位改回标准汉字。"""
    seen, changed = set(), 0
    def fix_cmap(stream):
        nonlocal changed
        data = stream.get_data().decode("latin-1")
        def rep(m):
            nonlocal changed
            hx = m.group(1)
            if len(hx) == 4:
                cp = int(hx, 16); nc = unrad(cp)
                if nc != cp:
                    changed += 1; return f"<{nc:04X}>"
            return m.group(0)
        out = []
        for block in re.split(r"(beginbfchar.*?endbfchar|beginbfrange.*?endbfrange)", data, flags=re.S):
            if block.startswith("beginbfchar"):
                block = re.sub(r"(<[0-9A-Fa-f]+>\s*)<([0-9A-Fa-f]{4})>", lambda m: m.group(1) + rep(re.match(r"<(\w+)>", "<" + m.group(2) + ">")), block)
            elif block.startswith("beginbfrange"):
                lines = []
                for line in block.split("\n"):
                    m = re.match(r"\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]{4})>\s*$", line)
                    if m:
                        lo, hi, dst = int(m.group(1), 16), int(m.group(2), 16), int(m.group(3), 16)
                        if any(unrad(dst + i) != dst + i for i in range(hi - lo + 1)):
                            w = len(m.group(1))
                            lines.append(f"{hi - lo + 1} beginbfchar")
                            for i in range(hi - lo + 1):
                                lines.append(f"<{lo + i:0{w}X}> <{unrad(dst + i):04X}>")
                            lines.append("endbfchar")
                            changed += 1
                            continue
                    lines.append(line)
                block = "\n".join(lines)
                # 拆出来的 bfchar 不能嵌在 bfrange 段里：把段落重排
                if "beginbfchar" in block:
                    ranges = [l for l in block.split("\n") if re.match(r"\s*<\w+>\s*<\w+>\s*<\w+>\s*$", l)]
                    chars = re.findall(r"\d+ beginbfchar\n(.*?)\nendbfchar", block, flags=re.S)
                    pieces = []
                    if ranges: pieces.append(f"{len(ranges)} beginbfrange\n" + "\n".join(ranges) + "\nendbfrange")
                    for c in chars:
                        n = len(c.split("\n")); pieces.append(f"{n} beginbfchar\n{c}\nendbfchar")
                    block = "\n".join(pieces)
            out.append(block)
        new = "".join(out)
        new = re.sub(r"\d+\s+(beginbfrange|beginbfchar)", lambda m: m.group(0), new)
        st = DecodedStreamObject(); st.set_data(new.encode("latin-1"))
        return st
    def walk_fonts(res):
        if res is None: return
        res = res.get_object()
        fonts = res.get("/Font")
        if fonts:
            for k, f in fonts.get_object().items():
                fo = f.get_object()
                tu = fo.get("/ToUnicode")
                if tu is not None and id(tu.get_object()) not in seen:
                    seen.add(id(tu.get_object()))
                    fo[NameObject("/ToUnicode")] = writer._add_object(fix_cmap(tu.get_object()))
                if fo.get("/Resources") is not None: walk_fonts(fo["/Resources"])
        xo = res.get("/XObject")
        if xo:
            for k, x in xo.get_object().items():
                xo2 = x.get_object()
                if xo2.get("/Resources") is not None: walk_fonts(xo2["/Resources"])
    for page in writer.pages:
        walk_fonts(page.get("/Resources"))
    return changed

def shrink(path):
    """每个裁切块各带一份 Type3 字形。写出后重新读入：压缩未压缩的流，合并内容相同的对象。
    （直接在拼合用的 writer 上做会弄乱字体的 ToUnicode，所以放在写出之后。）"""
    from pypdf.generic import StreamObject
    w = PdfWriter(clone_from=path)
    for i, obj in enumerate(w._objects):
        if isinstance(obj, StreamObject) and "/Filter" not in obj:
            enc = obj.flate_encode(); enc.indirect_reference = obj.indirect_reference; w._objects[i] = enc
    w.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)
    tmp = path + ".tmp"
    with open(tmp, "wb") as f: w.write(f)
    os.replace(tmp, path)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src_pdf"); ap.add_argument("selection"); ap.add_argument("records"); ap.add_argument("models"); ap.add_argument("out_pdf")
    ap.add_argument("--work", default=os.path.join(HERE, "_work"))
    a = ap.parse_args()
    os.makedirs(os.path.join(a.work, "clips"), exist_ok=True)
    sel = json.load(open(a.selection))
    recs = {r["id"]: r for r in json.load(open(a.records))}
    models = {m["id"]: m for m in json.load(open(a.models))}
    in_book = {g["id"] for mod in sel["modules"] for g in mod["groups"] if g.get("id")}
    # 1. 裁题块
    info = {}
    for _, mod, g, q in P.all_questions(sel):
        r = recs[q["id"]]; safe = q["id"].replace("/", "_")
        qp, hq = crop(a.src_pdf, r["page"], r["bbox"][1], r["bbox"][3], os.path.join(a.work, "clips", f"{safe}_q.pdf"))
        sb = r["sbbox"][3] if not r.get("sback_top") else r["sback_top"] - 2
        sp, hs = crop(a.src_pdf, r["spage"], r["sbbox"][1], sb, os.path.join(a.work, "clips", f"{safe}_s.pdf"))
        d = {"qp": qp, "hq": hq, "sp": sp, "hs": hs, "qtop": int(r["bbox"][1]), "stop": int(r["sbbox"][1])}
        ref = q.get("back_ref") or r.get("back_ref")
        if mod.get("kind") == "blind" and ref:
            if ref in in_book:
                d["br"] = {"text": f'{ref} {models[ref]["title"]}' if ref in models else ref, "link": f"group:{ref}"}
            elif ref in models:
                d["br"] = {"text": f'{ref} {models[ref]["title"]}', "where": f'原书第{models[ref]["pages"][0]}页'}
            elif ref == "基础":
                d["br"] = {"text": "基础步长与公比", "where": "原书第95页"}
        info[q["id"]] = d
    # 2. 规划并渲染（流式分页不够时加页）
    counts = {"toc": 2, "app": 3}
    for mi, _ in enumerate(sel["modules"]): counts[f"m{mi+1}"] = 2
    for attempt in range(12):
        pages, seqno, total = P.plan(sel, recs, info, counts)
        pageno = {}
        for i, pg in enumerate(pages):
            for k in pg["keys"]: pageno.setdefault(k, i + 1)
            if pg["kind"] == "front": assert (i + 1) % 2 == 1, f"练习页落在偶数页 {i+1}"
        body = "".join(pg["build"](i + 1, pageno) for i, pg in enumerate(pages))
        from fonts import build_fonts
        plain = html.unescape(re.sub(r"<[^>]+>", "", body)) + "0123456789 / " + CSS
        fp = build_fonts(plain, os.path.join(a.work, "fonts"))
        ff = "".join(f'@font-face {{ font-family: "JX"; src: url("file://{os.path.abspath(p)}"); font-weight: {w}; }}' for w, p in fp.items())
        doc = f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><style>{ff}{CSS}</style></head><body>{body}</body></html>'
        gh = os.path.join(a.work, "gen.html"); gp = os.path.join(a.work, "gen.pdf"); gm = os.path.join(a.work, "gen.json")
        open(gh, "w").write(doc)
        r = subprocess.run(["node", os.path.join(HERE, "render.js"), gh, gp, gm], capture_output=True, text=True)
        meta = json.load(open(gm)) if os.path.exists(gm) else None
        if r.returncode == 3 and meta:
            grow = set()
            for o in meta["overflow"]:
                name = o["id"].split("-")[0]
                if name not in counts: raise SystemExit(f"生成页溢出：{o}")
                grow.add(name)
            for name in grow: counts[name] += 2 if name.startswith("m") else 1
            print("加页重排：", {k: counts[k] for k in grow}); continue
        if r.returncode != 0:
            sys.stderr.write(r.stdout + r.stderr); raise SystemExit("渲染失败")
        break
    else:
        raise SystemExit("多次加页仍然溢出")
    assert meta["pageCount"] == len(pages)
    # 3. 拼合
    gen = PdfReader(gp); src = PdfReader(a.src_pdf)
    w = PdfWriter()
    uri_adds = []
    for i, pg in enumerate(pages):
        wp = w.add_page(gen.pages[i])
        for st in pg["stamps"]:
            d = info[st["id"]]; path = d["qp"] if st["which"] == "q" else d["sp"]
            h = d["hq"] if st["which"] == "q" else d["hs"]
            clip = PdfReader(path).pages[0]
            wp.merge_transformed_page(clip, Transformation().translate(0, PAGE_H - st["top"] - h))
            rr = recs[st["id"]]
            sp_no = rr["page"] if st["which"] == "q" else rr["spage"]
            ctop = d["qtop"] if st["which"] == "q" else d["stop"]
            srcp = src.pages[sp_no - 1]; SH = float(srcp.mediabox.height)
            for an in srcp.get("/Annots") or []:
                o = an.get_object(); act = o.get("/A")
                if act is None or act.get_object().get("/S") != "/URI": continue
                x0, y0, x1, y1 = [float(v) for v in o["/Rect"]]
                atop, abot = SH - y1, SH - y0
                if atop >= ctop - 1 and abot <= ctop + h + 1:
                    ntop = st["top"] + (atop - ctop); nbot = st["top"] + (abot - ctop)
                    uri_adds.append((i, (x0, PAGE_H - nbot, x1, PAGE_H - ntop), str(act.get_object()["/URI"])))
    for L in meta["links"]:
        t = L["target"]
        if t not in pageno: raise SystemExit(f"未知链接目标 {t}")
        w.add_annotation(page_number=L["page"], annotation=Link(rect=(L["x0"], PAGE_H - L["bottom"], L["x1"], PAGE_H - L["top"]),
                                                                target_page_index=pageno[t] - 1, border=[0, 0, 0]))
    for i, rect, url in uri_adds:
        w.add_annotation(page_number=i, annotation=Link(rect=rect, url=url, border=[0, 0, 0]))
    # 4. 书签
    w.add_outline_item("封面与说明", pageno["cover"] - 1); w.add_outline_item("认知地图", pageno["map"] - 1)
    w.add_outline_item("目录", pageno["toc"] - 1)
    for mi, mod in enumerate(sel["modules"]):
        top = w.add_outline_item(f'模块 {mod["no"]} · {mod["name"]}', pageno[f"mod:{mi+1}"] - 1)
        for g in mod["groups"]:
            gi = w.add_outline_item(f'{g.get("id", "")} {g["name"]}'.strip(), pageno[f'q:{g["questions"][0]["id"]}'] - 1, parent=top)
            for q in g["questions"]:
                w.add_outline_item(f'精选{seqno[q["id"]]:02d} · {q["id"]} · {recs[q["id"]]["source"][:22]}', pageno[f'q:{q["id"]}'] - 1, parent=gi)
    w.add_outline_item("附录 · 首式速查", pageno["app"] - 1); w.add_outline_item("选题说明", pageno["cut"] - 1)
    w.page_mode = "/UseOutlines"
    n = fix_tounicode(w)
    w.add_metadata({"/Title": sel["title"], "/Subject": sel.get("subject", ""), "/Author": "数字推理专项训练"})
    with open(a.out_pdf, "wb") as f: w.write(f)
    shrink(a.out_pdf)
    json.dump({"pages": len(pages), "pageno": pageno, "seqno": seqno, "kinds": [p["kind"] for p in pages]},
              open(os.path.join(a.work, "layout.json"), "w"), ensure_ascii=False, indent=1)
    print(f"写出 {a.out_pdf}：{len(pages)} 页，{total} 题；文字层修正 {n} 处部首码位")

if __name__ == "__main__":
    main()

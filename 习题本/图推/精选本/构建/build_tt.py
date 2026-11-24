#!/usr/bin/env python3
"""图形推理精选本构建：python3 build_tt.py <178题PDF> <200题PDF> <selection.json> <records.json> <输出PDF> [--work DIR]

题块与解析块用 pdftocairo 从两本原书矢量裁出，贴到 HTML 排好的框架页上。
题型训练模块题后即看答案；限时组先排题、后排答案。
"""
import argparse, html, json, os, re, subprocess, sys, unicodedata
from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.annotations import Link
from pypdf.generic import NameObject, DecodedStreamObject

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import CSS, PAGE_H, PAGE_W
from cliptools import crop
import pages_tt as P

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
    ap.add_argument("pdf178"); ap.add_argument("pdf200"); ap.add_argument("selection"); ap.add_argument("records"); ap.add_argument("out_pdf")
    ap.add_argument("--work", default=os.path.join(HERE, "_work"))
    a = ap.parse_args()
    os.makedirs(os.path.join(a.work, "clips"), exist_ok=True)
    sel = json.load(open(a.selection)); recs = {r["id"]: r for r in json.load(open(a.records))}
    src_of = lambda qid: a.pdf178 if qid[0] == "S" else a.pdf200
    info = {}
    for _, mod, g, q in P.all_questions(sel):
        r = recs[q["id"]]
        qp, hq = crop(src_of(q["id"]), r["page"], r["q_top"], r["q_bottom"], os.path.join(a.work, "clips", f'{q["id"]}_q.pdf'))
        sp, hs = crop(src_of(q["id"]), r["page"], r["a_top"], r["a_bottom"], os.path.join(a.work, "clips", f'{q["id"]}_s.pdf'))
        info[q["id"]] = {"qp": qp, "hq": hq, "sp": sp, "hs": hs}
    counts = {"toc": 3, "app": 6, "map": 1, "cut": 1}
    for mi, _ in enumerate(sel["modules"]): counts[f"m{mi+1}"] = 1
    for attempt in range(16):
        pages, seqno, total = P.plan(sel, recs, info, counts)
        pageno = {}
        for i, pg in enumerate(pages):
            for k in pg["keys"]: pageno.setdefault(k, i + 1)
        body = "".join(pg["build"](i + 1, pageno) for i, pg in enumerate(pages))
        from fonts import build_fonts
        plain = html.unescape(re.sub(r"<[^>]+>", "", body)) + "0123456789 / " + CSS
        fp = build_fonts(plain, os.path.join(a.work, "fonts"))
        ff = "".join(f'@font-face {{ font-family: "JX"; src: url("file://{os.path.abspath(p)}"); font-weight: {w}; }}' for w, p in fp.items())
        doc = f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><style>{ff}{CSS}</style></head><body>{body}</body></html>'
        gh = os.path.join(a.work, "gen.html"); gp = os.path.join(a.work, "gen.pdf"); gm = os.path.join(a.work, "gen.json")
        open(gh, "w").write(doc)
        rr = subprocess.run(["node", os.path.join(HERE, "render.js"), gh, gp, gm], capture_output=True, text=True)
        meta = json.load(open(gm)) if os.path.exists(gm) else None
        if rr.returncode == 3 and meta:
            grow = {}
            for o in meta["overflow"]:
                name = o["id"].split("-")[0]
                if name not in counts: raise SystemExit(f"生成页溢出：{o}")
                # 按最后一页溢出的高度估计还差几页，一次加够
                need = max(1, -(-(o["sh"] - o["ch"]) // max(1, o["ch"])))
                grow[name] = max(grow.get(name, 0), need)
            for name, n in grow.items(): counts[name] += n
            print("加页重排：", {k: counts[k] for k in grow}); continue
        if rr.returncode != 0:
            sys.stderr.write(rr.stdout + rr.stderr); raise SystemExit("渲染失败")
        break
    else:
        raise SystemExit("多次加页仍然溢出")
    assert meta["pageCount"] == len(pages)
    gen = PdfReader(gp); w = PdfWriter()
    for i, pg in enumerate(pages):
        wp = w.add_page(gen.pages[i])
        for st in pg["stamps"]:
            d = info[st["id"]]; path = d["qp"] if st["which"] == "q" else d["sp"]
            h = d["hq"] if st["which"] == "q" else d["hs"]
            s = st.get("scale", 1.0)
            clip = PdfReader(path).pages[0]
            cw = float(clip.mediabox.width)
            tx = (PAGE_W - cw * s) / 2
            wp.merge_transformed_page(clip, Transformation().scale(s).translate(tx, PAGE_H - st["top"] - h * s))
    for L in meta["links"]:
        t = L["target"]
        if t not in pageno: raise SystemExit(f"未知链接目标 {t}")
        w.add_annotation(page_number=L["page"], annotation=Link(rect=(L["x0"], PAGE_H - L["bottom"], L["x1"], PAGE_H - L["top"]),
                                                                target_page_index=pageno[t] - 1, border=[0, 0, 0]))
    w.add_outline_item("封面与说明", pageno["cover"] - 1); w.add_outline_item("认知地图", pageno["map"] - 1)
    w.add_outline_item("目录", pageno["toc"] - 1)
    for mi, mod in enumerate(sel["modules"]):
        top = w.add_outline_item(f'{mod["no"]} · {mod["name"]}', pageno[f"mod:{mi+1}"] - 1)
        for g in mod["groups"]:
            gi = w.add_outline_item(f'{g.get("no", "")} {g["name"]}'.strip(), pageno[f'q:{g["questions"][0]["id"]}'] - 1, parent=top)
            for q in g["questions"]:
                w.add_outline_item(f'{seqno[q["id"]]:03d} · {q["id"]} · {P.src_label(recs[q["id"]])[:24]}', pageno[f'q:{q["id"]}'] - 1, parent=gi)
    w.add_outline_item("附录 · 最快路径速查", pageno["app"] - 1)
    w.add_outline_item("选题说明", pageno["cut"] - 1)
    w.page_mode = "/UseOutlines"
    n = fix_tounicode(w)
    w.add_metadata({"/Title": sel["title"], "/Subject": sel.get("subject", ""), "/Author": "图推专项训练"})
    with open(a.out_pdf, "wb") as f: w.write(f)
    shrink(a.out_pdf)
    json.dump({"pages": len(pages), "pageno": pageno, "seqno": seqno, "kinds": [p["kind"] for p in pages]},
              open(os.path.join(a.work, "layout.json"), "w"), ensure_ascii=False, indent=1)
    print(f"写出 {a.out_pdf}：{len(pages)} 页，{total} 题；文字层修正 {n} 处部首码位")

if __name__ == "__main__":
    main()

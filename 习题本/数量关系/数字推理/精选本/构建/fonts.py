"""从系统 Noto Sans CJK 集合中取出简体中文字面，按用到的字子集化并转成 TrueType 轮廓。

Chromium 对 TTC 里的 CFF 字体只能输出 Type3 字形，且文字层会把“目、面、一”等字
映射到康熙部首码位。这里先去掉部首区码位，再把 CFF 转成 glyf，Chromium 就会正常
嵌入 CID 字体，复制、搜索都得到标准汉字。
"""
import os
from fontTools.ttLib import TTCollection, TTFont, newTable
from fontTools import subset
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen

SRC = {300: "/usr/share/fonts/opentype/noto/NotoSansCJK-Light.ttc",
       500: "/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc"}
RADICALS = set(range(0x2E80, 0x2FE0)) | set(range(0x31C0, 0x31F0))

def sc_face(path):
    c = TTCollection(path)
    for f in c.fonts:
        if "CJK SC" in f["name"].getDebugName(1):
            return f
    raise SystemExit("找不到 Noto Sans CJK SC")

def otf_to_ttf(font):
    glyph_order = font.getGlyphOrder()
    gs = font.getGlyphSet()
    glyf = newTable("glyf"); glyf.glyphOrder = glyph_order; glyf.glyphs = {}
    for name in glyph_order:
        pen = TTGlyphPen(gs)
        try:
            gs[name].draw(Cu2QuPen(pen, max_err=1.0, reverse_direction=True))
            glyf.glyphs[name] = pen.glyph()
        except Exception:
            glyf.glyphs[name] = TTGlyphPen(gs).glyph()
    font["glyf"] = glyf
    font["loca"] = newTable("loca")
    del font["CFF "]
    if "VORG" in font: del font["VORG"]
    maxp = font["maxp"]; maxp.tableVersion = 0x00010000
    for attr, val in (("maxZones", 1), ("maxTwilightPoints", 0), ("maxStorage", 0), ("maxFunctionDefs", 0),
                      ("maxInstructionDefs", 0), ("maxStackElements", 0), ("maxSizeOfInstructions", 0),
                      ("maxComponentElements", 0), ("maxPoints", 0), ("maxContours", 0),
                      ("maxCompositePoints", 0), ("maxCompositeContours", 0), ("maxComponentDepth", 0)):
        setattr(maxp, attr, val)
    font["head"].glyphDataFormat = 0
    font["head"].indexToLocFormat = 1
    post = font["post"]; post.formatType = 3.0
    font.sfntVersion = "\x00\x01\x00\x00"
    return font

def build_fonts(text, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    chars = {ord(c) for c in text if ord(c) >= 0x20} - RADICALS
    chars |= set(range(0x20, 0x7F))
    out = {}
    for weight, path in SRC.items():
        f = sc_face(path)
        opts = subset.Options(); opts.layout_features = ["kern", "palt", "vert"]; opts.name_IDs = ["*"]
        opts.notdef_outline = True; opts.hinting = False; opts.desubroutinize = True
        sub = subset.Subsetter(opts); sub.populate(unicodes=sorted(chars)); sub.subset(f)
        for t in f["cmap"].tables:          # 部首码位一律去掉，避免文字层映射错
            for cp in list(t.cmap):
                if cp in RADICALS: del t.cmap[cp]
        f = otf_to_ttf(f)
        name = f"jx-{weight}.ttf"
        p = os.path.join(out_dir, name); f.save(p); out[weight] = p
    return out

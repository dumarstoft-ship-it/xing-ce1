"""资料分析统计图：按转写数据画成SVG，嵌入题本时用题本字体（ZG Latin / ZG Song）。

原图没有入库，只有转写成表格的数据。这里按数据结构画常见的考卷统计图：柱状图、折线图、
柱线组合（数值用柱、增速用折线）、饼图。数值全部标注在图上，与转写表一致，不做任何取舍或换算。
图的样式（柱或线、灰度、标注位置）是推定的，不冒称与原图一致。

spec 字段：
  kind: bar | line | combo | pie | hbar
  categories: [类别...]
  bars: [{"name": 图例名, "values": [数字或None], "labels": [显示文字]}]        # bar、combo、hbar
  lines: [{"name": 图例名, "values": [...], "labels": [...]}]                 # line、combo
  slices: [{"name": 名称, "value": 数字, "label": 显示文字}]                     # pie
  left_unit / right_unit: 轴单位文字（可空）
  width_mm, height_mm: 原图印刷尺寸
"""
import math
from xml.sax.saxutils import escape

PT_PER_MM = 72 / 25.4
FS = 8.0           # 图内字号（pt）
FS_AXIS = 7.5
GRAYS = ["#9a9a9a", "#d0d0d0", "#5a5a5a", "#ffffff"]
LINE_STYLES = [("#000000", "none", "circle"), ("#000000", "3,2", "square"), ("#555555", "1.2,1.5", "triangle")]


def tw(s, fs=FS):
    """估计文字宽度（pt）：汉字与全角符号1em，其余0.5em。"""
    return sum(fs if ord(c) > 0x2000 and c not in "−–" else fs * 0.52 for c in str(s))


def nice_scale(lo, hi, n=5):
    if hi == lo:
        hi = lo + 1
    span = hi - lo
    raw = span / n
    mag = 10 ** math.floor(math.log10(raw))
    step = min((m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= raw), default=10 * mag)
    a = math.floor(lo / step) * step
    b = math.ceil(hi / step) * step
    return a, b, step


def fmt_tick(v, step):
    if abs(v) < 1e-9:
        return "0"
    d = 0 if step >= 1 else max(0, -int(math.floor(math.log10(step))))
    s = f"{v:.{d}f}"
    return s.replace("-", "−")


class SVG:
    def __init__(self, w, h):
        self.w, self.h, self.parts = w, h, []

    def add(self, s):
        self.parts.append(s)

    def text(self, x, y, s, fs=FS, anchor="middle", family="song", weight=None, rotate=None, halo=False):
        fam = '"ZG Latin", "ZG Song"' if family == "song" else '"ZG LatinB", "ZG Hei"'
        tr = f' transform="rotate({rotate} {x:.2f} {y:.2f})"' if rotate else ""
        if halo:   # 白底衬框（不用描边：描边会让PDF文字层里每个字重复一次）
            w = tw(s, fs)
            x0 = x - w / 2 if anchor == "middle" else (x - w if anchor == "end" else x)
            self.add(f'<rect x="{x0 - 0.8:.2f}" y="{y - fs * 0.82:.2f}" width="{w + 1.6:.2f}" height="{fs * 1.0:.2f}" fill="#fff"/>')
        self.add(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{fs}" text-anchor="{anchor}" '
                 f"font-family='{fam}' fill=\"#000\"{tr}>{escape(str(s))}</text>")

    def line(self, x1, y1, x2, y2, w=0.6, color="#000", dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{color}" stroke-width="{w}"{d}/>')

    def rect(self, x, y, w, h, fill, stroke="#000", sw=0.5):
        self.add(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def marker(self, x, y, shape, r=1.6):
        if shape == "circle":
            self.add(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="#fff" stroke="#000" stroke-width="0.6"/>')
        elif shape == "square":
            self.add(f'<rect x="{x - r:.2f}" y="{y - r:.2f}" width="{2 * r:.2f}" height="{2 * r:.2f}" fill="#000"/>')
        else:
            self.add(f'<path d="M{x:.2f},{y - r * 1.2:.2f} L{x + r * 1.1:.2f},{y + r * 0.8:.2f} L{x - r * 1.1:.2f},{y + r * 0.8:.2f} Z" fill="#000"/>')

    def render(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w:.2f}pt" height="{self.h:.2f}pt" '
                f'viewBox="0 0 {self.w:.2f} {self.h:.2f}">' + "".join(self.parts) + "</svg>\n")


def cat_lines(label, slot, fs=FS_AXIS):
    """类别名放不下一行时，在“年”后折成两行（如“9月”在上、“2023年”在下的写法改为“2023年／9月”两行）。"""
    if tw(label, fs) <= slot - 2:
        return [label]
    m = label.find("年")
    if 0 < m < len(label) - 1:
        return [label[:m + 1], label[m + 1:]]
    return [label]


def legend(svg, items, y, x_center):
    """items: [(kind, style_index, name)]，横排居中。"""
    gap, sw = 10, 12
    widths = [sw + 3 + tw(n) for _, _, n in items]
    total = sum(widths) + gap * (len(items) - 1)
    x = x_center - total / 2
    for (kind, i, name), wdt in zip(items, widths):
        if kind == "bar":
            svg.rect(x, y - 5.2, sw, 6, GRAYS[i % len(GRAYS)])
        else:
            color, dash, mk = LINE_STYLES[i % len(LINE_STYLES)]
            svg.line(x, y - 2.2, x + sw, y - 2.2, 0.8, color, None if dash == "none" else dash)
            svg.marker(x + sw / 2, y - 2.2, mk, 1.4)
        svg.text(x + sw + 3, y, name, anchor="start")
        x += wdt + gap


def axis_chart(spec):
    W = spec["width_mm"] * PT_PER_MM
    H = spec["height_mm"] * PT_PER_MM
    svg = SVG(W, H)
    cats = spec["categories"]
    bars = spec.get("bars") or []
    lines = spec.get("lines") or []
    has_right = bool(bars and lines)
    # 版面
    top = 8 + (14 if (len(bars) + len(lines)) > 1 or spec.get("legend_always") else 0)
    if spec.get("left_unit"):      # 纵轴上方写单位，要多留一行
        top += 10
    left = 30
    right = 12
    slot = (W - left - right) / len(cats)
    lines_per = [cat_lines(c, slot) for c in cats]
    bottom = 8 + 9.5 * max(len(x) for x in lines_per)
    x0, x1, y0, y1 = left, W - right, top, H - bottom
    pw = (x1 - x0) / len(cats)

    def scale_for(series):
        vals = [v for s in series for v in s["values"] if v is not None]
        lo, hi = min(vals + [0]), max(vals + [0])
        if lines and series is lines and not bars:
            lo = min(vals)
            lo = lo - (max(vals) - lo) * 0.15 if lo > 0 else lo
        hi = hi + (hi - lo) * 0.12
        return nice_scale(lo, hi)

    left_series = bars if bars else lines
    la, lb, ls = scale_for(left_series)
    ra = rb = rs = None
    if has_right:
        # 柱占下部约一半，折线浮在上部，两组数值标注互不遮挡
        bv = [v for s in bars for v in s["values"] if v is not None]
        la, lb, ls = nice_scale(min(bv + [0]), max(bv) * 1.85)
        lv = [v for s in lines for v in s["values"] if v is not None]
        lo, hi = min(lv), max(lv)
        span = (hi - lo) or abs(hi) or 1
        ra, rb, rs = nice_scale(lo - span * 1.25, hi + span * 0.18)

    def ly(v):
        return y1 - (v - la) / (lb - la) * (y1 - y0)

    def ry(v):
        return y1 - (v - ra) / (rb - ra) * (y1 - y0)

    # 坐标轴与刻度
    svg.line(x0, y0, x0, y1)
    t = la
    while t <= lb + 1e-9:
        yy = ly(t)
        svg.line(x0 - 2, yy, x0, yy)
        if abs(t) > 1e-9:
            svg.line(x0, yy, x1, yy, 0.25, "#999", "1.5,1.5")
        svg.text(x0 - 3, yy + 2.6, fmt_tick(t, ls), FS_AXIS, "end")
        t += ls
    # 柱线图不画右轴刻度：折线各点都标了数值，右轴只为把折线放在柱的上方
    zero = ly(0) if la <= 0 <= lb else y1
    svg.line(x0, zero, x1, zero, 0.6)
    if spec.get("left_unit"):
        svg.text(x0, y0 - 4, spec["left_unit"], FS_AXIS, "middle")

    # 类别标签
    for i, c in enumerate(cats):
        cx = x0 + pw * (i + 0.5)
        for k, ln in enumerate(lines_per[i]):
            svg.text(cx, y1 + 10 + 9.5 * k, ln, FS_AXIS)
    # 柱
    nb = len(bars)
    if nb:
        group_w = pw * (0.62 if nb > 1 else 0.5)
        bw = group_w / nb
        for j, s in enumerate(bars):
            for i, v in enumerate(s["values"]):
                if v is None:
                    continue
                bx = x0 + pw * i + (pw - group_w) / 2 + bw * j
                top_y, base = ly(max(v, 0)), ly(min(v, 0))
                svg.rect(bx, top_y, bw, max(base - top_y, 0.3), GRAYS[j % len(GRAYS)])
                lab = s["labels"][i]
                fs = min(FS_AXIS, max(5.5, (bw + 6) / max(1, len(str(lab))) / 0.52)) if nb > 1 else FS_AXIS
                ty = top_y - 2 if v >= 0 else base + fs + 1
                svg.text(bx + bw / 2, ty, lab, fs, halo=True)
    # 线
    for j, s in enumerate(lines):
        color, dash, mk = LINE_STYLES[j % len(LINE_STYLES)]
        yf = ry if has_right else ly
        pts = [(x0 + pw * (i + 0.5), yf(v)) for i, v in enumerate(s["values"]) if v is not None]
        d = " ".join(("M" if k == 0 else "L") + f"{x:.2f},{y:.2f}" for k, (x, y) in enumerate(pts))
        dash_attr = "" if dash == "none" else f' stroke-dasharray="{dash}"'
        svg.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="0.8"{dash_attr}/>')
        k = 0
        for i, v in enumerate(s["values"]):
            if v is None:
                continue
            x, y = pts[k]
            k += 1
            svg.marker(x, y, mk)
            off = -4 if j % 2 == 0 else 9
            svg.text(x, y + off, s["labels"][i], FS_AXIS, halo=True)
    # 图例
    items = [("bar", j, s["name"]) for j, s in enumerate(bars)] + [("line", j, s["name"]) for j, s in enumerate(lines)]
    if len(items) > 1 or spec.get("legend_always"):
        legend(svg, items, 9, W / 2)
    return svg.render()


def hbar_chart(spec):
    W = spec["width_mm"] * PT_PER_MM
    H = spec["height_mm"] * PT_PER_MM
    svg = SVG(W, H)
    cats = spec["categories"]
    s = spec["bars"][0]
    left = max(tw(c, FS_AXIS) for c in cats) + 8
    x0, x1, y0, y1 = left, W - 30, 6, H - 8
    ph = (y1 - y0) / len(cats)
    vmax = max(v for v in s["values"] if v is not None)
    svg.line(x0, y0, x0, y1)
    for i, (c, v, lab) in enumerate(zip(cats, s["values"], s["labels"])):
        cy = y0 + ph * (i + 0.5)
        svg.text(x0 - 4, cy + 2.6, c, FS_AXIS, "end")
        if v is None:
            continue
        bl = (x1 - x0) * v / vmax
        svg.rect(x0, cy - ph * 0.3, bl, ph * 0.6, GRAYS[0])
        svg.text(x0 + bl + 3, cy + 2.6, lab, FS_AXIS, "start")
    return svg.render()


def pie_chart(spec):
    W = spec["width_mm"] * PT_PER_MM
    H = spec["height_mm"] * PT_PER_MM
    svg = SVG(W, H)
    sl = spec["slices"]
    total = sum(x["value"] for x in sl)
    cx, cy = W * 0.42, H / 2
    r = min(W * 0.28, H * 0.36)
    a = -math.pi / 2
    fills = ["#5a5a5a", "#9a9a9a", "#d0d0d0", "#ffffff", "#7a7a7a", "#b5b5b5", "#e8e8e8", "#3a3a3a"]
    for i, x in enumerate(sl):
        da = 2 * math.pi * x["value"] / total
        b = a + da
        large = 1 if da > math.pi else 0
        p1 = (cx + r * math.cos(a), cy + r * math.sin(a))
        p2 = (cx + r * math.cos(b), cy + r * math.sin(b))
        svg.add(f'<path d="M{cx:.2f},{cy:.2f} L{p1[0]:.2f},{p1[1]:.2f} A{r:.2f},{r:.2f} 0 {large} 1 {p2[0]:.2f},{p2[1]:.2f} Z" '
                f'fill="{fills[i % len(fills)]}" stroke="#000" stroke-width="0.5"/>')
        m = (a + b) / 2
        ex, ey = cx + (r + 6) * math.cos(m), cy + (r + 6) * math.sin(m)
        svg.line(cx + r * math.cos(m), cy + r * math.sin(m), ex, ey, 0.4)
        anchor = "start" if math.cos(m) >= 0 else "end"
        svg.text(ex + (2 if anchor == "start" else -2), ey + 2.6, f'{x["name"]} {x["label"]}', FS_AXIS, anchor)
        a = b
    return svg.render()


def stack_chart(spec):
    """堆积柱：各段数值标在段内（段太矮时标在右侧），柱顶不另标合计。"""
    W = spec["width_mm"] * PT_PER_MM
    H = spec["height_mm"] * PT_PER_MM
    svg = SVG(W, H)
    cats, bars = spec["categories"], spec["bars"]
    top, left, right, bottom = 22, 32, 12, 16
    x0, x1, y0, y1 = left, W - right, top, H - bottom
    pw = (x1 - x0) / len(cats)
    totals = [sum(s["values"][i] or 0 for s in bars) for i in range(len(cats))]
    la, lb, ls = nice_scale(0, max(totals) * 1.08)

    def ly(v):
        return y1 - (v - la) / (lb - la) * (y1 - y0)
    svg.line(x0, y0, x0, y1)
    t = la
    while t <= lb + 1e-9:
        yy = ly(t)
        svg.line(x0 - 2, yy, x0, yy)
        if t > 0:
            svg.line(x0, yy, x1, yy, 0.25, "#999", "1.5,1.5")
        svg.text(x0 - 3, yy + 2.6, fmt_tick(t, ls), FS_AXIS, "end")
        t += ls
    svg.line(x0, y1, x1, y1, 0.6)
    if spec.get("left_unit"):
        svg.text(x0, y0 - 4, spec["left_unit"], FS_AXIS, "middle")
    bw = pw * 0.5
    for i, c in enumerate(cats):
        bx = x0 + pw * i + (pw - bw) / 2
        for k, ln in enumerate(cat_lines(c, pw)):
            svg.text(bx + bw / 2, y1 + 10 + 9.5 * k, ln, FS_AXIS)
        acc = 0
        for j, s in enumerate(bars):
            v = s["values"][i] or 0
            ya, yb = ly(acc + v), ly(acc)
            svg.rect(bx, ya, bw, yb - ya, GRAYS[j % len(GRAYS)])
            lab = s["labels"][i]
            if yb - ya >= FS_AXIS + 1.5:
                svg.text(bx + bw / 2, (ya + yb) / 2 + 2.6, lab, FS_AXIS, halo=True)
            else:
                svg.text(bx + bw + 2, (ya + yb) / 2 + 2.6, lab, FS_AXIS * 0.9, "start", halo=True)
            acc += v
    legend(svg, [("bar", j, s["name"]) for j, s in enumerate(bars)], 9, W / 2)
    return svg.render()


def multipie_chart(spec):
    """几组构成并排：每组一个饼图，组名在上，下方逐行列出各部分名称与占比（与扇区灰度对应）。"""
    W = spec["width_mm"] * PT_PER_MM
    H = spec["height_mm"] * PT_PER_MM
    svg = SVG(W, H)
    groups = spec["groups"]
    n = len(groups)
    cw = W / n
    nmax = max(len(g["slices"]) for g in groups)
    leg_h = nmax * 10
    r = max(14.0, min(cw * 0.3, (H - 20 - leg_h - 10) / 2))
    fills = ["#4a4a4a", "#8a8a8a", "#bdbdbd", "#ffffff", "#6a6a6a", "#e0e0e0", "#2a2a2a", "#a5a5a5"]
    for gi, g in enumerate(groups):
        cx = cw * (gi + 0.5)
        svg.text(cx, 11, g["name"], FS, family="hei")
        cy = 18 + r
        total = sum(x["value"] for x in g["slices"])
        a = -math.pi / 2
        for i, x in enumerate(g["slices"]):
            da = 2 * math.pi * x["value"] / total
            b = a + da
            large = 1 if da > math.pi else 0
            p1 = (cx + r * math.cos(a), cy + r * math.sin(a))
            p2 = (cx + r * math.cos(b), cy + r * math.sin(b))
            svg.add(f'<path d="M{cx:.2f},{cy:.2f} L{p1[0]:.2f},{p1[1]:.2f} A{r:.2f},{r:.2f} 0 {large} 1 {p2[0]:.2f},{p2[1]:.2f} Z" '
                    f'fill="{fills[i % len(fills)]}" stroke="#000" stroke-width="0.5"/>')
            a = b
        lw = max(tw(f'{x["name"]} {x["label"]}', FS_AXIS) for x in g["slices"]) + 10
        lx = cx - lw / 2
        for i, x in enumerate(g["slices"]):
            yy = cy + r + 12 + i * 10
            svg.rect(lx, yy - 6, 6, 6, fills[i % len(fills)])
            svg.text(lx + 9, yy, f'{x["name"]} {x["label"]}', FS_AXIS, "start")
    return svg.render()


def hbar2_chart(spec):
    """横向条形图：条长为第一组数值，右侧另列第二组数值（如环比增长率）。"""
    W = spec["width_mm"] * PT_PER_MM
    H = spec["height_mm"] * PT_PER_MM
    svg = SVG(W, H)
    cats = spec["categories"]
    s, extra = spec["bars"][0], spec["extra"]
    left = max(tw(c, FS_AXIS) for c in cats) + 8
    col = 46
    x0, x1, y0, y1 = left, W - col - 30, 16, H - 6
    ph = (y1 - y0) / len(cats)
    vmax = max(v for v in s["values"] if v is not None)
    svg.text((x0 + x1) / 2, 10, s["name"], FS_AXIS, family="hei")
    svg.text(W - col / 2 - 4, 10, extra["name"], FS_AXIS, family="hei")
    svg.line(x0, y0, x0, y1)
    for i, c in enumerate(cats):
        cy = y0 + ph * (i + 0.5)
        svg.text(x0 - 4, cy + 2.6, c, FS_AXIS, "end")
        v = s["values"][i]
        if v is not None:
            bl = (x1 - x0) * v / vmax
            svg.rect(x0, cy - ph * 0.3, bl, ph * 0.6, GRAYS[0])
            svg.text(x0 + bl + 3, cy + 2.6, s["labels"][i], FS_AXIS, "start")
        svg.text(W - col / 2 - 4, cy + 2.6, extra["labels"][i], FS_AXIS)
    return svg.render()


def render(spec):
    kind = spec["kind"]
    if kind in ("bar", "line", "combo"):
        return axis_chart(spec)
    if kind == "hbar":
        return hbar_chart(spec)
    if kind == "pie":
        return pie_chart(spec)
    if kind == "stack":
        return stack_chart(spec)
    if kind == "multipie":
        return multipie_chart(spec)
    if kind == "hbar2":
        return hbar2_chart(spec)
    raise ValueError(kind)


def text_values(spec):
    """图上印出的全部文字（用于核对PDF文字层）。"""
    out = []
    for c in spec.get("categories") or []:
        out += cat_lines(c, 0) if spec.get("kind") not in ("hbar", "hbar2") else [c]
    series = (spec.get("bars") or []) + (spec.get("lines") or [])
    # 只有一个指标的坐标图不画图例，指标名不印出来（单位另写在纵轴上方）
    legend = not (spec.get("kind") in ("bar", "line", "combo") and len(series) == 1 and not spec.get("legend_always"))
    for s in series:
        out += [x for x in s["labels"] if x not in (None, "")]
        if legend:
            out.append(s["name"])
    if spec.get("left_unit"):
        out.append(spec["left_unit"])
    for x in spec.get("slices") or []:
        out += [x["name"], x["label"]]
    for g in spec.get("groups") or []:
        out.append(g["name"])
        out += [y for x in g["slices"] for y in (x["name"], x["label"])]
    if spec.get("extra"):
        out += [spec["extra"]["name"]] + [x for x in spec["extra"]["labels"] if x]
    return out

#!/usr/bin/env python3
"""把「广东行测18套模拟」的一套题本排成考场样式的打印PDF。

    python3 广东行测18套模拟/打印排版/build_print.py M01 --font-dir <字体目录>

版式取自粉笔样卷（A4、小四正文每行36字、选项9字网格、每部分另起一页、
部分结束提示、页脚“第X页 共Y页”），字体取自中公样卷（方正书宋简体正文、
方正黑体简体标题与说明、方正楷体简体提示、Times New Roman 西文数字）。
实测依据与使用说明见同目录 README.md。

只读取考生可见的 `题目.jsonl`（不含答案），不改动任何题库或底稿。
排版层面的规范化（合并源PDF行末硬换行、空括号、填空线等）全部写入排版日志，
便于逐条核对；内容层面的问题应回到 selection.json 修改后重新生成。
"""
from __future__ import annotations

import argparse
import datetime as _dt
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent                      # 广东行测18套模拟/
REPO = PROJECT.parent

CN_NUM = "零一二三四五六七八九十"


def cn_number(n: int) -> str:
    if n <= 10:
        return CN_NUM[n]
    if n < 20:
        return "十" + (CN_NUM[n - 10] if n > 10 else "")
    tens, ones = divmod(n, 10)
    return CN_NUM[tens] + "十" + (CN_NUM[ones] if ones else "")


# --------------------------------------------------------------------------
# 字体
# --------------------------------------------------------------------------
FONT_ROLES = {
    # 角色: (PostScript 名, 文件名关键词)
    "Song": ("FZSSJW--GB1-0", ("FZSSJW", "方正书宋", "FZShuSong")),
    "Hei": ("FZHTJW--GB1-0", ("FZHTJW", "方正黑体", "FZHei")),
    "Kai": ("FZKTJW--GB1-0", ("FZKTJW", "方正楷体", "FZKai")),
    "Latin": ("TimesNewRomanPSMT", ("times.ttf", "Times New Roman.ttf", "TimesNewRoman")),
    "LatinB": ("TimesNewRomanPS-BoldMT", ("timesbd.ttf", "Times New Roman Bold.ttf", "TimesNewRomanBold")),
}
LATIN_FALLBACK = {
    "Latin": Path("/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"),
    "LatinB": Path("/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"),
}
# 中公样卷只把 ASCII 字符排成 Times；“”—①等全角符号仍用方正书宋。
# 方正书宋（GB2312版）缺 U+2212 减号，并入西文字体；度数符号随数字用西文字体。
LATIN_RANGE = "U+0020-007E, U+00B0, U+2212"
EXT_PREFIX = "补字"


def _cmap(path: Path) -> set[int]:
    from fontTools.ttLib import TTFont  # type: ignore
    return set(TTFont(str(path), lazy=True).getBestCmap())


def _ranges(cps: list[int]) -> str:
    out, i = [], 0
    while i < len(cps):
        j = i
        while j + 1 < len(cps) and cps[j + 1] == cps[j] + 1:
            j += 1
        out.append(f"U+{cps[i]:04X}" + (f"-{cps[j]:04X}" if j > i else ""))
        i = j + 1
    return ", ".join(out)


def _ps_name(path: Path) -> str | None:
    try:
        from fontTools.ttLib import TTFont  # type: ignore
    except ImportError:
        return None
    try:
        return TTFont(str(path), lazy=True)["name"].getDebugName(6)
    except Exception:
        return None


def find_fonts(font_dir: Path | None) -> dict[str, Path]:
    """按 PostScript 名（优先）或文件名在字体目录里找出各角色字体。"""
    found: dict[str, Path] = {}
    candidates: list[Path] = []
    if font_dir and font_dir.is_dir():
        candidates = [p for p in font_dir.rglob("*") if p.suffix.lower() in (".ttf", ".otf", ".ttc")]
    by_ps = {}
    for p in candidates:
        name = _ps_name(p)
        if name:
            by_ps.setdefault(name, p)
    for role, (ps, keys) in FONT_ROLES.items():
        if ps in by_ps:
            found[role] = by_ps[ps]
            continue
        for p in candidates:
            if any(k.lower() in p.name.lower() for k in keys):
                found[role] = p
                break
    for role, fallback in LATIN_FALLBACK.items():
        if role not in found and fallback.exists():
            found[role] = fallback
    # 补字：方正书宋简体是GB2312版，个别生僻字（如“岕”）不在其中。字体目录里以“补字”开头的
    # 宋体字体（如思源宋体的子集）只用于书宋缺的字，见 fonts_css 与构建日志。可放多个，
    # 按文件名排序，前一个没有的字才由后一个补。
    if font_dir and font_dir.is_dir():
        ext = sorted(p for p in font_dir.rglob(EXT_PREFIX + "*")
                     if p.suffix.lower() in (".ttf", ".otf", ".woff2", ".woff"))
        for i, p in enumerate(ext):
            found["SongExt" if i == 0 else f"SongExt{i + 1}"] = p
    missing = [r for r in FONT_ROLES if r not in found]
    if missing:
        raise SystemExit(
            "缺少字体：" + "、".join(missing) + "\n"
            "需要方正书宋简体、方正黑体简体、方正楷体简体（GB2312版，PostScript名 FZSSJW/FZHTJW/FZKTJW--GB1-0），"
            "可从方正字库官网获取（个人非商业使用免费），放入 --font-dir 指定的目录。字体文件不入库。"
        )
    return found


def fonts_css(fonts: dict[str, Path]) -> str:
    def face(family: str, path: Path, urange: str | None = None) -> str:
        rng = f"\n  unicode-range: {urange};" if urange else ""
        return f'@font-face {{\n  font-family: "{family}";\n  src: url("{path.as_uri()}");{rng}\n}}\n'
    return (
        face("ZG Latin", fonts["Latin"], LATIN_RANGE)
        + face("ZG LatinB", fonts["LatinB"], LATIN_RANGE)
        + face("ZG Song", fonts["Song"])
        + "".join(face("ZG Song", path, _ranges(sorted(cps))) for path, cps in _ext_layers(fonts) if cps)
        + face("ZG Hei", fonts["Hei"])
        + face("ZG Kai", fonts["Kai"])
    )


def _ext_layers(fonts: dict[str, Path]) -> list[tuple[Path, set[int]]]:
    """各补字字体实际负责的字：书宋和排在前面的补字字体都没有的那部分。"""
    taken = set(_cmap(fonts["Song"]))
    layers = []
    for key in sorted((k for k in fonts if k.startswith("SongExt")), key=lambda k: fonts[k].name):
        cps = _cmap(fonts[key]) - taken
        layers.append((fonts[key], cps))
        taken |= cps
    return layers


def check_glyphs(questions: list[dict], fonts: dict[str, Path], log: "Log") -> None:
    """正文用字逐一核对：书宋没有的字由补字字体排印并记入日志；两者都没有时直接报错。"""
    song = _cmap(fonts["Song"])
    layers = _ext_layers(fonts)
    ext = set().union(*(cps for _, cps in layers)) if layers else set()
    latin = set(range(0x20, 0x7F)) | {0xB0, 0x2212}
    used: dict[str, set[int]] = {}

    def walk(v, n):
        if isinstance(v, str):
            for ch in sub_digits(v):     # 下标数字排成下标（见 norm_text），不用书宋的字形
                if not ch.isspace():
                    used.setdefault(ch, set()).add(n)
        elif isinstance(v, dict):
            for k, x in v.items():
                if k not in ("path", "type", "id", "width_px", "height_px", "asset_id"):
                    walk(x, n)
        elif isinstance(v, list):
            for x in v:
                walk(x, n)
    for q in questions:
        walk({"s": q["stem"], "o": q["options"], "m": q.get("materials") or [], "b": q.get("block") or {}}, q["number"])
    lacking = {ch: ns for ch, ns in used.items() if ord(ch) not in song and ord(ch) not in latin}
    missing = {ch: ns for ch, ns in lacking.items() if ord(ch) not in ext}
    if missing:
        raise SystemExit("方正书宋缺字，且字体目录没有可补的字：" + "；".join(
            f"“{ch}”（U+{ord(ch):04X}，第{'、'.join(map(str, sorted(ns)))}题）" for ch, ns in missing.items())
            + "。可把含该字的宋体（如思源宋体）放入字体目录，文件名以“补字”开头")
    for ch, ns in sorted(lacking.items()):
        src = next(path for path, cps in layers if ord(ch) in cps)
        log.add(min(ns), "字体", "书宋缺字，由补字字体排印", ch,
                f"{src.name}（U+{ord(ch):04X}，第{'、'.join(map(str, sorted(ns)))}题）")


# --------------------------------------------------------------------------
# 排版层面的规范化（均记入日志）
# --------------------------------------------------------------------------
class Log:
    def __init__(self) -> None:
        self.items: list[dict] = []

    def add(self, number, where, kind, before, after) -> None:
        self.items.append({"题号": number, "位置": where, "类型": kind, "原文": before, "排版后": after})


MARKER = re.compile(r"^(（\d+）|\(\d+\)|[①-⑳]|[Ⅰ-Ⅻ][.．、]|[甲乙丙丁戊己庚辛]：|观众\d+：|[A-D][.．、]|第[一二三四五六七八九十]+[，、：])")   # Ⅰ.起的列项（M13第51题）
# 对话行：两到四字的称呼加冒号开头（如“小朱：”“张老师：”）。误判只会多保留一个换行
SPEAKER = re.compile(r"^[\u4e00-\u9fa5]{2,4}[：:]\S")
PROMPT = re.compile(
    r"^(以下|下列|由此|根据|据此|回答|增加|这段文字|这段话|依次填入|填入|最适合|将以上|上述|结果发现|问以下|问下列|问：|问:|那么)"
)
SENT_END = tuple("。！？；…”")


def _width(s: str) -> float:
    return sum(0.5 if c.isascii() else 1.0 for c in s)


def reflow(text: str, number, where: str, log: Log) -> list[str]:
    """合并源PDF的行末硬换行，保留真实分段（列表、对话、设问行）。

    只合并“上一行在句中断开”的换行。句末标点后的换行一律保留：误合并会把设问行、
    分段并进上文，误保留至多多一个短行，所以取保守一侧。底稿已规范化时本函数不改动分段。
    """
    lines = [ln for ln in text.split("\n") if ln.strip()]
    if not lines:
        return []
    paras = [lines[0]]
    for ln in lines[1:]:
        prev = paras[-1].rstrip()
        keep = (
            bool(MARKER.match(ln))                                  # 下一行以列表/对话标记开头
            or prev.endswith(("：", ":"))                           # 上一行以冒号引出下文
            or prev.endswith(SENT_END)                              # 上一句已完结
            or bool(PROMPT.match(ln) and MARKER.match(paras[-1]))   # 列表/对话项之后的设问行
            or bool(SPEAKER.match(ln))                              # 下一行是另一人的话
            or bool(PROMPT.match(ln) and SPEAKER.match(paras[-1]))  # 对话之后的设问行
            or bool(PROMPT.match(ln) and re.search(r"[？?]$|（[ 　]*）。?$", ln))   # 独立的问句设问行
        )
        if keep:
            paras.append(ln)
        else:
            joiner = " " if (prev[-1:].isascii() and prev[-1:].isalpha() and ln[:1].isascii() and ln[:1].isalpha()) else ""
            paras[-1] = prev + joiner + ln
            log.add(number, where, "合并源PDF行末硬换行", prev[-12:] + "⏎" + ln[:12], prev[-12:] + joiner + ln[:12])
    # 设问行末尾补冒号（原卷设问行均以冒号或问号结束）
    last = paras[-1]
    if len(paras) > 1 and PROMPT.match(last) and _width(last) <= 40 and not re.search(r"[：:？?。！）)]$", last):
        paras[-1] = last + "："
        log.add(number, where, "设问行末补冒号", last, paras[-1])
    return paras


DOTS = re.compile(r"·{3,}|•{3,}")
EMPTY_PAREN = re.compile(r"（[ 　]*）|\([ 　]*\)")
UNDERS = re.compile(r"_{3,}")
SPACE_BLANK = re.compile(r"(?<=\S)(?: {4,}|　{2,})(?=\S)")
BLANK_SIDE_SPACE = re.compile(r"(?:^|(?<=[^\x00-\x7F]))[ 　]+(?=_{3,})|(?<=___)[ 　]+(?=[^\x00-\x7F]|$)")
DIGIT_CJK_SPACE = re.compile(r"(?<=[0-9A-Za-z])[ ]+(?=[\u4e00-\u9fff])|(?<=[\u4e00-\u9fff])[ ]+(?=[0-9A-Za-z])")
HALF_PUNCT = re.compile(r"(?<=[\u4e00-\u9fff）”’])([:?;,])(?=[\u4e00-\u9fff“‘（]|\s|$)")
FULL_PUNCT = {":": "：", "?": "？", ";": "；", ",": "，"}
EDITORIAL_CELL = {"原表未标注": "", "原表空白": ""}


# 答题括号：粉笔样卷括号内约留两字宽，这里用全角括号夹一个全角空格
BRACKET = "（　）"


# 选项画在题图里时，题库在文字选项处放占位说明（“见题图中标为A的选项”“见题图中的 A 选项”），不印
FIG_PLACEHOLDER = re.compile(r"^见题图中(?:标为)?的?\s*[A-D]\s*(?:的)?选项。?$")


def options_in_figure(q: dict) -> bool:
    if q.get("options_mode") == "in_figure":
        return True
    opts = q.get("options") or {}
    has_fig = any(b["type"] == "figure" for b in q["stem"])
    return bool(opts) and has_fig and all(
        len(v) == 1 and v[0]["type"] == "text" and FIG_PLACEHOLDER.match(v[0]["text"].strip()) for v in opts.values())


def norm_text(s: str, number, where: str, log: Log) -> str:
    t = DOTS.sub("……", s)
    if t != s:
        log.add(number, where, "连续间隔点改为省略号", s, t)
    t2 = EMPTY_PAREN.sub(BRACKET, t)
    if t2 != t:
        log.add(number, where, "空括号统一为考场样式", t[-24:], t2[-24:])
    # 用一串空格充当的填空位置：HTML会把连续空格折成一个，印出来就看不到横线
    t3 = SPACE_BLANK.sub("____", t2)
    if t3 != t2:
        m = SPACE_BLANK.search(t2)
        log.add(number, where, "空格占位改为填空线", t2[max(0, m.start() - 8):m.end() + 8],
                t3[max(0, m.start() - 8):m.start() + 12])
    # 转写在填空线两侧留的空格（“太空领域 ____ 。”），原卷没有，印出来是一段空白
    t4 = BLANK_SIDE_SPACE.sub("", t3)
    if t4 != t3:
        m = BLANK_SIDE_SPACE.search(t3)
        log.add(number, where, "填空线两侧空格删去", t3[max(0, m.start() - 8):m.end() + 8],
                t4[max(0, m.start() - 8):m.start() + 8])
    # PDF转写在数字、西文与汉字之间留的空格（“6 条隧道”“3000 米”“APP 为了”），中文排版不留
    t5 = DIGIT_CJK_SPACE.sub("", t4)
    if t5 != t4:
        m = DIGIT_CJK_SPACE.search(t4)
        log.add(number, where, "数字、西文与汉字间空格删去", t4[max(0, m.start() - 6):m.end() + 6],
                t5[max(0, m.start() - 6):m.start() + 6])
    # 汉字后的半角冒号、问号、分号、逗号改全角（“古人云:”“一定为真?”）
    t6 = HALF_PUNCT.sub(lambda m: FULL_PUNCT[m.group(1)], t5)
    if t6 != t5:
        m = HALF_PUNCT.search(t5)
        log.add(number, where, "半角标点改全角", t5[max(0, m.start() - 8):m.end() + 4],
                t6[max(0, m.start() - 8):m.end() + 4])
    # 下标数字字符（“S₁”“A₂”）：方正书宋没有这些字形，改成数学片段里的下标排印
    t7 = sub_digits(t6)
    if t7 != t6:
        m = SUB_DIGITS.search(t6)
        log.add(number, where, "上下标、分数字符改为数学排印", t6[max(0, m.start() - 6):m.end() + 6],
                t7[max(0, m.start() - 6):m.end() + 12])
    return t7


SUB_DIGITS = re.compile("[₀₁₂₃₄₅₆₇₈₉]+|[⁰¹²³⁴⁵⁶⁷⁸⁹]+|[½⅓¼¾]")
SUB_PLAIN = str.maketrans("₀₁₂₃₄₅₆₇₈₉⁰¹²³⁴⁵⁶⁷⁸⁹", "01234567890123456789")
VULGAR = {"½": ("1", "2"), "⅓": ("1", "3"), "¼": ("1", "4"), "¾": ("3", "4")}


def _sub_tex(t: str) -> str:
    if t in VULGAR:
        return "\\frac{%s}{%s}" % VULGAR[t]
    return ("_{" if t[0] in "₀₁₂₃₄₅₆₇₈₉" else "^{") + t.translate(SUB_PLAIN) + "}"


def sub_digits(s: str) -> str:
    """下标、上标数字字符（“S₁”“m²”）和“½”这类分数字符，方正书宋没有字形：
    数学片段外的改为 $_{1}$、$^{2}$、$\\frac{1}{2}$，片段内的去掉外层$。"""
    out, pos = [], 0
    for m in re.finditer(r"\$[^$]+\$", s):
        out.append(SUB_DIGITS.sub(lambda d: "$" + _sub_tex(d.group(0)) + "$", s[pos:m.start()]))
        out.append(SUB_DIGITS.sub(lambda d: _sub_tex(d.group(0)), m.group(0)))
        pos = m.end()
    out.append(SUB_DIGITS.sub(lambda d: "$" + _sub_tex(d.group(0)) + "$", s[pos:]))
    return "".join(out)


# --------------------------------------------------------------------------
# 行内：数学片段与填空线
# --------------------------------------------------------------------------
SYMBOLS = {   # 题库数学片段里出现的符号命令，按印刷体字符输出
    "pi": "π", "alpha": "α", "beta": "β", "gamma": "γ", "theta": "θ", "lambda": "λ", "mu": "μ", "rho": "ρ",
    "omega": "ω", "Omega": "Ω", "Delta": "Δ", "delta": "δ", "varphi": "φ", "phi": "φ", "sigma": "σ",
    "leq": "≤", "le": "≤", "geq": "≥", "ge": "≥", "neq": "≠", "ne": "≠", "approx": "≈", "pm": "±",
    "infty": "∞", "rightarrow": "→", "to": "→", "Rightarrow": "⇒", "leftarrow": "←", "uparrow": "↑",
    "downarrow": "↓", "because": "∵", "therefore": "∴", "parallel": "∥", "perp": "⊥", "cdots": "⋯",
    "ldots": "…", "prime": "′", "sim": "∼", "equiv": "≡", "propto": "∝", "in": "∈", "cap": "∩", "cup": "∪",
}


def tex_to_html(src: str) -> str:
    """覆盖题库中出现的少量 LaTeX：\\frac \\sqrt ^ _ \\circ \\mathrm。"""
    pos = 0

    def group(upright: bool) -> str:
        nonlocal pos
        while pos < len(src) and src[pos] == " ":
            pos += 1
        if pos < len(src) and src[pos] == "{":
            pos += 1
            out = seq(upright, stop="}")
            pos += 1
            return out
        return atom(upright)

    def atom(upright: bool) -> str:
        nonlocal pos
        c = src[pos]
        if c == "\\":
            m = re.match(r"\\([A-Za-z]+)", src[pos:])
            cmd = m.group(1) if m else src[pos + 1]
            pos += len(cmd) + 1
            if cmd == "frac":
                a = group(upright)
                b = group(upright)
                return f'<span class="frac"><span>{a}</span><span>{b}</span></span>'
            if cmd == "sqrt":
                a = group(upright)
                return f'√<span class="sqrt-arg">{a}</span>'
            if cmd == "circ":
                return "°"
            if cmd == "triangle":
                return "△"
            if cmd in ("angle",):
                return "∠"
            if cmd in ("mathrm", "text", "rm"):
                return group(True)
            if cmd in ("times",):
                return "×"
            if cmd in ("div",):
                return "÷"
            if cmd in ("cdot",):
                return "·"
            if cmd in ("%",):
                return "%"
            if cmd in SYMBOLS:
                return SYMBOLS[cmd]
            if cmd in ("left", "right"):          # \left( \right) 只取括号本身
                return ""
            if cmd in ("text", "textbf", "mathbf", "operatorname"):
                return group(True)
            raise ValueError(f"未支持的 LaTeX 命令：\\{cmd}（{src}）")
        pos += 1
        if c.isalpha() and c.isascii() and not upright:
            return f'<span class="m-i">{html.escape(c)}</span>'
        if c.isascii():
            return f'<span class="m-r">{html.escape(c)}</span>'
        return html.escape(c)

    def seq(upright: bool, stop: str | None = None) -> str:
        nonlocal pos
        out = []
        while pos < len(src) and (stop is None or src[pos] != stop):
            c = src[pos]
            if c == " ":
                pos += 1
                continue
            if c in "^_":
                pos += 1
                arg = group(upright)
                if arg == "°":
                    out.append("°")
                else:
                    tag = "sup" if c == "^" else "sub"
                    out.append(f"<{tag}>{arg}</{tag}>")
                continue
            out.append(atom(upright))
        return "".join(out)

    return seq(False)


MATH = re.compile(r"\s*\$([^$]+)\$\s*")


def inline_html(s: str) -> str:
    """转义文字，渲染 $..$ 数学片段与填空线。数学两侧仅保留ASCII间距。"""
    out = []
    pos = 0
    for m in MATH.finditer(s):
        out.append(_text_html(s[pos:m.start()]))
        before = s[m.start() - 1] if m.start() > 0 else ""
        after = s[m.end()] if m.end() < len(s) else ""
        lead = " " if (before.isascii() and before.isalnum() and m.group(0)[0] == " ") else ""
        tail = " " if (after.isascii() and after.isalnum() and m.group(0)[-1] == " ") else ""
        out.append(lead + tex_to_html(m.group(1)) + tail)
        pos = m.end()
    out.append(_text_html(s[pos:]))
    return "".join(out)


# 填空线是行内块，浏览器会在它与后面的句号、逗号之间断行，标点落到下一行行首；
# 这里把填空线与紧邻的前后标点粘成不可断开的一段
BLANK_GLUE = re.compile(r'([“‘（「『]*)(<span class="blank"></span>)([，。、；：？！）”’」』]*)')


def _glue(m: re.Match) -> str:
    return f'<span class="nobr">{m.group(0)}</span>' if (m.group(1) or m.group(3)) else m.group(0)


# 原卷中加下划线的文字（如“画线词”），题库转写为 <u>…</u>
UNDERLINE = re.compile(r"<u>(.*?)</u>", re.S)


def _text_html(s: str) -> str:
    out, pos = [], 0
    for m in UNDERLINE.finditer(s):
        out.append(_plain_html(s[pos:m.start()]))
        out.append(f'<span class="ul">{_plain_html(m.group(1))}</span>')
        pos = m.end()
    out.append(_plain_html(s[pos:]))
    res = "".join(out)
    if "&lt;u&gt;" in res or "&lt;/u&gt;" in res:
        raise SystemExit(f"下划线标记没有成对：{s[:30]}")
    return res


def _plain_html(s: str) -> str:
    parts = UNDERS.split(s)
    return BLANK_GLUE.sub(_glue, '<span class="blank"></span>'.join(html.escape(p) for p in parts))


# --------------------------------------------------------------------------
# 题图尺寸：按题图在源PDF中的原始印刷尺寸
# --------------------------------------------------------------------------
class FigureSizer:
    MAX_W = 120.0   # mm，题干图
    MAX_H = 100.0   # mm

    def __init__(self) -> None:
        self.mock = {}
        p = REPO / "模考/2026下半年广东卷_16-33季_AI可读/图片清单.json"
        if p.exists():
            for x in json.loads(p.read_text(encoding="utf-8")):
                self.mock[x["id"]] = x.get("bbox_pt")
        self.jz = {}
        p = REPO / "江浙行测_AI题库/images/manifest.json"
        if p.exists():
            for k, x in json.loads(p.read_text(encoding="utf-8")).items():
                src = (x.get("sources") or [{}])[0]
                self.jz[k] = src.get("bbox")
        self.gd = {}                     # 广东真题题库（2013—2021、2022—2026）：裁图在源PDF中的框（pt）
        for d in ("广东/行测/2013-2021", "广东/行测/2022-2026", "广东/事业单位/结构化"):
            p = REPO / d / "assets-manifest.json"
            if p.exists():
                for x in json.loads(p.read_text(encoding="utf-8")):
                    box = x.get("source_bbox_points")
                    if not box and x.get("docx_extent_points"):      # Word原图：按文档中的显示尺寸
                        w, h = x["docx_extent_points"][:2]
                        box = [0, 0, w, h]
                    self.gd[x["id"]] = box
        for mf in sorted((REPO / "国考/资料分析/assets").glob("*/manifest.json")):   # 国考资料题库（M13起补资料组）
            for x in json.loads(mf.read_text(encoding="utf-8")):
                if x.get("source_bbox_points"):
                    self.gd[x["id"]] = x["source_bbox_points"]

    def size_mm(self, block: dict, in_material: bool = False) -> tuple[float, float, str]:
        w, h, how = self._size_mm(block, in_material)
        adj = ADJUST.lookup(block) if ADJUST else None
        if adj:
            from PIL import Image  # type: ignore
            wpx, hpx = Image.open(REPO / block["path"]).size
            w2 = min(float(adj["print_width_mm"]), self.MAT_W)
            return w2, w2 * hpx / wpx, f"登记印宽，默认规则为{w:.1f}mm（{how}）；{adj['reason']}"
        return w, h, how

    def _size_mm(self, block: dict, in_material: bool = False) -> tuple[float, float, str]:
        from PIL import Image  # type: ignore
        path = REPO / block["path"]
        wpx, hpx = Image.open(path).size
        bbox = None
        how = "按200dpi换算"
        aid = block.get("asset_id") or Path(block["path"]).stem   # 底稿有时省略asset_id，文件名即资产编号
        if "模考/" in block["path"] and aid in self.mock:
            bbox, how = self.mock[aid], "源PDF印刷尺寸（模考图片清单）"
        else:
            stem = Path(block["path"]).stem
            if "江浙行测_AI题库/images" in block["path"] and stem in self.jz:
                bbox, how = self.jz[stem], "源PDF印刷尺寸（江浙图片清单）"
            elif ("广东/行测/" in block["path"] or "广东/事业单位/" in block["path"] or "国考/资料分析/" in block["path"]) and stem in self.gd:
                bbox, how = self.gd[stem], "源PDF印刷尺寸（广东真题图片清单）"
        if bbox:
            w = (bbox[2] - bbox[0]) / 72 * 25.4
            h = (bbox[3] - bbox[1]) / 72 * 25.4
        else:
            w, h = wpx / 200 * 25.4, hpx / 200 * 25.4
        # 不放大低分辨率原图；只按考场常见尺寸设上限（广东九宫格图约7.8×9cm，横排图推约10—12cm宽）
        max_w, max_h = (self.MAT_W, self.MAT_H) if in_material else (self.MAX_W, self.MAX_H)
        scale = min(1.0, max_w / w, max_h / h)
        if scale < 1:
            how += f"，按考场常见尺寸缩至{scale:.0%}"
        return w * scale, h * scale, how

    MAT_W, MAT_H = 152.4, 110.0   # 资料图表可用满版心


class SizeAdjust:
    """题图尺寸调整.json：没有源印刷尺寸的重建图等，另行登记印宽（只缩放，不改像素）；
    每条写明依据，只在源图哈希未变时启用。"""

    def __init__(self) -> None:
        self.by_id = {}
        p = HERE / "题图尺寸调整.json"
        if p.exists():
            for rec in json.loads(p.read_text(encoding="utf-8")):
                self.by_id[Path(rec["path"]).stem] = rec

    def lookup(self, block: dict):
        import hashlib
        rec = self.by_id.get(block.get("asset_id") or Path(block["path"]).stem)
        if not rec or rec["path"] != block["path"]:
            return None
        digest = hashlib.sha256((REPO / block["path"]).read_bytes()).hexdigest()
        if digest != rec["source_image_sha256"]:
            raise SystemExit(f"题图尺寸调整.json 登记的 {block['path']} 已变动，请重新查看后更新哈希")
        return rec


ADJUST: SizeAdjust | None = None


def apply_whitespace_fixes(paper_id: str, questions: list[dict], log: Log) -> None:
    """排版空白勘误.json：底稿丢了原卷的空格或多出分段时，按原卷恢复。
    只许改空白（空格、换行），文字和标点一个不改；只在底稿该段文字未变时启用。"""
    import hashlib
    p = HERE / "排版空白勘误.json"
    if not p.exists():
        return
    by_no = {q["number"]: q for q in questions}
    for e in json.loads(p.read_text(encoding="utf-8")):
        if e["套卷"] != paper_id:
            continue
        n, where = e["题号"], e["位置"]
        q = by_no[n]
        blocks = q["stem"] if where == "题干" else q["options"][where.removeprefix("选项")]
        block = blocks[e.get("块", 0)]
        cur, new = block["text"], e["改为"]
        if cur == new:
            log.add(n, where, "底稿已按原卷修正空白", "排版空白勘误.json此条可删除", new[:24])
            continue
        if hashlib.sha256(cur.encode("utf-8")).hexdigest() != e["底稿文字SHA256"]:
            raise SystemExit(f"排版空白勘误.json：第{n}题{where}的底稿文字已变，请重新核对原卷后更新登记")
        if re.sub(r"\s", "", cur) != re.sub(r"\s", "", new):
            raise SystemExit(f"排版空白勘误.json：第{n}题{where}的登记不止改空白")
        block["text"] = new
        log.add(n, where, "依原卷恢复空白", cur, new)


class Redraws:
    """打印排版/重绘/ 下按原图坐标重绘的矢量图；只在源图哈希未变时启用。"""

    def __init__(self) -> None:
        self.by_id = {}
        p = HERE / "重绘" / "重绘核对记录.json"
        if p.exists():
            for rec in json.loads(p.read_text(encoding="utf-8")):
                self.by_id[rec["asset_id"]] = rec

    def lookup(self, block: dict, number, log: Log):
        import hashlib
        rec = self.by_id.get(block.get("asset_id") or Path(block["path"]).stem)
        if not rec:
            return None
        digest = hashlib.sha256((REPO / block["path"]).read_bytes()).hexdigest()
        if digest != rec["source_image_sha256"]:
            log.add(number, "题图", "源图已变，未用重绘图", block["path"], "沿用原图，请重新核对重绘")
            return None
        return rec


# --------------------------------------------------------------------------
# 结构：部分、说明
# --------------------------------------------------------------------------
PARTS = [
    {"name": "政治理论", "match": ["政治理论"], "kind": "politics"},
    {"name": "常识判断", "match": ["常识判断", "常识应用"],
     "intro": ["根据题目要求，在四个选项中选出一个最恰当的答案。"]},
    {"name": "言语理解与表达", "match": ["言语理解与表达"],
     "intro": ["本部分包括表达与理解两方面的内容。请根据题目要求，在四个选项中选出一个最恰当的答案。"]},
    {"name": "数量关系", "match": ["数量关系"], "kind": "quant"},
    {"name": "判断推理", "match": ["判断推理"], "kind": "judgment"},
    {"name": "科学推理", "match": ["科学推理"],
     "intro": ["每道题给出文字或图表信息，要求你在此基础上，运用基本科学知识进行推理判断，从四个备选项中选出最合理的一项。"]},
    {"name": "资料分析", "match": ["资料分析"],
     "intro": ["所给出的图、表、文字或综合性资料均有若干个问题要你回答。你应根据资料提供的信息进行分析、比较、计算和判断处理。"]},
]
SECTION_RANGES = {"政治理论": (1, 10), "常识判断": (11, 15), "言语理解与表达": (16, 30), "数量关系": (31, 45),
                  "判断推理": (46, 65), "科学推理": (66, 70), "资料分析": (71, 90)}   # 2025、2026年广东卷各部分题号
POLITICS_GROUPS = {
    "true_false": ("判断题", "{ord}、判断题。阅读题目，对题目表述的正误作出判断。"),
    "single_choice": ("单选题", "{ord}、单选题。每题只有 1 个答案是最恰当的，要求选出最恰当的 1 项。"),
    "multiple_choice": ("多选题", "{ord}、多选题。按照题目要求作答，每题所设选项至少有 2 个正确答案，要求选出所有正确答案，多选、少选、错选均不得分。"),
}
QUANT_GROUPS = {
    "数字推理": ("数字推理", "{ord}、数字推理，共 {n} 题。每道题给出一个数列，但其中缺少一项（几项），要求你仔细观察这个数列中数字之间的关系，找出其中的规律，然后从四个备选项中选出最合理的一项填补空缺。"),
    "数学运算": ("数学运算", "{ord}、数学运算，共 {n} 题。每道题给出表达数量关系的一段资料，要求你熟练运用加、减、乘、除等基本运算法则，利用基本的数学知识，准确、迅速地计算出结果，从四个备选项中选出正确的一项。"),
}
JUDGMENT_GROUPS = {
    "图形推理": ("图形推理", "{ord}、图形推理。请按每道题的答题要求作答。"),
    "定义判断": ("定义判断", "{ord}、定义判断。每道题先给出定义，然后列出四种情况，要求你严格依据定义，从中选出一个最符合或最不符合该定义的答案。注意：假设这个定义是正确的，不容置疑的。"),
    "类比推理": ("类比推理", "{ord}、类比推理。每道题给出一组相关的词，要求你在备选答案中找出一组与之在逻辑关系上最为贴近、相似或匹配的词。"),
    "逻辑推理": ("逻辑判断", "{ord}、逻辑判断。每道题给出一段陈述，这段陈述被假设是正确的、不容置疑的。要求你根据这段陈述，选择一个答案。注意：正确的答案应与所给的陈述相符合，不需要任何附加说明即可以从陈述中直接推出。"),
    "逻辑判断": ("逻辑判断", "{ord}、逻辑判断。每道题给出一段陈述，这段陈述被假设是正确的、不容置疑的。要求你根据这段陈述，选择一个答案。注意：正确的答案应与所给的陈述相符合，不需要任何附加说明即可以从陈述中直接推出。"),
}
COUNT_WORD = {1: "一", 2: "两", 3: "三", 4: "四", 5: "五"}


def _join_types(names: list[str]) -> str:
    if len(names) == 1:
        return names[0]
    return "、".join(names[:-1]) + "与" + names[-1]


def group_key(part: dict, q: dict) -> str | None:
    kind = part.get("kind")
    if kind == "politics":
        return q["question_type"]
    if kind in ("quant", "judgment"):
        return q.get("subtype") or ""
    return None


def group_table(part: dict) -> dict:
    return {"politics": POLITICS_GROUPS, "quant": QUANT_GROUPS, "judgment": JUDGMENT_GROUPS}.get(part.get("kind"), {})


# --------------------------------------------------------------------------
# 题目 HTML
# --------------------------------------------------------------------------
def paragraphs_html(text: str, number, where: str, log: Log, cls: str = "") -> list[str]:
    paras = reflow(norm_text(text, number, where, log), number, where, log)
    c = f' class="{cls}"' if cls else ""
    return [f"<p{c}>{inline_html(p)}</p>" for p in paras]


REDRAWS: Redraws | None = None


def figure_html(block: dict, sizer: FigureSizer, number, log: Log, in_material: bool = False) -> str:
    rec = REDRAWS.lookup(block, number, log) if REDRAWS else None
    if rec:
        kind = rec.get("kind", "svg")
        if kind == "svg":
            html_part, w, h = _svg_part(rec["svg_path"], rec["print_width_mm"])
            log.add(number, "题图", "改用按原图坐标的矢量重绘图", block["path"],
                    f"{rec['svg_path']}，{w:.1f}×{h:.1f}mm（核对见 重绘/重绘核对记录.json）")
            return f'<div class="fig">{html_part}</div>'
        if kind == "image":
            html_part, w, h = _png_part(rec["png_path"], rec["print_width_mm"])
            log.add(number, "题图", "改用原像素放大二值化图" if rec.get("binarize", True) else "改用原像素平滑放大图", block["path"],
                    f"{rec['png_path']}，{w:.1f}×{h:.1f}mm（核对见 重绘/重绘核对记录.json）")
            return f'<div class="fig">{html_part}</div>'
        if kind == "compose":
            parts, desc = [], []
            for part in rec["parts"]:
                if "svg_path" in part:
                    hp, w, h = _svg_part(part["svg_path"], part["print_width_mm"])
                else:
                    hp, w, h = _png_part(part["png_path"], part["print_width_mm"])
                parts.append(f'<div class="fig-part">{hp}</div>')
                desc.append(f"{part.get('svg_path') or part.get('png_path')} {w:.1f}×{h:.1f}mm")
            log.add(number, "题图", "题干小图矢量重绘、选项原像素", block["path"],
                    "；".join(desc) + "（核对见 重绘/重绘核对记录.json）")
            return '<div class="fig">' + "".join(parts) + "</div>"
        raise SystemExit(f"未知的重绘记录类型：{kind}")
    if block["path"].endswith(".svg"):
        # 编辑新画的矢量题图（如重编原创题）：内嵌SVG，按登记印宽
        svg = (REPO / block["path"]).read_text(encoding="utf-8")
        m = re.search(r'viewBox="[-\d.]+ [-\d.]+ ([\d.]+) ([\d.]+)"', svg)
        w = float(block["print_width_mm"])
        h = w * float(m.group(2)) / float(m.group(1))
        svg = re.sub(r'width="[\d.]+(?:pt|mm)?" height="[\d.]+(?:pt|mm)?"', f'width="{w:.2f}mm" height="{h:.2f}mm"', svg, count=1)
        log.add(number, "题图", "编辑绘制的矢量题图", block["path"], f"{w:.1f}×{h:.1f}mm（{block.get('size_basis', '登记印宽')}）")
        return f'<div class="fig">{svg}</div>'
    w, h, how = sizer.size_mm(block, in_material)
    src = (REPO / block["path"]).as_uri()
    log.add(number, "题图", "题图尺寸", block["path"], f"{w:.1f}×{h:.1f}mm（{how}）")
    return f'<div class="fig"><img src="{src}" style="width:{w:.2f}mm;height:{h:.2f}mm" alt=""></div>'


def _svg_part(rel: str, width_mm: float) -> tuple[str, float, float]:
    svg = (HERE / rel).read_text(encoding="utf-8")
    m = re.search(r'viewBox="[-\d.]+ [-\d.]+ ([\d.]+) ([\d.]+)"', svg)
    h = width_mm * float(m.group(2)) / float(m.group(1))
    svg = re.sub(r'width="[\d.]+" height="[\d.]+"', f'width="{width_mm:.2f}mm" height="{h:.2f}mm"', svg, count=1)
    return svg, width_mm, h


def _png_part(rel: str, width_mm: float) -> tuple[str, float, float]:
    from PIL import Image  # type: ignore
    path = HERE / rel
    wpx, hpx = Image.open(path).size
    h = width_mm * hpx / wpx
    return f'<img src="{path.as_uri()}" style="width:{width_mm:.2f}mm;height:{h:.2f}mm" alt="">', width_mm, h


def chart_html(block: dict, number, log: Log) -> str:
    """资料统计图：原图未入库、按转写数据重绘的SVG（重编/tools/charts.py），内嵌进题本，图中文字用题本字体。"""
    path = REPO / block["svg_path"]
    svg = path.read_text(encoding="utf-8")
    m = re.search(r'viewBox="[-\d.]+ [-\d.]+ ([\d.]+) ([\d.]+)"', svg)
    w = min(float(block["print_width_mm"]), FigureSizer.MAT_W)
    h = w * float(m.group(2)) / float(m.group(1))
    svg = re.sub(r'width="[\d.]+pt" height="[\d.]+pt"', f'width="{w:.2f}mm" height="{h:.2f}mm"', svg, count=1)
    log.add(number, "资料统计图", "按转写数据重绘的统计图", block["title"], f"{block['svg_path']}，{w:.1f}×{h:.1f}mm（原图印宽）")
    title = f'<div class="chart-title">{inline_html(block["title"])}</div>' if block.get("title") else ""
    notes = "".join(f'<p class="tbl-note">{inline_html(x)}</p>' for x in (block.get("notes") or "").split("\n") if x.strip())
    return f'<div class="chart">{title}<div class="fig">{svg}</div>{notes}</div>'


# ---- 表格 ----
# 编辑转写时写进表格的说明不是考题内容：单元格注记改回原表空白，备注里的“原表”说明改成考生能读的说法
EDITORIAL_NOTE = [
    (re.compile(r"“—”为原表缺省项。?"), "“—”表示该项数据缺省。"),
    (re.compile(r"“—”表示原表未(?:给出|提供)(?:该项)?数据。?"), "“—”表示未给出数据。"),
    (re.compile(r"“—”为原表未(?:给出|提供)的数据。?"), "“—”表示未给出数据。"),
    (re.compile(r"“—”为原表符号，不补算。?"), "“—”表示未给出数据。"),
]
# 只描述转写过程、对考生没有信息量的备注句（如“差值方向依题干”“不补算”“原表未标百分号”），印刷时删去
NOTE_META = re.compile(r"原表|依题干|转写|不补算|原图|单元格展开")
TABLE_PT = 10.5          # 表格字号（五号）
TABLE_PAD_EM = 0.9       # 单元格左右内边距合计（字宽）
TEXT_WIDTH_EM = 432 / TABLE_PT


def _em(s: str) -> float:
    """按五号字估算文字宽度（字宽单位）：汉字与全角符号1，数字与西文约0.5。"""
    w = 0.0
    for c in s:
        if c.isascii():
            w += 0.25 if c in ".,:;|!il" else 0.5
        else:
            w += 1.0
    return w


def _clean_cells(block: dict, number, log: Log) -> tuple[list[str], list[list[str]]]:
    heads = list(block.get("headers") or [])
    rows = []
    for row in block.get("rows") or []:
        out = []
        for c in row:
            if c in EDITORIAL_CELL:
                log.add(number, "资料表格", "删去编辑注记（原表此格空白）", c, EDITORIAL_CELL[c])
                c = EDITORIAL_CELL[c]
            out.append(c)
        rows.append(out)
    return heads, rows


def _col_widths(heads: list[str], rows: list[list[str]], avail: float = TEXT_WIDTH_EM) -> list[float] | None:
    """返回各列宽度（字宽）。正文格尽量不折行；表头可折行；实在放不下时首列折成两行。"""
    ncol = max([len(heads)] + [len(r) for r in rows])
    pad = TABLE_PAD_EM + 0.4                       # 内边距加少量余量，避免恰好卡边时折行
    body = [max([_em(r[i]) for r in rows if i < len(r)] + [1.0]) for i in range(ncol)]
    head = [_em(heads[i]) if i < len(heads) else 0 for i in range(ncol)]
    full = [max(b, 2.0) + pad for b in body]
    want = [max(f, h + pad) for f, h in zip(full, head)]
    if sum(want) <= avail:
        return want

    def spread(base: list[float]) -> list[float]:
        spare = avail - sum(base)
        deficit = [max(0.0, w - b) for w, b in zip(want, base)]
        tot = sum(deficit) or 1.0
        return [b + spare * d / tot for b, d in zip(base, deficit)]

    if sum(full) <= avail:
        return spread(full)
    two = full[:]
    two[0] = max(4.0, body[0] / 2 + 1) + pad       # 首列（指标名称）折成两行
    if sum(two) <= avail:
        return spread(two)
    return None


def table_html(block: dict, number, log: Log, avail: float = TEXT_WIDTH_EM) -> str:
    heads, rows = _clean_cells(block, number, log)
    title = block.get("title") or ""
    # 数字推理的数阵：原卷是一个数字方格，题库转写成表时加了“题目数表”的表题和“第1列”这类列名，只印数字
    if re.search(r"列名为转写时添加", block.get("notes") or "") and heads and all(re.fullmatch(r"第\d+列", h) for h in heads):
        log.add(number, "题干表格", "数阵去掉转写时加的表题和列名", f"{title}｜{'、'.join(heads)}", "只印数字方格")
        heads = []
        if title == "题目数表":
            title = ""
    # 两列长表（如逐年比例）在原卷中多为横排，转成两行以省版面
    if len(heads) == 2 and len(rows) >= 5 and all(len(r) == 2 for r in rows) \
            and max(_em(c) for r in rows for c in r) <= 6:
        th, tr = [heads[0]] + [r[0] for r in rows], [[heads[1]] + [r[1] for r in rows]]
        if _col_widths(th, tr, avail):          # 横排后仍放得下才转
            heads, rows = th, tr
            log.add(number, "资料表格", "两列长表改为横排", title, "表头行为原第一列，第二行为原第二列，数据不变")
    widths = _col_widths(heads, rows, avail)
    font = TABLE_PT
    if widths is None:
        font = 9.0
        widths = _col_widths(heads, rows, avail * TABLE_PT / font)
        log.add(number, "资料表格", "表格过宽，改用小五号", title, "")
    out = [f'<div class="tbl" data-cols="{len(widths or [])}">']
    css = [] if font == TABLE_PT else [f"font-size:{font}pt"]
    if widths:
        css.append(f"width:{sum(widths):.2f}em")
        out.append(f'<table class="fixed" style="{";".join(css)}">')
    else:
        out.append(f'<table style="{";".join(css)}">' if css else "<table>")
    if title:   # 表题用 caption，宽度随表格，长表题在表宽内折行
        out.append(f'<caption class="tbl-title">{inline_html(title)}</caption>')
    if widths:
        out.append("<colgroup>" + "".join(f'<col style="width:{w:.2f}em">' for w in widths) + "</colgroup>")
    if heads:
        out.append("<tr>" + "".join(f"<th>{_head_html(h)}</th>" for h in heads) + "</tr>")
    for row in rows:
        cells = []
        for i, c in enumerate(row):
            head_col = (i == 0 and not re.fullmatch(r"[\d.%−\-—]*", c or ""))
            cls = ' class="rowhead"' if head_col else ""
            cells.append(f"<td{cls}>{inline_html(c)}</td>")
        out.append("<tr>" + "".join(cells) + "</tr>")
    out.append("</table>")
    notes = (block.get("notes") or "").strip()
    if notes:
        shown = notes
        for pat, rep in EDITORIAL_NOTE:
            shown = pat.sub(rep, shown)
        if shown != notes:
            log.add(number, "资料表格", "备注中的转写说明改为考生用语", notes, shown)
        # 说明“—”含义的句子对考生有用（不能把未给出的数据当0），无论措辞如何都保留
        kept = [x for x in re.split(r"(?<=[。；])", shown)
                if x.strip() and (not NOTE_META.search(x) or "—" in x)]
        if "".join(kept) != shown:
            log.add(number, "资料表格", "删去只说明转写过程的备注句", shown, "".join(kept))
        shown = "".join(kept)
        if shown.strip() and shown.strip() not in ("备注：", "注："):
            out.append(f'<div class="tbl-note">{inline_html(shown)}</div>')
    out.append("</div>")
    return "".join(out)


def _head_html(h: str) -> str:
    """表头里的单位括号整体不拆行，只在括号前折行（避免“（亿人/次）”）。"""
    parts = re.split(r"([（(][^）)]*[）)])", h)
    return "".join(f'<span class="nobr">{inline_html(x)}</span>' if x[:1] in "（(" else inline_html(x)
                   for x in parts if x)


def table_width_em(block: dict, avail: float = TEXT_WIDTH_EM) -> float | None:
    heads, rows = list(block.get("headers") or []), block.get("rows") or []
    w = _col_widths(heads, [list(r) for r in rows], avail)
    return sum(w) if w else None


def figure_options_html(q: dict, sizer: "FigureSizer", log: Log) -> str:
    """选项为图（如资料分析的饼图选项）：原印刷尺寸，四列放得下排一行，否则两列，两列也放不下就一行一幅。"""
    n = q["number"]
    cells, widths = [], []
    for k in sorted(q["options"]):
        figs = [b for b in q["options"][k] if b["type"] == "figure"]
        texts = [b["text"] for b in q["options"][k] if b["type"] == "text"]
        if len(figs) != 1:
            raise SystemExit(f"第{n}题选项{k}应恰含一幅图，实际{len(figs)}幅")
        w, h, how = sizer.size_mm(figs[0])
        widths.append(w)
        src = (REPO / figs[0]["path"]).as_uri()
        log.add(n, f"选项{k}图", "题图尺寸", figs[0]["path"], f"{w:.1f}×{h:.1f}mm（{how}）")
        cap = f'<span class="optfig-text">{inline_html("".join(texts))}</span>' if texts else ""
        cells.append(f'<div class="optfig"><span class="lab">{k}.</span>'
                     f'<img src="{src}" style="width:{w:.2f}mm;height:{h:.2f}mm" alt="">{cap}</div>')
    # 四列放得下排一行，两列放得下排两行，再宽（如原卷一行一幅的饼图选项）一行一幅
    cols = 4 if 4 * max(widths) + 3 * 8 <= 152.4 else 2 if 2 * max(widths) + 8 <= 152.4 else 1
    log.add(n, "选项", "图形选项排法", f"{len(cells)}幅", f"每行{cols}幅")
    return f'<div class="opts figs" style="grid-template-columns:repeat({cols},1fr)">' + "".join(cells) + "</div>"


def options_html(q: dict, log: Log, sizer: "FigureSizer | None" = None) -> str:
    n = q["number"]
    if any(b["type"] == "figure" for o in q["options"].values() for b in o):
        return figure_options_html(q, sizer or FigureSizer(), log)
    if q["question_type"] == "true_false":
        items = [("A", "正确"), ("B", "错误")]
        return ('<div class="opts c2 fixed">'
                + "".join(f'<div class="opt"><span class="lab">{k}.</span>{v}</div>' for k, v in items)
                + "</div>")
    if options_in_figure(q):
        if q.get("options_mode") != "in_figure":
            log.add(q["number"], "选项", "选项在题图中，占位文字不印", "".join(b["text"] for b in q["options"]["A"]), "")
        return ""  # 选项画在题图中；题库里的“见题图中标为A的选项”是占位说明，不印
    blocks = []
    multi = False
    for k in sorted(q["options"]):
        parts = []
        for b in q["options"][k]:
            if b["type"] == "text":
                paras = reflow(norm_text(b["text"], n, f"选项{k}", log), n, f"选项{k}", log)
                if len(paras) > 1:
                    multi = True
                parts.extend(inline_html(p) for p in paras)
            else:
                raise SystemExit(f"第{n}题选项{k}含非文字块（{b['type']}），需扩展排版器")
        first, rest = parts[0], parts[1:]
        body = f'<p><span class="lab">{k}.</span>{first}</p>' + "".join(f"<p>{r}</p>" for r in rest)
        blocks.append(f'<div class="opt">{body}</div>')
    cls = "opts c1 fixed" if multi else "opts auto"
    return f'<div class="{cls}">' + "".join(blocks) + "</div>"


def question_html(q: dict, sizer: FigureSizer, log: Log) -> str:
    n = q["number"]
    stem_parts: list[str] = []
    texts = [b for b in q["stem"] if b["type"] == "text"]
    for b in q["stem"]:
        if b["type"] == "text":
            ps = paragraphs_html(b["text"], n, "题干", log)
            stem_parts.extend(ps)
        elif b["type"] == "figure":
            stem_parts.append(figure_html(b, sizer, n, log))
        elif b["type"] == "table":
            stem_parts.append(table_html(b, n, log))
        else:
            raise SystemExit(f"第{n}题含未知题干块：{b['type']}")
    if q["question_type"] == "true_false":
        last = texts[-1]["text"] if texts else ""
        if not re.search(r"（[ 　]*）\s*$|\([ 　]*\)\s*$", last):
            # 判断题题末加答题括号（粉笔样卷与广东原卷均有）
            idx = max(i for i, s in enumerate(stem_parts) if s.startswith("<p"))
            stem_parts[idx] = stem_parts[idx][:-4] + BRACKET + "</p>"
            log.add(n, "题干", "判断题题末加答题括号", last[-10:], last[-10:] + BRACKET)
    # 题号挂在第一段左侧；约6行以内的短题整题不跨页（长题仍可在题干与选项间分页，同粉笔样卷）
    num = f'<span class="num">{n}.</span>'
    # 资料分析题不整题保护：资料组是否在同一对开页由 spread_pass 负责，组内跨左右页不影响作答
    has_fig = any(b["type"] in ("figure", "table") for b in q["stem"]) or \
        any(b["type"] == "figure" for o in q["options"].values() for b in o)
    if q.get("materials"):
        keep = ""
    elif n in TURN_KEEPS:
        keep = " keep"      # 第二遍排版发现它跨过翻页，整题移到下一页
    elif has_fig:
        keep = " keep"      # 带图、带表的题整题不跨页（题干、图表、选项在同一页），避免题干与图表被翻页隔开
    else:
        keep = " keep" if _estimated_lines(q) <= 6 else ""
    out = (f'<div class="q{keep}" id="q{n}" data-n="{n}">{num}<div class="stem">' + "".join(stem_parts)
           + "</div>" + options_html(q, log, sizer) + "</div>")
    if any(("横线" in b["text"] or "画线" in b["text"]) for b in texts) \
            and 'class="blank"' not in out and 'class="ul"' not in out:
        raise SystemExit(f"第{n}题题面提到横线，但没有可印出的填空线或下划线")
    return out


def block_html(block: dict, number, log: Log) -> str:
    """专项的方法要点框：标题一行（黑体），要点逐条（宋体）。"""
    head = f'<p class="tips-h">方法要点｜{html.escape(block["title"])}</p>'
    pts = "".join(f"<p>{inline_html(norm_text(t, number, '方法要点', log))}</p>" for t in block.get("points") or [])
    return f'<div class="tips">{head}{pts}</div>'


def _estimated_lines(q: dict) -> float:
    """估算题目所占行数（每行36字）。含图或表的题不算短题。"""
    import math
    if any(b["type"] != "text" for b in q["stem"]):
        return 99
    lines = sum(math.ceil(max(1.0, _width(p)) / 36) for b in q["stem"] for p in b["text"].split("\n") if p.strip())
    if q["question_type"] == "true_false":
        return lines + 1
    if options_in_figure(q) or any(b["type"] != "text" for o in q["options"].values() for b in o):
        return 99
    widths = [_width("A." + "".join(b["text"] for b in o)) for o in q["options"].values()]
    w = max(widths or [0])
    if w <= 8:
        lines += 1
    elif w <= 17:
        lines += 2
    else:
        lines += sum(math.ceil(x / 36) for x in widths)
    return lines


# 第二遍排版时需要另起左页的资料组（见 spread_pass）
SPREAD_BREAKS: set[str] = set()


def material_html(m: dict, log: Log, first_q: int) -> str:
    cls = "material newpage" if m["id"] in SPREAD_BREAKS else "material"
    out = [f'<div class="{cls}" data-mid="{html.escape(m["id"])}">']
    blocks = m["blocks"]
    i = 0
    while i < len(blocks):
        b = blocks[i]
        if b["type"] == "text":
            out.extend(paragraphs_html(b["text"], first_q, "资料文字", log, cls="mtext"))
        elif b["type"] == "table":
            nxt = blocks[i + 1] if i + 1 < len(blocks) else None
            half = TEXT_WIDTH_EM / 2 - 1.5
            w1 = table_width_em(b, half)
            w2 = table_width_em(nxt, half) if nxt and nxt["type"] == "table" else None
            # 相邻两张窄表并排（正文格不折行时各能放进半个版心，表头可折行）；带备注的表需要整行宽，不并排
            noted = bool((b.get("notes") or "").strip() or (nxt and (nxt.get("notes") or "").strip()))
            if w1 and w2 and not noted:
                out.append('<div class="tbl-pair">' + table_html(b, first_q, log, half)
                           + table_html(nxt, first_q, log, half) + "</div>")
                log.add(first_q, "资料表格", "两张窄表并排", f"{b.get('title')} / {nxt.get('title')}", "")
                i += 2
                continue
            out.append(table_html(b, first_q, log))
        elif b["type"] == "figure":
            out.append(figure_html(b, FigureSizer(), first_q, log, in_material=True))
        elif b["type"] == "chart":
            out.append(chart_html(b, first_q, log))
        else:
            raise SystemExit(f"资料含未知块：{b['type']}")
        i += 1
    out.append("</div>")
    return "".join(out)


OPTION_SCRIPT = r"""
<script>
window.__layout = function () {
  const pt = px => px * 72 / 96;
  const out = [];
  document.querySelectorAll('.opts.auto').forEach(el => {
    const probe = document.createElement('span');
    probe.style.cssText = 'position:absolute;visibility:hidden;white-space:nowrap;left:0;top:0';
    document.body.appendChild(probe);
    let max = 0;
    el.querySelectorAll('.opt').forEach(o => {
      probe.innerHTML = o.querySelector('p').innerHTML;
      max = Math.max(max, pt(probe.getBoundingClientRect().width));
    });
    probe.remove();
    // 9字网格：一格108pt，留一字空隙
    const cls = max <= 96 ? 'c4' : (max <= 204 ? 'c2' : 'c1');
    el.classList.add(cls);
    const q = el.closest('.q');
    out.push({q: q ? +q.dataset.n : null, widest_pt: Math.round(max * 10) / 10, columns: cls});
  });
  return out;
};
</script>
"""


def absent_sections(missing: list[int], present: list[str], name: str, first: bool) -> list[tuple[str, int, int]]:
    """整个部分都空着（如M11常识判断第11—15题、加量套第1—15题）时，在它前面的部分说明里注明；
    排在第一个部分之前的，注在第一个部分。返回 [(部分名, 起, 止)]，按题号顺序。"""
    names = list(SECTION_RANGES)
    gone = {n for n, (lo, hi) in SECTION_RANGES.items()
            if n not in present and all(x in missing for x in range(lo, hi + 1))}
    i = names.index(name) if name in names else None
    if i is None:
        return []
    out = []
    if first:
        for n in names[:i]:
            if n in gone:
                out.append((n, *SECTION_RANGES[n]))
    for n in names[i + 1:]:
        if n not in gone:
            break
        out.append((n, *SECTION_RANGES[n]))
    return out


def body_html(paper_id: str, questions: list[dict], css_href: str, fonts_href: str, log: Log) -> str:
    sizer = FigureSizer()
    by_part: list[tuple[dict, list[dict]]] = []
    used = set()
    for part in PARTS:
        qs = [q for q in questions if q["section"] in part["match"]]
        if qs:
            by_part.append((part, qs))
            used.update(q["number"] for q in qs)
    leftover = [q["number"] for q in questions if q["number"] not in used]
    if leftover:
        raise SystemExit(f"以下题目的 section 无法归入考场部分：{leftover}")
    # 题号须连续且各部分按顺序
    order = [q["number"] for _, qs in by_part for q in qs]
    # 题号须递增且各部分按顺序；M09起政治常识材料不够时会空出题位（编排 skip），其余题号不变，
    # 空出的题号在所属部分的说明后注明
    missing = sorted(set(range(1, max(order) + 1)) - set(order))
    if order != sorted(order) or len(set(order)) != len(order) or (missing and max(order) != 90):
        raise SystemExit(f"题号不连续或部分顺序与原卷不符：{order}")
    if missing:
        log.add(None, "空题位", "本套没有第" + "、".join(map(str, missing)) + "题，在所属部分的说明后注明", "", "")

    out = [
        "<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\">",
        f"<title>{paper_id}</title>",
        f'<link rel="stylesheet" href="{fonts_href}"><link rel="stylesheet" href="{css_href}">',
        OPTION_SCRIPT,
        "</head><body>",
    ]
    for pi, (part, qs) in enumerate(by_part):
        ordinal = cn_number(pi + 1)
        out.append('<section class="part">')
        out.append(f'<h1 class="part-title">第{ordinal}部分　{part["name"]}</h1>')
        table = group_table(part)
        if table:
            keys = []
            for q in qs:
                k = group_key(part, q)
                if k not in table:
                    raise SystemExit(f"第{q['number']}题的题型“{k}”没有对应的考场说明，需在 build_print.py 中补充")
                if k not in keys:
                    keys.append(k)
            labels = []
            for k in keys:
                if table[k][0] not in labels:
                    labels.append(table[k][0])
            intro = f"本部分包括{_join_types(labels)}{COUNT_WORD.get(len(labels), str(len(labels)))}种类型的试题。"
            if part.get("kind") == "politics":
                intro = f"本部分包括{'、'.join(labels)}{COUNT_WORD.get(len(labels), str(len(labels)))}种类型的试题。"
            out.append(f'<p class="instr">{html.escape(intro)}</p>')
        else:
            for t in part["intro"]:
                out.append(f'<p class="instr">{html.escape(t)}</p>')
        lo, hi = SECTION_RANGES.get(part["name"], (qs[0]["number"], qs[-1]["number"]))
        gap = [x for x in missing if lo <= x <= hi]
        notes = [f'本部分没有第{"、".join(map(str, gap))}题'] if gap else []
        whole = absent_sections(missing, [p["name"] for p, _ in by_part], part["name"], first=pi == 0)
        if whole:
            names = "、".join(n for n, _, _ in whole)
            notes.append(f"本套不出{names}（第{whole[0][1]}—{whole[-1][2]}题）")
        if notes:
            out.append(f'<p class="instr">{"；".join(notes)}，答题卡上这几题不填涂。</p>')
        out.append('<p class="instr">请开始答题：</p>')

        current = None
        gi = 0
        seen_materials = set()
        for q in qs:
            if table:
                k = group_key(part, q)
                label = table[k][0]
                if label != current:
                    current = label
                    gi += 1
                    n = sum(1 for x in qs if table[group_key(part, x)][0] == label)
                    out.append(f'<p class="instr">{html.escape(table[k][1].format(ord=cn_number(gi), n=n))}</p>')
            for m in q.get("materials") or []:
                if m["id"] not in seen_materials:
                    seen_materials.add(m["id"])
                    out.append(material_html(m, log, q["number"]))
            if q.get("block"):      # 专项：每类题前印方法要点
                out.append(block_html(q["block"], q["number"], log))
            out.append(question_html(q, sizer, log))
        if pi + 1 < len(by_part):
            end = f"※※※ 第{ordinal}部分结束，请继续做第{cn_number(pi + 2)}部分！※※※"
        else:
            end = "※※※ 全部测验到此结束！※※※"
        out.append(f'<p class="part-end">{end}</p>')
        out.append("</section>")
    out.append("</body></html>")
    return "\n".join(out)


# --------------------------------------------------------------------------
# 封面与注意事项（粉笔样卷封面布局；注意事项按中公样卷，排在封面背面）
# --------------------------------------------------------------------------
def front_html(paper_no: int, n_parts: int, n_questions: int, minutes: int, subtitle: str,
               badge: str, fonts_href: str, with_notice: bool, extra: bool = False,
               title: str | None = None, tips: list[str] | None = None) -> str:
    # 加量套（S01起）标题注“加量”，与主套（M01—M18）区分；专项另给标题和提示
    title = title or f"行政职业能力测验（{'加量' if extra else ''}{cn_number(paper_no)}）"
    tip_ps = "".join(f"<p>{html.escape(t)}</p>" for t in tips) if tips else (
        "<p>为维护您的个人权益，确保考试的公平公正，请您协助我们监督考试实施工作。</p>"
        "<p>本场考试规定：监考老师要向本考场全体考生展示题本密封情况，并邀请<span class=\"m-r\">2</span>名考生代表验封签字后，方能开启试卷袋。</p>")
    badge_html = "<br>".join(html.escape(x) for x in badge.split("|"))
    notice = ""
    if with_notice:
        items = [
            f"行政职业能力测验共有{cn_number(n_parts)}个部分，{n_questions}道题，总时限为{minutes}分钟。",
            "将姓名与准考证号在指定位置上用黑色字迹的钢笔、签字笔或圆珠笔填写，并用2B铅笔在准考证号对应的数字上填涂。",
            "请将题本上的条形码揭下，贴在答题卡指定位置。没有贴条形码的答题卡将按作废处理，成绩计为零分。",
            "题目应在答题卡上作答，在题本上作答一律无效。",
            "待监考老师宣布考试开始后，你才可以开始答题。",
            "监考老师宣布考试结束时，你应立即停止作答，将题本、答题卡和草稿纸都翻过来放在桌上，待监考老师确认数量无误、发出离开指令后，方可离开考场。",
            "试题答错不倒扣分。",
            "严禁折叠答题卡！",
        ]
        lis = "".join(f'<p class="item"><span class="m-r">{i}</span>．{html.escape(t)}</p>' for i, t in enumerate(items, 1))
        notice = f"""
<section class="sheet notice">
  <h1>注　意　事　项</h1>
  {lis}
  <div class="stars">
    <div class="row">※※※※※※※※※※※※※※※※※※※※※※※※※</div>
    <div class="row mid"><span>※</span><span>请认真听取监考人员的指令。</span><span>※</span></div>
    <div class="row mid"><span>※</span><span>否则，会影响你的成绩。</span><span>※</span></div>
    <div class="row">※※※※※※※※※※※※※※※※※※※※※※※※※</div>
  </div>
</section>"""
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>封面</title>
<link rel="stylesheet" href="{fonts_href}">
<style>
@page {{ size: 210mm 297mm; margin: 0; }}
html {{ font-family: "ZG Latin", "ZG Song"; color: #000; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
body {{ margin: 0; }}
.sheet {{ position: relative; width: 210mm; height: 297mm; overflow: hidden; break-after: page; }}
.sheet:last-child {{ break-after: auto; }}
.hei {{ font-family: "ZG LatinB", "ZG Hei"; }}
.m-r {{ font-family: "ZG Latin"; }}
/* 左侧装订线与竖排信息栏 */
.bind {{ position: absolute; left: 26.6mm; top: 0; height: 297mm; border-left: 0.75pt dotted #000; }}
.cut {{ position: absolute; left: 26.6mm; right: 0; top: 190.1mm; border-top: 0.75pt dotted #000; }}
.vfield {{ position: absolute; display: flex; align-items: flex-end; font-family: "ZG LatinB", "ZG Hei";
          font-size: 13pt; line-height: 1; transform: translate(-50%, -50%) rotate(-90deg); white-space: nowrap; }}
.vfield .line {{ display: inline-block; border-bottom: 0.75pt solid #000; margin-left: 1mm; height: 1px; }}
.badge {{ position: absolute; left: 160mm; top: 12.2mm; width: 25.8mm; height: 15.4mm; box-sizing: border-box;
         border: 0.9pt solid #000; background: #d9d9d9; display: flex; align-items: center; justify-content: center;
         text-align: center; font-family: "ZG LatinB", "ZG Hei"; font-size: 13.5pt; line-height: 16.5pt; }}
.center {{ position: absolute; left: 26.6mm; right: 0; text-align: center; }}
.subtitle {{ top: 55.2mm; font-family: "ZG LatinB", "ZG Hei"; font-size: 15pt; line-height: 1; }}
.title {{ top: 64.6mm; font-family: "ZG LatinB", "ZG Hei"; font-size: 28pt; line-height: 1.15; }}
.tip-h {{ position: absolute; left: 57.6mm; top: 98.4mm; font-family: "ZG LatinB", "ZG Hei"; font-size: 14pt; line-height: 1; }}
.tip {{ position: absolute; left: 57.6mm; width: 123.5mm; top: 105.2mm; font-family: "ZG Latin", "ZG Kai";
       font-size: 14pt; line-height: 27pt; text-align: justify; }}
.tip p {{ margin: 0; text-indent: 2em; }}
.barcode {{ position: absolute; left: 69mm; top: 202.2mm; width: 21.3mm; height: 58.8mm; box-sizing: border-box;
           border: 0.9pt solid #555; border-radius: 2.6mm; background: #c9c9c9; }}
.barcode .inner {{ position: absolute; inset: 1.4mm; border: 0.6pt dashed #333; border-radius: 1.6mm;
                  display: flex; align-items: center; justify-content: center; }}
.barcode .txt {{ writing-mode: vertical-rl; font-family: "ZG LatinB", "ZG Hei"; font-size: 12pt; letter-spacing: 2.5mm;
                line-height: 1; margin-top: 2.5mm; }}
.peel {{ position: absolute; left: 116.5mm; top: 223.4mm; font-family: "ZG LatinB", "ZG Hei"; font-size: 15pt; line-height: 29pt; }}
/* 注意事项 */
.notice h1 {{ position: absolute; top: 33mm; left: 29.3mm; right: 28.3mm; margin: 0; text-align: center;
             font-family: "ZG LatinB", "ZG Hei"; font-weight: normal; font-size: 18pt; line-height: 1; }}
.notice .item {{ position: relative; left: 29.3mm; width: 152.4mm; margin: 0; text-indent: 2em; text-align: justify;
                font-family: "ZG Latin", "ZG Kai"; font-size: 14pt; line-height: 27pt; }}
.notice .item:first-of-type {{ margin-top: 55mm; }}
.stars {{ position: relative; left: 29.3mm; width: 152.4mm; margin-top: 16mm; font-family: "ZG LatinB", "ZG Hei";
         font-size: 14pt; line-height: 31pt; }}
.stars .row {{ display: flex; justify-content: center; letter-spacing: 0; }}
.stars .mid {{ justify-content: space-between; width: 350pt; margin: 0 auto; }}
.stars .row:not(.mid) {{ width: 350pt; margin: 0 auto; justify-content: space-between; overflow: hidden; }}
</style></head><body>
<section class="sheet cover">
  <div class="bind"></div>
  <div class="cut"></div>
  <div class="vfield" style="left:18.6mm; top:84.6mm">准考证号<span class="line" style="width:49mm"></span></div>
  <div class="vfield" style="left:18.6mm; top:221.3mm">姓名<span class="line" style="width:51mm"></span></div>
  <div class="badge"><div>{badge_html}</div></div>
  <div class="center subtitle">{html.escape(subtitle)}</div>
  <div class="center title">{html.escape(title)}</div>
  <div class="tip-h">重要提示</div>
  <div class="tip">
    {tip_ps}
  </div>
  <div class="barcode"><div class="inner"><div class="txt">条形码粘贴处</div></div></div>
  <div class="peel">请将此条形码揭下，<br>贴在答题卡指定位置</div>
</section>
{notice}
</body></html>"""


# --------------------------------------------------------------------------
# 渲染与检查
# --------------------------------------------------------------------------
def render(html_path: Path, pdf_path: Path) -> dict:
    node = shutil.which("node")
    if not node:
        raise SystemExit("需要 Node.js 与 playwright（npm i playwright）")
    r = subprocess.run([node, str(HERE / "render_pdf.js"), str(html_path), str(pdf_path)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("渲染失败：\n" + r.stderr[-3000:])
    return json.loads(r.stdout.strip().splitlines()[-1])


# 题图重绘中的标注沿用原图的无衬线字（Liberation Sans/Arial）
ALLOWED_FONT = re.compile(r"(FZSSJW|FZHTJW|FZKTJW|LiberationSerif|TimesNewRoman|Times|LiberationSans|Arial|NotoSerif)", re.I)


LINE_START_BAD = "，。、；：？！）”’」』"


def line_start_punct(pdf: Path, front_pages: int) -> list[tuple[int, str]]:
    """找出以句末标点开头的行。行首若是填空线（下划线不是文字），标点紧跟其后，不算。"""
    import pdfplumber  # type: ignore
    found = []
    with pdfplumber.open(str(pdf)) as doc:
        for i, page in enumerate(doc.pages):
            if i < front_pages:
                continue
            # 按字的竖直中心聚成行：西文数字与汉字基线不同，不能按底边取整分组
            rows: list[list] = []
            for c in sorted((c for c in page.chars if c["text"].strip()), key=lambda c: (c["top"] + c["bottom"]) / 2):
                mid = (c["top"] + c["bottom"]) / 2
                if rows and abs(mid - rows[-1][0]) <= 5:
                    rows[-1][1].append(c)
                else:
                    rows.append([mid, [c]])
            rules = [e for e in page.edges if e["orientation"] == "h"]
            for _, cs in rows:
                first = min(cs, key=lambda c: c["x0"])
                if first["text"] not in LINE_START_BAD:
                    continue
                blank_before = any(abs(e["top"] - first["bottom"]) < 4 and first["x0"] - 50 < e["x1"] <= first["x0"] + 1
                                   for e in rules)
                if not blank_before:
                    line = "".join(c["text"] for c in sorted(cs, key=lambda c: c["x0"]))
                    found.append((i + 1, line[:16]))
    return found


def check_pdf(pdf: Path, numbers: list[int], front_pages: int) -> dict:
    r = subprocess.run(["pdffonts", str(pdf)], capture_output=True, text=True)
    fonts = [ln.split()[0] for ln in r.stdout.splitlines()[2:] if ln.strip()]
    bad = [f for f in fonts if not ALLOWED_FONT.search(f)]
    if bad:
        raise SystemExit(f"PDF中出现非指定字体（缺字回退），需处理：{bad}")
    import pdfplumber  # type: ignore
    page_of = {}
    footers = []
    with pdfplumber.open(str(pdf)) as doc:
        for i, page in enumerate(doc.pages):
            words = page.extract_words(keep_blank_chars=False, use_text_flow=True)
            txt = page.extract_text() or ""
            if i >= front_pages:
                m = re.search(r"第(\d+)页\s*共(\d+)页", txt.replace("　", " "))
                footers.append((int(m.group(1)), int(m.group(2))) if m else None)
            for w in words:
                if i >= front_pages and w["x0"] < 30 * 72 / 25.4 and re.fullmatch(r"\d{1,3}\.", w["text"]):
                    page_of.setdefault(int(w["text"][:-1]), i + 1)
    total_body = len(footers)
    expected = [(k, total_body) for k in range(1, total_body + 1)]
    if footers != expected:
        raise SystemExit(f"页脚页码不连续：{footers}")
    bad_starts = line_start_punct(pdf, front_pages)
    if bad_starts:
        raise SystemExit(f"句末标点落在行首（避头尾失效）：{bad_starts}")
    missing = [k for k in numbers if k not in page_of]
    if missing:
        raise SystemExit(f"PDF中找不到以下题号：{missing}")
    seq = [page_of[k] for k in numbers]
    if seq != sorted(seq):
        raise SystemExit("题号在PDF中的页序不单调")
    return {"字体": fonts, "正文页数": total_body, "题号所在PDF页": page_of}


def spread_pass(body_pdf: Path, questions: list[dict]) -> dict:
    """找出跨过翻页的资料组。正文第1页印在纸张正面（右页），奇数页为右页、偶数页为左页；
    对开页为（偶，奇）。资料从奇数页开始、最后一题落在下一页，即需翻页才能看到题目。"""
    import pdfplumber  # type: ignore
    groups: dict[str, dict] = {}
    prev_section = None
    for q in questions:
        for m in q.get("materials") or []:
            # 部分内第一组资料紧跟部分标题，不能挪走，否则标题页只剩说明
            first_in_part = q["section"] != prev_section and m["id"] not in groups
            g = groups.setdefault(m["id"], {"m": m, "last": q["number"], "lead": first_in_part})
            g["last"] = q["number"]
        prev_section = q["section"]
    if not groups:
        return {}
    with pdfplumber.open(str(body_pdf)) as doc:
        pages = [re.sub(r"\s+", "", p.extract_text() or "") for p in doc.pages]
        qpage = {}
        for i, page in enumerate(doc.pages, 1):
            for w in page.extract_words():
                if w["x0"] < 30 * 72 / 25.4 and re.fullmatch(r"\d{1,3}\.", w["text"]):
                    qpage.setdefault(int(w["text"][:-1]), i)
    moved = {}
    for mid, g in groups.items():
        if mid in SPREAD_BREAKS or g["lead"]:
            continue
        first = next((b for b in g["m"]["blocks"] if b["type"] in ("text", "table", "chart")), None)
        if not first:
            continue
        key = re.sub(r"\s+", "", (first.get("text") or first.get("title") or ""))[:14]
        start = next((i for i, t in enumerate(pages, 1) if key and key in t), None)
        end = qpage.get(g["last"])
        # 已在页首的资料组再加分页也挪不动（除非插空白页），不处理
        at_top = start is not None and pages[start - 1].find(key) < 20
        if start and end and start % 2 == 1 and end == start + 1 and not at_top:
            moved[mid] = (start, end)
    return moved


TURN_KEEPS: set[int] = set()
TURN_KEEP_MAX_LINES = 18     # 约占半页多；更长的题（如长篇阅读）跨页属正常


def _part_starts(body_pdf: Path, questions: list[dict]) -> list[int]:
    """各部分第一题所在页（正文页码）。"""
    import pdfplumber  # type: ignore
    firsts, prev = [], None
    for q in questions:
        if q["section"] != prev:
            firsts.append(q["number"])
        prev = q["section"]
    qpage = {}
    with pdfplumber.open(str(body_pdf)) as doc:
        for i, page in enumerate(doc.pages, 1):
            for w in page.extract_words():
                if w["x0"] < 30 * 72 / 25.4 and re.fullmatch(r"\d{1,3}\.", w["text"]):
                    qpage.setdefault(int(w["text"][:-1]), i)
        total = len(doc.pages)
    return [qpage.get(n, 0) for n in firsts] + [total]


def turn_pass(body_pdf: Path, questions: list[dict]) -> dict:
    """找出跨过翻页的非资料题：从右页（奇数页）开始、最后一个选项落在背面，作答时要来回翻。
    不长于约18行的改为整题不跨页；部分内第一题不动（否则部分标题页只剩标题）。"""
    import pdfplumber  # type: ignore
    with pdfplumber.open(str(body_pdf)) as doc:
        pages = [re.sub(r"\s+", "", p.extract_text() or "") for p in doc.pages]
        qpage = {}
        for i, page in enumerate(doc.pages, 1):
            for w in page.extract_words():
                if w["x0"] < 30 * 72 / 25.4 and re.fullmatch(r"\d{1,3}\.", w["text"]):
                    qpage.setdefault(int(w["text"][:-1]), i)
    found = {}
    prev_section = None
    for q in questions:
        n = q["number"]
        first_in_part = q["section"] != prev_section
        prev_section = q["section"]
        if first_in_part or q.get("materials") or n in TURN_KEEPS or n not in qpage:
            continue
        start = qpage[n]
        if start % 2 == 0:
            continue
        if options_in_figure(q) or not q["options"]:
            continue
        last_opt = "".join(b.get("text", "") for b in q["options"][sorted(q["options"])[-1]] if b["type"] == "text")
        key = re.sub(r"\s+", "", norm_text(last_opt, n, "核对", Log()))
        key = re.split(r"\$|_{3,}", key)[0][:12]
        if len(key) < 2:
            continue
        end = next((i for i in range(start, min(start + 2, len(pages)) + 1) if key in pages[i - 1]), None)
        if end == start + 1 and _estimated_lines(q) <= TURN_KEEP_MAX_LINES:
            found[n] = (start, end)
    return found


def _expected_segments(q: dict) -> list[str]:
    """按排版时同样的规范化，取出该题应出现在PDF里的文字片段（数学式、填空线处切开）。"""
    quiet = Log()
    texts = []
    for m in q.get("materials") or []:          # 资料印在题目之前
        texts += [b["text"] for b in m["blocks"] if b["type"] == "text"]
    texts += [b["text"] for b in q["stem"] if b["type"] == "text"]
    if not options_in_figure(q):
        texts += [b["text"] for k in sorted(q["options"]) for b in q["options"][k] if b["type"] == "text"]
    segs = []
    for t in texts:
        for para in reflow(norm_text(t, q["number"], "核对", quiet), q["number"], "核对", quiet):
            for piece in re.split(r"\$[^$]+\$|_{3,}", re.sub(r"</?u>", "", para)):
                piece = re.sub(r"\s+", "", piece)
                if len(piece) >= 2:
                    segs.append(piece)
    return segs


def verify_content(pdf: Path, questions: list[dict], front_pages: int) -> dict:
    """逐题核对：题干、选项、资料文字按顺序出现在PDF文字层中；表格数值逐格出现。"""
    import pdfplumber  # type: ignore

    def normal_size(obj) -> bool:
        # 上下标、分数（约8—9pt）和题图标注会被抽到别的行，核对时去掉；正文12pt、表格10.5pt保留
        return obj.get("object_type") != "char" or obj.get("size", 12) >= 9.8
    with pdfplumber.open(str(pdf)) as doc:
        text = "".join((p.filter(normal_size).extract_text() or "") for p in doc.pages[front_pages:])
        # 统计图里的数值用小字号（约7.5pt），另取不按字号过滤的全文核对
        flat_all = re.sub(r"\s+", "", "".join((p.extract_text() or "") for p in doc.pages[front_pages:]))
    text = re.sub(r"第\d+页\s*共\d+页", "", text)
    flat = re.sub(r"\s+", "", text)
    pos = 0
    missing = []
    seen_mat = set()
    checked = 0
    for q in questions:
        mats = [m for m in q.get("materials") or [] if m["id"] not in seen_mat]
        q2 = dict(q, materials=mats)
        for seg in _expected_segments(q2):
            j = flat.find(seg, pos)
            if j < 0:
                missing.append((q["number"], seg[:30]))
            else:
                pos = j + len(seg)
                checked += 1
        for m in mats:
            seen_mat.add(m["id"])
            for b in m["blocks"]:
                if b["type"] == "chart":
                    for c in [b.get("title") or ""] + list(b.get("values") or []):
                        c2 = re.sub(r"\s+", "", str(c))
                        if len(c2) >= 2 and c2 not in flat_all:
                            missing.append((q["number"], "统计图：" + c2))
                        elif len(c2) >= 2:
                            checked += 1
                if b["type"] == "table":
                    for row in b.get("rows") or []:
                        for c in row:
                            c2 = re.sub(r"\s+", "", c)
                            if len(c2) >= 2 and c2 not in EDITORIAL_CELL and c2 not in flat:
                                missing.append((q["number"], "表格：" + c2))
                            elif len(c2) >= 2:
                                checked += 1
    if missing:
        raise SystemExit(f"PDF文字与题目.jsonl不一致（按序未找到）：{missing[:12]}")
    return {"已核对片段数": checked}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paper_id", help="如 M01")
    ap.add_argument("--font-dir", type=Path, default=None, help="方正书宋/黑体/楷体所在目录（不入库）")
    ap.add_argument("--subtitle", default="广东行测18套模拟")
    ap.add_argument("--badge", default="仅供个人|练习使用", help="封面右上角方框文字，用|分行")
    ap.add_argument("--minutes", type=int, default=90, help="注意事项中的总时限")
    ap.add_argument("--flow", action="store_true", help="各部分接着排、不另起页（专项练习本用）")
    ap.add_argument("--title", default=None, help="封面标题（专项等用）；默认“行政职业能力测验（一）”式")
    ap.add_argument("--cover-tip", action="append", default=None, help="封面“重要提示”各段（可多次给）；默认考场提示")
    ap.add_argument("--no-notice", action="store_true", help="不印封面背面的注意事项")
    ap.add_argument("--out", type=Path, default=None, help="输出目录，默认 <套卷>/打印版/")
    ap.add_argument("--keep-html", action="store_true")
    ap.add_argument("--avoid-page-turns", action="store_true",
                    help="为阅读方便挪动版面：资料组另起左页、跨过翻页的题整题移页。默认不挪，按实考样子顺排")
    ap.add_argument("--spread-data-groups", action="store_true",
                    help="只做资料组另起左页（M01、M02打印版按此生成，用于原样重建）")
    args = ap.parse_args()

    paper_dir = PROJECT / args.paper_id
    qfile = paper_dir / "题目.jsonl"
    if not qfile.exists():
        raise SystemExit(f"找不到 {qfile}")
    questions = [json.loads(l) for l in qfile.read_text(encoding="utf-8").splitlines() if l.strip()]
    questions.sort(key=lambda q: q["number"])
    meta = json.loads((paper_dir / "paper.json").read_text(encoding="utf-8")) if (paper_dir / "paper.json").exists() else {}
    m = re.search(r"(\d+)$", args.paper_id)
    paper_no = int(m.group(1)) if m else 1

    fonts = find_fonts(args.font_dir)
    global REDRAWS, ADJUST
    REDRAWS = Redraws()
    ADJUST = SizeAdjust()
    out_dir = args.out or (paper_dir / "打印版")
    out_dir.mkdir(parents=True, exist_ok=True)
    log = Log()
    apply_whitespace_fixes(args.paper_id, questions, log)
    check_glyphs(questions, fonts, log)

    with tempfile.TemporaryDirectory(prefix="print_") as td:
        tdp = Path(td)
        (tdp / "fonts.css").write_text(fonts_css(fonts), encoding="utf-8")
        shutil.copy(HERE / "exam.css", tdp / "exam.css")
        if args.flow:   # 专项练习本：各部分接着排，不另起页
            with open(tdp / "exam.css", "a", encoding="utf-8") as fcss:
                fcss.write("\n.part { break-before: auto; margin-top: 20pt; }\n.part:first-child { margin-top: 0; }\n"
                           ".instr, .part-title { break-inside: avoid; }\n")   # 部分标题、说明不拆在两页
        body = body_html(args.paper_id, questions, "exam.css", "fonts.css", log)
        (tdp / "body.html").write_text(body, encoding="utf-8")
        n_parts = body.count('<section class="part">')
        front = front_html(paper_no, n_parts, len(questions), args.minutes, args.subtitle, args.badge,
                           "fonts.css", not args.no_notice, extra=bool(re.match(r"(_试排)?S\d", args.paper_id)),
                           title=args.title, tips=args.cover_tip)
        (tdp / "front.html").write_text(front, encoding="utf-8")

        layout = render(tdp / "body.html", tdp / "body.pdf")
        # 默认按实考样子顺排：资料组跨翻页、题目跨页都照常发生，不为阅读方便另行挪动。
        # --avoid-page-turns 时才做下面两遍（M01、M02打印版生成时用过第二遍）。
        # 第二遍：资料组若跨过翻页（从右页开始、延续到背面），改从下一个左页开始，使材料与题目同在一个对开页
        for _ in range(3 if (args.avoid_page_turns or args.spread_data_groups) else 0):
            moved = spread_pass(tdp / "body.pdf", questions)
            if not moved:
                break
            for mid, (a, b) in moved.items():
                log.add(None, "资料组", "资料组另起左页，与题目同在一个对开页", f"{mid}：原在正文第{a}—{b}页", "")
            SPREAD_BREAKS.update(moved)
            body = body_html(args.paper_id, questions, "exam.css", "fonts.css", Log())
            (tdp / "body.html").write_text(body, encoding="utf-8")
            layout = render(tdp / "body.html", tdp / "body.pdf")
        # 第三遍：非资料题若从右页开始、延续到背面（不长于约18行），逐题试着整题移到下一页。
        # 只接受不改变其后各部分起始页的移动，即只用本部分末尾的空白，不连锁推后资料分析等后面的版面。
        base_starts = _part_starts(tdp / "body.pdf", questions)
        tried: set[int] = set()
        for _ in range(12 if args.avoid_page_turns else 0):
            cand = {n: v for n, v in turn_pass(tdp / "body.pdf", questions).items() if n not in tried}
            if not cand:
                break
            n, (a, b) = min(cand.items())
            tried.add(n)
            TURN_KEEPS.add(n)
            body = body_html(args.paper_id, questions, "exam.css", "fonts.css", Log())
            (tdp / "trial.html").write_text(body, encoding="utf-8")
            render(tdp / "trial.html", tdp / "trial.pdf")
            if _part_starts(tdp / "trial.pdf", questions) == base_starts:
                log.add(n, "分页", "跨过翻页的题整题移到下一页", f"原在正文第{a}—{b}页", "")
                shutil.copy(tdp / "trial.pdf", tdp / "body.pdf")
                (tdp / "body.html").write_text(body, encoding="utf-8")
            else:
                TURN_KEEPS.discard(n)
                log.add(n, "分页", "跨过翻页但保留原样", f"正文第{a}—{b}页",
                        "整题移页会使后面各部分整体后移")
        if tried:
            body = body_html(args.paper_id, questions, "exam.css", "fonts.css", Log())
            (tdp / "body.html").write_text(body, encoding="utf-8")
            layout = render(tdp / "body.html", tdp / "body.pdf")
        render(tdp / "front.html", tdp / "front.pdf")

        from pypdf import PdfWriter  # type: ignore
        writer = PdfWriter()
        writer.append(str(tdp / "front.pdf"))
        writer.append(str(tdp / "body.pdf"))
        pdf_path = out_dir / f"{Path(args.paper_id).name}_题本_打印版.pdf"   # 专项按“专项/D1”给路径，文件名只取末段
        writer.add_metadata({"/Title": f"{args.subtitle} {args.paper_id} 行政职业能力测验题本",
                             "/Creator": "广东行测18套模拟/打印排版/build_print.py"})
        with open(pdf_path, "wb") as fh:
            writer.write(fh)
        if args.keep_html:
            for name in ("body.html", "front.html", "fonts.css", "exam.css"):
                shutil.copy(tdp / name, out_dir / name)

    front_pages = 1 if args.no_notice else 2
    report = check_pdf(pdf_path, [q["number"] for q in questions], front_pages)
    content = verify_content(pdf_path, questions, front_pages)
    import hashlib
    summary = {
        "套卷": args.paper_id,
        "底稿版本": meta.get("version"),
        "底稿状态": meta.get("status"),
        "题目.jsonl_SHA256": hashlib.sha256(qfile.read_bytes()).hexdigest(),
        "PDF内容核对": f"题干、选项、资料文字按序与题目.jsonl一致，表格数值逐格出现；共{content['已核对片段数']}个片段",
        "生成时间": _dt.datetime.now(_dt.timezone(_dt.timedelta(hours=8))).isoformat(timespec="seconds"),
        "版式": "粉笔样卷：A4；小四正文36字/行，行距22.9pt；题号悬挂；选项9字网格；每部分另起一页",
        "字体": {k: v.name for k, v in fonts.items()},
        "PDF总页数": front_pages + report["正文页数"],
        "封面及注意事项页数": front_pages,
        "正文页数": report["正文页数"],
        "PDF内嵌字体": report["字体"],
        "题号所在PDF页": report["题号所在PDF页"],
        "选项排法": layout.get("decisions"),
        "排版层面处理": log.items,
    }
    (out_dir / "排版日志.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    shown = pdf_path.relative_to(REPO) if pdf_path.is_relative_to(REPO) else pdf_path
    print(f"已生成 {shown}：共{summary['PDF总页数']}页（正文{report['正文页数']}页），"
          f"排版处理{len(log.items)}项，见 排版日志.json")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""广东行测旧卷（2013—2021）整卷结构化工具。

输出格式与 广东/行测/2022-2026 题库一致（字段见 ../schema.json）。自动完成：文字分题、选项拆分、
行内小图（分数、根号、公式）占位、题图/材料图定位与 288 DPI 裁剪、答案文字层提取、扫描版答案页的候选行拼图、
文字守恒与裁图检查。人工判断写在每卷自己的修正文件里，build 读取后套用。

命令
  dump <卷> [--apply]          自动分题结果（默认不套用修正；--apply 套用行内小图文字、figure_questions、
                               option_splits、option_figures），供核对、编写修正文件
  answer-sheet <卷> [--work D] 扫描版答案 PDF：按两种解析格式裁出答案行拼成图，供人工逐题读两遍
                               （格式一“N、正确答案：X”；格式二不带题号的“故正确答案为X”，与题号行按顺序配对）
  build <卷> [--work D]        套用修正，只生成本卷文件（见下），并校验本卷
  index                        扫描全部已生成的卷，合并生成根目录汇总文件
  verify [<卷> ...]            校验指定卷；不带参数时校验全部卷，并检查根目录汇总是否最新

每卷的文件（多人可同时整理不同的卷，互不覆盖）
  输入  tools/papers/<卷>.json       登记：year、title、paper_variant、source_edition、question_pdf、answer_pdf、
                                    expected_questions；可选 missing_questions（原卷缺题的题号）、
                                    exam、subject（默认“公务员录用考试”“行政职业能力测验”，选调等其他考试时填写）、
                                    source_commit（记作来源的提交；默认沿用 sources/<卷>.json 已记录的提交，
                                    源 PDF 变了才改用 HEAD）
        tools/corrections/<卷>.json  人工修正（键见下）
  输出  <卷>.jsonl  <卷>.md  assets/<卷>/*.png  assets/<卷>/manifest.json  quality/<卷>.md  sources/<卷>.json
根目录汇总只由 index 生成（合并分支后有冲突时重跑 index 即可）：
  all.jsonl  assets-manifest.json  sources.json  quality-report.md  README.md

修正文件的键（都可省略）
  section_map      原卷部分名 → schema 部分名，如 {"常识应用": "常识判断"}；这里列出的原卷部分名同时被识别为
                   部分标题（如选调卷的“实词填空”“阅读理解”“推理判断”“思维能力测验”）
  section_ranges   [{from, to, section, note}] 按题号改部分（如原卷未单列的科学推理）
  material_groups  [[86, 90], ...] 资料分析各组材料的首末题号，用于核对自动分段
  inline_images    {"p04-i01": "1/3"} 行内小图的文字；缺哪个 build 会列出
  text_fixes       [{q, field: "stem" | "option:A", find, replace | set, reason}]；find 须恰好出现一次
  ignore_lines     ["69——75题暂缺"] 选项之后无法归属、又不属于试题内容的行（按开头匹配）
  bare_numbers     [67] 原卷题号后漏印“、”（如题号单独印在题图左侧）的题号，按题号行识别
  long_options     {"32": "A"} 核对过、原卷本来就超过80字的选项（不再报“选项过长”）
  figures          {"p06-i02": {bbox: [x0, top, x1, bottom]（pt）, reason, role, alt, transcription}}
  figure_questions {"p05-i03": 35} 把题图归入指定题号（图片对象连同白边越过下一题题号行等，自动归属错时用）；
                   归走后空出的“材料”并入前一组
  figure_materials {"p11-i01": 1} 把图片归入第 k 组材料（按阅读位置插入；材料图排在下一页页首而连同白边越过
                   第一题题号行、被自动归入该题时用）
  option_splits    [{q, label: "D", reason}] 在上一选项文字中按“ D、”拆出该项（自动补拆拆不出时才用）；
                   原卷标记不规范时加 at: "B、C、"，按这段原样文字拆分并整体删去
  option_figures   {"89": {"A": "p13-i02", "B": …}} 每个选项一张图：这些图在 figures 中设 role: "option"，
                   输出 option_label，选项 image_refs 指向各自的图（label_in_image 为 null）
  subtypes         {"52": "图形推理"} 判断推理小类覆盖。自动分类：有题图→图形推理；题干与各选项均为
                   A∶B 式（比号“∶”、半角或全角冒号）→类比推理；含“是指/定义”→定义判断；其余→逻辑判断
  question_notes   {"47": ["…"]}；materials {"2": {"question_notes": ["…"]}} 写入该组每题 notes
  answers          {"source": "…", "by_page": {"1": "1B 2D 3B"}} 人工读取的答案（答案PDF页码: 题号答案…）
  answer_notes     {"91": "…"} 答案说明
  report           {answers, source_issues, uncertain, review: [...]} 写入本卷质量报告；readme: [...] 写入 README

整理新的一卷
  1. 写 tools/papers/<卷>.json；2. dump 核对分题、材料与图片归属（改修正文件后用 dump --apply 再看）；
  3. answer-sheet 读答案（两遍），写入 answers.by_page；
  4. 在 tools/corrections/<卷>.json 补行内小图文字、图表转写、部分/小类与源文件问题注记；
  5. build <卷>（失败时按提示补修正）；6. 对照页面渲染图逐题、逐图复核；7. index；8. verify。

依赖：Python 3.10+；pdfplumber、Pillow、numpy；poppler-utils（pdftoppm、pdftotext）；git。可选 jsonschema。
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import logging
import math
import re
import shutil
import struct
import subprocess
import tempfile
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
OUT = TOOLS.parent                      # 广东/行测/2013-2021
REPO = TOOLS.parents[3]                 # 仓库根目录
DPI = 288
SCALE = DPI / 72.0                      # 每 pt 的像素数
GAP_SPLIT = 4.0                         # pt；同一行内大于此间距视为分隔（选项、多空词语）
LINE_TOL = 3.0                          # pt；字符竖直中心相差在此以内视为同一行
INLINE_MAX_H = 32.0                     # pt；不高于此且与文字同行的图片视为行内小图（分数、根号、公式）
PAD_PX = 6                              # 裁图四周留白（像素，288 DPI 下 1.5pt）
INK = 240                               # 灰度低于此值视为有墨迹（用于收紧裁剪框）
PAPERS_DIR = TOOLS / 'papers'           # 每卷登记信息
CORR_DIR = TOOLS / 'corrections'        # 每卷人工修正

SECTION_NAMES = ['政治理论', '常识判断', '言语理解与表达', '数量关系', '判断推理', '科学推理', '资料分析']
SECTION_ALIASES = {'常识应用': '常识判断', '常识': '常识判断', '言语理解': '言语理解与表达',
                   '言语表达与理解': '言语理解与表达', '数学运算': '数量关系'}
SUBTYPES = ['图形推理', '定义判断', '类比推理', '逻辑判断']
CN_NUM = '一二三四五六七八九十'
RE_SECTION = [
    re.compile(rf'^第[{CN_NUM}]+部分[\s:：]*(?P<name>[\u4e00-\u9fff]+)'),
    re.compile(rf'^[{CN_NUM}]+[、.．](?P<name>[\u4e00-\u9fff]{{2,8}}?)(?:[，。,.：:（(]|共|$)'),
]
RE_MATERIAL = [
    re.compile(r'^[（(]?\s*材料\s*(?P<k>[0-9一二三四五六七八九十]+)\s*[）)]?'),
    re.compile(r'^[（(]?\s*资料\s*(?P<k>[0-9一二三四五六七八九十]+)\s*[）)]?'),
    re.compile(r'^(?:根据|阅读)(?:以下|下列|下面|所给)(?:资料|材料)'),
    re.compile(rf'^[（(][{CN_NUM}]+[）)]$'),                  # 单独一行的组号“（一）”
]
RE_MAT_INSTR = re.compile(r'(?:根据|阅读)(?:以下|下列|下面|所给)(?:资料|材料)[，,]?(?:回答)?(?:第?\d+\s*[~～\-—–至]+\s*\d+题)?[：:。]?')
RE_QNUM = re.compile(r'^(\d{1,3})\s*[、.．]')
RE_QNUM_BARE = re.compile(r'^(\d{1,3})(?=\s|$)')    # 漏印“、”的题号（只在修正文件 bare_numbers 列出的题号上使用）
RE_OPT = re.compile(r'^([A-D])\s*[、.．:：]')
LABEL_ROW = re.compile(r'^[A-D][、.．]?[A-D]?$')     # 图下的选项字母行，如“B B”
RE_FOOTER = re.compile(r'^(?:[-－—–]\s*\d+\s*[-－—–]|第\s*\d+\s*页(?:\s*共\s*\d+\s*页)?|\d+)$')
RE_MARKER = re.compile(r'^(?:[①-⑳]|[（(]\d{1,2}[）)]|[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ][、.．])')
# 设问句：上一行以句末标点结束、本行以这些词开头时另起一段（即使上一行写满）
RE_PROMPT = re.compile(r'^(?:以下|下列|填入|依次填入|这段文字|这段话|上述|对这段|对上述|根据以上|根据上述|根据这段|'
                       r'要使上述|由此可以推出|由此可推出|如果以上|如果上述|最能)')
TERMINAL = set('。！？：；…!?:;')
CLOSERS = set('”’）)」』')


def die(msg: str) -> None:
    raise SystemExit(f'错误：{msg}')


# ---------------------------------------------------------------------------
# 基础数据结构
# ---------------------------------------------------------------------------
@dataclass
class Tok:
    text: str
    x0: float
    x1: float
    top: float
    bottom: float
    size: float = 10.0
    image: str | None = None            # 行内小图 id（如 p04-i01）

    @property
    def vc(self) -> float:
        return (self.top + self.bottom) / 2


@dataclass
class Img:
    page: int
    idx: int
    x0: float
    top: float
    x1: float
    bottom: float
    inline: bool = False

    @property
    def key(self) -> str:
        return f'p{self.page:02d}-i{self.idx:02d}'

    @property
    def h(self) -> float:
        return self.bottom - self.top


@dataclass
class Line:
    page: int
    toks: list
    text: str = ''
    segs: list = field(default_factory=list)   # [(text, x0, x1)]

    @property
    def x0(self): return min(t.x0 for t in self.toks)
    @property
    def x1(self): return max(t.x1 for t in self.toks)
    @property
    def top(self): return min(t.top for t in self.toks)
    @property
    def bottom(self): return max(t.bottom for t in self.toks)
    @property
    def em(self):
        sizes = [t.size for t in self.toks if not t.image]
        return statistics_median(sizes) if sizes else 10.5


def statistics_median(xs):
    xs = sorted(xs)
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


@dataclass
class Page:
    no: int
    width: float
    height: float
    chars: list
    images: list
    lines: list = field(default_factory=list)


def bare_label(segs, L: str) -> bool:
    """行首单独一个选项字母、隔开后紧跟选项文字（字母后的分隔符是全角空格等空白，读入时已丢弃）。"""
    return (len(segs) > 1 and segs[0][0] == L and not RE_OPT.match(segs[1][0])
            and re.match(r'[^\sA-Za-z]', segs[1][0]) is not None)


def kind(ch: str) -> str:
    if not ch:
        return ''
    o = ord(ch[0])
    if 0x4E00 <= o <= 0x9FFF or 0x3400 <= o <= 0x4DBF:
        return 'H'
    if ch.isascii() and ch.isalnum():
        return 'a'
    return 'p' if ch.isascii() else 'F'


# ---------------------------------------------------------------------------
# 版面：字符 → 行；图片分为行内小图与题图
# ---------------------------------------------------------------------------
def load_pages(pdf_path: Path) -> list[Page]:
    logging.getLogger('pdfminer').setLevel(logging.ERROR)
    import pdfplumber
    pages = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for no, pg in enumerate(pdf.pages, 1):
            W, H = float(pg.width), float(pg.height)
            chars = [Tok(c['text'], c['x0'], c['x1'], c['top'], c['bottom'], c.get('size', 10.0))
                     for c in pg.chars if c['text'] and not c['text'].isspace()]
            raw = sorted(pg.images, key=lambda i: (round(i['top'], 1), i['x0']))
            imgs = []
            for k, im in enumerate(raw, 1):
                x0, x1 = max(0.0, im['x0']), min(W, im['x1'])
                top, bottom = max(0.0, im['top']), min(H, im['bottom'])
                imgs.append(Img(no, k, x0, top, x1, bottom))
            pages.append(Page(no, W, H, chars, imgs))
    for p in pages:
        build_lines(p)
    return pages


def build_lines(page: Page) -> None:
    toks = sorted(page.chars, key=lambda t: (t.vc, t.x0))
    groups: list[list[Tok]] = []
    for t in toks:
        if groups and abs(t.vc - groups[-1][0].vc) <= LINE_TOL:
            groups[-1].append(t)
        else:
            groups.append([t])
    lines = [Line(page.no, sorted(g, key=lambda t: t.x0)) for g in groups]
    # 行内小图：高度不大、与某一文字行竖直重叠且左右紧邻文字
    for im in page.images:
        if im.h > INLINE_MAX_H:
            continue
        best, ov_best = None, 0.0
        for ln in lines:
            ov = min(im.bottom, ln.bottom) - max(im.top, ln.top)
            near = any(abs(t.x1 - im.x0) < 60 or abs(im.x1 - t.x0) < 60 for t in ln.toks)
            if ov > ov_best and near:
                best, ov_best = ln, ov
        if best is not None and ov_best >= 0.3 * min(im.h, best.bottom - best.top):
            im.inline = True
            best.toks.append(Tok('', im.x0, im.x1, im.top, im.bottom, best.em, image=im.key))
            best.toks.sort(key=lambda t: t.x0)
    # 去掉页码等页脚
    keep = []
    for ln in lines:
        txt = ''.join(t.text for t in ln.toks if not t.image)
        if ln.top > page.height * 0.92 and RE_FOOTER.match(txt.replace(' ', '')):
            continue
        keep.append(ln)
    page.lines = sorted(keep, key=lambda l: (l.top, l.x0))


def tok_text(t: Tok, inline_text: dict) -> str:
    if t.image:
        return inline_text.get(t.image, f'⟦{t.image}⟧')
    return t.text


def render_line(ln: Line, inline_text: dict) -> None:
    """拼出行文字与分段。原卷无空格字符，字间距全靠定位：中西文之间的自动间距不转成空格；
    空括号内的留白收为“（）”；两个西文字母/数字之间的明显间距记一个空格；大间距后的①②…另起一行。"""
    out, segs, cur, seg_x0, prev = [], [], [], None, None
    for t in ln.toks:
        s = tok_text(t, inline_text)
        if prev is not None:
            gap = t.x0 - prev.x1
            ps, ns = tok_text(prev, inline_text), s
            if gap > GAP_SPLIT:
                segs.append((''.join(cur), seg_x0, prev.x1))
                cur, seg_x0 = [], None
                if ps.endswith(('（', '(')) and ns.startswith(('）', ')')):
                    pass
                elif kind(ps[-1:]) == 'a' and kind(ns[:1]) == 'a':
                    out.append(' ')
                elif gap > 1.5 * ln.em and RE_MARKER.match(ns):
                    out.append('\n')
        if seg_x0 is None:
            seg_x0 = t.x0
        out.append(s)
        cur.append(s)
        prev = t
    if cur:
        segs.append((''.join(cur), seg_x0, prev.x1))
    ln.text = ''.join(out)
    ln.segs = segs


# ---------------------------------------------------------------------------
# 分题：章节、材料、题目
# ---------------------------------------------------------------------------
@dataclass
class QBlock:
    number: int
    section_raw: str
    lines: list = field(default_factory=list)
    figures: list = field(default_factory=list)
    material: int | None = None


@dataclass
class MBlock:
    k: int
    section_raw: str
    header: list = field(default_factory=list)   # 材料标题段（含编者按语）
    items: list = field(default_factory=list)    # ('line', Line) | ('fig', Img)
    questions: list = field(default_factory=list)


def match_section(text: str, extra=()):
    """返回原卷部分名（如“常识应用”）；不是部分标题则返回 None。extra：本卷修正文件 section_map 中的原卷部分名。"""
    t = text.replace(' ', '')
    for rx in RE_SECTION:
        m = rx.match(t)
        if m:
            name = m.group('name')
            for cand in SECTION_NAMES + sorted(set(SECTION_ALIASES) | set(extra), key=len, reverse=True):
                if name.startswith(cand):
                    return cand
    return None


def match_material(text: str) -> bool:
    t = text.replace(' ', '')
    return any(rx.match(t) for rx in RE_MATERIAL)


def segment(pages: list[Page], expected: int, inline_text: dict, missing=(), extra_sections=(), bare=()):
    """按阅读顺序把行与题图分到部分、材料、题目。材料有两种写法：带“材料1/（材料一）/根据以下资料”等标题；
    或（2013、2015、2017、2019等年）无标题，资料分析部分里上一组题的A—D选项之后直接接首行缩进的材料段落或图表。"""
    for p in pages:
        for ln in p.lines:
            render_line(ln, inline_text)
    stream = []
    for p in pages:
        # 文字行按该行文字字符的上缘排序：行内小图比文字高时，不致把题图（按下缘排序）排进句子中间
        stream += [('line', ln, min((t.top for t in ln.toks if not t.image), default=ln.top), ln.x0) for ln in p.lines]
        # 题图按下边缘排序：图片与题号同一横带、顶部高于题号行时（如2016年第31题）仍归入该题
        stream += [('fig', im, im.bottom, im.x0) for im in p.images if not im.inline]
    stream.sort(key=lambda it: (it[1].page, it[2], it[3]))
    left, right = margins(pages)
    preamble, headings, questions, materials, orphans = [], [], [], [], []
    section, cur_q, cur_m, collecting = None, None, None, False
    header_open = heading_open = False
    last_label, prev = '', None
    nxt = 1

    def new_material(first=None):
        nonlocal cur_m, cur_q, collecting
        cur_q = None
        cur_m = MBlock(len(materials) + 1, section)
        materials.append(cur_m)
        collecting = True
        if first is not None:
            cur_m.items.append(first)

    for kind_, obj, _, _ in stream:
        if kind_ == 'fig':
            heading_open = False
            if section == '资料分析' and cur_q is not None and last_label == 'D':
                new_material(('fig', obj))
            elif cur_q is not None:
                cur_q.figures.append(obj)
            elif cur_m is not None and collecting:
                cur_m.items.append(('fig', obj))
                header_open = False
            elif section == '资料分析':
                new_material(('fig', obj))
            else:
                orphans.append(obj)
            continue
        ln = obj
        short_prev = prev is not None and prev.x1 < right - 1.5 * prev.em
        indented = ln.x0 > left + 1.2 * ln.em
        prev = ln
        sec = match_section(ln.text, extra_sections) if len(ln.text) < 160 else None
        if sec:
            section, cur_q, cur_m, collecting = sec, None, None, False
            headings.append(ln)
            heading_open = ln.x1 >= right - 1.5 * ln.em
            continue
        if heading_open and not indented and not RE_QNUM.match(ln.text) and not match_material(ln.text):
            headings.append(ln)                       # 部分说明的续行
            heading_open = ln.x1 >= right - 1.5 * ln.em
            continue
        heading_open = False
        m = RE_QNUM.match(ln.text)
        while nxt in missing:
            nxt += 1                                  # tools/papers/<卷>.json 声明的原卷缺题题号
        if not m and nxt in bare:
            m = RE_QNUM_BARE.match(ln.text)           # 修正文件 bare_numbers：原卷题号后漏印“、”
        if m and int(m.group(1)) == nxt and nxt <= expected:
            cur_q = QBlock(nxt, section)
            cur_q.lines.append(ln)
            if cur_m is not None:
                cur_q.material = cur_m.k
                cur_m.questions.append(nxt)
            questions.append(cur_q)
            collecting, last_label = False, ''
            nxt += 1
            continue
        if match_material(ln.text) and section in (None, '资料分析'):
            if not (cur_m is not None and collecting and not cur_m.items and not cur_m.questions):
                new_material()                        # “（一）”后紧接“根据下列资料……”时并为同一材料标题
            cur_m.header.append(ln)
            header_open = ln.x1 >= right - 1.5 * ln.em
            continue
        if section == '资料分析' and cur_q is not None and last_label == 'D' and (indented or short_prev) \
                and not RE_OPT.match(ln.text):
            new_material(('line', ln))                # 无标题材料：选项结束后另起的缩进段落
            continue
        if cur_m is not None and collecting:
            if header_open and ln.x0 <= left + 0.5 * ln.em:
                cur_m.header.append(ln)
                header_open = ln.x1 >= right - 1.5 * ln.em
            else:
                header_open = False
                cur_m.items.append(('line', ln))
        elif cur_q is not None:
            cur_q.lines.append(ln)
            for text, _, _ in ln.segs:
                mo = RE_OPT.match(text)
                if mo and mo.group(1) == chr(ord(last_label or '@') + 1):
                    last_label = mo.group(1)
        elif section == '资料分析':
            new_material(('line', ln))
        else:
            preamble.append(ln)
    return dict(preamble=preamble, headings=headings, questions=questions, materials=materials,
                orphans=orphans, margins=(left, right))


def margins(pages):
    xs0 = sorted(ln.x0 for p in pages for ln in p.lines)
    xs1 = sorted(ln.x1 for p in pages for ln in p.lines)
    if not xs0:
        return 0.0, 0.0
    return xs0[len(xs0) // 20], xs1[int(len(xs1) * 0.95)]


def ends_terminal(s: str) -> bool:
    s = s.rstrip()
    if not s:
        return False
    if s[-1] in TERMINAL:
        return True
    return s[-1] in CLOSERS and len(s) > 1 and s[-2] in TERMINAL


def join_lines(lines: list[Line], left: float, right: float, first_strip: str = '', indent_paras=False) -> str:
    """把若干行拼成段落：上一行未写满且以句末标点结束、或本行以①等列项开头、或（材料中）本行首行缩进，则另起一段。"""
    out = ''
    prev = None
    for i, ln in enumerate(lines):
        txt = ln.text
        if i == 0 and first_strip:
            txt = txt[len(first_strip):]
        if prev is None:
            out = txt
        else:
            short = prev.x1 < right - 1.5 * prev.em
            new = bool(RE_MARKER.match(txt)) or (ends_terminal(prev.text) and (short or bool(RE_PROMPT.match(txt))))
            if indent_paras and ln.x0 > left + 1.2 * ln.em:
                new = True
            if new:
                out += '\n' + txt
            elif kind(out[-1:]) == 'a' and kind(txt[:1]) == 'a' and out[-1:].isalpha() and txt[:1].isalpha():
                out += ' ' + txt
            else:
                out += txt
        prev = ln
    return out


def parse_question(q: QBlock, left: float, right: float, autofix: list) -> dict:
    first = q.lines[0]
    m = RE_QNUM.match(first.text) or RE_QNUM_BARE.match(first.text)
    opt_i = next((i for i, ln in enumerate(q.lines) if i > 0 and (RE_OPT.match(ln.text) or bare_label(ln.segs, 'A'))), None)
    stem_lines = q.lines if opt_i is None else q.lines[:opt_i]
    opt_lines = [] if opt_i is None else q.lines[opt_i:]
    stem = join_lines(stem_lines, left, right, first_strip=m.group(0))
    options, want, labels_raw, strays, prev_ln = [], 0, [], [], None
    for ln in opt_lines:
        segs = ln.segs
        if options and not RE_OPT.match(segs[0][0]):
            if prev_ln is not None and prev_ln.x1 < right - 2 * prev_ln.em:
                strays.append(ln)                     # 上一行没写满，这一行不是折行：交人工判断
                continue
            # 选项折行：接到上一选项（同一行内被大间距隔开的部分用空格连接）
            options[-1]['text'] += ' '.join(s[0] for s in segs)
            prev_ln = ln
            continue
        prev_ln = ln
        for j, (text, _, _) in enumerate(segs):
            mo = RE_OPT.match(text) or (re.match(r'([A-D])', text) if j == 0 and want < 4 and bare_label(segs, 'ABCD'[want]) else None)
            if mo and want < 4 and mo.group(1) == 'ABCD'[want]:
                options.append({'label': mo.group(1), 'text': text[mo.end():].strip()})
                labels_raw.append(mo.group(0))
                want += 1
            elif options:
                sep = ' ' if options[-1]['text'] else ''
                options[-1]['text'] += sep + text
            else:
                stem += text
    if q.figures and strays and options and re.fullmatch(r'[A-D、.．\s]*', ''.join(o['text'] for o in options)) \
            and all(LABEL_ROW.match(ln.text.replace(' ', '')) for ln in strays):
        # 图下逐行排的选项字母（“A、A”“B B”“C C”“D D”）：不是无法归属的行，按选项字母行处理（选项在题图中）
        labels_raw += [ln.text for ln in strays]
        strays = []
    if 0 < len(options) < 4:
        # 选项之间没有留白（如“A、……好坏B、不健康……”），或下一项排在上一项的续行上（“…… D、……”）：
        # 按下一个应出现的选项字母补拆；字母前须是汉字、数字、右括号/引号/百分号或空白，
        # 拆后必须恰好得到 A—D 四项，否则不动、交人工核对
        whole = ''.join(f'\u0000{o["label"]}\u0001{o["text"]}' for o in options)
        cut, pos = [], 0
        for L in 'ABCD'[len(options):]:
            mo = re.compile(rf'(?<=[\u4e00-\u9fff\d）)”%\s])({L})[、.．](?=[^、.．\s])').search(whole, pos)
            if not mo:
                break
            cut.append(mo)
            pos = mo.end()
        if len(options) + len(cut) == 4:
            for mo in reversed(cut):
                whole = whole[:mo.start()] + f'\u0000{mo.group(1)}\u0001' + whole[mo.end():]
            parts = [x.split('\u0001', 1) for x in whole.split('\u0000') if x]
            labels_raw += [mo.group(0) for mo in cut]
            options = [{'label': a, 'text': b.strip()} for a, b in parts]
            autofix.append(f'第{q.number}题：选项之间没有留白，按选项字母补拆出{"、".join(m_.group(1) for m_ in cut)}项，请对照原卷确认。')
    if q.figures and options and re.fullmatch(r'[A-D、.．\s]*', ''.join(o['text'] for o in options)):
        # 图下只排了选项字母（“A、A B B C C D D”）：选项在图中
        autofix.append(f'第{q.number}题：选项行只有字母，按图形选项处理（选项在题图中）。')
        labels_raw += [o['text'] for o in options]       # 选项字母已在解析时记入 labels_raw
        options = []
    dups = []
    for o in options:
        dup = re.match(rf'^{o["label"]}\s*[.．、]\s*', o['text'])
        if dup:
            dups.append(f'{o["label"]}项“{dup.group(0).strip()}”')
            labels_raw.append(dup.group(0))
            o['text'] = o['text'][dup.end():]
    if dups:
        autofix.append(f'第{q.number}题：删去选项文字开头重复印出的选项字母（{"、".join(dups)}）。')
    pages = sorted({ln.page for ln in q.lines} | {f.page for f in q.figures})
    return dict(number=q.number, section_raw=q.section_raw, stem=stem, options=options,
                figures=list(q.figures), pages=pages, material=q.material, labels_raw=labels_raw,
                strays=[ln.text for ln in strays], prefix=m.group(0),
                raw=''.join(t.text for ln in q.lines if ln not in strays for t in ln.toks if not t.image),
                inline=[t.image for ln in q.lines for t in ln.toks if t.image])


def parse_material(mb: MBlock, left: float, right: float) -> dict:
    head = ''.join(ln.text for ln in mb.header).replace(' ', '')
    note = head
    for rx in RE_MATERIAL[:2] + [re.compile(rf'^[（(][{CN_NUM}]+[）)]')]:
        note = rx.sub('', note, count=1)
    note = RE_MAT_INSTR.sub('', note).strip('：:，, ')   # 去掉材料编号与“根据下列资料，回答86~90题”后，余下的才算编者按语
    blocks, buf = [], []

    def flush():
        if buf:
            blocks.append({'type': 'text', 'text': join_lines(buf, left, right, indent_paras=True)})
            buf.clear()
    for kind_, obj in mb.items:
        if kind_ == 'line':
            buf.append(obj)
        else:
            flush()
            blocks.append({'type': 'fig', 'img': obj})
    flush()
    pages = sorted({ln.page for ln in mb.header} | {o.page for _, o in mb.items})
    return dict(k=mb.k, header_text=head, header_note=note, blocks=blocks, pages=pages,
                questions=list(mb.questions),
                inline=[t.image for _, o in mb.items if _ == 'line' for t in o.toks if t.image])


def _take_figure(seg: dict, key: str, what: str):
    """从题目、材料或未归属图片中取出指定图片（供 figure_questions / figure_materials 重新归属）。"""
    found = None
    for q in seg['questions']:
        for im in list(q.figures):
            if im.key == key:
                q.figures.remove(im)
                found = im
    for m in seg['materials']:
        for it in list(m.items):
            if it[0] == 'fig' and it[1].key == key:
                m.items.remove(it)
                found = it[1]
    for im in list(seg['orphans']):
        if im.key == key:
            seg['orphans'].remove(im)
            found = im
    if found is None:
        die(f'{what}：找不到图片 {key}')
    return found


def apply_figure_questions(seg: dict, corr: dict) -> None:
    """figure_questions {"p05-i03": 35}：把指定题图归入指定题号，覆盖按图片下缘排序的自动归属（图片对象连同白边
    越过下一题题号行、资料分析中排在“C、 D、”字母行之后的选项图等情形）。归走后既无标题也无内容的“材料”删去，
    其题目并入前一组材料。"""
    fq = corr.get('figure_questions', {})
    fm = corr.get('figure_materials', {})
    if not fq and not fm:
        return
    qmap = {q.number: q for q in seg['questions']}
    mmap = {m.k: m for m in seg['materials']}
    for key, k in fm.items():
        # figure_materials {"p11-i01": 1}：把图片归入第 k 组材料（材料图排在下一页页首、连同白边越过第一题题号行等）
        found = _take_figure(seg, key, 'figure_materials')
        if k not in mmap:
            die(f'figure_materials：没有第{k}组材料')
        items = mmap[k].items
        pos = next((i for i, it in enumerate(items) if (it[1].page, it[1].top) > (found.page, found.top)), len(items))
        items.insert(pos, ('fig', found))
    for key, qn in fq.items():
        found = _take_figure(seg, key, 'figure_questions')
        if qn not in qmap:
            die(f'figure_questions：没有第{qn}题')
        qmap[qn].figures.append(found)
        qmap[qn].figures.sort(key=lambda im: (im.page, im.top, im.x0))
    kept = []
    for m in seg['materials']:
        if not m.header and not m.items:
            if not kept:
                die('figure_questions：第一组材料被清空，无法并入前一组')
            kept[-1].questions.extend(m.questions)
        else:
            kept.append(m)
    for k, m in enumerate(kept, 1):
        m.k = k
        for n in m.questions:
            qmap[n].material = k
    seg['materials'] = kept


def apply_option_fixes(r: dict, corr: dict, autofix: list) -> None:
    """紧接 parse_question 之后套用：
    option_splits  [{"q": 10, "label": "D", "reason": "…"}]：在最后一个选项的文字里按“ D、”拆出该项（自动补拆
                   未能拆出时才需要；自动补拆已拆出时会报错，请删去该条）；
    option_figures {"89": {"A": "p13-i02", …}}：每个选项各是一张图，选项先置为四个空文字选项，图与选项的对应在
                   生成题图时写入（见 link_option_figures）。"""
    n = r['number']
    for sp in corr.get('option_splits', []):
        if sp['q'] != n:
            continue
        L = sp['label']
        if not r['options'] or r['options'][-1]['label'] != chr(ord(L) - 1):
            die(f'option_splits：第{n}题最后一个选项不是{chr(ord(L) - 1)}项'
                + ('（自动补拆可能已拆出该项，请删去这一条）' if r['options'] and r['options'][-1]['label'] == L else ''))
        o = r['options'][-1]
        if 'at' in sp:          # 原卷选项标记印得不规范（如多印一个字母“B、C、”）：按给出的原样标记拆分，标记整体删去
            k = o['text'].count(sp['at'])
            if k != 1:
                die(f'option_splits：第{n}题{o["label"]}项中“{sp["at"]}”出现 {k} 次（应为 1 次）')
            i = o['text'].index(sp['at'])
            start, end, marker = i, i + len(sp['at']), sp['at']
        else:
            ms = list(re.finditer(rf'\s({L})\s*[、.．]', o['text']))
            if len(ms) != 1:
                die(f'option_splits：第{n}题{o["label"]}项中“ {L}、”出现 {len(ms)} 次（应为 1 次）')
            start, end, marker = ms[0].start(), ms[0].end(), ms[0].group(0)
        r['options'].append({'label': L, 'text': o['text'][end:].strip()})
        o['text'] = o['text'][:start].strip()
        r['labels_raw'].append(marker.strip())
        autofix.append(f'第{n}题：{sp["reason"]}')
    if str(n) in corr.get('option_figures', {}):
        if any(o['text'] for o in r['options']):
            die(f'option_figures：第{n}题有文字选项')
        r['options'] = [{'label': L, 'text': ''} for L in 'ABCD']


def link_option_figures(n: int, paper: str, figs: list, options: list, corr: dict) -> None:
    """option_figures：选项图的 role 须在 figures 中设为 option；写入 option_label，选项 image_refs 指向各自的图
    （label_in_image 为 null，与2022—2026题库同类题一致）。"""
    of = corr.get('option_figures', {}).get(str(n))
    if not of:
        return
    ids = {L: f'{paper}-{key}' for L, key in of.items()}
    byid = {f['image_id']: f for f in figs}
    for L, iid in ids.items():
        if iid not in byid:
            die(f'option_figures：第{n}题没有题图 {iid}')
        if byid[iid]['role'] != 'option':
            die(f'option_figures：{iid} 的 role 应在 figures 中设为 option')
        byid[iid]['option_label'] = L
    for o in options:
        if o['label'] not in ids:
            die(f'option_figures：第{n}题没有给出{o["label"]}项的图')
        o['image_refs'] = [{'image_id': ids[o['label']], 'label_in_image': None}]


def normalize_blanks(text: str, section: str | None) -> str:
    text = re.sub(r'[（(]\s*[）)]', '（）', text)
    if section == '数量关系':
        core = text.replace('（）', '')
        if core and re.fullmatch(r'[\d\s，,.．/√、\-－+]+', core):
            text = text.replace('（）', '（    ）')
    return text


def classify_subtype(rec: dict) -> str:
    stem = rec['stem']
    opts = [o['text'] for o in rec['options']]
    if rec['figures']:
        return '图形推理'
    if len(stem) <= 30 and re.search(r'[∶:：]', stem) and opts and all(re.search(r'[∶:：]', o) for o in opts):
        return '类比推理'
    if re.search(r'是指|定义', stem):
        return '定义判断'
    return '逻辑判断'


# ---------------------------------------------------------------------------
# 答案
# ---------------------------------------------------------------------------
RE_ANS_BATCH = re.compile(r'(\d{1,3})\s*[-—–~～]{1,3}\s*(\d{1,3})\s+([A-D](?:[\s.、，,]*[A-D])+)')
RE_ANS_ONE = re.compile(r'(\d{1,3})\s*[、.．]\s*(?:【?(?:正确)?答案】?(?:是|为)?)?\s*[：:]\s*([A-D]{1,4})(?![A-Za-z])')
RE_ANS_CONCL = re.compile(r'(?:正确)?(?:答案|选项)(?:应?为|是|选择?)[：:]?([A-D]{1,4})(?![A-Za-z])')   # 结论句（去空格后匹配）


def answer_text_layer(pdf: Path) -> tuple[dict, list]:
    """从答案 PDF 文字层提取答案；同时返回每页可读字符数，用于判断是否扫描页。"""
    found, stats = {}, []
    out = subprocess.run(['pdftotext', '-layout', str(pdf), '-'], capture_output=True, text=True).stdout
    pages = out.split('\f')
    if pages and not pages[-1].strip():
        pages = pages[:-1]          # pdftotext 在最后一页后也输出换页符
    for pno, page in enumerate(pages, 1):
        stats.append((pno, len(re.sub(r'\s', '', page))))
        for m in RE_ANS_BATCH.finditer(page):
            a, b = int(m.group(1)), int(m.group(2))
            letters = re.findall(r'[A-D]', m.group(3))
            if b - a + 1 == len(letters):
                for i, L in enumerate(letters):
                    found[a + i] = dict(value=L, page=pno, raw=m.group(0).strip())
        for m in RE_ANS_ONE.finditer(page):
            found.setdefault(int(m.group(1)), dict(value=m.group(2), page=pno, raw=re.sub(r'\s+', ' ', m.group(0))))
    if sum(n for _, n in stats) > 200:
        # 格式二的文字层版本（选调卷等）：每题解析以“N、”开头、以“故正确答案为X”结束；同一题的结论不一致时不取
        by_q = collections.defaultdict(list)
        for n, v, pno, _, raw in text_conclusions(pdf):
            by_q[n].append((v, pno, raw))
        for n, lst in by_q.items():
            if n not in found and len({v for v, _, _ in lst}) == 1:
                v, pno, raw = lst[-1]
                found[n] = dict(value=v, page=pno, raw=raw)
    return found, stats


def text_conclusions(pdf: Path) -> list:
    """有文字层的答案 PDF：按行找“N、”开头的解析起点（N 只取比上一题大 1—3 的数，避开解析里的列项）与其后的结论句
    “正确答案为X”。返回 [(题号, 答案, 页码, 答案字母的框 (x0, top, x1, bottom) pt, 去空格的整行)]。"""
    import pdfplumber
    out, cur, expect = [], None, 1
    with pdfplumber.open(str(pdf)) as doc:
        for pno, page in enumerate(doc.pages, 1):
            for ln in page.extract_text_lines(return_chars=True):
                chars = [c for c in ln['chars'] if not c['text'].isspace()]
                t = ''.join(c['text'] for c in chars)
                m = re.match(r'(\d{1,3})[、.．]', t)
                if m and expect <= int(m.group(1)) <= expect + 2:
                    cur, expect = int(m.group(1)), int(m.group(1)) + 1
                if cur is None or len(t) != len(chars):
                    continue
                for mm in RE_ANS_CONCL.finditer(t):
                    a, b = chars[mm.start(1)], chars[mm.end(1) - 1]
                    out.append((cur, mm.group(1), pno, (a['x0'], ln['top'], b['x1'], ln['bottom']), t))
    return out


def manual_answers(spec: dict) -> dict:
    res = {}
    for page, s in (spec or {}).get('by_page', {}).items():
        for q, v in re.findall(r'(\d{1,3})([A-D]{1,4}|正确|错误)', s):
            if int(q) in res:
                die(f'修正文件 answers.by_page 中第{q}题重复')
            res[int(q)] = dict(value=v, page=int(page))
    return res


# ---------------------------------------------------------------------------
# 渲染与裁图
# ---------------------------------------------------------------------------
def render_pages(pdf: Path, pages: list[int], work: Path) -> dict:
    work.mkdir(parents=True, exist_ok=True)
    res = {}
    for p in pages:
        stem = work / f'page-{p:02d}'
        png = stem.with_suffix('.png')
        if not png.exists():
            subprocess.run(['pdftoppm', '-r', str(DPI), '-png', '-singlefile', '-f', str(p), '-l', str(p),
                            str(pdf), str(stem)], check=True, capture_output=True)
        res[p] = png
    return res


_PAGE_CACHE: dict = {}


def crop_box(img_path: Path, im: Img, page: Page, override=None):
    """返回裁剪框（像素）。默认取图片对象外框，收紧到有墨迹处并留 1.5pt 白边，不越过邻近文字。"""
    import numpy as np
    from PIL import Image
    if img_path not in _PAGE_CACHE:
        _PAGE_CACHE[img_path] = Image.open(img_path).convert('RGB')
    full = _PAGE_CACHE[img_path]
    Wpx, Hpx = full.size
    if override:
        x0, t0, x1, b0 = override
        return full, (math.floor(x0 * SCALE), math.floor(t0 * SCALE), math.ceil(x1 * SCALE), math.ceil(b0 * SCALE))
    bx = (max(0, math.floor(im.x0 * SCALE)), max(0, math.floor(im.top * SCALE)),
          min(Wpx, math.ceil(im.x1 * SCALE)), min(Hpx, math.ceil(im.bottom * SCALE)))
    arr = np.asarray(full.crop(bx).convert('L'))
    ys, xs = np.where(arr < INK)
    if len(xs):
        tight = (bx[0] + xs.min(), bx[1] + ys.min(), bx[0] + xs.max() + 1, bx[1] + ys.max() + 1)
    else:
        tight = bx
    box = [tight[0] - PAD_PX, tight[1] - PAD_PX, tight[2] + PAD_PX, tight[3] + PAD_PX]
    box = [max(box[0], 0), max(box[1], 0), min(box[2], Wpx), min(box[3], Hpx)]
    # 留白不得碰到文字：逐个检查与文字框相交的方向并退回到图片外框
    for c in page.chars:
        cx0, cy0, cx1, cy1 = c.x0 * SCALE, c.top * SCALE, c.x1 * SCALE, c.bottom * SCALE
        if cx1 <= box[0] or cx0 >= box[2] or cy1 <= box[1] or cy0 >= box[3]:
            continue
        if cy1 <= tight[1]:
            box[1] = max(box[1], math.ceil(cy1))
        elif cy0 >= tight[3]:
            box[3] = min(box[3], math.floor(cy0))
        elif cx1 <= tight[0]:
            box[0] = max(box[0], math.ceil(cx1))
        elif cx0 >= tight[2]:
            box[2] = min(box[2], math.floor(cx0))
    return full, tuple(int(v) for v in box)


def text_inside(page: Page, box_pt) -> str:
    x0, t0, x1, b0 = box_pt
    hit = [c.text for c in page.chars if c.x1 > x0 + 0.5 and c.x0 < x1 - 0.5 and c.bottom > t0 + 0.5 and c.top < b0 - 0.5]
    return ''.join(hit)


def png_size(raw: bytes):
    return struct.unpack('>II', raw[16:24])


# ---------------------------------------------------------------------------
# 读取配置、修正
# ---------------------------------------------------------------------------
def load_cfg(paper: str):
    pf = PAPERS_DIR / f'{paper}.json'
    if not pf.exists():
        die(f'没有登记文件 tools/papers/{paper}.json')
    cf = CORR_DIR / f'{paper}.json'
    corr = json.loads(cf.read_text(encoding='utf-8')) if cf.exists() else {}
    return json.loads(pf.read_text(encoding='utf-8')), corr


def paper_files(paper: str) -> dict:
    """一卷的全部输出位置；build 只写这些文件。"""
    return dict(jsonl=OUT / f'{paper}.jsonl', md=OUT / f'{paper}.md', assets=OUT / 'assets' / paper,
                manifest=OUT / 'assets' / paper / 'manifest.json', quality=OUT / 'quality' / f'{paper}.md',
                sources=OUT / 'sources' / f'{paper}.json')


def paper_sort_key(paper: str):
    cfg = json.loads((PAPERS_DIR / f'{paper}.json').read_text(encoding='utf-8'))
    suffix = paper.split('-', 1)[1] if '-' in paper else ''
    return (cfg.get('year', 0), {'XZ': 0, 'XJ': 1}.get(suffix, 2), paper)


def list_papers(built_only: bool = False) -> list:
    papers = [f.stem for f in PAPERS_DIR.glob('*.json') if not f.stem.startswith('_')]
    if built_only:
        papers = [p for p in papers if paper_files(p)['jsonl'].exists()]
    return sorted(papers, key=paper_sort_key)


def git(*args) -> str:
    return subprocess.run(['git', '-C', str(REPO), *args], capture_output=True, text=True, check=True).stdout.strip()


def apply_text_fixes(recs: dict, corr: dict, log: list) -> None:
    for fx in corr.get('text_fixes', []):
        r = recs.get(fx['q'])
        if r is None:
            die(f'text_fixes 指向不存在的第{fx["q"]}题')
        fld = fx['field']
        if fld == 'stem':
            holder, key = r, 'stem'
        elif fld.startswith('option:'):
            holder = next(o for o in r['options'] if o['label'] == fld.split(':')[1])
            key = 'text'
        else:
            die(f'未知字段 {fld}')
        cur = holder[key]
        if 'set' in fx:
            holder[key] = fx['set']
        else:
            if cur.count(fx['find']) != 1:
                die(f'第{fx["q"]}题 {fld}：要替换的“{fx["find"]}”出现 {cur.count(fx["find"])} 次（应为 1 次），请重新核对原卷后更新修正文件')
            holder[key] = cur.replace(fx['find'], fx['replace'])
        log.append(f'第{fx["q"]}题{"题干" if fld == "stem" else fld.split(":")[1] + "项"}：{fx["reason"]}')


# ---------------------------------------------------------------------------
# dump / answer-sheet
# ---------------------------------------------------------------------------
def cmd_dump(paper: str, raw: bool = True):
    cfg, corr = load_cfg(paper)
    pages = load_pages(REPO / cfg['question_pdf'])
    inline = {} if raw else corr.get('inline_images', {})
    seg = segment(pages, cfg['expected_questions'], inline, set(cfg.get('missing_questions', [])),
                  corr.get('section_map', {}), set(corr.get('bare_numbers', [])))
    if not raw:
        apply_figure_questions(seg, corr)
    left, right = seg['margins']
    print(f'# {paper}  页数 {len(pages)}  左右边界 {left:.1f}/{right:.1f}pt')
    for ln in seg['headings']:
        print(f'[部分标题 p{ln.page}] {ln.text}')
    for ln in seg['preamble']:
        print(f'[卷首 p{ln.page}] {ln.text}')
    for p in pages:
        for im in p.images:
            print(f'[图片 {im.key}] {"行内" if im.inline else "题图"} bbox=({im.x0:.1f},{im.top:.1f},{im.x1:.1f},{im.bottom:.1f})')
    autofix = []
    mats = {m.k: parse_material(m, left, right) for m in seg['materials']}
    for q in seg['questions']:
        if q.material and q.material in mats and mats[q.material]['questions'][0] == q.number:
            m = mats[q.material]
            print(f'\n=== 材料{m["k"]}（第{m["questions"][0]}—{m["questions"][-1]}题，p{m["pages"]}）标题段：{m["header_text"]}')
            for b in m['blocks']:
                print('  [图]', b['img'].key) if b['type'] == 'fig' else print('  [文]', b['text'])
        r = parse_question(q, left, right, autofix)
        if not raw:
            apply_option_fixes(r, corr, autofix)
        print(f'\n--- 第{r["number"]}题 [{r["section_raw"]}] p{r["pages"]} 图{[f.key for f in r["figures"]]}')
        print(r['stem'])
        for o in r['options']:
            print(f'  {o["label"]}. {o["text"]}')
        for st in r['strays']:
            print(f'  [无法归属的行] {st}')
    for im in seg['orphans']:
        print(f'[未归属图片] {im.key}')
    for a in autofix:
        print('[自动修正]', a)
    print(f'\n共识别 {len(seg["questions"])} 题（应为 {cfg["expected_questions"]}），材料 {len(seg["materials"])} 组')


ANS_DPI = 96                             # 扫描版答案页按 96 DPI 灰度渲染（与常见扫描件原始分辨率一致）
ANS_TEMPLATE = TOOLS / 'answer-template.png'   # 加粗“正确答案”四字的二值模板（取自2020年乡镇卷答案第1页第1题）
ANS_MATCH = 0.6                          # 归一化相关系数阈值：2020、2021两卷答案行均≥0.65，其余各行≤0.47
ANS_TEMPLATE2 = TOOLS / 'answer-template-concl.png'   # 常规字重“正确答案为”五字（取自2017年卷答案第2页“故正确答案为C。”）
CONCL_MATCH = 0.6                        # 结论行阈值（两种模板取高者）：2017—2019年各卷结论行多在0.9以上，其余行多低于0.5


def ink_lines(dark):
    """按水平投影切出文字行 [(top, bottom)]。"""
    rows, out, start = dark.sum(axis=1), [], None
    for y, v in enumerate(rows):
        if v and start is None:
            start = y
        elif not v and start is not None:
            out.append((start, y))
            start = None
    return out


def _ncc_best(band, T):
    """band 与模板 T 在横向各位置的归一化相关系数，返回 (最大值, 位置)。"""
    import numpy as np
    from numpy.lib.stride_tricks import sliding_window_view as swv
    th, tw = T.shape
    if band.shape[0] < th or band.shape[1] < tw:
        return -1.0, 0
    Tz = T - T.mean()
    Tn = math.sqrt(float((Tz ** 2).sum()))
    W = swv(band, (th, tw))[0]
    Wz = W - W.mean(axis=(1, 2), keepdims=True)
    den = np.sqrt((Wz ** 2).sum(axis=(1, 2))) * Tn
    sc = np.where(den > 0, (Wz * Tz).sum(axis=(1, 2)) / np.where(den > 0, den, 1), -1)
    i = int(sc.argmax())
    return float(sc[i]), i


def match_answer_lines(dark, T):
    """格式一（2020、2021年）：在一页中找“N、正确答案：X”行——模板在行首 10—60 像素处横向滑动、上下错 1—2 像素，
    取最大相关系数。"""
    import numpy as np
    th, tw = T.shape
    hits, lines = [], ink_lines(dark)
    for a, b in lines:
        if b - a < th - 2 or b - a > th + 6:
            continue
        lx = int(np.where(dark[a:b].any(axis=0))[0].min())
        best = -1.0
        for dy in range(-1, b - a - th + 2):
            top = a + dy
            if top < 0:
                continue
            best = max(best, _ncc_best(dark[top:top + th, lx + 10:lx + 60 + tw], T)[0])
        if best >= ANS_MATCH:
            hits.append((a, b, lx, best))
    return hits, lines


def match_conclusions(dark, lines, templates):
    """格式二（2016—2019年）：不带题号的结论行“故正确答案为X。”（也可能在行中，如“本题为选非题，故正确答案为X。”）。
    两种模板都在整行宽度内滑动，取较高者。返回 [(top, bottom, x, 模板宽, 得分)]，含得分≥0.5的全部行，由调用方按阈值分开。"""
    out = []
    for a, b in lines:
        best = (-1.0, 0, 0)
        for T in templates:
            th, tw = T.shape
            if b - a < th - 2 or b - a > th + 6:
                continue
            for dy in range(-1, b - a - th + 2):
                top = a + dy
                if top < 0:
                    continue
                sc, x = _ncc_best(dark[top:top + th], T)
                if sc > best[0]:
                    best = (sc, x, tw)
        if best[0] >= 0.5:
            out.append((a, b, best[1], best[2], best[0]))
    return out


def _stroke(blk) -> float:
    """字形笔画粗细：各像素行最长连续墨迹的中位数（加粗数字约2—3像素，常规字母约1像素）。"""
    vals = []
    for row in blk < 128:
        best = cur = 0
        for v in row:
            cur = cur + 1 if v else 0
            best = max(best, cur)
        if best:
            vals.append(best)
    return float(sorted(vals)[len(vals) // 2]) if vals else 0.0


def is_number_line(g, dark, a: int, b: int, margin: int, bold: bool = True) -> bool:
    """题号行“N、……”：行首在左边距处，1—3个数字宽的字形（两位数也可能粘成一个）后紧跟“、”（墨迹只在行的下半部）。
    bold=True 时还要求数字笔画粗（2016年以后的解析题号多为加粗），以排除“C、D两项”这类以字母开头的行。"""
    import numpy as np
    colm = dark[a:b].any(axis=0)
    xs = np.where(colm)[0]
    if not len(xs) or abs(int(xs.min()) - margin) > 3 or b - a < 9:
        return False
    runs, start = [], None
    for x in range(int(xs.min()), min(int(xs.min()) + 70, len(colm))):
        if colm[x] and start is None:
            start = x
        elif not colm[x] and start is not None:
            runs.append((start, x))
            start = None
    lead = []
    for r in runs:
        w = r[1] - r[0]
        rows = np.where(dark[a:b, r[0]:r[1]].any(axis=1))[0]
        if 2 <= w <= 5 and rows.min() >= (b - a) * 0.45:          # “、”或“，”“。”
            ys, xs_ = np.where(dark[a:b, r[0]:r[1]] > 0)
            if not lead or len(xs_) < 3 or float(np.cov(xs_, ys)[0, 1]) <= 0:
                return False                                       # “、”自左上向右下；“，”的尾巴向左下
            ws = [d[1] - d[0] for d in lead]
            if not (all(4 <= x <= 8 for x in ws) or (len(ws) == 1 and 9 <= ws[0] <= 16)):
                return False
            return not bold or all(_stroke(g[a:b, d[0]:d[1]]) >= 2.0 for d in lead)
        lead.append(r)
        if len(lead) > 3:
            return False
    return False


def contact_sheet(items, out: Path, width: int, scale: int, cols: int = 1, label_w: int = 120):
    """items: [(标签, 灰度PIL图)] → 拼成若干张图，返回文件列表。"""
    from PIL import Image, ImageDraw
    files, per = [], 34 * cols
    for k in range(0, len(items), per):
        chunk = items[k:k + per]
        cell_h = max(im.size[1] for _, im in chunk) * scale + 8
        cell_w = width * scale + label_w
        rows = (len(chunk) + cols - 1) // cols
        sheet = Image.new('L', (cell_w * cols, cell_h * rows), 255)
        d = ImageDraw.Draw(sheet)
        for i, (lab, im) in enumerate(chunk):
            r, c = divmod(i, cols)
            im = im.resize((im.size[0] * scale, im.size[1] * scale))
            sheet.paste(im, (c * cell_w + label_w, r * cell_h + 4))
            d.text((c * cell_w + 4, r * cell_h + cell_h // 2 - 6), lab, fill=0)
        fn = out.parent / f'{out.stem}-{k // per + 1:02d}.png'
        sheet.save(fn)
        files.append(fn)
    return files


def cmd_answer_sheet(paper: str, work: Path):
    """扫描版答案 PDF 的读取辅助（没有 OCR 时用），按两种解析格式各出一套拼图：
    格式一（2020、2021年：每题有“N、正确答案：X，全站正确率……”行）
      answer-lines-*.png  检测到的答案行（整行），第一遍按此逐题读取；
      answer-zoom-*.png   同一批行的行首（题号到答案字母）放大三倍、四列排开，第二遍按此独立重读。
    格式二（2016—2019年：每题解析以“N、”开头、以不带题号的“故正确答案为X。”结束）
      answer-pairs-*.png  按阅读顺序把每条结论行与它前面最近的题号行配对：左格为题号行行首，右格为结论句（含答案
                          字母），均放大三倍；没有配上的题号行或结论行单独成行，标 NO CONCLUSION / NO NUMBER LINE；
      answer-maybe-*.png  得分略低于阈值的行（多为“故本题选择X”等措辞不同的结论句或正文中的“正确答案”），供补查。
    两种格式共用：answer-check-*.png  “解析/拓展”等两字短行的上一行（多为“因此，选择X选项”），用来再核一次。
    有文字层的答案 PDF（选调卷等）：文字层按“N、”起、“正确答案为X”止直接取答案（build 自动使用）；另出
      answer-text-*.png   按文字层定位裁出每条结论句的答案字母（标 Q题号 p页码），目视读一遍写入 answers.by_page，
                          build 时与文字层逐题比对，不一致的记为争议。
    两遍读取一致后，按“页码: 题号答案 …”写入 tools/corrections/<卷>.json 的 answers.by_page。"""
    import numpy as np
    from PIL import Image, ImageDraw
    cfg, _ = load_cfg(paper)
    pdf = REPO / cfg['answer_pdf']
    work.mkdir(parents=True, exist_ok=True)
    for pat in ('ans-*.png', 'answer-lines-*.png', 'answer-zoom-*.png', 'answer-check-*.png',
                'answer-pairs-*.png', 'answer-maybe-*.png', 'answer-text-*.png', 'text-*.png'):
        for old in work.glob(pat):          # 只清理本命令自己生成的文件
            old.unlink()
    subprocess.run(['pdftoppm', '-r', str(ANS_DPI), '-gray', '-png', str(pdf), str(work / 'ans')], check=True, capture_output=True)
    T = (np.asarray(Image.open(ANS_TEMPLATE).convert('L')) < 128).astype(float)
    T2 = (np.asarray(Image.open(ANS_TEMPLATE2).convert('L')) < 128).astype(float)
    full, zoom, check, maybe = [], [], [], []
    events, imgs = [], {}
    for f in sorted(work.glob('ans-*.png'), key=lambda x: int(re.findall(r'(\d+)\.png$', x.name)[0])):
        pno = int(re.findall(r'(\d+)\.png$', f.name)[0])
        g = Image.open(f).convert('L')
        imgs[pno] = g
        garr = np.asarray(g).astype(int)
        dark = (garr < 140).astype(float)
        hits, lines = match_answer_lines(dark, T)
        for a, b, lx, sc in hits:
            n = len(full) + 1
            full.append((f'#{n} p{pno} y{a}', g.crop((30, a - 3, 30 + 520, b + 3))))
            zoom.append((f'#{n} p{pno}', g.crop((lx - 2, a - 3, lx + 150, b + 3))))
        info = [(a, b, *(lambda c: (c.min(), c.max()))(np.where(dark[a:b].any(axis=0))[0])) for a, b in lines]
        for i, (a, b, x0, x1) in enumerate(info):
            if b - a >= 8 and x1 - x0 < 45 and i > 0:      # 两字短行（解析、拓展）
                pa, pb, _, _ = info[i - 1]
                check.append((f'p{pno} y{pa}', g.crop((30, pa - 3, 30 + 520, pb + 3))))
        # 格式二：结论行与题号行
        tall = [ln for ln in lines if ln[1] - ln[0] >= 9]
        starts = [int(np.where(dark[a:b].any(axis=0))[0].min()) for a, b in tall]
        margin = sorted(starts)[len(starts) // 2] if starts else 0
        for a, b, x, tw, sc in match_conclusions(dark, lines, [T, T2]):
            if sc >= CONCL_MATCH:
                events.append((pno, a, 'C', (b, x, tw)))
            else:
                maybe.append((f'p{pno} y{a} {sc:.2f}', g.crop((30, a - 3, 30 + 520, b + 3))))
        for a, b in tall:
            events.append((pno, a, 'N', (b, margin, garr, dark)))
    events.sort(key=lambda e: (e[0], e[1], e[2]))
    conclusions = [e for e in events if e[2] == 'C']

    def numbers(bold):
        return [e for e in events if e[2] == 'N' and is_number_line(e[3][2], e[3][3], e[1], e[3][0], e[3][1], bold)]
    nums, rule = numbers(True), '加粗题号'
    if len(nums) < 0.5 * len(conclusions):
        nums, rule = numbers(False), '题号不加粗（未要求笔画粗细）'
    seq = sorted(conclusions + nums, key=lambda e: (e[0], e[1]))
    rows, pending = [], []
    for e in seq:
        if e[2] == 'N':
            pending.append(e)
            continue
        for u in pending[:-1]:
            rows.append((u, None))
        rows.append((pending[-1] if pending else None, e))
        pending = []
    rows += [(u, None) for u in pending]

    def pair_image(nl, cl):
        num = imgs[nl[0]].crop((nl[3][1] - 2, nl[1] - 3, nl[3][1] + 48, nl[3][0] + 3)) if nl else None
        con = None
        if cl:
            b, x, tw = cl[3]
            con = imgs[cl[0]].crop((max(x - 16, 0), cl[1] - 3, x + tw + 44, b + 3))
        cell_h = max([im.size[1] for im in (num, con) if im is not None] + [20])
        canvas = Image.new('L', (50 + 20 + 16 + 69 + 44 + 10, cell_h), 255)
        d = ImageDraw.Draw(canvas)
        if num:
            canvas.paste(num, (0, 0))
        else:
            d.text((2, 4), 'NO NUMBER LINE', fill=0)
        if con:
            canvas.paste(con, (70, 0))
        else:
            d.text((72, 4), 'NO CONCLUSION', fill=0)
        return canvas
    pairs = []
    for k, (nl, cl) in enumerate(rows, 1):
        where = f'p{(cl or nl)[0]}'
        flag = '' if nl and cl else ' !'
        pairs.append((f'#{k} {where}{flag}', pair_image(nl, cl)))
    out = []
    out += contact_sheet(full, work / 'answer-lines', 520, 2)
    out += contact_sheet(zoom, work / 'answer-zoom', 152, 3, cols=4, label_w=70)
    out += contact_sheet(pairs, work / 'answer-pairs', 209, 3, cols=2, label_w=80)
    out += contact_sheet(maybe, work / 'answer-maybe', 520, 2)
    out += contact_sheet(check, work / 'answer-check', 520, 2)
    found, stats = answer_text_layer(pdf)
    scanned = [p for p, n in stats if n < 30]
    exp = cfg['expected_questions'] - len(cfg.get('missing_questions', []))
    tconc = text_conclusions(pdf) if sum(n for _, n in stats) > 200 else []
    if tconc:
        # 文字层版格式二：按文字层定位每条结论句的答案字母，从页面渲染图裁出（字母与它前面几个字），供目视读第二遍
        tdpi, timgs, tiles = 200, {}, []
        for pno in sorted({c[2] for c in tconc}):
            stem = work / f'text-{pno:02d}'
            subprocess.run(['pdftoppm', '-r', str(tdpi), '-gray', '-png', '-singlefile', '-f', str(pno), '-l', str(pno),
                            str(pdf), str(stem)], check=True, capture_output=True)
            timgs[pno] = Image.open(stem.with_suffix('.png')).convert('L')
        k = tdpi / 72
        for n, v, pno, (x0, top, x1, bottom), raw in tconc:
            tiles.append((f'Q{n} p{pno}', timgs[pno].crop((int((x0 - 84) * k), int((top - 2) * k), int((x1 + 14) * k),
                                                           int((bottom + 2) * k)))))
        out += contact_sheet(tiles, work / 'answer-text', max(t.size[0] for _, t in tiles), 1, cols=3, label_w=70)
    print(f'答案PDF共 {len(stats)} 页，其中 {len(scanned)} 页几乎没有文字层（扫描页）。')
    print(f'文字层可直接取到的答案：{ {k: v["value"] for k, v in sorted(found.items())} }')
    if tconc:
        got = collections.Counter(c[0] for c in tconc)
        print(f'文字层格式二（“N、”起、“正确答案为X”止）：结论句 {len(tconc)} 条，涉及 {len(got)} 题；'
              f'没有结论句的题：{[n for n in range(1, cfg["expected_questions"] + 1) if n not in got and n not in found]}；'
              f'结论句多于一条的题：{sorted(n for n, c in got.items() if c > 1)}。'
              '请按 answer-text 拼图逐条目视读取答案字母，写入 answers.by_page；build 时与文字层逐题比对。')
    print(f'格式一：检测到“N、正确答案：X”行 {len(full)} 条（本卷应有约 {exp} 条）。')
    unpaired_n = sum(1 for nl, cl in rows if cl is None)
    unpaired_c = sum(1 for nl, cl in rows if nl is None)
    print(f'格式二：结论行 {len(conclusions)} 条，题号行 {len(nums)} 条（{rule}），配成 {len(rows) - unpaired_n - unpaired_c} 对；'
          f'没有结论行的题号行 {unpaired_n} 条，没有题号行的结论行 {unpaired_c} 条（拼图中标“!”）；'
          f'得分略低于阈值的行 {len(maybe)} 条（answer-maybe）。')
    print('哪种格式的条数接近本卷题数，就按哪种格式的拼图读取；标“!”的行与 answer-maybe 中的行须对照整页确认。')
    for fn in out:
        print('  ', fn)
    print(f'两遍读取一致后，按 “页码: 题号答案 …” 写入 tools/corrections/{paper}.json 的 answers.by_page。')


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------
def build(paper: str, work: Path | None):
    cfg, corr = load_cfg(paper)
    qpdf, apdf = REPO / cfg['question_pdf'], (REPO / cfg['answer_pdf'] if cfg.get('answer_pdf') else None)
    commit = source_commit(cfg, paper)
    inline_text = corr.get('inline_images', {})
    pages = load_pages(qpdf)
    page_by_no = {p.no: p for p in pages}
    missing_q = set(cfg.get('missing_questions', []))
    seg = segment(pages, cfg['expected_questions'], inline_text, missing_q, corr.get('section_map', {}),
                  set(corr.get('bare_numbers', [])))
    apply_figure_questions(seg, corr)
    left, right = seg['margins']
    autofix, fixlog, problems = [], [], []
    if len(seg['questions']) != cfg['expected_questions'] - len(missing_q):
        die(f'只识别出 {len(seg["questions"])} 题（应为 {cfg["expected_questions"] - len(missing_q)}）；先用 dump 检查分题，'
            f'原卷缺题请在 tools/papers/{paper}.json 的 missing_questions 中声明')
    if seg['orphans']:
        die(f'有未归属的图片：{[i.key for i in seg["orphans"]]}')
    all_inline = [im.key for p in pages for im in p.images if im.inline]
    missing_inline = [k for k in all_inline if k not in inline_text]
    if missing_inline:
        die(f'行内小图未在 tools/corrections/{paper}.json 的 inline_images 中给出文字：{missing_inline}')

    recs = {}
    ignore = corr.get('ignore_lines', [])
    for q in seg['questions']:
        recs[q.number] = parse_question(q, left, right, autofix)
        apply_option_fixes(recs[q.number], corr, autofix)
        for st in recs[q.number]['strays']:
            if any(st.replace(' ', '').startswith(x) for x in ignore):
                autofix.append(f'第{q.number}题选项后的“{st}”按 ignore_lines 不收录。')
            else:
                die(f'第{q.number}题选项之后有一行无法归属：“{st}”。核对原卷后，若是题目内容请用 text_fixes 补入，'
                    f'若非试题内容（如“××题暂缺”说明）请写入 tools/corrections/{paper}.json 的 ignore_lines')
    mats = {m.k: parse_material(m, left, right) for m in seg['materials']}
    groups = [[m['questions'][0], m['questions'][-1]] if m['questions'] else [] for m in mats.values()]
    if 'material_groups' in corr and groups != corr['material_groups']:
        die(f'识别出的材料题组 {groups} 与 tools/corrections/{paper}.json 的 material_groups {corr["material_groups"]} 不符；先用 dump 检查材料分段')
    for r in recs.values():
        for o in r['options']:
            if (len(o['text']) > 80 and o['label'] not in corr.get('long_options', {}).get(str(r['number']), '')) \
                    or '\n' in o['text']:
                problems.append(f'第{r["number"]}题{o["label"]}项过长（{len(o["text"])}字），可能并入了下一题题干或材料，请核对')

    # 章节
    smap = dict(SECTION_ALIASES, **corr.get('section_map', {}))
    for r in recs.values():
        raw = r['section_raw']
        r['section'] = smap.get(raw, raw)
        r['notes'] = []
    for rng in corr.get('section_ranges', []):
        for n in range(rng['from'], rng['to'] + 1):
            recs[n]['section'] = rng['section']
            if rng.get('note'):
                recs[n]['notes'].append(rng['note'])
    for r in recs.values():
        if r['section'] not in SECTION_NAMES:
            die(f'第{r["number"]}题章节“{r["section"]}”不在 schema 范围内')

    apply_text_fixes(recs, corr, fixlog)
    for r in recs.values():
        r['stem'] = normalize_blanks(r['stem'], r['section'])
        for o in r['options']:
            o['text'] = o['text'].strip()
        if r['options'] and [o['label'] for o in r['options']] != list('ABCD'):
            die(f'第{r["number"]}题选项拆分异常：{[o["label"] for o in r["options"]]}')
        if '⟦' in r['stem'] or any('⟦' in o['text'] for o in r['options']):
            die(f'第{r["number"]}题仍有未转写的行内小图')

    # 文字守恒：输出的题干+选项 = 文字层原字符 − 题号 − 选项字母 + 行内小图转写（空白不计）
    conserve = []
    for n, r in recs.items():
        want = collections.Counter(re.sub(r'\s', '', r['raw'][len(r['prefix']):] if r['raw'].startswith(r['prefix']) else r['raw']))
        want -= collections.Counter(re.sub(r'\s', '', ''.join(r['labels_raw'])))
        want += collections.Counter(re.sub(r'\s', '', ''.join(inline_text[k] for k in r['inline'])))
        got = collections.Counter(re.sub(r'\s', '', r['stem'] + ''.join(o['text'] for o in r['options'])))
        if got != want:
            lost, extra = ''.join(sorted((want - got).elements())), ''.join(sorted((got - want).elements()))
            fixed = any(fx['q'] == n for fx in corr.get('text_fixes', []))
            conserve.append((n, lost, extra, fixed))
    bad = [c for c in conserve if not c[3]]
    if bad:
        die('文字守恒检查不通过（题号, 少了的字, 多出的字）：' + '；'.join(f'{n}: -{l!r} +{e!r}' for n, l, e, _ in bad))

    # 题图
    fig_cfg = corr.get('figures', {})
    fig_pages = sorted({f.page for r in recs.values() for f in r['figures']} |
                       {b['img'].page for m in mats.values() for b in m['blocks'] if b['type'] == 'fig'})
    own_work = work is None
    work = work or Path(tempfile.mkdtemp(prefix=f'{paper}-'))
    renders = render_pages(qpdf, fig_pages, work / 'render')
    files = paper_files(paper)
    asset_dir = files['assets']
    if asset_dir.exists():
        shutil.rmtree(asset_dir)
    asset_dir.mkdir(parents=True)
    manifest = []

    def make_figure(im: Img, role: str, qnums: list, default_alt: str):
        fid = f'{paper}-{im.key}'
        fc = fig_cfg.get(im.key, {})
        full, box = crop_box(renders[im.page], im, page_by_no[im.page], fc.get('bbox'))
        if fc.get('bbox'):
            fixlog.append(f'{fid}（第{"、".join(map(str, qnums))}题）：{fc.get("reason", "按人工指定的裁剪框裁图")}')
        crop = full.crop(box)
        path = asset_dir / f'{fid}.png'
        crop.save(path, format='PNG', optimize=True)
        raw = path.read_bytes()
        w, h = png_size(raw)
        bbox_pt = [round(box[0] / SCALE, 2), round(box[1] / SCALE, 2), round(box[2] / SCALE, 2), round(box[3] / SCALE, 2)]
        leak = text_inside(page_by_no[im.page], bbox_pt)
        if leak:
            problems.append(f'{fid} 裁剪框内含文字层字符：{leak}')
        manifest.append(dict(id=fid, path=f'assets/{paper}/{fid}.png', paper_id=paper, source_page=im.page,
                             source_bbox_points=bbox_pt, method='pdf_render_crop', width=w, height=h,
                             sha256=hashlib.sha256(raw).hexdigest(), transcription=fc.get('transcription', '')))
        obj = dict(type='image', image_id=fid, path=f'assets/{paper}/{fid}.png', role=role, option_label=None,
                   method='pdf_render_crop', alt=fc.get('alt', default_alt), transcription=fc.get('transcription', ''))
        return obj

    for n in sorted(recs):
        r = recs[n]
        figs = []
        for im in r['figures']:
            role = fig_cfg.get(im.key, {}).get('role') or ('question' if r['options'] else 'question_and_options')
            alt = f'{paper} 第{im.page}页 第{n}题题图' + ('（含选项A—D）' if role == 'question_and_options' else '')
            figs.append(make_figure(im, role, [n], alt))
        r['figure_objs'] = figs
        # 画有选项 A—D 的图（role=question_and_options）：没有文字选项时，选项全指向它；
        # 有文字选项（如“如上图所示”）时，文字照录，并同样指向图中对应字母
        qo = [f for f in figs if f['role'] == 'question_and_options']
        if not r['options']:
            if len(qo) != 1:
                die(f'第{n}题没有文字选项，画有选项的题图应恰好 1 张（现为 {len(qo)} 张）；'
                    f'请在 tools/corrections/{paper}.json 的 figures 中把只含题目部分的图设为 role: "question"')
            r['options'] = [{'label': L, 'text': '', 'image_refs': [{'image_id': qo[0]['image_id'], 'label_in_image': L}]}
                            for L in 'ABCD']
        else:
            for o in r['options']:
                o['image_refs'] = [{'image_id': qo[0]['image_id'], 'label_in_image': o['label']}] if len(qo) == 1 else []
        link_option_figures(n, paper, figs, r['options'], corr)

    # 材料
    mat_objs = {}
    for k, m in mats.items():
        mc = corr.get('materials', {}).get(str(k), {})
        content = []
        for b in m['blocks']:
            if b['type'] == 'text':
                content.append({'type': 'text', 'text': b['text']})
            else:
                alt = f'{paper} 第{b["img"].page}页 资料分析材料{k}图表'
                content.append(make_figure(b['img'], 'material', m['questions'], alt))
        mat_objs[k] = dict(id=f'{paper}-M{k}', question_numbers=m['questions'], source_pages=m['pages'], content=content)
        raw_m = ''.join(t.text for kind_, o in seg['materials'][k - 1].items if kind_ == 'line' for t in o.toks if not t.image)
        out_m = ''.join(b['text'] for b in content if b['type'] == 'text')
        if collections.Counter(re.sub(r'\s', '', raw_m)) + collections.Counter(re.sub(r'\s', '', ''.join(inline_text[x] for x in m['inline']))) != collections.Counter(re.sub(r'\s', '', out_m)):
            die(f'材料{k}文字守恒检查不通过')
        if m['header_note']:
            autofix.append(f'材料{k}标题后的编者按语不作为材料内容收录：“{redact(m["header_note"])}”')
        for n in m['questions']:
            for note in mc.get('question_notes', []):
                recs[n]['notes'].append(note)

    # 小类
    for n, r in recs.items():
        if r['section'] == '判断推理':
            st = corr.get('subtypes', {}).get(str(n)) or classify_subtype({'stem': r['stem'], 'options': r['options'], 'figures': r['figure_objs']})
            if st not in SUBTYPES:
                die(f'第{n}题小类“{st}”无效')
            r['notes'].insert(0, f'subtype:{st}')
    for n, notes in corr.get('question_notes', {}).items():
        recs[int(n)]['notes'].extend(notes)

    # 答案
    text_ans, stats = answer_text_layer(apdf) if apdf else ({}, [])
    man_ans = manual_answers(corr.get('answers'))
    ans_notes = corr.get('answer_notes', {})
    answer_log = dict(text=text_ans, manual=man_ans, stats=stats, conflicts=[], missing=[])
    for n, r in recs.items():
        t, mnl = text_ans.get(n), man_ans.get(n)
        cands = []
        for src in (mnl, t):
            if src and src['value'] not in [c['value'] for c in cands]:
                cands.append(src)
        if not cands:
            r['answer'] = dict(status='missing', values=[], source_pages=[], note=ans_notes.get(str(n), '答案PDF中未找到本题答案；未推测答案。'))
            answer_log['missing'].append(n)
            continue
        vals = [list(c['value']) if c['value'] not in ('正确', '错误') else [c['value']] for c in cands]
        pages_ = sorted({c['page'] for c in cands})
        if len(cands) > 1:
            answer_log['conflicts'].append((n, [c['value'] for c in cands]))
            r['answer'] = dict(status='disputed', values=vals, source_pages=pages_,
                               note=ans_notes.get(str(n), '答案PDF的图片与文字层给出不同答案，保留争议，不自行裁定。'))
        else:
            r['answer'] = dict(status='known', values=vals, source_pages=pages_, note=ans_notes.get(str(n), ''))
        typ = 'multiple_choice' if len(vals[0]) > 1 else 'single_choice'
        r['question_type'] = 'true_false' if vals[0][0] in ('正确', '错误') else typ
    for r in recs.values():
        r.setdefault('question_type', 'single_choice')

    # 组装记录
    qpdf_rel, apdf_rel = cfg['question_pdf'], cfg.get('answer_pdf')
    records = []
    for n in sorted(recs):
        r = recs[n]
        rec = collections.OrderedDict()
        rec['id'] = f'{paper}-Q{n:03d}'
        rec['year'] = cfg['year']
        rec['province'] = '广东'
        rec['exam'] = cfg.get('exam', '公务员录用考试')
        rec['subject'] = cfg.get('subject', '行政职业能力测验')
        rec['paper_id'] = paper
        rec['paper_variant'] = cfg['paper_variant']
        rec['source_edition'] = cfg['source_edition']
        rec['question_number'] = n
        rec['section'] = r['section']
        rec['question_type'] = r['question_type']
        rec['stem'] = r['stem']
        rec['options'] = [{'label': o['label'], 'text': o['text'], 'image_refs': o['image_refs']} for o in r['options']]
        rec['figures'] = r['figure_objs']
        rec['material'] = mat_objs.get(r['material']) if r['material'] else None
        rec['answer'] = r['answer']
        rec['source'] = dict(question_pdf=qpdf_rel, question_pages=r['pages'], answer_pdf=apdf_rel, repository_commit=commit)
        rec['notes'] = r['notes']
        records.append(rec)

    # 写文件：只写本卷自己的文件
    files['jsonl'].write_text(''.join(json.dumps(r, ensure_ascii=False, separators=(',', ':')) + '\n' for r in records), encoding='utf-8')
    files['manifest'].write_text(json.dumps(sorted(manifest, key=lambda e: e['id']), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    write_sources(cfg, commit, paper)
    files['md'].write_text(render_md(records, cfg, paper, commit), encoding='utf-8')
    files['quality'].parent.mkdir(exist_ok=True)
    files['quality'].write_text(render_report(records, cfg, corr, paper, commit, autofix, fixlog, problems,
                                              answer_log, manifest, all_inline, seg, conserve), encoding='utf-8')
    _PAGE_CACHE.clear()
    if own_work:
        shutil.rmtree(work, ignore_errors=True)
    print(f'已生成 {paper}：{len(records)} 题，题图/材料图 {len(manifest)} 张' + ('' if own_work else f'；渲染缓存 {work}'))
    if problems:
        print('需要处理的问题：\n  ' + '\n  '.join(problems))
    return records


CONTACT = re.compile(r'微信|QQ|qq|公众号|电话|WeChat|wx[:：]', re.I)
PAIRS = {'（': '）', '(': ')', '【': '】', '[': ']'}


def redact(s: str) -> str:
    """编者按语中常带署名、联系方式等推广信息：去掉包含联系方式的最外层括号整段，写入报告前使用。"""
    while True:
        m = CONTACT.search(s)
        if not m:
            return s
        stack, start = [], None
        for i, ch in enumerate(s[:m.start()]):
            if ch in PAIRS:
                stack.append(i)
            elif ch in PAIRS.values() and stack:
                stack.pop()
        if not stack:
            s = s[:m.start()] + s[m.end():]
            continue
        start = stack[0]
        depth, end = 0, len(s) - 1
        for j in range(start, len(s)):
            if s[j] in PAIRS:
                depth += 1
            elif s[j] in PAIRS.values():
                depth -= 1
                if depth == 0:
                    end = j
                    break
        s = s[:start] + s[end + 1:]


def github_repo() -> str:
    try:
        m = re.search(r'github\.com[:/](.+?)(?:\.git)?$', git('remote', 'get-url', 'origin'))
        return m.group(1) if m else ''
    except subprocess.CalledProcessError:
        return ''


def blob_at(commit: str, rel: str) -> str:
    line = git('ls-tree', commit, '--', rel)
    return line.split()[2] if line else ''


def source_commit(cfg: dict, paper: str) -> str:
    """提取所基于的提交：papers 中指定的 source_commit，或本卷 sources 文件已记录的提交——只要源 PDF 的 blob 与
    HEAD、工作区一致就沿用，避免仓库有无关提交时每题的 repository_commit 跟着变；否则用 HEAD。"""
    head = git('rev-parse', 'HEAD')
    rels = [r for r in (cfg['question_pdf'], cfg.get('answer_pdf')) if r]
    cands = [cfg['source_commit']] if cfg.get('source_commit') else []
    f = paper_files(paper)['sources']
    if f.exists():
        cands.append(json.loads(f.read_text(encoding='utf-8'))['commit'])
    for c in cands:
        try:
            full = git('rev-parse', c)
        except subprocess.CalledProcessError:
            continue
        if all(blob_at(full, r) and blob_at(full, r) == blob_at(head, r) == git('hash-object', '--', r) for r in rels):
            return full
    return head


def write_sources(cfg: dict, commit: str, paper: str) -> None:
    """sources/<卷>.json：源 PDF 在提交中的 blob，并核对与工作区文件一致。"""
    remote, srcs = github_repo(), []
    for rel in [cfg['question_pdf'], cfg.get('answer_pdf')]:
        if not rel:
            continue
        line = git('ls-tree', '-l', commit, '--', rel)
        if not line:
            die(f'{rel} 不在提交 {commit} 中')
        meta, _ = line.split('\t', 1)
        mode, typ, sha, size = meta.split()
        if git('hash-object', '--', rel) != sha:
            die(f'{rel} 与提交中的版本不一致')
        srcs.append(dict(path=rel, mode=mode, type=typ, sha=sha, size=int(size),
                         url=f'https://api.github.com/repos/{remote}/git/blobs/{sha}' if remote else ''))
    f = paper_files(paper)['sources']
    f.parent.mkdir(exist_ok=True)
    f.write_text(json.dumps({'paper_id': paper, 'commit': commit, 'sources': sorted(srcs, key=lambda x: x['path'])},
                            ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def blob_url(commit: str, rel: str) -> str:
    repo = github_repo()
    if repo:
        return f'https://github.com/{repo}/blob/{commit}/' + urllib.parse.quote(rel)
    return '../../../' + urllib.parse.quote(rel)


def num_ranges(nums) -> str:
    """[46,47,48,50] → '46—48、50'"""
    nums = sorted(nums)
    out, i = [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        out.append(str(nums[i]) if i == j else f'{nums[i]}—{nums[j]}')
        i = j + 1
    return '、'.join(out)


def pages_cn(pages):
    return '、'.join(str(p) for p in pages)


def answer_md(a: dict) -> str:
    if a['status'] == 'known':
        return '**答案：' + ''.join(a['values'][0]) + '**'
    if a['status'] == 'disputed':
        return '**答案：争议：' + ' 或 '.join(''.join(v) for v in a['values']) + '（原答案列出，不自行裁定）**'
    return '**答案：缺失（' + (a['note'] or '答案PDF中未找到') + '）**'


def render_md(records, cfg, paper, commit) -> str:
    qtype_cn = {'single_choice': '单选', 'multiple_choice': '多选', 'true_false': '判断'}
    out = [f'# {cfg["title"]}', '',
           f'共 {len(records)} 题，原题号完整保留。内容：题干、选项、答案（不收解析）；资料分析共用材料置于所属题组前，JSONL 每条记录完整内嵌材料。', '',
           f'[结构化数据]({paper}.jsonl) · [字段说明](schema.json) · [质量报告](quality/{paper}.md)', '',
           f'原题来源：[{Path(cfg["question_pdf"]).name}]({blob_url(commit, cfg["question_pdf"])})。']
    if cfg.get('answer_pdf'):
        out[-1] += f'答案来源：[{Path(cfg["answer_pdf"]).name}]({blob_url(commit, cfg["answer_pdf"])})（只取答案）。'
    def common(rs):
        if len(rs) < 2:
            return []
        c = [n for n in rs[0]['notes'] if not n.startswith('subtype:')]
        return [n for n in c if all(n in r['notes'] for r in rs[1:])]
    by_sec, by_mat = collections.defaultdict(list), collections.defaultdict(list)
    for r in records:
        by_sec[r['section']].append(r)
        if r['material']:
            by_mat[r['material']['id']].append(r)
    sec_notes = {k: common(v) for k, v in by_sec.items()}
    mat_notes = {k: [n for n in common(v) if n not in sec_notes[v[0]['section']]] for k, v in by_mat.items()}
    section, shown_mat = None, set()
    for r in records:
        if r['section'] != section:
            section = r['section']
            out += ['', f'## {section}']
            for n in sec_notes[section]:
                out += ['', f'> 说明：{n}']
        m = r['material']
        if m and m['id'] not in shown_mat:
            shown_mat.add(m['id'])
            qn = m['question_numbers']
            out += ['', f'<a id="{m["id"]}"></a>', '', f'### 共用材料：第 {qn[0]}—{qn[-1]} 题']
            for b in m['content']:
                if b['type'] == 'text':
                    out += ['', b['text']]
                else:
                    out += ['', f'![{b["alt"]}]({b["path"]})']
                    if b['transcription']:
                        out += ['', b['transcription']]
            for n in mat_notes[m['id']]:
                out += ['', f'> 材料说明：{n}']
        sub = next((n.split(':', 1)[1] for n in r['notes'] if n.startswith('subtype:')), None)
        meta = f'`{r["id"]}` · {qtype_cn[r["question_type"]]}' + (f' · {sub}' if sub else '') + f' · 原卷第 {pages_cn(r["source"]["question_pages"])} 页'
        out += ['', f'<a id="{r["id"]}"></a>', '', f'### 第 {r["question_number"]} 题', '', meta]
        if m:
            out += ['', f'[共用材料](#{m["id"]})']
        out += ['', r['stem']]
        for f in r['figures']:
            out += ['', f'![{f["alt"]}]({f["path"]})']
            if f['transcription']:
                out += ['', f['transcription']]
        for o in r['options']:
            if o['text']:
                txt = o['text']
            elif o['image_refs']:
                txt = f'见上方题图中 {o["image_refs"][0]["label_in_image"] or o["label"]} 项。'
            else:
                txt = ''
            out += ['', f'**{o["label"]}.** {txt}']
        out += ['', answer_md(r['answer'])]
        if r['answer']['note'] and r['answer']['status'] == 'known':
            out += ['', f'> 答案说明：{r["answer"]["note"]}']
        shared = set(sec_notes[r['section']]) | set(mat_notes.get(m['id'], []) if m else [])
        for n in r['notes']:
            if not n.startswith('subtype:') and n not in shared:
                out += ['', f'> 转写说明：{n}']
    return '\n'.join(out) + '\n'


def render_report(records, cfg, corr, paper, commit, autofix, fixlog, problems, answer_log, manifest, all_inline, seg, conserve) -> str:
    sec_count = collections.Counter(r['section'] for r in records)
    sub_count = collections.Counter(n.split(':', 1)[1] for r in records for n in r['notes'] if n.startswith('subtype:'))
    sub_ranges = collections.defaultdict(list)
    for r in records:
        for n in r['notes']:
            if n.startswith('subtype:'):
                sub_ranges[n.split(':', 1)[1]].append(r['question_number'])
    status = collections.Counter(r['answer']['status'] for r in records)
    mats = {r['material']['id']: r['material'] for r in records if r['material']}
    srcs = json.loads(paper_files(paper)['sources'].read_text(encoding='utf-8'))['sources']
    sha = {s['path']: s['sha'] for s in srcs}
    order = []
    for r in records:
        if r['section'] not in order:
            order.append(r['section'])
    L = [f'# {paper} 转换与校验记录', '',
         f'范围：{cfg["title"]}，共 {len(records)} 题。来源为仓库内题本与答案解析各 1 份 PDF，均未修改；'
         f'提取基于提交 `{commit}`。', '',
         '| 文件 | Git blob | 用途 |', '| --- | --- | --- |',
         f'| `{cfg["question_pdf"]}` | `{sha.get(cfg["question_pdf"], "")}` | 题干、选项、材料、题图（有文字层） |']
    if cfg.get('answer_pdf'):
        L.append(f'| `{cfg["answer_pdf"]}` | `{sha.get(cfg["answer_pdf"], "")}` | 只取答案，不收解析 |')
    L += ['', '## 完整性', '', '| 部分 | 题号 | 题数 |', '| --- | --- | ---: |']
    for s in order:
        nums = [r['question_number'] for r in records if r['section'] == s]
        runs, prev = [], None          # 按卷内顺序连续的题号成一段（原卷缺题不断开），部分被别的部分隔开时分段列出
        for i, r in enumerate(records):
            if r['section'] == s:
                if prev is not None and prev == i - 1:
                    runs[-1][1] = r['question_number']
                else:
                    runs.append([r['question_number'], r['question_number']])
                prev = i
        span = '、'.join(f'{a}—{b}' if a != b else f'{a}' for a, b in runs)
        L.append(f'| {s} | {span} | {len(nums)} |')
    L += [f'| 合计 | | {len(records)} |', '']
    if sub_count:
        L += ['判断推理小类（记在 notes，如 `subtype:类比推理`）：' +
              '，'.join(f'{k} {sub_count[k]} 题（第{num_ranges(sub_ranges[k])}题）' for k in SUBTYPES if sub_count[k]) + '。', '']
    nfig_q = sum(len(r['figures']) for r in records)
    qtypes = collections.Counter(r['question_type'] for r in records)
    qtype_cn = {'single_choice': '单选', 'multiple_choice': '多选', 'true_false': '判断'}
    nmat_img = len({b['image_id'] for m in mats.values() for b in m['content'] if b['type'] == 'image'})
    L += [f'- 资料分析共用材料 {len(mats)} 组，关联 {sum(len(m["question_numbers"]) for m in mats.values())} 题；每题 JSONL 内嵌完整材料。',
          f'- 图片 {len(manifest)} 张：题图 {nfig_q} 张、材料图 {nmat_img} 张，全部为 288 DPI 页面渲染后的裁剪（`pdf_render_crop`），无重绘。',
          f'- 行内小图 {len(all_inline)} 个（分数、根号、化学方程式）已转成文字，不另存图片：' + '、'.join(f'`{k}`' for k in all_inline) + '。',
          f'- 文字守恒检查：每题“题干+选项”与该题在原 PDF 文字层中的字符逐一相符（不计空白、题号与选项字母，行内小图按转写计）'
          + ('，' + str(len(records)) + ' 题全部通过' if not conserve else f'；人工修正造成差异的题：{[c[0] for c in conserve]}')
          + (f'；{len(mats)} 组材料正文同样相符。' if mats else '。'),
          '- 题型按答案判定（单选一个字母、多选多个字母）：' + '，'.join(f'{qtype_cn[k]} {v} 题' for k, v in qtypes.items()) + '。', '']
    custom = corr.get('report', {})
    L += ['## 答案', '', '| 状态 | 数量 |', '| --- | ---: |']
    for k, cn in [('known', '明确答案'), ('disputed', '争议答案'), ('missing', '答案缺失')]:
        L.append(f'| {cn}（`{k}`） | {status.get(k, 0)} |')
    stats = answer_log['stats']
    scanned = [p for p, n in stats if n < 30]
    texty = [p for p, n in stats if 0 < n < 30]
    tq, mq = set(answer_log['text']), set(answer_log['manual'])
    both = sorted(tq & mq)
    L += ['', f'答案PDF共 {len(stats)} 页，其中 {len(scanned)} 页为扫描图片、没有可用的正文文字层'
              + (f'（第{"、".join(map(str, texty))}页另有后加的少量文字）' if texty else '') + '。'
              + (f'文字层直接取到 {len(tq)} 题（' + '、'.join(f'{k}{v["value"]}' for k, v in sorted(answer_log['text'].items())) + '）；' if tq else '文字层没有取到答案；')
              + (f'{"扫描图" if scanned else "页面渲染图"}人工读取 {len(mq)} 题（第{num_ranges(sorted(mq))}题，记录在 `tools/corrections/{paper}.json` 的 `answers.by_page`）。' if mq else '')
              + (f'两处都有的第{num_ranges(both)}题逐一比对' + ('，结果一致。' if not answer_log['conflicts'] else f'，不一致：{answer_log["conflicts"]}。') if both else '')]
    if answer_log['missing']:
        L.append(f'缺失答案：{answer_log["missing"]}。')
    for item in custom.get('answers', []):
        L += ['', f'- {item}']
    L += ['', '## 源文件问题与处理', '']
    for item in custom.get('source_issues', []):
        L.append(f'- {item}')
    for item in autofix:
        L.append(f'- 自动处理：{item}')
    for item in fixlog:
        L.append(f'- 人工修正：{item}')
    L += ['', '## 转写拿不准、需要留意的地方', '']
    for item in custom.get('uncertain', []):
        L.append(f'- {item}')
    L += ['', '## 题图与材料图', '',
          '裁剪框取原 PDF 中图片对象的外框，收紧到有墨迹处并留 1.5pt 白边，再检查框内不含任何文字层字符'
          f'（题干、选项文字不入图；画在图中的选项字母 A—D 属于图片本身，随图保留）。`assets/{paper}/manifest.json`（汇总于根目录 `assets-manifest.json`）记录来源页、'
          '裁剪框（PDF pt，左上角为原点）、像素尺寸与 SHA-256；像素尺寸 = 裁剪框 × 4（288 DPI），可按 pt 尺寸原大印刷。', '',
          '| 图片 | 题号 | 页 | 裁剪框（pt） | 像素 | 文字转写 |', '| --- | --- | ---: | --- | --- | --- |']
    usage = collections.defaultdict(list)
    for r in records:
        for f in r['figures']:
            usage[f['image_id']].append(str(r['question_number']))
    for m in mats.values():
        for b in m['content']:
            if b['type'] == 'image':
                usage[b['image_id']] = [f'{m["question_numbers"][0]}—{m["question_numbers"][-1]}（材料）']
    for e in manifest:
        bb = ', '.join(f'{v:g}' for v in e['source_bbox_points'])
        L.append(f'| `{e["id"]}` | {"、".join(usage[e["id"]])} | {e["source_page"]} | {bb} | {e["width"]}×{e["height"]} | {"有" if e["transcription"] else "—"} |')
    L += ['', f'脚本检查：{len(manifest)} 张图的裁剪框内均没有文字层字符。' if not problems
          else '脚本检查发现问题：' + '；'.join(problems)]
    L += ['', '## 复核方法', '']
    for item in custom.get('review', []):
        L.append(f'- {item}')
    L += ['', '## 重跑', '', '```bash',
          f'python3 tools/extract.py build {paper}   # 读取 tools/papers/{paper}.json 与 tools/corrections/{paper}.json，只重写本卷文件',
          'python3 tools/extract.py index            # 重新合并根目录汇总（all.jsonl、assets-manifest.json、sources.json、quality-report.md、README.md）',
          'python3 tools/extract.py verify           # 校验全部卷（schema、题号、答案、材料、图片哈希、Markdown 链接）与汇总',
          '```', '']
    return '\n'.join(L)


# ---------------------------------------------------------------------------
# index：由各卷文件合并根目录汇总
# ---------------------------------------------------------------------------
def read_jsonl(path: Path) -> list:
    return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]


def index_outputs() -> dict:
    """由各卷文件生成根目录汇总的内容（不写盘；verify 用它检查汇总是否最新）。"""
    papers = list_papers(built_only=True)
    if not papers:
        die('还没有已生成的卷，先运行 build')
    alltxt, recs, cfgs, manifest, srcs = '', {}, {}, [], []
    for p in papers:
        f = paper_files(p)
        txt = f['jsonl'].read_text(encoding='utf-8')
        alltxt += txt
        recs[p] = [json.loads(x) for x in txt.splitlines() if x.strip()]
        cfgs[p] = load_cfg(p)
        manifest += json.loads(f['manifest'].read_text(encoding='utf-8'))
        srcs.append(json.loads(f['sources'].read_text(encoding='utf-8')))
    commits = sorted({x['commit'] for x in srcs})
    entries = {}
    for x in srcs:
        for e in x['sources']:
            e = dict(e)
            if len(commits) > 1:
                e['commit'] = x['commit']
            entries[e['path']] = e
    sources = {'commit': commits[0] if len(commits) == 1 else None,
               'sources': sorted(entries.values(), key=lambda e: e['path'])}
    manifest.sort(key=lambda e: e['id'])
    return {
        'all.jsonl': alltxt,
        'assets-manifest.json': json.dumps(manifest, ensure_ascii=False, indent=2) + '\n',
        'sources.json': json.dumps(sources, ensure_ascii=False, indent=2) + '\n',
        'quality-report.md': render_quality_index(papers, recs, cfgs, manifest, sources),
        'README.md': render_readme(papers, recs, cfgs, manifest, sources),
    }


def paper_stats(rs: list) -> dict:
    st = collections.Counter(r['answer']['status'] for r in rs)
    mats = {r['material']['id']: r['material'] for r in rs if r['material']}
    figs = {f['image_id'] for r in rs for f in r['figures']}
    mimgs = {b['image_id'] for m in mats.values() for b in m['content'] if b['type'] == 'image'}
    return dict(n=len(rs), known=st.get('known', 0), disputed=st.get('disputed', 0), missing=st.get('missing', 0),
                mats=len(mats), figs=len(figs), mimgs=len(mimgs),
                sec=collections.Counter(r['section'] for r in rs),
                sub=collections.Counter(n.split(':', 1)[1] for r in rs for n in r['notes'] if n.startswith('subtype:')))


def render_quality_index(papers, recs, cfgs, manifest, sources) -> str:
    stats = {p: paper_stats(recs[p]) for p in papers}
    tot = collections.Counter()
    for x in stats.values():
        tot.update({k: v for k, v in x.items() if isinstance(v, int)})
    L = ['# 广东行测（2013—2021）转换与校验汇总', '',
         f'共 {len(papers)} 套、{tot["n"]} 题。每卷的完整记录（来源与 blob、完整性、答案读取方式、源文件问题、'
         '转写拿不准的地方、题图清单、复核方法）见各卷报告。本文件由 `python3 tools/extract.py index` 生成，请勿手改。', '',
         '| 试卷 | 题数 | 明确答案 | 争议答案 | 答案缺失 | 共用材料 | 题图 | 材料图 | 详细报告 |',
         '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |']
    for p in papers:
        x = stats[p]
        L.append(f'| {cfgs[p][0]["title"]} `{p}` | {x["n"]} | {x["known"]} | {x["disputed"]} | {x["missing"]} | '
                 f'{x["mats"]} | {x["figs"]} | {x["mimgs"]} | [quality/{p}.md](quality/{p}.md) |')
    L += [f'| 合计 | {tot["n"]} | {tot["known"]} | {tot["disputed"]} | {tot["missing"]} | {tot["mats"]} | '
          f'{tot["figs"]} | {tot["mimgs"]} | |', '']
    secs = [s_ for s_ in SECTION_NAMES if any(stats[p]['sec'][s_] for p in papers)]
    L += ['## 各部分题数', '', '| 试卷 | ' + ' | '.join(secs) + ' | 判断推理小类 |',
          '| --- | ' + ' | '.join('---:' for _ in secs) + ' | --- |']
    for p in papers:
        x = stats[p]
        sub = '，'.join(f'{k} {x["sub"][k]}' for k in SUBTYPES if x['sub'][k])
        L.append(f'| `{p}` | ' + ' | '.join(str(x['sec'][s_]) for s_ in secs) + f' | {sub} |')
    L += ['', '## 争议与缺失答案', '']
    flagged = [(r['id'], r['answer']) for p in papers for r in recs[p] if r['answer']['status'] != 'known']
    L += [f'- `{i}`：{a["status"]}，候选 ' + ('、'.join(''.join(v) for v in a['values']) or '无') + f'；{a["note"]}'
          for i, a in flagged] or ['无。']
    noted = [(r['id'], r['answer']['note']) for p in papers for r in recs[p]
             if r['answer']['status'] == 'known' and r['answer']['note']]
    if noted:
        L += ['', '答案明确、但来源或依据需要留意的题：', '']
        L += [f'- `{i}`：{n}' for i, n in noted]
    L += ['', '## 图片', '',
          f'{len(manifest)} 张，全部为原 PDF 页面按 288 DPI 渲染后的裁剪（`pdf_render_crop`），其中 '
          f'{sum(1 for e in manifest if e["transcription"])} 张附文字转写。裁剪框（pt）、像素尺寸与 SHA-256 见 '
          '[assets-manifest.json](assets-manifest.json)。', '',
          '## 校验', '',
          '`python3 tools/extract.py verify` 校验全部卷：schema、题号、答案语义、材料一致性、图片 SHA-256 与像素尺寸、'
          'Markdown 链接、源 PDF blob，并检查本汇总及 all.jsonl、assets-manifest.json、sources.json、README.md 与各卷文件一致。'
          '源文件提取所基于的提交：' + (f'`{sources["commit"]}`' if sources['commit'] else '见 sources.json（各卷不同）') + '。', '']
    return '\n'.join(L)


def render_readme(papers, recs, cfgs, manifest, sources) -> str:
    stats = {p: paper_stats(recs[p]) for p in papers}
    n = sum(x['n'] for x in stats.values())
    ntr = sum(1 for e in manifest if e['transcription'])
    L = ['# 广东行测整卷结构化题库（2013—2021）', '',
         f'{len(papers)} 套试卷，共 {n} 题。按卷保留原题号，收录题干、选项、答案，不收录解析。字段与 '
         '[2022—2026 题库](../2022-2026/README.md) 相同，`year` 为 2013—2021。', '',
         '| 试卷 | 题数 | 明确答案 | 争议答案 | 答案缺失 | 文件 |', '| --- | ---: | ---: | ---: | ---: | --- |']
    for p in papers:
        x = stats[p]
        L.append(f'| {cfgs[p][0]["title"]} | {x["n"]} | {x["known"]} | {x["disputed"]} | {x["missing"]} | '
                 f'[阅读]({p}.md) · [JSONL]({p}.jsonl) · [质量报告](quality/{p}.md) |')
    L += ['', '## 给 AI 的入口', '',
          '- [all.jsonl](all.jsonl)：每行一道题，UTF-8；可直接逐行解析、分块或建立检索索引。',
          '- 每卷的 Markdown：供阅读，保留图片与图表文字数据。',
          '- [schema.json](schema.json)：字段类型；[assets-manifest.json](assets-manifest.json)：图片来源页、裁剪坐标（pt）、'
          '像素尺寸与 SHA-256；[sources.json](sources.json)：原 PDF 路径及 Git blob SHA。',
          '- [质量报告](quality-report.md)：各卷汇总；每卷的详细记录在 `quality/`。', '',
          'JSONL 每条题目都包含完整 `material`（如果有），包括材料文字、图表数据文字和图片路径。每题的 `figures` 包含题图；'
          '`options[].image_refs` 指向图形选项。读取图形题时，需要把图片一并交给支持图像的模型。所有 `path` 相对于本目录，'
          '不能只传 JSONL 而丢弃 `assets/`。', '',
          '`answer.values` 表示候选答案集合：单选 `[ ["A"] ]`，多选 `[ ["A","B"] ]`，判断题 `[ ["正确"] ]`；争议答案例如 '
          '`[ ["D"], ["B"] ]`，表示 D 或 B 两个候选，**不是多选 DB**。`status` 分别为 `known`、`disputed`、`missing`。'
          '缺失时 `values=[]`。', '',
          '判断推理题在 `notes` 中注明小类（`subtype:图形推理`、`subtype:定义判断`、`subtype:类比推理`、`subtype:逻辑判断`），'
          '组卷时可按小类筛选。原卷未单列科学推理部分的，按题型记为“科学推理”，并在 `notes` 中注明原卷位置。']
    extra = [(p, x) for p in papers for x in cfgs[p][1].get('report', {}).get('readme', [])]
    if extra:
        L += ['', '需要留意：', '']
        L += [f'- {cfgs[p][0]["title"]}：{x}' for p, x in extra]
    L += ['', '## 图文处理', '',
          f'正文、选项、数字、分数及上下标转为文字；行内的分数、根号、公式小图转写为文字，不另存图片。{len(manifest)} 个题图/材料图'
          f'文件均为原 PDF 页面按 288 DPI 渲染后的裁剪，只裁图形本身，无重绘；{ntr} 个图表另有经过对照的文字转写，便于纯文本检索。'
          '多空选项的两词之间保留一个空格（原卷以空白分隔）。源文件的措辞、数据和答案按原卷保留，明显的印刷问题在题目 `notes` 中说明。'
          '页码为 PDF 的 1 起算物理页码。', '',
          '## 整理与校验', '',
          '整理工具在 `tools/`：每卷的登记信息在 `tools/papers/<卷>.json`，人工修正在 `tools/corrections/<卷>.json`'
          '（各键的说明见 `python3 tools/extract.py --help`）。', '',
          '```bash',
          'python3 tools/extract.py dump <卷>          # 自动分题结果，供核对、编写修正',
          'python3 tools/extract.py answer-sheet <卷>  # 扫描版答案：裁出答案候选行拼图，人工读取',
          'python3 tools/extract.py build <卷>         # 只生成本卷文件，并校验本卷',
          'python3 tools/extract.py index              # 合并生成根目录汇总',
          'python3 tools/extract.py verify             # 校验全部卷与汇总',
          '```', '',
          '`build` 只写本卷的 `<卷>.jsonl`、`<卷>.md`、`assets/<卷>/`（含 `manifest.json`）、`quality/<卷>.md`、'
          '`sources/<卷>.json`，多人可以同时整理不同的卷；根目录的 `all.jsonl`、`assets-manifest.json`、`sources.json`、'
          '`quality-report.md` 与本文件只由 `index` 生成，合并后有冲突时重跑 `index` 即可。', '',
          '## 来源与可追溯性', '',
          '原始 PDF 位于仓库的 `真题/` 与 `答案解析/`，未修改。' +
          (f'提取基于提交 `{sources["commit"]}`；' if sources['commit'] else '各卷提取所基于的提交见 sources.json；') +
          f'{len(sources["sources"])} 个源文件的 blob SHA 见 [sources.json](sources.json)，build 时均已与本地 PDF 核对一致。', '']
    return '\n'.join(L)


def cmd_index() -> None:
    outs = index_outputs()
    for name, content in outs.items():
        (OUT / name).write_text(content, encoding='utf-8')
    papers = list_papers(built_only=True)
    print(f'已合并 {len(papers)} 卷（{"、".join(papers)}）→ {"、".join(outs)}')


# ---------------------------------------------------------------------------
# verify
# ---------------------------------------------------------------------------
def check(cond, msg: str) -> None:
    if not cond:
        die(f'校验失败：{msg}')


def verify_paper(paper: str, validator) -> dict:
    cfg, _ = load_cfg(paper)
    f = paper_files(paper)
    for k in ('jsonl', 'md', 'manifest', 'quality', 'sources'):
        check(f[k].exists(), f'{paper} 缺少 {f[k].relative_to(OUT)}')
    rs = read_jsonl(f['jsonl'])
    md = f['md'].read_text(encoding='utf-8')
    manifest = {e['id']: e for e in json.loads(f['manifest'].read_text(encoding='utf-8'))}
    nums = [k for k in range(1, cfg['expected_questions'] + 1) if k not in set(cfg.get('missing_questions', []))]
    check([r['question_number'] for r in rs] == nums, f'{paper} 题号与 tools/papers/{paper}.json 不符')
    check(len(re.findall(r'^### 第 \d+ 题$', md, re.M)) == len(nums), f'{paper} Markdown 题数不符')
    mats, used = {}, set()
    for r in rs:
        rid = r['id']
        if validator:
            errs = sorted(validator.iter_errors(r), key=lambda e: list(e.path))
            check(not errs, f'{rid}: {errs[0].message if errs else ""}')
        check(rid == f'{paper}-Q{r["question_number"]:03d}' and r['paper_id'] == paper and r['year'] == cfg['year'],
              f'{rid} 编号或年份不符')
        dumped = json.dumps(r, ensure_ascii=False)
        check(r['stem'] and '⟦' not in dumped and chr(0xFFFD) not in dumped, f'{rid} 题干为空或含未转写的占位')
        for para in r['stem'].split('\n'):
            check(para in md, f'{rid} 题干未出现在 Markdown')
        a = r['answer']
        check(len(a['values']) == {'known': 1, 'disputed': 2, 'missing': 0}[a['status']]
              or (a['status'] == 'disputed' and len(a['values']) > 1), f'{rid} 答案状态与候选数不符')
        check([o['label'] for o in r['options']] == list('ABCD'), f'{rid} 选项不是A—D')
        for o in r['options']:
            check(o['text'] or o['image_refs'], f'{rid} {o["label"]} 项为空')
            for ref in o['image_refs']:
                check(ref['image_id'] in {x['image_id'] for x in r['figures']}, f'{rid} 选项图不在题图中')
        for v in a['values']:
            check((len(v) > 1) == (r['question_type'] == 'multiple_choice'), f'{rid} 题型与答案不符')
        if r['section'] == '判断推理':
            check(sum(x.startswith('subtype:') for x in r['notes']) == 1, f'{rid} 缺判断推理小类')
        imgs = list(r['figures'])
        if r['section'] == '资料分析':
            check(r['material'] and r['question_number'] in r['material']['question_numbers'], f'{rid} 缺共用材料')
        if r['material']:
            mid = r['material']['id']
            check(mats.setdefault(mid, r['material']) == r['material'], f'{mid} 各题内嵌内容不一致')
            imgs += [b for b in r['material']['content'] if b['type'] == 'image']
        for im in imgs:
            check(im['image_id'] in manifest, f'{rid} 引用的 {im["image_id"]} 不在本卷 manifest')
            e = manifest[im['image_id']]
            check(im['path'] == e['path'] and im['transcription'] == e['transcription'] and im['path'] in md,
                  f'{im["image_id"]} 与 manifest 或 Markdown 不符')
            used.add(im['image_id'])
    for target in re.findall(r'\]\(([^)]+)\)', md):
        if not target.startswith(('http', '#')):
            check((OUT / urllib.parse.unquote(target)).exists(), f'{paper}.md 链接失效：{target}')
    for aid, e in manifest.items():
        check(e['paper_id'] == paper and aid.startswith(paper + '-'), f'{aid} 不属于 {paper}')
        raw = (OUT / e['path']).read_bytes()
        check(raw[:8] == b'\x89PNG\r\n\x1a\n' and hashlib.sha256(raw).hexdigest() == e['sha256'], f'{aid} SHA-256 不符')
        check(png_size(raw) == (e['width'], e['height']), f'{aid} 像素尺寸不符')
        bb = e['source_bbox_points']
        check(abs((bb[2] - bb[0]) * SCALE - e['width']) <= 1 and abs((bb[3] - bb[1]) * SCALE - e['height']) <= 1,
              f'{aid} 像素与裁剪框不符')
        check(aid in used, f'{aid} 未被任何题目引用')
    on_disk = {str(x.relative_to(OUT)) for x in f['assets'].glob('*.png')}
    check(on_disk == {e['path'] for e in manifest.values()}, f'assets/{paper}/ 与 manifest 不一致')
    src = json.loads(f['sources'].read_text(encoding='utf-8'))
    check(src['paper_id'] == paper, f'sources/{paper}.json 卷号不符')
    for e in src['sources']:
        check(git('hash-object', '--', e['path']) == e['sha'], f'{e["path"]} 与记录的 blob 不一致')
    return dict(questions=len(rs), materials=len(mats), images=len(manifest),
                answers=dict(collections.Counter(r['answer']['status'] for r in rs)))


def cmd_verify(papers: list) -> None:
    full = not papers
    try:
        import jsonschema
        validator = jsonschema.Draft202012Validator(json.loads((OUT / 'schema.json').read_text(encoding='utf-8')))
    except ImportError:
        validator = None
        print('提示：未安装 jsonschema，跳过 schema 校验')
    papers = papers or list_papers(built_only=True)
    result = {'status': 'PASS', 'papers': {p: verify_paper(p, validator) for p in papers}}
    if full:
        stale = [name for name, content in index_outputs().items()
                 if not (OUT / name).exists() or (OUT / name).read_text(encoding='utf-8') != content]
        check(not stale, f'根目录汇总未更新：{stale}；请运行 python3 tools/extract.py index')
        result['index'] = '最新'
        pending = [p for p in list_papers() if p not in papers]
        if pending:
            result['已登记未生成'] = pending
    print(json.dumps(result, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    d = sub.add_parser('dump', help='自动分题结果')
    d.add_argument('paper')
    d.add_argument('--apply', '--with-inline', dest='apply', action='store_true',
                   help='套用修正文件（行内小图文字、figure_questions、option_splits、option_figures）')
    s = sub.add_parser('answer-sheet', help='扫描版答案候选行拼图')
    s.add_argument('paper')
    s.add_argument('--work', type=Path, default=None)
    b = sub.add_parser('build', help='生成本卷文件并校验本卷')
    b.add_argument('paper')
    b.add_argument('--work', type=Path, default=None, help='页面渲染缓存目录（默认临时目录，用完删除）')
    sub.add_parser('index', help='合并生成根目录汇总')
    v = sub.add_parser('verify', help='校验指定卷；不带参数时校验全部卷与汇总')
    v.add_argument('papers', nargs='*')
    a = ap.parse_args()
    if a.cmd == 'dump':
        cmd_dump(a.paper, raw=not a.apply)
    elif a.cmd == 'answer-sheet':
        cmd_answer_sheet(a.paper, a.work or Path(tempfile.mkdtemp(prefix=f'{a.paper}-answers-')))
    elif a.cmd == 'build':
        build(a.paper, a.work)
        cmd_verify([a.paper])
        print('本卷已生成并校验；汇总根目录文件请运行：python3 tools/extract.py index')
    elif a.cmd == 'index':
        cmd_index()
    elif a.cmd == 'verify':
        cmd_verify(a.papers)


if __name__ == '__main__':
    main()

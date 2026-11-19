#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""广东事业单位统考《基本能力测试》（2022—2026）整卷结构化工具。

由 广东/行测/2013-2021/tools/extract.py 复制后修改；输出格式与广东省考题库（行测 2013-2021、2022-2026）一致
（字段见 ../schema.json），组卷工具可以同样读取。与省考版相比的改动：exam/subject 改为事业单位与基本能力测试，
year 为 2022—2026；部分标题文字层中的康熙部首字（如“⼀”“⽤”）按 NFKC 归一后再识别；题型可按原卷标注
（判断题、多选题）登记，判断题无选项、答案为“正确/错误”；答案可登记来自同一份答案的第二个候选（争议）；
answer-sheet 的模板、渲染分辨率可按卷配置；新增 Word（.docx）题源：直接读 word/document.xml 分题，
题图按原样从 word/media/ 复制（method=docx_original，登记像素尺寸、来源文件与文档中的显示尺寸）。

自动完成：文字分题、选项拆分、行内小图（分数、根号、公式）占位、题图/材料图定位与 288 DPI 裁剪、答案文字层提取、
扫描版答案页的候选行拼图、文字守恒与裁图检查。人工判断写在每卷自己的修正文件里，build 读取后套用。

命令
  dump <卷> [--with-inline]    自动分题结果（PDF 默认不套用修正；Word 套用 ignore_lines 并列出图片登记），供核对、编写修正文件
  answer-sheet <卷> [--work D] 扫描版答案 PDF：裁出答案结论行（如“正确答案”“故正确答案为X”）拼成图，供人工逐题读取
  build <卷> [--work D]        套用修正，只生成本卷文件（见下），并校验本卷
  index                        扫描全部已生成的卷，合并生成根目录汇总文件
  verify [<卷> ...]            校验指定卷；不带参数时校验全部卷，并检查根目录汇总是否最新

每卷的文件（多人可同时整理不同的卷，互不覆盖）
  输入  tools/papers/<卷>.json       登记：year、title、paper_variant、source_edition、question_pdf、answer_pdf、
                                    expected_questions；可选 missing_questions（原卷缺题的题号）、
                                    source_commit（记作来源的提交；默认沿用 sources/<卷>.json 已记录的提交，
                                    源 PDF 变了才改用 HEAD）、answer_sheet（扫描版答案的读取参数：dpi、
                                    templates、match、x_from、x_to、numbers、rows、zoom，默认值见 ANS_DEFAULT）；
                                    Word 题源写 question_docx（题目与答案
                                    在同一文档时不写 answer_pdf，记录中的 question_pdf/answer_pdf 都填该文档路径）；
                                    可选 question_number_pattern（题号行的正则，第1组为题号；默认“N.”“N、”，
                                    题号单独成行的卷如 2022、2023 年写 "^(\\d{1,3})(?=（多选）$|$)"）、
                                    reference_files（[{path, use}] 参与核对但不作题源的文件，如另一版本的题本，
                                    记入 sources 与质量报告）、answer_pdf_kind（"vector"：答案 PDF 是打印成曲线的
                                    矢量字形页面而非扫描图片，只影响报告措辞）
        tools/corrections/<卷>.json  人工修正（键见下）
  输出  <卷>.jsonl  <卷>.md  assets/<卷>/*.png  assets/<卷>/manifest.json  quality/<卷>.md  sources/<卷>.json
根目录汇总只由 index 生成（合并分支后有冲突时重跑 index 即可）：
  all.jsonl  assets-manifest.json  sources.json  quality-report.md  README.md

修正文件的键（都可省略）
  section_map      原卷部分名 → schema 部分名，如 {"常识应用": "常识判断"}
  section_ranges   [{from, to, section, note}] 按题号改部分（如原卷未单列的科学推理）
  material_groups  [[86, 90], ...] 资料分析各组材料的首末题号，用于核对自动分段
  inline_images    {"p04-i01": "1/3"} 行内小图的文字；缺哪个 build 会列出
  text_fixes       [{q, field: "stem" | "option:A", find, replace | set, reason}]；find 须恰好出现一次
  material_text_fixes {"2": [{find, replace, reason}]} 材料正文的修正（如按原卷分段补换行）；find 须恰好出现一次
  ignore_lines     ["69——75题暂缺"] 选项之后无法归属、又不属于试题内容的行（按开头匹配）；Word 题源中用于去掉
                   题干、材料里的页眉页脚残留（推广文字、题库编号等），报告只记匹配的开头
  figures          {"p06-i02": {bbox: [x0, top, x1, bottom]（pt）, reason, role, alt, transcription}}
  subtypes         {"52": "图形推理"} 判断推理小类覆盖。自动分类：有题图→图形推理；题干与各选项均为
                   A∶B 式→类比推理；含“是指/定义”→定义判断；其余→逻辑判断
  question_notes   {"47": ["…"]}；materials {"2": {"question_notes": ["…"]}} 写入该组每题 notes
  question_types   [{from, to, type}] 原卷标注的题型（true_false / multiple_choice / single_choice）；
                   不写时按答案判定（一个字母单选、多个字母多选、正确/错误判断）。登记后与答案、题干中的
                   “（判断题）”“{多选题}”等标注逐题核对，不一致即报错
  answers          {"source": "…", "by_page": {"1": "1B 2D 3B 4正确"}} 人工读取的答案（答案PDF页码: 题号答案…）；
                   alternatives {"17": "72D"} 同一份答案里另给的候选（如解析末尾“倾向于D”），与 by_page 合成争议
  answer_notes     {"91": "…"} 答案说明
  missing_figures  {"66": "…"} 原文档缺题图（选项画在图中，因而也缺选项）的题：options 记为空并说明
  missing_materials {"91": "…"} 原文档缺资料的资料分析题：material 记为 null 并说明
  docx_images      {"image4": {q, role, alt, transcription}} Word 题源：word/media 中每张非装饰图片归属的题与角色
                   （浮动图片在文档流中的位置不可靠，须逐张登记）；material 图写 {material: 2, ...}
  report           {answers, source_issues, uncertain, review: [...]} 写入本卷质量报告；readme: [...] 写入 README；
                   sections: [{title, intro, items}] 另起的报告小节（排在“源文件问题与处理”之后）
  transcription    原卷没有文字层（如打印成曲线的矢量字形 PDF）时，题目文字按人工转写收录（题图仍从 question_pdf
                   裁剪）：{sections: [{from, to, name}], questions: {"1": {pages, stem, options: [A,B,C,D 文字],
                   figures: ["p07-i01"], inline: ["p05-i01"]}}, materials: {"1": {questions: [首, 末], pages, header,
                   content: ["段落", {image: "p13-i01"}]}}}；question_pdf 中每张图片须归属某题、某组材料，或作为
                   行内小图写在 inline_images；选项只有字母（“A、A B、B…”）且有题图的按图形选项处理；不做文字守恒检查

整理新的一卷
  1. 写 tools/papers/<卷>.json；2. dump 核对分题、材料与图片归属；3. answer-sheet 读答案，写入 answers.by_page；
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
import unicodedata
import urllib.parse
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
OUT = TOOLS.parent                      # 广东/事业单位/结构化
REPO = TOOLS.parents[3]                 # 仓库根目录
PROVINCE = '广东'
EXAM = '事业单位公开招聘考试'
SUBJECT = '基本能力测试'
BANK = '广东事业单位统考《基本能力测试》'
YEARS = '2022—2026'
QTYPES = ('true_false', 'single_choice', 'multiple_choice')
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
                   '言语表达与理解': '言语理解与表达', '数学运算': '数量关系', '数字推理': '数量关系'}
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
RE_OPT = re.compile(r'^([A-D])\s*[、.．:：]')
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

    @property
    def ttop(self):
        """文字的上沿（不计并入的行内小图），用于排阅读顺序：竖排分数比文字高，不应把所在行排到上一行之前。"""
        tops = [t.top for t in self.toks if not t.image]
        return min(tops) if tops else self.top


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
    # 行内小图：高度不大、与某一文字行竖直重叠且左右紧邻文字。竖排分数常与上下两行等量重叠（如题号“54.”行与
    # 其下的逗号行），此时取左右间距最小（紧挨着文字）的那一行，间距相同再比重叠量
    for im in page.images:
        if im.h > INLINE_MAX_H:
            continue
        cands = []
        for ln in lines:
            ov = min(im.bottom, ln.bottom) - max(im.top, ln.top)
            gap = min(min(abs(t.x1 - im.x0), abs(im.x1 - t.x0)) for t in ln.toks)
            if gap < 60 and ov > 0 and ov >= 0.3 * min(im.h, ln.bottom - ln.top):
                cands.append((round(gap, 1), -ov, ln.top, ln))
        if cands:
            best = min(cands, key=lambda c: c[:3])[3]
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
    page.lines = sorted(keep, key=lambda l: (l.ttop, l.x0))


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


def match_section(text: str):
    """返回原卷部分名（如“常识应用”）；不是部分标题则返回 None。
    先按 NFKC 归一：部分标题的文字层里常有康熙部首字（“⼀.常识应⽤”中的 U+2F00、U+2F64），印出字形与常用字相同。"""
    t = unicodedata.normalize('NFKC', text).replace(' ', '')
    for rx in RE_SECTION:
        m = rx.match(t)
        if m:
            name = m.group('name')
            for cand in SECTION_NAMES + sorted(SECTION_ALIASES, key=len, reverse=True):
                if name.startswith(cand):
                    return cand
    return None


def match_material(text: str) -> bool:
    t = text.replace(' ', '')
    return any(rx.match(t) for rx in RE_MATERIAL)


def segment(pages: list[Page], expected: int, inline_text: dict, missing=(), qnum=RE_QNUM):
    """按阅读顺序把行与题图分到部分、材料、题目。材料有两种写法：带“材料1/（材料一）/根据以下资料”等标题；
    或（2013、2015、2017、2019等年）无标题，资料分析部分里上一组题的A—D选项之后直接接首行缩进的材料段落或图表。
    qnum：题号行的正则（第1组为题号），默认 RE_QNUM；题号单独成行的卷在 tools/papers/<卷>.json 的
    question_number_pattern 中另行登记。"""
    for p in pages:
        for ln in p.lines:
            render_line(ln, inline_text)
    stream = []
    for p in pages:
        stream += [('line', ln, ln.ttop, ln.x0) for ln in p.lines]
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
        sec = match_section(ln.text) if len(ln.text) < 160 else None
        if sec:
            section, cur_q, cur_m, collecting = sec, None, None, False
            headings.append(ln)
            heading_open = ln.x1 >= right - 1.5 * ln.em
            continue
        if heading_open and not indented and not qnum.match(ln.text) and not match_material(ln.text):
            headings.append(ln)                       # 部分说明的续行
            heading_open = ln.x1 >= right - 1.5 * ln.em
            continue
        heading_open = False
        m = qnum.match(ln.text)
        while nxt in missing:
            nxt += 1                                  # tools/papers/<卷>.json 声明的原卷缺题题号
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
    """左右边界。左边界取正文列：行首位置的众数覆盖三成以上的行时用众数（事业单位卷的两位题号悬挂在正文列左侧，
    用 5% 分位数会把题号列当成左边界，使所有正文行都像“缩进”），否则沿用 5% 分位数。"""
    xs0 = sorted(ln.x0 for p in pages for ln in p.lines)
    xs1 = sorted(ln.x1 for p in pages for ln in p.lines)
    if not xs0:
        return 0.0, 0.0
    left = xs0[len(xs0) // 20]
    mode, cnt = collections.Counter(round(x) for x in xs0).most_common(1)[0]
    if cnt >= 0.3 * len(xs0):
        left = min(x for x in xs0 if round(x) == mode)
    return left, xs1[int(len(xs1) * 0.95)]


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


def parse_question(q: QBlock, left: float, right: float, autofix: list, qnum=RE_QNUM) -> dict:
    first = q.lines[0]
    m = qnum.match(first.text)
    opt_i = next((i for i, ln in enumerate(q.lines) if i > 0 and RE_OPT.match(ln.text)), None)
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
        for text, _, _ in segs:
            mo = RE_OPT.match(text)
            if mo and want < 4 and mo.group(1) == 'ABCD'[want]:
                options.append({'label': mo.group(1), 'text': text[mo.end():].strip()})
                labels_raw.append(mo.group(0))
                want += 1
            elif options:
                sep = ' ' if options[-1]['text'] else ''
                options[-1]['text'] += sep + text
            else:
                stem += text
    if 0 < len(options) < 4:
        # 选项之间没有留白（如“A、……好坏B、不健康……”）：按下一个应出现的选项字母补拆；
        # 字母前须是汉字、数字或右括号/引号/百分号，拆后必须恰好得到 A—D 四项，否则不动、交人工核对
        whole = ''.join(f'\u0000{o["label"]}\u0001{o["text"]}' for o in options)
        cut, pos = [], 0
        for L in 'ABCD'[len(options):]:
            mo = re.compile(rf'(?<=[\u4e00-\u9fff\d）)”%])({L})[、.．](?=[^、.．\s])').search(whole, pos)
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


def normalize_blanks(text: str, section: str | None) -> str:
    text = re.sub(r'[（(]\s*[）)]', '（）', text)
    if section == '数量关系':
        core = text.replace('（）', '')
        if core and re.fullmatch(r'[\d\s，,.．/√、\-－+]+。?', core):     # 事业单位卷数列末尾带句号
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
    return found, stats


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
def qnum_re(cfg: dict):
    """题号行的正则：tools/papers/<卷>.json 的 question_number_pattern（第1组为题号），默认 RE_QNUM。"""
    return re.compile(cfg['question_number_pattern']) if cfg.get('question_number_pattern') else RE_QNUM


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
def cmd_dump_docx(paper: str, cfg: dict, corr: dict):
    units = docx_units(REPO / cfg['question_docx'])
    seg = segment_docx(units, cfg, corr)
    print(f'# {paper}  Word 单元 {len(units)} 个（行与图片）')
    for t, after in seg['headings']:
        print(f'[部分标题 第{after}题之后] {t}')
    for im in seg['decor']:
        print(f'[装饰细线图片] {im.media} {im.cx}x{im.cy} EMU @{im.loc}')
    for im, near in seg['imgs']:
        print(f'[图片] {im.media} 显示 {im.cx / EMU_PER_PT:.1f}x{im.cy / EMU_PER_PT:.1f}pt {"浮动" if im.anchor else "嵌入"} @{im.loc} 附近第{near}题'
              f' → 登记：{corr.get("docx_images", {}).get(Path(im.media).stem, "（未登记）")}')
    for who, t, why in seg['ignored']:
        print(f'[不收录] {who}：{t}（{why}）')
    mats = {m['k']: m for m in seg['materials']}
    for q in seg['questions']:
        if q['material'] and mats[q['material']]['questions'][0] == q['number']:
            m = mats[q['material']]
            print(f'\n=== 材料{m["k"]}（第{m["questions"][0]}—{m["questions"][-1]}题）标题：{m["header"]}')
            print('  [文] ' + join_docx(m['lines']))
        r = parse_docx_question(q)
        a = q['answer']
        print(f'\n--- 第{q["number"]}题 [{q["section_raw"]}] 标注{{{q["tag"]}}} @{q["locs"][0]}  答案：{a["value"] if a else "（无）"}'
              f'  解析结论：{answer_conclusion(q["analysis"])}')
        print(r['stem'])
        for o in r['options']:
            print(f'  {o["label"]}. {o["text"]}')
        if r['partial_options']:
            print(f'  [只拆出 {r["partial_options"]} 个选项]')
    print(f'\n共识别 {len(seg["questions"])} 题（应为 {cfg["expected_questions"]}），材料 {len(seg["materials"])} 组')


def cmd_dump_transcribed(paper: str, cfg: dict, corr: dict):
    pages = load_pages(REPO / cfg['question_pdf'])
    tr = corr['transcription']
    print(f'# {paper}  页数 {len(pages)}  原卷没有文字层，题目文字取自 tools/corrections/{paper}.json 的 transcription')
    for p in pages:
        for im in p.images:
            print(f'[图片 {im.key}] bbox=({im.x0:.1f},{im.top:.1f},{im.x1:.1f},{im.bottom:.1f})'
                  + (f' 行内：{corr["inline_images"][im.key]}' if im.key in corr.get('inline_images', {}) else ''))
    mats = {int(k): m for k, m in tr.get('materials', {}).items()}
    for n in sorted(int(k) for k in tr.get('questions', {})):
        for k, m in mats.items():
            if m['questions'][0] == n:
                print(f'\n=== 材料{k}（第{m["questions"][0]}—{m["questions"][1]}题，p{m.get("pages")}）{m.get("header", "")}')
                for b in m['content']:
                    print('  [图]', b['image']) if isinstance(b, dict) else print('  [文]', b)
        q = tr['questions'][str(n)]
        print(f'\n--- 第{n}题 p{q.get("pages")} 图{q.get("figures", [])}')
        print(q['stem'])
        for L, t in zip('ABCD', q.get('options', [])):
            print(f'  {L}. {t}')
    print(f'\n共 {len(tr.get("questions", {}))} 题（应为 {cfg["expected_questions"]}），材料 {len(mats)} 组')


def cmd_dump(paper: str, raw: bool = True):
    cfg, corr = load_cfg(paper)
    if cfg.get('question_docx'):
        return cmd_dump_docx(paper, cfg, corr)
    if corr.get('transcription'):
        return cmd_dump_transcribed(paper, cfg, corr)
    pages = load_pages(REPO / cfg['question_pdf'])
    inline = {} if raw else corr.get('inline_images', {})
    qnum = qnum_re(cfg)
    seg = segment(pages, cfg['expected_questions'], inline, set(cfg.get('missing_questions', [])), qnum)
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
        r = parse_question(q, left, right, autofix, qnum)
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


# 扫描版答案的读取参数。默认值为省考旧卷：96 DPI 灰度渲染（与常见扫描件原始分辨率一致）；模板为加粗“正确答案”四字
# 的二值图（取自2020年乡镇卷答案第1页第1题），在行首 10—60 像素处滑动；归一化相关系数阈值 0.6（2020、2021两卷答案行
# 均≥0.65，其余各行≤0.47）。事业单位卷在 tools/papers/<卷>.json 的 answer_sheet 中另行设置（见各卷登记文件）。
ANS_DEFAULT = dict(dpi=96, templates=['answer-template.png'], match=0.6, x_from=10, x_to=60, numbers=False, rows=34, zoom=150)


def answer_sheet_cfg(cfg: dict) -> dict:
    return dict(ANS_DEFAULT, **cfg.get('answer_sheet', {}))


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


def match_answer_lines(dark, templates, ac):
    """在一页中找答案结论行：每个模板在行首 x_from—x_to 像素处横向滑动、上下错 1—2 像素，取最大相关系数。
    返回 [(top, bottom, 行首x, 相关系数, 模板序号)] 与全部文字行。"""
    import numpy as np
    from numpy.lib.stride_tricks import sliding_window_view as swv
    prepared = []
    for T in templates:
        Tz = T - T.mean()
        prepared.append((T.shape, Tz, math.sqrt(float((Tz ** 2).sum()))))
    hits, lines = [], ink_lines(dark)
    for a, b in lines:
        lx = int(np.where(dark[a:b].any(axis=0))[0].min())
        best, which = -1.0, None
        for ti, ((th, tw), Tz, Tn) in enumerate(prepared):
            if b - a < th - 2 or b - a > th + 6:
                continue
            for dy in range(-1, b - a - th + 2):
                top = a + dy
                band = dark[max(top, 0):top + th, max(lx + ac['x_from'], 0):lx + ac['x_to'] + tw]
                if top < 0 or band.shape[0] < th or band.shape[1] < tw:
                    continue
                W = swv(band, (th, tw))[0]
                Wz = W - W.mean(axis=(1, 2), keepdims=True)
                den = np.sqrt((Wz ** 2).sum(axis=(1, 2))) * Tn
                sc = np.where(den > 0, (Wz * Tz).sum(axis=(1, 2)) / np.where(den > 0, den, 1), -1)
                if float(sc.max()) > best:
                    best, which = float(sc.max()), ti
        if best >= ac['match']:
            hits.append((a, b, lx, best, which))
    return hits, lines


def contact_sheet(items, out: Path, width: int, scale: int, cols: int = 1, label_w: int = 120, rows_per: int = 34):
    """items: [(标签, 灰度PIL图)] → 拼成若干张图，返回文件列表。"""
    from PIL import Image, ImageDraw
    files, per = [], rows_per * cols
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


def hcat(*ims, gap: int = 12):
    from PIL import Image
    h = max(im.size[1] for im in ims)
    out = Image.new('L', (sum(im.size[0] for im in ims) + gap * (len(ims) - 1), h), 255)
    x = 0
    for im in ims:
        out.paste(im, (x, 0))
        x += im.size[0] + gap
    return out


def cmd_answer_sheet(paper: str, work: Path):
    """扫描版答案 PDF 的读取辅助（没有 OCR 时用）：
    answer-lines-*.png  每条检测到的答案结论行（整行；登记了 numbers 时左侧拼上其前最近的“N.”题号行），第一遍按此逐题读取；
    answer-zoom-*.png   同一批行的行首（到答案字母为止）放大、多列排开，第二遍按此独立重读；
    answer-check-*.png  省考旧卷：“解析/拓展”等短行的上一行（多为“因此，选择X选项”）；登记了 numbers 时改为每条结论行
                        之后紧跟的非题号行（解析末尾另加的说明，如“倾向于D选项”），用来再核一次。
    两遍结果一致后，按“页码: 题号答案 …”写入 tools/corrections/<卷>.json 的 answers.by_page。"""
    import numpy as np
    from PIL import Image
    cfg, _ = load_cfg(paper)
    ac = answer_sheet_cfg(cfg)
    s = ac['dpi'] / 96.0                     # 以 96 DPI 为基准的长度换算
    pdf = REPO / cfg['answer_pdf']
    work.mkdir(parents=True, exist_ok=True)
    for pat in ('ans-*.png', 'answer-lines-*.png', 'answer-zoom-*.png', 'answer-check-*.png', 'answer-gaps-*.png'):
        for old in work.glob(pat):          # 只清理本命令自己生成的文件
            old.unlink()
    subprocess.run(['pdftoppm', '-r', str(ac['dpi']), '-gray', '-png', str(pdf), str(work / 'ans')], check=True, capture_output=True)
    templates = [(np.asarray(Image.open(TOOLS / t).convert('L')) < 128).astype(float) for t in ac['templates']]
    full, zoom, check, per_tpl, spans = [], [], [], collections.Counter(), []
    indent = None
    last_num = None                          # 最近的题号行（可跨页）：(页, 图, top, bottom, x)
    W = int(520 * s)
    for f in sorted(work.glob('ans-*.png'), key=lambda x: int(re.findall(r'(\d+)\.png$', x.name)[0])):
        pno = int(re.findall(r'(\d+)\.png$', f.name)[0])
        g = Image.open(f).convert('L')
        dark = (np.asarray(g) < 140).astype(float)
        hits, lines = match_answer_lines(dark, templates, ac)
        hit_at = {a: h for h in hits for a in [h[0]]}
        info = [(a, b, *(lambda c: (int(c.min()), int(c.max())))(np.where(dark[a:b].any(axis=0))[0])) for a, b in lines]
        H = dark.shape[0]
        if hits:
            indent = statistics_median([h[2] for h in hits])   # 结论行的行首即段落缩进，题号行也从这里起
        is_num = [ac['numbers'] and indent is not None and abs(x0 - indent) <= 4 * s and a < 0.92 * H
                  and 6 * s <= b - a <= 10.5 * s and 5 * s <= x1 - x0 <= 45 * s
                  for a, b, x0, x1 in info]   # 数字比汉字矮；页脚页码不算
        for i, (a, b, x0, x1) in enumerate(info):
            if is_num[i]:
                last_num = (pno, g, a, b, x0)
                spans.append(dict(num=last_num, hits=0, tail=[]))
                continue
            if spans:
                spans[-1]['tail'] = (spans[-1]['tail'] + [(pno, g, a, b)])[-3:]
            if a not in hit_at:
                continue
            _, _, lx, sc, ti = hit_at[a]
            per_tpl[ac['templates'][ti]] += 1
            if spans:
                spans[-1]['hits'] += 1
            n = len(full) + 1
            line = g.crop((int(30 * s), a - 3, int(30 * s) + W, b + 3))
            if ac['numbers'] and last_num:
                lp, lg, na, nb, nx = last_num
                num = lg.crop((nx - 3, na - 3, nx + int(50 * s), nb + 3))
                full.append((f'#{n} p{pno} y{a}' + (f' (num p{lp})' if lp != pno else ''), hcat(num, line)))
            else:
                full.append((f'#{n} p{pno} y{a}', line))
            zoom.append((f'#{n} p{pno}', g.crop((lx - 2, a - 3, lx + int(ac['zoom'] * s), b + 3))))
            if ac['numbers'] and i + 1 < len(info) and not is_num[i + 1]:
                na_, nb_, _, _ = info[i + 1]
                if na_ - b < 40 * s:
                    check.append((f'after #{n} p{pno} y{na_}', g.crop((int(30 * s), na_ - 3, int(30 * s) + W, nb_ + 3))))
        if not ac['numbers']:
            for i, (a, b, x0, x1) in enumerate(info):
                if b - a >= 8 and x1 - x0 < 45 and i > 0:      # 两字短行（解析、拓展）
                    pa, pb, _, _ = info[i - 1]
                    check.append((f'p{pno} y{pa}', g.crop((30, pa - 3, 30 + 520, pb + 3))))
    gaps = []
    for k, sp in enumerate(spans):
        if sp['hits'] != 1:
            lp, lg, na, nb, nx = sp['num']
            num = lg.crop((nx - 3, na - 3, nx + int(50 * s), nb + 3))
            for tp, tg, ta, tb in (sp['tail'] if sp['hits'] == 0 else []):
                gaps.append((f'span{k + 1} p{tp} y{ta}', hcat(num, tg.crop((int(30 * s), ta - 3, int(30 * s) + W, tb + 3)))))
            if sp['hits'] > 1:
                gaps.append((f'span{k + 1} x{sp["hits"]} p{lp}', num))
    out = []
    zs = 2 if s > 1.5 else 3
    out += contact_sheet(full, work / 'answer-lines', max(im.size[0] for _, im in full) if full else W, 1, rows_per=ac['rows'], label_w=170)
    out += contact_sheet(zoom, work / 'answer-zoom', int((ac['zoom'] + 2) * s), zs, cols=2 if s > 1.5 else 4, label_w=70, rows_per=ac['rows'])
    if check:
        out += contact_sheet(check, work / 'answer-check', W, 1, rows_per=ac['rows'], label_w=170)
    if gaps:
        out += contact_sheet(gaps, work / 'answer-gaps', max(im.size[0] for _, im in gaps), 1, rows_per=ac['rows'], label_w=170)
    found, stats = answer_text_layer(pdf)
    scanned = [p for p, n in stats if n < 30]
    print(f'答案PDF共 {len(stats)} 页，其中 {len(scanned)} 页几乎没有文字层（扫描页）；按 {ac["dpi"]} DPI 渲染。')
    print(f'文字层可直接取到的答案：{ {k: v["value"] for k, v in sorted(found.items())} }')
    exp = cfg['expected_questions'] - len(cfg.get('missing_questions', []))
    print(f'检测到答案结论行 {len(full)} 条（本卷应有约 {exp} 条；各模板命中：{dict(per_tpl)}；多出或少了的请到对应页查看）。')
    if ac['numbers']:
        odd = [(k + 1, sp['hits']) for k, sp in enumerate(spans) if sp['hits'] != 1]
        print(f'题号行 {len(spans)} 条；结论行不是恰好 1 条的题号段（第几段, 条数）：{odd}（见 answer-gaps，段号≈题号；第1题的“1.”太窄可能不计入）')
    for fn in out:
        print('  ', fn)
    print(f'两遍读取一致后，按 “页码: 题号答案 …” 写入 tools/corrections/{paper}.json 的 answers.by_page。')


# ---------------------------------------------------------------------------
# Word（.docx）题源：直接读 word/document.xml，不经 PDF
# ---------------------------------------------------------------------------
W_NS = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
A_NS = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
R_NS = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
WP_NS = '{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}'
EMU_PER_PT = 12700
DECOR_MAX_EMU = 2 * EMU_PER_PT          # 显示高度不超过 2pt 的图片是分隔细线（PDF 转 Word 留下的页眉页脚线），不收录
RE_DQ = re.compile(r'^\s*(\d{1,3})\s*(?:([.．、])\s*)?(?:\{(判断题|多选题|单选题)\}\s*(?:[.．、]\s*)?)?')
RE_DSEC = re.compile(r'^\s*[一二三四五六七八九十]+\s*[、.．]\s*(判断题|多项选择题|单项选择题|多选题|单选题)')
RE_DMAT = re.compile(r'^\s*根据(?:以下|下列)(?:资料|材料)[，,]?\s*回答\s*(\d{1,3})\s*[-—–~～]\s*(\d{1,3})\s*题\s*[:：]?')
RE_DANS = re.compile(r'答案\s*[：:]')
DOCX_TAG_TYPE = {'判断题': 'true_false', '多选题': 'multiple_choice', '单选题': 'single_choice'}
PDF_TAG_TYPE = {'（判断题）': 'true_false', '（多选题）': 'multiple_choice', '（单选题）': 'single_choice',
                '（多选）': 'multiple_choice'}       # 2022、2023年卷题号后印“（多选）”
LABEL_PRE = r'[\s一-鿿\d）)”"%，。、；：？?！]'


@dataclass
class DocxImg:
    key: str            # image04（取自 word/media/image4.png，补零便于排序）
    media: str          # word/media/image4.png
    cx: int             # 文档中的显示宽、高（EMU）
    cy: int
    anchor: bool        # 浮动图片（wp:anchor）在文档流中的位置不代表版面位置
    loc: str
    page: int | None = None     # Word 没有页码


def docx_units(path: Path) -> list:
    """word/document.xml → 按文档顺序的单元：('line', 文字, 位置, 是否在表格中) 与 ('img', DocxImg, 位置, 是否在表格中)。
    段落内的换行（w:br）切成多行；表格逐行逐格展开；段落属性里的制表位（w:pPr/w:tabs）不算文字。"""
    z = zipfile.ZipFile(path)
    doc = ET.fromstring(z.read('word/document.xml'))
    rels = ET.fromstring(z.read('word/_rels/document.xml.rels'))
    rid = {r.get('Id'): r.get('Target') for r in rels}
    units = []

    def make_img(d, loc, in_table):
        blip = d.find('.//' + A_NS + 'blip')
        ext = d.find('.//' + WP_NS + 'extent')
        if blip is None or ext is None:
            return None
        target = 'word/' + rid[blip.get(R_NS + 'embed')]
        num = int(re.findall(r'(\d+)', Path(target).stem)[-1])
        return DocxImg(f'image{num:02d}', target, int(ext.get('cx')), int(ext.get('cy')),
                       d.find(WP_NS + 'anchor') is not None, loc)

    def para(p, loc, in_table):
        buf = []

        def flush():
            units.append(('line', ''.join(buf), loc, in_table))
            buf.clear()

        def walk(el):
            for c in el:
                tag = c.tag
                if tag in (W_NS + 'pPr', W_NS + 'rPr'):
                    continue
                if tag == W_NS + 't':
                    buf.append(c.text or '')
                elif tag == W_NS + 'tab':
                    buf.append('\t')
                elif tag in (W_NS + 'br', W_NS + 'cr'):
                    flush()
                elif tag == W_NS + 'drawing':
                    im = make_img(c, loc, in_table)
                    if im is not None:
                        if ''.join(buf).strip():
                            flush()
                        units.append(('img', im, loc, in_table))
                else:
                    walk(c)
        walk(p)
        flush()

    def table(t, loc):
        for ri, tr in enumerate(t.findall(W_NS + 'tr'), 1):
            for ci, tc in enumerate(tr.findall(W_NS + 'tc'), 1):
                for k, c in enumerate(tc, 1):
                    if c.tag == W_NS + 'p':
                        para(c, f'{loc}r{ri}c{ci}p{k}', True)
                    elif c.tag == W_NS + 'tbl':
                        table(c, f'{loc}r{ri}c{ci}t{k}')

    body = doc.find(W_NS + 'body')
    np_, nt = 0, 0
    for c in body:
        if c.tag == W_NS + 'p':
            np_ += 1
            para(c, f'P{np_}', False)
        elif c.tag == W_NS + 'tbl':
            nt += 1
            table(c, f'T{nt}')
    return units


def clean_docx(t: str) -> str:
    """Word 文字的空白：制表符、全角空格当空格；汉字与全角标点两侧的空格是排版留白，去掉；首尾空白去掉。"""
    t = t.replace('\t', ' ').replace('　', ' ').replace('\xa0', ' ')
    t = re.sub(r' +', ' ', t)
    cjk = r'[　-〿＀-￯一-鿿“”‘’（）《》—…]'
    t = re.sub(rf' (?={cjk})', '', t)
    t = re.sub(rf'(?<={cjk}) ', '', t)
    return t.strip()


def join_docx(lines: list) -> str:
    """把 Word 的若干段拼成题干：上一段以句末标点结束、或本段是设问句，另起一行；否则（PDF 转 Word 在页末断开的段）直接接上。"""
    out = ''
    for t in lines:
        t = clean_docx(t)
        if not t:
            continue
        if not out:
            out = t
        elif ends_terminal(out) or RE_PROMPT.match(t) or RE_MARKER.match(t):
            out += '\n' + t
        else:
            out += t
    return out


def segment_docx(units: list, cfg: dict, corr: dict) -> dict:
    ignore = corr.get('ignore_lines', [])
    expected, missing = cfg['expected_questions'], set(cfg.get('missing_questions', []))
    questions, materials, decor, ignored, headings, imgs = [], [], [], [], [], []
    st = dict(section=None, state='pre', cur=None, curm=None, nxt=1)

    def skip_reason(t, in_table):
        """不收录的行：返回 (记录用的文字, 原因)。按 ignore_lines 去掉的行只记匹配的开头，不转录推广文字、编号等。"""
        tt = t.replace(' ', '').replace('\t', '')
        for x in ignore:
            if tt.startswith(x):
                return f'以“{x}”开头的一行', '按 ignore_lines 不收录'
        if in_table and re.fullmatch(r'\d{1,3}', tt):
            return f'单独一格的数字“{tt}”', '是 PDF 转 Word 留下的页码，不收录'
        return None

    def handle(q, s):
        mA = RE_DANS.search(s)
        if mA:
            before, after = s[:mA.start()], s[mA.end():]
            if before.strip():
                q['lines'].append(before)
            mv = re.match(r'\s*([A-Da-d]{1,4}|正确|错误)', after)
            q['answer'] = dict(value=mv.group(1) if mv else None, raw=('答案：' + after).strip())
            st['state'] = 'analysis'
        elif re.match(r'\s*解析\s*[：:]', s):
            st['state'] = 'analysis'
        else:
            q['lines'].append(s)

    for kind_, obj, loc, in_table in units:
        if kind_ == 'img':
            if obj.cy <= DECOR_MAX_EMU:
                decor.append(obj)
            else:
                imgs.append((obj, st['cur']['number'] if st['cur'] else None))
            continue
        t = obj
        if not t.replace('\t', '').strip():
            continue
        ms = RE_DSEC.match(t)
        if ms:
            st['section'] = ms.group(1)
            st['state'] = 'between'
            headings.append((t.strip(), st['cur']['number'] if st['cur'] else 0))
            continue
        mm = RE_DMAT.match(t)
        if mm:
            st['curm'] = dict(k=len(materials) + 1, header=t.strip(), lines=[], questions=[],
                              range=(int(mm.group(1)), int(mm.group(2))), locs=[loc])
            materials.append(st['curm'])
            st['state'] = 'material'
            rest = t[mm.end():].strip()
            if rest:
                st['curm']['lines'].append(rest)
            continue
        while st['nxt'] in missing:
            st['nxt'] += 1
        m = RE_DQ.match(t)
        if m and (m.group(2) or m.group(3)) and int(m.group(1)) == st['nxt'] and st['nxt'] <= expected:
            n = st['nxt']
            q = dict(number=n, section_raw=st['section'], tag=m.group(3), prefix=m.group(0).strip(), lines=[],
                     analysis=[], answer=None, material=None, locs=[loc], figures=[])
            cm = st['curm']
            if cm is not None and cm['range'][0] <= n <= cm['range'][1]:
                q['material'] = cm['k']
                cm['questions'].append(n)
            questions.append(q)
            st['cur'], st['state'] = q, 'stem'
            st['nxt'] += 1
            handle(q, t[m.end():])
            continue
        if st['state'] == 'stem':
            why = skip_reason(t, in_table)
            if why:
                ignored.append((f'第{st["cur"]["number"]}题', *why))
                continue
            st['cur']['locs'].append(loc)
            handle(st['cur'], t)
        elif st['state'] == 'material':
            why = skip_reason(t, in_table)
            if why:
                ignored.append((f'材料{st["curm"]["k"]}', *why))
                continue
            st['curm']['lines'].append(t)
            st['curm']['locs'].append(loc)
        elif st['state'] == 'analysis' and st['cur'] is not None:
            st['cur']['analysis'].append(t)
    return dict(questions=questions, materials=materials, decor=decor, ignored=ignored, headings=headings, imgs=imgs)


def parse_docx_question(q: dict) -> dict:
    lines = [x for x in (clean_docx(s) for s in q['lines']) if x]
    text = '\n'.join(lines)
    cuts, pos = [], 0
    for L in 'ABCD':
        mo = re.compile(rf'(?:^|(?<={LABEL_PRE})){L}\s*[.．、]', re.M).search(text, pos)
        if not mo:
            break
        cuts.append(mo)
        pos = mo.end()
    if len(cuts) == 4:
        stem_part = text[:cuts[0].start()]
        options = []
        for i, mo in enumerate(cuts):
            end = cuts[i + 1].start() if i < 3 else len(text)
            options.append({'label': 'ABCD'[i], 'text': ''.join(clean_docx(x) for x in text[mo.end():end].split('\n'))})
        labels_raw = [mo.group(0) for mo in cuts]
    else:
        stem_part, options, labels_raw = text, [], []
    return dict(number=q['number'], section_raw=q['section_raw'], stem=join_docx(stem_part.split('\n')), options=options,
                figures=list(q['figures']), pages=[], material=q['material'], labels_raw=labels_raw, strays=[],
                prefix='', raw=''.join(q['lines']), inline=[], tag=q['tag'], partial_options=len(cuts) if 0 < len(cuts) < 4 else 0,
                locs=q['locs'])


def answer_conclusion(analysis: list):
    """从解析文字中找结论里的答案字母（“故答案为C”“故本题答案选择BD”“选C”“只有A”等），取最后一处；找不到返回 None。"""
    txt = ''.join(analysis)
    pats = [r'答案(?:为|是|选择|选)\s*[:：]?\s*([A-Da-d]{1,4})(?![A-Za-z])', r'本题选(?:择)?\s*([A-D]{1,4})(?![A-Za-z])',
            r'(?:因此|故|所以)[，,]?\s*(?:本题)?选(?:择)?\s*([A-D]{1,4})(?![A-Za-z])', r'(?<![A-Za-z])选\s*([A-D]{1,4})[。.]',
            r'对应选项\s*([A-D])', r'只有\s*([A-D])(?:项)?(?:符合)?[。，,]', r'([A-D])项符合']
    found = []
    for p in pats:
        for mo in re.finditer(p, txt):
            found.append((mo.start(), mo.group(1).upper()))
    return max(found)[1] if found else None


def load_docx_source(cfg: dict, corr: dict, paper: str, autofix: list) -> dict:
    path = REPO / cfg['question_docx']
    units = docx_units(path)
    seg = segment_docx(units, cfg, corr)
    missing_q = set(cfg.get('missing_questions', []))
    if len(seg['questions']) != cfg['expected_questions'] - len(missing_q):
        die(f'Word 文档只识别出 {len(seg["questions"])} 题（应为 {cfg["expected_questions"] - len(missing_q)}）；先用 dump 检查分题')
    qby = {q['number']: q for q in seg['questions']}
    # 图片归属：浮动图片在文档流中的位置不可靠，须在修正文件 docx_images 中逐张登记
    dcfg = corr.get('docx_images', {})
    mat_imgs = collections.defaultdict(list)
    seen = set()
    for im, near in seg['imgs']:
        stem = Path(im.media).stem
        if stem in seen:
            die(f'{im.media} 在文档中出现不止一次（非装饰图片），请核对')
        seen.add(stem)
        c = dcfg.get(stem)
        if c is None:
            die(f'Word 图片 {im.media}（文档位置 {im.loc}，附近为第{near}题）没有在 tools/corrections/{paper}.json 的 docx_images 中登记归属')
        if 'material' in c:
            mat_imgs[c['material']].append(im)
        else:
            qby[c['q']]['figures'].append(im)
    unused = sorted(set(dcfg) - seen)
    if unused:
        die(f'docx_images 登记了文档中没有的图片：{unused}')
    recs = {}
    for q in seg['questions']:
        r = parse_docx_question(q)
        if r['partial_options']:
            die(f'第{q["number"]}题只拆出 {r["partial_options"]} 个选项，请核对原文档后用 text_fixes 处理')
        recs[q['number']] = r
    mats = {}
    for m in seg['materials']:
        text = join_docx(m['lines'])
        blocks = [{'type': 'text', 'text': p} for p in ([text] if text else [])]
        blocks += [{'type': 'fig', 'img': im} for im in mat_imgs.get(m['k'], [])]
        mats[m['k']] = dict(k=m['k'], header_text=m['header'], header_note='', blocks=blocks, pages=[], questions=m['questions'],
                            inline=[], raw=''.join(m['lines']))
    if seg['decor']:
        autofix.append(f'Word 文档中 {len(seg["decor"])} 处显示高度≤2pt 的细线图片（' +
                       '、'.join(sorted({Path(i.media).name for i in seg['decor']})) + '，PDF 转 Word 留下的页眉页脚分隔线）不收录。')
    for who, t, why in seg['ignored']:
        autofix.append(f'{who}中{t}{why}。')
    for t, after in seg['headings']:
        autofix.append(f'部分标题“{t}”（位于第{after}题之后）只用于分部分，不收录。' if after else f'部分标题“{t}”只用于分部分，不收录。')
    text_ans, lower = {}, []
    for q in seg['questions']:
        a = q['answer']
        if a and a['value']:
            v = a['value']
            if v != v.upper():
                lower.append(q['number'])
                v = v.upper()
            text_ans[q['number']] = dict(value=v, page=None, raw=a['raw'][:40])
    if lower:
        autofix.append('答案字母为小写的题（' + '、'.join(f'第{n}题' for n in lower) + '）按大写记录。')
    concl = {q['number']: answer_conclusion(q['analysis']) for q in seg['questions']}
    return dict(recs=recs, mats=mats, text_ans=text_ans, stats=[], conclusions=concl, seg=seg, all_inline=[],
                units=len(units), zip=zipfile.ZipFile(path))


def load_pdf_source(cfg: dict, corr: dict, paper: str, autofix: list) -> dict:
    qpdf = REPO / cfg['question_pdf']
    inline_text = corr.get('inline_images', {})
    pages = load_pages(qpdf)
    missing_q = set(cfg.get('missing_questions', []))
    qnum = qnum_re(cfg)
    seg = segment(pages, cfg['expected_questions'], inline_text, missing_q, qnum)
    left, right = seg['margins']
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
        recs[q.number] = parse_question(q, left, right, autofix, qnum)
        tags = [v for k, v in PDF_TAG_TYPE.items() if recs[q.number]['stem'].startswith(k)]
        recs[q.number]['tag'] = {'true_false': '判断题', 'multiple_choice': '多选题', 'single_choice': '单选题'}[tags[0]] if tags else None
        for st in recs[q.number]['strays']:
            if any(st.replace(' ', '').startswith(x) for x in ignore):
                autofix.append(f'第{q.number}题选项后的“{st}”按 ignore_lines 不收录。')
            else:
                die(f'第{q.number}题选项之后有一行无法归属：“{st}”。核对原卷后，若是题目内容请用 text_fixes 补入，'
                    f'若非试题内容（如“××题暂缺”说明）请写入 tools/corrections/{paper}.json 的 ignore_lines')
    mats = {}
    for mb in seg['materials']:
        m = parse_material(mb, left, right)
        m['raw'] = ''.join(t.text for kind_, o in mb.items if kind_ == 'line' for t in o.toks if not t.image)
        mats[m['k']] = m
    apdf = REPO / cfg['answer_pdf'] if cfg.get('answer_pdf') else None
    text_ans, stats = answer_text_layer(apdf) if apdf else ({}, [])
    for h in seg['headings']:
        raw_h = h.text
        if raw_h != unicodedata.normalize('NFKC', raw_h) and re.search('[⺀-⿟]', raw_h):
            autofix.append(f'部分标题第{h.page}页“{raw_h}”的文字层含康熙部首字（' +
                           '、'.join(f'{c}(U+{ord(c):04X})' for c in sorted(set(re.findall('[⺀-⿟]', raw_h)))) +
                           '），印出字形与常用字相同；按 NFKC 归一后识别部分，标题本身不收录。')
    return dict(recs=recs, mats=mats, text_ans=text_ans, stats=stats, conclusions={}, seg=seg, all_inline=all_inline,
                pages=pages, qpdf=qpdf)


def load_transcribed_source(cfg: dict, corr: dict, paper: str, autofix: list) -> dict:
    """原卷没有文字层（如打印成曲线的矢量字形 PDF）：题干、选项、材料文字取自修正文件的 transcription，
    题图与材料图仍按 question_pdf 中的图片对象裁剪。每张图片须归属某题、某组材料，或作为行内小图登记文字。"""
    qpdf = REPO / cfg['question_pdf']
    tr = corr['transcription']
    pages = load_pages(qpdf)
    imgs = {im.key: im for p in pages for im in p.images}
    inline_text = corr.get('inline_images', {})
    missing_q = set(cfg.get('missing_questions', []))
    nums = [n for n in range(1, cfg['expected_questions'] + 1) if n not in missing_q]
    qs = tr.get('questions', {})
    if sorted(int(k) for k in qs) != nums:
        die(f'transcription.questions 的题号与 tools/papers/{paper}.json 不符')
    sec_of = {n: s['name'] for s in tr.get('sections', []) for n in range(s['from'], s['to'] + 1)}
    used, inl_used = {}, {}

    def take(key, who):
        if key not in imgs:
            die(f'{who} 引用的图片 {key} 不在 {cfg["question_pdf"]} 中')
        if key in used or key in inline_text:
            die(f'图片 {key} 重复登记（{used.get(key, "inline_images")}、{who}）')
        used[key] = who
        return imgs[key]
    recs = {}
    for n in nums:
        q = qs[str(n)]
        if n not in sec_of:
            die(f'transcription.sections 没有覆盖第{n}题')
        opts = q.get('options', [])
        if opts and len(opts) != 4:
            die(f'transcription 第{n}题的选项应为 4 项（现为 {len(opts)} 项）')
        for k in q.get('inline', []):
            if k not in imgs or k not in inline_text:
                die(f'第{n}题的行内小图 {k} 不在 question_pdf 中或未在 inline_images 中给出文字')
            inl_used[k] = n
        r = dict(number=n, section_raw=sec_of[n], stem=q['stem'], options=[{'label': L, 'text': t} for L, t in zip('ABCD', opts)],
                 figures=[take(k, f'第{n}题') for k in q.get('figures', [])], pages=list(q['pages']), material=None,
                 labels_raw=[], strays=[], prefix='', raw=None, inline=list(q.get('inline', [])), tag=None)
        tags = [v for k, v in PDF_TAG_TYPE.items() if r['stem'].startswith(k)]
        r['tag'] = {'true_false': '判断题', 'multiple_choice': '多选题', 'single_choice': '单选题'}[tags[0]] if tags else None
        if r['figures'] and r['options'] and all(o['text'] == o['label'] for o in r['options']):
            autofix.append(f'第{n}题：图下选项只印了字母（“A、A B、B C、C D、D”），按图形选项处理（选项在题图中）。')
            r['options'] = []
        recs[n] = r
    mats = {}
    for k, m in sorted(tr.get('materials', {}).items(), key=lambda kv: int(kv[0])):
        k = int(k)
        qn = list(range(m['questions'][0], m['questions'][1] + 1))
        blocks = [{'type': 'text', 'text': b} if isinstance(b, str) else {'type': 'fig', 'img': take(b['image'], f'材料{k}')}
                  for b in m['content']]
        for n in qn:
            if recs[n]['material'] is not None:
                die(f'第{n}题同时属于两组材料')
            recs[n]['material'] = k
        mats[k] = dict(k=k, header_text=m.get('header', ''), header_note='', blocks=blocks, pages=list(m['pages']),
                       questions=qn, inline=[], raw=None)
    stray_inline = sorted(k for k in inline_text if k in imgs and k not in inl_used)
    if stray_inline:
        die(f'inline_images 登记的行内小图 {stray_inline} 没有被任何题目的 inline 引用')
    unused = sorted(k for k in imgs if k not in used and k not in inline_text)
    if unused:
        die(f'{cfg["question_pdf"]} 中的图片 {unused} 没有归属（题图、材料图或 inline_images）')
    apdf = REPO / cfg['answer_pdf'] if cfg.get('answer_pdf') else None
    text_ans, stats = answer_text_layer(apdf) if apdf else ({}, [])
    all_inline = sorted(k for k in inline_text if k in imgs)
    return dict(recs=recs, mats=mats, text_ans=text_ans, stats=stats, conclusions={}, seg=None, all_inline=all_inline,
                pages=pages, qpdf=qpdf)


def check_qtype(n: int, qt: str, vals: list) -> str | None:
    for v in vals:
        if qt == 'true_false' and v not in (['正确'], ['错误']):
            return f'判断题的答案应为“正确/错误”，现为 {v}'
        if qt == 'multiple_choice' and (len(v) < 2 or not set(v) <= set('ABCD')):
            return f'多选题的答案应为两个以上字母，现为 {v}'
        if qt == 'single_choice' and (len(v) != 1 or v[0] not in 'ABCD'):
            return f'单选题的答案应为一个字母，现为 {v}'
    return None


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------
def build(paper: str, work: Path | None):
    cfg, corr = load_cfg(paper)
    is_docx = bool(cfg.get('question_docx'))
    commit = source_commit(cfg, paper)
    inline_text = corr.get('inline_images', {})
    autofix, fixlog, problems = [], [], []
    if is_docx:
        src = load_docx_source(cfg, corr, paper, autofix)
    elif corr.get('transcription'):
        src = load_transcribed_source(cfg, corr, paper, autofix)
    else:
        src = load_pdf_source(cfg, corr, paper, autofix)
    recs, mats = src['recs'], src['mats']
    groups = [[m['questions'][0], m['questions'][-1]] if m['questions'] else [] for m in mats.values()]
    if 'material_groups' in corr and groups != corr['material_groups']:
        die(f'识别出的材料题组 {groups} 与 tools/corrections/{paper}.json 的 material_groups {corr["material_groups"]} 不符；先用 dump 检查材料分段')
    for r in recs.values():
        for o in r['options']:
            if len(o['text']) > 80 or '\n' in o['text']:
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

    # 题型：按原卷标注登记的题型，与题干中的“（判断题）”“{多选题}”等标注核对
    declared = {}
    for rng in corr.get('question_types', []):
        if rng['type'] not in QTYPES:
            die(f'question_types 中的题型“{rng["type"]}”无效')
        for n in range(rng['from'], rng['to'] + 1):
            declared[n] = rng['type']
    for n, r in recs.items():
        tag_t = DOCX_TAG_TYPE.get(r.get('tag'))
        if n in declared and tag_t and tag_t != declared[n]:
            die(f'第{n}题原卷标注为“{r["tag"]}”，与 question_types 登记的 {declared[n]} 不符')

    apply_text_fixes(recs, corr, fixlog)
    miss_fig = {int(k): v for k, v in corr.get('missing_figures', {}).items()}
    for r in recs.values():
        r['stem'] = normalize_blanks(r['stem'], r['section'])
        for o in r['options']:
            o['text'] = o['text'].strip()
        if r['options'] and [o['label'] for o in r['options']] != list('ABCD'):
            die(f'第{r["number"]}题选项拆分异常：{[o["label"] for o in r["options"]]}')
        if declared.get(r['number']) == 'true_false' and r['options']:
            die(f'第{r["number"]}题登记为判断题，但拆出了选项')
        if '⟦' in r['stem'] or any('⟦' in o['text'] for o in r['options']):
            die(f'第{r["number"]}题仍有未转写的行内小图')

    # 文字守恒：输出的题干+选项 = 原文字（PDF 文字层或 Word 文字）− 题号 − 选项字母 + 行内小图转写（空白不计；
    # 空括号按 normalize_blanks 统一为“（）”后再比，Word 中的“( )”“(）”等写法因此不算差异）
    conserve = []
    for n, r in recs.items():
        if r['raw'] is None:
            continue                                  # 转写的题（原卷没有文字层），没有可比对的原文字
        raw = r['raw'][len(r['prefix']):] if r['raw'].startswith(r['prefix']) else r['raw']
        want = collections.Counter(re.sub(r'\s', '', re.sub(r'[（(]\s*[）)]', '（）', raw)))
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
    fig_cfg = dict(corr.get('figures', {}), **corr.get('docx_images', {}))
    files = paper_files(paper)
    asset_dir = files['assets']
    if asset_dir.exists():
        shutil.rmtree(asset_dir)
    asset_dir.mkdir(parents=True)
    manifest = []
    own_work = work is None
    if is_docx:
        renders, page_by_no = {}, {}
    else:
        page_by_no = {p.no: p for p in src['pages']}
        fig_pages = sorted({f.page for r in recs.values() for f in r['figures']} |
                           {b['img'].page for m in mats.values() for b in m['blocks'] if b['type'] == 'fig'})
        work = work or Path(tempfile.mkdtemp(prefix=f'{paper}-'))
        renders = render_pages(src['qpdf'], fig_pages, work / 'render')

    def fig_key(im):
        return Path(im.media).stem if isinstance(im, DocxImg) else im.key

    def make_figure(im, role: str, qnums: list, default_alt: str):
        fid = f'{paper}-{im.key}'
        fc = fig_cfg.get(fig_key(im), {})
        if isinstance(im, DocxImg):
            raw = src['zip'].read(im.media)
            if raw[:8] != b'\x89PNG\r\n\x1a\n':
                die(f'{im.media} 不是 PNG；本工具只按原样收录 PNG 图片')
            path = asset_dir / f'{fid}.png'
            path.write_bytes(raw)                      # 按原样保存：字节与文档内的图片完全相同，不重新编码
            w, h = png_size(raw)
            manifest.append(dict(id=fid, path=f'assets/{paper}/{fid}.png', paper_id=paper, source_file=im.media,
                                 source_page=None, source_bbox_points=None,
                                 docx_extent_points=[round(im.cx / EMU_PER_PT, 2), round(im.cy / EMU_PER_PT, 2)],
                                 method='docx_original', width=w, height=h, sha256=hashlib.sha256(raw).hexdigest(),
                                 transcription=fc.get('transcription', '')))
            method = 'docx_original'
        else:
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
            method = 'pdf_render_crop'
        return dict(type='image', image_id=fid, path=f'assets/{paper}/{fid}.png', role=role, option_label=None,
                    method=method, alt=fc.get('alt', default_alt), transcription=fc.get('transcription', ''))

    def where(im):
        return f'{Path(im.media).name}' if isinstance(im, DocxImg) else f'第{im.page}页'

    for n in sorted(recs):
        r = recs[n]
        figs = []
        for im in r['figures']:
            role = fig_cfg.get(fig_key(im), {}).get('role') or ('question' if r['options'] else 'question_and_options')
            alt = f'{paper} {where(im)} 第{n}题题图' + ('（含选项A—D）' if role == 'question_and_options' else '')
            figs.append(make_figure(im, role, [n], alt))
        r['figure_objs'] = figs
        # 画有选项 A—D 的图（role=question_and_options）：没有文字选项时，选项全指向它；
        # 有文字选项（如“如上图所示”）时，文字照录，并同样指向图中对应字母
        qo = [f for f in figs if f['role'] == 'question_and_options']
        if not r['options']:
            if declared.get(n) == 'true_false' or n in miss_fig:
                continue
            if len(qo) != 1:
                die(f'第{n}题没有文字选项，画有选项的题图应恰好 1 张（现为 {len(qo)} 张）；'
                    f'请在 tools/corrections/{paper}.json 的 figures / docx_images 中把只含题目部分的图设为 role: "question"，'
                    f'原文档缺图的写入 missing_figures')
            r['options'] = [{'label': L, 'text': '', 'image_refs': [{'image_id': qo[0]['image_id'], 'label_in_image': L}]}
                            for L in 'ABCD']
        else:
            for o in r['options']:
                o['image_refs'] = [{'image_id': qo[0]['image_id'], 'label_in_image': o['label']}] if len(qo) == 1 else []
    for n, why in miss_fig.items():
        if recs[n]['figure_objs'] or recs[n]['options']:
            die(f'missing_figures 登记的第{n}题有题图或选项，请核对')
        recs[n]['notes'].append(why)

    # 材料
    mat_objs = {}
    miss_mat = {int(k): v for k, v in corr.get('missing_materials', {}).items()}
    mfix = corr.get('material_text_fixes', {})
    for k, m in mats.items():
        mc = corr.get('materials', {}).get(str(k), {})
        content = []
        for b in m['blocks']:
            if b['type'] == 'text':
                content.append({'type': 'text', 'text': b['text']})
            else:
                alt = f'{paper} {where(b["img"])} 资料分析材料{k}图表'
                content.append(make_figure(b['img'], 'material', m['questions'], alt))
        for fx in mfix.get(str(k), []):
            hits = [b for b in content if b['type'] == 'text' and fx['find'] in b['text']]
            if len(hits) != 1 or hits[0]['text'].count(fx['find']) != 1:
                die(f'material_text_fixes 材料{k}：要替换的“{fx["find"]}”应恰好出现一次')
            hits[0]['text'] = hits[0]['text'].replace(fx['find'], fx['replace'])
            fixlog.append(f'材料{k}（第{m["questions"][0]}—{m["questions"][-1]}题）：{fx["reason"]}')
        out_m = ''.join(b['text'] for b in content if b['type'] == 'text')
        if m['raw'] is not None and collections.Counter(re.sub(r'\s', '', m['raw'])) + collections.Counter(re.sub(r'\s', '', ''.join(inline_text[x] for x in m['inline']))) != collections.Counter(re.sub(r'\s', '', out_m)):
            die(f'材料{k}文字守恒检查不通过')
        if m['header_note']:
            autofix.append(f'材料{k}标题后的编者按语不作为材料内容收录：“{redact(m["header_note"])}”')
        if not content:
            if not all(n in miss_mat for n in m['questions']):
                die(f'材料{k}（第{m["questions"]}题）没有内容；原文档缺资料的请写入 missing_materials')
            autofix.append(f'材料{k}只有“{m["header_text"]}”一句、没有资料内容，第{num_ranges(m["questions"])}题的 material 记为 null。')
            for n in m['questions']:
                recs[n]['material'] = None
            continue
        mat_objs[k] = dict(id=f'{paper}-M{k}', question_numbers=m['questions'], source_pages=m['pages'], content=content)
        for n in m['questions']:
            for note in mc.get('question_notes', []):
                recs[n]['notes'].append(note)
    for n, why in miss_mat.items():
        if recs[n]['material'] is not None:
            die(f'missing_materials 登记的第{n}题仍有材料，请核对')
        recs[n]['notes'].append(why)

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
    text_ans, stats = src['text_ans'], src['stats']
    man_ans = manual_answers(corr.get('answers'))
    alt_ans = manual_answers({'by_page': (corr.get('answers') or {}).get('alternatives', {})})
    ans_notes = corr.get('answer_notes', {})
    answer_log = dict(text=text_ans, manual=man_ans, alternatives=alt_ans, stats=stats, conflicts=[], missing=[],
                      conclusions=src['conclusions'], docx=is_docx)
    src_cn = 'Word 文档' if is_docx else '答案PDF'
    for n, r in recs.items():
        t, mnl, alt = text_ans.get(n), man_ans.get(n), alt_ans.get(n)
        cands = []
        for c in (mnl, t, alt):
            if c and c['value'] not in [x['value'] for x in cands]:
                cands.append(c)
        if not cands:
            r['answer'] = dict(status='missing', values=[], source_pages=[], note=ans_notes.get(str(n), f'{src_cn}中未找到本题答案；未推测答案。'))
            answer_log['missing'].append(n)
        else:
            vals = [list(c['value']) if c['value'] not in ('正确', '错误') else [c['value']] for c in cands]
            pages_ = sorted({c['page'] for c in cands if c['page']})
            if len(cands) > 1:
                answer_log['conflicts'].append((n, [c['value'] for c in cands]))
                r['answer'] = dict(status='disputed', values=vals, source_pages=pages_,
                                   note=ans_notes.get(str(n), f'{src_cn}给出不同答案，保留争议，不自行裁定。'))
            else:
                r['answer'] = dict(status='known', values=vals, source_pages=pages_, note=ans_notes.get(str(n), ''))
        vals = r['answer']['values']
        if n in declared:
            qt = declared[n]
        elif vals:
            qt = 'true_false' if vals[0][0] in ('正确', '错误') else ('multiple_choice' if len(vals[0]) > 1 else 'single_choice')
        else:
            qt = 'single_choice'
        err = check_qtype(n, qt, vals)
        if err:
            die(f'第{n}题：{err}')
        r['question_type'] = qt

    # 组装记录
    qsrc, asrc = src_files(cfg)
    records = []
    for n in sorted(recs):
        r = recs[n]
        rec = collections.OrderedDict()
        rec['id'] = f'{paper}-Q{n:03d}'
        rec['year'] = cfg['year']
        rec['province'] = PROVINCE
        rec['exam'] = EXAM
        rec['subject'] = SUBJECT
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
        rec['source'] = dict(question_pdf=qsrc, question_pages=r['pages'], answer_pdf=asrc, repository_commit=commit)
        rec['notes'] = r['notes']
        records.append(rec)

    # 写文件：只写本卷自己的文件
    files['jsonl'].write_text(''.join(json.dumps(r, ensure_ascii=False, separators=(',', ':')) + '\n' for r in records), encoding='utf-8')
    files['manifest'].write_text(json.dumps(sorted(manifest, key=lambda e: e['id']), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    write_sources(cfg, commit, paper)
    files['md'].write_text(render_md(records, cfg, paper, commit), encoding='utf-8')
    files['quality'].parent.mkdir(exist_ok=True)
    files['quality'].write_text(render_report(records, cfg, corr, paper, commit, autofix, fixlog, problems,
                                              answer_log, manifest, src['all_inline'], src['seg'], conserve), encoding='utf-8')
    _PAGE_CACHE.clear()
    if own_work and work is not None:
        shutil.rmtree(work, ignore_errors=True)
    print(f'已生成 {paper}：{len(records)} 题，题图/材料图 {len(manifest)} 张' + ('' if own_work or work is None else f'；渲染缓存 {work}'))
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
    rels = all_src_files(cfg)
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
    for rel in all_src_files(cfg):
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


def src_files(cfg: dict) -> tuple:
    """(题目来源, 答案来源)：Word 题源的答案与题目在同一文档。"""
    q = cfg.get('question_docx') or cfg['question_pdf']
    a = cfg.get('answer_pdf') or (cfg['question_docx'] if cfg.get('question_docx') else None)
    return q, a


def all_src_files(cfg: dict) -> list:
    """本卷用到的全部源文件：题目、答案来源，加上 reference_files（参与核对、不作题源的文件）。"""
    return sorted({r for r in src_files(cfg) if r} | {x['path'] for x in cfg.get('reference_files', [])})


def render_md(records, cfg, paper, commit) -> str:
    qtype_cn = {'single_choice': '单选', 'multiple_choice': '多选', 'true_false': '判断'}
    qsrc, asrc = src_files(cfg)
    out = [f'# {cfg["title"]}', '',
           f'共 {len(records)} 题，原题号完整保留。内容：题干、选项、答案（不收解析）；资料分析共用材料置于所属题组前，JSONL 每条记录完整内嵌材料。', '',
           f'[结构化数据]({paper}.jsonl) · [字段说明](schema.json) · [质量报告](quality/{paper}.md)', '',
           f'原题来源：[{Path(qsrc).name}]({blob_url(commit, qsrc)})。']
    if asrc and asrc != qsrc:
        out[-1] += f'答案来源：[{Path(asrc).name}]({blob_url(commit, asrc)})（只取答案）。'
    elif asrc:
        out[-1] += '答案取自同一文档每题后的“答案：”（只取答案，不收解析）。'
    for ref in cfg.get('reference_files', []):
        out[-1] += f'参考：[{Path(ref["path"]).name}]({blob_url(commit, ref["path"])})（{ref["use"]}）。'

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
        pg = r['source']['question_pages']
        meta = f'`{r["id"]}` · {qtype_cn[r["question_type"]]}' + (f' · {sub}' if sub else '') + \
               (f' · 原卷第 {pages_cn(pg)} 页' if pg else ' · 原文档为 Word（无页码）')
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
    is_docx = bool(cfg.get('question_docx'))
    qsrc, asrc = src_files(cfg)
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
    qtype_cn = {'single_choice': '单选', 'multiple_choice': '多选', 'true_false': '判断'}
    if is_docx:
        L = [f'# {paper} 转换与校验记录', '',
             f'范围：{cfg["title"]}，共 {len(records)} 题。来源为仓库内 1 份 Word 文档（题目与答案解析合编），未修改；'
             f'提取基于提交 `{commit}`。', '',
             '| 文件 | Git blob | 用途 |', '| --- | --- | --- |',
             f'| `{qsrc}` | `{sha.get(qsrc, "")}` | 题干、选项、材料、题图（读 word/document.xml 与 word/media/）；答案只取每题的“答案：”，不收解析 |']
    else:
        refs = cfg.get('reference_files', [])
        L = [f'# {paper} 转换与校验记录', '',
             f'范围：{cfg["title"]}，共 {len(records)} 题。来源为仓库内题本与答案解析各 1 份 PDF'
             + (f'，另有 {len(refs)} 份参考文件' if refs else '') + '，均未修改；'
             f'提取基于提交 `{commit}`。', '',
             '| 文件 | Git blob | 用途 |', '| --- | --- | --- |',
             f'| `{qsrc}` | `{sha.get(qsrc, "")}` | '
             + ('题本（以此为准）：原卷没有文字层，题干、选项、材料按修正文件中的转写收录；题图、材料图从本卷裁剪 |'
                if corr.get('transcription') else '题干、选项、材料、题图（有文字层） |')]
        if asrc:
            L.append(f'| `{asrc}` | `{sha.get(asrc, "")}` | 只取答案，不收解析 |')
        for ref in refs:
            L.append(f'| `{ref["path"]}` | `{sha.get(ref["path"], "")}` | {ref["use"]} |')
    L += ['', '## 完整性', '', '| 部分 | 题号 | 题数 | 题型 |', '| --- | --- | ---: | --- |']
    for s in order:
        rs = [r for r in records if r['section'] == s]
        nums = [r['question_number'] for r in rs]
        qt = collections.Counter(r['question_type'] for r in rs)
        L.append(f'| {s} | {num_ranges(nums)} | {len(nums)} | ' + '，'.join(f'{qtype_cn[k]} {v}' for k, v in qt.items()) + ' |')
    L += [f'| 合计 | | {len(records)} | |', '']
    if sub_count:
        L += ['判断推理小类（记在 notes，如 `subtype:类比推理`）：' +
              '，'.join(f'{k} {sub_count[k]} 题（第{num_ranges(sub_ranges[k])}题）' for k in SUBTYPES if sub_count[k]) + '。', '']
    nfig_q = sum(len(r['figures']) for r in records)
    qtypes = collections.Counter(r['question_type'] for r in records)
    nmat_img = len({b['image_id'] for m in mats.values() for b in m['content'] if b['type'] == 'image'})
    declared = bool(corr.get('question_types'))
    if is_docx:
        img_line = (f'- 图片 {len(manifest)} 张：题图 {nfig_q} 张、材料图 {nmat_img} 张，全部按原样取自 Word 的 word/media/'
                    '（`docx_original`，字节与文档内图片完全相同，未重新编码、未裁剪、未重绘）。')
        cons_src = '该题在 Word 文档中的文字'
    else:
        img_line = f'- 图片 {len(manifest)} 张：题图 {nfig_q} 张、材料图 {nmat_img} 张，全部为 288 DPI 页面渲染后的裁剪（`pdf_render_crop`），无重绘。'
        cons_src = '该题在原 PDF 文字层中的字符'
    L += [f'- 资料分析共用材料 {len(mats)} 组，关联 {sum(len(m["question_numbers"]) for m in mats.values())} 题；每题 JSONL 内嵌完整材料。', img_line]
    if all_inline:
        L.append(f'- 行内小图 {len(all_inline)} 个（分数等）已转成文字，不另存图片：' + '、'.join(f'`{k}`' for k in all_inline) + '。')
    if corr.get('transcription'):
        cons_line = ('- 文字来源：原卷没有文字层，每题“题干+选项”与材料正文取自修正文件的 `transcription`（转写与核对方法见下文'
                     '“复核方法”），没有可做文字守恒检查的原文字；' + str(len(records)) + ' 题与转写一一对应。')
    else:
        cons_line = (f'- 文字守恒检查：每题“题干+选项”与{cons_src}逐一相符（不计空白、题号与选项字母，行内小图按转写计）'
                     + ('，' + str(len(records)) + ' 题全部通过' if not conserve else f'；人工修正造成差异的题：{[c[0] for c in conserve]}')
                     + (f'；{len(mats)} 组材料正文同样相符。' if mats else '。'))
    L += [cons_line,
          ('- 题型按原卷标注登记（`question_types`），并与答案逐题核对（判断题答案为“正确/错误”、多选题两个以上字母、单选题一个字母）：'
           if declared else '- 题型按答案判定（单选一个字母、多选多个字母）：')
          + '，'.join(f'{qtype_cn[k]} {v} 题' for k, v in qtypes.items()) + '。判断题没有选项（`options` 为空）。' if qtypes.get('true_false') else
          ('- 题型按原卷标注登记（`question_types`），并与答案逐题核对：' if declared else '- 题型按答案判定（单选一个字母、多选多个字母）：')
          + '，'.join(f'{qtype_cn[k]} {v} 题' for k, v in qtypes.items()) + '。', '']
    custom = corr.get('report', {})
    L += ['## 答案', '', '| 状态 | 数量 |', '| --- | ---: |']
    for k, cn in [('known', '明确答案'), ('disputed', '争议答案'), ('missing', '答案缺失')]:
        L.append(f'| {cn}（`{k}`） | {status.get(k, 0)} |')
    tq, mq, aq = set(answer_log['text']), set(answer_log['manual']), set(answer_log.get('alternatives', {}))
    if is_docx:
        concl = answer_log.get('conclusions', {})
        agree = sorted(n for n, v in concl.items() if v and n in answer_log['text'] and v == answer_log['text'][n]['value'])
        differ = sorted(n for n, v in concl.items() if v and n in answer_log['text'] and v != answer_log['text'][n]['value'])
        nocon = sorted(n for n in answer_log['text'] if not concl.get(n))
        L += ['', f'Word 文档中每题之后有“答案：X”一行（个别写在选项或题干行末），脚本取到 {len(tq)} 题。'
              + f'再与同题解析的结论（如“故答案为C”“故本题答案选择BD”“只有D”）逐题比对：一致 {len(agree)} 题'
              + (f'（第{num_ranges(agree)}题）' if agree else '') + (f'；不一致 {len(differ)} 题（第{num_ranges(differ)}题，逐题人工核对，见下）' if differ else '')
              + (f'；解析中没有可比对的结论字母 {len(nocon)} 题（第{num_ranges(nocon)}题，含全部判断题，逐题人工核对答案行）。' if nocon else '。')]
    else:
        stats = answer_log['stats']
        scanned = [p for p, n in stats if n < 30]
        texty = [p for p, n in stats if 0 < n < 30]
        both = sorted(tq & mq)
        vector = cfg.get('answer_pdf_kind') == 'vector'
        L += ['', f'答案PDF共 {len(stats)} 页，其中 {len(scanned)} 页'
              + ('为矢量字形页面（文字打印成曲线，不是扫描图片）、没有文字层' if vector else '为扫描图片、没有可用的正文文字层')
              + (f'（第{"、".join(map(str, texty))}页另有后加的少量文字）' if texty else '') + '。'
              + (f'文字层直接取到 {len(tq)} 题（' + '、'.join(f'{k}{v["value"]}' for k, v in sorted(answer_log['text'].items())) + '）；' if tq else '文字层没有取到答案；')
              + (f'{"页面" if vector else "扫描图"}人工读取 {len(mq)} 题（第{num_ranges(sorted(mq))}题，记录在 `tools/corrections/{paper}.json` 的 `answers.by_page`）' if mq else '')
              + (f'，另有第{num_ranges(sorted(aq))}题的第二个候选记在 `answers.alternatives`。' if aq else '。')
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
    for sec in custom.get('sections', []):
        L += ['', f'## {sec["title"]}', '']
        if sec.get('intro'):
            L += [sec['intro'], '']
        for item in sec.get('items', []):
            L.append(f'- {item}')
    L += ['', '## 转写拿不准、需要留意的地方', '']
    for item in custom.get('uncertain', []):
        L.append(f'- {item}')
    usage = collections.defaultdict(list)
    for r in records:
        for f in r['figures']:
            usage[f['image_id']].append(str(r['question_number']))
    for m in mats.values():
        for b in m['content']:
            if b['type'] == 'image':
                usage[b['image_id']] = [f'{m["question_numbers"][0]}—{m["question_numbers"][-1]}（材料）']
    if is_docx:
        L += ['', '## 题图与材料图', '',
              'Word 中的图片按原样保存：从 .docx 的 word/media/ 取出原文件写入 `assets/`，字节不变（SHA-256 与文档内图片相同，'
              'verify 时逐张与源文档比对），没有 PDF 坐标。`assets/' + paper + '/manifest.json`（汇总于根目录 `assets-manifest.json`）'
              '记录来源文件（`source_file`）、像素尺寸、文档中的显示尺寸（`docx_extent_points`，pt）与 SHA-256；`source_page`、'
              '`source_bbox_points` 记为 null。浮动图片在文档流中的位置不代表版面位置，每张图片的归属在修正文件 `docx_images` 中逐张登记。', '',
              '| 图片 | 题号 | 来源文件 | 显示尺寸（pt） | 像素 | 文字转写 |', '| --- | --- | --- | --- | --- | --- |']
        for e in manifest:
            ext = '×'.join(f'{v:g}' for v in e['docx_extent_points'])
            L.append(f'| `{e["id"]}` | {"、".join(usage[e["id"]])} | `{e["source_file"]}` | {ext} | {e["width"]}×{e["height"]} | {"有" if e["transcription"] else "—"} |')
        L += ['', '脚本检查：' + (f'{len(manifest)} 张图均为文档原图，未发现问题。' if not problems else '发现问题：' + '；'.join(problems))]
    else:
        L += ['', '## 题图与材料图', '',
              '裁剪框取原 PDF 中图片对象的外框，收紧到有墨迹处并留 1.5pt 白边，再检查框内不含任何文字层字符'
              f'（题干、选项文字不入图；画在图中的选项字母 A—D 属于图片本身，随图保留）。`assets/{paper}/manifest.json`（汇总于根目录 `assets-manifest.json`）记录来源页、'
              '裁剪框（PDF pt，左上角为原点）、像素尺寸与 SHA-256；像素尺寸 = 裁剪框 × 4（288 DPI），可按 pt 尺寸原大印刷。', '',
              '| 图片 | 题号 | 页 | 裁剪框（pt） | 像素 | 文字转写 |', '| --- | --- | ---: | --- | --- | --- |']
        for e in manifest:
            bb = ', '.join(f'{v:g}' for v in e['source_bbox_points'])
            L.append(f'| `{e["id"]}` | {"、".join(usage[e["id"]])} | {e["source_page"]} | {bb} | {e["width"]}×{e["height"]} | {"有" if e["transcription"] else "—"} |')
        if corr.get('transcription') and not problems:
            L += ['', f'原卷没有文字层，脚本无法检查裁剪框内是否混入题干文字；{len(manifest)} 张图的裁剪范围已逐张对照原页目视检查（见复核方法）。']
        else:
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
                mats=len(mats), figs=len(figs), mimgs=len(mimgs), qt=collections.Counter(r['question_type'] for r in rs),
                sec=collections.Counter(r['section'] for r in rs),
                sub=collections.Counter(n.split(':', 1)[1] for r in rs for n in r['notes'] if n.startswith('subtype:')))


def render_quality_index(papers, recs, cfgs, manifest, sources) -> str:
    stats = {p: paper_stats(recs[p]) for p in papers}
    tot = collections.Counter()
    for x in stats.values():
        tot.update({k: v for k, v in x.items() if isinstance(v, int)})
    L = [f'# {BANK}（{YEARS}）转换与校验汇总', '',
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
    qcn = [('true_false', '判断题'), ('multiple_choice', '多选题'), ('single_choice', '单选题')]
    L += ['', '## 题型', '', '| 试卷 | ' + ' | '.join(c for _, c in qcn) + ' |', '| --- | ' + ' | '.join('---:' for _ in qcn) + ' |']
    for p in papers:
        L.append(f'| `{p}` | ' + ' | '.join(str(stats[p]['qt'][k]) for k, _ in qcn) + ' |')
    L += ['', '## 争议与缺失答案', '']
    flagged = [(r['id'], r['answer']) for p in papers for r in recs[p] if r['answer']['status'] != 'known']
    L += [f'- `{i}`：{a["status"]}，候选 ' + ('、'.join(''.join(v) for v in a['values']) or '无') + f'；{a["note"]}'
          for i, a in flagged] or ['无。']
    noted = [(r['id'], r['answer']['note']) for p in papers for r in recs[p]
             if r['answer']['status'] == 'known' and r['answer']['note']]
    if noted:
        L += ['', '答案明确、但来源或依据需要留意的题：', '']
        L += [f'- `{i}`：{n}' for i, n in noted]
    unusable = [(r['id'], [n for n in r['notes'] if n.startswith('原文档缺')]) for p in papers for r in recs[p]]
    unusable = [(i, ns) for i, ns in unusable if ns]
    if unusable:
        L += ['', '## 原文档缺图、缺资料的题', '', '这些题的题图或资料在源文件中就缺失，题目无法单独使用，组卷时请跳过或另找原卷补齐：', '']
        L += [f'- `{i}`：{"；".join(ns)}' for i, ns in unusable]
    meth = collections.Counter(e['method'] for e in manifest)
    L += ['', '## 图片', '',
          f'{len(manifest)} 张：' + '，'.join(f'{ {"pdf_render_crop": "原 PDF 页面按 288 DPI 渲染后的裁剪（`pdf_render_crop`）", "docx_original": "从 Word 文档 word/media/ 按原样取出的原图（`docx_original`）"}.get(k, k)}{v} 张' for k, v in sorted(meth.items(), key=lambda kv: kv[0], reverse=True))
          + f'；其中 {sum(1 for e in manifest if e["transcription"])} 张附文字转写。来源页与裁剪框（pt）或来源文件与显示尺寸、像素尺寸与 SHA-256 见 '
          '[assets-manifest.json](assets-manifest.json)。', '',
          '## 校验', '',
          '`python3 tools/extract.py verify` 校验全部卷：schema、题号、题型与答案语义、材料一致性、图片 SHA-256 与像素尺寸（Word 原图另与源文档逐字节比对）、'
          'Markdown 链接、源文件 blob，并检查本汇总及 all.jsonl、assets-manifest.json、sources.json、README.md 与各卷文件一致。'
          '源文件提取所基于的提交：' + (f'`{sources["commit"]}`' if sources['commit'] else '见 sources.json（各卷不同）') + '。', '']
    return '\n'.join(L)


def render_readme(papers, recs, cfgs, manifest, sources) -> str:
    stats = {p: paper_stats(recs[p]) for p in papers}
    n = sum(x['n'] for x in stats.values())
    ntr = sum(1 for e in manifest if e['transcription'])
    meth = collections.Counter(e['method'] for e in manifest)
    L = [f'# {BANK}整卷结构化题库（{YEARS}）', '',
         f'{len(papers)} 套试卷，共 {n} 题。按卷保留原题号，收录题干、选项、答案，不收录解析。每行一题的字段、题图裁剪与清单、'
         '答案写法、质量报告与广东省考题库（[行测 2013—2021](../../行测/2013-2021/README.md)、[行测 2022—2026](../../行测/2022-2026/README.md)）'
         f'一致，组卷工具可以同样读取；`exam` 为“{EXAM}”，`subject` 为“{SUBJECT}”，`year` 为 2022—2026。', '',
         '| 试卷 | 题数 | 判断题 | 多选题 | 单选题 | 明确答案 | 争议答案 | 答案缺失 | 文件 |',
         '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |']
    for p in papers:
        x = stats[p]
        L.append(f'| {cfgs[p][0]["title"]} | {x["n"]} | {x["qt"]["true_false"]} | {x["qt"]["multiple_choice"]} | {x["qt"]["single_choice"]} | '
                 f'{x["known"]} | {x["disputed"]} | {x["missing"]} | '
                 f'[阅读]({p}.md) · [JSONL]({p}.jsonl) · [质量报告](quality/{p}.md) |')
    L += ['', '## 给 AI 的入口', '',
          '- [all.jsonl](all.jsonl)：每行一道题，UTF-8；可直接逐行解析、分块或建立检索索引。',
          '- 每卷的 Markdown：供阅读，保留图片与图表文字数据。',
          '- [schema.json](schema.json)：字段类型；[assets-manifest.json](assets-manifest.json)：图片来源（PDF 页与裁剪坐标 pt，'
          '或 Word 内的来源文件与显示尺寸）、像素尺寸与 SHA-256；[sources.json](sources.json)：源文件路径及 Git blob SHA。',
          '- [质量报告](quality-report.md)：各卷汇总；每卷的详细记录在 `quality/`。', '',
          'JSONL 每条题目都包含完整 `material`（如果有），包括材料文字、图表数据文字和图片路径。每题的 `figures` 包含题图；'
          '`options[].image_refs` 指向图形选项。读取图形题时，需要把图片一并交给支持图像的模型。所有 `path` 相对于本目录，'
          '不能只传 JSONL 而丢弃 `assets/`。', '',
          '`answer.values` 表示候选答案集合：单选 `[ ["A"] ]`，多选 `[ ["A","B"] ]`，判断题 `[ ["正确"] ]`；争议答案例如 '
          '`[ ["D"], ["B"] ]`，表示 D 或 B 两个候选，**不是多选 DB**。`status` 分别为 `known`、`disputed`、`missing`。'
          '缺失时 `values=[]`。', '',
          '`section` 照原卷部分记（原卷“常识应用”记为常识判断，“言语表达与理解”记为言语理解与表达；原卷只按题型分部分的，'
          '按题目内容记，并在 `notes` 中说明）。判断推理题在 `notes` 中注明小类（`subtype:图形推理`、`subtype:定义判断`、'
          '`subtype:类比推理`、`subtype:逻辑判断`），组卷时可按小类筛选。', '',
          '## 与省考题库的不同', '',
          '- 题型：常识部分有判断题（`question_type` 为 `true_false`，原卷没有选项，`options` 为空数组，答案为“正确/错误”）'
          '和多选题（`multiple_choice`）。题型按原卷标注登记，并与答案逐题核对。',
          '- 卷名为 `SYDW<年>`（如 `SYDW2024-Q001`），没有乡镇/县级后缀；`paper_variant` 记为“未标卷别”。',
          '- Word 题源（2026年卷）：题图按原样从 .docx 的 word/media/ 取出（`method` 为 `docx_original`，schema 的 method 为此增加了这个值），'
          '不裁剪、不重新编码；清单中 `source_page`、`source_bbox_points` 为 null，另记 `source_file`（文档内路径）与 '
          '`docx_extent_points`（文档中的显示尺寸，pt）。Word 没有页码，`question_pages`、`material.source_pages`、`answer.source_pages` '
          '为空数组；`source.question_pdf` 与 `source.answer_pdf` 都填该 .docx 的路径（字段名沿用省考题库）。',
          '- 源文件缺图、缺资料的题照实记录：原文档缺题图（图中画有选项）的题 `options` 为空数组；缺资料的资料分析题 `material` 为 null；'
          '均在 `notes` 中说明（以“原文档缺”开头），无法单独使用。',
          '- 组卷工具 `广东行测18套模拟/重编/tools/build_paper.py` 目前只读取 `广东/行测/` 下的 `GD20*.jsonl`、按 `GD…` 编号解析来源，'
          '打印排版按 `广东/行测/` 的 `assets-manifest.json` 取原卷印宽；要用本题库，需把本目录、`SYDW20*.jsonl` 与 `SYDW…` 编号加进去'
          '（Word 原图没有 PDF 裁剪框，印宽可用 `docx_extent_points`）。本题库未改动组卷工具。']
    extra = [(p, x) for p in papers for x in cfgs[p][1].get('report', {}).get('readme', [])]
    if extra:
        L += ['', '需要留意：', '']
        L += [f'- {cfgs[p][0]["title"]}：{x}' for p, x in extra]
    parts = []
    if meth.get('pdf_render_crop'):
        parts.append(f'{meth["pdf_render_crop"]} 个为原 PDF 页面按 288 DPI 渲染后的裁剪，只裁图形本身，无重绘')
    if meth.get('docx_original'):
        parts.append(f'{meth["docx_original"]} 个为 Word 文档中的原图，按原样保存')
    L += ['', '## 图文处理', '',
          f'正文、选项、数字、分数及上下标转为文字；行内的分数、公式小图转写为文字，不另存图片。{len(manifest)} 个题图/材料图文件中，'
          + '；'.join(parts) + f'；{ntr} 个图表另有经过对照的文字转写，便于纯文本检索。'
          '源文件的措辞、数据和答案按原卷保留，错字照录，明显的印刷问题在题目 `notes` 中说明。PDF 页码为 1 起算的物理页码。', '',
          '## 整理与校验', '',
          '整理工具在 `tools/`（由 `广东/行测/2013-2021/tools/` 复制后修改）：每卷的登记信息在 `tools/papers/<卷>.json`，'
          '人工修正在 `tools/corrections/<卷>.json`（各键的说明见 `python3 tools/extract.py --help`）。', '',
          '```bash',
          'python3 tools/extract.py dump <卷>          # 自动分题结果（PDF 或 Word），供核对、编写修正',
          'python3 tools/extract.py answer-sheet <卷>  # 扫描版答案：裁出答案结论行拼图，人工读取',
          'python3 tools/extract.py build <卷>         # 只生成本卷文件，并校验本卷',
          'python3 tools/extract.py index              # 合并生成根目录汇总',
          'python3 tools/extract.py verify             # 校验全部卷与汇总',
          '```', '',
          '`build` 只写本卷的 `<卷>.jsonl`、`<卷>.md`、`assets/<卷>/`（含 `manifest.json`）、`quality/<卷>.md`、'
          '`sources/<卷>.json`，多人可以同时整理不同的卷；根目录的 `all.jsonl`、`assets-manifest.json`、`sources.json`、'
          '`quality-report.md` 与本文件只由 `index` 生成，合并后有冲突时重跑 `index` 即可。', '',
          '## 来源与可追溯性', '',
          '原始文件位于仓库的 `广东/事业单位/<年>/`，未修改。' +
          (f'提取基于提交 `{sources["commit"]}`；' if sources['commit'] else '各卷提取所基于的提交见 sources.json；') +
          f'{len(sources["sources"])} 个源文件的 blob SHA 见 [sources.json](sources.json)，build 时均已与本地文件核对一致。', '']
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
    cfg, corr = load_cfg(paper)
    f = paper_files(paper)
    for k in ('jsonl', 'md', 'manifest', 'quality', 'sources'):
        check(f[k].exists(), f'{paper} 缺少 {f[k].relative_to(OUT)}')
    rs = read_jsonl(f['jsonl'])
    md = f['md'].read_text(encoding='utf-8')
    manifest = {e['id']: e for e in json.loads(f['manifest'].read_text(encoding='utf-8'))}
    nums = [k for k in range(1, cfg['expected_questions'] + 1) if k not in set(cfg.get('missing_questions', []))]
    check([r['question_number'] for r in rs] == nums, f'{paper} 题号与 tools/papers/{paper}.json 不符')
    check(len(re.findall(r'^### 第 \d+ 题$', md, re.M)) == len(nums), f'{paper} Markdown 题数不符')
    miss_fig = {int(k) for k in corr.get('missing_figures', {})}
    miss_mat = {int(k) for k in corr.get('missing_materials', {})}
    qsrc, asrc = src_files(cfg)
    mats, used = {}, set()
    for r in rs:
        rid = r['id']
        if validator:
            errs = sorted(validator.iter_errors(r), key=lambda e: list(e.path))
            check(not errs, f'{rid}: {errs[0].message if errs else ""}')
        check(rid == f'{paper}-Q{r["question_number"]:03d}' and r['paper_id'] == paper and r['year'] == cfg['year'],
              f'{rid} 编号或年份不符')
        check(r['exam'] == EXAM and r['subject'] == SUBJECT and r['province'] == PROVINCE, f'{rid} exam/subject/province 不符')
        check(r['source']['question_pdf'] == qsrc and r['source']['answer_pdf'] == asrc, f'{rid} 来源文件不符')
        dumped = json.dumps(r, ensure_ascii=False)
        check(r['stem'] and '⟦' not in dumped and chr(0xFFFD) not in dumped, f'{rid} 题干为空或含未转写的占位')
        for para in r['stem'].split('\n'):
            check(para in md, f'{rid} 题干未出现在 Markdown')
        a = r['answer']
        check(len(a['values']) == {'known': 1, 'disputed': 2, 'missing': 0}[a['status']]
              or (a['status'] == 'disputed' and len(a['values']) > 1), f'{rid} 答案状态与候选数不符')
        if r['question_type'] == 'true_false':
            check(r['options'] == [], f'{rid} 判断题不应有选项')
        elif r['question_number'] in miss_fig:
            check(r['options'] == [] and r['figures'] == [], f'{rid} 登记为缺图，却有题图或选项')
        else:
            check([o['label'] for o in r['options']] == list('ABCD'), f'{rid} 选项不是A—D')
        for o in r['options']:
            check(o['text'] or o['image_refs'], f'{rid} {o["label"]} 项为空')
            for ref in o['image_refs']:
                check(ref['image_id'] in {x['image_id'] for x in r['figures']}, f'{rid} 选项图不在题图中')
        err = check_qtype(r['question_number'], r['question_type'], a['values'])
        check(not err, f'{rid} 题型与答案不符：{err}')
        if r['section'] == '判断推理':
            check(sum(x.startswith('subtype:') for x in r['notes']) == 1, f'{rid} 缺判断推理小类')
        imgs = list(r['figures'])
        if r['section'] == '资料分析' and r['question_number'] not in miss_mat:
            check(r['material'] and r['question_number'] in r['material']['question_numbers'], f'{rid} 缺共用材料')
        if r['question_number'] in miss_mat:
            check(r['material'] is None, f'{rid} 登记为缺资料，却有 material')
        if r['material']:
            mid = r['material']['id']
            check(mats.setdefault(mid, r['material']) == r['material'], f'{mid} 各题内嵌内容不一致')
            imgs += [b for b in r['material']['content'] if b['type'] == 'image']
        for im in imgs:
            check(im['image_id'] in manifest, f'{rid} 引用的 {im["image_id"]} 不在本卷 manifest')
            e = manifest[im['image_id']]
            check(im['path'] == e['path'] and im['transcription'] == e['transcription'] and im['path'] in md
                  and im['method'] == e['method'], f'{im["image_id"]} 与 manifest 或 Markdown 不符')
            used.add(im['image_id'])
    for target in re.findall(r'\]\(([^)]+)\)', md):
        if not target.startswith(('http', '#')):
            check((OUT / urllib.parse.unquote(target)).exists(), f'{paper}.md 链接失效：{target}')
    zf = zipfile.ZipFile(REPO / cfg['question_docx']) if cfg.get('question_docx') else None
    for aid, e in manifest.items():
        check(e['paper_id'] == paper and aid.startswith(paper + '-'), f'{aid} 不属于 {paper}')
        raw = (OUT / e['path']).read_bytes()
        check(raw[:8] == b'\x89PNG\r\n\x1a\n' and hashlib.sha256(raw).hexdigest() == e['sha256'], f'{aid} SHA-256 不符')
        check(png_size(raw) == (e['width'], e['height']), f'{aid} 像素尺寸不符')
        if e['method'] == 'docx_original':
            check(zf is not None and e['source_page'] is None and e['source_bbox_points'] is None, f'{aid} Word 原图的登记不符')
            check(hashlib.sha256(zf.read(e['source_file'])).hexdigest() == e['sha256'], f'{aid} 与源文档中的 {e["source_file"]} 不是同一文件')
        else:
            bb = e['source_bbox_points']
            check(abs((bb[2] - bb[0]) * SCALE - e['width']) <= 1 and abs((bb[3] - bb[1]) * SCALE - e['height']) <= 1,
                  f'{aid} 像素与裁剪框不符')
        check(aid in used, f'{aid} 未被任何题目引用')
    on_disk = {str(x.relative_to(OUT)) for x in f['assets'].glob('*') if x.name != 'manifest.json'}
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
    d.add_argument('--with-inline', action='store_true', help='套用修正文件中的行内小图文字')
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
        cmd_dump(a.paper, raw=not a.with_inline)
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

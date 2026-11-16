"""按题库保存的逐行坐标（source_spans），恢复转写时并掉的分段与换行。只动空白，不动文字。

- 资料文字：原卷每段首行缩进两字（行首x≈90pt，普通行≈68pt）。按行宽估出每行字数，找到段末所在位置，
  落到最近的句末标点后分段。
- 题干设问：原卷设问常单独成行，转写并进了上一句。若某行的宽度与设问句的估计宽度相符、上一行未排满，
  就在设问句前换行。
"""
import re

INDENT_X = 85.0      # 行首x大于此值视为段首缩进
LEFT_X = 72.0        # 普通行首
RIGHT_FULL = 500.0   # 行尾x大于此值视为排满

def char_w(ch, cw):
    if ch in "  ":
        return 0.25 * cw
    if ord(ch) < 0x2000 or ch in "−–":
        return 0.5 * cw
    return cw

def text_width(s, cw):
    return sum(char_w(c, cw) for c in s)

def estimate_cw(lines):
    """取排满的行估字宽：版心宽约 448pt / 38字。"""
    return 11.8

def _consume(text, lines, cw):
    pos, ends = 0, []
    for b in lines:
        width = b[2] - b[0]
        acc, j = 0.0, pos
        while j < len(text) and acc + char_w(text[j], cw) <= width + 0.45 * cw:
            acc += char_w(text[j], cw)
            j += 1
        ends.append(j)
        pos = j
    return ends

def calibrate_cw(text, lines):
    """找一个字宽，使各行恰好用完全部文字（字号随卷而异，约10.5—12pt）。"""
    lo, hi = 8.0, 14.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if _consume(text, lines, mid)[-1] < len(text):
            hi = mid          # 字宽估大了，装不下
        else:
            lo = mid
    return lo

def split_paragraphs(text, lines, cw=None):
    """text: 不含换行的整段文字；lines: 这段文字对应的各行bbox（按阅读顺序）。返回分段后的文字列表。"""
    if not lines:
        return [text]
    starts = [i for i, b in enumerate(lines) if b[0] > INDENT_X]
    if not starts or starts == [0] and len(lines) == 1:
        return [text]
    cw = cw or calibrate_cw(text, lines)
    ends = _consume(text, lines, cw)
    cut = []
    for i in starts:
        if i == 0:
            continue
        k = ends[i - 1]                      # 上一行末尾＝上一段末尾
        best = None
        for d in range(0, 12):
            for kk in (k - d, k + d):
                if 0 < kk <= len(text) and text[kk - 1] in "。！？；：”）":
                    best = kk
                    break
            if best:
                break
        if best:
            cut.append(best)
    out, last = [], 0
    for c in sorted(set(cut)):
        if c > last:
            out.append(text[last:c])
            last = c
    out.append(text[last:])
    return [p for p in out if p]

def split_question_line(stem, spans):
    """设问句在原卷单独成行、转写时并进上一句的，在设问句前加换行。

    条件（都要满足）：某行从左边界起排、宽度与设问句相符，上一行没有排满，
    且此前各行的总宽度与设问句之前的文字宽度相符。返回(新题干, 设问句或None)。
    """
    last = stem.rsplit("\n", 1)[-1]
    m = re.search(r"(?<=[。！？；”])([^。！？；”\n]{4,70}(?:？|：|（\s*）。?|\(\s*\)。?))$", last)
    if not m:
        return stem, None
    q = m.group(1)
    head = stem[: len(stem) - len(q)]
    head_last = head.rsplit("\n", 1)[-1]
    head_lines_before = head.count("\n")
    for cw in [x / 10 for x in range(100, 126, 2)]:
        qw = text_width(q, cw)
        for i in range(1, len(spans)):
            b, prev = spans[i], spans[i - 1]
            w = b[2] - b[0]
            if b[0] > LEFT_X or prev[2] > RIGHT_FULL or abs(w - qw) > 1.0 * cw:
                continue
            # 此前各行宽度之和应与设问前文字相当（首行含题号约两字宽）
            before = sum(x[2] - x[0] for x in spans[:i])
            need = text_width(head.replace("\n", ""), cw) + 2 * cw
            if abs(before - need) <= (2.5 + head_lines_before) * cw:
                return head + "\n" + q, q
    return stem, None

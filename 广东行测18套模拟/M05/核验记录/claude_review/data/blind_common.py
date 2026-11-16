# -*- coding: utf-8 -*-
"""盲解公用工具：只读取工作目录下的 blind_input.json（不读仓库其他任何文件）。

- 所有数值从 blind_input.json 的材料文本/表格中按字符串取出，转为 Fraction 精确计算；
- 舍入稳健性：显示值按其末位 ±0.5 单位取区间，对所有变量取角点（2^n 组合）求结果范围，
  并检查"最接近选项/判断结论"在所有角点是否不变（本卷涉及的函数在区间内对各变量单调，角点即极值）。
"""
import itertools
import json
import os
import re
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
BLIND = json.load(open(os.path.join(HERE, "blind_input.json"), encoding="utf-8"))
BYNUM = {q["number"]: q for q in BLIND}


def q(num):
    return BYNUM[num]


def material_blocks(num):
    out = []
    for m in q(num)["materials"]:
        out.extend(m["blocks"])
    return out


def material_text(num):
    return "\n".join(b["text"] for b in material_blocks(num) if b["type"] == "text")


def tables(num):
    return [b for b in material_blocks(num) if b["type"] == "table"]


def norm_num(s):
    s = s.strip().replace("−", "-").replace("％", "%").replace(",", "")
    return s


def frac(s):
    """'93.3%' -> Fraction(933,1000)；'−55' -> -55；'4.9' -> 49/10。"""
    s = norm_num(s)
    pct = s.endswith("%")
    if pct:
        s = s[:-1]
    v = F(s)
    return v / 100 if pct else v


def half_unit(s):
    """显示值末位的半个单位（同 frac 的量纲；百分数按百分比换算成小数）。"""
    s = norm_num(s)
    pct = s.endswith("%")
    if pct:
        s = s[:-1]
    d = len(s.split(".")[1]) if "." in s else 0
    h = F(5, 10 ** (d + 1))
    return h / 100 if pct else h


def find_in_text(num, pattern, group=1):
    """在材料文本中用正则取一个数字字符串（返回原字符串，便于记录显示精度）。"""
    t = material_text(num)
    m = re.search(pattern, t)
    if not m:
        raise ValueError("pattern not found: %s" % pattern)
    return m.group(group)


def table_dict(num, ti=0, key_col=0):
    t = tables(num)[ti]
    d = {}
    for r in t["rows"]:
        d[r[key_col]] = r
    return t["headers"], d


def corners(spec, func):
    """spec: {name: display_string or (value Fraction, halfwidth Fraction)}；
    func(env) -> Fraction / number。返回 (center, min, max, [all corner results])。"""
    names = list(spec)
    vals = {}
    for n in names:
        s = spec[n]
        if isinstance(s, tuple):
            vals[n] = s
        else:
            vals[n] = (frac(s), half_unit(s))
    center = func({n: vals[n][0] for n in names})
    res = []
    for signs in itertools.product((-1, 1), repeat=len(names)):
        env = {n: vals[n][0] + sg * vals[n][1] for n, sg in zip(names, signs)}
        res.append(func(env))
    return center, min(res), max(res), res


def nearest(x, options):
    """options: {letter: Fraction}；返回最接近的字母（并列时返回列表）。"""
    ds = {k: abs(F(x) - F(v)) for k, v in options.items()}
    m = min(ds.values())
    ks = [k for k, d in ds.items() if d == m]
    return ks[0] if len(ks) == 1 else ks


def opt_vals(num):
    """把文字选项中的数字（如 '861.1'、'6.5%'）解析为 Fraction。"""
    out = {}
    for k, v in q(num)["options"].items():
        txt = "".join(b.get("text", "") for b in v)
        out[k] = frac(txt)
    return out


def fx(x, n=6):
    return "%.*f" % (n, float(x))


def pct(x, n=4):
    return "%.*f%%" % (n, float(x) * 100)


def robust_nearest(spec, func, options, label=""):
    c, lo, hi, res = corners(spec, func)
    near_c = nearest(c, options)
    nears = sorted(set(str(nearest(r, options)) for r in res))
    lines = [
        "%s 中心值=%s  角点范围=[%s, %s]" % (label, fx(c), fx(lo), fx(hi)),
        "  最接近选项(中心)=%s；各角点最接近选项集合=%s → %s"
        % (near_c, nears, "稳健" if len(nears) == 1 else "不稳健"),
    ]
    return c, lo, hi, near_c, len(nears) == 1, "\n".join(lines)

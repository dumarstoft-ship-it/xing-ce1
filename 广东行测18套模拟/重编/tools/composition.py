"""逐题题型统计，与近三年广东真题范围（题型参照_2024-2026.md）对照。

范围是参照，不是配额：差一两道无妨；真题每年都有的类型（★）每套都要有。
"""
import re

# (部分, 类别, 下限, 上限, 每年都有)
RANGES = [
    ("言语", "逻辑填空-单空", 1, 3, True), ("言语", "逻辑填空-多空", 2, 4, True), ("言语", "主旨意图", 3, 6, True),
    ("言语", "细节判断", 0, 2, False), ("言语", "标题", 0, 1, False), ("言语", "语句填空", 1, 2, True),
    ("言语", "语句排序", 1, 2, True), ("言语", "词句理解、接语", 0, 0, False),
    ("数学运算", "和差倍比方程", 2, 3, True), ("数学运算", "行程", 1, 1, True), ("数学运算", "工程", 1, 1, True),
    ("数学运算", "最值与构造", 1, 1, True), ("数学运算", "排列组合与概率", 1, 2, True), ("数学运算", "经济利润", 0, 1, False),
    ("数学运算", "几何", 0, 1, False), ("数学运算", "杂题", 1, 2, False), ("数学运算", "浓度、容斥", 0, 0, False),
    ("图形推理", "规律类", 2, 3, True), ("图形推理", "空间类", 2, 3, True), ("图形推理", "拼合", 1, 1, True),
    ("图形推理", "截面", 0, 0, False), ("图形推理", "字符串", 0, 0, False),
    ("逻辑判断", "翻译推理", 0, 2, False), ("逻辑判断", "分析推理", 2, 3, True), ("逻辑判断", "真假推理", 0, 0, False),
    ("逻辑判断", "削弱", 1, 2, True), ("逻辑判断", "加强", 1, 2, True), ("逻辑判断", "前提假设", 2, 3, True),
    ("逻辑判断", "论证缺陷与评价", 0, 1, False), ("逻辑判断", "解释", 2, 3, True), ("逻辑判断", "结构比较", 3, 3, True),
    ("逻辑判断", "归纳结论", 0, 0, False),
    ("科学推理", "力学", 1, 2, True), ("科学推理", "电学", 1, 1, True), ("科学推理", "化学", 0, 1, False),
    ("科学推理", "生物", 1, 1, True), ("科学推理", "地理", 1, 1, True), ("科学推理", "光热声及其他", 0, 0, False),
    ("资料分析", "比较排序", 3, 3, True), ("资料分析", "比重", 2, 5, True), ("资料分析", "增长量", 1, 3, True),
    ("资料分析", "现期量与简单计算", 1, 2, True), ("资料分析", "综合分析判断", 2, 5, True), ("资料分析", "材料理解", 2, 5, True),
    ("资料分析", "增长率", 0, 4, False), ("资料分析", "基期量", 0, 1, False), ("资料分析", "倍数", 0, 1, False),
    ("资料分析", "平均数", 0, 1, False), ("资料分析", "图形选项", 0, 1, False),
]


def norm_label(part, label):
    """把逐题归类（解题记录、言语选题）归到参照表的类别名；一题可计入多类（如拼合同时是空间类）。"""
    L = label or ""
    if part == "言语":
        if L.startswith("逻辑填空"):
            return ["逻辑填空-单空" if "单空" in L else "逻辑填空-多空"]
        if L.startswith("语句排序"):
            return ["语句排序"]
        if L.startswith(("词句理解", "接语")):
            return ["词句理解、接语"]
        for k in ("主旨意图", "细节判断", "标题", "语句填空"):
            if L.startswith(k):
                return [k]
        return [L]
    if part == "数学运算":
        for k in ["和差倍比方程", "行程", "工程", "最值与构造", "排列组合与概率", "经济利润", "几何", "杂题"]:
            if k in L:
                return [k]
        if "浓度" in L or "容斥" in L:
            return ["浓度、容斥"]
        return [L]
    if part == "图形推理":
        out = []
        if "规律" in L:
            out.append("规律类")
        if "空间" in L:
            out.append("空间类")
        if "拼合" in L:
            out.append("拼合")
        if "截面" in L:
            out.append("截面")
        if "字符串" in L:
            out.append("字符串")
        return out
    if part == "逻辑判断":
        for k in ["翻译推理", "分析推理", "真假推理", "削弱", "加强", "前提假设", "解释", "结构比较", "归纳结论"]:
            if k in L:
                return [k]
        if "缺陷" in L or "评价" in L:
            return ["论证缺陷与评价"]
        return [L]
    if part == "科学推理":
        for k in ["力学", "电学", "化学", "生物", "地理", "光热声"]:
            if k in L:
                return ["光热声及其他" if k == "光热声" else k]
        return [L]
    if part == "资料分析":
        for k in ["比较排序", "比重", "增长量", "现期量", "综合分析", "材料理解", "增长率", "基期量", "倍数", "平均数", "图形选项"]:
            if k in L:
                return [{"现期量": "现期量与简单计算", "综合分析": "综合分析判断"}.get(k, k)]
        return [L]
    return [L]


def part_of(n):
    if 16 <= n <= 30:
        return "言语"
    if 36 <= n <= 45:
        return "数学运算"
    if 46 <= n <= 50:
        return "图形推理"
    if 51 <= n <= 65:
        return "逻辑判断"
    if 66 <= n <= 70:
        return "科学推理"
    if n >= 71:
        return "资料分析"
    return None


def table(labels):
    """labels: {题号: 归类文字}。返回 [(部分, 类别, 本卷数, 范围文字, 判定, 题号列表)]。"""
    hits = {}
    for n, lab in labels.items():
        part = part_of(n)
        if not part:
            continue
        for c in norm_label(part, lab):
            hits.setdefault((part, c), []).append(n)
    rows = []
    for part, cat, lo, hi, every in RANGES:
        ns = sorted(hits.get((part, cat), []))
        k = len(ns)
        rng = f"{lo}" if lo == hi else f"{lo}—{hi}"
        if every:
            rng += "★"
        if every and k == 0:
            verdict = "缺"
        elif k < lo:
            verdict = f"少{lo - k}"
        elif k > hi:
            verdict = f"多{k - hi}"
        else:
            verdict = "√"
        rows.append((part, cat, k, rng, verdict, ns))
    known = {(p, c) for p, c, *_ in RANGES}
    for (part, cat), ns in sorted(hits.items()):
        if (part, cat) not in known:
            rows.append((part, cat, len(ns), "—", "未归类", sorted(ns)))
    return rows

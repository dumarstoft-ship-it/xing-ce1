"""第68题：一对表现正常的父母生出患病女儿，判断遗传方式。
对四种遗传方式，枚举父母所有可能的基因型，看“父母都正常”时能否生出患病女儿。
"""
from itertools import product

def autosomal(dominant):
    genos = ["AA", "Aa", "aa"]
    def affected(g):
        return ("A" in g) if dominant else (g == "aa")
    res = []
    for f, m in product(genos, genos):
        if affected(f) or affected(m):
            continue
        for gf, gm in product(f, m):
            child = "".join(sorted(gf + gm))
            if affected(child):
                res.append((f, m, child))
    return res

def xlinked(dominant):
    fathers = ["XAY", "XaY"]
    mothers = ["XAXA", "XAXa", "XaXa"]
    def aff_f(g):
        return ("XA" in g) if dominant else (g == "XaY")
    def aff_m(g):
        return ("XA" in g) if dominant else (g == "XaXa")
    res = []
    for f, m in product(fathers, mothers):
        if aff_f(f) or aff_m(m):
            continue
        fx = f[:2]  # 父亲传给女儿的X
        for mx in (m[:2], m[2:]):
            daughter = "".join(sorted([fx, mx], reverse=True))
            if aff_m(daughter):
                res.append((f, m, daughter))
    return res

modes = {
    "A 常染色体隐性": autosomal(False),
    "B 常染色体显性": autosomal(True),
    "C 伴X隐性": xlinked(False),
    "D 伴X显性": xlinked(True),
}
for k, v in modes.items():
    print(k, "：父母正常而女儿患病的组合", sorted(set(v)) if v else "不存在")
assert modes["A 常染色体隐性"] and not modes["B 常染色体显性"] and not modes["C 伴X隐性"] and not modes["D 伴X显性"]
print("答案: A")

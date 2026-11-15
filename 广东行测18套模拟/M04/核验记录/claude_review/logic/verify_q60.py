#!/usr/bin/env python3
"""M04 第60题 穷举验证（只依据题本可见内容）。

形式化：
  人员 P = {甲, 乙, 丙, 丁}；身高 h: P → {1.65, 1.68, 1.70, 1.72} 为双射（“有身高为……的四人”）。
  体型 thin(p) ∈ {瘦, 胖}，恰好 2 瘦 2 胖。
  规则：瘦者陈述为真，胖者陈述为假：  thin(p) ↔ S_p 为真。
  S_甲: h(甲) < 1.70
  S_乙: h(丙) = 1.72 ∧ thin(丙)
  S_丙: h(丁) = 1.68 ∧ ¬thin(丁)
  S_丁: h(乙) = 1.65 ∧ thin(乙)
  标准解读（standard）：合取命题为假 ⇔ 至少一个合取支为假。
  对照解读（strict）：说假话者的陈述“每一个分句都假”（非标准，用来检验题目是否依赖解读）。

运行：python3 verify_q60.py
"""
from itertools import permutations, combinations

P = ["甲", "乙", "丙", "丁"]
H = [165, 168, 170, 172]  # 单位：厘米，避免浮点比较


def clauses(h, thin):
    """返回每人陈述的分句真值列表。"""
    return {
        "甲": [h["甲"] < 170],
        "乙": [h["丙"] == 172, thin["丙"]],
        "丙": [h["丁"] == 168, not thin["丁"]],
        "丁": [h["乙"] == 165, thin["乙"]],
    }


def solve(mode):
    sols = []
    for perm in permutations(H):
        h = dict(zip(P, perm))
        for thin_set in combinations(P, 2):
            thin = {p: (p in thin_set) for p in P}
            cl = clauses(h, thin)
            ok = True
            for p in P:
                if thin[p]:
                    ok &= all(cl[p])
                else:
                    if mode == "standard":
                        ok &= not all(cl[p])
                    else:  # strict
                        ok &= not any(cl[p])
            if ok:
                sols.append((h, thin))
    return sols


OPTIONS = {
    "A": ("甲", 165, False),
    "B": ("乙", 170, True),
    "C": ("丙", 172, True),
    "D": ("丁", 168, False),
}

if __name__ == "__main__":
    for mode in ("standard", "strict"):
        sols = solve(mode)
        print(f"[{mode}] {len(sols)} 个解")
        for h, thin in sols:
            print("   ", "  ".join(f"{p}:{h[p]/100:.2f}{'瘦' if thin[p] else '胖'}" for p in P))
            for k, (p, hh, th) in OPTIONS.items():
                print(f"      选项{k}: {p}身高{hh/100:.2f}、{'偏瘦' if th else '偏胖'} -> {h[p] == hh and thin[p] == th}")
    std = solve("standard")
    assert len(std) == 1
    h, thin = std[0]
    good = [k for k, (p, hh, th) in OPTIONS.items() if h[p] == hh and thin[p] == th]
    assert good == ["D"], good
    print("结论：标准解读下唯一解，且仅选项 D 成立；严格解读（假话每句都假）下无解，题目不依赖该非标准解读。")

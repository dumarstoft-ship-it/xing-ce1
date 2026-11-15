#!/usr/bin/env python3
"""M04 第57题：投诉率口径对“最不能解释”答案的影响（玩具数值模型）。

目的：说明 GPT 对源题“该市同期关于餐饮消费的投诉率”所做的 clarify_denominator 改写是否必要。
记号：V = 餐饮消费人次；Dc = 餐饮类投诉量；Oc = 其他类投诉量。
各选项的作用（只取选项字面给出的机制，不额外加条件）：
  A 游客涌入，消费基数增大→投诉绝对数增加：V×k，Dc×k（与基数同比例），Oc 不变
  B 菜品质量下降：每次消费引发投诉的概率上升：Dc×q
  C 投诉渠道更便捷、人们更愿维权：所有类别投诉同比例上升：Dc×c，Oc×c
  D 隐性收费引发争议：Dc×d
三种口径：
  (i)   餐饮投诉量 / 餐饮消费人次           —— 编辑稿口径（明示分母）
  (ii)  餐饮投诉量 / 全部投诉量              —— 源题“关于餐饮消费的投诉率”的另一种可读法
  (iii) 全部投诉量 / 餐饮消费人次           —— 编辑稿分子未写“餐饮”时的字面极端读法
判定：某选项“能解释”⇔ 该口径下比率上升。
运行：python3 verify_q57_denominator.py
"""
V, Dc, Oc = 10000.0, 100.0, 300.0
k, q, c, d = 1.5, 1.3, 1.3, 1.3

effects = {
    "A": dict(V=V * k, Dc=Dc * k, Oc=Oc),
    "B": dict(V=V, Dc=Dc * q, Oc=Oc),
    "C": dict(V=V, Dc=Dc * c, Oc=Oc * c),
    "D": dict(V=V, Dc=Dc * d, Oc=Oc),
}
readings = {
    "(i) 餐饮投诉/餐饮人次": lambda s: s["Dc"] / s["V"],
    "(ii) 餐饮投诉/全部投诉": lambda s: s["Dc"] / (s["Dc"] + s["Oc"]),
    "(iii) 全部投诉/餐饮人次": lambda s: (s["Dc"] + s["Oc"]) / s["V"],
}
base = dict(V=V, Dc=Dc, Oc=Oc)
for name, f in readings.items():
    r0 = f(base)
    cannot = []
    parts = []
    for opt, s in effects.items():
        r1 = f(s)
        explains = r1 > r0 * (1 + 1e-12)
        parts.append(f"{opt}:{'能' if explains else '不能'}({r1 / r0:.3f}×)")
        if not explains:
            cannot.append(opt)
    print(f"{name}: " + "  ".join(parts) + f"  → 最不能解释: {cannot}")
print("结论：源题口径若读作(ii)，答案会变成C；编辑稿明示分母为餐饮消费人次后，(i)(iii)均唯一选A，改写必要且不改变原题考点。")

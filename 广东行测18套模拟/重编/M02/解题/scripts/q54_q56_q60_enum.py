"""第54、56、60题核验：枚举所有情形。"""
from itertools import product, permutations

imp = lambda a, b: (not a) or b

print("== 第54题 ==")
names = ["冯", "陈", "楚", "魏", "周", "吴", "郑"]
sols = []
for v in product([False, True], repeat=7):
    f, c, chu, wei, zhou, wu, zheng = v
    c1 = (zhou and wu) != (wu and zheng)          # 要么(周且吴)，要么(吴且郑)：恰有一项成立
    c2 = imp(zheng or (not wu), f and chu)          # 只有冯且楚，才 郑或非吴
    c3 = imp(c or wu, wei and not chu)              # 陈或吴 → 魏且非楚
    if c1 and c2 and c3:
        sols.append(dict(zip(names, v)))
print("满足条件的情形数：", len(sols))
for n in names:
    vals = {s[n] for s in sols}
    print(n, "一定通知" if vals == {True} else ("一定不通知" if vals == {False} else "不确定"))
# 对照：若把“要么…要么…”理解为相容的“或”
sols2 = []
for v in product([False, True], repeat=7):
    f, c, chu, wei, zhou, wu, zheng = v
    if ((zhou and wu) or (wu and zheng)) and imp(zheng or (not wu), f and chu) and imp(c or wu, wei and not chu):
        sols2.append(dict(zip(names, v)))
print("对照（相容或）：", {n: sorted({s[n] for s in sols2}) for n in names})

print("== 第56题 ==")
people = ["甲", "乙", "丙", "丁", "戊"]
courses = ["地理", "鉴赏", "急救", "历史"]
ok = []
for a in product(courses, repeat=5):
    s = dict(zip(people, a))
    st = [
        s["甲"] == "地理",
        s["乙"] == s["丁"],
        not (s["丙"] == "鉴赏" and s["丁"] == "鉴赏"),
        s["甲"] != "急救" or s["丙"] != "历史",
        s["乙"] != "鉴赏",
    ]
    if sum(st) == 1:
        ok.append((s, st.index(True)))
print("只有一人猜对的选课情形数：", len(ok), "；猜对的人：", sorted({people[i] for _, i in ok}))
print("确定的选课：", {p: sorted({s[p] for s, _ in ok}) for p in people})
opts = {
    "A 有人选地理": lambda s: "地理" in s.values(),
    "B 没人选地理": lambda s: "地理" not in s.values(),
    "C 乙、丙都不选急救": lambda s: s["乙"] != "急救" and s["丙"] != "急救",
    "D 乙、丁都不选鉴赏": lambda s: s["乙"] != "鉴赏" and s["丁"] != "鉴赏",
}
for k, f in opts.items():
    print(k, "一定为真" if all(f(s) for s, _ in ok) else "不一定")
# 对照：若要求四门课都有人选
ok4 = [(s, i) for s, i in ok if set(s.values()) == set(courses)]
print("对照（四门课都要有人选）情形数：", len(ok4),
      {k: all(f(s) for s, _ in ok4) for k, f in opts.items()})

print("== 第60题 ==")
members = ["小李", "小赵", "小钱"]
res = []
for g in permutations(["大一", "大二", "大三"]):
    for m in permutations(["文学", "数学", "计算机"]):
        G = dict(zip(members, g)); M = dict(zip(members, m))
        # (1) 存在“大一且数学”的成员，且不是小李（小李与其是好友）
        fresh_math = [p for p in members if G[p] == "大一" and M[p] == "数学"]
        c1 = len(fresh_math) == 1 and fresh_math[0] != "小李"
        # (2) 小钱年级最高；小钱与计算机专业的成员共同演出 → 小钱不是计算机专业
        c2 = G["小钱"] == "大三" and M["小钱"] != "计算机"
        if c1 and c2:
            res.append({p: G[p] + M[p] for p in members})
print("唯一解：", res)

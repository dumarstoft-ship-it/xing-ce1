"""第56题枚举：5人分到综合/执法/服务3岗，每岗1-2人。
(2) 甲不在综合 -> 乙在执法；(3) 丙、戊不同岗；(4) 执法人数 > 服务人数；附加：丁在服务。
"""
import itertools

people = "甲乙丙丁戊"
posts = ["综合", "执法", "服务"]
sols = []
for assign in itertools.product(posts, repeat=5):
    a = dict(zip(people, assign))
    cnt = {p: assign.count(p) for p in posts}
    if any(not (1 <= cnt[p] <= 2) for p in posts):
        continue
    if a["甲"] != "综合" and a["乙"] != "执法":
        continue
    if a["丙"] == a["戊"]:
        continue
    if not cnt["执法"] > cnt["服务"]:
        continue
    if a["丁"] != "服务":
        continue
    sols.append(a)

print("满足条件的分配数:", len(sols))
for s in sols:
    print("  ", s)
opts = {
    "A 甲在综合岗": lambda a: a["甲"] == "综合",
    "B 乙不在执法岗": lambda a: a["乙"] != "执法",
    "C 丙在执法岗": lambda a: a["丙"] == "执法",
    "D 戊不在综合岗": lambda a: a["戊"] != "综合",
}
for k, f in opts.items():
    print(k, "一定为真" if all(f(s) for s in sols) else "不一定")

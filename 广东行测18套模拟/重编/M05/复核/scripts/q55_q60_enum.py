"""Q55 and Q60: brute-force enumeration."""
import itertools

# ---------------- Q55 ----------------
people = ["甲", "乙", "丙", "丁", "戊"]
courses = ["绘画", "书法", "舞蹈", "唱歌", "陶艺"]
pairs = [frozenset(p) for p in itertools.combinations(courses, 2)]
sols = []
for assign in itertools.product(pairs, repeat=5):
    a = dict(zip(people, assign))
    if any(sum(c in s for s in assign) != 2 for c in courses):
        continue                                            # each course exactly 2 people
    if a["甲"] & {"绘画", "舞蹈"}: continue                 # ①
    if a["乙"] & a["丙"] or "陶艺" in a["丙"]: continue     # ②
    if "书法" in a["丁"] or len(a["丁"] & a["戊"]) != 1: continue  # ③
    if "唱歌" in a["戊"] or a["戊"] & a["甲"]: continue     # ④
    if a["乙"] != frozenset({"书法", "绘画"}): continue     # ⑤
    sols.append(a)
print("Q55 solutions:", len(sols))
for s in sols:
    print("   ", {p: "+".join(sorted(s[p], key=courses.index)) for p in people})
checks = {
    "A 甲报陶艺": lambda s: "陶艺" in s["甲"],
    "B 丙报绘画": lambda s: "绘画" in s["丙"],
    "C 丁报舞蹈": lambda s: "舞蹈" in s["丁"],
    "D 戊报陶艺": lambda s: "陶艺" in s["戊"],
}
for k, f in checks.items():
    print(f"   {k}: always={all(f(s) for s in sols)} sometimes={any(f(s) for s in sols)}")

# ---------------- Q60 ----------------
names = ["小红", "小明", "小丽", "小强"]
good = []
for hats in itertools.product("RB", repeat=4):
    h = dict(zip(names, hats))
    seen = lambda me: [h[n] for n in names if n != me]
    st = {
        "小红": seen("小红").count("R") == 2 and seen("小红").count("B") == 1,
        "小明": seen("小明").count("B") == 3,
        "小丽": seen("小丽").count("R") == 3,
    }
    if all((h[p] == "R") == st[p] for p in st):   # red tells truth, blue lies
        good.append(h)
print("\nQ60 consistent assignments:", good)
print("   小强 colours possible:", sorted({g["小强"] for g in good}))
print("   小强 same colour as 小明 in all solutions?", all(g["小强"] == g["小明"] for g in good),
      "| in any?", any(g["小强"] == g["小明"] for g in good))

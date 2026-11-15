"""Blind brute-force checks for M02 Q51/53/56/59/62 (written before seeing any key)."""
from itertools import permutations, product

def hr(t):
    print("\n" + "=" * 8 + " " + t + " " + "=" * 8)

# ---------------- Q51 ----------------
hr("Q51 propositional: premise  fly -> (strong & joint)")
# variables: s = 两翼健壮, j = 共同力量推动, f = 飞向天空
def premise51(s, j, f):
    return (not f) or (s and j)          # 除非(s∧j)否则不f  ==  ¬(s∧j) → ¬f  ==  f → (s∧j)
stmts51 = {
    "①": lambda s, j, f: (not (s and j)) or f,          # (s∧j) → f
    "②": lambda s, j, f: (not f) or (s and j),          # f → (s∧j)
    "③": lambda s, j, f: (not ((not s) or (not j))) or (not f),  # (¬s∨¬j) → ¬f
    "④": lambda s, j, f: f or ((not s) or (not j)),     # ¬f → (¬s∨¬j)
}
valid51 = []
for k, fn in stmts51.items():
    ok = all(fn(s, j, f) for s, j, f in product([0, 1], repeat=3) if premise51(s, j, f))
    print(k, "entailed" if ok else "NOT entailed")
    if ok:
        valid51.append(k)
opts51 = {"A": "①②", "B": "②③", "C": "③④", "D": "②④"}
print("entailed set:", valid51, "-> option(s):", [o for o, v in opts51.items() if set(v) == set(valid51)])

# ---------------- Q53 ----------------
hr("Q53 shelf arrangement")
albums = "ABCDEF"
singer = {"A": "甲", "B": "甲", "C": "乙", "D": "乙", "E": "丙", "F": "丙"}
def base53(pos):   # pos: album -> shelf (1..6)
    adj = lambda x, y: abs(pos[x] - pos[y]) == 1
    if adj("A", "C"): return False
    if adj("F", "C"): return False
    ends = [a for a in "AB" if pos[a] in (1, 6)]
    return len(ends) == 1
all53 = []
for perm in permutations(range(1, 7)):
    pos = dict(zip(albums, perm))
    if base53(pos):
        all53.append(pos)
print("arrangements satisfying (1)-(3) overall:", len(all53))
cond = [p for p in all53 if p["C"] == 2 and p["E"] == 4]
for p in cond:
    print("  ", "".join(sorted(p, key=lambda a: p[a])))
opts53 = {"A": ("B", 1), "B": ("B", 5), "C": ("D", 5), "D": ("D", 6)}
for o, (a, s) in opts53.items():
    print(o, f"{a} at {s}:", "possible" if any(p[a] == s for p in cond) else "impossible")

# ---------------- Q56 ----------------
hr("Q56 exactly-one-true guess")
depts = ["人事", "财务", "办公"]
def truths56(a):  # a: (甲, 乙, 丙)
    return [a[0] == "人事", a[1] != "财务", a[2] != "人事"]
opts56 = {"A": ("人事", "财务", "办公"), "B": ("办公", "财务", "人事"),
          "C": ("财务", "办公", "人事"), "D": ("人事", "办公", "财务")}
print("-- with all-different (permutations):")
sol_perm = [a for a in permutations(depts) if sum(truths56(a)) == 1]
for a in permutations(depts):
    print("  ", a, truths56(a), "<-- solution" if a in sol_perm else "")
print("solutions:", sol_perm, "options matching:", [o for o, v in opts56.items() if v in sol_perm])
print("-- WITHOUT all-different (27 assignments):")
sol_free = [a for a in product(depts, repeat=3) if sum(truths56(a)) == 1]
print("count:", len(sol_free))
for a in sol_free:
    print("  ", a, truths56(a))
print("options consistent:", [o for o, v in opts56.items() if v in sol_free])
# also: 'each department taken by at least someone' is equivalent to permutation for 3 people/3 depts.

# ---------------- Q59 ----------------
hr("Q59 balloons")
people = ["明", "军", "花", "飞", "雅"]
balloons = [("红", "圆"), ("蓝", "星"), ("黄", "心"), ("蓝", "圆"), ("红", "心")]
def S_ming(a):  # 小花和小雅的气球都不是圆形的，也不是蓝色的
    return all(a[x][1] != "圆" and a[x][0] != "蓝" for x in ("花", "雅"))
def S_jun(a):   # 我的气球与小雅的颜色和形状都不一样
    return a["军"][0] != a["雅"][0] and a["军"][1] != a["雅"][1]
def S_fei(a):   # 小雅的气球是黄色的，小明的气球是蓝色的
    return a["雅"][0] == "黄" and a["明"][0] == "蓝"
def S_hua(a):   # 小军的气球与我的是一样的颜色，小飞的气球不是五角星形的
    return a["军"][0] == a["花"][0] and a["飞"][1] != "星"
S = {"明": S_ming, "军": S_jun, "飞": S_fei, "花": S_hua}
opts59 = {"A": ("军", ("红", "心")), "B": ("花", ("黄", "心")),
          "C": ("飞", ("红", "圆")), "D": ("明", ("蓝", "星"))}
def solve59(active):
    sols = []
    for perm in permutations(balloons):
        a = dict(zip(people, perm))
        if all(S[k](a) for k in active):
            sols.append(a)
    return sols
def show(sols):
    for a in sols:
        print("    ", {p: "".join(a[p]) for p in people})
for active in [("明", "军", "飞", "花"), ("明", "飞", "花"), ("军", "飞", "花"), ("明", "军", "花"), ("明", "军", "飞")]:
    sols = solve59(active)
    true_opts = [o for o, (p, b) in opts59.items() if sols and all(a[p] == b for a in sols)]
    poss_opts = [o for o, (p, b) in opts59.items() if any(a[p] == b for a in sols)]
    print(f"statements {active}: {len(sols)} solution(s); necessarily-true options {true_opts}; possible options {poss_opts}")
    if len(sols) <= 4:
        show(sols)
# Alternative reading check: could "我的气球与小雅的颜色和形状都不一样" be read as NOT(same colour AND same shape)? (trivially true since balloons distinct)
# Also check: if we suppose exactly one / exactly one false etc. -- reported for robustness only.
print("-- robustness: number of true statements per full assignment, for curiosity")
from collections import Counter
cnt = Counter()
for perm in permutations(balloons):
    a = dict(zip(people, perm))
    cnt[sum(S[k](a) for k in S)] += 1
print(cnt)

# ---------------- Q62 ----------------
hr("Q62 premise for 小苏 参加 剪纸")
# vars for 小苏: y=艺术阅读, b=版画, s=书法, j=剪纸 ; premises are universal but only matter for 小苏 here
def prem62(y, b, s, j):
    return (y or b) and ((not y) or (not s)) and s
opts62 = {
    "A": lambda y, b, s, j: not y,
    "B": lambda y, b, s, j: not b,
    "C": lambda y, b, s, j: (not j) or b,       # 剪 → 版
    "D": lambda y, b, s, j: j or (not b),       # ¬剪 → ¬版  ==  版 → 剪
}
models = [m for m in product([0, 1], repeat=4) if prem62(*m)]
print("models of premises alone:", models, "-> j always true?", all(m[3] for m in models))
for o, fn in opts62.items():
    ms = [m for m in models if fn(*m)]
    consistent = bool(ms)
    entails = all(m[3] for m in ms)
    print(o, "consistent with stem" if consistent else "CONTRADICTS stem (no model)",
          "| entails 剪纸:", "vacuously (ex falso)" if not consistent else entails)

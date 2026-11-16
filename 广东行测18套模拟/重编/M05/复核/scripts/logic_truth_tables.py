"""Truth-table checks for Q51, Q61, Q63, Q64 (formal logic)."""
import itertools

def entails(premises, conclusion, vars_):
    for vals in itertools.product((False, True), repeat=len(vars_)):
        e = dict(zip(vars_, vals))
        if all(p(e) for p in premises) and not conclusion(e):
            return False
    return True

imp = lambda a, b: (not a) or b

# ---- Q51 ----  S 智能化, N 新优势, U 整体升级, O 优化提升传统产业, T 技术改造, M 模式创新, J 结构优化
V51 = list("SNUOTMJ")
prem_necessary = [lambda e: imp(e["U"], e["O"]),                         # O 是 U 的必然选择 (必要条件)
                  lambda e: imp(e["O"], e["T"] and e["M"] and e["J"]),   # 只有TMJ才O
                  lambda e: imp(e["S"] or e["N"], e["U"])]               # S或N -> U
opts51 = {
  "A 若无新优势则无法优化提升": lambda e: imp(not e["N"], not e["O"]),
  "B 技术改造和模式创新是新优势的必要条件": lambda e: imp(e["N"], e["T"] and e["M"]),
  "C 除非整体升级否则没有TMJ": lambda e: imp(e["T"] and e["M"] and e["J"], e["U"]),
  "D 只要优化提升就能整体升级": lambda e: imp(e["O"], e["U"]),
}
print("Q51 (必然选择 = 必要条件):")
for k, f in opts51.items():
    print("   ", k, entails(prem_necessary, f, V51))
prem_suff = [lambda e: imp(e["O"], e["U"])] + prem_necessary[1:]
print("Q51 (sensitivity: if 必然选择 were read as 充分条件 O->U):")
for k, f in opts51.items():
    print("   ", k, entails(prem_suff, f, V51))

# ---- Q61 ---- structural comparison: each argument -> (major conditional, minor premise, conclusion)
def valid_form(major, minor, concl):
    # major = (antecedent literal, consequent literal); literals = (var, sign)
    lit = lambda e, l: e[l[0]] if l[1] else not e[l[0]]
    return entails([lambda e: imp(lit(e, major[0]), lit(e, major[1])), lambda e: lit(e, minor)],
                   lambda e: lit(e, concl), ["X", "Y"])
def canon(major, minor, concl):
    """rewrite major into contrapositive form if needed so that the minor premise matches antecedent or consequent literally"""
    forms = [major, ((major[1][0], not major[1][1]), (major[0][0], not major[0][1]))]
    out = []
    for a, c in forms:
        if minor == a: role = "affirm/deny antecedent(=MP)"
        elif minor == c: role = "minor = consequent"
        else: continue
        out.append(role)
    return out
X, nX, Y, nY = ("X", True), ("X", False), ("Y", True), ("Y", False)
args61 = {
  "stem 若非X则非Y; X; 故Y": ((nX, nY), X, Y),
  "A 若X则Y; X; 故Y":         ((X, Y), X, Y),
  "B 除非X否则非Y; Y; 故X":   ((nX, nY), Y, X),
  "C 只有X才Y(Y->X); X; 故非Y": ((Y, X), X, nY),
  "D 若X则Y; Y; 故X":         ((X, Y), Y, X),
}
print("\nQ61:")
for k, (mj, mn, cc) in args61.items():
    # normalise: express major as P->Q with minor premise == Q (affirming consequent) or == P (MP)
    contr = ((mj[1][0], not mj[1][1]), (mj[0][0], not mj[0][1]))
    shape = None
    for a, c in (mj, contr):
        if mn == c and cc == a: shape = "P->Q; Q; so P  (affirming consequent, invalid)"
        if mn == a and cc == c: shape = "P->Q; P; so Q  (modus ponens, valid)"
    if shape is None: shape = "other"
    print(f"   {k:28s} valid={valid_form(mj, mn, cc)}  shape={shape}")

# ---- Q63 ----  L 监管滞后, W 可能沦为凶器, F 织密法治之网, Z 科技创新真正造福人类
V63 = list("LWFZ")
prem63 = [lambda e: imp(e["L"], e["W"]), lambda e: imp(e["Z"], e["F"])]
opts63 = {
  "A 若非F则非Z": lambda e: imp(not e["F"], not e["Z"]),
  "B 只要F就Z": lambda e: imp(e["F"], e["Z"]),
  "C 若非L则非W": lambda e: imp(not e["L"], not e["W"]),
  "D 唯有F才非W": lambda e: imp(not e["W"], e["F"]),
}
print("\nQ63:")
for k, f in opts63.items():
    print("   ", k, entails(prem63, f, V63))

# ---- Q64 ---- each option: two premises + conclusion over P,Q,R
V64 = list("PQR")
def chk(p1, p2, c):
    return entails([p1, p2], c, V64)
P = lambda e: e["P"]; Q = lambda e: e["Q"]; R = lambda e: e["R"]
print("\nQ64:")
print("   stem  P->Q, Q->R => P->R :", chk(lambda e: imp(e["P"], e["Q"]), lambda e: imp(e["Q"], e["R"]), lambda e: imp(e["P"], e["R"])))
print("   A     P->Q, Q->R => R->P :", chk(lambda e: imp(e["P"], e["Q"]), lambda e: imp(e["Q"], e["R"]), lambda e: imp(e["R"], e["P"])))
print("   B     P->Q, Q->R => P->R :", chk(lambda e: imp(e["P"], e["Q"]), lambda e: imp(e["Q"], e["R"]), lambda e: imp(e["P"], e["R"])), "(conclusion stated first, '这是因为')")
print("   C     P->Q, Q->R => ~P->~R:", chk(lambda e: imp(e["P"], e["Q"]), lambda e: imp(e["Q"], e["R"]), lambda e: imp(not e["P"], not e["R"])))
print("   D     P->Q, Q->R => R->P :", chk(lambda e: imp(e["P"], e["Q"]), lambda e: imp(e["Q"], e["R"]), lambda e: imp(e["R"], e["P"])), "(P=垃圾分类,Q=整洁,R=幸福感; 结论 R->P)")

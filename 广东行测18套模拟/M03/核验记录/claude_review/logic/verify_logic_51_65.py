#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
M03 第51—65题（判断推理·逻辑判断）穷举/形式化核验脚本。

只依赖 Python 3 标准库，可独立重跑：
    python3 verify_logic_51_65.py

覆盖：
  Q51 真假话（三句两假）              —— 穷举真值
  Q53 专业/持书分配                   —— 穷举排列（含“删去‘四人的专业各不相同’”的对照）
  Q55 补前提（四类人数不等式）        —— 穷举小整数，找反例
  Q60 职业预言（只有会计师的预言对）  —— 穷举排列（含另一种读法的对照）
  Q61 / Q64 逻辑结构相似              —— 把题干和各选项形式化为命题公式，
                                        判断（a）推理是否有效；（b）在变量换名下，
                                        前提集合与结论是否逐条逻辑等价于题干
  Q63 录用人数                        —— 穷举 2^6 种录用方案

每题的形式化都写在对应函数的注释里。若对形式化有异议，改注释下面那几行即可重跑。
"""
from itertools import permutations, product

OPT = "ABCD"


def hr(title):
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


# ---------------------------------------------------------------------------
# 通用：真值表工具
# ---------------------------------------------------------------------------
def models(nvars):
    return list(product([False, True], repeat=nvars))


def equiv(f, g, nvars):
    return all(f(*m) == g(*m) for m in models(nvars))


def valid(premises, conclusion, nvars):
    """所有使前提全真的赋值下结论都真 -> 有效；返回 (是否有效, 反例赋值)"""
    for m in models(nvars):
        if all(p(*m) for p in premises) and not conclusion(*m):
            return False, m
    return True, None


def isomorphic(arg_opt, arg_stem):
    """
    结构相似判定（严格版）：存在一个变量换名（允许对变量取反，即“正负文字互换”），
    使选项的每个前提与题干的某个前提逻辑等价（前提一一对应），且结论逻辑等价。
    arg = (nvars, [premise_fn...], conclusion_fn, 变量名列表)
    返回匹配到的换名方案列表。
    """
    n1, P1, C1, _ = arg_opt
    n2, P2, C2, _ = arg_stem
    if n1 != n2 or len(P1) != len(P2):
        return []
    hits = []
    for perm in permutations(range(n2)):
        for neg in product([False, True], repeat=n2):
            # 选项变量 i  <->  题干变量 perm[i]（neg[i] 为 True 表示取反对应）
            def tr(fn):
                def g(*m):  # m 是题干变量赋值
                    args = [(not m[perm[i]]) if neg[i] else m[perm[i]] for i in range(n1)]
                    return fn(*args)
                return g
            if not equiv(tr(C1), C2, n2):
                continue
            used = set()
            ok = True
            for p in P1:
                found = False
                for j, q in enumerate(P2):
                    if j not in used and equiv(tr(p), q, n2):
                        used.add(j)
                        found = True
                        break
                if not found:
                    ok = False
                    break
            if ok:
                hits.append((perm, neg))
    return hits


imp = lambda a, b: (not a) or b
iff = lambda a, b: a == b


# ---------------------------------------------------------------------------
# Q51
# ---------------------------------------------------------------------------
def q51():
    hr("Q51 三个判断两假一真")
    # 变量：Q=小张学秦篆，W=小张学魏碑，H=小李学汉隶
    # (1) W -> H
    # (2) ¬Q ∧ ¬W
    # (3) Q ∨ W        （“或者……或者……”按公考惯例为相容选言）
    #     对照读法：Q ⊕ W（若误读为不相容选言）
    # 约束：三句中恰两句为假
    options = {
        "A": lambda Q, W, H: W and H,
        "B": lambda Q, W, H: (not W) and H,
        "C": lambda Q, W, H: W and (not H),
        "D": lambda Q, W, H: (not W) and (not H),
    }
    for label, s3 in [("相容选言（标准读法）", lambda Q, W: Q or W),
                      ("不相容选言（对照读法）", lambda Q, W: Q != W)]:
        sols = []
        for Q, W, H in models(3):
            s = [imp(W, H), (not Q) and (not W), s3(Q, W)]
            if s.count(False) == 2:
                sols.append((Q, W, H, s))
        print(f"\n[{label}] 满足“两假一真”的赋值：")
        for Q, W, H, s in sols:
            print(f"   秦篆={Q!s:5} 魏碑={W!s:5} 汉隶={H!s:5}  三句真值={s}")
        ent = [k for k, f in options.items() if all(f(Q, W, H) for Q, W, H, _ in sols)]
        con = [k for k, f in options.items() if any(f(Q, W, H) for Q, W, H, _ in sols)]
        print(f"   必然为真的选项：{ent}；可能为真的选项：{con}")


# ---------------------------------------------------------------------------
# Q53
# ---------------------------------------------------------------------------
def q53():
    hr("Q53 专业与持书")
    P = ["甲", "乙", "丙", "丁"]
    M = ["文", "经", "历", "社"]
    # 形式化（题本版）：
    #   major: 四人到四专业的双射（“四人的专业各不相同”）
    #   每人带一本本专业书 -> 四本书分属四专业
    #   hold : 交换后四人到四本书（按专业标记）的双射
    #   (1) major[丙]=历，major[丁]=文
    #   (2) hold[甲]=社，hold[乙]≠文
    #   (3) 对每人 hold[x] ≠ major[x]
    # “交换”按一般重新分配理解（非两两对调）；对两两对调读法另作对照。
    def solve(require_pairwise=False):
        sols = []
        for mj in permutations(M):
            major = dict(zip(P, mj))
            if major["丙"] != "历" or major["丁"] != "文":
                continue
            for hd in permutations(M):
                hold = dict(zip(P, hd))
                if hold["甲"] != "社" or hold["乙"] == "文":
                    continue
                if any(hold[x] == major[x] for x in P):
                    continue
                if require_pairwise:
                    # 两两对调：若 x 持有 y 的书，则 y 持有 x 的书
                    owner = {major[x]: x for x in P}
                    if any(hold[owner[hold[x]]] != major[x] for x in P):
                        continue
                sols.append((major, hold))
        return sols

    opts = {
        "A": lambda mj, hd: mj["甲"] == "经",
        "B": lambda mj, hd: hd["丙"] == "文",
        "C": lambda mj, hd: mj["乙"] == "社",
        "D": lambda mj, hd: hd["丁"] == "历",
    }
    for label, pw in [("一般重新分配（题本读法）", False), ("两两对调（对照读法）", True)]:
        sols = solve(pw)
        print(f"\n[{label}] 解的个数 = {len(sols)}")
        for mj, hd in sols:
            print("   专业:", mj, " 持书:", hd)
        if sols:
            for k, f in opts.items():
                vals = {f(mj, hd) for mj, hd in sols}
                tag = "能推出（所有解均真）" if vals == {True} else (
                    "必假" if vals == {False} else "不能推出（有真有假）")
                print(f"   选项{k}: {tag}")
        else:
            print("   无解 -> 该读法下题目不成立，考生会自然排除此读法")

    # 对照：删去“四人的专业各不相同”，只保留首句。
    # 此时专业为任意映射；书为实体书（每人一本本专业书），交换为实体书的置换。
    # (3) 两种理解：强 = 所持书的专业≠本人专业；弱 = 所持书不是自己带来的那一本。
    print("\n[对照：删去“四人的专业各不相同”] ")
    for strong in (True, False):
        sols = []
        for mj in product(M, repeat=4):
            major = dict(zip(P, mj))
            if major["丙"] != "历" or major["丁"] != "文":
                continue
            for perm in permutations(range(4)):  # 第 i 人持有第 perm[i] 人带来的书
                hold = {P[i]: major[P[perm[i]]] for i in range(4)}
                if hold["甲"] != "社" or hold["乙"] == "文":
                    continue
                if strong and any(hold[x] == major[x] for x in P):
                    continue
                if (not strong) and any(perm[i] == i for i in range(4)):
                    continue
                sols.append((tuple(mj), perm, tuple(hold[x] for x in P)))
        uniq = sorted(set((s[0], s[2]) for s in sols))
        print(f"   条件(3)取{'强' if strong else '弱'}义：解（专业, 持书）{len(uniq)} 组")
        for mj, hd in uniq:
            print("     专业", dict(zip(P, mj)), " 持书", dict(zip(P, hd)))
        for k, f in opts.items():
            vals = {f(dict(zip(P, mj)), dict(zip(P, hd))) for mj, hd in uniq}
            tag = "能推出" if vals == {True} else ("必假" if vals == {False} else "不能推出")
            print(f"     选项{k}: {tag}")


# ---------------------------------------------------------------------------
# Q55
# ---------------------------------------------------------------------------
def q55():
    hr("Q55 补前提：女教师是否多于男教师")
    # 变量：fn=师范女，fx=非师范女，mn=师范男，mx=非师范男（非负整数）
    # 已知：fn > mx；目标：fn+fx > mn+mx
    opts = {
        "A 师范<非师范": lambda fn, fx, mn, mx: fn + mn < fx + mx,
        "B 师范>非师范": lambda fn, fx, mn, mx: fn + mn > fx + mx,
        "C 师范女>非师范男(复述)": lambda fn, fx, mn, mx: fn > mx,
        "D 非师范女>非师范男": lambda fn, fx, mn, mx: fx > mx,
    }
    R = range(0, 8)
    for k, f in opts.items():
        cex = None
        for fn, fx, mn, mx in product(R, repeat=4):
            if fn > mx and f(fn, fx, mn, mx) and not (fn + fx > mn + mx):
                cex = (fn, fx, mn, mx)
                break
        if cex:
            print(f"   {k}: 不足以保证结论，反例 师范女={cex[0]} 非师范女={cex[1]} "
                  f"师范男={cex[2]} 非师范男={cex[3]}")
        else:
            print(f"   {k}: 在 0..7 范围内无反例（A 的代数证明：两式相加得 非师范女>师范男，"
                  f"再与 师范女>非师范男 相加）" if k.startswith("A") else f"   {k}: 无反例")


# ---------------------------------------------------------------------------
# Q60
# ---------------------------------------------------------------------------
def q60():
    hr("Q60 预言真假与职业")
    P = ["甲", "乙", "丙", "丁"]
    J = ["企业家", "大学教师", "歌手", "会计师"]
    # 预言：甲: 乙≠歌手；乙: 丙=会计师；丙: 丁≠企业家；丁: 乙≠大学教师
    pred = {
        "甲": lambda a: a["乙"] != "歌手",
        "乙": lambda a: a["丙"] == "会计师",
        "丙": lambda a: a["丁"] != "企业家",
        "丁": lambda a: a["乙"] != "大学教师",
    }
    # 读法一（自然读法）：成为会计师的那个人的预言为真，其余三人的预言为假
    sols = []
    for jb in permutations(J):
        a = dict(zip(P, jb))
        acc = [x for x in P if a[x] == "会计师"][0]
        if all(pred[x](a) == (x == acc) for x in P):
            sols.append(a)
    print("   读法一（会计师本人所作预言为真、其余为假）解：")
    for a in sols:
        print("     ", a)
    options = {
        "A": ["企业家", "大学教师", "歌手", "会计师"],
        "B": ["大学教师", "歌手", "企业家", "会计师"],
        "C": ["企业家", "歌手", "会计师", "大学教师"],
        "D": ["会计师", "大学教师", "歌手", "企业家"],
    }
    for k, v in options.items():
        if any([a[x] for x in P] == v for a in sols):
            print(f"   与选项{k}一致")
    # 读法二（对照）：只有“关于会计师的那条预言”（乙的预言）为真，其余为假
    sols2 = []
    for jb in permutations(J):
        a = dict(zip(P, jb))
        if pred["乙"](a) and not pred["甲"](a) and not pred["丙"](a) and not pred["丁"](a):
            sols2.append(a)
    print(f"   读法二（只有内容涉及会计师的预言为真）解的个数 = {len(sols2)}（无解，考生会排除此读法）")


# ---------------------------------------------------------------------------
# Q61
# ---------------------------------------------------------------------------
def q61():
    hr("Q61 逻辑结构相似（必要/充分条件）")
    # 题干：p=提高管理水平，q=优化工作流程，r=工作效率提升
    #   前提 p→r；q→r；结论 r→(p∨q)（“要想r，必须p或q” = p∨q 是 r 的必要条件）
    stem = (3, [lambda p, q, r: imp(p, r), lambda p, q, r: imp(q, r)],
            lambda p, q, r: imp(r, p or q), ["p", "q", "r"])
    # A：x=科学施肥，y=提高产量，z=改良土壤：x→y；x→z；结论 x→(y∨z)
    A = (3, [lambda x, y, z: imp(x, y), lambda x, y, z: imp(x, z)],
         lambda x, y, z: imp(x, y or z), ["施肥", "产量", "土壤"])
    # B：g=绿色生产，u=减少污染，v=节约资源：“只有g才u” u→g；v→g；结论 (u∨v)→g
    B = (3, [lambda g, u, v: imp(u, g), lambda g, u, v: imp(v, g)],
         lambda g, u, v: imp(u or v, g), ["绿色", "减污", "节资"])
    # C：l=降低故障率，j=定期检修，s=避免事故，o=规范操作：l→j；s→o；结论 (l∨s)→o
    C = (4, [lambda l, j, s, o: imp(l, j), lambda l, j, s, o: imp(s, o)],
         lambda l, j, s, o: imp(l or s, o), ["降故障", "检修", "避事故", "规范"])
    # D：a=加强宣传，d=优化设计，k=提高知名度：a→k；d→k；结论 k→(a∨d)（“k的前提是a或d”）
    D = (3, [lambda a, d, k: imp(a, k), lambda a, d, k: imp(d, k)],
         lambda a, d, k: imp(k, a or d), ["宣传", "设计", "知名度"])
    v, cex = valid(stem[1], stem[2], stem[0])
    print(f"   题干推理有效？{v}  （反例赋值 p,q,r = {cex}）")
    for k, arg in zip(OPT, [A, B, C, D]):
        vv, cx = valid(arg[1], arg[2], arg[0])
        iso = isomorphic(arg, stem)
        print(f"   选项{k}: 推理有效？{vv!s:5}  与题干结构同构？{'是' if iso else '否'}")


# ---------------------------------------------------------------------------
# Q63
# ---------------------------------------------------------------------------
def q63():
    hr("Q63 录用人数")
    names = ["甲", "乙", "丙", "丁", "戊", "己"]
    # (1) 丙⊕丁  (2) 甲∨乙  (3) 甲⊕丁  (4) 乙↔丙  (5) 甲+戊+己 = 2
    sols = []
    for m in models(6):
        j, y, b, d, w, g = m
        if (b != d) and (j or y) and (j != d) and iff(y, b) and (j + w + g == 2):
            sols.append(m)
    for m in sols:
        print("   录用：", [n for n, x in zip(names, m) if x], " 人数 =", sum(m))
    print("   可能的人数集合：", sorted({sum(m) for m in sols}))


# ---------------------------------------------------------------------------
# Q64
# ---------------------------------------------------------------------------
def q64():
    hr("Q64 逻辑结构相似（联言前件的否定后件式）")
    # 题干（细版）：t=以真实为土壤（=取材于真实事件），s=以真诚为养分，k=口碑好，b=票房好
    #   前提 (t∧s)→(k∧b)；t；¬k   结论 ¬s
    stem_fine = (4, [lambda t, s, k, b: imp(t and s, k and b),
                     lambda t, s, k, b: t, lambda t, s, k, b: not k],
                 lambda t, s, k, b: not s, ["t", "s", "k", "b"])
    # 题干（粗版）：把“口碑票房双丰收”记作 w，“口碑很差”蕴含 ¬w
    #   前提 (t∧s)→w；t；¬w   结论 ¬s
    stem = (3, [lambda t, s, w: imp(t and s, w), lambda t, s, w: t, lambda t, s, w: not w],
            lambda t, s, w: not s, ["t", "s", "w"])
    # A：q=提升质量，x=产销稳定增长，y=出口稳定增长
    #   “除非q，否则(¬x∨¬y)” ≡ ¬q→(¬x∨¬y)；x；¬q   结论 ¬y
    A = (3, [lambda q, x, y: imp(not q, (not x) or (not y)),
             lambda q, x, y: x, lambda q, x, y: not q],
         lambda q, x, y: not y, ["质量", "产销", "出口"])
    # B：h=跑前热身，l=跑后拉伸，r=减小冲击
    #   (h∨l)→r；h；¬r（把“仍感到疲惫”宽松地当作¬r）   结论 ¬l
    B = (3, [lambda h, l, r: imp(h or l, r), lambda h, l, r: h, lambda h, l, r: not r],
         lambda h, l, r: not l, ["热身", "拉伸", "减冲击"])
    # C：m=用于商标，a=用于商业广告，u=轮椅使用了标识，v=违规
    #   (m∨a)→v；u   结论 v（u 与 m、a 无逻辑联系）
    C = (4, [lambda m, a, u, v: imp(m or a, v), lambda m, a, u, v: u],
         lambda m, a, u, v: v, ["商标", "广告", "使用", "违规"])
    # D：n=退税商店增多，e=验核时间减少，p=2.0政策实施
    #   (n∧e)→p；¬n；p   结论 e
    D = (3, [lambda n, e, p: imp(n and e, p), lambda n, e, p: not n, lambda n, e, p: p],
         lambda n, e, p: e, ["商店增多", "时间减少", "政策实施"])
    v1, _ = valid(stem_fine[1], stem_fine[2], stem_fine[0])
    v2, _ = valid(stem[1], stem[2], stem[0])
    print(f"   题干推理有效？细版 {v1}，粗版 {v2}")
    for k, arg in zip(OPT, [A, B, C, D]):
        vv, cx = valid(arg[1], arg[2], arg[0])
        iso = isomorphic(arg, stem)
        extra = ""
        if k == "B":
            consistent = any(all(p(*m) for p in arg[1]) for m in models(3))
            extra = f"  （B 的三个前提可同时为真？{consistent}——h→r 与 ¬r 冲突，故 B 实为前提矛盾）"
        print(f"   选项{k}: 推理有效？{vv!s:5}  与题干（粗版）同构？{'是' if iso else '否'}{extra}")
    # A 的等价变形展示：¬q→(¬x∨¬y) 与 (x∧y)→q 等价
    print("   A 的条件 ¬q→(¬x∨¬y) 与 (x∧y)→q 等价？",
          equiv(lambda q, x, y: imp(not q, (not x) or (not y)),
                lambda q, x, y: imp(x and y, q), 3))


if __name__ == "__main__":
    q51()
    q53()
    q55()
    q60()
    q61()
    q63()
    q64()

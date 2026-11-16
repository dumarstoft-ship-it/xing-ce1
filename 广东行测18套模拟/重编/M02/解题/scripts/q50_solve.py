"""第50题核验（二）：枚举四块积木的所有摆法，检验每个选项能否由它们恰好拼成。

各选项的格子状态由 q50_render.py 渲染比对题图得到（并逐一目视核对）：
  "有"=看得见的方块（必须被积木占据），"空"=看得见的空位（不能占），
  "挡"=被挡住看不见（可占可不占）。坐标 (x 向右, d 向后, h 向上)。
积木形状（同一坐标系，题图辨认）：
  P1 T形5块（平面）；P2 L形4块（平面）；
  P3 6块：前排底层3块 + 右端上方1块 + 右端后方上下2块；
  P4 6块：L形三格底面叠两层（左前、左后、右后各上下2块）。
     P4 左后下方那块在图中完全被挡住，另按5块的情形也算一遍作对照。
"""
import itertools

import numpy as np

ALL = set(itertools.product(range(3), range(3), range(3)))

P1 = {(0, 0, 2), (1, 0, 2), (2, 0, 2), (1, 0, 1), (1, 0, 0)}
P2 = {(0, 0, 2), (1, 0, 2), (1, 0, 1), (1, 0, 0)}
P3 = {(0, 0, 0), (1, 0, 0), (2, 0, 0), (2, 0, 1), (2, 1, 0), (2, 1, 1)}
P4_6 = {(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (1, 1, 0), (1, 1, 1)}
P4_5 = P4_6 - {(0, 1, 0)}


def rotations():
    def rx(p): x, d, h = p; return (x, -h, d)
    def ry(p): x, d, h = p; return (h, d, -x)
    def rz(p): x, d, h = p; return (-d, x, h)
    mats = []
    seen = set()
    for a in range(4):
        for b in range(4):
            for c in range(4):
                def f(p, a=a, b=b, c=c):
                    for _ in range(a): p = rx(p)
                    for _ in range(b): p = ry(p)
                    for _ in range(c): p = rz(p)
                    return p
                key = tuple(f(q) for q in ((1, 0, 0), (0, 1, 0), (0, 0, 1)))
                if key not in seen:
                    seen.add(key); mats.append(f)
    assert len(mats) == 24
    return mats


ROTS = rotations()


def placements(piece):
    out = set()
    for f in ROTS:
        cells = [f(p) for p in piece]
        mx = [min(c[i] for c in cells) for i in range(3)]
        norm = [tuple(c[i] - mx[i] for i in range(3)) for c in cells]
        for dx, dd, dh in itertools.product(range(3), repeat=3):
            pl = frozenset((c[0] + dx, c[1] + dd, c[2] + dh) for c in norm)
            if pl <= ALL:
                out.add(pl)
    return list(out)


def grid(rows):
    """rows: {h: "d0 d1 d2"}, 每段3个字符对应 x=0..2，取值 有/空/挡。"""
    st = {}
    for h, line in rows.items():
        for d, seg in enumerate(line.split()):
            for x, ch in enumerate(seg):
                st[(x, d, h)] = ch
    return st


OPTS = {
    "A": grid({2: "有有有 有有空 有有有", 1: "空有空 有有空 挡挡有", 0: "空有空 有挡有 挡挡有"}),
    "B": grid({2: "有有空 有有空 有有空", 1: "有有空 挡挡有 挡挡有", 0: "有空有 挡有有 挡挡空"}),
    "C": grid({2: "空有有 空有有 有有有", 1: "空空有 有有有 挡挡有", 0: "空空有 有有有 挡挡有"}),
    "D": grid({2: "有空空 有有有 有有有", 1: "有有有 挡挡有 挡挡空", 0: "有空空 挡有有 挡挡空"}),
}


def solve(st, pieces):
    must = {c for c, v in st.items() if v == "有"}
    allowed = {c for c, v in st.items() if v != "空"}
    pls = [[p for p in placements(pc) if p <= allowed] for pc in pieces]
    total = sum(len(pc) for pc in pieces)
    sols = []
    # 先放最大的积木，剪枝
    order = sorted(range(len(pieces)), key=lambda i: len(pls[i]))

    def rec(k, used, chosen):
        if k == len(order):
            if must <= used:
                sols.append(dict(chosen))
            return
        i = order[k]
        for p in pls[i]:
            if used & p:
                continue
            chosen[i] = p
            rec(k + 1, used | p, chosen)
            del chosen[i]
    rec(0, frozenset(), {})
    return sols, total, len(must), len(allowed)


if __name__ == "__main__":
    for label, p4 in (("P4按6块", P4_6), ("P4按5块(对照)", P4_5)):
        print("==", label, "==")
        for k, st in OPTS.items():
            sols, total, nm, na = solve(st, [P1, P2, P3, p4])
            print(f"选项{k}: 积木共{total}块；必须占{nm}格，最多可占{na}格；可行拼法 {len(sols)} 种")
            if sols:
                s = sols[0]
                names = ["T形", "L形", "积木3", "积木4"]
                for i in sorted(s):
                    print("   ", names[i], sorted(s[i]))

    print("== 读图敏感性检查（P4按6块） ==")
    pcs = [P1, P2, P3, P4_6]
    stA = dict(OPTS["A"]); stA[(2, 1, 2)] = "有"
    print("A 若(2,1,2)有方块：拼法", len(solve(stA, pcs)[0]), "种")
    for nv in ("有", "挡"):
        stB = dict(OPTS["B"]); stB[(2, 2, 0)] = nv
        print(f"B 若(2,2,0)读作“{nv}”：拼法", len(solve(stB, pcs)[0]), "种")
    flips = []
    for c, v in OPTS["B"].items():
        for nv in ("有", "空", "挡"):
            if nv != v:
                st = dict(OPTS["B"]); st[c] = nv
                if solve(st, pcs)[0]:
                    flips.append((c, v, nv))
    print("B 中改动单格读法后变为可拼的情形：", flips,
          "（只涉及底层前排中间、中层前排右侧两个明显的空位）")

    print("== B 项分情况推理的逐步核对 ==")
    allowed = {c for c, v in OPTS["B"].items() if v != "空"}
    corner = (2, 0, 0)
    for nm, pc in (("T形", P1), ("L形", P2), ("积木3", P3), ("积木4", P4_6)):
        print(" 能放到底层右前角", corner, "的", nm, "摆法：",
              [sorted(p) for p in placements(pc) if p <= allowed and corner in p])
    L = frozenset({(2, 0, 0), (2, 1, 0), (1, 1, 0), (0, 1, 0)})
    T1 = frozenset({(0, 0, 0), (0, 0, 1), (0, 0, 2), (0, 1, 1), (0, 2, 1)})
    Q3 = frozenset({(0, 0, 0), (0, 0, 1), (0, 0, 2), (0, 1, 2), (1, 0, 2), (1, 1, 2)})
    rem = allowed - L
    print(" L形放好后，能覆盖底层左前角(0,0,0)的摆法：",
          {nm: [sorted(p) for p in placements(pc) if p <= rem and (0, 0, 0) in p]
           for nm, pc in (("T形", P1), ("积木3", P3), ("积木4", P4_6))})
    rem = allowed - L - T1
    print(" 情况①T形放左前棱后，能覆盖底层左后角(0,2,0)的积木3/积木4摆法：",
          [sorted(p) for pc in (P3, P4_6) for p in placements(pc) if p <= rem and (0, 2, 0) in p])
    rem = allowed - L - Q3
    Ts = [p for p in placements(P1) if p <= rem and (1, 0, 1) in p]
    print(" 情况②积木3放左前棱后，能覆盖中层前排中间(1,0,1)的T形摆法", len(Ts), "种；",
          "积木4摆法", len([p for p in placements(P4_6) if p <= rem and (1, 0, 1) in p]), "种")
    for T in Ts:
        print("   T=", sorted(T), "之后积木4能否恰好填满剩余：",
              any(p == rem - T for p in placements(P4_6)))

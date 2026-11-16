"""Q47: compute candidate features for every cell/option (lattices verified by eye
against a 4x enlargement; produced by q47_read.py)."""
CELLS = {
    "R1C1": [".W.W", "WBWW", "BBWB", "W.BW"],
    "R1C2": ["BW.B", "WWBW", "WB.W", "WBW."],
    "R1C3": [".B.W", "BBWB", "BWWB", "B.BW"],
    "R2C1": ["BW..", "WW.B", ".BWW", ".WWB"],
    "R2C2": ["BW.B", "WBBW", "BW.W", "WWWB"],
    "R2C3": ["WB..", "BW.B", ".BWB", "WBBW"],
    "R3C1": ["WW.W", "W.WB", "WWBW", "WBWW"],
    "R3C2": ["WWBB", "WWBW", "B.WW", ".BW."],
    "A": ["WBBW", "BWWB", "WWWW", ".BWW"],
    "B": ["BB.W", "BWWB", "WWBB", "WWBW"],
    "C": ["WBBW", "BWWB", "WWBW", "WBWW"],
    "D": ["BB.W", "BWWB", "WWBB", ".WWW"],
}

N4 = [(0, 1), (1, 0)]


def comps(g, chars):
    seen = set()
    n = 0
    for r in range(4):
        for c in range(4):
            if g[r][c] in chars and (r, c) not in seen:
                n += 1
                st = [(r, c)]
                seen.add((r, c))
                while st:
                    y, x = st.pop()
                    for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < 4 and 0 <= nx < 4 and g[ny][nx] in chars and (ny, nx) not in seen:
                            seen.add((ny, nx))
                            st.append((ny, nx))
    return n


def pairs(g):
    bb = ww = bw = 0
    for r in range(4):
        for c in range(4):
            for dy, dx in N4:
                ny, nx = r + dy, c + dx
                if ny < 4 and nx < 4:
                    a, b = g[r][c], g[ny][nx]
                    if a == "." or b == ".":
                        continue
                    if a == b == "B":
                        bb += 1
                    elif a == b == "W":
                        ww += 1
                    else:
                        bw += 1
    return bb, ww, bw


def sym(g, ch):
    """which symmetries the set of positions with chars in ch has"""
    S = {(r, c) for r in range(4) for c in range(4) if g[r][c] in ch}
    res = []
    tf = {
        "|": lambda r, c: (r, 3 - c), "-": lambda r, c: (3 - r, c),
        "\\": lambda r, c: (c, r), "/": lambda r, c: (3 - c, 3 - r),
        "rot180": lambda r, c: (3 - r, 3 - c),
    }
    for k, f in tf.items():
        if {f(r, c) for r, c in S} == S:
            res.append(k)
    return ",".join(res) or "-none-"


hdr = "cell  nB nW tot emp | compB compW compAll | BB WW BW | symShape symB symW"
print(hdr)
for k, g in CELLS.items():
    s = "".join(g)
    nB, nW = s.count("B"), s.count("W")
    bb, ww, bw = pairs(g)
    print(f"{k:5} {nB:2} {nW:2} {nB + nW:3} {16 - nB - nW:3} | {comps(g, 'B'):5} {comps(g, 'W'):5} "
          f"{comps(g, 'BW'):7} | {bb:2} {ww:2} {bw:2} | {sym(g, 'BW'):8} {sym(g, 'B'):6} {sym(g, 'W')}")

print()
print("row/col black counts per cell")
for k, g in CELLS.items():
    rows = [r.count("B") for r in g]
    cols = [sum(g[r][c] == "B" for r in range(4)) for c in range(4)]
    roww = [r.count("W") for r in g]
    colw = [sum(g[r][c] == "W" for r in range(4)) for c in range(4)]
    empt = [(r, c) for r in range(4) for c in range(4) if g[r][c] == "."]
    print(f"{k:5} rowsB={rows} colsB={cols} rowsW={roww} colsW={colw} empty={empt}")

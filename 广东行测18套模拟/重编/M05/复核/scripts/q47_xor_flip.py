"""Q47 (3x3): test row rule  fig3 == F(fig1 XOR fig2)  for candidate transforms F.
Elements were read from zoomed crops:
 Row1 (circle family): straight half-segments H_WO,H_OE,V_NO,V_OS and quarter arcs
   o_XY = outer arc of the circle in quadrant XY, i_XY = inward arc (centred on bounding-square corner XY).
 Row2 (grid 5x5 points, x right 0..4, y down 0..4): unit segments h(y,x), v(x,y), diagonal d1 '/'(x,y)->(x-1,y+1), d2 '\\'.
 Row3 (hexagon lattice: T,UR,LR,B,LL,UL vertices + centre C): edges as frozensets.
"""
# ---------- row 1 ----------
r1f1 = {"H_WO","H_OE","o_NE","i_NW","o_SW","i_SW","i_SE"}
r1f2 = {"V_NO","V_OS","H_OE","o_NW","i_NW","o_NE","i_NE","o_SE","i_SE"}
r1f3 = {"V_NO","V_OS","H_WO","o_NW","i_NW","o_NE","i_SE","o_SW"}
def r1_flipv(s):   # N<->S
    m = {"N":"S","S":"N","E":"E","W":"W","O":"O"}
    out = set()
    for e in s:
        kind, pts = e.split("_")
        if kind in ("o","i"):
            out.add(kind+"_"+m[pts[0]]+m[pts[1]])
        else:
            a, b = m[pts[0]], m[pts[1]]
            if kind == "V":
                out.add("V_"+("NO" if "N" in (a,b) else "OS"))
            else:
                out.add("H_"+pts)
    return out
def r1_fliph(s):   # E<->W
    m = {"N":"N","S":"S","E":"W","W":"E","O":"O"}
    out = set()
    for e in s:
        kind, pts = e.split("_")
        if kind in ("o","i"):
            q = m[pts[0]]+m[pts[1]]
            out.add(kind+"_"+("".join(sorted(q, key=lambda c: "NS".find(c) if c in "NS" else 9))))
        elif kind == "H":
            out.add("H_"+("WO" if "W" in (m[pts[0]], m[pts[1]]) else "OE"))
        else:
            out.add(e)
    return out

# ---------- row 2 ----------
def H(y, x0, x1): return {("h", y, x) for x in range(x0, x1)}
def V(x, y0, y1): return {("v", x, y) for y in range(y0, y1)}
def D1(x, y, n):  return {("d1", x-i, y+i) for i in range(n)}   # '/' from (x,y) down-left n steps
def D2(x, y, n):  return {("d2", x+i, y+i) for i in range(n)}   # '\' from (x,y) down-right n steps
r2f1 = H(0,0,4)|H(1,0,4)|H(3,0,4)|H(4,2,4)|V(0,0,3)|V(4,3,4)|D1(4,0,4)
r2f2 = H(0,2,4)|D1(4,0,3)|H(1,0,3)|H(2,0,4)|H(3,0,1)|V(0,3,4)|H(4,0,4)|V(4,1,4)
r2f3 = H(0,0,2)|D2(0,0,1)|H(1,1,4)|V(4,1,3)|H(3,3,4)|V(0,0,4)|H(2,0,4)|H(4,0,2)
def r2_flipv(s):
    out = set()
    for e in s:
        if e[0] == "h": out.add(("h", 4-e[1], e[2]))
        elif e[0] == "v": out.add(("v", e[1], 3-e[2]))
        elif e[0] == "d1":   # (x,y)->(x-1,y+1) becomes (x,4-y)->(x-1,3-y) i.e. '\' from (x-1,3-y)
            out.add(("d2", e[1]-1, 3-e[2]))
        else:                # d2 (x,y)->(x+1,y+1) becomes '/' from (x+1,3-y)
            out.add(("d1", e[1]+1, 3-e[2]))
    return out
def r2_fliph(s):
    out = set()
    for e in s:
        if e[0] == "h": out.add(("h", e[1], 3-e[2]))
        elif e[0] == "v": out.add(("v", 4-e[1], e[2]))
        elif e[0] == "d1": out.add(("d2", 4-e[1], e[2]))
        else: out.add(("d1", 4-e[1], e[2]))
    return out

# ---------- row 3 ----------
def E(*pairs): return {frozenset(p.split("-")) for p in pairs}
r3f1 = E("UL-T","T-C","UL-C","C-UR","UR-LR","LR-B","B-LL","LL-C")
r3f2 = E("T-C","C-B","UL-T","UL-LL","LL-C","T-UR","UR-C","C-LR","LR-B")
OPT = {
 "A": E("UL-T","T-C","UL-LL","LL-C","C-UR","UR-LR","LR-B"),
 "B": E("T-C","C-B","UL-C","C-LR","T-UR","UR-LR","UL-LL","LL-B"),
 "C": E("T-UR","UR-LR","UL-C","C-LR","C-B","LL-B","UL-LL"),
 "D": E("UL-T","T-C","C-B","UL-LL","LL-C","C-UR","UR-LR","LR-B"),
}
VF = {"T":"B","B":"T","UL":"LL","LL":"UL","UR":"LR","LR":"UR","C":"C"}
HF = {"T":"T","B":"B","UL":"UR","UR":"UL","LL":"LR","LR":"LL","C":"C"}
def r3_map(s, m): return {frozenset(m[v] for v in e) for e in s}

print("row1: XOR==f3?", (r1f1 ^ r1f2) == r1f3,
      "| flipV(XOR)==f3?", r1_flipv(r1f1 ^ r1f2) == r1f3,
      "| flipH(XOR)==f3?", r1_fliph(r1f1 ^ r1f2) == r1f3)
print("row2: XOR==f3?", (r2f1 ^ r2f2) == r2f3,
      "| flipV(XOR)==f3?", r2_flipv(r2f1 ^ r2f2) == r2f3,
      "| flipH(XOR)==f3?", r2_fliph(r2f1 ^ r2f2) == r2f3)
x3 = r3f1 ^ r3f2
for k, o in OPT.items():
    print(f"row3 option {k}: ==XOR? {o == x3}  ==flipV(XOR)? {o == r3_map(x3, VF)}  ==flipH(XOR)? {o == r3_map(x3, HF)}")

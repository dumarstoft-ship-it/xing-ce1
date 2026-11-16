"""Q46: check rule 'exactly 5 faces AND one face is similar (same shape, any size,
rotation or reflection allowed) to the outer contour'.
Face counts come from regions.py (flood fill). Vertex coordinates below were read
from zoomed crops (crop.py); units are zoomed pixels, only ratios/angles matter.
Similarity score = max relative deviation of side ratios / max angle deviation
under the best cyclic alignment (with and without reflection).
"""
import math

def sig(poly):
    n = len(poly)
    sides = [math.dist(poly[i], poly[(i+1) % n]) for i in range(n)]
    per = sum(sides)
    sides = [s/per for s in sides]
    angs = []
    for i in range(n):
        a, b, c = poly[i-1], poly[i], poly[(i+1) % n]
        v1 = (a[0]-b[0], a[1]-b[1]); v2 = (c[0]-b[0], c[1]-b[1])
        cross = v1[0]*v2[1]-v1[1]*v2[0]; dot = v1[0]*v2[0]+v1[1]*v2[1]
        angs.append(math.degrees(math.atan2(abs(cross), dot)) * (1 if cross > 0 else -1))
    # make orientation consistent (sum of signed interior angle sign)
    if sum(angs) < 0:
        angs = [-a for a in angs]
    return sides, angs

def best_match(p, q):
    if len(p) != len(q):
        return None
    best = None
    for poly in (q, q[::-1]):
        s2, a2 = sig(poly)
        s1, a1 = sig(p)
        n = len(p)
        for k in range(n):
            # vertex i of p <-> vertex i+k of poly ; side i <-> side i+k
            ds = max(abs(s1[i]-s2[(i+k) % n]) / s1[i] for i in range(n))
            da = max(abs(abs(a1[i])-abs(a2[(i+k) % n])) for i in range(n))
            sg = all((a1[i] > 0) == (a2[(i+k) % n] > 0) for i in range(n))  # convex/concave pattern
            cand = (round(ds, 3), round(da, 1), sg)
            if sg and (best is None or cand[:2] < best[:2]):
                best = cand
    return best

PANELS = {
  "fig1": dict(faces=5, outer=[(75,90),(330,205),(595,90),(595,650),(335,765),(75,655)],
               cand={"ML": [(75,330),(190,380),(315,320),(315,580),(190,625),(75,575)],
                     "TR": [(330,205),(595,90),(595,455),(315,390),(315,320),(190,380)]}),
  "fig2": dict(faces=5, outer=[(585,110),(935,110),(935,460),(585,460)],
               cand={"diamond": [(760,118),(928,285),(762,455),(595,290)]}),
  "fig3": dict(faces=5, outer=[(245,130),(655,130),(655,740),(40,740)],
               cand={"TR": [(330,130),(655,130),(655,465),(430,460)],
                     "TL": [(245,130),(330,130),(430,460),(140,465)]}),
  "fig4": dict(faces=5, outer=[(120,120),(725,120),(680,725),(70,725)],
               cand={"BR": [(395,420),(690,420),(680,725),(370,720)],
                     "TL": [(120,120),(515,125),(415,350),(110,350)]}),
  "fig5": dict(faces=5, outer=[(195,200),(650,200),(745,455),(650,700),(200,700),(95,455)],
               cand={"upperHex": [(300,200),(550,200),(590,330),(540,460),(300,460),(255,330)],
                     "lowerHex": [(300,465),(540,465),(565,560),(540,645),(305,645),(270,560)]}),
  "optA": dict(faces=5, outer=[(85,170),(300,170),(300,295),(440,295),(440,525),(85,525)],
               cand={"step": [(300,235),(300,295),(440,295),(350,395),(210,395),(210,320)],
                     "LB": [(85,320),(210,320),(210,395),(350,395),(225,525),(85,525)]}),
  "optB": dict(faces=4, outer=[(590,175),(850,175),(945,345),(850,510),(590,510)],
               cand={"innerPent": [(660,255),(795,255),(850,345),(795,430),(660,430)]}),
  "optC": dict(faces=5, outer=[(95,355),(210,255),(680,255),(680,765),(95,765)],
               cand={"TR": [(380,255),(680,255),(680,515),(440,515),(380,465)],
                     "TL": [(95,355),(210,255),(380,255),(380,465),(95,520)]}),
  "optD": dict(faces=5, outer=[(170,270),(615,270),(665,770),(115,770)],
               cand={"topBand": [(170,270),(615,270),(625,385),(160,385)],
                     "innerLeft(face)": [(270,485),(395,485),(395,765),(240,765)],
                     "innerTrapezoid(NOT a face, split by vertical)": [(270,485),(520,485),(545,765),(240,765)]}),
}

for name, p in PANELS.items():
    print(f"{name}: faces={p['faces']}")
    for cn, poly in p["cand"].items():
        m = best_match(p["outer"], poly)
        print(f"    {cn:45s} vs outer -> {m}  (side-ratio dev, angle dev deg, concavity pattern ok)")

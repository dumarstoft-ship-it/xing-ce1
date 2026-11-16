"""第47题核验：把九宫格8幅图和4个选项的线段手工量取为坐标（题图8倍放大后的像素坐标），
计算直线数、封闭区域数、笔画数、端点数、交点数、各方向线条数等特征，寻找规律并检验选项。

线段坐标来自 q47_*_x8.png（题图每格裁出后放大8倍）。
"""
from fractions import Fraction
from itertools import combinations
import math

FIGS = {
    "1": [((120,128),(712,128)),((120,320),(718,320)),((315,128),(315,320)),((505,128),(505,500)),
          ((125,495),(125,690)),((125,690),(315,690)),((315,690),(315,500)),((315,500),(690,500)),((690,500),(690,705))],
    "2": [((115,125),(115,320)),((115,320),(495,320)),((495,125),(495,320)),((310,320),(310,700)),
          ((110,510),(310,510)),((310,700),(495,700)),((495,700),(495,510)),((495,510),(700,510)),((700,510),(700,705))],
    "3": [((115,110),(115,705)),((115,705),(305,705)),((300,110),(300,320)),((300,320),(690,320)),
          ((690,320),(690,705)),((490,700),(690,700)),((490,320),(490,700)),((115,505),(490,505))],
    "4": [((125,105),(125,395)),((125,395),(405,395)),((405,108),(405,695)),((405,108),(700,108)),
          ((405,108),(688,690)),((688,395),(688,690))],
    "5": [((110,115),(695,115)),((110,398),(690,398)),((262,115),(262,398)),((410,115),(685,685)),
          ((262,398),(398,685)),((398,398),(398,685)),((398,685),(685,685))],
    "6": [((425,115),(715,115)),((715,115),(715,390)),((715,390),(430,530)),((430,530),(130,530)),
          ((130,400),(130,688)),((130,400),(425,400)),((425,400),(425,115)),((130,688),(430,688))],
    "7": [((405,75),(120,220)),((120,220),(688,580)),((405,75),(405,400)),((688,205),(688,580)),
          ((405,400),(120,580)),((120,580),(408,722))],
    "8": [((400,70),(400,735)),((400,75),(685,210)),((685,210),(685,585)),((400,735),(685,585)),
          ((120,220),(685,580)),((400,400),(685,210))],
    "A": [((120,240),(395,80)),((395,80),(685,225)),((685,225),(115,595)),((405,405),(405,735)),
          ((115,595),(405,735)),((405,735),(665,575))],
    "B": [((65,410),(205,125)),((205,125),(565,685)),((65,410),(235,695)),((390,410),(725,410)),
          ((575,125),(725,405)),((725,405),(565,685))],
    "C": [((65,410),(210,115)),((210,115),(580,115)),((580,115),(730,405)),((210,115),(575,690)),
          ((575,690),(730,405)),((400,405),(730,405))],
    "D": [((195,120),(565,120)),((195,120),(45,410)),((45,410),(375,410)),((45,410),(200,690)),
          ((200,690),(565,120)),((565,120),(710,410))],
}

TOL = 14  # 像素容差（8倍图上的线宽约12px）


def snap_points(segs):
    """把相距很近的端点合并为同一点。"""
    pts = []
    def find(p):
        for q in pts:
            if math.dist(p, q) <= TOL:
                return q
        pts.append(p)
        return p
    out = []
    for a, b in segs:
        out.append((find(a), find(b)))
    return out, pts


def point_on_seg(p, a, b, tol=TOL):
    ax, ay = a; bx, by = b; px, py = p
    L = math.dist(a, b)
    if L == 0:
        return False
    # 垂距
    d = abs((bx-ax)*(ay-py) - (ax-px)*(by-ay)) / L
    if d > tol:
        return False
    t = ((px-ax)*(bx-ax) + (py-ay)*(by-ay)) / (L*L)
    return -tol/L <= t <= 1 + tol/L


def seg_intersection(a, b, c, d):
    (x1,y1),(x2,y2),(x3,y3),(x4,y4) = a,b,c,d
    den = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
    if den == 0:
        return None
    t = ((x1-x3)*(y3-y4) - (y1-y3)*(x3-x4)) / den
    u = -((x1-x2)*(y1-y3) - (y1-y2)*(x1-x3)) / den
    L1 = math.dist(a, b); L2 = math.dist(c, d)
    e1 = TOL / L1; e2 = TOL / L2
    if -e1 <= t <= 1+e1 and -e2 <= u <= 1+e2:
        return (x1 + t*(x2-x1), y1 + t*(y2-y1))
    return None


def direction(a, b):
    dx = b[0]-a[0]; dy = b[1]-a[1]
    ang = math.degrees(math.atan2(-dy, dx)) % 180
    if ang < 10 or ang > 170:
        return "H"
    if 80 < ang < 100:
        return "V"
    return "/" if ang < 90 else "\\"


def analyse(segs):
    segs, _ = snap_points(segs)
    n_lines = len(segs)
    # 所有节点：端点 + 交点
    nodes = []
    def add(p):
        for q in nodes:
            if math.dist(p, q) <= TOL:
                return q
        nodes.append(p)
        return p
    for a, b in segs:
        add(a); add(b)
    for (a, b), (c, d) in combinations(segs, 2):
        p = seg_intersection(a, b, c, d)
        if p is not None:
            add(p)
    # 每条线段上的节点，按参数排序 → 图的边
    edges = set()
    for a, b in segs:
        on = [q for q in nodes if point_on_seg(q, a, b)]
        L = math.dist(a, b)
        on.sort(key=lambda q: ((q[0]-a[0])*(b[0]-a[0]) + (q[1]-a[1])*(b[1]-a[1])) / L)
        for p, q in zip(on, on[1:]):
            if p != q:
                edges.add(tuple(sorted([p, q])))
    deg = {q: 0 for q in nodes}
    for p, q in edges:
        deg[p] += 1; deg[q] += 1
    used = [q for q in nodes if deg[q] > 0]
    V = len(used); E = len(edges)
    # 连通分量
    adj = {q: [] for q in used}
    for p, q in edges:
        adj[p].append(q); adj[q].append(p)
    seen = set(); comps = 0
    for q in used:
        if q in seen:
            continue
        comps += 1
        stack = [q]
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x); stack.extend(adj[x])
    regions = E - V + comps
    odd = sum(1 for q in used if deg[q] % 2 == 1)
    strokes = sum(1 for _ in range(1)) and None
    # 每个连通分量的笔画数 = max(1, 奇点数/2)
    strokes = 0
    seen = set()
    for q in used:
        if q in seen:
            continue
        comp = []
        stack = [q]
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x); comp.append(x); stack.extend(adj[x])
        o = sum(1 for x in comp if deg[x] % 2 == 1)
        strokes += max(1, o // 2)
    endpoints = sum(1 for q in used if deg[q] == 1)
    junction3 = sum(1 for q in used if deg[q] >= 3)
    points2 = sum(1 for q in used if deg[q] >= 2)
    dirs = {}
    for a, b in segs:
        k = direction(a, b)
        dirs[k] = dirs.get(k, 0) + 1
    return dict(lines=n_lines, regions=regions, parts=comps, odd=odd, strokes=strokes,
                endpoints=endpoints, branch=junction3, joints=points2, edges=E, dirs=dirs)


if __name__ == "__main__":
    for k, segs in FIGS.items():
        print(k, analyse(segs))

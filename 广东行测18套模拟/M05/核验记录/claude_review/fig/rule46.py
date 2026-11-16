# Q46: from measured components, derive (triangle vertex+edge, circle edge, segment polar angle/orientation) per figure,
# then test options against: triangle +1.5 edges clockwise; circle -1 edge (ccw); segment rotates -60 deg about centre.
import numpy as np, runpy, io, contextlib
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    runpy.run_path('analyze46.py')
lines = buf.getvalue().splitlines()
data = {}; cur = None
for ln in lines:
    if ln.startswith('=='):
        p = ln.split(); cur = p[1]
        cx, cy = map(float, ln.split('center (')[1].split(')')[0].split(','))
        xmin, xmax = map(int, ln.split('x[')[1].split(']')[0].split(','))
        ymin, ymax = map(int, ln.split('y[')[1].split(']')[0].split(','))
        data[cur] = {'c': (cx, cy), 'bbox': (xmin, xmax, ymin, ymax), 'comps': []}
    elif 'comp n=' in ln:
        n = int(ln.split('n=')[1].split()[0]); x, y = map(float, ln.split('centroid(')[1].split(')')[0].split(','))
        ang = float(ln.split('ang=')[1].split()[0]); r = float(ln.split(' r=')[1].split()[0])
        ori = float(ln.split('orient=')[1].split()[0]); el = float(ln.split('elong=')[1].split()[0])
        if r > 35: continue  # hexagon corner artefacts
        data[cur]['comps'].append(dict(n=n, x=x, y=y, ang=ang, r=r, ori=ori, el=el))
VN = ['V1(左上)', 'V2(右上)', 'V3(右)', 'V4(右下)', 'V5(左下)', 'V6(左)']
EN = ['E1上', 'E2右上', 'E3右下', 'E4下', 'E5左下', 'E6左上']
def verts(d):
    xmin, xmax, ymin, ymax = d['bbox']; cy = (ymin + ymax) / 2; w = xmax - xmin
    return [(xmin + w/4, ymin), (xmax - w/4, ymin), (xmax, cy), (xmax - w/4, ymax), (xmin + w/4, ymax), (xmin, cy)]
res = {}
for k, d in data.items():
    V = verts(d); segs = [c for c in d['comps'] if c['el'] > 4]
    blobs = [c for c in d['comps'] if c['el'] <= 4]
    seg = segs[0]
    out = {'seg_ang': seg['ang'], 'seg_ori': seg['ori']}
    # circle: blob with elong ~1.1-1.3 and n ~ 90-110 hugging an edge midpoint; triangle: the other blob (n ~ 80-100)
    tri = circ = None
    if len(blobs) == 2:
        # circle centroid lies at r~24-26 at an edge-midpoint angle (90,30,-30,-90,-150,150)
        def mid_err(c): return min(abs(((c['ang'] - a + 180) % 360) - 180) for a in (90, 30, -30, -90, -150, 150))
        circ, tri = sorted(blobs, key=mid_err)
    elif len(blobs) == 1:
        tri = circ = blobs[0]   # merged (figure 5)
    if circ is not None:
        e = int(np.argmin([abs(((circ['ang'] - a + 180) % 360) - 180) for a in (90, 30, -30, -90, -150, 150)]))
        out['circle_edge'] = EN[e] if len(blobs) == 2 else EN[0] + '(与三角形重叠，目视为上边)'
    if tri is not None:
        dv = [np.hypot(tri['x'] - vx, tri['y'] - vy) for vx, vy in V]; vi = int(np.argmin(dv))
        # adjacent edges of vertex vi: edge (vi-1) ends at vi, edge vi starts at vi
        mids = [((V[i][0] + V[(i+1) % 6][0]) / 2, (V[i][1] + V[(i+1) % 6][1]) / 2) for i in range(6)]
        cand = [(vi - 1) % 6, vi]
        ei = min(cand, key=lambda i: np.hypot(tri['x'] - mids[i][0], tri['y'] - mids[i][1]))
        pos = ei + (0.0 if ei == vi else 0.5)   # perimeter interval start (in edges, clockwise from V1)
        out['tri'] = '%s 贴 %s, 周长区间[%.1f,%.1f]' % (VN[vi], EN[ei], pos, pos + 0.5)
        out['tri_pos'] = pos
    res[k] = out
for k, o in res.items():
    print('%-3s 三角形: %-34s 圆: %-22s 短线: 极角%5.0f° 方向%4.0f°' % (k, o.get('tri', '-'), o.get('circle_edge', '-'), o['seg_ang'], o['seg_ori']))
print('\n预测图6: 三角形周长区间[1.5,2.0](=图2)；圆贴E6左上；短线极角≈90°、方向0°(水平)')
for L in 'ABCD':
    o = res[L]
    ok_t = abs(o['tri_pos'] - 1.5) < 0.01
    ok_c = o['circle_edge'].startswith('E6')
    ok_s = abs(((o['seg_ang'] - 90 + 180) % 360) - 180) < 15 and (o['seg_ori'] < 10 or o['seg_ori'] > 170)
    print('选项%s: 三角形%s 圆%s 短线%s -> %s' % (L, '✓' if ok_t else '✗', '✓' if ok_c else '✗', '✓' if ok_s else '✗', '符合' if ok_t and ok_c and ok_s else '排除'))

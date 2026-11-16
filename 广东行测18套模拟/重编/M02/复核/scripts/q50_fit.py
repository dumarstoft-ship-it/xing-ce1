"""Q50: reconstruct each option's voxel set by fitting renders to the drawing.
Greedy toggling search from several starts; reports voxels whose state is fixed by the
picture and voxels that are hidden (rendering identical either way)."""
import sys, random, itertools
sys.path.insert(0, '.')
import numpy as np
from PIL import Image, ImageFilter
from q50_render import render, full

SRC = '/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s17_p13_i00.png'
src = Image.open(SRC).convert('L')

def prep(img):
    return np.array(img.filter(ImageFilter.GaussianBlur(0.8))).astype(float)

def loss(vox, X0, YB, target, off, size):
    r = prep(render(vox, X0, YB, size=size, off=off))
    return float(((r - target) ** 2).mean())

def fit(name, X0, YB, off, size=(80, 75), starts=6, seed=0):
    target = prep(src.crop((off[0], off[1], off[0] + size[0], off[1] + size[1])))
    allv = sorted(full())
    best_overall = None
    rng = random.Random(seed)
    for s in range(starts):
        vox = set(allv) if s == 0 else {v for v in allv if rng.random() < 0.7}
        cur = loss(vox, X0, YB, target, off, size)
        improved = True
        while improved:
            improved = False
            order = allv[:]; rng.shuffle(order)
            for v in order:
                cand = vox ^ {v}
                l = loss(cand, X0, YB, target, off, size)
                if l < cur - 1e-6:
                    vox, cur, improved = cand, l, True
        if best_overall is None or cur < best_overall[0]:
            best_overall = (cur, vox)
    cur, vox = best_overall
    # which voxels matter?
    hidden = []
    for v in allv:
        l = loss(vox ^ {v}, X0, YB, target, off, size)
        if abs(l - cur) < 1e-9:
            hidden.append(v)
    missing = sorted(set(allv) - vox)
    print(f'{name}: loss {cur:.1f}; visibly missing: {[m for m in missing if m not in hidden]}')
    print(f'   hidden (undetermined) voxels: {hidden}')
    print(f'   present count incl. hidden-as-present: {27 - len([m for m in missing if m not in hidden])}')
    return vox, hidden

if __name__ == '__main__':
    params = {k: tuple(map(float, v.split(','))) for k, v in (a.split('=') for a in sys.argv[1:])}
    for name, (X0, YB, ox, oy) in params.items():
        fit(name, X0, YB, (int(ox), int(oy)))

def refine(name, X0, YB, off, size=(80, 75), rounds=3):
    target = prep(src.crop((off[0], off[1], off[0] + size[0], off[1] + size[1])))
    vox = None
    for _ in range(rounds):
        if vox is None:
            vox = full()
        # optimise placement with voxels fixed
        best = (loss(vox, X0, YB, target, off, size), X0, YB)
        for dx in np.arange(-3, 3.01, 0.5):
            for dy in np.arange(-3, 3.01, 0.5):
                l = loss(vox, X0 + dx, YB + dy, target, off, size)
                if l < best[0]:
                    best = (l, X0 + dx, YB + dy)
        _, X0, YB = best
        vox, hidden = fit_quiet(X0, YB, off, size, target)
    missing = sorted(set(full()) - vox)
    vis_missing = [m for m in missing if m not in hidden]
    print(f'{name}: X0={X0} YB={YB} loss={loss(vox, X0, YB, target, off, size):.1f}')
    print(f'   visibly missing ({len(vis_missing)}): {vis_missing}')
    print(f'   hidden/undetermined ({len(hidden)}): {hidden}')
    return vox, hidden, X0, YB

def fit_quiet(X0, YB, off, size, target, starts=6, seed=0):
    allv = sorted(full())
    rng = random.Random(seed)
    best_overall = None
    for s in range(starts):
        vox = set(allv) if s == 0 else {v for v in allv if rng.random() < 0.7}
        cur = loss(vox, X0, YB, target, off, size)
        improved = True
        while improved:
            improved = False
            order = allv[:]; rng.shuffle(order)
            for v in order:
                cand = vox ^ {v}
                l = loss(cand, X0, YB, target, off, size)
                if l < cur - 1e-6:
                    vox, cur, improved = cand, l, True
        if best_overall is None or cur < best_overall[0]:
            best_overall = (cur, vox)
    cur, vox = best_overall
    hidden = [v for v in allv if abs(loss(vox ^ {v}, X0, YB, target, off, size) - cur) < 1e-9]
    return vox, hidden

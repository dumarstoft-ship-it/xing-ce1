"""Q50 robustness: vary weakly-determined voxels (drawing evidence thin) and hidden
voxels; check solvability for piece-4 with 5 or 6 cubes."""
import sys, itertools, io, contextlib
sys.path.insert(0, '.')
with contextlib.redirect_stdout(io.StringIO()):
    from q50_solve import T5, L4, P6, P4_vis, P4_hid, solve, FULL
# option: (visibly missing, hidden voxels, weakly determined voxels with their read state)
opts = {
    'A': ({(0,0,0),(0,1,0),(2,0,0),(2,1,0),(2,1,1),(2,2,1)}, [(0,0,2),(0,1,2),(1,0,1),(1,0,2),(1,1,2)], [(1,1,1),(0,2,1),(1,2,1),(2,2,1)]),
    'B': ({(1,0,0),(2,0,2),(2,1,0),(2,2,0),(2,2,1),(2,2,2)}, [(0,0,1),(0,0,2),(0,1,1),(0,1,2),(1,0,2),(1,1,1),(1,1,2)], [(0,2,1),(1,2,1)]),
    'C': ({(0,0,0),(0,1,0),(0,2,0),(0,2,1),(1,0,0),(1,1,0)}, [(0,0,2),(0,1,2),(1,0,2),(1,1,2)], [(1,2,1),(2,1,1)]),
    'D': ({(1,0,0),(1,2,0),(2,0,0),(2,0,2),(2,1,2),(2,2,0)}, [(0,0,1),(0,0,2),(0,1,1),(0,1,2),(1,0,2),(1,1,1),(1,1,2)], [(0,2,1)]),
}
P4_6 = P4_vis | {P4_hid}
for k, (miss, hidden, weak) in opts.items():
    base = FULL - miss
    print(f'== {k}: as read = {len(base)} cubes (hidden counted present)')
    for p4name, P4 in (('piece4=6', P4_6), ('piece4=5', P4_vis)):
        pieces = [T5, L4, P6, P4]
        tot = sum(len(p) for p in pieces)
        main = len(solve(pieces, base)) if len(base) == tot else 'count mismatch'
        # variants: flip any subset of weak voxels, remove any subset of hidden voxels
        solvable_variants = []
        n_var = 0
        for wr in range(len(weak) + 1):
            for wflip in itertools.combinations(weak, wr):
                shape0 = base ^ set(wflip)
                for hr in range(len(hidden) + 1):
                    for hdrop in itertools.combinations(hidden, hr):
                        shape = shape0 - set(hdrop)
                        if len(shape) != tot:
                            continue
                        n_var += 1
                        if solve(pieces, shape):
                            solvable_variants.append((wflip, hdrop))
        print(f'   {p4name}: shape as read -> solutions: {main}; variants with right count: {n_var}, solvable: {len(solvable_variants)}')
        for v in solvable_variants[:4]:
            print('        e.g. weak flipped', v[0], 'hidden removed', v[1])

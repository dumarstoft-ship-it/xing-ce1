"""Q49 robustness: also allow cubes that would be completely hidden in the drawings of
piece 1 and of the options (cells directly behind the bottom row of the back wall),
then repeat the exhaustive tiling search of q49_assemble.py."""
import q49_assemble as base  # runs the base search once and prints it

P1_hid = base.P1_hid + [(0, 0, 2), (1, 0, 2)]          # behind a1/b1 under the level-2 roof
OPT_hid = {
    "A": base.OPT["A"][1] + [(0, 0, 3), (1, 0, 3)],
    "B": base.OPT["B"][1] + [(0, 0, 3), (1, 0, 3)],
    "C": base.OPT["C"][1] + [(0, 0, 3)],
    "D": base.OPT["D"][1] + [(0, 0, 3)],
}
p1_vars = base.variants(base.P1_vis, P1_hid)
p2_vars = base.variants(base.P2_vis, base.P2_hid)
opt_vars = {k: base.variants(base.OPT[k][0], OPT_hid[k]) for k in "ABCD"}
print("\n=== with extra hidden-cube candidates ===")
print("piece1 sizes", sorted(len(v) for v in p1_vars))
for k, vs in opt_vars.items():
    print(f"option {k} sizes", sorted(len(v) for v in vs))
found = {k: 0 for k in "ABCD"}
for p1 in p1_vars:
    for pl1 in base.placements(p1, base.BIG):
        rest1 = base.BIG - pl1
        for p2 in p2_vars:
            if len(p2) >= len(rest1):
                continue
            for pl2 in base.placements(p2, rest1):
                rest = rest1 - pl2
                shape = base.all_orients(rest)
                for k, vs in opt_vars.items():
                    for v in vs:
                        if len(v) == len(rest) and base.normalize(v) in shape:
                            found[k] += 1
print("tilings per option:", found)

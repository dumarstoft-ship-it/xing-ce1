"""Q68: metals X, Y, Z.
Exp 1: in equal dilute HCl only Y gives H2 bubbles -> Y is above H; X and Z are below H.
Exp 2: Z put into X's sulfate solution -> X deposits on Z -> Z is more active than X.
Enumerate every activity order of {X, Y, Z, H} and keep those consistent with both experiments."""
from itertools import permutations

keep = set()
for order in permutations(["X", "Y", "Z", "H"]):     # most active first
    pos = {s: i for i, s in enumerate(order)}
    reacts_with_acid = {m: pos[m] < pos["H"] for m in "XYZ"}
    if reacts_with_acid != {"X": False, "Y": True, "Z": False}:
        continue
    if not pos["Z"] < pos["X"]:                       # Z displaces X from its salt
        continue
    keep.add(">".join(s for s in order if s != "H"))
print("metal orders consistent with both experiments:", keep)
assert keep == {"Y>Z>X"}

opts = {"A": "Y>Z>X", "B": "Y>X>Z", "C": "Z>X>Y", "D": "X>Z>Y"}
matches = [k for k, v in opts.items() if v in keep]
assert matches == ["A"], matches
print("ANSWER:", matches[0])

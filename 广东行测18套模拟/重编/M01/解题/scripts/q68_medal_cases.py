"""Q68: the medal is one of: pure Fe, pure Cu, homogeneous Cu-Fe alloy. Add dilute HCl.
Fe + 2HCl -> FeCl2 (pale green) + H2 (bubbles); Cu does not react with dilute HCl.
Each option is 'if observation then conclusion'; check it over every material consistent with
the observation. The option that fails is the incorrect statement."""
materials = {"pure Fe": {"Fe"}, "pure Cu": {"Cu"}, "Cu-Fe alloy": {"Cu", "Fe"}}

def observe(comp):
    return {
        "bubbles": "Fe" in comp,
        "no bubbles": "Fe" not in comp,
        "solid left with excess HCl": "Cu" in comp,   # all Fe dissolves in excess acid; Cu stays
        "pale green solution": "Fe" in comp,
    }

options = {
    "A": ("bubbles", lambda c: "Cu" not in c, "contains no Cu"),
    "B": ("no bubbles", lambda c: "Fe" not in c, "contains no Fe"),
    "C": ("solid left with excess HCl", lambda c: "Cu" in c, "contains Cu"),
    "D": ("pale green solution", lambda c: "Fe" in c, "contains Fe"),
}
wrong = []
for k, (obs, concl, text) in options.items():
    consistent = [m for m, comp in materials.items() if observe(comp)[obs]]
    ok = all(concl(materials[m]) for m in consistent)
    print(f"{k}: if '{obs}' -> possible {consistent}; conclusion '{text}' always true? {ok}")
    if not ok:
        wrong.append(k)
assert wrong == ["A"]
print("Incorrect statement (the answer):", wrong[0])

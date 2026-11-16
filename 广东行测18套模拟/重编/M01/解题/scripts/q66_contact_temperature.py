"""Q66: an aluminium cup and a ceramic cup left outdoors for a long time are at the SAME temperature
(thermal equilibrium with the surroundings), yet they feel different. What the hand senses is the
skin-surface (contact) temperature, set by each body's thermal effusivity e = sqrt(k*rho*c):
    T_contact = (e_skin*T_skin + e_cup*T_cup) / (e_skin + e_cup)
Typical property values (order of magnitude is what matters)."""
from math import sqrt
mat = {                     # k [W/m/K], rho [kg/m^3], c [J/kg/K]
    "aluminium": (237, 2700, 897),
    "ceramic":   (1.5, 2400, 850),
    "skin":      (0.37, 1100, 3400),
}
e = {m: sqrt(k * r * c) for m, (k, r, c) in mat.items()}
for m in mat:
    print(f"{m:10s} k={mat[m][0]:>6} W/mK   effusivity e = {e[m]:8.0f}")
print("conductivity ratio Al/ceramic ~", round(mat['aluminium'][0] / mat['ceramic'][0]))

T_skin = 33.0
for season, T_cup in (("winter", -2.0), ("summer", 45.0)):
    for cup in ("aluminium", "ceramic"):
        Tc = (e["skin"] * T_skin + e[cup] * T_cup) / (e["skin"] + e[cup])
        print(f"{season}: both cups at {T_cup:5.1f} C -> skin contact with {cup:9s}: {Tc:5.1f} C")
print("winter: Al feels colder; summer: Al feels hotter -> same cause both times: Al conducts heat far better (C).")
print("A wrongly says the cups' temperatures differ; B (hardness) and D (internal energy) do not set the touch sensation.")
print("ANSWER: C")

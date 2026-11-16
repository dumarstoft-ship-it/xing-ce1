"""Q38: jia 90 m/min, yi 60 m/min, walking toward each other from A and B.
jia starts 2 min later than yi; at the meeting jia has walked 360 m more than yi. Distance AB?
options A1080 B1320 C2400 D2520"""
from fractions import Fraction as F

# jia walks t minutes, yi walks t+2 minutes: 90t - 60(t+2) = 360
t = F(360 + 120, 90 - 60)
dist = 90 * t + 60 * (t + 2)
print(f"t = {t} min; jia {90*t} m, yi {60*(t+2)} m, AB = {dist} m")
assert t == 16 and dist == 2520

# brute force over whole-second meeting times to confirm uniqueness
cands = []
for sec in range(0, 60 * 120):
    tm = F(sec, 60)
    if 90 * tm - 60 * (tm + 2) == 360:
        cands.append((tm, 90 * tm + 60 * (tm + 2)))
print("brute force:", cands)
assert cands == [(16, 2520)]

# trap: forgetting yi's extra 2 minutes -> 150 * 16 = 2400
print("trap (both walk 16 min):", 150 * 16)

opts = {"A": 1080, "B": 1320, "C": 2400, "D": 2520}
matches = [k for k, v in opts.items() if v == dist]
assert matches == ["D"], matches
print("ANSWER:", matches[0])

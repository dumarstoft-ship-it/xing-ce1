"""Q38: planned 50 km/h for 2 h -> 100 km. Actual: first half (50 km) at 60 km/h,
second half at half the planned speed (25 km/h), plus a 10 min red-light stop."""
from fractions import Fraction as F
v_plan, t_plan = 50, F(2)
D = v_plan * t_plan
t_actual = (D / 2) / 60 + (D / 2) / F(v_plan, 2) + F(10, 60)
late_min = (t_actual - t_plan) * 60
print("distance", D, "km; first half", (D/2)/60*60, "min; second half", (D/2)/F(v_plan,2)*60, "min; stop 10 min")
print("actual total", t_actual * 60, "min vs plan", t_plan * 60, "min -> late", late_min, "min")
print("trap without the 10-min stop:", late_min - 10)
opts = {"A": 50, "B": 60, "C": 70, "D": 80}
m = [k for k, v in opts.items() if v == late_min]
assert m == ["B"], m
print("ANSWER:", m[0])

"""Q41: profit margin 25%; cost +15%; price x1.5 then x0.8. Compare new margin with old."""
from fractions import Fraction as F
cost = F(100); price = cost * F(125, 100)
new_cost = cost * F(115, 100)
new_price = price * F(3, 2) * F(8, 10)
new_margin = (new_price - new_cost) / new_cost
delta_pp = (new_margin - F(1, 4)) * 100
print("new price", new_price, "new cost", new_cost, "new margin", float(new_margin) * 100, "%")
print("change:", float(delta_pp), "percentage points")
assert delta_pp > 5
print("ANSWER: A (higher by more than 5 points)")

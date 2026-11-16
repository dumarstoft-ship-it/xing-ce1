"""Q67: blowing air along the upper surface of a thin sheet of paper.
Bernoulli (same height, incompressible): p_top = p0 - rho*v^2/2 while air below is ~still at p0.
Compare the pressure deficit with the paper's weight per unit area."""
rho = 1.2            # kg/m^3, air at room temperature
g = 9.8
grammage = 0.080     # kg/m^2, ordinary 80 g/m^2 paper (thin paper is lighter still)
w_per_area = grammage * g
print(f"paper weight per area ~ {w_per_area:.2f} Pa")

for v in (2, 5, 10, 15):
    dp = 0.5 * rho * v ** 2
    print(f"blow speed {v:>2} m/s -> top pressure lower by {dp:6.1f} Pa ({dp / w_per_area:5.1f} x weight/area)")
    assert dp > 0

# even a gentle 2 m/s breath gives ~2.4 Pa > 0.78 Pa -> net upward force: the sheet rises,
# i.e. force from air on the upper surface is SMALLER than on the lower surface.
assert 0.5 * rho * 2 ** 2 > w_per_area
print("sheet rises; upper-surface force < lower-surface force -> option D (升起、小于)")

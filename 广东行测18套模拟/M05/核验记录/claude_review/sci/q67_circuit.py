# Q67 blind check. Topology read from figure s27_p18_i01.png:
#  Node P = whole left vertical wire. Node Q = right vertical above R0. Node T = right vertical below R0.
#  Branch 1 (top):    R (rheostat) P--Q ; slider wire tied to Q (right end side) -> right part of R shorted,
#                     R_eff = left part (left end .. slider). Slider left->right: R_eff 0 -> Rmax (increases).
#  Branch 2:          L1 P--Q
#  R0:                Q--T (on right vertical)
#  Branch 3:          A1 + battery + S, P--T
#  Branch 4 (bottom): A2 + L2, P--T  -> L2 directly across the ideal source.
# Ideal ammeters (0 ohm), ideal source U const.
U, R0, RL1, RL2, Rmax = 6.0, 5.0, 10.0, 10.0, 20.0
def par(a, b):
    if a == 0 or b == 0: return 0.0
    return a * b / (a + b)
print(" x(slider pos 0=left..1=right) R_eff  I_A2   U_L2  P_L2   U_L1   P_L1   I_A1")
for k in range(0, 11):
    x = k / 10
    Reff = x * Rmax
    Rp = par(Reff, RL1)
    Ibr = U / (R0 + Rp)
    UL1 = Ibr * Rp
    IA2 = U / RL2
    IA1 = IA2 + Ibr
    print(f"   {x:4.1f}                     {Reff:5.1f}  {IA2:.3f}  {U:.2f}  {U*U/RL2:.2f}  {UL1:.3f}  {UL1**2/RL1:.3f}  {IA1:.3f}")
print("Conclusion: A1 decreases (A true), A2 constant (B true), L2 constant (C true), L1 voltage/power increase (D false).")
# Robustness: even with a non-ideal source (internal r), L2 would change; stem says source voltage constant.
r = 1.0
print("\nIf source had internal resistance r=1 ohm (NOT the stated model):")
for k in (0, 5, 10):
    Reff = k / 10 * Rmax
    Rp = par(Reff, RL1)
    Rext = par(RL2, R0 + Rp)
    I = U / (Rext + r)
    Uterm = I * Rext
    print(f"  x={k/10:.1f}: U_terminal={Uterm:.3f}, I_A2={Uterm/RL2:.3f}")

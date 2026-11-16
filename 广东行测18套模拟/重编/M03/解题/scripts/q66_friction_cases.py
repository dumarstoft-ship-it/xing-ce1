"""Q66: block A rests on a uniformly rough floor under a horizontal pull F (to the right).
F is raised to 2F; max static friction = sliding friction = f_max (= mu*m*g, constant).
Which statement is necessarily true?
  A moves right with VARIABLE acceleration
  B moves right with UNIFORM (constant) acceleration
  C stays at rest
  D may stay at rest, or may accelerate to the right
Sweep every admissible F (rest initially => 0 < F <= f_max) and see what 2F does."""
from fractions import Fraction as Fr

m = Fr(1)
f_max = Fr(10)          # arbitrary units; only the ratio F/f_max matters

outcomes = set()
for i in range(1, 1001):
    F = f_max * Fr(i, 1000)            # 0 < F <= f_max, consistent with 'at rest' initially
    pull = 2 * F
    if pull <= f_max:
        state = "rest"                 # static friction grows to 2F and holds it
    else:
        a = (pull - f_max) / m          # sliding friction constant on a uniform floor
        # acceleration does not depend on time or speed -> uniformly accelerated motion
        state = "uniform acceleration right"
        assert a > 0
    outcomes.add(state)
print("possible outcomes:", outcomes)
print("threshold: stays at rest iff F <= f_max/2; e.g. F=0.4 f_max -> rest, F=0.8 f_max -> a=0.6 f_max/m")
assert outcomes == {"rest", "uniform acceleration right"}

always = {
    "A": outcomes <= {"variable acceleration right"},
    "B": outcomes <= {"uniform acceleration right"},
    "C": outcomes <= {"rest"},
    "D": outcomes <= {"rest", "uniform acceleration right"},  # 'accelerating right' includes uniform acceleration
}
print("statement holds in every admissible case:", always)
assert [k for k, v in always.items() if v] == ["D"]
print("ANSWER: D")

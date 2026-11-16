"""Q69: autosomal recessive disease, incidence 1/20000. An unaffected couple already has an
affected child -> both parents must be carriers (Aa). Next child affected?"""
from fractions import Fraction as F
from itertools import product
from math import sqrt

# Mendelian cross Aa x Aa
kids = [a + b for a, b in product("Aa", "Aa")]
p_aff = F(sum(k == "aa" for k in kids), len(kids))
print("Aa x Aa offspring:", kids, "-> P(aa) =", p_aff)

# population numbers only matter for a couple whose genotypes are unknown (distractor)
q = sqrt(1 / 20000); p = 1 - q
carrier_given_normal = 2 * p * q / (1 - q * q)
print(f"q = {q:.5f}, P(carrier | unaffected) = {carrier_given_normal:.5f} ~ 1/{1/carrier_given_normal:.0f}")
random_couple = carrier_given_normal ** 2 / 4
print(f"random unaffected couple, first child affected: {random_couple:.3e} ~ 1/{1/random_couple:.0f} (close to option C)")
assert p_aff == F(1, 4)
print("ANSWER: B (1/4)")

"""Brute-force search for alternative 'natural' rules per option.
For each option we fill the blank, then test a battery of exam-style rule families
on the full sequence. A family only counts if it leaves >= MINCHK verifications
beyond its free parameters. Output: per option, the rule families it satisfies."""
from fractions import Fraction as F
import itertools, sys

MINCHK = 2

def diffs(s): return [s[i+1]-s[i] for i in range(len(s)-1)]
def sums(s): return [s[i+1]+s[i] for i in range(len(s)-1)]
def ratios(s):
    if any(x == 0 for x in s[:-1]): return None
    return [F(s[i+1])/F(s[i]) for i in range(len(s)-1)]

def base_patterns(s):
    """Return list of (name, checks) for simple patterns the whole seq s satisfies."""
    out = []
    L = len(s)
    if L >= 3 and all(x == s[0] for x in s):
        out.append(("const=%s" % s[0], L-1))
    if L >= 3:
        d = diffs(s)
        if all(x == d[0] for x in d) and d[0] != 0:
            out.append(("arith(d=%s)" % d[0], L-2))
    if L >= 3 and all(x != 0 for x in s):
        r = ratios(s)
        if r and all(x == r[0] for x in r) and r[0] not in (0, 1):
            out.append(("geom(r=%s)" % r[0], L-2))
    if L >= 4:
        if all(s[i] == s[i-1]+s[i-2] for i in range(2, L)):
            out.append(("fib-like", L-2))
    # powers (i+off)^k + c, also -(...)
    for k in (2, 3):
        for off in range(-3, 8):
            for c in range(-6, 7):
                for sg in (1, -1):
                    if all(s[i] == sg*((i+off)**k) + c for i in range(L)):
                        if L-2 >= 1:
                            out.append(("%s(n+%d)^%d%+d" % ('' if sg == 1 else '-', off, k, c), L-2))
    # (i+off)^k + (-1)^i*c alternating correction
    for k in (2, 3):
        for off in range(-3, 8):
            for c in range(1, 6):
                for ph in (0, 1):
                    if all(s[i] == (i+off)**k + c*(-1)**(i+ph) for i in range(L)):
                        out.append(("(n+%d)^%d +-%d alt" % (off, k, c), L-2))
    # primes consecutive
    P = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
    for st in range(len(P)-L+1):
        if list(s) == P[st:st+L]:
            out.append(("consecutive primes", L-1))
    if L >= 4 and all(s[i] == s[i-2] for i in range(2, L)):
        out.append(("period-2", L-2))
    return out

def transforms(s):
    """Yield (name, derived sequence, extra_params)."""
    yield ("diff", diffs(s), 1)
    r = ratios(s)
    if r is not None:
        yield ("ratio", r, 1)
    yield ("sum2", sums(s), 1)
    if len(s) >= 6:
        yield ("odd-pos", s[0::2], 0)
        yield ("even-pos", s[1::2], 0)
    # a(n) - p*a(n-1) for nice p  (linear recurrence with simple remainder)
    for p in [F(x, 2) for x in range(-8, 9)] + [F(x, 3) for x in (-2, -1, 1, 2, 4, 5)]:
        if p in (0, 1):
            continue
        yield ("a(n)-%s*a(n-1)" % p, [F(s[i])-p*s[i-1] for i in range(1, len(s))], 1)
    # a(n) - a(n-1) - a(n-2), a(n) - a(n-1) - 2a(n-2), etc
    for p, q in itertools.product([F(x, 2) for x in range(-6, 7)], repeat=2):
        if q == 0 or (p, q) == (1, 1):
            pass
        if q == 0:
            continue
        yield ("a(n)-%s*a(n-1)-%s*a(n-2)" % (p, q), [F(s[i])-p*s[i-1]-q*s[i-2] for i in range(2, len(s))], 2)
    yield ("a(n)-a(n-1)*a(n-2)", [s[i]-s[i-1]*s[i-2] for i in range(2, len(s))], 2)
    yield ("a(n)-a(n-1)^2", [s[i]-s[i-1]**2 for i in range(1, len(s))], 1)
    yield ("a(n)+a(n-1)", [s[i]+s[i-1] for i in range(1, len(s))], 1)
    yield ("a(n)*a(n-1)", [s[i]*s[i-1] for i in range(1, len(s))], 1)
    # a(n) - n^k
    for k in (2, 3):
        for off in range(-1, 3):
            yield ("a(n)-(n+%d)^%d" % (off, k), [s[i]-(i+off)**k for i in range(len(s))], 0)
    # a(n) / n
    yield ("a(n)*(n)", [F(s[i])*(i+1) for i in range(len(s))], 0)
    yield ("a(n)/(n)", [F(s[i])/(i+1) for i in range(len(s))], 0)

def explain(s, depth=2):
    res = []
    for name, chk in base_patterns(s):
        if chk >= MINCHK:
            res.append((name, chk))
    if depth == 0:
        return res
    for tname, t, extra in transforms(s):
        if len(t) < 3:
            continue
        for name, chk in explain(t, depth-1):
            c = chk  # checks counted on derived seq already
            if c >= MINCHK:
                res.append((tname + " -> " + name, c))
    return res

def run(name, known, blank, options, depth=2, show=8):
    print("=" * 70)
    print(name, known, "blank at", blank)
    for letter, val in options.items():
        s = list(known)
        s.insert(blank, val)
        ex = explain(s, depth)
        # dedupe
        seen = []
        for e in ex:
            if e[0] not in [x[0] for x in seen]:
                seen.append(e)
        print("  %s=%s : %d rules" % (letter, val, len(seen)))
        for e in seen[:show]:
            print("        ", e)

if __name__ == "__main__":
    cases = {
        "N001": ([1, 2, 6, 16, 44, 120], None, {"A": 164, "B": 176, "C": 240, "D": 328}),
        "N002": ([11, 27, 51, 87, 141], None, {"A": 222, "B": 231, "C": 259, "D": 286}),
        "N004": ([F(-16, 10), -4, -6, -3, F(3, 2)], None, {"A": F(-9, 4), "B": F(-3, 2), "C": F(3, 2), "D": F(15, 4)}),
        "N005": ([38, 6, 22, 14, 16], 4, {"A": 10, "B": 12, "C": 18, "D": 20}),
        "N006": ([9, 6, 5, F(9, 2), F(21, 5)], None, {"A": 4, "B": F(18, 5), "C": 3, "D": F(27, 10)}),
        "N007": ([10, 3, 13, 1, 14, 2, 16, 9], None, {"A": 23, "B": 24, "C": 25, "D": 26}),
        "N008sq": ([4, 9, 16, 27, 46], None, {"A": 64, "B": 80, "C": 81, "D": 84}),
        "N009": ([11, 14, 26, 44, 65], None, {"A": 80, "B": 83, "C": 86, "D": 89}),
        "N011": ([-1, 2, 6, 21, 43], None, {"A": 61, "B": 75, "C": 82, "D": 98}),
        "N012": ([23, 34, 58, 93, 152], None, {"A": 176, "B": 206, "C": 246, "D": 296}),
        "N013": ([81, 27, 18, 18, 24], None, {"A": 36, "B": 40, "C": 44, "D": 48}),
        "N014": ([5, -7, 16, -50, 202], None, {"A": 1012, "B": -1012, "C": 1122, "D": -1122}),
        "N015": ([1, F(1, 3), F(5, 18), F(10, 27), F(55, 81)], None, {"A": F(35, 54), "B": F(385, 243), "C": F(455, 486), "D": F(745, 729)}),
        "N016": ([1, 0, 1, 5, 4, 5, 9], None, {"A": 8, "B": 9, "C": 10, "D": 11}),
        "N018": ([3, 5, 17, 39, 71], None, {"A": 107, "B": 113, "C": 121, "D": 135}),
        "N019": ([-6, -2, -10, 6, -26], None, {"A": -90, "B": 90, "C": -38, "D": 38}),
        "N021": ([2, 5, 14, 35, 74], None, {"A": 88, "B": 105, "C": 126, "D": 137}),
        "N023": ([0, 6, 24, 60, 120], None, {"A": 200, "B": 210, "C": 220, "D": 230}),
        "N025": ([0, 2, 6, 12, 20], 1, {"A": -1, "B": 0, "C": 1, "D": 2}),
        "N026": ([1, 3, F(7, 2), F(5, 2), F(31, 24)], None, {"A": F(8, 15), "B": F(21, 40), "C": F(127, 120), "D": 5}),
        "N027": ([24, 14, 26, 33, 46], None, {"A": 56, "B": F(125, 2), "C": 66, "D": F(143, 2)}),
        "N028": ([3, 5, 20, 4, 6, 30, 7, 9, 72, 12, 14], None, {"A": 143, "B": 168, "C": 177, "D": 182}),
        "N030": ([2, 13, 25, 39, 56], None, {"A": 66, "B": 77, "C": 78, "D": 89}),
    }
    sel = sys.argv[1:] or list(cases)
    for k in sel:
        known, blank, opts = cases[k]
        run(k, known, len(known) if blank is None else blank, opts)

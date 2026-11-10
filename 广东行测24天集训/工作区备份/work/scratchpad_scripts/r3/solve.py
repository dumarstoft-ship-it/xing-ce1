"""Independent solve of D01-N001..N030 (number series).
Each entry: known terms, options, a rule function that, given a candidate list
(known terms with the blank filled), returns True iff the whole list obeys the rule.
We report which options satisfy each rule (want exactly one)."""
from fractions import Fraction as F
import math

def ok_all(seq, pred):
    return all(pred(seq, i) for i in range(len(seq)))

def check(name, known, blank_pos, options, rules):
    print(f"== {name}")
    for rname, rule in rules:
        hits = []
        for letter, val in options.items():
            seq = list(known)
            seq.insert(blank_pos, val)
            try:
                if rule(seq):
                    hits.append(letter)
            except Exception as e:
                pass
        print(f"   rule[{rname}] -> options satisfying: {hits}")

def diffs(s):
    return [s[i+1]-s[i] for i in range(len(s)-1)]

def is_arith(s):
    d = diffs(s)
    return all(x == d[0] for x in d)

def is_geom(s):
    return all(s[i] != 0 for i in range(len(s)-1)) and all(F(s[i+1], 1)/s[i] == F(s[1], 1)/s[0] for i in range(len(s)-1))

END = 10**9  # sentinel meaning append at end

def run():
    # N001
    k = [1, 2, 6, 16, 44, 120]
    o = {"A": 164, "B": 176, "C": 240, "D": 328}
    check("N001", k, len(k), o, [
        ("a_n = 2(a_{n-1}+a_{n-2})", lambda s: all(s[i] == 2*(s[i-1]+s[i-2]) for i in range(2, len(s)))),
    ])
    # N002
    k = [11, 27, 51, 87, 141]
    o = {"A": 222, "B": 231, "C": 259, "D": 286}
    check("N002", k, len(k), o, [
        ("diffs geometric x1.5", lambda s: is_geom(diffs(s))),
        ("a_n = 1.5a_{n-1}+10.5", lambda s: all(F(s[i]) == F(3, 2)*s[i-1] + F(21, 2) for i in range(1, len(s)))),
    ])
    # N003
    k = [12, 25, 310, 417]
    o = {"A": 521, "B": 526, "C": 632, "D": 647}
    def n003(s):
        for n, v in enumerate(s, start=1):
            st = str(v)
            if not st.startswith(str(n)):
                return False
            if int(st[len(str(n)):]) != n*n + 1:
                return False
        return True
    check("N003", k, len(k), o, [("split: n | n^2+1", n003)])
    # N004
    k = [F(-16, 10), F(-4), F(-6), F(-3), F(15, 10)]
    o = {"A": F(-225, 100), "B": F(-15, 10), "C": F(15, 10), "D": F(375, 100)}
    check("N004", k, len(k), o, [
        ("ratios arithmetic (2.5,1.5,0.5,-0.5,...)", lambda s: is_arith([s[i+1]/s[i] for i in range(len(s)-1)])),
    ])
    # N005  blank at index 4, last term 16 after
    k = [38, 6, 22, 14, 16]
    o = {"A": 10, "B": 12, "C": 18, "D": 20}
    check("N005", k, 4, o, [
        ("a_n = (a_{n-1}+a_{n-2})/2", lambda s: all(F(s[i]) == F(s[i-1]+s[i-2], 2) for i in range(2, len(s)))),
    ])
    # N006
    k = [F(9), F(6), F(5), F(9, 2), F(21, 5)]
    o = {"A": F(4), "B": F(18, 5), "C": F(3), "D": F(27, 10)}
    check("N006", k, len(k), o, [
        ("a_n = 3(n+2)/n = (9,12,15,...)/(1,2,3,...)", lambda s: all(s[i] == F(3*(i+3), i+1) for i in range(len(s)))),
    ])
    # N007
    k = [10, 3, 13, 1, 14, 2, 16, 9]
    o = {"A": 23, "B": 24, "C": 25, "D": 26}
    check("N007", k, len(k), o, [
        ("odd-position term = sum of previous two", lambda s: all(s[i] == s[i-1]+s[i-2] for i in range(2, len(s), 2))),
    ])
    # N008 work with squares
    k = [4, 9, 16, 27, 46]
    o = {"A": 64, "B": 80, "C": 81, "D": 84}
    check("N008 (radicands)", k, len(k), o, [
        ("2nd diffs geometric x2", lambda s: is_geom(diffs(diffs(s)))),
        ("diffs d_{n}=2d_{n-1}-3", lambda s: all(diffs(s)[i] == 2*diffs(s)[i-1]-3 for i in range(1, len(diffs(s))))),
    ])
    # N009
    k = [11, 14, 26, 44, 65]
    o = {"A": 80, "B": 83, "C": 86, "D": 89}
    check("N009", k, len(k), o, [
        ("2nd diffs arithmetic (9,6,3,0)", lambda s: is_arith(diffs(diffs(s)))),
    ])
    # N010
    k = [12, 311, 7, 234, 83]
    o = {"A": 152, "B": 94, "C": 47, "D": 15}
    ds = lambda v: sum(int(c) for c in str(v))
    check("N010", k, len(k), o, [
        ("digit sums arithmetic 3,5,7,9,11,13", lambda s: is_arith([ds(v) for v in s])),
    ])
    # N011
    k = [-1, 2, 6, 21, 43]
    o = {"A": 61, "B": 75, "C": 82, "D": 98}
    check("N011", k, len(k), o, [
        ("a_n + a_{n+1} = n^3", lambda s: all(s[i]+s[i+1] == (i+1)**3 for i in range(len(s)-1))),
    ])
    # N012
    k = [23, 34, 58, 93, 152]
    o = {"A": 176, "B": 206, "C": 246, "D": 296}
    check("N012", k, len(k), o, [
        ("a_n = a_{n-1}+a_{n-2}+1", lambda s: all(s[i] == s[i-1]+s[i-2]+1 for i in range(2, len(s)))),
    ])
    # N013
    k = [81, 27, 18, 18, 24]
    o = {"A": 36, "B": 40, "C": 44, "D": 48}
    check("N013", k, len(k), o, [
        ("ratios 1/3,2/3,3/3,4/3,5/3", lambda s: all(F(s[i+1], s[i]) == F(i+1, 3) for i in range(len(s)-1))),
    ])
    # N014
    k = [5, -7, 16, -50, 202]
    o = {"A": 1012, "B": -1012, "C": 1122, "D": -1122}
    check("N014", k, len(k), o, [
        ("a_{n+1} = -n*a_n + 2(-1)^n", lambda s: all(s[i+1] == -(i+1)*s[i] + 2*(-1)**(i+1) for i in range(len(s)-1))),
    ])
    # N015
    k = [F(1), F(1, 3), F(5, 18), F(10, 27), F(55, 81)]
    o = {"A": F(35, 54), "B": F(385, 243), "C": F(455, 486), "D": F(745, 729)}
    check("N015", k, len(k), o, [
        ("ratios 2/6,5/6,8/6,11/6,... arithmetic", lambda s: is_arith([s[i+1]/s[i] for i in range(len(s)-1)])),
    ])
    # N016
    k = [1, 0, 1, 5, 4, 5, 9]
    o = {"A": 8, "B": 9, "C": 10, "D": 11}
    check("N016", k, len(k), o, [
        ("a_n = a_{n-3}+4", lambda s: all(s[i] == s[i-3]+4 for i in range(3, len(s)))),
    ])
    # N017  decimal - integer = 12,15,18,...
    k = [(1, 13), (3, 18), (7, 25), (4, 25), (9, 33)]
    o = {"A": (6, 34), "B": (8, 35), "C": (10, 43), "D": (12, 45)}
    check("N017", k, len(k), o, [
        ("decimal-integer arithmetic (12,15,18,21,24)", lambda s: is_arith([b-a for a, b in s])),
    ])
    # N018
    k = [3, 5, 17, 39, 71]
    o = {"A": 107, "B": 113, "C": 121, "D": 135}
    check("N018", k, len(k), o, [
        ("2nd diffs constant 10", lambda s: is_arith(diffs(s))),
    ])
    # N019
    k = [-6, -2, -10, 6, -26]
    o = {"A": -90, "B": 90, "C": -38, "D": 38}
    check("N019", k, len(k), o, [
        ("diffs geometric x(-2)", lambda s: is_geom(diffs(s))),
        ("a_n = -2a_{n-1}-14", lambda s: all(s[i] == -2*s[i-1]-14 for i in range(1, len(s)))),
        ("a_n = 2a_{n-2}-a_{n-1}", lambda s: all(s[i] == 2*s[i-2]-s[i-1] for i in range(2, len(s)))),
    ])
    # N020
    k = [(21, 98), (18, 77), (17, 49), (14, 55)]
    o = {"A": (12, 26), "B": (13, 66), "C": (14, 26), "D": (15, 66)}
    check("N020", k, len(k), o, [
        ("integer diffs alternate -3,-1", lambda s: [s[i+1][0]-s[i][0] for i in range(len(s)-1)] == [-3, -1, -3, -1][:len(s)-1]),
        ("int(n+2) = digitsum(dec(n))", lambda s: all(s[i+2][0] == ds(s[i][1]) for i in range(len(s)-2))),
    ])
    # N021
    k = [2, 5, 14, 35, 74]
    o = {"A": 88, "B": 105, "C": 126, "D": 137}
    check("N021", k, len(k), o, [
        ("(n-1)^3 + 2n", lambda s: all(s[i] == i**3 + 2*(i+1) for i in range(len(s)))),
        ("3rd diffs constant", lambda s: is_arith(diffs(diffs(s)))),
    ])
    # N022
    k = [(3, 2), (5, 5), (11, 9), (19, 21), (43, 37)]
    o = {"A": (73, 89), "B": (75, 85), "C": (85, 73), "D": (89, 75)}
    check("N022", k, len(k), o, [
        ("int+dec doubles 5,10,20,40,80,160", lambda s: is_geom([a+b for a, b in s])),
        ("int-dec diffs geometric x(-2)", lambda s: is_geom(diffs([a-b for a, b in s]))),
    ])
    # N023
    k = [0, 6, 24, 60, 120]
    o = {"A": 200, "B": 210, "C": 220, "D": 230}
    check("N023", k, len(k), o, [
        ("n^3 - n", lambda s: all(s[i] == (i+1)**3 - (i+1) for i in range(len(s)))),
    ])
    # N024
    k = [(1, 1), (2, 3), (5, 8), (13, 21), (34, 55)]
    o = {"A": (89, 144), "B": (89, 151), "C": (99, 144), "D": (99, 151)}
    def n024(s):
        flat = [x for p in s for x in p]
        return all(flat[i] == flat[i-1]+flat[i-2] for i in range(2, len(flat)))
    check("N024", k, len(k), o, [("concatenated Fibonacci", n024)])
    # N025 blank at index 1
    k = [0, 2, 6, 12, 20]
    o = {"A": -1, "B": 0, "C": 1, "D": 2}
    check("N025", k, 1, o, [
        ("(n-1)(n-2)", lambda s: all(s[i] == i*(i-1) for i in range(len(s)))),
        ("diffs arithmetic", lambda s: is_arith(diffs(s))),
    ])
    # N026
    k = [F(1), F(3), F(7, 2), F(5, 2), F(31, 24)]
    o = {"A": F(8, 15), "B": F(21, 40), "C": F(127, 120), "D": F(5)}
    check("N026", k, len(k), o, [
        ("(2^n - 1)/(n-1)!", lambda s: all(s[i] == F(2**(i+1)-1, math.factorial(i)) for i in range(len(s)))),
    ])
    # N027
    k = [F(24), F(14), F(26), F(33), F(46)]
    o = {"A": F(56), "B": F(125, 2), "C": F(66), "D": F(143, 2)}
    check("N027", k, len(k), o, [
        ("a_n = a_{n-1} + a_{n-2}/2", lambda s: all(s[i] == s[i-1] + s[i-2]/2 for i in range(2, len(s)))),
    ])
    # N028
    k = [3, 5, 20, 4, 6, 30, 7, 9, 72, 12, 14]
    o = {"A": 143, "B": 168, "C": 177, "D": 182}
    check("N028", k, len(k), o, [
        ("third = (first+1)*second", lambda s: all(s[i+2] == (s[i]+1)*s[i+1] for i in range(0, len(s), 3))),
        ("third = (second-1)*second", lambda s: all(s[i+2] == (s[i+1]-1)*s[i+1] for i in range(0, len(s), 3))),
        ("third = first*second (trap)", lambda s: all(s[i+2] == s[i]*s[i+1] for i in range(0, len(s), 3))),
    ])
    # N029
    k = [(2, 5), (2, 4), (8, 9), (56, 13), (560, 22)]
    o = {"A": (5600, 36), "B": (6140, 35), "C": (6720, 36), "D": (7280, 35)}
    check("N029", k, len(k), o, [
        ("int ratios 1,4,7,10,13 and dec Fibonacci-like", lambda s: is_arith([F(s[i+1][0], s[i][0]) for i in range(len(s)-1)]) and all(s[i][1] == s[i-1][1]+s[i-2][1] for i in range(2, len(s)))),
        ("int ratios only", lambda s: is_arith([F(s[i+1][0], s[i][0]) for i in range(len(s)-1)])),
        ("dec only", lambda s: all(s[i][1] == s[i-1][1]+s[i-2][1] for i in range(2, len(s)))),
    ])
    # N030
    k = [2, 13, 25, 39, 56]
    o = {"A": 66, "B": 77, "C": 78, "D": 89}
    check("N030", k, len(k), o, [
        ("2nd diffs arithmetic (1,2,3,4)", lambda s: is_arith(diffs(diffs(s)))),
        ("2nd diffs Fibonacci-like (1,2,3,5)", lambda s: all(diffs(diffs(s))[i] == diffs(diffs(s))[i-1]+diffs(diffs(s))[i-2] for i in range(2, len(diffs(diffs(s)))))),
    ])

run()

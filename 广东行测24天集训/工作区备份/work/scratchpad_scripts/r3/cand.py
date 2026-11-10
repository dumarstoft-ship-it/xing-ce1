import sys
sys.path.insert(0, '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/r3')
from altsearch import run
from fractions import Fraction as F
cases = {
 "ZJ2021A-53": ([80, 70, 62, 58, 70], 4, {"A": 59, "B": 60, "C": 61, "D": 63}),
 "ZJ2023A-53": ([163, 47, 22, -19, 79], 5, {"A": -256, "B": -115, "C": 181, "D": 223}),
 "SZ2023-48": ([5, 6, 9, 13, 15, 18, 19], 7, {"A": 27, "B": 26, "C": 25, "D": 24}),
 "SZ2020SW-6": ([2, 3, 7, 22, 155], 5, {"A": 3411, "B": 2988, "C": 1188, "D": 741}),
}
for k, (known, blank, opts) in cases.items():
    run(k, known, blank, opts, depth=2, show=5)
# explicit rule checks
print("ZJ2021A-53 2nd diffs:", [[(s:= [80,70,62,58,x,70]) and [s[i]-s[i+1] for i in range(5)]] for x in (59,60,61,63)])
for x in (59,60,61,63):
    s=[80,70,62,58,x,70]; d=[s[i]-s[i+1] for i in range(5)]; dd=[d[i]-d[i+1] for i in range(4)]
    print('  opt',x,'diffs',d,'2nd',dd)
for x in (-256,-115,181,223):
    s=[163,47,22,-19,79,x]; print('ZJ2023A-53 opt',x, all(s[i]==s[i-2]-3*s[i-1] for i in range(2,6)))
for x in (27,26,25,24):
    s=[5,6,9,13,15,18,19,x]; print('SZ2023-48 opt',x,'pair sums',[s[i]+s[i+1] for i in range(0,8,2)])
for x in (3411,2988,1188,741):
    s=[2,3,7,22,155,x]; print('SZ2020SW-6 opt',x, all(s[i]==s[i-1]*s[i-2]+1 for i in range(2,6)))

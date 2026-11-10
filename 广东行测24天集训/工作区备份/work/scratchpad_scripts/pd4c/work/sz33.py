from itertools import permutations
col = '黑白蓝红黄'
A = tuple('黑白蓝红黄')
P = list(permutations(col))
M = []
for B in P:
    if A[4] != B[1]: continue
    if any(A[i] == B[i] for i in range(5)): continue
    for C in P:
        if C[1] != A[0] or C[4] != B[3]: continue
        if any(C[i] in (A[i], B[i]) for i in range(5)): continue
        for D in P:
            if D[2] != C[0] or D[4] != C[2]: continue
            if any(D[i] in (A[i], B[i], C[i]) for i in range(5)): continue
            for E in P:
                if B[3] != E[2]: continue
                if any(E[i] in (A[i], B[i], C[i], D[i]) for i in range(5)): continue
                M.append((B, C, D, E))
print(len(M))
for m in M: print(' 乙', ''.join(m[0]), '丙', ''.join(m[1]), '丁', ''.join(m[2]), '戊', ''.join(m[3]))
opts = {'A': (0, '白黄红黑蓝'), 'B': (1, '红黑黄白蓝'), 'C': (2, '白蓝黄黑红'), 'D': (3, '蓝黑白黄红')}
for k, (i, s) in opts.items():
    v = [''.join(m[i]) == s for m in M]
    print(k, 'ALL' if all(v) else 'SOME' if any(v) else 'NONE')

from itertools import combinations, permutations, product
S = [frozenset(c) for c in combinations(range(1, 8), 4) if sum(c) == 17]
print('sets', [sorted(s) for s in S])
# R1 set reading (exact): |Q∩D|=2, Q\D ⊆ C with |Q∩C|=2 exactly, |D∩C|=1
for exact in (True, False):
    sol = []
    for D, C, Q in product(S, repeat=3):   # D=盯得准 C=出得快 Q=敲得狠
        a = Q & D; b = Q & C
        if exact:
            ok = len(a) == 2 and len(b) == 2 and not (a & b) and len(D & C) == 1
        else:  # loose: Q 可拆成两两：两次与盯相同、其余两次与出相同（允许还有别的重合）；盯与出恰有 1 个相同
            ok = any(set(x) <= D and (Q - set(x)) <= C for x in combinations(Q, 2)) and len(D & C) == 1
        if ok: sol.append((sorted(D), sorted(C), sorted(Q)))
    print('exact' if exact else 'loose', len(sol))
    for s in sol: print('   盯', s[0], '出', s[1], '敲', s[2], 'common', sorted(set(s[0]) & set(s[1])))
# R2 round reading: sequences
seqs = [p for s in S for p in permutations(s)]
cnt = 0; commons = set(); ex = {}
for D in seqs:
    for C in seqs:
        same_dc = sum(1 for i in range(4) if D[i] == C[i])
        if same_dc != 1: continue
        for Q in seqs:
            qd = [i for i in range(4) if Q[i] == D[i]]; qc = [i for i in range(4) if Q[i] == C[i]]
            # 敲 有 2 次与盯相同，其余 2 次与出相同
            if len(qd) == 2 and len(qc) == 2 and not set(qd) & set(qc):
                cnt += 1; com = frozenset(set(D) & set(C)); commons.add(com); ex.setdefault(com, (D, C, Q))
print('round reading models', cnt, 'common sets', [sorted(c) for c in commons])
for c, e in ex.items(): print('  ', sorted(c), e)

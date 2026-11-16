# 第45题：总数<100，男女4:7；党员占3/5；党员男比非党员男多10人。党员中女性几人？
sols = []
for n in range(1, 100):
    if n % 11 or n % 5:
        continue
    m, f = n * 4 // 11, n * 7 // 11
    party = n * 3 // 5
    for pm in range(0, m + 1):
        nm = m - pm
        if pm - nm != 10:
            continue
        pf = party - pm
        nf = (n - party) - nm
        if pf < 0 or nf < 0:
            continue
        sols.append((n, m, f, party, pm, nm, pf, nf))
for s in sols:
    print("总%d 男%d 女%d 党员%d 党员男%d 非党员男%d 党员女%d 非党员女%d" % s)
assert len(sols) == 1 and sols[0][6] == 18
print("答案: C")

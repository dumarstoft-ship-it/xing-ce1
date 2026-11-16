# 第40题：男女6:1，总数≤100；外省占12.5%，外省男女4:3。本省女生比外省男生多几人？
sols = []
for n in range(1, 101):
    if n % 7 or n % 8:
        continue
    out = n // 8
    if out % 7:
        continue
    male, female = n * 6 // 7, n // 7
    out_m, out_f = out * 4 // 7, out * 3 // 7
    local_f = female - out_f
    sols.append((n, male, female, out, out_m, out_f, local_f, local_f - out_m))
for s in sols:
    print("总%d 男%d 女%d 外省%d(男%d女%d) 本省女%d  差%d" % s)
assert len(sols) == 1 and sols[0][-1] == 1
print("答案: A（C=5 是本省女生人数，B=3 是外省女生，D=8 是女生总数）")

# 第41题：上午丁=1.5×张；下午丁=上午丁-6=下午张-12；四项合计110。求张总量。
sols = []
for zs in range(0, 111):          # 张上午
    for ds in range(0, 111):      # 丁上午
        if 2 * ds != 3 * zs:
            continue
        dx = ds - 6
        zx = dx + 12
        if dx < 0 or zs + ds + dx + zx != 110:
            continue
        sols.append((zs, ds, zx, dx))
print("(张上午, 丁上午, 张下午, 丁下午):", sols)
assert len(sols) == 1
zs, ds, zx, dx = sols[0]
print("张共", zs + zx, "丁共", ds + dx)
assert zs + zx == 56
print("答案: D（B=54 是丁老师的总量）")

"""M11 第45题：18个奖品分成数量互不相同的4份（每份至少1个），一份最多几个。 选项 A6 B8 C12 D15"""
best = 0
for a in range(1, 19):
    for b in range(a + 1, 19):
        for c in range(b + 1, 19):
            d = 18 - a - b - c
            if d > c:
                best = max(best, d)
print('最多', best)
assert best == 12
print('若允许某份为0：', 18 - (0 + 1 + 2), '（D项）')

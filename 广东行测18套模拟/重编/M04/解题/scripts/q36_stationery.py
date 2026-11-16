"""第36题：9a + 14b + 21c = 141，三种文具各若干（a,b,c ≥ 1），求 b 的最大值。"""
sols = []
for a in range(1, 141 // 9 + 1):
    for b in range(1, 141 // 14 + 1):
        for c in range(1, 141 // 21 + 1):
            if 9 * a + 14 * b + 21 * c == 141:
                sols.append((a, b, c))
print("全部正整数解 (笔记本, 水彩笔, 文具盒):", sols)
bmax = max(s[1] for s in sols)
print("水彩笔最多:", bmax, "对应解:", [s for s in sols if s[1] == bmax])
print("b 的可能取值:", sorted({s[1] for s in sols}), "（均为3的倍数）")
# 若允许某种为0（不符合“三种文具各若干”），看看会怎样
sols0 = [(a, b, c) for a in range(0, 16) for b in range(0, 11) for c in range(0, 7) if 9 * a + 14 * b + 21 * c == 141]
print("若允许为0的解:", sols0, "b最大", max(s[1] for s in sols0))
options = {"A": 3, "B": 4, "C": 6, "D": 10}
hits = [k for k, v in options.items() if v == bmax]
assert hits == ["C"]
print("答案:", hits)

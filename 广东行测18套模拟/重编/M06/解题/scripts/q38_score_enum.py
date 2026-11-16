# 第38题：5人平均83（总分415），整数、互不相同、百分制；第3高+第4高=160；
# 其余相邻名次（1-2、2-3、4-5）分差不超过5。求第3高最低多少。
sols = []
for s3 in range(0, 101):
    s4 = 160 - s3
    if not (0 <= s4 < s3 <= 100):
        continue
    for s2 in range(s3 + 1, min(s3 + 5, 100) + 1):
        for s1 in range(s2 + 1, min(s2 + 5, 100) + 1):
            s5 = 415 - s1 - s2 - s3 - s4
            if 0 <= s5 < s4 and s4 - s5 <= 5:
                sols.append((s1, s2, s3, s4, s5))
mins3 = min(s[2] for s in sols)
print("可行方案数", len(sols), "第3高最小值", mins3)
print("取到最小值的方案:", [s for s in sols if s[2] == mins3])
print("第3高可取的值:", sorted(set(s[2] for s in sols)))
assert mins3 == 81
# 不要求互不相同时（第3、4名同分80）才会得到80
print("若允许s3=s4=80：", 80 + 80 == 160, "但违反“各不相同”")
print("答案: B")

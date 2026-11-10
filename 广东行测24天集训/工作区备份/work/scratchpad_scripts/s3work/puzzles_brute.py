from itertools import combinations, permutations

print("== X13 选4人发言")
P = ["甲","乙","丙","丁","戊","己","庚"]
sols = []
for c in combinations(P, 4):
    s = set(c)
    c1 = not ("甲" in s and "丁" in s)
    c2 = (not ("丙" in s or "戊" in s)) or ("甲" in s and "己" not in s)
    c3 = (not ("乙" in s or "庚" in s)) or ("丁" in s and "甲" not in s)
    if c1 and c2 and c3: sols.append(c)
print("  满足条件的方案:", sols)
opts = {"A":{"乙","庚"},"B":{"丙","丁"},"C":{"己","戊"},"D":{"甲","乙"}}
for k,v in opts.items():
    print(f"  {k} 在所有方案中成立? {all(v <= set(x) for x in sols)}")

print("== X14 四种作物面积排序 (数值越大面积越大)")
crops = ["紫薯","红薯","南瓜","玉米"]
sols = []
for perm in permutations(range(4)):
    a = dict(zip(crops, perm))   # 0..3, 3 最大
    big = max(a, key=a.get); small = min(a, key=a.get)
    c1 = (big == "紫薯") != (big == "南瓜")  # 要么...要么...
    c2 = (big != "紫薯") or (small == "红薯")
    given = a["红薯"] > a["玉米"]
    if c1 and c2 and given: sols.append(a)
for s in sols: print("  ", sorted(s, key=s.get, reverse=True))
checks = {
 "A 南瓜>玉米": lambda a: a["南瓜"]>a["玉米"],
 "B 紫薯>玉米": lambda a: a["紫薯"]>a["玉米"],
 "C 紫薯<红薯": lambda a: a["紫薯"]<a["红薯"],
 "D 玉米>南瓜": lambda a: a["玉米"]>a["南瓜"],
}
for k,f in checks.items():
    print(f"  {k}: 恒真 {all(f(a) for a in sols)}  可能 {any(f(a) for a in sols)}")

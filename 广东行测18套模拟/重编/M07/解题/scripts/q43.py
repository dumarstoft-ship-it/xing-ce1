# 第43题：年龄24,26,29,32,34,36；选3人依次汇报（排序）；平均年龄超过28（和>84），任两人年龄差不超过10
from itertools import combinations, permutations
ages = [24, 26, 29, 32, 34, 36]
good = [c for c in combinations(ages, 3) if sum(c) > 84 and max(c) - min(c) <= 10]
print(len(good), good)
arr = [p for p in permutations(ages, 3) if sum(p) > 84 and max(p) - min(p) <= 10]
print("汇报情况数", len(arr))
assert len(arr) == 78
# 口径检验：平均年龄等于28算不算“超过”；“不超过10”是否含10
ge = [c for c in combinations(ages, 3) if sum(c) >= 84 and max(c) - min(c) <= 10]
lt = [c for c in combinations(ages, 3) if sum(c) > 84 and max(c) - min(c) < 10]
print("若平均可等于28：", len(ge) * 6, "；若年龄差须小于10：", len(lt) * 6)
print("只算组合不排序：", len(good))

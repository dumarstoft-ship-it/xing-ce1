"""M05 第44题：步行街长1485米，左侧每隔15米、右侧每隔33米装垃圾桶，起点终点两端均装；
中间路段若同一位置两侧都要装，只在左侧装一个。逐米枚举位置计数。
"""
L = 1485
left = {x for x in range(0, L + 1) if x % 15 == 0}
right = {x for x in range(0, L + 1) if x % 33 == 0}
assert 0 in left and L in left and 0 in right and L in right   # 两端两侧都恰好落在安装点上
print("左侧个数:", len(left), "右侧个数:", len(right))

both_middle = sorted(x for x in left & right if 0 < x < L)
print("中间路段两侧重合的位置:", both_middle, "共", len(both_middle), "处")

total = len(left) + len(right) - len(both_middle)
print("总数（两端两侧都装，中间重合处只装左侧）:", total)
assert (len(left), len(right), len(both_middle), total) == (100, 46, 8, 138)

# 对照：若两端也只装一个（误把合并规则用于两端），得 136
alt = len(left) + len(right) - len(left & right)
print("对照：两端也合并时为", alt, "（A项，题干限定“中间路段”才合并，故不取）")
assert alt == 136
print("答案: B 138")

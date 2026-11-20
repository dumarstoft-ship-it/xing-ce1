"""S02 第35题：3×3数表 4 6 9 / 12 9 2 / 18 ? 3（题图已看）  选项 A3 B4 C5 D6
每行三数之积都是216。"""
rows = [(4, 6, 9), (12, 9, 2)]
assert all(a * b * c == 216 for a, b, c in rows)
ans = 216 // (18 * 3)
assert 18 * ans * 3 == 216
opts = {'A': 3, 'B': 4, 'C': 5, 'D': 6}
print('所求', ans, '答案：', [k for k, v in opts.items() if v == ans])
# 列方向无同样整齐的规律：各列积 4×12×18=864，6×9×?，9×2×3=54

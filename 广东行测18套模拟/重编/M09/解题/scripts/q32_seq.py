"""M09 第32题：35，71，53，17，62，（ ）  选项 A24 B26 C36 D38
核验：各项数字之和都等于8；另观察到35与53、71与17互为数字倒序，62的倒序26也在选项中。"""
seq = [35, 71, 53, 17, 62]
opts = {'A': 24, 'B': 26, 'C': 36, 'D': 38}
ds = lambda n: sum(map(int, str(n)))
print('各项数字和:', [ds(x) for x in seq])
assert all(ds(x) == 8 for x in seq)
ok = [k for k, v in opts.items() if ds(v) == 8]
print('选项数字和:', {k: ds(v) for k, v in opts.items()}, '满足=8的:', ok)
assert ok == ['B']
# 交叉：两位数中数字和为8且十位不为0的有 17,26,35,44,53,62,71,80；与已出现项不重复的选项只有26
print('倒序关系：', 35, '↔', 53, '；', 71, '↔', 17, '；', 62, '↔', int(str(62)[::-1]))
# 作差无规律（检查一下，避免漏掉别的规律）
print('一级差:', [b - a for a, b in zip(seq, seq[1:])])

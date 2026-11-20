"""S02 第33题：2，4，8，16，20，40，44，（ ）  选项 A48 B60 C64 D88
交替“×2、+4”：2×2=4，4+4=8，8×2=16，16+4=20，20×2=40，40+4=44，44×2=88。"""
seq = [2, 4, 8, 16, 20, 40, 44]
ops = [(lambda x: x * 2) if i % 2 == 0 else (lambda x: x + 4) for i in range(7)]
assert all(ops[i](seq[i]) == seq[i + 1] for i in range(6))
nxt = ops[6](seq[6])
opts = {'A': 48, 'B': 60, 'C': 64, 'D': 88}
print('下一项', nxt, '答案：', [k for k, v in opts.items() if v == nxt])
assert nxt == 88
# 两两分组 (2,4)(8,16)(20,40)(44,?) 组内后项是前项的2倍，同样得88
print('若只看前4项“×2”续写：', 16 * 2, '；只看最后的“+4”：', 44 + 4, '（A项）')

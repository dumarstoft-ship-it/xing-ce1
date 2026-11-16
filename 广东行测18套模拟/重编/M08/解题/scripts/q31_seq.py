"""M08 第31题：-3，4，0，9，7，（ ）  选项 A10 B14 C18 D22
核验：相邻两项之和为 1,4,9,16,25（平方数）；另用作差法交叉验证。"""
seq = [-3, 4, 0, 9, 7]
opts = {'A': 10, 'B': 14, 'C': 18, 'D': 22}
sums = [seq[i] + seq[i + 1] for i in range(len(seq) - 1)]
print('相邻两项和:', sums)
assert sums == [n * n for n in range(1, 5)]
ok_sum = [k for k, v in opts.items() if seq[-1] + v == 25]
print('满足“第5、6项之和=25”的选项:', ok_sum)
# 交叉验证：作差 7,-4,9,-2,? 奇数位 7,9,11 / 偶数位 -4,-2
diffs = [seq[i + 1] - seq[i] for i in range(len(seq) - 1)]
print('一级差:', diffs)
ok_diff = [k for k, v in opts.items() if v - seq[-1] == diffs[2] + (diffs[2] - diffs[0])]
print('作差法(差的奇数位 7,9,11)对应选项:', ok_diff)
assert ok_sum == ok_diff == ['C']
print('答案 C = 18')

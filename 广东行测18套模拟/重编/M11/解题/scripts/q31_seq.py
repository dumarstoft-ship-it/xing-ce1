"""M11 第31题：2、10、30、68、130、（ ）  选项 A222 B272 C300 D390
规律：n³+n（1+1、8+2、27+3、64+4、125+5）。"""
seq = [2, 10, 30, 68, 130]
opts = {'A': 222, 'B': 272, 'C': 300, 'D': 390}
assert all(a == n ** 3 + n for n, a in enumerate(seq, 1))
v1 = 6 ** 3 + 6
d1 = [b - a for a, b in zip(seq, seq[1:])]
d2 = [b - a for a, b in zip(d1, d1[1:])]
d3 = [b - a for a, b in zip(d2, d2[1:])]
print('一级差', d1, '二级差', d2, '三级差', d3)
v2 = seq[-1] + d1[-1] + d2[-1] + d3[-1]
assert v1 == v2 == 222
print('答案：', [k for k, v in opts.items() if v == v1])
# 若只看成 n³ 附近而用 n³+n² 等别的修正：6³+6²=252，不在选项中

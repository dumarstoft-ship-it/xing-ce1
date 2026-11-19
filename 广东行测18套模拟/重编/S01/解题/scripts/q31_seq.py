"""S01 第31题：49，510，611，712，（ ）  选项 A810 B811 C812 D813
机械拆分：4|9、5|10、6|11、7|12，前段与后段各自加1。"""
parts = [(4, 9), (5, 10), (6, 11), (7, 12)]
assert [int(f'{a}{b}') for a, b in parts] == [49, 510, 611, 712]
assert all(b == a + 5 for a, b in parts)
nxt = int(f'{8}{13}')
opts = {'A': 810, 'B': 811, 'C': 812, 'D': 813}
print('下一项', nxt, '答案：', [k for k, v in opts.items() if v == nxt])
assert nxt == 813

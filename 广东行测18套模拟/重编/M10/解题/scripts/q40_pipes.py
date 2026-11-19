"""M10 第40题：管材堆每层比上一层多1根；搬走99根后少了3层（最上面3层），剩余每层都少3根，剩10层，求剩余根数。
选项 A245 B265 C305 D325"""
opts = {'A': 245, 'B': 265, 'C': 305, 'D': 325}
sols = []
for a in range(1, 200):                  # a：原最上层根数
    for n in range(4, 60):               # n：原层数
        layers = [a + i for i in range(n)]
        removed = sum(layers[:3]) + 3 * (n - 3)
        remain = [x - 3 for x in layers[3:]]
        if removed == 99 and len(remain) == 10 and min(remain) > 0:
            sols.append((a, n, sum(remain), remain))
for s in sols:
    print('原最上层', s[0], '原层数', s[1], '剩余', s[2], s[3])
assert len(sols) == 1 and sols[0][2] == 265
a, n, tot, rem = sols[0]
# 剩余10层为22…31，与原堆最上面10层完全相同；也可用原总数364−99
assert rem == [a + i for i in range(10)] and sum(a + i for i in range(13)) - 99 == tot
print('答案：', [k for k, v in opts.items() if v == tot])

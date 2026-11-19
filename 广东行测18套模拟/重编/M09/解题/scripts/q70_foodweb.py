"""M09 第70题：食物网。题图箭头：甲→乙，乙→丙，甲→丁，甲→戊，乙→己，丙→己，丁→戊，戊→己。
核验：从生产者（无箭头指入）到最高级消费者（无箭头指出）枚举全部食物链；找既捕食又竞争的物种对。"""
edges = [('甲', '乙'), ('乙', '丙'), ('甲', '丁'), ('甲', '戊'), ('乙', '己'), ('丙', '己'), ('丁', '戊'), ('戊', '己')]
nodes = sorted({x for e in edges for x in e})
succ = {n: [b for a, b in edges if a == n] for n in nodes}
pred = {n: [a for a, b in edges if b == n] for n in nodes}
producers = [n for n in nodes if not pred[n]]
tops = [n for n in nodes if not succ[n]]
chains = []
def dfs(path):
    if not succ[path[-1]]:
        chains.append('→'.join(path)); return
    for nx in succ[path[-1]]:
        dfs(path + [nx])
for p in producers:
    dfs([p])
print('生产者', producers, '最高级消费者', tops)
print('食物链共', len(chains), '条：', chains)
assert len(chains) == 4                       # A 错
both = []
for a, b in edges:                            # b 捕食 a
    if set(pred[a]) & set(pred[b]):           # 二者有共同食物 → 竞争
        both.append((a, b, sorted(set(pred[a]) & set(pred[b]))))
print('既有捕食又有竞争的物种对（被捕食者, 捕食者, 共同食物）：', both)
assert ('丁', '戊', ['甲']) in both           # D 正确
# 营养级：己在各链中处于第三或第四营养级，是最高级消费者，个体数一般最少（B错）；
# 生态系统的能量最终来自太阳能，甲（生产者）只是固定太阳能的起点（C错）。

"""M10 第45题：60人答5题，答对人数45、36、54、48、52，4人全错，至少几人全对。 选项 A7 B9 C11 D13
下界：答错人次共15+24+6+12+8=65，4个全错者占去4×5=20，其余56人共答错45人次；
每个非全对者至少错1题，所以非全对者至多45人，全对者至少56−45=11人。
构造：让45人各只错1题即可取到11。"""
right = [45, 36, 54, 48, 52]
N, zero = 60, 4
wrong = [N - r for r in right]
rest_wrong = [w - zero for w in wrong]
assert min(rest_wrong) >= 0
lower = (N - zero) - sum(rest_wrong)
print('各题答错', wrong, '；去掉4个全错者后各题答错', rest_wrong, '共', sum(rest_wrong), '；全对至少', lower)
# 构造验证：4人全错；45人各错一题（按各题剩余错数分配）；其余全对
people = [[0] * 5 for _ in range(zero)]
for q, w in enumerate(rest_wrong):
    for _ in range(w):
        row = [1] * 5
        row[q] = 0
        people.append(row)
while len(people) < N:
    people.append([1] * 5)
assert len(people) == N
assert [sum(p[q] for p in people) for q in range(5)] == right
assert sum(1 for p in people if sum(p) == 0) == zero
allc = sum(1 for p in people if sum(p) == 5)
print('构造：全对', allc, '人，各题答对人数', [sum(p[q] for p in people) for q in range(5)])
assert allc == lower == 11
# 等价算法：答对人次235，56人中非全对者每人至多对4题 → 全对 ≥ 235−4×56 = 11
assert sum(right) - 4 * (N - zero) == 11

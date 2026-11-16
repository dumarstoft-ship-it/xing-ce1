# 第55题 枚举验证：5人各选1项活动（周边游Z/看电影K/做手工S），每项1-2人
from itertools import product

people = ['王', '李', '张', '赵', '刘']
acts = ['Z', 'K', 'S']   # Z=周边游 K=看电影 S=做手工


def ok(a):
    cnt = {x: list(a.values()).count(x) for x in acts}
    if any(not (1 <= cnt[x] <= 2) for x in acts):
        return False
    # (1) 小张或小赵选做手工或看电影 -> 小王选周边游
    if (a['张'] in 'SK' or a['赵'] in 'SK') and a['王'] != 'Z':
        return False
    # (2) 小赵或小刘选周边游或看电影 -> 小王或小李选做手工
    if (a['赵'] in 'ZK' or a['刘'] in 'ZK') and not (a['王'] == 'S' or a['李'] == 'S'):
        return False
    # (3) 小刘选做手工或小张选周边游 -> 小李和小赵选看电影
    if (a['刘'] == 'S' or a['张'] == 'Z') and not (a['李'] == 'K' and a['赵'] == 'K'):
        return False
    return True


sols = []
for combo in product(acts, repeat=5):
    a = dict(zip(people, combo))
    if a['赵'] == 'S' and ok(a):
        sols.append(a)

print('小赵选做手工时的全部可行方案：')
for s in sols:
    print('  ', s)

opts = {
    'A 小刘选择看电影': lambda a: a['刘'] == 'K',
    'B 小王选择周边游': lambda a: a['王'] == 'Z',
    'C 小李选择做手工': lambda a: a['李'] == 'S',
    'D 小张选择看电影': lambda a: a['张'] == 'K',
}
for k, f in opts.items():
    print(k, '一定为真' if all(f(s) for s in sols) else '不一定为真')

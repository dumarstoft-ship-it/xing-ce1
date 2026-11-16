# 第60题：枚举每个选项的选球方式下所有投篮顺序与命中情况，看能否恰好得9分
import itertools
VAL = {'大': 3, '中': 2, '小': 1}
opts = {'A 三次大球，两次中球': '大大大中中', 'B 两次大球，三次小球': '大大小小小',
        'C 一次大球，四次中球': '大中中中中', 'D 一次大球，四次小球': '大小小小小'}
for k, balls in opts.items():
    scores = set(); example = None
    for order in set(itertools.permutations(balls)):
        for hits in itertools.product((True, False), repeat=5):
            s = 0
            for i, (b, h) in enumerate(zip(order, hits)):
                if h: s += VAL[b]
                else: s += 0 if i == 0 else 1          # 第一次投不中0分，其余投不中鼓励1分
            scores.add(s)
            if s == 9 and example is None:
                example = (''.join(order), ''.join('中' if h else '空' for h in hits))
    print(f'{k}: 可能得分 {sorted(scores)}；能得9分: {9 in scores}' + (f'，例：顺序{example[0]} 命中{example[1]}' if example else ''))

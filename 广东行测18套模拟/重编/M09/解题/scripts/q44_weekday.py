"""M09 第44题：大门每2天清洁一次，消防每3天检查一次，绿化每5天养护一次，本周四三项同天完成，下一次同天是星期几？
选项 A星期一 B星期二 C星期六 D星期日
核验：逐日枚举，从周四（第0天）起找下一个同时是2、3、5倍数的天数，再换算星期。"""
from math import lcm
days = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
start = 3   # 星期四
d = next(t for t in range(1, 1000) if t % 2 == 0 and t % 3 == 0 and t % 5 == 0)
print('下一次同天：', d, '天后；最小公倍数', lcm(2, 3, 5))
w = days[(start + d) % 7]
print('是', w)
assert w == '星期六'
opts = {'A': '星期一', 'B': '星期二', 'C': '星期六', 'D': '星期日'}
print('答案：', [k for k, v in opts.items() if v == w])
# 易错：把“每2天、每3天、每5天”读成“每隔2天、3天、5天”（周期3、4、6）
d2 = lcm(3, 4, 6)
print('误读为每隔：', d2, '天后 →', days[(start + d2) % 7], [k for k, v in opts.items() if v == days[(start + d2) % 7]])

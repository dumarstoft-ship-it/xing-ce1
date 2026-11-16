# 第36题：甲乙共120人；甲男30%；乙男女相等；乙调10名男生到甲后两部门男生相等。求乙原有人数
sols = []
for x in range(0, 121):            # x = 甲人数
    y = 120 - x
    if (3 * x) % 10 or y % 2:      # 甲男 = 0.3x 为整数，乙男 = y/2 为整数
        continue
    ja, yi = 3 * x // 10, y // 2
    if yi >= 10 and ja + 10 == yi - 10:
        sols.append((x, y, ja, yi))
print(sols)                          # [(50, 70, 15, 35)]
assert len(sols) == 1 and sols[0][1] == 70
# 错误思路：只给甲加10、忘了乙要减10： 0.3x+10 = (120-x)/2 → x=62.5 不是整数；把甲的人数50当成答案→A

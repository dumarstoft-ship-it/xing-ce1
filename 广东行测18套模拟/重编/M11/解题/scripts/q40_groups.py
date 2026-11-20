"""M11 第40题：7男5女一组，剩8男；9男5女一组，剩40女。求员工总数。 选项 A446 B488 C508 D576"""
sols = []
for men in range(1, 1000):
    for women in range(1, 1000):
        if (men - 8) % 7 == 0 and women % 5 == 0 and (men - 8) // 7 == women // 5 and men >= 8 \
           and men % 9 == 0 and (women - 40) % 5 == 0 and men // 9 == (women - 40) // 5 and women >= 40:
            sols.append((men, women))
print('（男，女）：', sols)
assert sols == [(288, 200)]
print('总数', sum(sols[0]))

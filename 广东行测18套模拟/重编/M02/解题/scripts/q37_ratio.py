"""第37题：A+B=2C，A+C=3B，订单总量可能是多少？ 选项 A38 B57 C64 D84

核验：枚举正整数 A、B、C（总量不超过 120），列出所有可能的总量，再看哪个选项在其中。
"""
options = {"A": 38, "B": 57, "C": 64, "D": 84}

totals = {}
for a in range(1, 121):
    for b in range(1, 121):
        for c in range(1, 121):
            if a + b == 2 * c and a + c == 3 * b and a + b + c <= 120:
                totals[a + b + c] = (a, b, c)
print("可能的总量:", sorted(totals))   # 12 的倍数
for k, v in options.items():
    print(k, v, "可能，A,B,C=%s" % (totals[v],) if v in totals else "不可能")

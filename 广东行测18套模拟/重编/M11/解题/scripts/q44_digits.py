"""M11 第44题：一件商品标价的个位与十位弄反，顾客少付27元，标价不可能是？ 选项 A42 B63 C85 D96"""
ok = [n for n in range(10, 100) if n - (10 * (n % 10) + n // 10) == 27]
print('交换后少27元的两位数标价：', ok)
assert all((n // 10) - (n % 10) == 3 for n in ok)
opts = {'A': 42, 'B': 63, 'C': 85, 'D': 96}
print('不可能的选项：', [k for k, v in opts.items() if v not in ok])

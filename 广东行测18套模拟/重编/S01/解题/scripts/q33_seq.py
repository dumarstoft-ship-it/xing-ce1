"""S01 第33题：5，7，17，31，65，（ ）  选项 A97 B113 C127 D135
a(n)=a(n−1)+2a(n−2)：17=7+10，31=17+14，65=31+34 → 65+62=127；
另一写法：×2−3、×2+3交替：7=5×2−3，17=7×2+3，31=17×2−3，65=31×2+3 → 65×2−3=127。"""
seq = [5, 7, 17, 31, 65]
assert all(seq[i] == seq[i - 1] + 2 * seq[i - 2] for i in range(2, 5))
assert all(seq[i] == 2 * seq[i - 1] + (3 if i % 2 == 0 else -3) for i in range(1, 5))
v1 = seq[-1] + 2 * seq[-2]
v2 = 2 * seq[-1] - 3
print(v1, v2)
assert v1 == v2 == 127
opts = {'A': 97, 'B': 113, 'C': 127, 'D': 135}
print('答案：', [k for k, v in opts.items() if v == v1])

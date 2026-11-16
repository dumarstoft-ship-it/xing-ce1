"""第58题：按四个选项给出的答案算四人得分；再对所有可能答案(每题A/B/C/D)全枚举，
看满足得分4、5、1、4的答案组合有哪些，以及选项是否唯一。"""
from itertools import product
ans = {
 '小红': 'BBCABBCBBB',
 '小黑': 'CCBBCABAAC',
 '小白': 'BACCACABCA',
 '小黄': 'BCCACCBBAC',
}
target = {'小红': 4, '小黑': 5, '小白': 1, '小黄': 4}
opts = {'A': 'CACACACBAB', 'B': 'ABBCBCCABC', 'C': 'ABCBCBCAAC', 'D': 'BACACABCBB'}
def score(key, s):
    return sum(a == b for a, b in zip(key, s))
for k, key in opts.items():
    sc = {n: score(key, s) for n, s in ans.items()}
    print(k, key, sc, '符合' if sc == target else '不符')
# full enumeration with letters A-D (D never chosen by anyone, acts as 'nobody right')
cnt = 0; keys = []
names = list(ans)
for key in product('ABCD', repeat=10):
    if all(score(key, ans[n]) == target[n] for n in names):
        cnt += 1
        keys.append(''.join(key))
print('全枚举(每题A-D)符合得分的答案组合数:', cnt)
print('其中出现在选项里的:', [k for k, v in opts.items() if v in keys])

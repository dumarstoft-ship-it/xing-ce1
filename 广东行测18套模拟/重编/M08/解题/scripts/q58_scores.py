"""Q58: which option's answer key gives the four contestants scores 4, 5, 1, 4?
Also enumerate all keys over the letters A-D to see how much the scores pin down."""
from itertools import product

ans = {'小红': 'BBCABBCBBB', '小黑': 'CCBBCABAAC', '小白': 'BACCACABCA', '小黄': 'BCCACCBBAC'}
target = [4, 5, 1, 4]
opts = {'A': 'CACACACBAB', 'B': 'ABBCBCCABC', 'C': 'ABCBCBCAAC', 'D': 'BACACABCBB'}
score = lambda key, a: sum(k == x for k, x in zip(key, a))
for o, key in opts.items():
    s = [score(key, a) for a in ans.values()]
    print(o, key, s, 'OK' if s == target else '')
n = 0
for key in product('ABCD', repeat=10):
    if [score(key, a) for a in ans.values()] == target:
        n += 1
print('keys over A-D consistent with the scores:', n, '(the question only asks which option fits)')

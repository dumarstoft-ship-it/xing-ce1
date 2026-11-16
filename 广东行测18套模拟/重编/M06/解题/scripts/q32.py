# 第32题：8，15，26，39，56，（ ）
# 规律：一次作差 7、11、13、17，为连续质数，下一项差为19。
seq = [8, 15, 26, 39, 56]
options = {"A": 72, "B": 75, "C": 84, "D": 89}

def is_prime(n):
    return n > 1 and all(n % p for p in range(2, int(n ** 0.5) + 1))

primes = [p for p in range(2, 60) if is_prime(p)]
ok = []
for k, v in options.items():
    s = seq + [v]
    d = [b - a for a, b in zip(s, s[1:])]
    i = primes.index(d[0]) if d[0] in primes else None
    consecutive = i is not None and d == primes[i:i + len(d)]
    d2 = [b - a for a, b in zip(d, d[1:])]
    print(k, v, "一次差", d, "二次差", d2, "连续质数" if consecutive else "")
    if consecutive:
        ok.append(k)
assert ok == ["B"], ok
print("答案:", ok)

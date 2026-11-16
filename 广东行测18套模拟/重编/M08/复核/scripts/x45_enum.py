# 第45题：A+B+C+D=45，A=B+4，C=45/5=9，D<=min(A,B,C)，人数为正整数，求 A 最小
sols = []
C = 45 // 5
for B in range(1, 45):
    A = B + 4
    D = 45 - A - B - C
    if D >= 1 and D <= min(A, B, C):
        sols.append((A, B, C, D))
print('可行解(A,B,C,D)：', sols)
print('A 最小 =', min(s[0] for s in sols))
for a in (12, 13, 15, 16):
    B = a - 4; D = 45 - a - B - C
    print(f'A={a}: B={B}, D={D}, D<=min(A,B,C)? {D <= min(a, B, C)}')

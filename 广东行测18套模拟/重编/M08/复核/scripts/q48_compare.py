"""第48题：比较各选项与框内串的结构相似度。
face角度取自 q48_classify.py 的输出（0右,90上,180左,270下，45度一档）。
度量1：两两位置“是否相同”的关系一致的对数（28对）。
度量2：两两位置“角度差”一致的对数（等价于整体旋转后相同）。
度量3：两两位置角度差互为相反数的对数（等价于整体镜像后相同）。"""
from itertools import combinations
S = {
 'frame': [90, 270, 270, 0, 225, 90, 0, 135],
 'A': [225, 180, 180, 135, 90, 225, 135, 90],
 'B': [0, 90, 90, 225, 45, 0, 225, 315],
 'C': [90, 225, 45, 0, 315, 90, 0, 270],
 'D': [45, 225, 225, 315, 180, 225, 315, 0],
}
def pattern(seq):
    m = {}; out = ''
    for s in seq:
        m.setdefault(s, 'abcdefgh'[len(m)]); out += m[s]
    return out
f = S['frame']
pairs = list(combinations(range(8), 2))
for k in 'ABCD':
    s = S[k]
    eq = sum((f[i] == f[j]) == (s[i] == s[j]) for i, j in pairs)
    rot = sum((f[j] - f[i]) % 360 == (s[j] - s[i]) % 360 for i, j in pairs)
    ref = sum((f[j] - f[i]) % 360 == (s[i] - s[j]) % 360 for i, j in pairs)
    print(k, pattern(s), 'same-pattern pairs', eq, '/28', '| rot-relation pairs', rot, '| mirror-relation pairs', ref)
print('frame', pattern(f))

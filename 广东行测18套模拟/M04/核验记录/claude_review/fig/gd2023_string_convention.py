"""Calibration: the two real 2023 Guangdong '字符串' questions (hand-read from
广东/行测/2022-2026/assets/GD2023-XJ/GD2023-XJ-p14-i01.png, official key A; and
GD2023-XZ-p15-i01.png, official key A). Test which identity scheme reproduces the official key:
fine = every distinct drawing is its own symbol (180-degree-rotated copies are different);
coarse = a drawing and its 180-degree rotation are the same symbol."""
def canon(seq):
    m={}; return ''.join(m.setdefault(s,'abcdefgh'[len(m)]) for s in seq)
# arrows by compass direction
XJ={'stem':['W','N','E','NW','NE','W','NW','N'],
    'A':['NW','SW','SE','E','NE','NW','E','SW'],
    'B':['E','S','W','SW','SE','E','NE','S'],
    'C':['N','E','S','W','N','E','S','W'],
    'D':['E','NW','W','SW','NW','E','SW','NW']}
axis={'N':'|','S':'|','E':'-','W':'-','NE':'/','SW':'/','NW':'\\','SE':'\\'}
# triangles: (fill, pointing direction / right-angle corner)
XZ={'stem':['wU','gD','gD','wU','wD','gU','gD','gU'],
    'A':['gTR','gBL','gBL','gTR','gTL','gBR','gBL','gBR'],
    'B':['gDia','wDia','wDia','gDia','gCir','wCir','wCir','wDia'],
    'C':['wR','gL','gL','wR','wL','gL','gR','gL'],
    'D':['gRect','gSq','gSq','gRect','wStar','gStar','gSq','wStar']}
rot180={'wU':'wD','wD':'wU','gU':'gD','gD':'gU','gTR':'gBL','gBL':'gTR','gTL':'gBR','gBR':'gTL','wR':'wL','wL':'wR','gR':'gL','gL':'gR'}
def coarse_xz(s): return min(s, rot180.get(s,s))
for name,Q,coarse in (('GD2023县级卷第50题(箭头)',XJ,lambda s: axis[s]),('GD2023乡镇卷第55题(三角)',XZ,coarse_xz)):
    for scheme,f in (('fine',lambda s:s),('coarse',coarse)):
        st=canon([f(s) for s in Q['stem']])
        hits=[o for o in 'ABCD' if canon([f(s) for s in Q[o]])==st]
        print(f'{name} {scheme:6s}: stem {st}; exact matches {hits}')

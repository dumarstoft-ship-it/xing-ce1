"""M11 第69题：夏至日白昼最长的点。题图：甲在北极圈以北，乙在赤道与北回归线之间，丙在赤道与南回归线之间，
丁在南回归线与南极圈之间（看图读出，纬度取代表值）。按太阳赤纬+23.44°计算昼长。"""
from math import tan, radians, acos, degrees
dec = 23.44
pts = {'甲': 70.0, '乙': 10.0, '丙': -12.0, '丁': -45.0}
def daylen(lat):
    c = -tan(radians(lat)) * tan(radians(dec))
    if c <= -1: return 24.0
    if c >= 1: return 0.0
    return 2 * degrees(acos(c)) / 15
for k, lat in pts.items():
    print(k, '纬度%+.0f°' % lat, '昼长%.1f小时' % daylen(lat))
best = max(pts, key=lambda k: daylen(pts[k]))
assert best == '甲'
print('最长：', best, '（北极圈以北出现极昼）')

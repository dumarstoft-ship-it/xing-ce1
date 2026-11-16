"""第70题：夏至日（太阳直射23.44°N）各地"昼长-夜长"差值反推纬度。
差值：甲 1.5h，乙 0，丙 3h，丁 -2h。

用日出日落公式 cos(H0) = -tan(φ)·tan(δ)（不计大气折射，与中学地理口径一致），
昼长 = 2*H0/15 小时，差值 = 2*昼长 - 24。由差值反解纬度 φ。
另给出计入大气折射（太阳中心 -0.833°）的结果作对照。
"""
from math import radians, degrees, tan, cos, sin, atan, acos

DELTA = 23.44  # 夏至日太阳赤纬


def lat_from_diff(diff_h):
    day = (24 + diff_h) / 2
    H0 = day * 15 / 2                      # 半昼弧（度）
    tphi = -cos(radians(H0)) / tan(radians(DELTA))
    return degrees(atan(tphi))


def diff_from_lat(phi, refraction=False):
    h0 = -0.833 if refraction else 0.0
    p, d = radians(phi), radians(DELTA)
    c = (sin(radians(h0)) - sin(p) * sin(d)) / (cos(p) * cos(d))
    c = max(-1.0, min(1.0, c))
    day = 2 * degrees(acos(c)) / 15
    return 2 * day - 24


places = {"甲": 1.5, "乙": 0.0, "丙": 3.0, "丁": -2.0}
lat = {}
for k, dlt in places.items():
    lat[k] = lat_from_diff(dlt)
    hemi = "北" if lat[k] > 1e-9 else ("南" if lat[k] < -1e-9 else "赤道")
    print("%s: 差值 %+.1fh -> 纬度 %.1f°（%s）" % (k, dlt, abs(lat[k]), hemi))

print("A 甲、丙同半球：", lat["甲"] * lat["丙"] > 0)
print("B 丙纬度高于乙：", abs(lat["丙"]) > abs(lat["乙"]))
print("C 丁在南半球：", lat["丁"] < 0)
print("D 甲纬度高于丁：", abs(lat["甲"]) > abs(lat["丁"]), "（甲%.1f° vs 丁%.1f°）" % (abs(lat["甲"]), abs(lat["丁"])))

# 单调性检查：|差值| 随纬度绝对值增大而增大，南北对称取反
for phi in [0, 10, 20, 30, 40, 50, 60]:
    print("纬度 %2d°N 差值 %+.2fh，%2d°S 差值 %+.2fh" % (phi, diff_from_lat(phi), phi, diff_from_lat(-phi)))
print("[对照] 计入大气折射时赤道差值 %+.2fh（教材口径忽略折射，取 0）" % diff_from_lat(0, refraction=True))

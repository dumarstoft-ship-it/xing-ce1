"""Q70: a summer-holiday evening, 21:00 Beijing time (UTC+8, 120E).
(1) Kashgar: not dark yet. (2) Sydney: winter.
Compute local mean solar time and approximate sunset with a standard declination/hour-angle formula."""
from math import radians, degrees, sin, cos, tan, acos, asin

def sunset_bjt(lat, lon, N):
    """approx sunset in Beijing time (hours) for day-of-year N"""
    g = 2 * 3.141592653589793 / 365 * (N - 1)
    decl = -degrees(asin(0.39779 * cos(radians(0.98565 * (N + 10) + 1.914 * sin(radians(0.98565 * (N - 2)))))))
    eot = 229.18 * (0.000075 + 0.001868 * cos(g) - 0.032077 * sin(g) - 0.014615 * cos(2 * g) - 0.040849 * sin(2 * g))
    h0 = -0.833  # refraction + solar radius
    cosH = (sin(radians(h0)) - sin(radians(lat)) * sin(radians(decl))) / (cos(radians(lat)) * cos(radians(decl)))
    H = degrees(acos(cosH))
    solar_noon_utc = 12 - lon / 15 - eot / 60
    return decl, (solar_noon_utc + H / 15 + 8) % 24, H / 7.5

cities = {"Kashgar": (39.47, 75.99), "Dalian": (38.91, 121.61), "Sydney": (-33.87, 151.21)}
N = 201  # ~20 July, summer holiday
for name, (lat, lon) in cities.items():
    local_mean = 21 - (120 - lon) * 4 / 60
    decl, ss, daylen = sunset_bjt(lat, lon, N)
    h, m = int(ss), round((ss - int(ss)) * 60)
    lm_h, lm_m = int(local_mean), round((local_mean - int(local_mean)) * 60)
    print(f"{name:8s} lat {lat:6.2f} lon {lon:6.2f}: local mean time at 21:00 BJT = {lm_h:02d}:{lm_m:02d}; "
          f"sunset ~ {h:02d}:{m:02d} BJT; day length {daylen:4.1f} h")
print(f"solar declination on day {N}: {decl:+.1f} deg (sun over the northern hemisphere)")
assert decl > 0
print("Kashgar and Dalian have almost the same latitude (similar day length), so (1) is a longitude /")
print("local-time effect of Earth's ROTATION, not latitude; Sydney (southern hemisphere) has winter in July")
print("because of Earth's REVOLUTION with its tilted axis (direct-sun point north of the equator). -> D")
print("ANSWER: D")

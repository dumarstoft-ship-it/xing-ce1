"""Q50: section of the staircase solid by the plane through P, Q, R.

P = back-bottom-right corner, Q = front-bottom-right corner, R = back-top-left corner
(R sits on the dotted hidden vertical edge that drops to the back-bottom-left corner).
PQ is a depth edge, so the plane contains the depth direction: the section is the
depth-extrusion of the segments where the diagonal (top-left corner -> bottom-right
corner) of the staircase profile lies inside the profile.  Every inside segment gives
one rectangle; the cylinder must be checked separately.

Coordinates below are outline centre-lines measured from the original 600x150 image
(ASCII dumps), in image pixels (y downwards).
"""


def trace(name, top_left, bottom_right, steps):
    """steps: list of (x_start, x_end, top_y) of the profile, left to right"""
    (x0, y0), (x1, y1) = top_left, bottom_right
    slope = (y1 - y0) / (x1 - x0)
    line = lambda x: y0 + slope * (x - x0)
    segs = []
    for xs, xe, ty in steps:
        # inside where line y >= top_y (below the top surface, image y downwards)
        lo, hi = xs, xe
        if line(xs) < ty:            # line above the step at its left end
            xin = x0 + (ty - y0) / slope
            if xin >= xe:
                continue
            lo = max(xs, xin)
        segs.append((round(lo, 1), round(hi, 1)))
    print(f"{name}: slope {slope:.3f}")
    for xs, xe, ty in steps:
        print(f"   step x[{xs},{xe}] top y={ty}: diagonal at right end y={line(xe):.2f} "
              f"({'below' if line(xe) > ty else 'above'} the corner by {abs(line(xe) - ty):.2f}px)")
    k = (1 + slope ** 2) ** 0.5
    lens = [round((b - a) * k, 1) for a, b in segs]
    print(f"   inside segments (x): {segs}  slanted lengths: {lens}")
    return segs


# front face: top-left (3.7,34.3), Q (85.6,86.5); risers at x=15.5 and 29.5;
# step tops: 34.3 / 49.5 / 61
front = trace("front face", (3.7, 34.3), (85.6, 86.5),
              [(3.7, 15.5, 34.3), (15.5, 29.5, 49.5), (29.5, 85.6, 61.0)])
# back face: R (19.9,14.5), P (98.5,74); back risers at x=30.5 and 44.5;
# step tops: 14.5 / 31.5 / 44.5
back = trace("back face", (19.9, 14.5), (98.5, 74.0),
             [(19.9, 30.5, 14.5), (30.5, 44.5, 31.5), (44.5, 98.5, 44.5)])

# cylinder: sides at x=73.5..89.5 on the low top face (drawn at ~half depth)
# front-face equivalent x of its axis ~ 81.5 - 6.5 = 75 ; radius ~8 -> x in [67, 83]
# the diagonal there (front face): y = 34.3 + 0.637*(67-3.7) = 74.6 > 61 (low top),
# i.e. the plane is already inside the low block, below the cylinder base.
print("front-face diagonal at cylinder x=67:", round(34.3 + (86.5 - 34.3) / (85.6 - 3.7) * (67 - 3.7), 1),
      "vs low-block top y=61 -> cylinder (above y=61) not cut")

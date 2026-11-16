"""M07第69题（编辑新写的电学题）电路图：热敏电阻Rt与定值电阻R0并联，A1在干路，A2与R0串联。

    python3 广东行测18套模拟/重编/M07/figures/make_thermistor.py
"""
from pathlib import Path

OUT = Path(__file__).with_name("thermistor_circuit.svg")
FONT = 'font-family=\'"ZG Latin", "ZG Song"\''
W, H = 250, 126
lines, dots, texts = [], [], []


def L(*pts):
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    lines.append(f'<path d="{d}"/>')


def T(x, y, s, size=10.5, italic=False, anchor="middle"):
    st = ' font-style="italic"' if italic else ""
    texts.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}"{st} text-anchor="{anchor}">{s}</text>')


def sub(x, y, sym, s, italic=True):
    T(x, y, sym, italic=italic)
    T(x + 6.8, y + 3, s, size=7)


def meter(cx, cy, s):
    lines.append(f'<circle cx="{cx}" cy="{cy}" r="9"/>')
    T(cx - 1.5, cy + 3.8, "A", italic=False)
    T(cx + 4.3, cy + 6.3, s, size=6)


# 版面：左边电源，上边开关S和干路电流表A1；右边两条并联支路（上Rt，下R0与A2）
xl, xr, yt, yb = 30, 225, 28, 112
xa, xb = 120, 225          # 并联段左右节点
y1, y2 = 28, 82            # 两条支路的高度
# 电源（竖放，长板在上）
ym = (yt + yb) / 2
L((xl, yt), (xl, ym - 4))
lines.append(f'<path d="M{xl-9},{ym-4} H{xl+9}"/>')
lines.append(f'<path d="M{xl-5},{ym+3} H{xl+5}" stroke-width="2.6" stroke-linecap="butt"/>')
L((xl, ym + 3), (xl, yb), (xr, yb), (xr, y1))
# 上边：开关S、电流表A1
L((xl, yt), (52, yt))
dots.append(f'<circle cx="52" cy="{yt}" r="1.7"/>'); dots.append(f'<circle cx="74" cy="{yt}" r="1.7"/>')
L((52, yt), (71, yt - 9))
T(63, yt - 13, "S", italic=True)
L((74, yt), (86, yt))
meter(95, yt, "1")
L((104, yt), (xa, yt))
# 上支路：热敏电阻Rt（矩形加斜线）
L((xa, y1), (150, y1))
lines.append(f'<rect x="150" y="{y1-5}" width="34" height="10"/>')
L((146, y1 + 9), (154, y1 + 9), (180, y1 - 9))
sub(160, y1 - 11, "R", "t")
L((184, y1), (xb, y1))
# 下支路：R0与电流表A2串联
L((xa, y1), (xa, y2), (138, y2))
lines.append(f'<rect x="138" y="{y2-5}" width="34" height="10"/>')
sub(150, y2 - 9, "R", "0")
L((172, y2), (186, y2))
meter(195, y2, "2")
L((204, y2), (xb, y2))
dots.append(f'<circle cx="{xa}" cy="{y1}" r="1.8"/>'); dots.append(f'<circle cx="{xb}" cy="{y2}" r="1.8"/>')   # 并联段的两个节点

svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{H}pt" viewBox="0 0 {W} {H}">',
       '<rect width="100%" height="100%" fill="#fff"/>',
       '<g stroke="#000" stroke-width="1.1" fill="none" stroke-linecap="round" stroke-linejoin="round">', *lines, '</g>',
       '<g fill="#000">', *dots, '</g>',
       f'<g {FONT} fill="#000">', *texts, '</g>', '</svg>']
OUT.write_text("\n".join(svg) + "\n", encoding="utf-8")
print(OUT)

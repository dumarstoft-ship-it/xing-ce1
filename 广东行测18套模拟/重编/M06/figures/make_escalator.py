"""M06第69题（编辑新写的电学题）选项电路图：四个电路排成2×2，字体用题本字体。

    python3 广东行测18套模拟/重编/M06/figures/make_escalator.py

A：S₂并在电动机两端；B：S₁、S₂位置对调；C：S₁在干路、S₂并在R两端（正确）；D：M与R并联，S₂串在R支路。
"""
from pathlib import Path

OUT = Path(__file__).with_name("escalator_circuits.svg")
FONT = 'font-family=\'"ZG Latin", "ZG Song"\''
CW, CH = 165, 150          # 每格宽高（pt）
lines, dots, texts = [], [], []


def L(x1, y1, x2, y2):
    lines.append(f'<path d="M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f}"/>')


def dot(x, y, r=1.7):
    dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}"/>')


def T(x, y, s, size=10.5, italic=False, anchor="middle"):
    st = ' font-style="italic"' if italic else ""
    texts.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}"{st} text-anchor="{anchor}">{s}</text>')


def sw_label(x, y, sub):
    """开关名：斜体S加下标。(x, y)为S的基线中点。"""
    T(x, y, "S", italic=True)
    T(x + 6.5, y + 3, sub, size=7)


def battery_v(x, ym):
    lines.append(f'<path d="M{x-9:.1f},{ym-4:.1f} H{x+9:.1f}"/>')
    lines.append(f'<path d="M{x-5:.1f},{ym+3:.1f} H{x+5:.1f}" stroke-width="2.6" stroke-linecap="butt"/>')


def switch_h(x1, x2, y, sub, lab_xy=None):
    """横放开关，刀片向上翘起；开关名默认标在刀片上方。"""
    dot(x1, y), dot(x2, y)
    L(x1, y, x2 - 3, y - 9)
    sw_label(*(lab_xy or ((x1 + x2) / 2, y - 12)), sub)


def motor(cx, cy, r=8.5):
    lines.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}"/>')
    T(cx, cy + 3.8, "M")


def circuit(ox, oy, kind):
    xl, xr, yt, yb = ox + 22, ox + 140, oy + 36, oy + 94
    ym = (yt + yb) / 2
    battery_v(xl, ym)
    L(xl, yt, xl, ym - 4)
    L(xl, ym + 3, xl, yb)
    main_sub, by_sub = ("2", "1") if kind == "swap" else ("1", "2")
    # 上边：干路开关
    L(xl, yt, ox + 44, yt)
    switch_h(ox + 44, ox + 66, yt, main_sub)
    if kind == "parallel":
        xa = ox + 96
        L(ox + 66, yt, xr, yt)
        L(xl, yb, xr, yb)
        dot(xa, yt), dot(xa, yb)
        L(xa, yt, xa, ym - 8.5)
        motor(xa, ym)
        L(xa, ym + 8.5, xa, yb)
        # 右侧支路：R 与 S₂ 串联
        L(xr, yt, xr, yt + 5)
        lines.append(f'<rect x="{xr-5:.1f}" y="{yt+5:.1f}" width="10" height="20"/>')
        T(xr - 15, yt + 19, "R", italic=True)
        L(xr, yt + 25, xr, yt + 33)
        dot(xr, yt + 33), dot(xr, yt + 49)
        L(xr, yt + 49, xr + 9, yt + 36)
        sw_label(xr - 17, yt + 45, by_sub)
        L(xr, yt + 49, xr, yb)
        return
    # 上边：电动机
    L(ox + 66, yt, ox + 95.5, yt)
    motor(ox + 104, yt)
    L(ox + 112.5, yt, xr, yt)
    L(xr, yt, xr, yb)
    # 下边：分压电阻
    L(xl, yb, ox + 66, yb)
    lines.append(f'<rect x="{ox+66:.1f}" y="{yb-5:.1f}" width="30" height="10"/>')
    T(ox + 81, yb - 9, "R", italic=True)
    L(ox + 96, yb, xr, yb)
    if kind in ("correct", "swap"):
        xa, xb, yy = ox + 54, ox + 108, yb + 18
        dot(xa, yb), dot(xb, yb)
        L(xa, yb, xa, yy)
        L(xa, yy, ox + 70, yy)
        switch_h(ox + 70, ox + 92, yy, by_sub, lab_xy=(xb + 13, yy + 4))
        L(ox + 92, yy, xb, yy)
        L(xb, yy, xb, yb)
    elif kind == "shortM":
        xa, xb, yy = ox + 86, ox + 122, yt - 18
        dot(xa, yt), dot(xb, yt)
        L(xa, yt, xa, yy)
        L(xa, yy, ox + 94, yy)
        dot(ox + 94, yy), dot(ox + 114, yy)
        L(ox + 94, yy, ox + 111, yy - 9)
        L(ox + 114, yy, xb, yy)
        L(xb, yy, xb, yt)
        sw_label(ox + 132, yy - 2, by_sub)


ORDER = {"A": "shortM", "B": "swap", "C": "correct", "D": "parallel"}
for i, (k, kind) in enumerate(ORDER.items()):
    ox, oy = (i % 2) * CW, (i // 2) * CH
    circuit(ox, oy, kind)
    T(ox + 81, oy + CH - 8, k, size=11)

W, H = 2 * CW, 2 * CH
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{H}pt" viewBox="0 0 {W} {H}">',
       '<rect width="100%" height="100%" fill="#fff"/>',
       '<g stroke="#000" stroke-width="1.1" fill="none" stroke-linecap="round">', *lines, '</g>',
       '<g fill="#000">', *dots, '</g>',
       f'<g {FONT} fill="#000">', *texts, '</g>', '</svg>']
OUT.write_text("\n".join(svg) + "\n", encoding="utf-8")
print(OUT, W, H)

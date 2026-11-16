"""M08第35题（第23季第35题）圆形数阵：原图未入库，按题库转写表重画。

题库把原图转成表“四个圆内的数字”（每个圆用一条竖直直径和一条水平直径分成左上、右上、左下、右下
四格），这里按表中数字与方位画回四个圆，数字与方位不改。尺寸按原卷版面推定：题号行（y≈657—669pt）
与选项行（y≈745—757pt）之间约75pt，圆的直径取21mm，四圆横排、间距9mm，总宽111mm。

    python3 广东行测18套模拟/重编/M08/figures/make_q35_circles.py
"""
from pathlib import Path

OUT = Path(__file__).with_name("q35_circles.svg")
FONT = 'font-family=\'"ZG Latin", "ZG Song"\''
ROWS = [("2", "6", "10", "8"), ("5", "11", "4", "3"), ("7", "17", "11", "4"), ("？", "9", "18", "3")]   # 左上、右上、左下、右下

MM = 72 / 25.4                 # 1mm = 2.835pt；SVG单位取pt
D, GAP, PAD = 21 * MM, 9 * MM, 1.2
R = D / 2
W = 4 * D + 3 * GAP + 2 * PAD
H = D + 2 * PAD
FS = 10.5                      # 与正文字号相同
shapes, texts = [], []
for i, (ul, ur, ll, lr) in enumerate(ROWS):
    cx, cy = PAD + R + i * (D + GAP), PAD + R
    shapes.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{R:.2f}"/>')
    shapes.append(f'<path d="M{cx - R:.2f},{cy:.2f} L{cx + R:.2f},{cy:.2f} M{cx:.2f},{cy - R:.2f} L{cx:.2f},{cy + R:.2f}"/>')
    off = R * 0.45
    for s, dx, dy in ((ul, -off, -off), (ur, off, -off), (ll, -off, off), (lr, off, off)):
        texts.append(f'<text x="{cx + dx:.2f}" y="{cy + dy + FS * 0.36:.2f}" font-size="{FS}" text-anchor="middle">{s}</text>')

svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.2f}pt" height="{H:.2f}pt" viewBox="0 0 {W:.2f} {H:.2f}">',
       '<rect width="100%" height="100%" fill="#fff"/>',
       '<g stroke="#000" stroke-width="0.8" fill="none">', *shapes, '</g>',
       f'<g {FONT} fill="#000">', *texts, '</g>', '</svg>']
OUT.write_text("\n".join(svg) + "\n", encoding="utf-8")
print(OUT, f"{W / MM:.1f}mm × {H / MM:.1f}mm")

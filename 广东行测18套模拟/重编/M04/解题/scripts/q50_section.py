# -*- coding: utf-8 -*-
"""Q50 截面：过 P、Q、R 的平面截台阶形多面体。

P、Q 是底面右侧那条“前后方向”棱的两端，所以截面平行于前后方向；截面形状 = 正面轮廓被
“R 所在左上棱 → PQ 棱”这条斜线截出的各段，沿前后方向拉伸成的矩形（宽度都等于物体前后深度）。

正面轮廓直接从题图量得（原图像素；下面也用理想整数格 4/3/2 高、1/1/4.5 宽再算一遍）。
"""
import math

def cut(widths, heights, cyl=None):
    """widths: 各台阶的水平宽度（从左到右），heights: 对应高度。斜线从 (0,H0) 到 (L,0)。"""
    xs = [0]
    for w in widths:
        xs.append(xs[-1] + w)
    L, H = xs[-1], heights[0]
    z = lambda x: H * (1 - x / L)
    k = math.sqrt(1 + (H / L) ** 2)
    segs = []
    for i, h in enumerate(heights):
        a, b = xs[i], xs[i + 1]
        # 斜线在本段内且低于该段高度的部分
        x_enter = max(a, L * (1 - h / H))
        if x_enter < b:
            segs.append((round(x_enter, 2), b, round((b - x_enter) * k, 2)))
        else:
            segs.append(None)
        print('  第%d段 x∈[%.1f,%.1f] 高%.1f：斜线在左端z=%.2f 右端z=%.2f -> %s' % (
            i + 1, a, b, h, z(a), z(b), '截到，斜长%.2f' % ((b - x_enter) * k) if x_enter < b else '截不到'))
    if cyl:
        c0, c1, base = cyl
        print('  圆柱所在 x∈[%.1f,%.1f]：斜线高度 %.2f~%.2f，圆柱底面高 %.1f -> %s' % (
            c0, c1, z(c1), z(c0), base, '截到圆柱' if z(c0) > base else '截不到圆柱'))
    return segs

print('按题图像素量得的正面轮廓：')
# 左边 x=3，第一级竖面 x≈16.5，第二级 x≈29.5，右端 x≈86；底边 y=86.5，三级顶面 y=34.5/49.5/61.5
s1 = cut([13.5, 13.0, 56.5], [52.0, 37.0, 25.0], cyl=(65, 81, 25.0))
print('按理想整数格（高4/3/2，宽1/1/4.5）：')
s2 = cut([1, 1, 4.5], [4, 3, 2], cyl=(4.9, 6.2, 2))
print('结论：截面为 3 个宽度相同（=物体前后深度）的矩形，长度比约',
      ' : '.join('%.2f' % s[2] for s in s1 if s), '；圆柱不被截到 → 选项B（三个矩形、无椭圆）')

"""M10 第46题（GD2017-Q031）：正方形与菱形叠成八角，读出每幅图里涂黑的小三角位置。

8 个位置按顺时针编号：0 上尖(菱形) 1 右上角(正方形) 2 右尖 3 右下角 4 下尖 5 左下角 6 左尖 7 左上角。
在每个小三角内部取一个小窗口求平均灰度，<100 记为黑。
"""
from PIL import Image
import numpy as np
import sys

path = sys.argv[1] if len(sys.argv) > 1 else '/home/user/xing-ce1/广东/行测/2013-2021/assets/GD2017/GD2017-p03-i08.png'
a = np.array(Image.open(path).convert('L')).astype(float)

def center_of_panel(x0, x1, y0, y1):
    # 以图形中最外层黑线的包围盒中心为中心
    sub = a[y0:y1, x0:x1] < 128
    ys, xs = np.nonzero(sub)
    # 去掉外框：只保留离边框 8 像素以上的点
    keep = (xs > 8) & (xs < (x1-x0-8)) & (ys > 8) & (ys < (y1-y0-8))
    xs, ys = xs[keep], ys[keep]
    return x0 + (xs.min()+xs.max())/2, y0 + (ys.min()+ys.max())/2, (xs.max()-xs.min())/2

OFF = {0:(0,-1), 1:(1,-1), 2:(1,0), 3:(1,1), 4:(0,1), 5:(-1,1), 6:(-1,0), 7:(-1,-1)}
def read(x0, x1, y0, y1):
    cx, cy, r = center_of_panel(x0, x1, y0, y1)   # r ≈ 菱形半对角线
    res = []
    for k in range(8):
        dx, dy = OFF[k]
        if dx and dy:   # 正方形角：在正方形角与菱形边之间
            px, py = cx + dx*0.66*r, cy + dy*0.66*r
        else:           # 菱形尖：伸出正方形之外
            px, py = cx + dx*0.85*r, cy + dy*0.85*r
        w = a[int(py)-2:int(py)+3, int(px)-2:int(px)+3].mean()
        res.append(1 if w < 100 else 0)
    return res

top = [(10,225),(230,445),(450,665),(668,885)]
opts = {'A':(120,338),'B':(340,556),'C':(558,776),'D':(778,995)}
names = ['上尖','右上角','右尖','右下角','下尖','左下角','左尖','左上角']
for i,(x0,x1) in enumerate(top):
    r = read(x0, x1, 10, 225)
    print(f'图{i+1}: 黑={sum(r)}', [names[k] for k in range(8) if r[k]])
for k,(x0,x1) in opts.items():
    r = read(x0, x1, 272, 490)
    print(f'{k}: 黑={sum(r)}', [names[j] for j in range(8) if r[j]])

# 规律核对：黑块是顺时针连续的一段；记“段首”（逆时针端）位置
def run(r):
    n = sum(r)
    for s in range(8):
        if all(r[(s+t) % 8] for t in range(n)):
            return s, n
seq = [run(read(x0, x1, 10, 225)) for (x0,x1) in top]
print('各图(段首编号, 黑块数):', seq)
print('段首每次逆时针移 2 格(90°)、黑块数每次减 1 → 第5幅应为 段首', (seq[-1][0]-2) % 8, '共 1 块，即', names[(seq[-1][0]-2) % 8])

"""M08 第69题：按题图连线做节点电压法。
节点：P(左竖线)、Q(右竖线)、M(灯右端)、N(电压表左端/滑变左端)。
电源(含电流表)接在P、Q之间；L: P-M；R1与S1串联: M-Q；S2: M-N；S3: P-N；电压表: N-Q；
R2 只接左端和滑片，有效电阻=左端到滑片段，滑片右移有效电阻增大。"""
import itertools
def solve(closed, R2, U=6.0, RL=10.0, R1=10.0):
    big, tiny = 1e9, 1e-6
    elems = [('P', 'M', RL, 'L'), ('N', 'Q', big, 'V'), ('N', 'Q', R2, 'R2')]
    if 'S1' in closed: elems.append(('M', 'Q', R1 + tiny, 'R1'))
    if 'S2' in closed: elems.append(('M', 'N', tiny, 'S2'))
    if 'S3' in closed: elems.append(('P', 'N', tiny, 'S3'))
    # P 接地(0)，Q 固定为 U；未知 M、N
    nodes = ['M', 'N']
    fixed = {'P': 0.0, 'Q': U}
    import copy
    A = [[0.0]*2 for _ in range(2)]; b = [0.0, 0.0]
    for a, c, R, _ in elems:
        gcond = 1.0/R
        for x, y in ((a, c), (c, a)):
            if x in nodes:
                i = nodes.index(x)
                A[i][i] += gcond
                if y in nodes: A[i][nodes.index(y)] -= gcond
                else: b[i] += gcond*fixed[y]
    # 防止悬空节点奇异：加极小对地电导
    for i in range(2): A[i][i] += 1e-15
    det = A[0][0]*A[1][1]-A[0][1]*A[1][0]
    vM = (b[0]*A[1][1]-A[0][1]*b[1])/det; vN = (A[0][0]*b[1]-b[0]*A[1][0])/det
    IL = (0.0 - vM)/RL
    return abs(IL)**2*RL   # 灯功率
cases = {'A': {'S1'}, 'B': {'S2'}, 'C': {'S1', 'S3'}, 'D': {'S2', 'S3'}}
claims = {'A': '变暗', 'B': '变亮', 'C': '不变', 'D': '变亮'}
for k, sw in cases.items():
    p_left, p_right = solve(sw, R2=5.0), solve(sw, R2=20.0)   # 滑片右移：5Ω→20Ω
    if abs(p_right - p_left) < 1e-6*max(p_left, 1e-12) or abs(p_right-p_left) < 1e-12: trend = '不变'
    else: trend = '变亮' if p_right > p_left else '变暗'
    lit = '灯被短路/不亮' if p_left < 1e-9 and p_right < 1e-9 else ''
    print(k, sorted(sw), f'P_L(5Ω)={p_left:.4f}W P_L(20Ω)={p_right:.4f}W 实际:{trend} {lit} 选项说:{claims[k]}',
          '✓' if trend == claims[k] else '✗')

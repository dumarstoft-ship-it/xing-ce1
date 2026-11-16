"""第67题：按题图连接关系做节点电压分析，求各电表示数。

读图得到的连接（节点命名）：
  P：左侧竖导线下段（A1 下端、V1 左端、电源左端、L3 左端）
  T：左上角（A1 上端、V3 左端、L1 上端）
  M：中间横导线（V1 右端、L1 下端、V2 左端、A2 上端）
  R：右侧竖导线（V3 右端、V2 右端、L2 右端、开关右端、A3 右端）
  X：A2 与 L2 之间；Y：L3 与 A3 之间
元件：电源 P-R（闭合 S），A1: P-T，V3: T-R，L1: T-M，V1: P-M，V2: M-R，A2: M-X，L2: X-R，L3: P-Y，A3: Y-R
电流表用极小电阻、电压表用极大电阻近似理想表，精确分数求解。
"""
from fractions import Fraction as F

U = F(6)                 # 电源电压（任取）
RL = F(10)               # 灯丝电阻（三灯相同）
RA = F(1, 10**9)         # 理想电流表
RV = F(10**12)           # 理想电压表

elements = {
    "A1": ("P", "T", RA), "V3": ("T", "R", RV), "L1": ("T", "M", RL),
    "V1": ("P", "M", RV), "V2": ("M", "R", RV), "A2": ("M", "X", RA),
    "L2": ("X", "R", RL), "L3": ("P", "Y", RL), "A3": ("Y", "R", RA),
}
fixed = {"P": F(0), "R": U}
unknown = ["T", "M", "X", "Y"]

# 节点方程：sum (V_node - V_other)/R = 0
n = len(unknown)
A = [[F(0)] * n for _ in range(n)]
b = [F(0)] * n
for i, node in enumerate(unknown):
    for (u, v, r) in elements.values():
        if node not in (u, v):
            continue
        other = v if u == node else u
        g = 1 / r
        A[i][i] += g
        if other in fixed:
            b[i] += g * fixed[other]
        else:
            A[i][unknown.index(other)] -= g

# 高斯消元
m = [row[:] + [bb] for row, bb in zip(A, b)]
for c in range(n):
    p = next(r for r in range(c, n) if m[r][c] != 0)
    m[c], m[p] = m[p], m[c]
    for r in range(n):
        if r != c and m[r][c] != 0:
            f = m[r][c] / m[c][c]
            m[r] = [x - f * y for x, y in zip(m[r], m[c])]
V = dict(fixed)
for i, node in enumerate(unknown):
    V[node] = m[i][n] / m[i][i]

read = {}
for name, (u, v, r) in elements.items():
    if name[0] == "A":
        read[name] = abs(V[u] - V[v]) / r
    elif name[0] == "V":
        read[name] = abs(V[u] - V[v])
for name in ["A1", "A2", "A3", "V1", "V2", "V3"]:
    unit = "A" if name[0] == "A" else "V"
    print(name, "%.6f %s" % (float(read[name]), unit))
print("各灯电压：L1 %.4f V, L2 %.4f V, L3 %.4f V" % tuple(
    float(abs(V[elements[k][0]] - V[elements[k][1]])) for k in ("L1", "L2", "L3")))

r = {k: float(v) for k, v in read.items()}
print("A. V3最小？", r["V3"] < min(r["V1"], r["V2"]), "（V3=%.3f，V1=V2=%.3f）" % (r["V3"], r["V1"]))
print("B. A3最大？", r["A3"] > max(r["A1"], r["A2"]))
print("C. A1=A2？", abs(r["A1"] - r["A2"]) < 1e-6)
print("D. V1=V2？", abs(r["V1"] - r["V2"]) < 1e-6)

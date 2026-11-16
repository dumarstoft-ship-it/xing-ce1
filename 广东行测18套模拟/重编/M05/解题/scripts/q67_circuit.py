"""M05 第67题：电路动态分析。

读图得到的连接（题图已放大核对）：
  电源左端 -> 左侧竖导线（节点L）；电源右端 -> 开关S -> 电流表A1 -> 右侧竖导线（节点R）。
  支路1：L -> R1 -> R2 -> R（R1、R2串联）。
  电压表V：左引线接在L与R1之间的导线上，右引线接在R2与R之间的导线上 -> 测R1、R2串联总电压。
  支路2：L -> (R3 ∥ R4) -> 电流表A2 -> R。
  即：支路1与支路2并联，A1在干路，A2测R3、R4并联部分的电流，V测并联电路两端电压（=电源电压）。

用节点电压法精确求解（电流表取1e-9Ω、电压表取1e12Ω），比较各情形下 V、A1、A2 的变化。
R2：温度升高阻值变大（温度下降则变小）；R3：光照增强阻值变小（光照减弱则变大）。
"""
from fractions import Fraction as F

R_AMM = F(1, 10 ** 9)
R_VM = F(10 ** 12)


def solve(U, R1, R2, R3, R4):
    # 节点：L(地,0V)，T(电源正极经开关后，固定为U)，R，M(R1与R2之间)，X(R3∥R4与A2之间)
    unknown = ["R", "M", "X"]
    fixed = {"L": F(0), "T": F(U)}
    elems = [
        ("T", "R", R_AMM, "A1"),
        ("L", "M", F(R1), "R1"),
        ("M", "R", F(R2), "R2"),
        ("L", "R", R_VM, "V"),
        ("L", "X", F(R3), "R3"),
        ("L", "X", F(R4), "R4"),
        ("X", "R", R_AMM, "A2"),
    ]
    n = len(unknown)
    idx = {u: i for i, u in enumerate(unknown)}
    A = [[F(0)] * n for _ in range(n)]
    b = [F(0)] * n
    for a, c, r, _ in elems:
        gcond = 1 / r
        for p, q in ((a, c), (c, a)):
            if p in idx:
                A[idx[p]][idx[p]] += gcond
                if q in idx:
                    A[idx[p]][idx[q]] -= gcond
                else:
                    b[idx[p]] += gcond * fixed[q]
    # 高斯消元
    for i in range(n):
        piv = next(k for k in range(i, n) if A[k][i] != 0)
        A[i], A[piv] = A[piv], A[i]
        b[i], b[piv] = b[piv], b[i]
        for k in range(n):
            if k != i and A[k][i] != 0:
                f = A[k][i] / A[i][i]
                A[k] = [x - f * y for x, y in zip(A[k], A[i])]
                b[k] -= f * b[i]
    volt = dict(fixed)
    for u in unknown:
        volt[u] = b[idx[u]] / A[idx[u]][idx[u]]
    cur = {name: (volt[a] - volt[c]) / r for a, c, r, name in elems}
    return {"V": float(volt["L"] - volt["R"]) * -1, "A1": float(cur["A1"]), "A2": float(-cur["A2"])}


U, R1, R4 = 12, 10, 20
base = dict(R2=20, R3=30)
cases = {
    "基准": base,
    "温度下降(R2变小)": dict(base, R2=10),
    "光照增强(R3变小)": dict(base, R3=15),
    "光照减弱(R3变大)": dict(base, R3=60),
}
res = {}
for name, c in cases.items():
    res[name] = solve(U, R1, c["R2"], c["R3"], R4)
    print(f"{name:12s} V={res[name]['V']:.6f}V  A1={res[name]['A1']:.6f}A  A2={res[name]['A2']:.6f}A")


def trend(key, case):
    d = res[case][key] - res["基准"][key]
    return "变大" if d > 1e-6 else ("变小" if d < -1e-6 else "不变")


judge = {
    "A": trend("V", "温度下降(R2变小)") == "变小" and trend("A1", "温度下降(R2变小)") == "变大",
    "B": trend("V", "温度下降(R2变小)") == "不变" and trend("A1", "温度下降(R2变小)") == "变大",
    "C": trend("A1", "光照增强(R3变小)") == "变大" and trend("A2", "光照增强(R3变小)") == "变小",
    "D": trend("A1", "光照减弱(R3变大)") == "不变" and trend("A2", "光照减弱(R3变大)") == "变大",
}
for case in list(cases)[1:]:
    print(case, {k: trend(k, case) for k in ("V", "A1", "A2")})
print("各选项是否成立:", judge)
assert [k for k, v in judge.items() if v] == ["B"]
print("答案: B")

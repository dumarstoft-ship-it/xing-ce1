#!/usr/bin/env python3
"""M04 第63题 穷举验证（只依据题本可见内容：题干文字 + assets/q63_snake.png）。

形式化：
  蛇身节 i = 1..20（图中共20格，编号沿蛇身连续），颜色 c(i) ∈ {红, 橙, 黄, 绿, 蓝}。
  (1) 每节一种颜色，五色之一。
  (2) 任意连续4节颜色两两不同 ⇔ ∀i,j: 1 ≤ |i-j| ≤ 3 → c(i) ≠ c(j)。
  (3) 已涂：c1=红, c5=橙, c6=黄, c10=红, c14=蓝, c16=黄, c18=橙, c20=绿。
  选项：A c2=绿；B c9=蓝；C c12=黄；D c19=红。

另外：把题图读成网格坐标 (行, 列)，检查
  (a) 编号相邻的两节在网格上边相邻（蛇身连续）；
  (b) 编号不相邻的两节在网格上不边相邻（不存在会让考生误读“连续”的额外接触）；
  (c) 图中已涂颜色与文字条件(3)一致；
  (d) 图中显示的数字恰为未涂节。
坐标由人工读图得到（行自上而下 0..3，列自左而右 0..9），见 GRID。

运行：python3 verify_q63.py
"""

COLORS = ["红", "橙", "黄", "绿", "蓝"]
N = 20
GIVEN = {1: "红", 5: "橙", 6: "黄", 10: "红", 14: "蓝", 16: "黄", 18: "橙", 20: "绿"}
OPTIONS = {"A": (2, "绿"), "B": (9, "蓝"), "C": (12, "黄"), "D": (19, "红")}

# 人工读图：节号 -> (行, 列, 图中所写内容)
GRID = {
    1: (2, 0, "红"), 2: (2, 1, "2"), 3: (1, 1, "3"), 4: (0, 1, "4"),
    5: (0, 2, "橙"), 6: (0, 3, "黄"), 7: (1, 3, "7"), 8: (2, 3, "8"),
    9: (3, 3, "9"), 10: (3, 4, "红"), 11: (3, 5, "11"), 12: (2, 5, "12"),
    13: (1, 5, "13"), 14: (0, 5, "蓝"), 15: (0, 6, "15"), 16: (0, 7, "黄"),
    17: (0, 8, "17"), 18: (0, 9, "橙"), 19: (1, 9, "19"), 20: (2, 9, "绿"),
}


def check_figure():
    ok = True
    adj = lambda a, b: abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1
    cells = {k: v[:2] for k, v in GRID.items()}
    assert len(set(cells.values())) == N, "格子重叠"
    for i in range(1, N):
        if not adj(cells[i], cells[i + 1]):
            print(f"  [图] 第{i}与第{i+1}节不相邻！")
            ok = False
    for i in range(1, N + 1):
        for j in range(i + 2, N + 1):
            if adj(cells[i], cells[j]):
                print(f"  [图] 非连续的第{i}与第{j}节在图上相邻（可能误导）")
                ok = False
    for i, (_, _, label) in GRID.items():
        if i in GIVEN:
            if label != GIVEN[i]:
                print(f"  [图] 第{i}节图中写“{label}”，文字条件为“{GIVEN[i]}”")
                ok = False
        else:
            if label != str(i):
                print(f"  [图] 第{i}节图中写“{label}”，应为编号")
                ok = False
    return ok


def solve():
    sols = []
    c = [None] * (N + 1)

    def ok_at(i, col):
        for d in (1, 2, 3):
            for j in (i - d, i + d):
                if 1 <= j <= N and c[j] == col:
                    return False
        return True

    def dfs(i):
        if i > N:
            sols.append(c[1:].copy())
            return
        if i in GIVEN:
            if ok_at(i, GIVEN[i]):
                c[i] = GIVEN[i]
                dfs(i + 1)
                c[i] = None
            return
        for col in COLORS:
            if ok_at(i, col):
                c[i] = col
                dfs(i + 1)
                c[i] = None

    # 先放已知色（便于 ok_at 同时检查前后），再 DFS 未知格
    for k, v in GIVEN.items():
        c[k] = v
    # 校验已知色彼此不冲突
    for k in GIVEN:
        v = c[k]
        c[k] = None
        assert ok_at(k, v), f"已知色在第{k}节自相矛盾"
        c[k] = v

    unknown = [i for i in range(1, N + 1) if i not in GIVEN]

    def dfs2(idx):
        if idx == len(unknown):
            sols.append(c[1:].copy())
            return
        i = unknown[idx]
        for col in COLORS:
            if ok_at(i, col):
                c[i] = col
                dfs2(idx + 1)
                c[i] = None

    dfs2(0)
    return sols


def brute_force_count():
    """独立的朴素穷举（不用回溯剪枝），5^12≈2.4亿太慢，这里用逐窗口过滤的生成式代替：
    逐节扩展，只保留满足“最近3节不同”的前缀——与 dfs 等价但写法独立，用来交叉验证。"""
    prefixes = [[]]
    for i in range(1, N + 1):
        new = []
        cand = [GIVEN[i]] if i in GIVEN else COLORS
        for pre in prefixes:
            for col in cand:
                if col not in pre[-3:]:
                    new.append(pre + [col])
        prefixes = new
    return prefixes


if __name__ == "__main__":
    print("题图检查：", "通过" if check_figure() else "有问题")
    sols = solve()
    alt = brute_force_count()
    assert sorted(map(tuple, sols)) == sorted(map(tuple, alt))
    print(f"满足条件的涂色方案数：{len(sols)}（两种独立枚举一致）")
    for s in sols:
        print("   ", " ".join(f"{i}{col}" for i, col in enumerate(s, 1)))
    for k, (pos, col) in OPTIONS.items():
        always = all(s[pos - 1] == col for s in sols)
        sometimes = any(s[pos - 1] == col for s in sols)
        print(f"  选项{k}（第{pos}节{col}）：必然={always}，可能={sometimes}")
    # 每个未知节的可能颜色
    for i in range(1, N + 1):
        vals = sorted({s[i - 1] for s in sols}, key=COLORS.index)
        if i not in GIVEN:
            print(f"   第{i}节可能色：{vals}")
    good = [k for k, (pos, col) in OPTIONS.items() if all(s[pos - 1] == col for s in sols)]
    assert good == ["C"], good
    print("结论：唯一可推出的是选项 C")

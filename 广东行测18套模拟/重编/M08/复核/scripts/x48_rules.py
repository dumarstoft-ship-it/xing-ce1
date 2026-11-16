# 第48题：对读出的 4x4 黑格检验候选规律（对称轴、黑格数、连接方式、连通块数、角接触点数）
stems = {
    '1': ["..#.", ".#.#", "#...", ".#.."],
    '2': [".#..", "#...", ".#.#", "..#."],
    '3': ["#...", ".#.#", "..#.", ".#.."],
    '4': [".#..", "#.#.", "...#", "..#."],
    '5': ["..#.", ".#..", "#.#.", "...#"],
}
opts = {
    'A': [".#..", "..#.", "#..#", ".#.."],
    'B': ["...#", "#.#.", ".#..", "#.#."],
    'C': [".#..", "..#.", ".#.#", "#..."],
    'D': [".#..", ".##.", "..##", "...."],
}

def cells(g):
    return {(r, c) for r in range(4) for c in range(4) if g[r][c] == '#'}

def sym(S):
    res = []
    if {(c, r) for r, c in S} == S: res.append('主对角线')
    if {(3 - c, 3 - r) for r, c in S} == S: res.append('副对角线')
    if {(r, 3 - c) for r, c in S} == S: res.append('竖轴')
    if {(3 - r, c) for r, c in S} == S: res.append('横轴')
    return res

def edge_pairs(S):
    return sum(1 for (r, c) in S for (dr, dc) in [(0, 1), (1, 0)] if (r + dr, c + dc) in S)

def corner_pairs(S):
    return sum(1 for (r, c) in S for (dr, dc) in [(1, 1), (1, -1)] if (r + dr, c + dc) in S)

def components(S, nbrs):
    S = set(S); n = 0
    while S:
        st = [S.pop()]; n += 1
        while st:
            r, c = st.pop()
            for dr, dc in nbrs:
                q = (r + dr, c + dc)
                if q in S:
                    S.remove(q); st.append(q)
    return n

N8 = [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if (a, b) != (0, 0)]
for name, g in list(stems.items()) + list(opts.items()):
    S = cells(g)
    print(f'{name}: 黑格{len(S)}  对称轴{sym(S)}  边相邻对{edge_pairs(S)}  角接触对{corner_pairs(S)}  '
          f'8邻连通块{components(S, N8)}  行计数{[sum(1 for r,c in S if r==i) for i in range(4)]}  '
          f'列计数{[sum(1 for r,c in S if c==i) for i in range(4)]}')

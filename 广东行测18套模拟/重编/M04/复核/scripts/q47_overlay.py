"""Q47: test position-wise overlay rules (two cells -> third) along rows and along
columns, in every order. A rule is a lookup table pair->result that must be consistent
on all known triples; then it is applied to predict the missing cell."""
import itertools

from q47_features import CELLS  # noqa: E402  (same directory)

G = {}
for r in range(1, 4):
    for c in range(1, 4):
        k = f"R{r}C{c}"
        if k in CELLS:
            G[(r, c)] = CELLS[k]


def triples(lines):
    """lines: list of (cellX, cellY, cellZ) keys; yield per-position triples"""
    for a, b, z in lines:
        for i in range(4):
            for j in range(4):
                yield G[a][i][j], G[b][i][j], G[z][i][j]


def test(name, known, target):
    table, ok = {}, True
    for x, y, z in triples(known):
        if (x, y) in table and table[(x, y)] != z:
            ok = False
        table.setdefault((x, y), z)
    a, b, _ = target
    pred, unknown = [], False
    for i in range(4):
        row = ""
        for j in range(4):
            key = (G[a][i][j], G[b][i][j])
            if key in table:
                row += table[key]
            else:
                row += "?"
                unknown = True
        pred.append(row)
    match = [o for o in "ABCD" if all(
        p == "?" or p == q for pr, qr in zip(pred, CELLS[o]) for p, q in zip(pr, qr))]
    print(f"{name:28} consistent={ok} table={dict(sorted(table.items()))}")
    if ok:
        print(f"{'':28} prediction={pred} unknown={unknown} matching options={match}")


for perm in itertools.permutations(range(3)):
    # rows: columns perm[0], perm[1] -> perm[2]
    known = [((r, perm[0] + 1), (r, perm[1] + 1), (r, perm[2] + 1)) for r in (1, 2)]
    if perm[2] == 2:
        target = ((3, perm[0] + 1), (3, perm[1] + 1), (3, 3))
        test(f"rows C{perm[0]+1}+C{perm[1]+1}->C{perm[2]+1}", known, target)
    else:
        # check only consistency on rows 1,2 (target would need the unknown as input)
        test(f"rows C{perm[0]+1}+C{perm[1]+1}->C{perm[2]+1}", known, known[0])
    knownc = [((perm[0] + 1, c), (perm[1] + 1, c), (perm[2] + 1, c)) for c in (1, 2)]
    if perm[2] == 2:
        targetc = ((perm[0] + 1, 3), (perm[1] + 1, 3), (3, 3))
        test(f"cols R{perm[0]+1}+R{perm[1]+1}->R{perm[2]+1}", knownc, targetc)
    else:
        test(f"cols R{perm[0]+1}+R{perm[1]+1}->R{perm[2]+1}", knownc, knownc[0])

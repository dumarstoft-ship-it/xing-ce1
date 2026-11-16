"""Q48: each symbol is the same coin-shaped cylinder; it is recorded by the direction of
its visible end face (the end drawn as a full ellipse), in degrees clockwise from 'up':
  0 = lying flat, top face visible      180 = lying flat, bottom face visible
  90 = standing, face on the right      270 = standing, face on the left
  45/135/225/315 = tilted, face toward upper-right/lower-right/lower-left/upper-left
Readings taken from 6-10x enlargements of
/home/user/xing-ce1/模考/2026下半年广东卷_16-33季_AI可读/assets/s23_p12_i02.png
"""
S = {
    'box': [0, 180, 180, 90, 225, 0, 90, 315],
    'A':   [225, 270, 270, 315, 0, 225, 315, 0],
    'B':   [90, 0, 0, 225, 45, 90, 225, 135],
    'C':   [0, 225, 45, 90, 135, 0, 90, 180],
    'D':   [45, 225, 225, 135, 270, 225, 135, 90],
}


def signature(seq):
    """Pattern of identical symbols: first-occurrence index of each symbol."""
    seen = {}
    return [seen.setdefault(v, len(seen)) for v in seq]


def adj_angle(seq):
    return [min((b - a) % 360, (a - b) % 360) for a, b in zip(seq, seq[1:])]


box_sig = signature(S['box'])
print('box signature', box_sig, ' letters:', ''.join('abcdefgh'[i] for i in box_sig))
for k in 'ABCD':
    sig = signature(S[k])
    diff = [i + 1 for i, (x, y) in enumerate(zip(sig, box_sig)) if x != y]
    print(k, ''.join('abcdefgh'[i] for i in sig), 'same pattern' if sig == box_sig else f'differs at position(s) {diff}')

print('\nalternative reading (angle between neighbours), for reference:')
print('box', adj_angle(S['box']))
for k in 'ABCD':
    a = adj_angle(S[k])
    print(k, a, 'matches', sum(x == y for x, y in zip(a, adj_angle(S['box']))), 'of 7')

# 只读：核对 blind_input.json、selection.json、题本_待审.md 第1—15题题面与选项是否一致
import json, re
M = '/home/user/xing-ce1/广东行测18套模拟/M05/'
blind = {q['number']: q for q in json.load(open('blind_input.json', encoding='utf-8'))}
sel = {q['number']: q for q in json.load(open(M + 'selection.json', encoding='utf-8')) if q['number'] <= 15}
book = open(M + '题本_待审.md', encoding='utf-8').read()
def flat(x):
    if isinstance(x, str):
        return x
    if isinstance(x, list):
        return ''.join(flat(i) for i in x)
    if isinstance(x, dict):
        return x.get('text', '') if x.get('type') == 'text' else flat(x.get('text', ''))
    return str(x)
# 拆题本
blocks = {}
for m in re.finditer(r'^### (\d+)\.\n(.*?)(?=^### |^## |\Z)', book, flags=re.S | re.M):
    blocks[int(m.group(1))] = m.group(2)
ok = True
for n in range(1, 16):
    b, s = blind[n], sel[n]
    bs, ss = flat(b['stem']), flat(s['stem'])
    if bs != ss:
        ok = False; print(n, '题干不一致\n  blind:', bs, '\n  sel  :', ss)
    for k in 'ABCD':
        bo = flat(b['options'].get(k, '')) if b['options'] else ''
        so = flat(s['options'].get(k, '')) if s['options'] else ''
        if bo != so:
            ok = False; print(n, k, '选项不一致', bo, '|', so)
    blk = blocks.get(n, '')
    if ss not in blk:
        ok = False; print(n, '题本中未找到相同题干')
    for k in 'ABCD':
        so = flat(s['options'].get(k, '')) if s['options'] else ''
        if so and f'**{k}.** {so}' not in blk:
            ok = False; print(n, k, '题本中选项不一致')
print('全部一致' if ok else '存在不一致')

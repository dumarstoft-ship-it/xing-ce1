# 只读：查看 selection.json 结构
import json, sys
p = '/home/user/xing-ce1/广东行测18套模拟/M05/selection.json'
d = json.load(open(p, encoding='utf-8'))
print(type(d))
if isinstance(d, dict):
    print(list(d.keys())[:50])
    for k, v in d.items():
        if isinstance(v, list):
            print(k, 'list len', len(v))
            if v and isinstance(v[0], dict):
                print('  item keys:', list(v[0].keys()))
        elif isinstance(v, dict):
            print(k, 'dict keys', list(v.keys())[:30])
        else:
            print(k, repr(v)[:200])
elif isinstance(d, list):
    print('len', len(d))
    print(list(d[0].keys()))

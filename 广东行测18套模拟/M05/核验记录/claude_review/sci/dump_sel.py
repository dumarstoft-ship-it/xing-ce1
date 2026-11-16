# Read-only dump of M05 selection.json entries for Q66-70.
import json
d = json.load(open('/home/user/xing-ce1/广东行测18套模拟/M05/selection.json'))
print("keys of first item:", list(d[0].keys()))
for it in d:
    n = it.get('number') or it.get('no') or it.get('题号')
    if n in (66, 67, 68, 69, 70):
        print("=" * 100)
        print(json.dumps(it, ensure_ascii=False, indent=1))

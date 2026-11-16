# 只读：列出广东近年真题前20题（政治理论/常识部分）题面、选项、答案，用于对照命题风格
import json, sys
base = '/home/user/xing-ce1/广东/行测/2022-2026/'
for f in sys.argv[1:]:
    rows = [json.loads(l) for l in open(base + f, encoding='utf-8') if l.strip()]
    print('#'*30, f, len(rows))
    for r in rows:
        if r['question_number'] > 20:
            continue
        opts = r.get('options') or []
        if isinstance(opts, list):
            o = ' | '.join(f"{x.get('label','')}.{x.get('text','')}" if isinstance(x, dict) else str(x) for x in opts)
        else:
            o = json.dumps(opts, ensure_ascii=False)
        ans = r.get('answer', {}).get('values')
        print(f"Q{r['question_number']} [{r['section']}/{r['question_type']}] {r['stem']}")
        if o:
            print('   ', o)
        print('    答案:', ans)

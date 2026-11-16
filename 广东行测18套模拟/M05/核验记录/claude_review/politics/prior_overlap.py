# 只读：列出前四套中含指定关键词的题目题干/选项/答案，便于判断M05第2、7、9题是否与前卷重复
import json, sys
base = '/home/user/xing-ce1/广东行测18套模拟/'
kws = sys.argv[1:]
for d in ['M01', 'M02', 'M03', 'M04']:
    try:
        qs = json.load(open(base + d + '/selection.json', encoding='utf-8'))
    except Exception as e:
        print(d, 'ERR', e); continue
    for q in qs:
        s = json.dumps({k: q.get(k) for k in ['stem', 'options']}, ensure_ascii=False)
        hit = [k for k in kws if k in s]
        if hit:
            print('='*20, d, q['number'], q.get('section'), q.get('question_type'), '命中', hit, '答案', q.get('answer'))
            print(s[:900])

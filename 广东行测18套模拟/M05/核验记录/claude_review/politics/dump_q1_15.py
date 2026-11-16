# 只读：导出 selection.json 第1—15题的关键字段
import json
p = '/home/user/xing-ce1/广东行测18套模拟/M05/selection.json'
d = json.load(open(p, encoding='utf-8'))
for q in d:
    if q['number'] > 15:
        continue
    print('='*100)
    print('题号', q['number'], q['section'], q['subtype'], q['question_type'])
    for k in ['source_id','source_bank','source_file','answer','source_answer','selection_reason']:
        print(f'[{k}]', json.dumps(q.get(k), ensure_ascii=False))
    print('[stem]', json.dumps(q.get('stem'), ensure_ascii=False))
    print('[options]', json.dumps(q.get('options'), ensure_ascii=False))
    print('[analysis]')
    print(json.dumps(q.get('analysis'), ensure_ascii=False, indent=1))
    print('[edits]')
    print(json.dumps(q.get('edits'), ensure_ascii=False, indent=1))
    print('[provenance]')
    print(json.dumps(q.get('provenance'), ensure_ascii=False, indent=1))
    print('[verification]')
    print(json.dumps(q.get('verification'), ensure_ascii=False, indent=1))

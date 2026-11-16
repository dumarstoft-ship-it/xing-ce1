# 只读：核对阅览HTML中第1—15题的答案与解析文字是否与 selection.json 一致
import json, re, html
M = '/home/user/xing-ce1/广东行测18套模拟/M05/'
sel = {q['number']: q for q in json.load(open(M + 'selection.json', encoding='utf-8')) if q['number'] <= 15}
h = open(M + '阅览/M05_解析_阅览.html', encoding='utf-8').read()
text = html.unescape(re.sub(r'<[^>]+>', '\n', h))
text = re.sub(r'\n\s*\n+', '\n', text)
for n in range(1, 16):
    a = sel[n]['analysis']
    print(n, '答案', sel[n]['answer'], '| 解析原文在阅览HTML中:', a in text)
md = open(M + '答案与解析_待审.md', encoding='utf-8').read()
for n in range(1, 16):
    a = sel[n]['analysis']
    print(n, '| 解析原文在答案与解析_待审.md中:', a in md)

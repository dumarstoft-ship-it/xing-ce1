"""第81题（及第82题A、D项）：材料原句核对。"""
import json
d = json.load(open('/home/user/xing-ce1/广东行测18套模拟/重编/M07/输入/data.json'))
text = [m for m in d['materials'] if m['id'].endswith('m3')][0]['blocks'][0]['text']
first = text.split('。')[0]
print('首句：', first)
items = {'①': '坚定不移贯彻新发展理念', '②': '扎实推动高质量发展', '③': '有力落实落细各项政策措施',
         '④': '全省经济运行总体延续回升向好态势'}
for k, s in items.items():
    print(k, s, '在首句中' if s in first else '不在首句', '位置', first.find(s))
print('④位于“有力落实落细各项政策措施，”之后，是举措带来的运行状态（结果），不是推行的政策 -> A（①②③）')
for s in ['服务业增长稳定', '市场销售平稳增长', '采矿业增加值（18.8%）实现两位数增长']:
    assert s in text, s
print('第82题A、D项原句均在材料中')

import json,re,sys
raw=open('/home/user/xing-ce1/学习资料/盖句精读（词句新版·全151篇·手机版）(2).html',encoding='utf-8').read()
m=re.search(r'<script id="data" type="application/json">(.*?)</script>',raw,re.S)
D=json.loads(m.group(1)); ART={a['id']:a for a in D}
for aid in sys.argv[1:]:
    a=ART[aid]
    print('=====',aid,a['title'])
    for q in a['q']:
        print(q['id'], q['kind'], 'p',q['p'], 'ans', q['options'][q['answer']])
        print('   ', q['note'])

import json
META = {}
for f in ['meta.json', 'meta2.json', 'meta3.json']:
    META.update(json.load(open('/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/pd3b/' + f)))
SCAN_ANS = {
    'GD2017': 'xing-ce1/答案解析/2017年广东公务员考试《行测》真题答案及解析.pdf',
    'GD2015X': 'xing-ce1/答案解析/2015年广东公务员考试《行测》真题县级卷答案及解析.pdf',
    'GD2014X': 'xing-ce1/答案解析/2014年广东公务员考试《行测》真题（县级以上卷）答案及解析.pdf',
    'GD20131': 'xing-ce1/答案解析/2013年广东公务员考试《行测》一卷答案及解析.pdf',
    'GD2018': 'xing-ce1/答案解析/2018年广东省公务员录用考试《行测》真题（县级、乡镇统一卷）答案及解析.pdf',
    'GD2019X': 'xing-ce1/答案解析/2019年广东公务员考试《行测》真题（县级）答案及解析.pdf',
    'GD2021X': 'xing-ce1/答案解析/2021年0314广东公务员考试《行测》真题（县级）参考答案及解析.pdf',
    'GD2016X': 'xing-ce1/答案解析/2016年广东公务员考试《行测》真题（县级卷）答案及解析.pdf',
}
GD2021X_FILE = 'xing-ce1/真题/2021年0314广东公务员考试《行测》真题（县级）.pdf'

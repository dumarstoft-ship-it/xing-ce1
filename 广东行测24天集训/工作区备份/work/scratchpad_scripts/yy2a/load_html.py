import json, re
HTML_FILE = 'xing-ce1/学习资料/盖句精读（词句新版·全151篇·手机版）(2).html'
def load():
    raw = open('/home/user/' + HTML_FILE, encoding='utf-8').read()
    m = re.search(r'<script id="data" type="application/json">(.*?)</script>', raw, re.S)
    return json.loads(m.group(1))
def ptext(para):
    return ''.join(sg.get('t', sg.get('m', '')) for sg in para)

import re
C = '一-鿿'
def zh(t):
    t = re.sub('(?<=[A-Za-z0-9%])[ \t]+(?=[' + C + '“”])', '', t)
    t = re.sub('(?<=[' + C + '“”，。])[ \t]+(?=[A-Za-z0-9])', '', t)
    t = re.sub(r'(?<![0-9]),|,(?![0-9])', '，', t)
    t = re.sub(r'(?<![0-9]):|:(?![0-9])', '：', t)
    t = t.replace(';', '；').replace('?', '？').replace('!', '！')
    t = re.sub(r'\(\s*\)', '（  ）', t)
    t = re.sub(r'\(([^()]*[' + C + r'][^()]*)\)', r'（\1）', t)
    t = re.sub(r'\s+', ' ', t).strip()
    t = re.sub('(?<=[' + C + '。：？）”])\\s+(?=[' + C + '（“])', '', t)
    return t

# -*- coding: utf-8 -*-
"""Build clean paragraph-joined material text from the PDF text layer (content unchanged; only layout spaces and
line breaks are normalised). Paragraph starts are given explicitly per material."""
import re, os, sys, json
SP = '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/zl4b'
CJK = r'㐀-鿿＀-￯　-〿“”‘’—'
PARA = {
    'ZLM-JS2023A-1': ['2021年，我国移动互联网', '2021年，全国地级及以上城市'],
    'ZLM-ZJ2015A-3': ['经过50多年的发展', '台湾资本市场第一层次', '台湾资本市场第二层次', '台湾资本市场第三层次'],
    'ZLM-ZJ2017A-1': ['2015年国家自然科学基金委', '在研究项目系列方面', '在人才项目系列方面'],
    'ZLM-GK2016D-3': ['截至2014年12月底', '2014年，全国新登记注册市场主体', '2014年，新登记注册现代服务业企业', '2014年，新登记注册外商投资企业'],
    'ZLM-JS2016A-1': ['2015年1~7月，我国机电产品', '上述7大类劳动密集型'],
    'ZLM-JS2018A-3': ['按地区分', '2017年末，全国机动车驾驶人'],
    'ZLM-ZJ2020B-2': ['2017年，全球对清洁能源的投资', '从主要清洁能源类型看'],
}
def clean(raw, mid):
    t = raw.replace('\xa0', ' ')
    lines = [l.strip() for l in t.split('\n') if l.strip()]
    s = ''.join(lines)
    s = re.sub(r'[ \t]+', '', s)          # the materials contain no meaningful spaces (checked against screenshots)
    for p in PARA.get(mid, []):
        i = s.find(p)
        assert i >= 0, (mid, p)
        if i > 0:
            s = s[:i] + '\n' + s[i:]
    return s
if __name__ == '__main__':
    for mid in PARA:
        raw = open(f'{SP}/matprev/{mid}.txt').read()
        print('=====', mid); print(clean(raw, mid))

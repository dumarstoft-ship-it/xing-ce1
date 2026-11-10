"""Compare my planned passages against (1) every earlier-round verbal deliverable and (2) the user's HTML (盖句精读) text.
4-gram containment of my passage in the other text; reports >=0.35."""
import json, re, os, sys, html, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qx import get, raw
from simcheck import norm, grams, body
def L(p): return [json.loads(l) for l in open(p) if l.strip()] if os.path.exists(p) else []
PREV=[]
for d in ['out/YY-A','out/YY-B','out2/YY2A','out2/YY2B','out3/YY3A','out3/YY3B','out4/YY4A']:
    for q in L(f'/home/user/work/{d}/questions.jsonl'):
        PREV.append((d.split('/')[-1]+':'+q['id'], grams(norm(q.get('stem','')))))
H=open('/home/user/xing-ce1/学习资料/盖句精读（词句新版·全151篇·手机版）(2).html',encoding='utf8',errors='ignore').read()
H=re.sub(r'<script.*?</script>|<style.*?</style>','',H,flags=re.S)
HT=norm(html.unescape(re.sub(r'<[^>]+>','',H)))
# the HTML may keep its data in JSON inside <script>; also normalise the raw file
HR=norm(html.unescape(open('/home/user/xing-ce1/学习资料/盖句精读（词句新版·全151篇·手机版）(2).html',encoding='utf8',errors='ignore').read()))
HG=grams(HT)|grams(HR)
def check(keys):
    n=0
    for key in keys:
        tag,q=key.rsplit('-',1); qq=get(tag,int(q))
        nb=norm(re.sub(r'^\s*\d{1,3}\s*[、\.．]','',body(qq['text']))); g=grams(nb)
        hits=[]
        for pid,pg in PREV:
            if not pg: continue
            c=len(g&pg)/max(1,min(len(g),len(pg)))
            if c>=0.35 and len(g&pg)>=20: hits.append((round(c,2),pid))
        ch=len(g&HG)/max(1,len(g))
        if hits or ch>=0.35:
            n+=1; print(key,'PREV:',sorted(hits,reverse=True)[:4],'HTML containment=%.2f'%ch)
    print('checked',len(keys),'flagged',n,'| prev items',len(PREV),'| html chars',len(HT),len(HR))
if __name__=='__main__':
    from plan4 import PLAN, PXPLAN
    check([k for d in PLAN for k in PLAN[d]]+[k for d in PXPLAN for k in PXPLAN[d]])

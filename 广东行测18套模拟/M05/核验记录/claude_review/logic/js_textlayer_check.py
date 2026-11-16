# Compare M05 text (Q56/58/60/64/65) with the raw PDF text layer of the JS originals (pdftotext -raw), ignoring the
# question-number prefixes and option letters. Read-only; PDFs from the shallow clone at commit 407016b.
import json, subprocess, re
REPO='/home/user/xing-ce1'
P21='/home/user/dumarstoft-ship-it/xingce/2021年江苏公务员考试《行测》真题（A卷）.pdf'
P22='/home/user/dumarstoft-ship-it/xingce/2022年江苏公务员考试《行测》真题（A类）....pdf'
def page(p,n): return subprocess.run(['pdftotext','-raw','-f',str(n),'-l',str(n),p,'-'],capture_output=True,text=True).stdout
raw={('21',12):page(P21,12),('21',13):page(P21,13),('21',14):page(P21,14),('22',17):page(P22,17)}
m05={}
for l in open(f'{REPO}/广东行测18套模拟/M05/题目.jsonl',encoding='utf-8'):
    r=json.loads(l); m05[r['number']]=r
def flat(s): return re.sub(r'\s+','',s)
checks=[(56,('21',14)),(58,('21',12)),(60,('22',17)),(64,('21',13)),(65,('21',13))]
for n,key in checks:
    r=m05[n]; rp=flat(raw[key])
    parts=[('stem',''.join(b['text'] for b in r['stem']))]+[('opt'+k,''.join(b['text'] for b in v)) for k,v in r['options'].items()]
    for m in r.get('materials') or []: parts.append(('material',''.join(b['text'] for b in m['blocks'])))
    for where,t in parts:
        ok = flat(t) in rp
        print(n, where, 'found-in-PDF-text-layer(ignoring whitespace)=',ok)
    # show raw text-layer lines around key spots, to see real spaces/colons
for key,needle in [(('21',14),'隧道:'),(('21',12),'古人云'),(('22',17),'一定为真'),(('22',17),'3000'),(('21',13),'2020')]:
    t=raw[key]; i=t.find(needle); print(key, needle, repr(t[max(0,i-20):i+30]))

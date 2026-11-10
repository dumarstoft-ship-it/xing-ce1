import sys, re, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ansx import seg, info
PAT=[r'正确答案[：:]\s*([A-D])', r'故正确答案为\s*([A-D])', r'因此[，,]?\s*选择\s*([A-D])\s*选项', r'故本题答案为\s*([A-D])', r'正确选项为\s*([A-D])', r'答案为\s*([A-D])', r'故选\s*([A-D])', r'【答案】\s*([A-D])',r'正确答案是[：:]?\s*【?\s*([A-D])']
for k in sys.argv[1:]:
    tag,n=k.rsplit('-',1); n=int(n)
    r=seg(tag,n)
    if not r: print(k,'NOT FOUND'); continue
    s=r['seg']
    found=[]
    for P in PAT:
        for m in re.finditer(P,s): found.append((m.start(),m.group(1)))
    found=sorted(set(found))
    letters=[x[1] for x in found]
    disp='争议' in s
    auto=json.load(open(f'/home/user/work/answers/{tag}.json'))['answers'].get(str(n),{}).get('ans') if os.path.exists(f'/home/user/work/answers/{tag}.json') else None
    print(k, 'p',r['page'], 'letters',letters, 'auto',auto, 'DISPUTE' if disp else '', '| first:', s[:50].replace('\n',' '))

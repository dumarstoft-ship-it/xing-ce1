"""Independent safety net: OCR each source crop (300dpi) and diff against the final text (CJK characters only).
OCR is noisy, so this only lists candidate spots; every listed spot is then judged by eye against the page image."""
import json, os, re, sys, subprocess, difflib, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qx import get, crop
SP=os.path.dirname(os.path.abspath(__file__)); os.makedirs(f'{SP}/ocr300', exist_ok=True)
Q=[json.loads(l) for l in open('/home/user/work/out4/YY4B/questions.jsonl')]
def cjk(s): return ''.join(c for c in unicodedata.normalize('NFKC', s) if '一'<=c<='鿿')
tot=0
for q in Q:
    tag=q['source']['index_tag']; n=q['source']['qno']; key=f'{tag}-{n}'
    png=f'{SP}/ocr300/{key}.png'; txt=f'{SP}/ocr300/{key}'
    if not os.path.exists(txt+'.txt'):
        crop(get(tag,n), png, dpi=300)
        subprocess.run(['tesseract', png, txt, '-l', 'chi_sim', '--psm', '6'], capture_output=True, timeout=600, env=dict(os.environ, OMP_THREAD_LIMIT='2'))
    o=cjk(open(txt+'.txt',encoding='utf8').read())
    mine=cjk(q['stem']+''.join(q['options'][L] for L in 'ABCD'))
    sm=difflib.SequenceMatcher(None, mine, o, autojunk=False)
    subs=[]
    for t,i1,i2,j1,j2 in sm.get_opcodes():
        if t=='replace' and (i2-i1)==(j2-j1) and (i2-i1)<=2: subs.append((mine[max(0,i1-6):i1]+'['+mine[i1:i2]+'→'+o[j1:j2]+']'+mine[i2:i2+6]))
        elif t=='delete' and (i2-i1)<=3: subs.append(mine[max(0,i1-6):i1]+'[-'+mine[i1:i2]+']'+mine[i2:i2+6])
    cov=sum(b.size for b in sm.get_matching_blocks())/max(1,len(mine))
    tot+=len(subs)
    print(q['id'], key, 'match=%.3f'%cov, 'spots:', subs)
print('total candidate spots', tot)

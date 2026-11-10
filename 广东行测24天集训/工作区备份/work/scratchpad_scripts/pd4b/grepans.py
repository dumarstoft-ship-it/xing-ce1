# grep analysis full text by regex. usage: grepans.py PID REGEX [n] [before]
import sys, re
sys.path.insert(0,'/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/pd4b')
from ans_lib import load
pid=sys.argv[1]; pat=re.compile(sys.argv[2]); n=int(sys.argv[3]) if len(sys.argv)>3 else 1500
before=int(sys.argv[4]) if len(sys.argv)>4 else 120
f,full,offs=load(pid)
print('==========',pid,f, 'chars', len(full) if full else 0)
last=-10**9
for mm in pat.finditer(full):
    h=mm.start()
    if h-last<n: continue
    last=h
    pg=max(i for i,o in enumerate(offs) if o<=h)+1
    print('----- page',pg,'pos',h); print(full[max(0,h-before):h+n]); break

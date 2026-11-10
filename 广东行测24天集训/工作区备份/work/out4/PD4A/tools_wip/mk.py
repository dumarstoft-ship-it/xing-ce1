"""mk.py TAG Q [dpi] [--keep-opts] [--raw]: render clean asset candidate into as/<PID>-<Q>.png (PID = tag without _xc)"""
import sys
sys.path.insert(0,'/home/user/work/out2/PD2A/tools')
from rq import render
from PIL import Image
tag,q=sys.argv[1],int(sys.argv[2]); dpi=250
for x in sys.argv[3:]:
    if x.isdigit(): dpi=int(x)
out=f"as/{tag.replace('_xc','')}-{q}.png"
p=render(tag,q,out,dpi,keep_opts='--keep-opts' in sys.argv,raw='--raw' in sys.argv)
im=Image.open(p); print(p,im.size)

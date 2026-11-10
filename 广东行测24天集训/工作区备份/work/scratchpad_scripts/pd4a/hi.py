"""hi.py TAG Q [dpi] [--raw]: render one question at high dpi into hi/TAG-Q.png (keeps option letters)"""
import sys
sys.path.insert(0,'/home/user/work/out2/PD2A/tools')
from rq import render
tag,q=sys.argv[1],int(sys.argv[2]); dpi=int(sys.argv[3]) if len(sys.argv)>3 and sys.argv[3].isdigit() else 220
from PIL import Image
p=render(tag,q,f'hi/{tag}-{q}.png',dpi,keep_opts=True,raw='--raw' in sys.argv)
im=Image.open(p); print(p,im.size)

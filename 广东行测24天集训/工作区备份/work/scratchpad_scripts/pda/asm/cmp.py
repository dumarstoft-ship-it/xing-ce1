import sys, json
from PIL import Image
from render import render
c=sys.argv[1]; cells=json.loads(sys.argv[2]); X0=int(sys.argv[3]) if len(sys.argv)>3 else 98
a=render([tuple(x) for x in cells],X0=X0); b=Image.open(f'../r/z_gd20x43_o{c}.png').convert('RGB')
cv=Image.new('RGB',(b.width+10+600,575),'white'); cv.paste(b,(0,0)); cv.paste(a,(b.width+10,0)); cv.save(f'cmp{c}.png'); print('ok')

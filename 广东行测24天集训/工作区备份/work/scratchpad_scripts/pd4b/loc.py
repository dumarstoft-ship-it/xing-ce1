# locate keyword in OCR'd pages. usage: loc.py TAG REGEX
import sys,re,os,glob
tag=sys.argv[1]; pat=re.compile(sys.argv[2])
for base in ('/home/user/work/ocr','/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/pd4b/ocr'):
    d=f'{base}/{tag}'
    if not os.path.isdir(d): continue
    for f in sorted(glob.glob(d+'/p*.txt')):
        t=re.sub(r'\s','',open(f,errors='ignore').read())
        for m in pat.finditer(t):
            print(f, '|', t[max(0,m.start()-40):m.start()+160]); break

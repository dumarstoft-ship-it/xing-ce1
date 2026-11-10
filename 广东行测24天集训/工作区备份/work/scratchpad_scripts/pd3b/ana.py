import pymupdf, json, sys, re, unicodedata
pymupdf.TOOLS.mupdf_display_errors(False)
W='/home/user/work'
tag=sys.argv[1]; qno=int(sys.argv[2]); n=int(sys.argv[3]) if len(sys.argv)>3 else 1500
a=json.load(open(f'{W}/answers/{tag}.json'))
doc=pymupdf.open('/home/user/'+a['file'])
pages=[unicodedata.normalize('NFKC',pg.get_text()) for pg in doc]
full=''; offs=[]
for i,t in enumerate(pages):
    offs.append(len(full)); full+=t
pat=re.compile(r'(?:^|\n)\s*(?:第\s*|题目\s*|【解析\s*)?(?:【\s*%d\s*】|%d\s*(?:题)?\s*(?:[\.、．:：—]|\n|(?=【)|(?=正确)|(?=\s*解析)))'%(qno,qno))
hits=[m.start() for m in pat.finditer(full)]
print('file:',a['file'],'auto ans:',a['answers'].get(str(qno)))
for h in hits[:4]:
    pg=max(i for i,o in enumerate(offs) if o<=h)+1
    print('----- hit at page',pg)
    print(full[h:h+n])

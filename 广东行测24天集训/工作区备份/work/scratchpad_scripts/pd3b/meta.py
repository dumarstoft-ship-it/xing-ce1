import json, sys, os, re, unicodedata, pymupdf
pymupdf.TOOLS.mupdf_display_errors(False)
W='/home/user/work'
sel=[l.split() for l in open(sys.argv[1]) if l.strip() and not l.startswith('#')]
out={}
for row in sel:
    key, qtag, atag = row[0], row[1], row[2]
    pid,q=key.rsplit('-',1); q=int(q)
    info={'key':key,'qtag':qtag,'atag':atag}
    if qtag!='-':
        for x in json.load(open(f'{W}/index/{qtag}.json')):
            if x.get('kind')=='q' and x['qno']==q:
                info.update(file=x['file'], pages=sorted(set(s[0]+1 for s in x['segs'])), text=x['text'], images=x.get('images'))
    if atag!='-':
        a=json.load(open(f'{W}/answers/{atag}.json'))
        info['ans_file']=a['file']; info['auto']=a['answers'].get(str(q))
        doc=pymupdf.open('/home/user/'+a['file'])
        pages=[unicodedata.normalize('NFKC',pg.get_text()) for pg in doc]
        full=''; offs=[]
        for t in pages: offs.append(len(full)); full+=t
        pat=re.compile(r'(?:^|\n)\s*(?:第\s*|题目\s*|【解析\s*)?(?:【\s*%d\s*】|%d\s*(?:题)?\s*(?:[\.、．:：—]|\n|(?=【)|(?=正确)|(?=\s*解析)))'%(q,q))
        hits=[m.start() for m in pat.finditer(full)]
        info['ans_hits']=[max(i for i,o in enumerate(offs) if o<=h)+1 for h in hits]
    out[key]=info
    print(key, info.get('file','')[-40:], info.get('pages'), info.get('ans_file','')[-30:], info.get('auto'), info.get('ans_hits'))
json.dump(out,open(sys.argv[2],'w'),ensure_ascii=False,indent=1)

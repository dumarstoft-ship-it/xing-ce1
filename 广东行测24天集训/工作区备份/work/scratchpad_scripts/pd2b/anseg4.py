import json,pymupdf,unicodedata,re,sys
pymupdf.TOOLS.mupdf_display_errors(False)
# usage: anseg4.py TAG anchor_text [anchor_text...]  -> prints from anchor in analysis to next '正确答案为'
tag=sys.argv[1]
a=json.load(open(f'/home/user/work/answers/{tag}.json'))
doc=pymupdf.open('/home/user/'+a['file'])
pages=[unicodedata.normalize('NFKC',p.get_text()) for p in doc]
full='\n'.join(pages)
starts=[];acc=0
for p in pages: starts.append(acc); acc+=len(p)+1
def pg(pos):
    for i in range(len(starts)-1,-1,-1):
        if pos>=starts[i]: return i+1
for anc in sys.argv[2:]:
    i=full.find(anc)
    if i<0: print('=====',anc,'NA'); continue
    # back up to the question number line
    j=full.rfind('\n',0,max(0,i-400))
    k=full.find('正确答案为',i)
    if k<0: k=i+1500
    s=full[max(0,i-350):k+20]
    s=re.sub(r'\n+','\n',s)
    print('=====',tag,anc,'page',pg(i)); print(s[-2200:])

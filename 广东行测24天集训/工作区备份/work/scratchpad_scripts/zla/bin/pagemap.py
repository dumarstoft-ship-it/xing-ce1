import json, sys, pymupdf, unicodedata, re
pymupdf.TOOLS.mupdf_display_errors(False)
tag=sys.argv[1]
f=json.load(open(f'/home/user/work/index/{tag}.json'))[0]['file']
doc=pymupdf.open('/home/user/'+f)
for p in [int(x) for x in sys.argv[2].split(',')]:
    print(f'--- {tag} page {p} h={doc[p].rect.height:.0f}')
    for b in doc[p].get_text('blocks'):
        t=re.sub(r'\s+',' ',unicodedata.normalize('NFKC',b[4]))[:46]
        kind='IMG' if b[6]==1 else ''
        print(f'  {b[1]:6.1f}-{b[3]:6.1f} {kind} {t}')
    for im in doc[p].get_image_info():
        bb=im['bbox']; print(f'  [image] {bb[1]:.1f}-{bb[3]:.1f} x {bb[0]:.0f}-{bb[2]:.0f}')

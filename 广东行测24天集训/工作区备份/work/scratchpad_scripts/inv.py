import os, sys, json, pymupdf, hashlib
roots = ['/home/user/xing-ce1', '/home/user/xingce']
rows = []
for r in roots:
    for dp, dn, fn in os.walk(r):
        if '.git' in dp: continue
        for f in fn:
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, '/home/user')
            size = os.path.getsize(p)
            h = hashlib.md5(open(p,'rb').read()).hexdigest()
            info = {'path': rel, 'size': size, 'md5': h}
            if f.lower().endswith('.pdf'):
                try:
                    d = pymupdf.open(p)
                    info['pages'] = d.page_count
                    txt = ''.join(d[i].get_text() for i in range(min(3, d.page_count)))
                    info['text_chars_first3'] = len(txt.strip())
                    allc = sum(len(d[i].get_text().strip()) for i in range(d.page_count))
                    info['text_chars_all'] = allc
                    info['imgs_first3'] = sum(len(d[i].get_images()) for i in range(min(3,d.page_count)))
                except Exception as e:
                    info['err'] = str(e)
            rows.append(info)
json.dump(rows, open('/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/inventory_raw.json','w'), ensure_ascii=False, indent=1)
print(len(rows))

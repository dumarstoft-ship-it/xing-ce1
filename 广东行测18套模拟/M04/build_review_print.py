#!/usr/bin/env python3
"""M04审阅PDF：沿用公共考场样式，以WeasyPrint离线排版。

依赖：weasyprint>=70、fonttools、pdfplumber、pypdf、reportlab。
参数与 ../打印排版/build_print.py 相同。
"""
import importlib.util
import json
import logging
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlparse

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('m04_shared_print',HERE.parent/'打印排版/build_print.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def render(html_path,pdf_path):
    import tinyhtml5
    from weasyprint import HTML
    from fontTools.ttLib import TTFont
    logging.getLogger('weasyprint').setLevel(logging.ERROR)
    # 仅读取本次公共工具写出的固定HTML。按指定字体的实际advance宽度分列，
    # 与原工具的96pt/204pt阈值一致，不依赖浏览器脚本。
    css=(html_path.parent/'fonts.css').read_text()
    fonts={}
    for family,url in re.findall(r'font-family: "([^"]+)";\s*src: url\("([^"]+)"\)',css):
        path=unquote(urlparse(url).path)
        f=TTFont(path)
        fonts[family]=(f.getBestCmap(),f['hmtx'].metrics,f['head'].unitsPerEm)
    def width(text):
        total=0
        for ch in text:
            name='ZG Latin' if (ord(ch)<127 or ch in '°−') else 'ZG Song'
            cmap,metrics,upm=fonts[name]
            total+=metrics[cmap.get(ord(ch),'.notdef')][0]/upm*12
        return total
    root=tinyhtml5.parse(html_path.read_text(),namespace_html_elements=False)
    head=root.find('head')
    rare_style=ET.SubElement(head,'style')
    rare_style.text='''@font-face {font-family:"ZG RareSong";src:url("file:///usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc");unicode-range:U+5C95;}
    html {font-family:"ZG Latin","ZG Song","ZG RareSong";}
    .frac {display:inline-block;vertical-align:-0.45em;line-height:1;width:auto;}
    .frac > span {display:block;line-height:1.05;text-align:center;}
    .q:has(.opts) {break-inside:avoid;}'''
    decisions=[]
    for q in root.iter('div'):
        if 'q' not in q.get('class','').split():
            continue
        for el in q.iter('div'):
            classes=el.get('class','').split()
            if 'opts' in classes and 'auto' in classes:
                widest=max(width(''.join(o.itertext())) for o in el if 'opt' in o.get('class','').split())
                cls='c4' if widest<=96 else 'c2' if widest<=204 else 'c1'
                el.set('class',el.get('class','')+' '+cls)
                decisions.append({'q':int(q.get('data-n')),'widest_pt':round(widest,1),'columns':cls})
    for parent in root.iter():
        for child in list(parent):
            if child.tag=='script':
                parent.remove(child)
    # 原封面竖排条形码提示改用逐字换行，避免渲染器对writing-mode支持不同。
    for el in root.iter('div'):
        if el.get('class')=='txt':
            text=''.join(el.itertext())
            el.clear()
            el.set('class','txt')
            el.set('style','text-align:center;letter-spacing:0;line-height:2')
            for ch in text:
                span=ET.SubElement(el,'div');span.text=ch
    content='<!doctype html>'+ET.tostring(root,encoding='unicode',method='html')
    html_path.write_text(content)
    HTML(string=content,base_url=str(html_path.parent)).write_pdf(str(pdf_path))
    return {'decisions':decisions,'renderer':'WeasyPrint 70'}

module.render=render
original_paragraphs_html=module.paragraphs_html
def paragraphs_html(text,number,where,log,cls=''):
    if number==64 and where=='题干':
        parts=[x.strip() for x in text.splitlines() if x.strip()]
        log.add(number,where,'保留发言者及设问分段',text,'共'+str(len(parts))+'段')
        attr=f' class="{cls}"' if cls else ''
        return [f'<p{attr}>{module.inline_html(module.norm_text(x,number,where,log))}</p>' for x in parts]
    return original_paragraphs_html(text,number,where,log,cls)
module.paragraphs_html=paragraphs_html
# 铁路材料可完整放在一页；避免首段单独留在上一组的页尾。
module.SPREAD_BREAKS.add('M04-M04')
# WeasyPrint以CSS家族名命名嵌入子集；仍仅允许明确指定的五种角色。
module.ALLOWED_FONT=re.compile(r'(FZSSJW|FZHTJW|FZKTJW|LiberationSerif|TimesNewRoman|Times|LiberationSans|Arial|ZG[- ]?(?:Song|Hei|Kai|Latin|RareSong))',re.I)
if __name__=='__main__':
    module.main()

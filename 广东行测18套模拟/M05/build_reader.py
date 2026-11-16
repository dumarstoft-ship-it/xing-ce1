#!/usr/bin/env python3
"""Standalone, answer-separated HTML viewers; not the official print template."""
import json,html,re,base64,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent;R=D.parents[1];O=D/'阅览';O.mkdir(exist_ok=True)
questions=[json.loads(s) for s in (D/'题目.jsonl').read_text().splitlines() if s.strip()]
rows=json.loads((D/'selection.json').read_text())
STYLE='''body{max-width:850px;margin:40px auto;padding:0 24px;font-family:"Noto Serif CJK SC","Songti SC","SimSun",serif;line-height:1.85;font-size:18px;color:#141414;background:white}h1{font-size:28px;border-bottom:2px solid;padding-bottom:15px}h2{font-size:24px;margin-top:55px}article{margin:26px 0 40px;break-inside:avoid}h3{font-size:19px;margin:0 0 10px}.text{white-space:pre-wrap;overflow-wrap:anywhere}img{display:block;max-width:100%;height:auto;margin:18px auto}table{border-collapse:collapse;width:100%;font-size:15px;margin:18px 0}td,th{border:1px solid #777;padding:6px 8px;text-align:center}th{font-weight:700}td:first-child{text-align:left}.option{margin:8px 0}.option strong{margin-right:14px}.option>.text{display:inline}.fraction{display:inline-grid;vertical-align:middle;text-align:center;line-height:1.2;font-size:.95em;margin:0 3px}.fraction>span:first-child{border-bottom:1px solid;padding:0 3px 2px}.fraction>span:last-child{padding-top:2px}.small{font-size:14px;color:#555}a{color:#184975}.material{margin:25px 0 35px;padding-bottom:15px;border-bottom:1px solid #aaa}@media print{body{font-size:12pt;line-height:1.7;margin:0;max-width:none}h2{break-before:page}.small{font-size:9pt}@page{size:A4;margin:18mm 20mm}}'''
def formula(m):
 s=html.escape(m.group(1))
 s=re.sub(r'\\frac\{([^{}]+)\}\{([^{}]+)\}',lambda m:'<span class="fraction"><span>'+m[1]+'</span><span>'+m[2]+'</span></span>',s)
 s=re.sub(r'\\(?:mathrm|text)\{([^{}]+)\}',r'\1',s)
 s=re.sub(r'_\{([^{}]+)\}',r'<sub>\1</sub>',s);s=re.sub(r'_([A-Za-z0-9])',r'<sub>\1</sub>',s)
 s=re.sub(r'\^\{([^{}]+)\}',r'<sup>\1</sup>',s);s=re.sub(r'\^([A-Za-z0-9])',r'<sup>\1</sup>',s)
 return s

def rich(s):
 # Display-only reflow: keep words, intra-line spaces and explicit structural
 # boundaries. A period at a source soft wrap does NOT create a paragraph.
 original=s
 keep=re.compile(r'^(?:[（(]\d+[）)]|[①②③④⑤⑥⑦⑧⑨⑩]|[\u4e00-\u9fff]{1,4}[：:]|以下|下列|根据|依次|填入|将以上|这段)')
 lines=s.split('\n');outtext=lines[0]
 for line in lines[1:]:
  outtext+=('\n' if not line or keep.match(line) or outtext.endswith('\n') else '')+line
 assert outtext.replace('\n','')==original.replace('\n','')
 s=outtext
 out=[];p=0
 for m in re.finditer(r'\$([^$]+)\$',s):
  out.append(html.escape(s[p:m.start()]));out.append(formula(m));p=m.end()
 out.append(html.escape(s[p:]));return ''.join(out).replace('&lt;u&gt;','<u>').replace('&lt;/u&gt;','</u>')
def blocks(bs):
 out=[]
 for b in bs:
  if b['type']=='text':out.append('<div class="text">'+rich(b['text'])+'</div>')
  elif b['type']=='figure':
   f=R/b['path'];src='data:image/png;base64,'+base64.b64encode(f.read_bytes()).decode()
   width=min(650,max(300,b.get('width_px',600)))
   out.append(f'<img alt="题图" style="width:{width}px" src="{src}">')
  elif b['type']=='table':
   out.append('<p><strong>'+html.escape(b.get('title',''))+'</strong></p><table><thead><tr>')
   out.extend('<th>'+html.escape(str(x))+'</th>' for x in b['headers']);out.append('</tr></thead><tbody>')
   for row in b['rows']:out.append('<tr>'+''.join('<td>'+html.escape(str(x))+'</td>' for x in row)+'</tr>')
   out.append('</tbody></table>')
   if b.get('notes'):out.append('<p>'+html.escape(b['notes'])+'</p>')
 return '\n'.join(out)
def page(title,body):return '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>'+title+'</title><style>'+STYLE+'</style><body>'+body+'</body></html>'
_cfg=json.loads((D/'paper.json').read_text(encoding='utf-8')) if 'D' in globals() else {}
body='<h1>广东行测模拟 M05｜第五套题本</h1><p>90题 · 90分钟 · '+_cfg.get('version','')+'</p><p class="small">仅为题本阅览页，不含答案；正式打印请用打印版PDF。第1—4题判断，第5—8题单选，第9—10题多选，其余单选。</p>'
section=None;seen=set();groups={}
for q in questions:
 for m in q['materials']:groups.setdefault(m['id'],[]).append(q['number'])
for q in questions:
 if q['section']!=section:section=q['section'];body+='<h2>'+section+'</h2>'
 for m in q['materials']:
  if m['id'] not in seen:
   ns=groups[m['id']];label=f'材料：回答第{ns[0]}题' if len(ns)==1 else f'材料：回答第{ns[0]}—{ns[-1]}题'
   body+='<section class="material"><h3>'+label+'</h3>'+blocks(m['blocks'])+'</section>';seen.add(m['id'])
 body+='<article id="q'+str(q['number'])+'"><h3>'+str(q['number'])+'.</h3>'+blocks(q['stem'])
 if q['question_type']=='true_false':body+='<p>（　）</p>'
 elif q['options_mode']!='in_figure':
  for k,v in q['options'].items():body+='<div class="option"><strong>'+k+'.</strong>'+blocks(v)+'</div>'
 body+='</article>'
body+='<p>—— 全部题目结束 ——</p>'
(O/'M05_题本_阅览.html').write_text(page('M05第五套题本',body),encoding='utf-8')
body='<h1>M05｜答案与解析</h1><p class="small">此页含答案。编辑核验完成，独立外审未开始；题源和证据边界详见完整资料包。</p>'
for st in range(0,90,10):
 rs=rows[st:st+10];body+='<table><tr>'+''.join('<th>'+str(q['number'])+'</th>' for q in rs)+'</tr><tr>'+''.join('<td>'+q['answer']+'</td>' for q in rs)+'</tr></table>'
for q in rows:
 body+='<article><h3>第'+str(q['number'])+'题　'+q['answer']+'</h3><p>'+html.escape(q['analysis'])+'</p><p class="small">来源：'+q['source_id']+'</p>'
 if q.get('source_notice'):body+='<p class="small">'+html.escape(q['source_notice'])+'</p>'
 for ref in q.get('provenance',{}).get('references',[]):body+='<p class="small"><a href="'+html.escape(ref['url'],quote=True)+'">'+html.escape(ref['title'])+'</a>：'+html.escape(ref['locator'])+'</p>'
 body+='</article>'
(O/'M05_解析_阅览.html').write_text(page('M05第五套解析',body),encoding='utf-8')
print('Standalone HTML readers built; no external images or font files.')

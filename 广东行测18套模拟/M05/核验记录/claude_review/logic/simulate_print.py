# Simulate what the project's print pipeline (build_print.py @ HEAD c583368) would print for M05 Q51-65:
# imports the module read-only and applies norm_text + reflow to stems/materials/options. Writes nothing to the repo.
import importlib.util, json, sys
REPO='/home/user/xing-ce1'
spec=importlib.util.spec_from_file_location('bp', f'{REPO}/广东行测18套模拟/打印排版/build_print.py')
bp=importlib.util.module_from_spec(spec); spec.loader.exec_module(bp)
log=bp.Log()
rows=[json.loads(l) for l in open(f'{REPO}/广东行测18套模拟/M05/题目.jsonl',encoding='utf-8') if l.strip()]
def show(s): return s.replace(' ','␣')
for r in rows:
    n=r['number']
    if not 51<=n<=65: continue
    print('='*8, n)
    for m in r.get('materials') or []:
        for b in m['blocks']:
            if b['type']=='text':
                for p in bp.reflow(bp.norm_text(b['text'],n,'资料文字',log),n,'资料文字',log): print('  [材料段] '+show(p))
    for b in r['stem']:
        if b['type']=='text':
            for p in bp.reflow(bp.norm_text(b['text'],n,'题干',log),n,'题干',log): print('  [题干段] '+show(p))
    for k,v in r['options'].items():
        t=''.join(x.get('text','') for x in v)
        t2=bp.norm_text(t,n,'选项'+k,log)
        if t2!=t: print(f'  [选项{k}] '+show(t2))
print('\n排版日志（Q51-65）:')
for it in log.items:
    print('  ', json.dumps(it, ensure_ascii=False))

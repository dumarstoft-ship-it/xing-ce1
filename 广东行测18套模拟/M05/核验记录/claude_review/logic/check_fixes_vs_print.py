# Check that the proposed whitespace fixes survive build_print.py (HEAD) reflow unchanged in paragraphing:
# number of printed paragraphs == number of lines in the proposed text, and no "合并源PDF行末硬换行" entries remain.
import importlib.util, json
REPO='/home/user/xing-ce1'
spec=importlib.util.spec_from_file_location('bp', f'{REPO}/广东行测18套模拟/打印排版/build_print.py')
bp=importlib.util.module_from_spec(spec); spec.loader.exec_module(bp)
fx=json.load(open('proposed_fixes.json',encoding='utf-8'))
for n,cs in fx.items():
    for c in cs:
        log=bp.Log()
        paras=bp.reflow(bp.norm_text(c['改为'],int(n),c['位置'],log),int(n),c['位置'],log)
        want=[x for x in c['改为'].split('\n') if x.strip()]
        merges=[i for i in log.items if i['类型']=='合并源PDF行末硬换行']
        print(f'第{n}题 {c["位置"]}: 底稿行数={len(want)} 打印段数={len(paras)} 打印期合并={len(merges)} ->', 'OK' if len(want)==len(paras) and not merges else 'CHECK')

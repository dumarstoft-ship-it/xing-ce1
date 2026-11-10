import sys, json, subprocess, os
sys.path.insert(0, os.path.dirname(__file__))
from sel import SEL
W = '/home/user/work'; SP = '/tmp/claude-0/-home-user/1da31e5f-c9a0-5fe9-aa65-8db5d3863581/scratchpad/zl2a'
EXTRA = {
 'SD2021_xc': 'xingce/2021年山东公务员考试《行测》真题参考答案及解析.pdf',
 'SC2022H_xc': 'xingce/2022年四川下半年公务员录用考试《行测》 答案解析_decrypted.pdf',
 'SC2024_xc': 'xingce/2024年四川省公务员录用考试《行测》答案解析.pdf',
 'JS2024A_xc': 'xingce/2024年江苏省公务员录用考试《行测》（A类）答案+解析.pdf',
}
for g, mats in SEL.items():
    for mid, tag, qs in mats:
        try: f = json.load(open(f'{W}/answers/{tag}.json'))['file']
        except Exception: f = EXTRA.get(tag)
        if tag in EXTRA: f = EXTRA[tag]
        if not f or not os.path.exists('/home/user/' + f if not f.startswith('/') else f):
            print(tag, 'NO ANALYSIS FILE', f); continue
        for q in qs:
            out = subprocess.run(['python3', f'{SP}/bin/ans.py', f, str(q), '1500'], capture_output=True, text=True).stdout
            open(f'{SP}/v/ans/{tag}_{q}.txt', 'w').write(f + '\n' + out)
            first = [l for l in out.split('\n') if l.strip()][:3]
            print(tag, q, '|', ' / '.join(first)[:160])

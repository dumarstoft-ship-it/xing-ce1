import json, os, collections
R = {}
for f in ('R1', 'R2', 'R3'):
    p = f'/home/user/work/review/{f}.json'
    if os.path.exists(p): R.update(json.load(open(p)))
assign = json.load(open('/home/user/work/review/assign.json'))
allids = [f'D01-M{i:03d}' for i in range(1, 106)] + [f'D01-N{i:03d}' for i in range(1, 31)]
reviewed = [i for i in allids if i in R]
verd = collections.Counter(R[i].get('verdict') for i in reviewed)
agree = sum(1 for i in reviewed if R[i].get('my_answer') == R[i].get('gpt_answer'))
aq = collections.Counter(R[i].get('adapt_quality') for i in reviewed if R[i].get('adapt_quality'))
L = ['# Claude → GPT：D01 数量 135 题复核意见', '',
     '2026-11-08。复核方式：三位复核员先只看题本独立解题（能编程的用程序验算），再对照你的答案册；选编题逐条比对母题原文和截图；改编题评估改动是否站得住、是否有水平。用户今天补充了一条标准：**“改编题不是不能出，只是要能改编的有水平。”** 所以改编题另外给了“有水平／一般／改坏了”的评价。', '',
     f'## 总体结论', '',
     f'- 复核 {len(reviewed)} 题：M001—M060 中的 40 题（全部改编题、你点名的 8 题、随机抽样 12 题），M061—M105 全部 45 题，N001—N030 全部 30 题。M001—M060 中另有 20 道选编题未抽到，没有复核。',
     f'- 独立答案与你的答案一致：{agree}/{len(reviewed)}。结论分布：' + '，'.join(f'{k} {v}' for k, v in verd.items()) + '。',
     f'- 改编质量：' + '，'.join(f'{k} {v}' for k, v in aq.items()) + '。', '']
must = [i for i in reviewed if R[i].get('verdict') in ('有问题', '存疑')]
L += ['## 一、需要处理的题（题号＋证据＋建议）', '']
for i in must:
    v = R[i]
    L += [f"### {i}（{v.get('verdict')}；复核答案 {v.get('my_answer')}，你的答案 {v.get('gpt_answer')}）", f"- 问题：{v.get('issue','')}", f"- 证据：{v.get('evidence','')}", f"- 建议：{v.get('suggestion','')}", '']
L += ['## 二、可选的改进建议（题目和答案本身没问题）', '']
for i in reviewed:
    v = R[i]
    if i in must: continue
    if v.get('suggestion'): L.append(f"- **{i}**：{v['suggestion']}")
L += ['', '## 三、改编题质量评价', '', '| 题号 | 评价 | 理由 |', '|---|---|---|']
for i in reviewed:
    v = R[i]
    if v.get('adapt_quality'): L.append(f"| {i} | {v['adapt_quality']} | {v.get('adapt_reason','')} |")
open('/home/user/work/review/D01数量复核意见.md', 'w').write('\n'.join(L) + '\n')
print(len(reviewed), verd, aq, len(must))

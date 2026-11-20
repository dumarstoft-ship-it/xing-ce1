"""M11 第66题：某可燃物着火点为t，图中①—⑤各点的温度与O₂含量，燃烧火势从大到小。选项 A①②③ B②④⑤ C③④⑤ D⑤④②
题图读数（看图）：①在纵轴上（O₂含量为0），温度高于t；②、④在虚线t上，④的O₂多于②；③温度低于t；
⑤温度高于t、O₂含量最多。燃烧条件：温度达到着火点且有氧气；O₂越多（温度越高）燃烧越剧烈。"""
pts = {'①': dict(T=1.5, O2=0.0), '②': dict(T=1.0, O2=1.0), '③': dict(T=0.5, O2=1.8),
       '④': dict(T=1.0, O2=2.6), '⑤': dict(T=1.6, O2=3.5)}          # T以着火点t为1
burn = [k for k, p in pts.items() if p['T'] >= 1.0 and p['O2'] > 0]
order = sorted(burn, key=lambda k: (pts[k]['O2'], pts[k]['T']), reverse=True)
print('能燃烧的点', burn, '火势从大到小', ''.join(order))
assert ''.join(order) == '⑤④②'
opts = {'A': '①②③', 'B': '②④⑤', 'C': '③④⑤', 'D': '⑤④②'}
print('答案：', [k for k, v in opts.items() if v == ''.join(order)], '；B项是同三点的从小到大顺序')

"""S01 第67题：匀速直线运动的高铁车厢内竖直上抛小球，判断①—④。 选项 A①③ B③④ C②③ D①④
以地面为参考系：小球水平速度=车速v（惯性），竖直方向上抛初速u。分别取两种车速比较。"""
g, u = 9.8, 3.0
res = {}
for v in (50.0, 90.0):                     # 两种车速（m/s）
    t_top = u / g
    vy_top = u - g * t_top                 # 最高点竖直速度
    T = 2 * u / g                          # 落回抛出高度所需时间
    x_ball_ground = v * T                  # 对地水平位移
    x_hand_ground = v * T                  # 抛球的手（随车）对地水平位移
    res[v] = dict(vy_top=vy_top, T=T, rel_train=x_ball_ground - x_hand_ground, ground=x_ball_ground)
    print('车速%.0f：最高点竖直速度%.3f，空中时间%.3fs，落点相对车厢偏移%.3f m，对地水平位移%.2f m'
          % (v, vy_top, T, res[v]['rel_train'], res[v]['ground']))
s1 = all(abs(r['vy_top']) < 1e-12 for r in res.values())          # ① 成立
s2 = False                                                         # ② 最高点竖直对地速度为0，不是最大
s3 = res[90.0]['rel_train'] < res[50.0]['rel_train'] or res[90.0]['ground'] < res[50.0]['ground']
s4 = abs(res[90.0]['T'] - res[50.0]['T']) < 1e-12                  # ④ 成立
print('①', s1, '②', s2, '③', s3, '④', s4)
assert (s1, s2, s3, s4) == (True, False, False, True)
print('答案：D（①④）')

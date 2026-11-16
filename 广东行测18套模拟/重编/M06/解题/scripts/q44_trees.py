# 第44题：路长450米，两侧种；每15米一棵柳树，两端都种；相邻柳树之间等距种2棵松树。松树比柳树多几棵？
L, gap = 450, 15
willow_one_side = L // gap + 1
pine_one_side = (L // gap) * 2
diff_one = pine_one_side - willow_one_side
print("单侧 柳", willow_one_side, "松", pine_one_side, "差", diff_one, "；两侧差", 2 * diff_one)
assert 2 * diff_one == 58
# 逐米模拟一侧
pos_w = list(range(0, L + 1, gap))
pos_p = [p + gap * k / 3 for p in pos_w[:-1] for k in (1, 2)]
assert len(pos_w) == 31 and len(pos_p) == 60
print("答案: D（B=29 只算了一侧）")

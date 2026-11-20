"""S02 第44题：周长2000米的环湖绿道，每50米一盏路灯，共几盏。 选项 A40 B41 C80 D81
环形植树：棵数=周长÷间隔。用位置枚举验证。"""
positions = {(50 * k) % 2000 for k in range(0, 1000)}
print('路灯数', len(positions))
assert len(positions) == 40
print('按直线两端都种算：', 2000 // 50 + 1, '（B项）')

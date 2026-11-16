# 第45题：长方形ABCD面积36，E为AB中点，S△BEF=5，F在BC上，求阴影△EFD面积
from fractions import Fraction as F
# 设 AB=h（竖边），BC=w（横边），wh=36。只依赖比例，取若干组(w,h)验证结果不变
for w, h in [(9, 4), (6, 6), (12, 3), (F(36, 5), 5)]:
    assert w * h == 36
    BE = F(h) / 2
    BF = 2 * 5 / BE                     # 1/2*BE*BF=5
    assert 0 < BF < w
    AED = F(1, 2) * (F(h) / 2) * w      # 9
    BEF = F(1, 2) * BE * BF             # 5
    FCD = F(1, 2) * (w - BF) * h        # 8
    shade = 36 - AED - BEF - FCD
    print(w, h, "AED", AED, "BEF", BEF, "FCD", FCD, "阴影", shade)
    assert shade == 14
# 易错：BF/BC=5/9 → FC/BC=4/9，若把△FCD算成 4/9×36=16（忘了乘1/2）→ 36-9-5-16=6；若把△AED当成1/2×36/2=9以外的值...
print("忘记△AED是长方形1/4：若按1/2算→", 36 - 18 - 5 - 8)

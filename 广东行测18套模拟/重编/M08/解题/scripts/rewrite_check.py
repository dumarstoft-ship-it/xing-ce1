"""M08第89题改写（第4组，铁路货运）：四项与上年相比增加或减少的数量排序。

材料：石油运量13050万吨，增长5.4%；粮食运量6847万吨，下降8.0%；冶炼物资运量90986万吨，下降5.3%；
全国铁路货运总发送量50.35亿吨（比上年增加0.51亿吨），其中国家铁路39.11亿吨、增长0.2%，其他铁路增长3.9%。
同时按增速的舍入区间（±0.05个百分点）和其他铁路现期量的舍入区间核对排序是否稳定。
"""
from itertools import product

def change(cur, r):           # 现期量×|增速|÷(1＋增速)，r带符号（%）
    return cur * abs(r) / (100 + r)

other = (50.35 - 39.11) * 10000          # 万吨
items = {"①石油": (13050, 5.4), "②其他铁路": (other, 3.9), "③粮食": (6847, -8.0), "④冶炼物资": (90986, -5.3)}
vals = {k: change(c, r) for k, (c, r) in items.items()}
for k, v in vals.items():
    print(f"{k}：{v:.1f}万吨（{'增加' if items[k][1] > 0 else '减少'}）")
order = sorted(vals, key=vals.get, reverse=True)
print("从多到少：", "".join(k[0] for k in order))
assert "".join(k[0] for k in order) == "④②①③"

# 另一种算法：其他铁路增量＝总增量－国家铁路增量
alt = 0.51 * 10000 - change(39.11 * 10000, 0.2)
print(f"其他铁路（总增量－国家铁路增量）：{alt:.1f}万吨")
assert vals["④冶炼物资"] > max(alt, vals["②其他铁路"]) and min(alt, vals["②其他铁路"]) > vals["①石油"]

# 舍入稳定性：每个增速取±0.05个百分点、其他铁路现期量取±0.01亿吨的边界组合，排序不变
stable = True
for d1, d2, d3, d4, dq in product((-0.05, 0.05), repeat=5):
    v = {"①": change(13050, 5.4 + d1), "②": change(other + dq * 10000, 3.9 + d2),
         "③": change(6847, -8.0 + d3), "④": change(90986, -5.3 + d4)}
    stable &= "".join(sorted(v, key=v.get, reverse=True)) == "④②①③"
print("舍入边界下排序都不变：", stable)
assert stable

opts = {"A": "②④①③", "B": "④②③①", "C": "④②①③", "D": "②①③④"}
print("答案：", [k for k, s in opts.items() if s == "④②①③"])
# 错项来由：A按现期量排（其他铁路11.24亿吨＞冶炼物资9.10亿吨）；D把减少当负数、按增量从多到少排
signed = {"①": vals["①石油"], "②": vals["②其他铁路"], "③": -vals["③粮食"], "④": -vals["④冶炼物资"]}
assert "".join(sorted(signed, key=signed.get, reverse=True)) == opts["D"]
cur = {"①": 13050, "②": other, "③": 6847, "④": 90986}
assert "".join(sorted(cur, key=cur.get, reverse=True)) == opts["A"]
print("A＝按现期量排，D＝按带符号的增量排：核对无误")


# ---------------------------------------------------------------------------
# M08第78题改写（第2组，国内旅游）：四项同比增速排序。
# 材料：全国国内出游48.9亿人次，增长93.3%；城镇居民37.6亿人次，增长94.9%；农村居民出游花费增长106.4%。
print("\n第78题改写")
tot, r_tot, urb, r_urb, r_rural_spend = 48.9, 93.3, 37.6, 94.9, 106.4

def rural_rate(t, rt, u, ru):
    return ((t - u) / (t / (1 + rt / 100) - u / (1 + ru / 100)) - 1) * 100

r_rural = rural_rate(tot, r_tot, urb, r_urb)
print(f"农村居民出游人次：2023年{tot - urb:.1f}亿，2022年{tot / 1.933 - urb / 1.949:.2f}亿，增速{r_rural:.1f}%")
rates = {"①": r_tot, "②": r_urb, "③": r_rural, "④": r_rural_spend}
order78 = "".join(sorted(rates, key=rates.get, reverse=True))
print("从高到低：", order78)
assert order78 == "④②①③"
# 舍入稳定性：人次±0.05亿、增速±0.05个百分点的全部边界组合
ok = all("".join(sorted({"①": r_tot + c, "②": r_urb + d, "③": rural_rate(tot + a, r_tot + c, urb + b, r_urb + d),
                         "④": r_rural_spend + e}.items(), key=lambda kv: kv[1], reverse=True)[i][0] for i in range(4)) == "④②①③"
         for a, b, c, d, e in product((-0.05, 0.05), repeat=5))
print("舍入边界下排序都不变：", ok)
assert ok
opts78 = {"A": "④③②①", "B": "④②③①", "C": "④①②③", "D": "④②①③"}
print("答案：", [k for k, s in opts78.items() if s == order78])
# 混合增长率：总人次增速介于城镇、农村之间；城镇94.9%＞总93.3%，故农村＜93.3%
assert r_urb > r_tot > r_rural

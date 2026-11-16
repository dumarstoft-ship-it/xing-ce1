"""M07改写的资料题复算：第89题（原第79题，四个地区互联网业务收入同比增量排序）。"""
total, nat = 8676, 5.6                     # 表1：2024年1—6月业务收入；表2：2024年1—6月同比增速
mid, west, ne = 408.8, 525.4, 20.8
east = total - mid - west - ne
rate = {"东部": nat - 0.4, "中部": nat + 6.4, "西部": 4.6, "东北": -2.1}
rev = {"东部": east, "中部": mid, "西部": west, "东北": ne}
inc = {k: rev[k] * rate[k] / (100 + rate[k]) for k in rev}
order = sorted(inc, key=inc.get, reverse=True)
print("东部收入", round(east, 1), "增速", rate["东部"], {k: round(v, 2) for k, v in inc.items()}, "→", "、".join(order))
assert order == ["东部", "中部", "西部", "东北"]                                   # B
assert sorted(rate, key=rate.get, reverse=True) == ["中部", "东部", "西部", "东北"]  # 按增速：C
assert sorted(rev, key=rev.get, reverse=True) == ["东部", "西部", "中部", "东北"]    # 按收入：A
print("复算一致")

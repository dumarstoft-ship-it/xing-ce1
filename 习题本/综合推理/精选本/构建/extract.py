#!/usr/bin/env python3
"""从原书 PDF 提取 337 题的结构化记录。

python3 extract.py <原书PDF> <records.json>

原书版式：第1—4页分类目录；第5页起每题两页（正面练习页、背面草稿解析页）；
第679页起为题源说明与索引。小组划分取自原书分类目录。
"""
import json, re, subprocess, sys

GROUPS = """一一对应 · 删去不可能的配对 01–13
三项对应 · 共用一组表头 14–19
相对高低 · 接出比较链 20–26
成对数值 · 同向相加消去重叠项 27–32
固定名次 · 从已知位置填人 33–35
相邻与间隔 · 在位置格上排块 36–44
方位与时段 · 在格中放入对象 45–47
逐轮获知 · 排除当时还分不清的情形 48–50
多对多对应 · 逐行逐列补名额 51–56
多项属性 · 分行计数再对齐 57–63
集合人数 · 算重叠或给出上下界 64–71
按名单选人 · 先核名额再查禁配 72–78
分组去向 · 按各组空位补人 79–85
检验容量 · 排除人数过多或不足的分支 86–94
局部名额 · 由剩余人选推出必选关系 95–96
总分与胜负 · 还原每场得分 97–101
两种去留 · 取两条分支的共同结论 102–114
沿箭头推理 · 找到能启动的事实 115–132
必要条件 · 从结果追回门槛 133–150
缺一条箭头 · 从待证结论反推 151–160
前件是“或” · 逆否后逐项排除 161–164
至少一项成立 · 划去一支再接下一条 165–173
前件是“且” · 保留组合，等另一项 174–190
后件是“且” · 分开使用两个结论 191–204
后件是“或” · 两项都排除才能逆推 205–212
恰一与同值 · 绑定两个对象的状态 213–218
条件触发的恰一 · 在前件成立后绑定 219–220
规则连锁 · 从冲突倒推起点 221–224
全称与存在 · 沿同一个人传递属性 225–236
否定全称 · 留下一个反例或见证 237–246
逐行核对 · 数出每种结果的真话数 247–256
每人恰一真 · 一句命中就划掉另一句 257–264
互为否定的两句话 · 先扣一真一假 265–282
真假配额 · 先扣已经占用的名额 283–293
多行命中计数 · 按列分配真假名额 294–296
整句真假 · 把判断转成对象的状态 297–311
原题辨析 · 查清词义与隐含前提 312–323
原题辨析 · 用第二种安排检验唯一性 324–329
原题辨析 · 用反例核对参考答案 330–337"""
CATS = [("对应与排序", 1, 50), ("分组与名额", 51, 114), ("复合条件与约束传播", 115, 246),
        ("真假判断", 247, 311), ("原题辨析", 312, 337)]

def page_text(pdf, i):
    return subprocess.run(["pdftotext", "-layout", "-f", str(i), "-l", str(i), pdf, "-"],
                          capture_output=True, text=True, check=True).stdout

def squeeze(text, indent_tables=False):
    out, blank = [], 0
    for l in text.splitlines():
        if not l.strip():
            blank += 1
            if blank == 1: out.append("")
            continue
        blank = 0
        out.append("  " + l.strip() if indent_tables and re.match(r"^\s{6,}\S", l) else l.strip())
    return "\n".join(out).strip()

def main():
    pdf, out = sys.argv[1], sys.argv[2]
    groups = []
    for line in GROUPS.splitlines():
        m = re.match(r"(.+?) (\d+)–(\d+)$", line)
        groups.append((m.group(1), int(m.group(2)), int(m.group(3))))
    recs = []
    for i in range(1, 338):
        pp, sp = 3 + 2 * i, 4 + 2 * i
        pt, st = page_text(pdf, pp), page_text(pdf, sp)
        source = re.sub(r"^综合推理 / 二刷题本\s+", "", pt.splitlines()[0]).strip()
        sol_header = re.sub(r"^综合推理 / 二刷题本\s+", "", st.splitlines()[0]).strip()
        m = re.search(r"(\d{2,3})\s+二刷练习", pt)
        assert m and int(m.group(1)) == i, f"第{pp}页不是第{i}题练习页"
        stem = re.sub(r"^.*?二刷练习\s*\n", "", pt, flags=re.S)
        stem = re.sub(r"\n\s*草稿\s+作答\s*_+.*$", "", stem, flags=re.S)
        m = re.search(r"\n\s*(\d{2,3})\s+草稿解析\s+答案\s*([^\n]+)", st)
        assert m and int(m.group(1)) == i, f"第{sp}页不是第{i}题解析页"
        sol = re.sub(r"\n\s*分类目录\s+\d+\s*$", "", st[m.end():].rstrip(), flags=re.S)
        g = next(g for g in groups if g[1] <= i <= g[2])
        assert sol_header.split(" / ")[0].strip() == g[0], (i, sol_header)
        recs.append(dict(idx=i, page=pp, spage=sp, source=source, sol_header=sol_header,
                         group=g[0], category=next(c[0] for c in CATS if c[1] <= i <= c[2]),
                         origin=sol_header.split(" / ")[1] if " / " in sol_header else "",
                         answer=m.group(2).strip(), stem=squeeze(stem), solution=squeeze(sol, True)))
    json.dump(recs, open(out, "w"), ensure_ascii=False, indent=1)
    print(f"提取 {len(recs)} 题 → {out}")

if __name__ == "__main__":
    main()

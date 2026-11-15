#!/usr/bin/env python3
"""M03 组合对应型单选题（第6、12、13、15题）的选项区分度枚举（只读仓库）。

用法：
    python3 option_discrimination.py [仓库根目录]
输出：
    - 终端打印：各题“知道哪几项即可锁定答案”、每一项单独能排除哪些选项、
      以及“题面字面即可排除”的选项（例如把“××客家话”归入非客家方言）
    - 同目录 option_discrimination.out.json

方法：直接从 selection.json 读取当前选项，把每个选项按“、”拆成依次对应的标签；
以编辑答案为正确组合，枚举考生已知的题项子集，求与已知项相容的剩余选项集合。
这只度量“组合结构”的区分度，不判断知识本身对错（对错由人工依据核对）。
本脚本不修改仓库任何文件。
"""
import itertools
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/home/user/xing-ce1")
SEL = ROOT / "广东行测18套模拟" / "M03" / "selection.json"

# 题项名称（人工从题干摘出，仅用于打印）及字面线索：题项名称本身已含类别词时，
# 把它归入其他类别的选项可“凭字面排除”，不需要任何知识。
ITEMS = {
    6: ["①各民族文化融为一体、共同维护国家团结", "②对世界文明成果兼收并蓄", "③面对新问题不断革新创造"],
    12: ["广州话", "梅州客家话", "潮州话", "雷州话"],
    13: ["确立思想建党、政治建军原则", "制定抗日民族统一战线的策略方针", "明确实行全面抗战路线"],
    15: ["纪传体通史", "纪传体断代史", "编年体通史"],
}
LEXICAL_CUES = {12: {1: "客家方言"}}  # 第12题第2项“梅州客家话”字面已含“客家”


# 审稿建议的替代选项（不改答案字母），与当前稿用同一方法评估；仅为“如果这样改”的演算。
PROPOSALS = {
    "13_alt": {
        "base": 13,
        "note": "第13题建议改法：让只知一个会议无法锁定D（当前只知瓦窑堡或洛川任一项即可锁定）",
        "answer": "D",
        "options": {"A": "遵义会议、洛川会议、瓦窑堡会议", "B": "古田会议、洛川会议、瓦窑堡会议",
                    "C": "遵义会议、瓦窑堡会议、洛川会议", "D": "古田会议、瓦窑堡会议、洛川会议"},
        "names": ["确立思想建党、政治建军原则", "制定抗日民族统一战线的策略方针", "明确实行全面抗战路线"],
        "lexical": {},
    },
    "12_alt": {
        "base": 12,
        "note": "第12题建议改法：题项“梅州客家话”改为“梅县话”，选项不变；C不再能凭字面排除",
        "answer": "B",
        "options": None,  # 沿用当前选项
        "names": ["广州话", "梅县话", "潮州话", "雷州话"],
        "lexical": {},
    },
}


def split_option(text):
    t = text.replace("《", "").replace("》", "、").strip("、")
    return [x.strip() for x in t.split("、") if x.strip()]


def main():
    sel = {q["number"]: q for q in json.loads(SEL.read_text(encoding="utf-8"))}
    out = {}
    cases = [(n, names, sel[n]["options"], sel[n]["answer"], LEXICAL_CUES.get(n, {}))
             for n, names in ITEMS.items()]
    for tag, p in PROPOSALS.items():
        opts_src = p["options"] or sel[p["base"]]["options"]
        cases.append((tag, p["names"], opts_src, p["answer"], p["lexical"]))
    for n, names, raw_opts, key, cues in cases:
        if isinstance(n, str):
            print(f"\n##### 建议改法演算 {n}：{PROPOSALS[n]['note']}")
        opts = {k: split_option(v) for k, v in raw_opts.items()}
        truth = opts[key]
        k = len(names)
        assert all(len(v) == k for v in opts.values()), (n, opts)
        print(f"\n=== 第{n}题  编辑答案 {key}：{'、'.join(truth)}")
        for letter, labels in opts.items():
            print(f"  {letter}: {' / '.join(labels)}")
        single = {}
        for i in range(k):
            elim = [L for L, lab in opts.items() if lab[i] != truth[i]]
            remain = [L for L in opts if L not in elim]
            single[names[i]] = {"eliminates": elim, "remaining": remain}
            print(f"  只知第{i+1}项（{names[i]}={truth[i]}）→ 剩余 {remain}")
        min_known = None
        unique_sets = []
        for r in range(1, k + 1):
            for S in itertools.combinations(range(k), r):
                remain = [L for L, lab in opts.items() if all(lab[i] == truth[i] for i in S)]
                if remain == [key]:
                    unique_sets.append([i + 1 for i in S])
                    if min_known is None:
                        min_known = r
        print(f"  锁定唯一答案至少需知道 {min_known} 项；可锁定的最小组合："
              f"{[s for s in unique_sets if len(s) == min_known]}")
        lexical = []
        for i, cue in cues.items():
            for L, lab in opts.items():
                if lab[i] != cue:
                    lexical.append({"option": L, "item": names[i], "assigned": lab[i], "cue": cue})
                    print(f"  字面即可排除：{L} 把“{names[i]}”归为“{lab[i]}”")
        # 各标签在每一位置出现次数，看干扰项是否只是“堆同一个词”
        pos_counts = []
        for i in range(k):
            c = {}
            for lab in opts.values():
                c[lab[i]] = c.get(lab[i], 0) + 1
            pos_counts.append(c)
        print(f"  各位置标签出现次数：{pos_counts}")
        out[n] = {"answer": key, "options": opts, "single_item": single,
                  "min_items_to_identify": min_known,
                  "minimal_identifying_sets": [s for s in unique_sets if len(s) == min_known],
                  "lexical_giveaways": lexical, "label_counts_by_position": pos_counts}
    (HERE / "option_discrimination.out.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n已写出", HERE / "option_discrimination.out.json")


if __name__ == "__main__":
    main()

"""政常新题的裁定记录 → 采用.json（build_data.py 读它决定哪些题上网页、改了什么）。

用法：python3 广东行测18套模拟/备考资料/马哲辨析/非马哲/核对/裁定.py
- 已有盲做结果、且答案与出题人一致的题，默认“采用”；不一致的必须在 DECISIONS 里裁定，否则报错。
- DECISIONS 每条：status（采用/待审/删除）、why（裁定理由，给人看）、patch（要改的字段）。
  patch 里 "options" 写成 {序号: {"text"/"why"/"correct": 新值}}，只改列出的项；其余字段整段替换；
  "source_ids+" 表示在原 source_ids 后追加。
- K 知识块（K-…）也可以在这里改或删：patch 直接替换字段。
"""
import copy
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
NEW = HERE.parent / "新题"

DECISIONS = {
    # ---------- F1（P3、P1），核对人C3 ----------
    "F-P3-07-1": {"why": "条件栏不写内部知识编号；增强党性为根本性任务有Codex原文证据。", "patch": {
        "condition": "依据《中国共产党章程》（2022年修改）、二十届五中全会公报及2026年10月29日通过的《中共中央关于持之以恒推进全面从严治党若干重大问题的决定》；“宪法具有最高法律效力”依据《中华人民共和国立法法》（2023年修正）。",
        "source_ids+": ["E-PT-05"]}},
    "F-P3-08-1": {"why": "唯一错项带“不区分……都”，凭绝对词可排除；改成只看损失大小这一条件替换。", "patch": {
        "options": {1: {"text": "认定工作探索中的失误是否属于违纪违法，主要看造成的损失大小",
                        "why": "错因：把依据事实、性质、情节和规则综合判断，换成了只看损失大小（被替换的是：条件）。损失是事实的一部分，但是否违纪违法还要看性质、情节和是否违反明确的纪律法律规定。"}}}},
    "F-P1-09-1": {"why": "条件栏不写内部知识编号，写出处。", "patch": {
        "condition": "“前三组概括主要内容”“六个必须坚持体现贯穿其中的立场观点方法”依据党的二十大报告（2022年）；“十四个坚持”构成新时代坚持和发展中国特色社会主义的基本方略，依据党的十九大报告（2017年）。"}},
    "F-P1-10-1": {"why": "照报告原文“既有……更有……”。", "patch": {
        "options": {3: {"text": "中国式现代化既有各国现代化的共同特征，更有基于自己国情的中国特色"}}}},
    # ---------- F2（P2、P4），核对人C3 ----------
    "F-P2-15-1": {"why": "对企业用水的规范说法是超定额累进加价，阶梯水价一般指居民用水。", "patch": {
        "lead": "某缺水城市先测算本地水资源承载能力，据此确定新增工业项目的规模；政府核定企业用水定额，同时开展水权交易、实行超定额累进加价，引导企业节水。",
        "options": {0: {"text": "按承载能力确定项目规模体现以水定产；定额管理与水权交易、累进加价并用，体现政府和市场两手发力"},
                    1: {"text": "按承载能力确定项目规模体现以水定产；定额管理与水权交易、累进加价并用，体现地表水和地下水两手发力"},
                    2: {"text": "水权交易和超定额累进加价运用市场和价格机制，与“节水优先”的治水思路相互冲突"}}}},
    "F-P4-02-1": {"why": "原选项的前后半句可拼出答案（取交集就能猜中），改写两个错项的对应半句。", "patch": {
        "options": {0: {"text": "前者是党的第二十四次全国代表大会，后者仍处在第十四届全国人大的任期之内"},
                    1: {"text": "前者属于党的第二十届中央委员会，后者表明第十四届全国人大任期已满、换届为第十五届"}}}},
    "F-P4-07-1": {"why": "“另一院”在题干里没有交代，改成直接的说法；四项全对保留。", "patch": {
        "options": {3: {"text": "省政协是统一战线组织和专门协商机构，其协商建言不属于立法表决"}}}},
    # ---------- F6（广东），核对人C4 ----------
    "F-GD-004-1": {"why": "广东报告里新兴产业与未来产业同在一个小节，“段”容易混；改说“列举”。", "patch": {
        "options": {0: {"text": "依据2026年广东省政府工作报告：生物制造列在未来产业的列举中",
                        "why": "错因：把国家文件的列法套到了广东报告上（文件替换）。2026年广东省政府工作报告把生物制造列在新兴产业的列举中；该报告的新兴产业与未来产业写在同一小节，要看具体列在哪一组。"}}}},
    "F-GD-004-2": {"why": "“新兴产业段”改说“列入新兴产业”，避免和合写的小节标题混。", "patch": {
        "stem": "2026年广东省政府工作报告把生物制造列入新兴产业，与2025年国家十五五《建议》列入未来产业的做法不一致，属于广东报告的归类错误。",
        "fix": "2026年广东省政府工作报告把生物制造列入新兴产业，与2025年国家十五五《建议》列入未来产业的做法不一致，这是两份文件各自的列法，判断归类要按题干指定的文件和年份。"}},
    "F-GD-011-1": {"why": "原题四项全对，练不到平台与主线的错配；把前海、河套的主线对调成错项。", "patch": {
        "options": {1: {"text": "前海重点联系深港科技创新合作，河套重点联系深港现代服务业合作", "correct": False,
                        "why": "错因：把前海、河套的主线对调了（被替换的是：对应关系）。前海抓深港现代服务业合作，河套抓深港科技创新合作；主线用于区分定位，不表示平台只能发展一种产业。"}}}},
    "F-GD-013-2": {"why": "原设问要求同时与民营经济促进法衔接，亮码入企的依据在广东方案，严格读题会漏选；改成结合两份文件判断。", "patch": {
        "stem": "结合广东2026年优化法治化一流营商环境工作方案和《中华人民共和国民营经济促进法》（2025年5月20日起施行），下列做法正确的有（）",
        "explain": "减少重复干扰与依法监管可以同时成立：亮码入企出自广东方案，让检查可监督；合并、联合检查和重点领域全覆盖监管见民营经济促进法第52条；检查不以企业同意为前提。"}},
    "F-GD-020-2": {"why": "导语里“某市已有同领域法规”是自编情境，写明；11月25日的草案说明有Codex证据。", "patch": {
        "condition": "据2026-11-26南方日报对11月25日省十四届人大常委会第二十八次会议的报道（LAW-S16）；截至2026-11-27未取得该条例通过、公布、施行的依据。导语中“省内某市已有同领域法规”为自编情境。本题只考核验法律状态的方法，不断言其后是否通过，也不涉及草案内容。",
        "source_ids+": ["E-YF-03"]}},
}


def apply(q, patch):
    q = copy.deepcopy(q)
    for k, v in patch.items():
        if k == "options":
            for i, ch in v.items():
                q["options"][int(i)].update(ch)
        elif k.endswith("+"):
            base = k[:-1]
            q[base] = (q.get(base) or []) + [x for x in v if x not in (q.get(base) or [])]
        else:
            q[k] = v
    return q


def key_of(q):
    return q["answer"] if q["type"] == "判断" else "".join("ABCDEF"[i] for i, o in enumerate(q["options"]) if o["correct"])


def main():
    items = {}
    for f in sorted(NEW.glob("F*.json")):
        for q in json.loads(f.read_text(encoding="utf-8")):
            items[q["id"]] = q
    kblocks = {}
    for f in sorted(NEW.glob("K_*.json")):
        for r in json.loads(f.read_text(encoding="utf-8")):
            kblocks[r["id"]] = r
    checks = {}
    for f in sorted(HERE.glob("check_*_F*.json")):
        for r in json.loads(f.read_text(encoding="utf-8")):
            checks.setdefault(r["id"], []).append(str(r.get("answer")).strip())
    unknown = set(DECISIONS) - set(items) - set(kblocks)
    assert not unknown, ("裁定里有不存在的编号：", unknown)
    out, pending = {}, []
    for i, q in items.items():
        d = DECISIONS.get(i)
        if i not in checks and not d:
            pending.append(i)          # 还没核对，也没裁定：先不上网页
            continue
        if d is None and any(a != key_of(q) for a in checks[i]):
            raise SystemExit(f"{i}：核对答案{checks[i]}与出题人{key_of(q)}不一致，必须裁定")
        d = d or {}
        status = d.get("status", "采用")
        rec = {"status": status}
        if d.get("why"):
            rec["note"] = d["why"]
        if d.get("patch"):
            new = apply(q, d["patch"])
            rec["override"] = {k: new[k] for k in new if new[k] != q.get(k)}
            if status == "采用" and new["type"] != "判断":
                nc = sum(1 for o in new["options"] if o["correct"])
                assert (nc == 1) if new["type"] == "单选" else (2 <= nc <= 4), (i, nc)
        if status == "待审":
            rec["review"] = d.get("review") or d.get("why") or ""
        out[i] = rec
    for k, d in DECISIONS.items():
        if k in kblocks:
            rec = {"status": d.get("status", "采用"), "note": d.get("why", "")}
            if d.get("patch"):
                new = apply(kblocks[k], d["patch"])
                rec["override"] = {f: new[f] for f in new if new[f] != kblocks[k].get(f)}
            out[k] = rec
    (HERE / "采用.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    from collections import Counter
    print("裁定完成：", dict(Counter(r["status"] for r in out.values())), "改动", sum(1 for r in out.values() if r.get("override")),
          "| 未核对未裁定（暂不上网页）", len(pending), pending[:8])


if __name__ == "__main__":
    main()

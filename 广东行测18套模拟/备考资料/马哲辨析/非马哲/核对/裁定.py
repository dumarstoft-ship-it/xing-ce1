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
    "F-GD-020-2": {"why": "导语里“某市已有同领域法规”是自编情境，写明；11月25日的草案说明有Codex证据；导语补“广东”。", "patch": {
        "lead": "2026年11月下旬，小周看到报道：11月25日召开的广东省十四届人大常委会第二十八次会议，听取了关于省人工智能发展促进条例草案的说明。他又查到，省内某市已有同领域的市级地方性法规。",
        "condition": "据2026-11-26南方日报对11月25日省十四届人大常委会第二十八次会议的报道（LAW-S16）；截至2026-11-27未取得该条例通过、公布、施行的依据。导语中“省内某市已有同领域法规”为自编情境。本题只考核验法律状态的方法，不断言其后是否通过，也不涉及草案内容。",
        "source_ids+": ["E-YF-03"]}},
    # ---------- 题干检查C8的附带意见 ----------
    "F-LAW-001-1": {"why": "导语补月份，法律部门的新口径（2026年法工委文章）对应时点更明确。", "patch": {
        "lead": "某同学2026年11月复习时，把“行政法”“生态环境法”“行政法规”“地方性法规”写在笔记的同一栏里，打算按一个标准排出先后。"}},
    "F-GD-016-1": {"why": "“主办过”是截至某时的状态，设问补时点。", "patch": {
        "stem": "截至2026年11月，中国主办过的亚太经合组织（APEC）领导人非正式会议，按举办时间先后排列，举办城市依次是（）"}},
    "F-LAW-003-1": {"why": "原错项拿法典和全国人大常委会制定的法律比，学界有“基本法律高于非基本法律”的说法，较真时可争；改成和其他基本法律比，错得没有争议。", "patch": {
        "options": {3: {"text": "全国人大通过的法典，效力高于全国人大制定的其他基本法律",
                        "why": "错因：把“法典”当成了独立的效力等级（层级替换）。法典由全国人大制定，属于法律层次，和其他基本法律一样，没有高于它们的独立效力等级；法律之间的冲突按特别规定、新旧规定和立法法规定的裁决程序处理。"}}}},
    "F-LAW-013-1": {"why": "照国家发展规划法第21条原文写“审查和批准”（F9出题人指出）。", "patch": {
        "options": {1: {"text": "国家发展规划确需调整的，由国务院提出方案，报党中央同意后提请全国人大审查和批准",
                        "why": "错因：把全国人大常委会换成了全国人大（主体替换）。国家发展规划公布后未经法定程序不得调整；确需调整的，由国务院提出方案，报党中央同意后，提请全国人大常委会审查和批准（第21条）。"}}}},
    # ---------- F3（党史），核对人C4 ----------
    "F-H05-1": {"why": "错项的错因写准：三大政策是新三民主义的政策内涵，不是“无关”；大会是实际上确立了三大政策。", "patch": {
        "options": {3: {"why": "错因：把三大政策当成了三民主义本身（被替换的是：关系）。新三民主义仍是民族、民权、民生三项主义；联俄、联共、扶助农工是它的政策内涵，国民党一大实际上确立了这三大政策（“三大政策”是后来的概括），毛泽东称之为“联俄、联共、扶助农工三大政策的三民主义”。二者相关，但不是同一份清单。"}}}},
    "F-H15-1": {"why": "解析补上八大两句原文，并说明②在1981年决议中形成规范表述。", "patch": {
        "explain": "1956年八大：“人民对于建立先进的工业国的要求同落后的农业国的现实之间的矛盾”，以及“人民对于经济文化迅速发展的需要同当前经济文化不能满足人民需要的状况之间的矛盾”，主要任务落到发展生产力、实现国家工业化；1981年历史决议：“人民日益增长的物质文化需要同落后的社会生产之间的矛盾”，形成此后沿用的规范表述；2017年十九大：“人民日益增长的美好生活需要和不平衡不充分的发展之间的矛盾”。主要矛盾变化没有改变社会主义初级阶段的基本国情。"}},
    "F-H16-1": {"why": "解析补一处权威评价作依据。", "patch": {
        "explain": "正确。1958年开始的“大跃进”和人民公社化运动出现急于求成、违背经济规律等严重问题，1959—1961年国民经济发生严重困难；1966—1976年“文化大革命”是严重曲折。1981年十一届六中全会通过的历史决议指出，“文化大革命”使党、国家和人民遭到建国以来最严重的挫折和损失，同时充分肯定了建国以来的基本成就。历史评价要把具体错误与这一时期取得的制度、工业等成就分别看待，也不能把困难全推给自然因素。"}},
    "F-H31-1": {"why": "注明材料是自编情境，并给一个真实例子。", "patch": {
        "condition": "按人物主要事迹发生的年代归类，不按纪念作品的创作年代。导语为自编情境；现实中也有这类作品，例如1990年发表的《念奴娇·追思焦裕禄》。"}},
    # ---------- F4、F5（法律），核对人C5 ----------
    "F-LAW-029-2": {"why": "原句后半可读成断言，也可读成“在法律没有规定须先复议的情形下”的限定语，两读答案相反；改成明确的断言。", "patch": {
        "stem": "《中华人民共和国行政复议法》（2023年修订，2024年1月1日起施行）没有规定须先申请行政复议的情形，公民对行政行为不服的，都可以不经复议直接提起行政诉讼。",
        "fix": "《中华人民共和国行政复议法》（2023年修订，2024年1月1日起施行）规定了须先申请行政复议的情形；属于这些情形的，应当先申请行政复议，对复议决定不服的再依法提起行政诉讼，其他情形一般可以选择复议或者直接起诉。"}},
    "F-LAW-018-1": {"why": "两个错项依赖第23条第2款的例外，补进解析，挂Codex原文证据。", "patch": {
        "explain": "分两步：先看应否处罚（不满14周岁不予处罚；14至不满18周岁从轻或者减轻），再看拘留是否执行（第23条四类人通常不执行）。第23条第2款有两类例外：前三类人（已满14不满16周岁、已满16不满18周岁初次违反、70周岁以上）情节严重、影响恶劣的；第一、三类人一年以内二次以上违反治安管理的，都不受不执行拘留的限制。怀孕或者哺乳自己不满1周岁婴儿的不在这两类例外之列。“初次违法”“不执行拘留”都不等于不处罚。",
        "source_ids+": ["E-LAW-07"]}},
    "F-LAW-018-2": {"why": "挂Codex原文证据（第23条原文）。", "patch": {"source_ids+": ["E-LAW-07"]}},
    "F-LAW-016-2": {"why": "三个错项原来靠“即视为未曾发生”“彻底”“只有……才”这类绝对词就能排除；去掉标记，保留原来的错因。", "patch": {
        "options": {0: {"text": "记录封存后，原罚款决定随之撤销"},
                    1: {"text": "封存就是将该记录从公安机关信息系统中删除"},
                    3: {"text": "封存后，有关单位需要查询该记录的，应当先取得李某本人同意"}}}},
    "F-LAW-021-2": {"why": "错项原来自带“与案件无关”“明显超过”“以……为名”等违法标记，不用法律知识也能排除；改成要靠知识判断的说法。", "patch": {
        "options": {0: {"text": "为防止转移，对企业负责人亲属名下的房产不加区分一并查封",
                        "why": "错因：没有区分涉案人与案外人财产（被替换的是措施对象）。该法要求区分涉案人财产与案外人财产、涉案财物与合法财产，案外人的财产不能因为与当事人有亲属关系就一并查封。"},
                    1: {"text": "为确保追缴到位，冻结数额可以适当高于涉案金额",
                        "why": "错因：突破了数额边界（被替换的是措施范围）。查封、扣押、冻结不得超权限、超范围、超数额、超时限。"},
                    3: {"text": "对两家企业之间的合同欠款纠纷，立案冻结欠款方账户以促成还款",
                        "why": "错因：把经济纠纷当成了经济犯罪处理（被替换的是案件性质）。该法要求办案区分经济纠纷与经济犯罪，不能用刑事立案和冻结措施替企业催收欠款。"}}}},
    "F-LAW-017-1": {"why": "“轻伤”在法律上是故意伤害罪的入罪门槛用语，改为“轻微伤”。", "patch": {
        "lead": "2026年2月，乙在夜市醉酒滋事，无故对甲拳打脚踢，殴打仍在持续。甲为摆脱殴打，用力将乙推开，乙摔倒后手臂擦伤，甲也受了轻微伤。经查，甲推开乙是为了制止乙正在进行的殴打，没有明显超过必要限度。"}},
    "F-LAW-023-1": {"why": "原题四项全对、没有干扰项；把第一项改成“通过日当施行日”的错项，答案变为三项。", "patch": {
        "options": {0: {"text": "该法于2025年9月12日通过，自通过之日起施行", "correct": False,
                        "why": "错因：把施行日期换成了通过日期（被替换的是：阶段）。该法2025年9月12日通过，自2025年11月1日起施行。"}}}},
    "F-LAW-030-1": {"why": "“正提请审议”带现在时，超出报道能证明的范围；改为“已提请本次会议审议”。", "patch": {
        "options": {2: {"text": "两部条例草案已提请本次会议审议，是否通过、何时施行须另查正式文本"}},
        "source_ids+": ["E-YF-03"]}},
}


# 证据比对里不采用的条目（编号：理由）
EA_SKIP = {}


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
    # 证据比对（Codex原文证据 vs 第一批题）：解析、条件、条次补充，叠加在 DECISIONS 之后；EA_SKIP 里的不采用
    import re
    ev_fix = {}
    ea_f = HERE / "证据比对.json"
    for r in (json.loads(ea_f.read_text(encoding="utf-8")) if ea_f.exists() else []):
        if r["id"] in EA_SKIP:
            continue
        pt = {}
        for k, v in r["fix"].items():
            m = re.match(r"options\[(\d+)\]\.(text|why)$", k)
            if m:
                pt.setdefault("options", {}).setdefault(int(m[1]), {})[m[2]] = v
            else:
                assert k in ("stem", "lead", "condition", "explain", "fix"), (r["id"], k)
                pt[k] = v
        if r.get("evidence"):
            pt["source_ids+"] = r["evidence"]
        ev_fix[r["id"]] = (pt, r["verdict"])
    # 题干自足检查（网页作答后才显示条件栏）：检查人给出的导语、设问补限定，叠加在 DECISIONS 之后
    stem_fix = {}
    for f in sorted(HERE.glob("题干补限定_*.json")):
        for r in json.loads(f.read_text(encoding="utf-8")):
            assert set(r["patch"]) <= {"lead", "stem", "fix"}, (f.name, r["id"])
            stem_fix[r["id"]] = r
    checks = {}
    for f in sorted(HERE.glob("check_*_F*.json")):
        for r in json.loads(f.read_text(encoding="utf-8")):
            checks.setdefault(r["id"], []).append(str(r.get("answer")).strip())
    unknown = (set(DECISIONS) | set(stem_fix) | set(ev_fix)) - set(items) - set(kblocks)
    assert not unknown, ("裁定里有不存在的编号：", unknown)
    out, pending = {}, []
    for i, q in items.items():
        d = DECISIONS.get(i)
        if i not in checks and not d:
            pending.append(i)          # 还没核对，也没裁定：先不上网页
            continue
        if d is None and any(a != key_of(q) for a in checks[i]):
            raise SystemExit(f"{i}：核对答案{checks[i]}与出题人{key_of(q)}不一致，必须裁定")
        d = dict(d or {})
        if i in ev_fix:
            pt, verdict = ev_fix[i]
            merged = dict(d.get("patch") or {})
            for k, v in pt.items():
                if k == "options":
                    opts = {int(x): dict(y) for x, y in (merged.get("options") or {}).items()}
                    for oi, ch in v.items():
                        opts.setdefault(oi, {}).update(ch)
                    merged["options"] = opts
                elif k == "source_ids+":
                    merged[k] = (merged.get(k) or []) + [x for x in v if x not in (merged.get(k) or [])]
                else:
                    merged[k] = v
            d["patch"] = merged
            d["why"] = "；".join(x for x in (d.get("why"), f"证据比对（{verdict}）") if x)
        if i in stem_fix:
            d["patch"] = {**(d.get("patch") or {}), **stem_fix[i]["patch"]}
            d["why"] = "；".join(x for x in (d.get("why"), "题干补限定：" + stem_fix[i]["problem"]) if x)
        status = d.get("status", "采用")
        rec = {"status": status}
        if d.get("why"):
            rec["note"] = d["why"]
        if d.get("patch"):
            # 错题重练时，错误判断题会用 fix 当题干：改了题干限定就要同步改 fix
            if q["type"] == "判断" and q["answer"] == "错误" and "stem" in d["patch"] and "fix" not in d["patch"]:
                print(f"提醒：{i} 改了题干但没改 fix（重练时 fix 会当题干显示），请核对")
            new = apply(q, d["patch"])
            rec["override"] = {k: new[k] for k in new if new[k] != q.get(k)}
            if status == "采用" and new["type"] != "判断":
                nc = sum(1 for o in new["options"] if o["correct"])
                assert (nc == 1) if new["type"] == "单选" else (2 <= nc <= 4), (i, nc)
        if status == "待审":
            rec["review"] = d.get("review") or d.get("why") or ""
        out[i] = rec
    # K 知识块：核对人审过（K核对_*.json 里有记录、且不是“删除”）或 DECISIONS 里列了的才采用
    k_checked = {}
    for f in sorted(HERE.glob("K核对_*.json")):
        for r in json.loads(f.read_text(encoding="utf-8")):
            k_checked[r["id"]] = r
    for k in kblocks:
        if k in k_checked and k not in DECISIONS:
            v = k_checked[k].get("verdict", "")
            out[k] = {"status": "删除" if v == "删除" else "采用", "note": "K块核对：" + v}
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

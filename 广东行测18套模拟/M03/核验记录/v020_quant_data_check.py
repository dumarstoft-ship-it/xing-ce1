#!/usr/bin/env python3
"""独立核验 v0.2.0 数量/资料补丁涉及的事实与材料保全守卫。

仅以内存方式把补丁应用到已归档的0.1.0；不写selection、旧数值报告或题源。
未涉及的旧题不在本轮重算范围。第35题像素核验由v020_q35_redraw.py记录。
"""

import ast
import copy
import datetime
import hashlib
import itertools
import json
import math
from pathlib import Path
import re
from fractions import Fraction as F

from PIL import Image


HERE = Path(__file__).resolve().parent
M03 = HERE.parent
ROOT = M03.parents[1]
BASE = M03 / "历史版本/0.1.0/selection.json"
PATCH = M03 / "修订底稿/v020_quant_data_patch.json"


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def serial(value):
    if isinstance(value, F):
        return {"exact": str(value), "decimal": float(value)}
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(v) for v in value]
    return value


def run_guard(rows):
    """只执行现有数值脚本新尾段的真实函数，避免另写一套宽松判断。"""
    script = M03 / "编辑底稿/quant_data_check.py"
    tree = ast.parse(script.read_text())
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
              and n.name == "verify_material_preservation")
    env = {"json": json, "re": re, "ROWS": rows,
           "mat": lambda n: rows[n].get("materials", [rows[n]["source_question"]["material"]])[0]}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), str(script), "exec"), env)
    return env["verify_material_preservation"]()


def main():
    before = {q["number"]: q for q in json.loads(BASE.read_text())}
    patch = json.loads(PATCH.read_text())
    after = copy.deepcopy(before)
    numbers = [p["number"] for p in patch]
    assert numbers == [33, 35, 37, 38, 40, 42, 43, 81, 82, 83, 84, 85, 86, 88]
    allowed = {"analysis", "stem_override", "materials", "source_notice"}
    for p in patch:
        assert set(p) == {"number", "updates", "added_edits", "reason"}
        assert set(p["updates"]) <= allowed
        assert p["reason"] and p["added_edits"]
        after[p["number"]].update(copy.deepcopy(p["updates"]))
        after[p["number"]]["edits"].extend(copy.deepcopy(p["added_edits"]))
    for n in before:
        for key in ["source_question", "source_id", "source_answer", "answer"]:
            assert before[n].get(key) == after[n].get(key), (n, key)
        assert before[n].get("options_override") == after[n].get("options_override"), n
    source = ROOT / before[31]["source_file"]
    bank = {q["id"]: q for q in map(json.loads, source.read_text().splitlines())}
    selected = list(range(31, 46)) + list(range(71, 91))
    assert all(after[n]["source_question"] == bank[after[n]["source_id"]] for n in selected)

    report = {"scope": "0.1.0归档加v020补丁的内存稿；本轮有价值修订的定向复核，不冒称全卷或原PDF复核。",
              "base_file": str(BASE.relative_to(ROOT)), "base_sha256": hashlib.sha256(BASE.read_bytes()).hexdigest(),
              "patch_file": str(PATCH.relative_to(ROOT)), "patch_sha256": hashlib.sha256(PATCH.read_bytes()).hexdigest(),
              "patched_numbers": numbers, "checks": {}}
    checks = report["checks"]

    series = [F(3), F(7, 3), F(5, 3), F(1), F(43, 81)]
    assert all(series[i + 1] - series[i] == -F(2, 3) for i in range(3))
    assert series[3] - F(2, 3) != series[4]
    numerators = [x * 3 ** i for i, x in enumerate(series)]
    assert numerators == [3, 7, 15, 27, 43]
    assert [numerators[i+1] - numerators[i] for i in range(4)] == [4, 8, 12, 16]
    checks[33] = {"arithmetic_false_fifth": F(1, 3), "actual_fifth": series[-1],
                  "numerators": numerators, "next": F(63, 243), "answer": "D"}

    figure = after[35]["stem_override"][1]
    assert figure == {"type": "figure", "path": "广东行测18套模拟/M03/assets/q35_number_grid_v020.png",
                      "path_base": "repository", "width_px": 2160, "height_px": 540}
    with Image.open(ROOT / figure["path"]) as im:
        assert im.size == (2160, 540)
    grid = before[35]["source_question"]["stem"][0]["rows"]
    for row in grid[:3]:
        a, b, c, d = [int(x.replace("−", "-")) for x in row[1:]]
        assert b * c - a == d
    assert 8 * 7 - 22 == 34
    layout = json.loads((HERE / "v020_q35_layout_check.json").read_text())
    assert layout["source_values_TL_TR_BL_BR"] == [r[1:] for r in grid]
    assert layout["status"] == "PASS"
    checks[35] = {"source_grid_preserved": True, "answer": "B",
                  "layout_report": "核验记录/v020_q35_layout_check.json",
                  "manual_view": "本轮实际打开新2160×540 PNG及120毫米、300dpi缩放预览；负号与直径分离。"}

    populations = []
    for population in range(100, 700):
        a, b, c = population // 100, population // 10 % 10, population % 10
        if population - (100*b + 10*a + c) == 270 and population - (100*c + 10*b + a) == 594:
            populations.append(population)
    assert populations == [630]
    buses = [(x, y) for x in range(14) for y in range(17) if 50*x + 40*y == 630]
    assert min(x for x, y in buses) == 3
    checks[37] = {"populations": populations, "swapped_hundreds_ones": "036 = 36",
                  "bus_solutions": buses, "answer": "C"}

    assert "本月进价保持不变" in after[38]["stem_override"][0]["text"]
    price = F(30) / F(1, 5)
    profit_old, profit_new = price - 120, price * F(6, 5) - 120
    sales_ratio = F(4, 5) * profit_old / profit_new
    revenue_ratio = sales_ratio * F(6, 5)
    assert price == 150 and revenue_ratio == F(12, 25)
    checks[38] = {"original_price": price, "profit_old_new": [profit_old, profit_new],
                  "sales_ratio": sales_ratio, "revenue_ratio": revenue_ratio,
                  "decrease": 1 - revenue_ratio, "answer": "D"}

    exposed = {key: 1 - ((F(7) - drop) / 7) ** 3 for key, drop in
               zip("ABCD", map(F, ["1.54", "1.75", "2.10", "3.00"]))}
    assert exposed["A"] < F(37, 64) == exposed["B"] < exposed["C"] < exposed["D"]
    checks[40] = {"exposed_fractions_by_option": exposed, "threshold": F(37, 64),
                  "minimum_drop": F(7, 4), "answer": "B"}

    common = (datetime.date(2023, 3, 30) - datetime.date(2023, 1, 1)).days + 1
    leap = (datetime.date(2024, 3, 30) - datetime.date(2024, 1, 1)).days + 1
    phase = lambda day, period: (day - 1) % period + 1
    assert [phase(common, 12), phase(leap, 12)] == [5, 6]
    cases = {"correct": (leap - 1, phase(leap - 1, 9)),
             "forget_Jan2": (leap, phase(leap, 9)),
             "wrong_common_year": (common - 1, phase(common - 1, 9)),
             "both_errors": (common, phase(common, 9))}
    assert [x[1] for x in cases.values()] == [8, 9, 7, 8]
    checks[42] = {"calendar_ordinals_common_leap": [common, leap], "chen_day_and_cycle_phase": cases,
                  "corresponding_choices": ["B", "A", "D", "B"], "answer": "B"}

    probability = F(0)
    mass = F(0)
    weights = [F(4, 5), F(2, 25), F(3, 25)]  # 首次合格、首次不合格而潜在补考合格/不合格。
    for outcome in itertools.product(range(3), repeat=4):
        weight = math.prod(weights[x] for x in outcome)
        mass += weight
        first = outcome.count(0)
        final = first + outcome.count(1) if first >= 2 else first
        if final == 3:
            probability += weight
    three_first = F(4) * F(4, 5)**3 * F(1, 5) * F(3, 5)
    two_first = F(6) * F(4, 5)**2 * F(1, 5)**2 * 2 * F(2, 5) * F(3, 5)
    assert mass == 1 and probability == three_first + two_first == F(4992, 15625)
    checks[43] = {"enumerated_potential_outcomes": 81, "total_mass": mass,
                  "three_first": three_first, "two_first": two_first, "correct": probability,
                  "mistaken_cancel_exactly_two": three_first,
                  "omit_C_2_1": three_first + two_first / 2, "answer": "D"}

    original_material = before[81]["materials"][0]
    material = after[81]["materials"][0]
    removed = "据中国海关总署统计数据显示，2023年7月，中国空调产量同比增长29.0%。"
    ac = {r[0]: [F(r[1]), F(r[2])] for r in material["blocks"][0]["rows"]}
    a, b = ac["2023年7月"][0], ac["2023年6月"][0]
    u, v = ac["2023年7月"][1], ac["2023年6月"][1]
    july = (a-b)/(a/(1+u/100)-b/(1+v/100))-1
    sensitivity = [(a7-a6)/(a7/(1+r7/100)-a6/(1+r6/100))-1 for a7,a6,r7,r6 in
                   itertools.product([a-F(1,2),a+F(1,2)], [b-F(1,2),b+F(1,2)],
                                     [u-F(1,20),u+F(1,20)], [v-F(1,20),v+F(1,20)])]
    assert max(sensitivity) < F("0.2895")
    assert all(after[n]["materials"] == after[81]["materials"] for n in range(81,86))
    assert material["blocks"][0]["rows"] == original_material["blocks"][0]["rows"]
    assert material["blocks"][1]["text"] == original_material["blocks"][1]["text"].removeprefix(removed)
    monthly = {month: ac[f"2022年{month}月"][0]-ac[f"2022年{month-1}月"][0] for month in [9,10,11,12]}
    increments = [monthly[m]-monthly[m-1] for m in [10,11,12]]
    assert increments == [-302,21,309]
    base_june_cum = ac["2023年6月"][0] / (1+ac["2023年6月"][1]/100)
    base_may_cum = ac["2023年5月"][0] / (1+ac["2023年5月"][1]/100)
    unaffected = {81: ac["2022年12月"][0]-base_june_cum,
                  82: monthly[10]/monthly[9]-1,
                  83: (ac["2023年6月"][0]-ac["2023年5月"][0])/(base_june_cum-base_may_cum)-1,
                  84: F(".846")/F("1.013")-1, 85: increments}
    checks["81-85"] = {"removed_sentence": removed, "new_header": material["blocks"][0]["headers"][0],
                       "july_monthly_growth_from_table": july,
                       "rounding_bound_assumption": "累计量各±0.5万台、累计增速各±0.05个百分点，独立取16个端点组合；作为保守外包络。",
                       "rounding_growth_bounds": [min(sensitivity),max(sensitivity)],
                       "29_percent_rounded_interval": [F(".2895"),F(".2905")],
                       "question_dependency_note": {81:"2022全年及2023上半年累计量/增速",82:"2022年8—10月累计量",83:"2023年5—6月累计量/增速",84:"7月出口金额/数量同比",85:"2022年8—12月累计量"},
                       "unaffected_question_results": unaffected,
                       "source_material_snapshot_sha256": digest(before[81]["source_question"]["material"]),
                       "display_material_before_sha256": digest(original_material),
                       "display_material_after_sha256": digest(material),
                       "C_wrong_metric_cumulative_growth_percent": [F("3.2"),F("2.0"),F("1.8")],
                       "manual_graph_review": "本轮实际打开85题A—D：A递增、B先降后升、C递减、D先升后降。"}

    prod, cons = before[86]["materials"][0]["blocks"]
    production = {int(r[0]): list(map(F,r[1:])) for r in prod["rows"]}
    consumption = {int(r[0]): list(map(F,r[1:])) for r in cons["rows"]}
    assert production[2022][-1] == 92872 and sum(production[2022][1:]) == production[2022][0]
    growth = {y: production[y][-1]/production[y-1][-1]-1 for y in range(2019,2023)}
    assert min(growth,key=growth.get) == 2022
    checks[86] = {"retained_2022_other_production": production[2022][-1], "growth_by_year": growth,
                  "table_row_sum_preserved": True, "answer": "D",
                  "source_boundary": "转写表可核；本轮未取得粉笔原PDF逐格核对，未据构成规律改成95064。"}
    proportions = lambda row: [x/row[0] for x in row[1:]]
    checks[88] = {"correct_2022_consumption": proportions(consumption[2022]),
                  "A_approximate_match_2022_production": proportions(production[2022]),
                  "C_approximate_match_2018_production": proportions(production[2018]),
                  "manual_graph_review": "本轮实际打开88题A—D；B灰色略过半、白色不到一成、格纹与黑色接近；A/C约七成灰色；D白色明显偏大。近似对应不是图像精确角度测量。",
                  "answer": "B"}

    scoped = {n: after[n] for n in selected}
    report["material_guard_positive"] = run_guard(scoped)
    def change_cell(rows):
        for n in range(81,86): rows[n]["materials"][0]["blocks"][0]["rows"][0][1] = "15723"
    def delete_extra_text(rows):
        for n in range(81,86): rows[n]["materials"][0]["blocks"][1]["text"] = ""
    def alter_metadata(rows):
        for n in range(81,86): rows[n]["materials"][0]["source_pages"] = []
    def wrong_header(rows):
        for n in range(81,86): rows[n]["materials"][0]["blocks"][0]["headers"][0] = "月份"
    def omit_edit_record(rows):
        rows[81]["edits"] = [e for e in rows[81]["edits"] if e["type"] != "material_sentence_removal"]
    def split_shared_group(rows):
        rows[85]["materials"][0]["blocks"][0]["notes"] = ""
    mutations = {"numeric_cell_changed":change_cell,"extra_text_deleted":delete_extra_text,
                 "source_metadata_changed":alter_metadata,"unregistered_header":wrong_header,
                 "missing_edit_record":omit_edit_record,"shared_group_differs":split_shared_group}
    rejected = {}
    for name, mutate in mutations.items():
        candidate = copy.deepcopy(scoped)
        mutate(candidate)
        try:
            run_guard(candidate)
        except AssertionError as exc:
            rejected[name] = {"rejected":True,"reason":str(exc)}
        else:
            raise AssertionError(f"material guard accepted {name}")
    report["material_guard_negative_cases"] = rejected
    current = {q["number"]: q for q in json.loads((M03/"selection.json").read_text())}
    report["current_canonical_has_all_patch_updates"] = all(
        all(current[p["number"]].get(k) == v for k,v in p["updates"].items()) for p in patch)
    report["summary"] = {"patch_items":len(patch),"source_objects_checked_unchanged":35,
                         "all_90_answer_keys_unchanged":True,"shared_material_rows":5,
                         "material_guard_negative_cases_rejected":len(rejected),"status":"PASS"}
    (HERE/"v020_quant_data_check.json").write_text(json.dumps(serial(report),ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(report["summary"],ensure_ascii=False))


if __name__ == "__main__":
    main()

# M04 Claude审核证据

结论与理由见[审核意见](../../Claude审核意见.md)；逐题结论见 [claude_review.json](claude_review.json)。本目录只新增文件，不改动GPT的内部记录。

## 盲解原文件

`blind/` 下是七个模块各自在打开答案前写入的原文件，未作改动：

- `pol.json`：1—15题
- `verbal.json`：16—30题。第16、17、20、25、26题对原题有模糊印象，第18题认出原文出处，文件中已注明
- `quant.json`：31—45题
- `fig.json`：46—50题，分别按重绘图和原图作答
- `logic.json`：51—65题
- `sci.json`：66—70题
- `data.json`：71—90题

## 复核脚本

只读仓库，缺省仓库根目录为 `/home/user/xing-ce1`。在各自目录下运行：

```bash
python3 -B <脚本名>
```

各脚本的运行输出与脚本放在一起。

| 目录 | 脚本 | 内容 |
| --- | --- | --- |
| politics | audit_lecture_pages.py | 逐页核对讲义所引页是否支持题面（第12题页码问题） |
| politics | checks_q10_q13_q15.py | 第10、13、15题枚举核验 |
| verbal | diff_stems.py | 16—30题题面与源题逐字比对（保留标点） |
| quant | blind_check.py、distractor_and_edge_check.py | 31—45题精确复算、干扰项对应错法、第41题构造能否以分计价 |
| quant | alt_rules_search.py | 数字推理替代规律搜索 |
| fig | verify_q46.py、verify_q47.py | 重绘图与原图逐格采样比对，规律验证 |
| fig | q48_symbols.py、q48_patterns.py | 第48题图符分割、像素相关与三种口径下的结构（答案应为B） |
| fig | gd2023_string_convention.py | 用广东2023年两道字符串真题校准口径 |
| fig | verify_q49.py | 第49题折叠与24种旋转穷举 |
| fig | linework_compare.py | 重绘图与原图的线宽、灰度对比 |
| logic | verify_q56.py、verify_q60.py、verify_q63.py | 穷举唯一性 |
| logic | verify_q57_denominator.py | 第57题三种投诉率口径下各选项能否解释 |
| logic | compare_stems.py | 题面与源题字符级及分段比对（第61题选项丢失换行） |
| sci | check_q66_friction.py、check_q67_circuit.py | 摩擦复算；电路理想与非理想电表两种情形 |
| sci | figure_compare.py | 第66、67题重绘图与原图叠图比对 |
| data | blind_calc.py、rounding_robustness.py | 71—90题精确复算与舍入稳健性 |
| data | q90_figs.py | 第90题选项图像素点位与计算值拟合 |
| data | material_compare.py | 材料与源对象逐字逐格比对 |

**图片**：

- `fig/q48_symbol_twins.png`：第48题题干、B、C三行的图符对照。
- `sci/overlay_q66.png`、`sci/overlay_q67.png`：重绘图与原图叠图。

**未收入的**：第50题建模脚本依赖较多裁剪图，未收入，结论见审核意见。

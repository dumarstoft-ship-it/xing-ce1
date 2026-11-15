# M03 Claude审核证据

结论与理由见[审核意见](../../Claude审核意见.md)；逐题结论见 [claude_review.json](claude_review.json)。

## 盲解答案

`blind/` 下是七个模块各自在打开答案前写入的原文件，未作改动：

- `pol.json`：1—15题，判断题以A表示正确、B表示错误
- `verbal.json`：16—30题。第18、21、24题盲解时对机构答案有模糊记忆：第21、24题已在本文件中注明，第18题补记在 `verbal/review_comparison.json`
- `quant.json`：31—45题
- `fig.json`：46—50题
- `logic.json`：51—65题
- `sci.json`：66—70题
- `data.json`：71—90题

## 复核脚本

只用Python标准库，以及 Pillow、numpy。都只读仓库，缺省仓库根目录为 `/home/user/xing-ce1`，多数脚本可用第一个参数另指。在各自目录下运行：

```bash
python3 -B <脚本名>
```

| 目录 | 脚本 | 内容 |
| --- | --- | --- |
| politics | option_discrimination.py | 第6、12、13、15题选项区分度：知道哪几项即可锁定答案；第12、13题改法演算 |
| politics | provenance_page_check.py | 关键表述是否出现在讲义所引页 |
| verbal | diff_stems.py | 16—30题 stem_override 与源题逐字比对 |
| quant | verify_q31_45.py | 31—45题：数字推理替代规律搜索，计算题精确分数或穷举，逐选项判定 |
| quant | q35_legibility.py、q35_fix_prototype.py | 第35题16格字形到直径、圆周的间距；重绘参数搜索 |
| quant | source_fidelity_check.py | 源对象与源库逐字段一致 |
| fig | q46_symmetry.py | 第46题5种对称判定（颜色须对应） |
| fig | q47_rule_check.py | 第47题28种环面平移搜索与选项差异；读 q47_grids.json（蜂窝逐格转录） |
| fig | q49_views.py、q49_rule_check.py | 第49题视图关系穷举与干扰项构造；读 q49_fit_results.json（12幅立体重建） |
| fig | q50_enumerate.py | 第50题拼合穷举（24种旋转、遮挡格全部取法）；读 q50_hidden.json、q50_readings.json |
| logic | verify_logic_51_65.py | 51、53、55、60、61、63、64题穷举与形式化（形式化写在注释里） |
| logic | diff_stems_51_65.py | 源换行逐个分类（句末分隔或句中折行），检查是否保留 |
| logic | check_print_blank_q55.py | 第55题空格占位在旧排版规则下印不出横线 |
| sci | q69_foodchains.py | 第69题四套边集比对，枚举食物链 |
| sci | q66_68_checks.py | 第66题浮力参数扫描，第67题落点扫描，第68题原子守恒 |
| sci | print_sizes.py | 第66—70题图中最小文字、线条在各印宽下的毫米数 |
| data | blind_calc_71_90.py | 71—90题只读考生题面的精确复算与选项距离 |
| data | sensitivity_and_provenance.py | 舍入敏感性；能源表“总量×构成比”取数规律 |
| data | q88_pie_measure.py | 第88题饼图扇区逐像素实测 |
| data | source_diff_71_90.py | 资料题面与源逐格比对 |

各脚本的运行输出（`.out.txt`、`_output.txt`、`.json`）与脚本放在一起。

`sci/q70_annotated_x3.png` 是第70题读图标注图，标出高程、山脊与山谷、河道上的三个交点及真北方向。`quant/q35_print_preview_c3.png` 是第35题第3圆的打印预览，可见负号与直径粘连。

图推第47、49、50题的转录与重建脚本依赖较多图像处理代码，未收入仓库，只保留它们输出的转录数据。

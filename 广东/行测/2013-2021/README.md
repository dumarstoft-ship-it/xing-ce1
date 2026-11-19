# 广东行测整卷结构化题库（2013—2021）

2 套试卷，共 200 题。按卷保留原题号，收录题干、选项、答案，不收录解析。字段与 [2022—2026 题库](../2022-2026/README.md) 相同，`year` 为 2013—2021。

| 试卷 | 题数 | 明确答案 | 争议答案 | 答案缺失 | 文件 |
| --- | ---: | ---: | ---: | ---: | --- |
| 2020年广东行测（乡镇卷） | 100 | 100 | 0 | 0 | [阅读](GD2020-XZ.md) · [JSONL](GD2020-XZ.jsonl) · [质量报告](quality/GD2020-XZ.md) |
| 2021年广东行测（乡镇卷） | 100 | 100 | 0 | 0 | [阅读](GD2021-XZ.md) · [JSONL](GD2021-XZ.jsonl) · [质量报告](quality/GD2021-XZ.md) |

## 给 AI 的入口

- [all.jsonl](all.jsonl)：每行一道题，UTF-8；可直接逐行解析、分块或建立检索索引。
- 每卷的 Markdown：供阅读，保留图片与图表文字数据。
- [schema.json](schema.json)：字段类型；[assets-manifest.json](assets-manifest.json)：图片来源页、裁剪坐标（pt）、像素尺寸与 SHA-256；[sources.json](sources.json)：原 PDF 路径及 Git blob SHA。
- [质量报告](quality-report.md)：各卷汇总；每卷的详细记录在 `quality/`。

JSONL 每条题目都包含完整 `material`（如果有），包括材料文字、图表数据文字和图片路径。每题的 `figures` 包含题图；`options[].image_refs` 指向图形选项。读取图形题时，需要把图片一并交给支持图像的模型。所有 `path` 相对于本目录，不能只传 JSONL 而丢弃 `assets/`。

`answer.values` 表示候选答案集合：单选 `[ ["A"] ]`，多选 `[ ["A","B"] ]`，判断题 `[ ["正确"] ]`；争议答案例如 `[ ["D"], ["B"] ]`，表示 D 或 B 两个候选，**不是多选 DB**。`status` 分别为 `known`、`disputed`、`missing`。缺失时 `values=[]`。

判断推理题在 `notes` 中注明小类（`subtype:图形推理`、`subtype:定义判断`、`subtype:类比推理`、`subtype:逻辑判断`），组卷时可按小类筛选。原卷未单列科学推理部分的，按题型记为“科学推理”，并在 `notes` 中注明原卷位置。

需要留意：

- 2021年广东行测（乡镇卷）：第91—95题的答案只见于解析PDF后加的一行文字（没有解析过程），且原PDF自注材料2“参考必胜公考整理，真实性有待核实”；组卷时请留意。

## 图文处理

正文、选项、数字、分数及上下标转为文字；行内的分数、根号、公式小图转写为文字，不另存图片。55 个题图/材料图文件均为原 PDF 页面按 288 DPI 渲染后的裁剪，只裁图形本身，无重绘；12 个图表另有经过对照的文字转写，便于纯文本检索。多空选项的两词之间保留一个空格（原卷以空白分隔）。源文件的措辞、数据和答案按原卷保留，明显的印刷问题在题目 `notes` 中说明。页码为 PDF 的 1 起算物理页码。

## 整理与校验

整理工具在 `tools/`：每卷的登记信息在 `tools/papers/<卷>.json`，人工修正在 `tools/corrections/<卷>.json`（各键的说明见 `python3 tools/extract.py --help`）。

```bash
python3 tools/extract.py dump <卷>          # 自动分题结果，供核对、编写修正
python3 tools/extract.py answer-sheet <卷>  # 扫描版答案：裁出答案候选行拼图，人工读取
python3 tools/extract.py build <卷>         # 只生成本卷文件，并校验本卷
python3 tools/extract.py index              # 合并生成根目录汇总
python3 tools/extract.py verify             # 校验全部卷与汇总
```

`build` 只写本卷的 `<卷>.jsonl`、`<卷>.md`、`assets/<卷>/`（含 `manifest.json`）、`quality/<卷>.md`、`sources/<卷>.json`，多人可以同时整理不同的卷；根目录的 `all.jsonl`、`assets-manifest.json`、`sources.json`、`quality-report.md` 与本文件只由 `index` 生成，合并后有冲突时重跑 `index` 即可。

## 来源与可追溯性

原始 PDF 位于仓库的 `真题/` 与 `答案解析/`，未修改。提取基于提交 `52f9811b22cad5410a7108dd0a07a879f1187aa5`；4 个源文件的 blob SHA 见 [sources.json](sources.json)，build 时均已与本地 PDF 核对一致。

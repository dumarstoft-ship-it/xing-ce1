# 广东事业单位统考《基本能力测试》整卷结构化题库（2022—2026）

5 套试卷，共 500 题。按卷保留原题号，收录题干、选项、答案，不收录解析。每行一题的字段、题图裁剪与清单、答案写法、质量报告与广东省考题库（[行测 2013—2021](../../行测/2013-2021/README.md)、[行测 2022—2026](../../行测/2022-2026/README.md)）一致，组卷工具可以同样读取；`exam` 为“事业单位公开招聘考试”，`subject` 为“基本能力测试”，`year` 为 2022—2026。

| 试卷 | 题数 | 判断题 | 多选题 | 单选题 | 明确答案 | 争议答案 | 答案缺失 | 文件 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 2022年广东事业单位统考《基本能力测试》 | 100 | 20 | 10 | 70 | 100 | 0 | 0 | [阅读](SYDW2022.md) · [JSONL](SYDW2022.jsonl) · [质量报告](quality/SYDW2022.md) |
| 2023年广东事业单位统考《基本能力测试》 | 100 | 20 | 10 | 70 | 100 | 0 | 0 | [阅读](SYDW2023.md) · [JSONL](SYDW2023.jsonl) · [质量报告](quality/SYDW2023.md) |
| 2024年广东事业单位统考《基本能力测试》 | 100 | 20 | 10 | 70 | 99 | 1 | 0 | [阅读](SYDW2024.md) · [JSONL](SYDW2024.jsonl) · [质量报告](quality/SYDW2024.md) |
| 2025年广东事业单位统考《基本能力测试》 | 100 | 20 | 10 | 70 | 100 | 0 | 0 | [阅读](SYDW2025.md) · [JSONL](SYDW2025.jsonl) · [质量报告](quality/SYDW2025.md) |
| 2026年广东事业单位统考《基本能力测试》 | 100 | 20 | 10 | 70 | 100 | 0 | 0 | [阅读](SYDW2026.md) · [JSONL](SYDW2026.jsonl) · [质量报告](quality/SYDW2026.md) |

## 给 AI 的入口

- [all.jsonl](all.jsonl)：每行一道题，UTF-8；可直接逐行解析、分块或建立检索索引。
- 每卷的 Markdown：供阅读，保留图片与图表文字数据。
- [schema.json](schema.json)：字段类型；[assets-manifest.json](assets-manifest.json)：图片来源（PDF 页与裁剪坐标 pt，或 Word 内的来源文件与显示尺寸）、像素尺寸与 SHA-256；[sources.json](sources.json)：源文件路径及 Git blob SHA。
- [质量报告](quality-report.md)：各卷汇总；每卷的详细记录在 `quality/`。

JSONL 每条题目都包含完整 `material`（如果有），包括材料文字、图表数据文字和图片路径。每题的 `figures` 包含题图；`options[].image_refs` 指向图形选项。读取图形题时，需要把图片一并交给支持图像的模型。所有 `path` 相对于本目录，不能只传 JSONL 而丢弃 `assets/`。

`answer.values` 表示候选答案集合：单选 `[ ["A"] ]`，多选 `[ ["A","B"] ]`，判断题 `[ ["正确"] ]`；争议答案例如 `[ ["D"], ["B"] ]`，表示 D 或 B 两个候选，**不是多选 DB**。`status` 分别为 `known`、`disputed`、`missing`。缺失时 `values=[]`。

`section` 照原卷部分记（原卷“常识应用”记为常识判断，“言语表达与理解”记为言语理解与表达；原卷只按题型分部分的，按题目内容记，并在 `notes` 中说明）。判断推理题在 `notes` 中注明小类（`subtype:图形推理`、`subtype:定义判断`、`subtype:类比推理`、`subtype:逻辑判断`），组卷时可按小类筛选。

## 与省考题库的不同

- 题型：常识部分有判断题（`question_type` 为 `true_false`，原卷没有选项，`options` 为空数组，答案为“正确/错误”）和多选题（`multiple_choice`）。题型按原卷标注登记，并与答案逐题核对。
- 卷名为 `SYDW<年>`（如 `SYDW2024-Q001`），没有乡镇/县级后缀；`paper_variant` 记为“未标卷别”。
- Word 题源（2026年卷）：题图按原样从 .docx 的 word/media/ 取出（`method` 为 `docx_original`，schema 的 method 为此增加了这个值），不裁剪、不重新编码；清单中 `source_page`、`source_bbox_points` 为 null，另记 `source_file`（文档内路径）与 `docx_extent_points`（文档中的显示尺寸，pt）。Word 没有页码，`question_pages`、`material.source_pages`、`answer.source_pages` 为空数组；`source.question_pdf` 与 `source.answer_pdf` 都填该 .docx 的路径（字段名沿用省考题库）。
- 源文件缺图、缺资料的题照实记录：原文档缺题图（图中画有选项）的题 `options` 为空数组；缺资料的资料分析题 `material` 为 null；均在 `notes` 中说明（以“原文档缺”开头），无法单独使用。
- 组卷工具 `广东行测18套模拟/重编/tools/build_paper.py` 目前只读取 `广东/行测/` 下的 `GD20*.jsonl`、按 `GD…` 编号解析来源，打印排版按 `广东/行测/` 的 `assets-manifest.json` 取原卷印宽；要用本题库，需把本目录、`SYDW20*.jsonl` 与 `SYDW…` 编号加进去（Word 原图没有 PDF 裁剪框，印宽可用 `docx_extent_points`）。本题库未改动组卷工具。

需要留意：

- 2024年广东事业单位统考《基本能力测试》：第72题答案解析给出D、B两个答案（两种解法，解析倾向D），记为争议；组卷时请留意。
- 2025年广东事业单位统考《基本能力测试》：原版题本是打印成曲线的矢量PDF（网友回忆版，没有文字层），文字按原版逐字转写（以有文字层的版本2为底稿）；版本2与原版有较多文字出入、7题答案不同，本卷一律以原版为准，出入见质量报告。
- 2026年广东事业单位统考《基本能力测试》：原文档缺第66题题图、第91—95题资料、第96—100题资料中的统计图（第98、100题需要）、第62题C/D两项的数值；这些题照实记录并在 notes 中说明，第66、91—95题无法单独使用。
- 2026年广东事业单位统考《基本能力测试》：第67、71题的答案解析注明题图/选项有误，答案照原文档记录。

## 图文处理

正文、选项、数字、分数及上下标转为文字；行内的分数、公式小图转写为文字，不另存图片。68 个题图/材料图文件中，58 个为原 PDF 页面按 288 DPI 渲染后的裁剪，只裁图形本身，无重绘；10 个为 Word 文档中的原图，按原样保存；15 个图表另有经过对照的文字转写，便于纯文本检索。源文件的措辞、数据和答案按原卷保留，错字照录，明显的印刷问题在题目 `notes` 中说明。PDF 页码为 1 起算的物理页码。

## 整理与校验

整理工具在 `tools/`（由 `广东/行测/2013-2021/tools/` 复制后修改）：每卷的登记信息在 `tools/papers/<卷>.json`，人工修正在 `tools/corrections/<卷>.json`（各键的说明见 `python3 tools/extract.py --help`）。

```bash
python3 tools/extract.py dump <卷>          # 自动分题结果（PDF 或 Word），供核对、编写修正
python3 tools/extract.py answer-sheet <卷>  # 扫描版答案：裁出答案结论行拼图，人工读取
python3 tools/extract.py build <卷>         # 只生成本卷文件，并校验本卷
python3 tools/extract.py index              # 合并生成根目录汇总
python3 tools/extract.py verify             # 校验全部卷与汇总
```

`build` 只写本卷的 `<卷>.jsonl`、`<卷>.md`、`assets/<卷>/`（含 `manifest.json`）、`quality/<卷>.md`、`sources/<卷>.json`，多人可以同时整理不同的卷；根目录的 `all.jsonl`、`assets-manifest.json`、`sources.json`、`quality-report.md` 与本文件只由 `index` 生成，合并后有冲突时重跑 `index` 即可。

## 来源与可追溯性

原始文件位于仓库的 `广东/事业单位/<年>/`，未修改。提取基于提交 `3eadbf4cafe03d1f6e9089b3bb696e838ee60f0a`；10 个源文件的 blob SHA 见 [sources.json](sources.json)，build 时均已与本地文件核对一致。

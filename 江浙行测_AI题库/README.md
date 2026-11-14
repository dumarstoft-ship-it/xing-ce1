# 江浙行测 AI 题库

按源仓库现有江苏、浙江试卷，整理 **判断推理、言语理解与表达、数量关系**。题目与答案解析分开，提供 Markdown、逐题 JSONL 和独立图片。

**共 14 组试卷、1,215 个原题号**：判断推理 553，言语 377，数量 285。其中 11 个题号仅保留原文件的缺题占位，14 道题有原文省略条件；不自行补题。

根据用户要求，**不收录题干或选项含图片的言语题**：2024 浙江第 41 题、2025 浙江第 38 题、2026 浙江第 40 题。对应答案解析和重绘图也未收录。

## 读取入口

- [questions.jsonl](questions.jsonl)：每行一道题，含选项、共用材料全文、图片位置、原题号和来源页码，不含答案字段。
- [answers.jsonl](answers.jsonl)：通过 `question_id` 对应题目，存放来源参考答案及原解析；缺失或冲突的答案为 `null`。
- [materials.jsonl](materials.jsonl)：18 组共用材料；每道相关题中也嵌入材料，便于 AI 单独读取。
- [图片索引](images/manifest.json)：329 个原图资产；27 个附代码描摹高清 PNG / SVG。原图始终保留。
- [质量与缺失说明](quality_report.md)、[试卷清单](manifest.json)、[来源文件清单](sources.json)。

## 按试卷阅读

|省份|年份 / 卷别|原题号数|题目|答案解析|
|---|---|---:|---|---|
|江苏|2020 / A类|100|[Markdown](papers/江苏/2020_A类/questions.md)|[Markdown](papers/江苏/2020_A类/answers.md)|
|江苏|2021 / A类|100|[Markdown](papers/江苏/2021_A类/questions.md)|[Markdown](papers/江苏/2021_A类/answers.md)|
|江苏|2022 / A类|98|[Markdown](papers/江苏/2022_A类/questions.md)|[Markdown](papers/江苏/2022_A类/answers.md)|
|江苏|2023 / A类|100|[Markdown](papers/江苏/2023_A类/questions.md)|[Markdown](papers/江苏/2023_A类/answers.md)|
|江苏|2024 / A类|100|[Markdown](papers/江苏/2024_A类/questions.md)|[Markdown](papers/江苏/2024_A类/answers.md)|
|江苏|2025 / A类|95|[Markdown](papers/江苏/2025_A类/questions.md)|[Markdown](papers/江苏/2025_A类/answers.md)|
|江苏|2026 / 卷别未注明|20|[Markdown](papers/江苏/2026_卷别未注明/questions.md)|[Markdown](papers/江苏/2026_卷别未注明/answers.md)|
|浙江|2020 / B卷|70|[Markdown](papers/浙江/2020_B卷/questions.md)|[Markdown](papers/浙江/2020_B卷/answers.md)|
|浙江|2021 / A类|90|[Markdown](papers/浙江/2021_A类/questions.md)|[Markdown](papers/浙江/2021_A类/answers.md)|
|浙江|2022 / A类|90|[Markdown](papers/浙江/2022_A类/questions.md)|[Markdown](papers/浙江/2022_A类/answers.md)|
|浙江|2023 / A类|90|[Markdown](papers/浙江/2023_A类/questions.md)|[Markdown](papers/浙江/2023_A类/answers.md)|
|浙江|2024 / A类|89|[Markdown](papers/浙江/2024_A类/questions.md)|[Markdown](papers/浙江/2024_A类/answers.md)|
|浙江|2025 / A类|89|[Markdown](papers/浙江/2025_A类/questions.md)|[Markdown](papers/浙江/2025_A类/answers.md)|
|浙江|2026 / A类|84|[Markdown](papers/浙江/2026_A类/questions.md)|[Markdown](papers/浙江/2026_A类/answers.md)|

## 数据约定

- JSONL 为 UTF-8，一行一个 JSON 对象；`question_id` 在题目和答案文件中一一对应。省份、年份、卷别、科目、原题号均独立存储。
- `stem` 与 `options` 用于结构化读取；`content` 保留完整阅读顺序。仅在图中的选项明确标为 `options_mode: in_figure`，需要结合 `figures` 阅读。
- 图片路径以本目录为根；Markdown 试卷使用相对链接。`source.pdf_pages` 是从 1 开始的 PDF 物理页码，不是页脚印刷编号。图片可以注明同仓库解析文件中的清晰对应图作为来源。
- 纯文字、分数、根式、公式、数表尽量转成文本。`C(n,k)` 表示组合数，`A(n,k)` 表示排列数；幂次采用上标或括号，根式采用 `√` / `∛`，带分数写为“整数又分子/分母”。数表保留位置关系。
- 填空位置写作下划线；正文中原有划线以 `<u>...</u>` 保留。原文可见错字、错误论述和省略不擅自修正，已确认的问题写入 `quality_flags` / `notes`。
- 代码描摹按原图轮廓及灰度生成，不能恢复原图未提供的细节。最新范围内没有收录 AI 模型重绘图。

## 本地使用与校验

```bash
python3 tools/validate.py
python3 tools/read_questions.py --province 江苏 --year 2024 --section 数量关系
python3 tools/read_questions.py --province 浙江 --complete-only --with-answers
```

`--with-answers` 才会主动关联答案；`--complete-only` 会跳过缺题占位和原文省略题。

## 来源固定版本

[源仓库 dumarstoft-ship-it/xingce](https://github.com/dumarstoft-ship-it/xingce) 的提交 `407016b55b49581efa3771bb59a2dee8761d982f`。26 个相关 PDF 的路径、Git blob SHA 和逐题页码均已记录。源仓库 2026 江苏现有相关材料只包含数量关系，卷别未注明；2026 浙江现有题目没有配套答案解析。未将其他省份或常识、政治、资料分析加入本库。

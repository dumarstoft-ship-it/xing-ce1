# 构建说明

从原书 PDF 重新生成精选本。改选题、改导读文字都只改 `selection.py`，然后重跑下面的命令。

| 脚本 | 作用 |
| --- | --- |
| `extract.py` | 从原书提取337题的题源、题面、答案和解析，记下每题所在页 |
| `selection.py` | 选题与分类、各模型的导读文字、每题突破口；写出 selection.json |
| `build.py`、`pages.py`、`render.js`、`fonts.py` | 排导读页并抽取原书题页，拼成精选本 |
| `verify.py` | 逐题核对题面、页码、双面奇偶、链接和字体 |
| `readme_gen.py` | 生成上一级的 README.md 和 选题清单.json |

题页从原书原样抽取，只改两处：右下角页码换成新页码，字体和位置都不变；练习页右上角加“精选 n / N”。原书的内部链接在新书里会失效，所以删去；指向仓库原卷和参考解析的外部链接保留。

## 依赖

- Python 3：`pypdf`、`fontTools`
- Node.js 与 `playwright`（Chromium）
- poppler-utils：`pdftotext`、`pdffonts`
- 字体：Noto Sans CJK 的 Light、Medium 两种字重（Ubuntu 包 `fonts-noto-cjk`、`fonts-noto-cjk-extra`）

## 命令

在本目录下运行，`W` 是任意临时目录：

```bash
W=/tmp/jx && mkdir -p $W
```

```bash
python3 extract.py ../../综合推理二刷题本_广东真题增补_337题分类逐题解析.pdf $W/records.json
```

```bash
python3 selection.py $W/selection.json $W/records.json
```

```bash
python3 build.py ../../综合推理二刷题本_广东真题增补_337题分类逐题解析.pdf $W/selection.json $W/records.json ../综合推理精选本_80题.pdf --work $W/work
```

```bash
python3 verify.py ../综合推理精选本_80题.pdf $W/selection.json $W/records.json ../../综合推理二刷题本_广东真题增补_337题分类逐题解析.pdf
```

```bash
python3 readme_gen.py $W/selection.json $W/records.json $W/work/layout.json .. 综合推理精选本_80题.pdf ../综合推理二刷题本_广东真题增补_337题分类逐题解析.pdf $W/notes.json
```

题数变了要同时改输出文件名。

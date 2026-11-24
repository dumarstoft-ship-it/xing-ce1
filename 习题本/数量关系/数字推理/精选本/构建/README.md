# 构建说明

从原书 PDF 重新生成数字推理精选本。改选题、改导读文字都只改 `selection.py`，然后重跑下面的命令。

| 脚本 | 作用 |
| --- | --- |
| `extract_sx.py` | 从原书提取249题的出处、题面、答案、解析和在页面上的位置，另存30个模型的首式提示 |
| `selection.py` | 选题与分模块、导读文字、每题首式；写出 selection.json |
| `build_sx.py`、`pages_sx.py`、`common.py`、`cliptools.py`、`fonts.py`、`render.js` | 裁题块、排导读页和题页框架，拼成精选本 |
| `verify_sx.py` | 逐题核对练习页与背面解析、页码、双面奇偶、链接和文字层 |
| `readme_sx.py` | 生成上一级的 README.md 和 选题清单.json |

原书一页放五六道题，所以不能整页抽取：每道题的练习块和解析块用 pdftocairo 从原书矢量裁出，只含这一块的内容和文字，再贴到新页面上。练习在正面，同一组题的解析在背面。裁切后的文字层会把“首、广、用”等字记成康熙部首码位，构建时改回标准汉字。真题出处链接平移后保留，“回练”改指本册页码。

## 依赖

- Python 3：`pypdf`、`pdfplumber`、`fontTools`
- Node.js 与 `playwright`（Chromium）
- poppler-utils：`pdftocairo`、`pdftotext`、`pdffonts`
- 字体：Noto Sans CJK 的 Light、Medium 两种字重（Ubuntu 包 `fonts-noto-cjk`、`fonts-noto-cjk-extra`）

## 命令

在本目录下运行，`W` 是任意临时目录：

```bash
W=/tmp/sx && mkdir -p $W
```

```bash
python3 extract_sx.py ../../广东数字推理_30个模型条件反射训练.pdf $W/records.json
```

```bash
python3 selection.py $W/selection.json $W/records.json
```

```bash
python3 build_sx.py ../../广东数字推理_30个模型条件反射训练.pdf $W/selection.json $W/records.json $W/records_models.json ../数字推理精选本_75题.pdf --work $W/work
```

```bash
python3 verify_sx.py ../数字推理精选本_75题.pdf $W/selection.json $W/records.json $W/work/layout.json
```

```bash
python3 readme_sx.py $W/selection.json $W/records.json $W/work/layout.json .. 数字推理精选本_75题.pdf ../广东数字推理_30个模型条件反射训练.pdf
```

题数变了要同时改输出文件名。

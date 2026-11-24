# 构建说明

从两本原书 PDF 重新生成图形推理精选本。改选题、改方法卡文字，只改 `sel_cube.py`、`sel_space.py`、`sel_plane.py`（训练模块）和 `selection.py`（限时套卷、封面、认知地图、选题说明），然后重跑下面的命令。

| 文件 | 作用 |
| --- | --- |
| `extract_tt.py` | 从两本原书提取378题的出处、答案、解析和题块、解析块在页面上的位置 |
| `评估/eval_*.json` | 逐题评估：级别（核心、进阶、备选、删、留作限时）、题型、最快路径、限时、发现的问题和理由 |
| `sel_cube.py`、`sel_space.py`、`sel_plane.py` | 训练模块的分组、方法卡文字和勘误；题目的最快路径取自逐题评估 |
| `selection.py` | 汇总全部模块，配限时套卷，写封面、认知地图和选题说明；写出 selection.json |
| `build_tt.py`、`pages_tt.py`、`common.py`、`cliptools.py`、`fonts.py`、`render.js` | 裁题块、排导读页和题页框架，拼成精选本 |
| `verify_tt.py` | 逐题核对编号、原题号、解析位置、页码、链接、文字层和字体嵌入 |
| `readme_tt.py` | 生成上一级的 README.md 和 选题清单.json |

每道题的题块和解析块用 pdftocairo 从原书矢量裁出，只含这一块的内容和文字，再贴到新页面上。178题的题号行在裁切后会丢字形，所以从题图上沿开始裁；200题的题号行与本册标签重复，也不裁，解析块止于正文，不含“延伸阅读”和“原答案／参考口径”两行。出处统一印在本册的题目标签里。裁切后的文字层会把一些汉字记成康熙部首码位，构建时改回标准汉字。

训练模块题后即看答案；限时套卷先排一套5道题，再排这一套的答案页，题页不印原题号。

## 依赖

- Python 3：`pypdf`、`pdfplumber`、`fontTools`
- Node.js 与 `playwright`（Chromium）
- poppler-utils：`pdftocairo`、`pdftotext`、`pdffonts`，以及 `poppler-data`（178题用 Adobe-GB1 字体，缺它提取不到文字）
- 字体：Noto Sans CJK 的 Light、Medium 两种字重（Ubuntu 包 `fonts-noto-cjk`、`fonts-noto-cjk-extra`）

## 命令

在本目录下运行，`W` 是任意临时目录，`B` 是原书目录：

```bash
W=/tmp/tt && mkdir -p $W && B=../../200题与固定题型_题后即看答案
```

```bash
python3 extract_tt.py "$B/固定题型178题_题后即看答案.pdf" "$B/平面图推200题_题后即看答案.pdf" "$B/平面图推200题_答案数据.json" $W/records.json
```

```bash
python3 selection.py $W/records.json $W/selection.json
```

```bash
python3 build_tt.py "$B/固定题型178题_题后即看答案.pdf" "$B/平面图推200题_题后即看答案.pdf" $W/selection.json $W/records.json ../图形推理精选本_207题.pdf --work $W/work
```

```bash
python3 verify_tt.py ../图形推理精选本_207题.pdf $W/selection.json $W/records.json $W/work/layout.json
```

```bash
python3 readme_tt.py $W/selection.json $W/records.json $W/work/layout.json .. 图形推理精选本_207题.pdf ../200题与固定题型_题后即看答案
```

题数变了要同时改输出文件名。裁好的题块缓存在 `$W/work/clips`，改了裁切坐标要先删掉这个目录。

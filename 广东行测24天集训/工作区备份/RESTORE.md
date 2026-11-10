# 工作区备份与恢复

这里是编题工作区 `/home/user/work` 的备份（2026-11-10）。工具和说明里的路径都写死为 `/home/user/work/...`，所以要恢复到同一位置。

## 恢复
```bash
mkdir -p /home/user/work && cp -r "/home/user/xing-ce1/广东行测24天集训/工作区备份/work/." /home/user/work/
```
然后按需补两样（不补也能继续编题）：
- 各批成品目录：`build/pkg2`（第1批）、`build/pkg_r2`、`build/pkg_r3` 可从本分支 `Claude_资料判断言语/第1批`、`第2批`、`第3批` 整目录复制过去；`used_list.py` 和盲审脚本会读它们。
- 编者脚本：备份里的 `scratchpad_scripts/` 原来在会话临时目录下（任务书和报告里写的 `/tmp/claude-0/.../scratchpad/<编者>/`）。新会话里那个路径不存在，用的时候直接从 `scratchpad_scripts/<编者>/` 取。

## 备份了什么
| 目录或文件 | 内容 |
|---|---|
| `SPEC.md` | 共同编者工作说明（历次用户决定、GPT 审核要求、各轮补充） |
| `tools/` | render、claim、validate、assemble、build_books、used_list、review_list、mk_blind、cmp_blind、save_report 等 |
| `index/`、`answers/`、`qindex.jsonl` | 各卷切题索引、自动抽取的参考答案、全题平铺索引（含同题组） |
| `out/claims.jsonl`、`out/claims_notsame.jsonl` | 已用题登记库、图推“不是同题”名单 |
| `out/zl_materials/` | 资料材料库（合并和改编都要用） |
| `out/`、`out2/`、`out3/` 各编者目录 | 第 1—3 轮的题目数据、脚本、检查记录（不含图片，图片在各批成品里） |
| `out4/` | 第 4 轮现场，全部保留，含图片、任务书 `briefs/`、各编者报告或 `progress.*` |
| `build/` | 合并配置等小文件 |
| `books/` | 打印题本的脚本 |
| `scratchpad_scripts/` | 各编者放在临时目录里的脚本（只收 .py、.js） |

没有备份、可以重新生成的：`renders/`、`ocr/`（出图和 OCR 缓存）、`quant/`（数量原文提取的中间文件，成品在 `共享输入/数量原文/`）、`build/pkg*`（见上）。

## 依赖
- 两个题源仓库要在 `/home/user/xing-ce1` 和 `/home/user/xingce`（索引里的 PDF 路径是相对 `/home/user` 的）。
- Python 用到 PyMuPDF（fitz）、Pillow、bs4；打印题本另用 pandoc 和 Node 的 playwright。

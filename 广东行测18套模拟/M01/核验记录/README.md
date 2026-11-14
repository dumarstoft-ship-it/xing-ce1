# M01核验记录

这里保留本轮选编中的独立作答、计算、来源定位、交叉复核与处理记录。它们是本轮内部工作证据，不表示Claude已经审核，也不把来源参考答案视为天然正确。

| 文件组 | 内容 |
| --- | --- |
| `politics_independent_answers.json`、`politics_review.*` | 政治常识15题先盲答后对照；四项小修意见 |
| `politics_review_resolution.json` | 四项小修落实及额外来源补强；答案未变 |
| `verbal_independent_answers.json`、`verbal_review*` | 言语选编独立作答与另一位复核者的15题检查 |
| `verbal_national_provenance.json` | 国考入选题原卷题号、页码与文件哈希 |
| `quant_data_verification.json` | 数量与资料的计算、枚举及综合题逐项检查；弃选材料另列，不作为本卷已用 |
| `quant_data_prior_exposure_scan.json` | 对旧专项可读文本的精确重复检查与两道初选替换 |
| `judgment_verification.json` | 条件推理、计票、名次、对局及最终图题的补充核算 |
| `judgment_prior_exposure_scan.json` | 图题源ID、旧交付PDF与图像等排查范围及结果 |
| `old_graphic_source_ids.json` | 从旧200题与178题两册识别的来源索引，含另见卷别引用；供后续选题排查 |
| `judgment_logic_review.*` | 判断逻辑15题的追加独立复核 |
| `assembly_review.json` | 最终图题、服务贸易组与题面装配的主编复核范围 |
| `verbal_notes.md`、`quant_data_notes.md`、`judgment_notes.md` | 模块选择理由、弃选原因、来源限制及排版注意点 |

部分记录使用选编过程中的临时文件名和当时题面。当前有效底稿以[`../selection.json`](../selection.json)为准，修订响应说明哪些意见已经落实。旧题被交付与用户实际做过是不同事实；无匹配也不构成“从未见过”的保证。

# KRAS-G12D-pMHC-design

Computational design and control-based screening of KRAS G12D pMHC binders. Results are model predictions, not experimental binding evidence.

[中文说明](#中文说明)

## Research question

Can designed single-chain binders distinguish KRAS G12D peptide–HLA-A*11:01–β2m from matched wild-type and peptide-free controls under prespecified computational criteria?

## Current result

The preceding mixed-checkpoint BoltzGen batch produced 32 candidate designs. Its planned Boltz2 mutant screen completed 32/32 inputs (seed 15), and the project audit parsed all predictions with zero audit errors. None passed the frozen mutant gate (0/32); all 32 failed the peptide atom-pair contact threshold. Since none passed the first gate, WT/apo and repeat-seed confirmations were not run for that batch.

A later automatic follow-on run, `boltzgen_mixed25_clampF_mpnn_v1`, contained 32 candidate IDs despite “mixed25” in its run label. The seed-15 mutant screen completed 32/32; one candidate passed the mutant-only gate and proceeded to mutant/WT/apo confirmations at seeds 15, 16, and 17. All three confirmations failed the two mutant-versus-WT interface-difference thresholds, leaving zero qualified candidates. See [the follow-on run addendum](docs/RUN_STATUS_20261031_follow_on_screen.md).

The preceding checkpoint recorded 864 unique designs screened. A sequence-hash comparison found no exact match for the 32 follow-on candidates among 2,517 hashes recovered from prior project audit, generation, and results records. The recorded cumulative count is 896 unique designs screened and zero qualified candidates; see the coverage limits in `audit/boltzgen_mixed25_clampF_mpnn_v1_uniqueness_reconciliation.json`. These are computational screening results only and do not establish binding, affinity, or specificity experimentally.

See [run status](RUN_STATUS_20261031.md), [follow-on status](docs/RUN_STATUS_20261031_follow_on_screen.md), [frozen criteria](docs/criteria_v1.json), [criteria amendments](docs/), [progress history](docs/PROGRESS.md), and [results](results/RESULTS.md). This archive records existing work; it does not claim that earlier scientific runs were rerun or independently validated.

## Repository contents

- `scripts/`: project-specific input preparation, screening, audit, and comparison scripts.
- `audit/`: criteria, per-candidate metrics and gates, input ledgers, hashes, and run manifests.
- `results/`: selected structures and compact analysis outputs; near-miss candidates are not qualified.
- `inputs/`: selected public reference structures and screening inputs.
- `docs/`: criteria history, progress, and conversation coverage notes.
- Larger predictions, historical trees, full inputs, generation outputs, and sanitized logs are in the [historical Release](https://github.com/ziguimu/KRAS-G12D-pMHC-design/releases/tag/archive-2026-10-31) and the [follow-on screening Release](https://github.com/ziguimu/KRAS-G12D-pMHC-design/releases/tag/archive-2026-10-31-batch2). Each asset has a file-level manifest with source and published hashes.

## Reproduction and recovery

Historical commands, software versions, known corrections, incomplete or stopped runs, hardware notes, and source-coverage limits are retained where recorded. Public text copies redact local paths and host identifiers. Set paths for your own environment before running scripts; this repository is not a one-command reproduction claim.

Release assets are each below 512 MiB. Extract them into a clean directory and follow [RESTORE.md](RESTORE.md). Download both the historical archive and the supplemental follow-on screening Release to recover all archived stages. The manifest distinguishes byte-identical files from privacy-redacted text copies. The corresponding original text files remain local where exact source bytes cannot be restored. Model weights, caches, and third-party tools with unresolved redistribution terms are excluded.

## Licensing

Original code is MIT licensed where rights are established. Original documentation and data are CC BY 4.0 where rights are established. Third-party materials retain their own terms; see [LICENSE-DATA.md](LICENSE-DATA.md) and the portfolio's [third-party register](https://github.com/ziguimu/protein-design-portfolio/blob/main/THIRD_PARTY_SOURCES.md).

## Conversation archive

The redacted long-form TfR1/KRAS campaign transcript is indexed under [docs/conversations](docs/conversations/README.md). The current GitHub-archival chat record is partial; the linked prior ChatGPT conversation was unavailable for retrieval, and inaccessible turns or attachments are not represented as complete coverage.

## 中文说明

本项目记录 KRAS G12D pMHC 结合剂的计算设计和对照筛选。计算预测不等同于实验结合证据。

### 研究问题

在预先规定的计算标准下，设计的单链结合剂能否区分 KRAS G12D 肽–HLA-A*11:01–β2m 与匹配的野生型、无肽对照？

### 当前结果

此前 BoltzGen 混合检查点批次生成了 32 个候选设计。既定 Boltz2 mutant 筛选（seed 15）完成 32/32 个输入；项目审计解析全部预测且没有审计错误。冻结 mutant 门槛通过数为 0/32；32 条均未通过肽原子对接触阈值，因此本批没有运行 WT/apo 或重复种子确认。

之后自动启动的后续运行标签为 `boltzgen_mixed25_clampF_mpnn_v1`，但输入和指标文件包含 32 个候选编号。seed 15 mutant 筛选完成 32/32；1 条通过 mutant 单阶段门槛，并进入 seed 15、16、17 的 mutant/WT/apo 确认。三次确认均未通过 mutant 相对 WT 的两项界面差值门槛，最终合格候选为零。详见[后续运行记录](docs/RUN_STATUS_20261031_follow_on_screen.md)。

上一检查点累计 864 条不同设计已筛选。对既有项目 audit、generation、results 记录中的 2,517 个序列哈希进行核对，本次 32 条均无完全匹配。记录的累计筛选数为 896 条独特设计，合格候选仍为零；覆盖范围和限制见 `audit/boltzgen_mixed25_clampF_mpnn_v1_uniqueness_reconciliation.json`。这些都只是计算筛选结果，不构成实验结合、亲和力或特异性证据。

详见[此前运行状态](RUN_STATUS_20261031.md)、[后续运行记录](docs/RUN_STATUS_20261031_follow_on_screen.md)、[冻结标准](docs/criteria_v1.json)、[标准修订](docs/)、[进度历史](docs/PROGRESS.md)和[结果](results/RESULTS.md)。本仓库归档已有工作，不表示重新运行或独立验证以往科学计算。

### 仓库内容

- `scripts/`：项目专用输入准备、筛选、审计与比较脚本。
- `audit/`：标准、逐候选指标与门槛结果、输入台账、哈希及运行清单。
- `results/`：精选结构和精简分析结果；近似候选不代表合格。
- `inputs/`：精选公开参考结构及筛选输入。
- `docs/`：标准历史、进度和对话覆盖说明。
- 大型预测、历史目录、完整输入、生成输出和脱敏日志位于[历史 Release](https://github.com/ziguimu/KRAS-G12D-pMHC-design/releases/tag/archive-2026-10-31)及[后续筛选 Release](https://github.com/ziguimu/KRAS-G12D-pMHC-design/releases/tag/archive-2026-10-31-batch2)。每个附件均附带来源与发布哈希组成的逐文件清单。

### 复现与恢复

尽可能保留历史命令、软件版本、已知修正、未完成或停止的运行、硬件说明和资料覆盖限制。公开文本副本已脱敏本机路径和主机标识；执行脚本前需按自己的环境配置路径。本项目不宣称一键复现。

Release 单个附件均小于 512 MiB。请解压到干净目录并按 [RESTORE.md](RESTORE.md) 操作。恢复后续筛选时还需下载后续筛选 Release。清单区分字节相同文件与脱敏文本副本。无法由发布文本恢复原始字节的源文件仍保留在本地。模型权重、缓存及再分发许可未明确的第三方工具不在附件中。

### 许可

权利明确的原创代码采用 MIT；原创文档和数据采用 CC BY 4.0。第三方材料依照其自身条款，见 [LICENSE-DATA.md](LICENSE-DATA.md) 和总览仓库的[第三方来源登记](https://github.com/ziguimu/protein-design-portfolio/blob/main/THIRD_PARTY_SOURCES.md)。

### 对话记录

脱敏后的 TfR1/KRAS 长流程对话见 [docs/conversations](docs/conversations/README.md)。本次 GitHub 归档对话记录为部分覆盖；所链接的先前 ChatGPT 对话无法读取，未将无法访问的消息或附件表示为完整记录。

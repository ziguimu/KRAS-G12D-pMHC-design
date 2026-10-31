# KRAS Challenge 5 run status — 2026-10-31

The mixed-checkpoint BoltzGen design and inverse-folding batch completed 32/32 designs with zero failed examples. The planned Boltz2 mutant screen (seed 15) then completed 32/32 inputs with zero failed model examples. The project audit parsed all 32 predictions with zero audit errors.

The frozen mutant gate passed 0/32 candidates. All 32 failed the peptide atom-pair contact criterion; additional confidence, interface, geometry, and clash criteria failed for subsets. Because no candidate passed the first-stage mutant gate, WT/apo controls and repeated-seed confirmation were not run for this batch. This is a computational filter result, not experimental binding evidence.

The cumulative count is 864 unique designs screened (832 previously recorded plus these 32 sequence-checked candidates), with zero qualified candidates. The target of three qualified candidates was not met.

A prepared-only historical input ledger had been interpreted as a screened-sequence duplicate source. Cross-checking its status and prediction outputs showed that those sequences had no prior screen results. The current 32 candidates were therefore screened and are included in the cumulative count. The superseded duplicate-exclusion ledger is retained as history alongside the corrected audit and explanation.

An automatically launched resume process later attempted to write to the same prediction directory. It was terminated to prevent concurrent output collisions. Its partial log is retained. The original planned run completed and its 32 outputs passed the project parser. No further design or folding computation was started for archival.

The run log reports an NVIDIA RTX 5070 Laptop GPU. Third-party model weights, model caches, and tools with unresolved redistribution terms remain excluded.

## 中文说明

BoltzGen 混合检查点的设计和逆折叠批次完成 32/32 条，模型失败数为零。随后按既定流程完成 Boltz2 mutant 筛选（seed 15）：32/32 个输入完成，模型失败数为零。项目审计解析全部 32 个预测，审计错误为零。

冻结 mutant 门槛通过数为 0/32。32 条均未达到肽原子对接触标准；部分候选还未通过置信度、界面、几何或碰撞标准。由于第一阶段 mutant 门槛无人通过，本批未运行 WT/apo 对照或重复种子确认。这是计算过滤结果，不是实验结合证据。

累计为 864 条不同设计（此前记录 832 条，本次增加 32 条并完成序列核对），合格候选为零。未达到 3 条合格候选的目标。

一个仅准备输入的历史台账曾被误判为已筛选序列来源。检查该台账状态和预测输出后，确认对应序列此前没有筛选结果，因此本批 32 条实际进行了筛选并计入累计数。被替代的重复排除台账仍作为历史记录保留，并与更正说明一同归档。

后续自动恢复流程曾尝试写入同一预测目录。为避免并发输出冲突，已停止该重复进程并保留其不完整日志。原定筛选完成，项目解析器成功读取 32 个预测。归档期间没有启动额外设计或折叠计算。

运行日志记录 GPU 为 NVIDIA RTX 5070 Laptop。第三方模型权重、缓存及再分发许可不明的工具仍未纳入发布包。


This file is a frozen record of the preceding 864-design checkpoint. The subsequent automatic follow-on screen and three-seed confirmation are recorded in [RUN_STATUS_20261031_follow_on_screen.md](docs/RUN_STATUS_20261031_follow_on_screen.md); the cumulative unique screened-design count there is 896.

## Asp6 follow-on update (2026-10-31)

# KRAS Asp6 follow-on batch and screening update (2026-10-31)

## English

An automatic BoltzGen follow-on run, `boltzgen_Asp6_mixed32_v2`, completed its design and inverse-folding stages for 32/32 examples according to the retained log. The process exit code was not captured. An existing, designated Boltz2 mutant seed-15 screen then completed all 32 inputs. The prediction log reports zero failed examples; the project audit parsed 32/32 predictions with zero audit errors. The frozen mutant gate passed 0/32 candidates. No mutant/WT/apo confirmation panel was triggered.

Sequence-hash reconciliation found that all 32 generated sequences duplicate historical audited sequences. This batch adds zero unique sequences; the recorded cumulative unique count remains 896. The 32 repeat predictions are retained and reported separately from that unique-sequence count. Model metrics are computational screening evidence only, not experimental binding, affinity, or specificity evidence.

A separate accidental invocation, `boltzgen_Asp6_v2_mutant_seed15`, used a shared input directory containing 98 pre-existing YAMLs. It was stopped by the operator after about 77 seconds when the duplication was detected. Its 589 partial output files are included in the supplemental archive and explicitly excluded from all scientific metrics. The designated `boltzgen_Asp6_mixed32_v2_seed15` screen completed independently and was not interrupted.

The supplementary Release `archive-2026-10-31-batch3` stores the generated run, designated screen inputs and predictions, metrics, gate, sequence ledgers, logs, and the separated partial duplicate attempt. See the asset manifest for original and published hashes and the restore instructions. Some text files have privacy redactions, so their source byte hashes are recorded separately from the published byte hashes.

## 中文

自动启动的 BoltzGen 后续运行 `boltzgen_Asp6_mixed32_v2` 根据保留日志完成了 32/32 个设计与逆折叠样本；进程退出码未被捕获。随后，既定的 Boltz2 mutant seed-15 筛选完成 32/32 个输入。预测日志显示失败样本为 0；项目审计解析了 32/32 个预测且审计错误为 0。冻结的 mutant 门槛通过 0/32 个候选，因此没有触发 mutant/WT/apo 确认面板。

序列哈希核对发现，本批 32 条生成序列均与历史审计序列重复。本批新增独特序列数为 0，记录的累计独特序列数仍为 896。32 条重复序列的预测结果单独保留，不计作新增独特序列。模型指标仅是计算筛选证据，不构成实验结合、亲和力或特异性证据。

另有一次误启动的独立调用 `boltzgen_Asp6_v2_mutant_seed15` 使用了包含 98 个既有 YAML 输入的共享目录。发现重复后，操作人员在约 77 秒时停止了该调用。该调用生成的 589 个部分输出文件被收入补充归档，并明确排除在所有科学指标之外。既定的 `boltzgen_Asp6_mixed32_v2_seed15` 正式筛选独立完成，未被中断。

补充 Release `archive-2026-10-31-batch3` 保存生成运行、既定筛选输入与预测、指标、门槛结果、序列台账、日志及单独标记的重复调用部分输出。原始哈希与公开副本哈希见附件清单；恢复步骤见恢复说明。部分文本文件经过隐私脱敏，因此清单分别记录源文件和发布文件哈希。

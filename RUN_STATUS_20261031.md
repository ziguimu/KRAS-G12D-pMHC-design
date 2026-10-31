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

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

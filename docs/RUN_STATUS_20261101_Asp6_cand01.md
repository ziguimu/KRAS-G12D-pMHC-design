# Asp6 candidate 01: screen and confirmation record

Date: 2026-11-01 (Asia/Shanghai)  
Release: [archive-2026-11-01-batch4](https://github.com/ziguimu/KRAS-G12D-pMHC-design/releases/tag/archive-2026-11-01-batch4)  
Archive: `KRAS-Asp6-cand01-confirmation-01.zip`  
Archive SHA-256: `3a0b54786a2614de8c5fb4d59cbd540a47f2124e6e171cdd0c48323b6e8fa506`  
Manifest source records: 1,004 files; archive size 128,768,499 bytes.

## Workflow outcome

- `boltzgen_Asp6_cand01_mpnn_v1`: 64 candidates.
- Seed-15 mutant screen: 64/64 predictions parsed; zero prediction failures and zero audit errors.
- Initial mutant gate: 2 passed, 62 failed.
- Confirmation panel: six inputs (mutant/WT/apo for each of the two candidates), run at seeds 15, 16, and 17.
- Both candidates failed the numeric gate at each seed; 6/6 candidate-seed comparisons failed. Qualified candidates: 0.
- Seed 15 and 17 processes exited with code 0. Seed 16 logs and all six outputs are complete and parse without errors; the process exit code was not captured and is recorded as unknown.
- Sequence reconciliation: 64 unique sequences within this batch; no exact match among 367 historical sequence records scanned. The prior project-level cumulative count remains 896 for its documented scope; this comparison is not complete enough to recompute a global cumulative total.
- This is computational screening only. It does not demonstrate binding, affinity, specificity, or biological activity.

## Recovery validation

A fresh copy of the public Release asset was downloaded into a clean directory and checked with the repository restore verifier. Result: PASS, 1,004 expected and verified; 920 byte-identical and 84 privacy-transformed; zero missing members, size mismatches, published-hash mismatches, unsafe paths, unexpected ZIP members, or ZIP CRC errors.

## Included record types

The Release contains generation and prediction inputs/outputs, screen predictions, per-candidate metrics and gates, mutant/WT/apo panel inputs, three-seed confirmation predictions and comparisons, process logs, sequence reconciliation, and a completion reconciliation. The archive manifest records source-relative paths and source/published hashes. Privacy-transformed text restores its published representation and path, but not original source bytes; original source text remains local.

## 中文记录

- `boltzgen_Asp6_cand01_mpnn_v1` 共 64 条候选；seed 15 mutant 预测 64/64 均成功解析，预测失败 0，审计错误 0。
- mutant 初筛通过 2 条、未通过 62 条。两条候选各有 mutant/WT/apo 三种输入，并在 seed 15、16、17 确认；6/6 候选-种子比较均未通过数值门槛，合格候选为 0。
- seed 15、17 进程退出码为 0。seed 16 日志及六个输出完整且均可解析，退出码未捕获，记为未知。
- 本批次内部 64 条序列各不相同；与扫描的 367 条历史序列记录无完全匹配。此前项目级累计数 896 条仍仅适用于原有记录范围；本次比较覆盖不足，不能据此重算全局累计数。
- 结果仅为计算筛选，不代表实验结合、亲和力、特异性或生物活性证据。
- 独立下载恢复校验：1,004 项通过；920 项与源字节一致，84 项经过隐私转换。缺件、大小不符、哈希不符、不安全路径、意外 ZIP 成员及 CRC 错误均为 0。

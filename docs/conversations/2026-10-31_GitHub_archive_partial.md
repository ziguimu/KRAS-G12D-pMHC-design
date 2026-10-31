# GitHub project archival — partial conversation record

Coverage: currently accessible user instructions and task decisions from the active Codex conversation only. Earlier referenced ChatGPT conversation ID `<UUID>` was unavailable, so its messages and attachments are not included. This is not a complete account export.

## User request

The user requested a six-repository public GitHub portfolio covering AI BinderDesign (EGFR/TNF), GLP1R reproduction, TfR1 binder design, KRAS G12D pMHC design, the reusable AI protein design skill, and a portfolio overview. The user approved bilingual public documentation, preservation of historical outcomes and limitations, release assets for large outputs, remote restoration/hash verification, and exact-path local cleanup only after archive verification.

## KRAS task decision

The user chose to wait for the already running 32-design BoltzGen batch and its planned screening before archiving KRAS. No new design generation was authorized.

## Outcome recorded for this task

The mixed-checkpoint BoltzGen batch completed 32/32. The planned Boltz2 mutant screen completed 32/32, the audit parsed 32/32 predictions, and zero passed the frozen mutant gate. WT/apo and repeated-seed confirmation were not run because none passed the first gate. An automatically started overlapping resume process was stopped to avoid concurrent writes to the same output directory; its partial log was retained.

Sensitive internal system/developer instructions and inaccessible tool payloads are intentionally omitted from this public redacted transcript. Use the release manifest and run status files for file-level source and transformation records.

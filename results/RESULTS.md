# Results summary

| Stage | Candidates | Result |
|---|---:|---|
| Previously recorded Challenge 5 screens | 832 unique designs | 0 qualified |
| Mixed-checkpoint BoltzGen batch | 32 designs | 32/32 predicted and audited |
| Mutant seed-15 gate, current batch | 32 | 0 passed |
| WT/apo and repeat-seed confirmation, preceding batch | 0 | Not run because none passed the mutant gate |
| Automatic follow-on mutant screen | 32 | 1 passed the mutant-only gate |
| Follow-on mutant/WT/apo confirmation | 3 seeds | All 3 failed mutant-versus-WT interface-difference criteria |
| Cumulative | 896 unique designs | 0 qualified |

All 32 current candidates failed the peptide atom-pair contact criterion. Additional frozen confidence, interface, geometry, and clash criteria failed across subsets. See the per-candidate metrics and gate CSV files under `audit/`.

A historical ledger listed the same sequences as prepared for a screen. It had no associated prior prediction outputs and did not represent a completed screen. The current batch was therefore screened and counted once. The earlier duplicate-exclusion table remains in the raw audit package as a superseded record; see the reconciliation note in `audit/`.

No experimental binding or affinity measurements are available in this archive.


The automatic follow-on run is recorded separately in [the run addendum](../docs/RUN_STATUS_20261031_follow_on_screen.md). Its 32 sequence hashes did not match any of the 2,517 hashes recovered from prior sequence-bearing audit, generation, and results tables; the exact coverage is recorded in the uniqueness reconciliation JSON.

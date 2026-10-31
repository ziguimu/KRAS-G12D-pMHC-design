# Project progress

## Established workflow

The Challenge 5 record includes legacy pMHC design, RFdiffusion and ProteinMPNN stages, Boltz/BoltzGen workflows, mutant screens, and matched WT/apo or repeated-seed controls for candidates reaching later gates. Criteria and corrections remain versioned in the audit records.

## Current batch

- 32 mixed-checkpoint BoltzGen designs and inverse-folded structures completed without failed examples.
- Boltz2 mutant seed-15 screening completed for all 32 inputs.
- Structural audit parsed all 32; no parser errors.
- Frozen mutant gate: 0/32 passed.
- No WT/apo or repeated-seed runs were warranted under the pre-established workflow because none passed the mutant gate.
- Cumulative total: 864 unique designs screened; zero qualified candidates.
- An automatically launched overlapping resume process was stopped to prevent writes to the same output directory. Its partial log remains available as a failure/cancellation record.

## Interpretation limits

These are model-generated structures and scores. They are not measurements of binding affinity, experimental validation, or proof of mutant specificity. The archive preserves prior failed runs and corrections and does not relabel them as successful reruns.


## Follow-on screen completed 2026-10-31

- Automatic Boltz2 mutant seed-15 screen: 32/32 predictions; 1 passed the mutant-only gate.
- Candidate `boltzgen_mixed25_clampF_mpnn_v1_s4235_19` completed mutant/WT/apo confirmation at seeds 15, 16, and 17. All three confirmation gates failed the same two mutant-versus-WT interface-difference thresholds.
- Sequence-hash reconciliation found 32 new unique sequences in the recorded source tables. Cumulative total: 896 unique screened; zero qualified.
- Detailed scope and interpretation are in [the follow-on run status](RUN_STATUS_20261031_follow_on_screen.md).

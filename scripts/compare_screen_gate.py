import argparse
import csv
import json
import math
from pathlib import Path

from audit_baseline import ROOT, dump_csv

p = argparse.ArgumentParser()
p.add_argument('--candidate-metrics', required=True)
p.add_argument('--output', required=True)
a = p.parse_args()
criteria = json.loads((ROOT / 'criteria_v1.json').read_text())
baseline = [r for r in csv.DictReader((ROOT / 'audit' / 'baseline_seed15_v2_metrics.csv').open()) if r['condition'] == 'mutant']
assert len(baseline) == 4 and all(r['status'] == 'output_audited' for r in baseline)
high = criteria['higher_is_better_mutant']
low = criteria['lower_is_better_mutant']
thresholds = {k: max(float(r[k]) for r in baseline) for k in high}
thresholds.update({k: min(float(r[k]) for r in baseline) for k in low})
rows = []
for r in csv.DictReader(Path(a.candidate_metrics).open()):
    missing, failed = [], []
    if r['status'] != 'output_audited':
        missing.append('audited_prediction')
    else:
        for k in high + low:
            try:
                v = float(r[k])
                if not math.isfinite(v):
                    raise ValueError(k)
                if k in high and v < thresholds[k] - 1e-8:
                    failed.append(k)
                if k in low and v > thresholds[k] + 1e-8:
                    failed.append(k)
            except (KeyError, ValueError):
                missing.append(k)
        if float(r.get('all_target_pairs_lt2A', 0) or 0) > 0:
            failed.append('absolute_clash_gate')
    rows.append({'candidate_id': r['candidate_id'], 'status': 'missing_data' if missing else ('pass_mutant_screen_pending_controls' if not failed else 'failed_mutant_gate'), 'failed_metrics': ';'.join(failed), 'missing_metrics': ';'.join(missing), **{k: r.get(k, '') for k in thresholds}, 'peptide_atom_pairs_lt4A': r.get('peptide_atom_pairs_lt4A', ''), 'peptide_residue_pairs_lt4A': r.get('peptide_residue_pairs_lt4A', ''), 'peptide_positions_lt4A': r.get('peptide_positions_lt4A', ''), 'all_target_pairs_lt2A': r.get('all_target_pairs_lt2A', '')})
dump_csv(ROOT / 'audit' / f'{a.output}.csv', rows)
(ROOT / 'audit' / f'{a.output}_thresholds.json').write_text(json.dumps(thresholds, indent=2))
print(json.dumps({'screened': len(rows), 'passed_mutant_gate': sum(r['status'] == 'pass_mutant_screen_pending_controls' for r in rows), 'failed': sum(r['status'] == 'failed_mutant_gate' for r in rows), 'missing': sum(r['status'] == 'missing_data' for r in rows)}, indent=2))

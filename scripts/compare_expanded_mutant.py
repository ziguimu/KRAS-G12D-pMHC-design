import argparse, csv, json, math
from audit_baseline import ROOT, dump_csv

parser = argparse.ArgumentParser()
parser.add_argument('--metrics', default='audit/expanded_mutant_seed15_metrics.csv')
parser.add_argument('--output', default='audit/expanded_mutant_gate_v1.csv')
args = parser.parse_args()
baseline = list(csv.DictReader((ROOT / 'audit/baseline_seed15_v2_metrics.csv').open()))
candidates = list(csv.DictReader((ROOT / args.metrics).open()))
criteria = json.loads((ROOT / 'criteria_v1.json').read_text())
base = {r['candidate_id']: r for r in baseline if r['condition'] == 'mutant'}
assert len(base) == 4 and all(r['status'] == 'output_audited' for r in base.values())
thresholds = {}
for key in criteria['higher_is_better_mutant']:
    thresholds[key] = max(float(r[key]) for r in base.values())
for key in criteria['lower_is_better_mutant']:
    thresholds[key] = min(float(r[key]) for r in base.values())

out = []
for row in candidates:
    failed, missing = [], []
    if row['status'] != 'output_audited' or row['condition'] != 'mutant':
        missing.append('audited_mutant_prediction')
    else:
        for key, cut in thresholds.items():
            try:
                value = float(row[key])
                if not math.isfinite(value):
                    raise ValueError(key)
                if key in criteria['higher_is_better_mutant'] and value < cut - 1e-8:
                    failed.append(key)
                if key in criteria['lower_is_better_mutant'] and value > cut + 1e-8:
                    failed.append(key)
            except (ValueError, KeyError):
                missing.append(key)
    if float(row.get('all_target_pairs_lt2A', 0) or 0) > 0:
        failed.append('absolute_clash_gate')
    out.append({
        'candidate_id': row['candidate_id'],
        'status': 'missing_data' if missing else ('pass_mutant_screen_pending_controls' if not failed else 'failed_mutant_gate'),
        'failed_metric_count': len(failed),
        'failed_metrics': ';'.join(failed),
        'missing_metrics': ';'.join(missing),
        **{k: row.get(k, '') for k in thresholds},
    })

dump_csv(ROOT / args.output, out)
(ROOT / 'audit/expanded_mutant_thresholds_v1.json').write_text(json.dumps(thresholds, indent=2))
print(json.dumps({
    'screened': len(out),
    'mutant_gate_pass': sum(r['status'] == 'pass_mutant_screen_pending_controls' for r in out),
    'failed': sum(r['status'] == 'failed_mutant_gate' for r in out),
    'missing': sum(r['status'] == 'missing_data' for r in out),
    'best_near_misses': sorted(
        ({'candidate_id': r['candidate_id'], 'failed_metric_count': r['failed_metric_count'], 'failed_metrics': r['failed_metrics']} for r in out if r['status'] == 'failed_mutant_gate'),
        key=lambda r: (r['failed_metric_count'], r['candidate_id'])
    )[:10],
}, indent=2))

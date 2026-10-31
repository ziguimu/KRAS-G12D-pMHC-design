import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

import yaml

from audit_baseline import ROOT, dump_csv, sha

p = argparse.ArgumentParser()
p.add_argument('--run-id', required=True)
p.add_argument('--exclude-metrics', nargs='+', required=True)
p.add_argument('--output-id', required=True)
p.add_argument('--limit', type=int, default=32)
a = p.parse_args()
seq_csv = ROOT / 'audit' / f'{a.run_id}_sequences.csv'
raw = list(csv.DictReader(seq_csv.open()))
excluded = set()
for fname in a.exclude_metrics:
    path = ROOT / 'audit' / fname
    excluded.update(r['sequence'] for r in csv.DictReader(path.open()) if r.get('sequence'))
best = {}
for row in raw:
    seq = row['sequence']
    if seq in excluded:
        continue
    score = float(row['mpnn_score'])
    if seq not in best or score < float(best[seq]['mpnn_score']):
        best[seq] = row
chosen = sorted(best.values(), key=lambda r: (float(r['mpnn_score']), r['sequence']))[:a.limit]
if len(chosen) < 8:
    raise RuntimeError(f'Only {len(chosen)} unique novel sequences available')
template_path = ROOT / 'inputs' / 'rfd_micro_central_extended_try6_s016_fixedcontacts_all32_v2_panel' / 'rfd_micro_central_extended_try6_s016_fixedcontacts_s016_mutant.yaml'
template = yaml.safe_load(template_path.read_text())
out = ROOT / 'inputs' / f'{a.output_id}_mutant'
out.mkdir(exist_ok=True)
rows = []
for rank, r in enumerate(chosen, 1):
    cid = f'{a.output_id}_s{rank:03d}'
    payload = json.loads(json.dumps(template))
    d = next(e['protein'] for e in payload['sequences'] if e['protein']['id'] == 'D')
    d['sequence'] = r['sequence']
    path = out / f'{cid}.yaml'
    path.write_text(yaml.safe_dump(payload, sort_keys=False))
    rows.append({'candidate_id': cid, 'sequence': r['sequence'], 'length': len(r['sequence']), 'sequence_source': 'ProteinMPNN_fixed_contact_inverse_folding_on_Boltz2_mutant_pose', 'source_backbone': r['source_pdb'], 'mpnn_score': r['mpnn_score'], 'sequence_sha256': hashlib.sha256(r['sequence'].encode()).hexdigest(), 'input_yaml': str(path), 'input_sha256': sha(path), 'status': 'prepared_mutant_screen'})
dump_csv(ROOT / 'audit' / f'{a.output_id}_selected.csv', rows)
(ROOT / 'audit' / f'{a.output_id}_selection_manifest.json').write_text(json.dumps({'run_id': a.run_id, 'generated': len(raw), 'unique_novel_after_exclusion': len(best), 'excluded_metric_files': a.exclude_metrics, 'selected': len(rows), 'selection': 'lowest ProteinMPNN score after exact sequence deduplication and excluding prior tested sequences'}, indent=2))
print(json.dumps({'generated': len(raw), 'unique_novel_after_exclusion': len(best), 'selected': len(rows)}, indent=2))

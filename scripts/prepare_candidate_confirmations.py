import argparse
import csv
import json
from pathlib import Path

import yaml

from audit_baseline import ROOT, B2M, HLA, PEPTIDES, dump_csv, sha

p = argparse.ArgumentParser()
p.add_argument('--candidate-ids', nargs='+', required=True)
a = p.parse_args()
metric_files = [
    ROOT / 'audit' / 'rfd_micro_central_extended_try6_s016_fixedcontacts_all32_metrics.csv',
    ROOT / 'audit' / 'rfd_micro_central_extended_try6_s016_fixedcontacts_resample02_seed15_mutant_metrics.csv',
    ROOT / 'audit' / 'rfd_micro_central_extended_try6_s016_fixedcontacts_resample05_d6_bias_partialfix_seed15_mutant_metrics.csv',
]
metrics = {}
for path in metric_files:
    metrics.update({r['candidate_id']: r for r in csv.DictReader(path.open())})
ledger = []
for cid in a.candidate_ids:
    if cid not in metrics:
        raise ValueError(f'Candidate missing from audited metric files: {cid}')
    seq = metrics[cid]['sequence']
    out = ROOT / 'inputs' / f'{cid}_confirmation_panel'
    out.mkdir(exist_ok=True)
    for condition, peptide in {**PEPTIDES, 'apo': None}.items():
        chains = {'A': HLA, 'B': B2M, 'D': seq}
        if peptide is not None:
            chains['C'] = peptide
        entries = []
        for chain, chain_seq in chains.items():
            msa = str(ROOT / 'inputs' / 'msa' / f'{chain}.csv') if chain in ('A', 'B') else 'empty'
            entries.append({'protein': {'id': chain, 'sequence': chain_seq, 'msa': msa}})
        path = out / f'{cid}_{condition}.yaml'
        path.write_text(yaml.safe_dump({'version': 1, 'sequences': entries}, sort_keys=False))
        ledger.append({'candidate_id': cid, 'condition': condition, 'sequence': seq, 'length': len(seq), 'input_yaml': str(path), 'input_sha256': sha(path)})
dump_csv(ROOT / 'audit' / 'candidate_confirmation_inputs.csv', ledger)
print(json.dumps({'candidates': len(a.candidate_ids), 'conditions': len(ledger), 'candidate_ids': a.candidate_ids}, indent=2))

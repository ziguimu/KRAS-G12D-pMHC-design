import csv
import hashlib
import json
from pathlib import Path

import yaml

from audit_baseline import ROOT, B2M, HLA, PEPTIDES, dump_csv, sha

cid = 'rfd_micro_central_extended_try6_s016_fixedcontacts_resample02_s024'
metrics_path = ROOT / 'audit' / 'rfd_micro_central_extended_try6_s016_fixedcontacts_resample02_seed15_mutant_metrics.csv'
candidate = next(r for r in csv.DictReader(metrics_path.open()) if r['candidate_id'] == cid)
seq = candidate['sequence']
out = ROOT / 'inputs' / f'{cid}_confirmation_panel'
out.mkdir(exist_ok=True)
rows = []
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
    rows.append({'candidate_id': cid, 'condition': condition, 'sequence': seq, 'length': len(seq), 'input_yaml': str(path), 'input_sha256': sha(path)})
dump_csv(ROOT / 'audit' / f'{cid}_confirmation_ledger.csv', rows)
print(json.dumps({'candidate_id': cid, 'conditions': len(rows), 'input_files': [r['input_yaml'] for r in rows]}, indent=2))

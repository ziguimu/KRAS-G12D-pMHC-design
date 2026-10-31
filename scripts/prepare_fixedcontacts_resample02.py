import csv
import hashlib
import json
import re
from pathlib import Path

import yaml

from audit_baseline import ROOT, dump_csv, sha


RUN_ID = 'rfd_micro_central_extended_try6_s016_fixedcontacts'
BATCH = 'mpnn_resample02'
FASTA = ROOT / 'generation' / RUN_ID / BATCH / 'seqs' / 'rfd_micro_central_extended_try6_design_4118_s08_interfacebias_s016_mutant_model_0.fa'
SOURCE_YAML = ROOT / 'inputs' / 'rfd_micro_central_extended_try6_s016_fixedcontacts_all32_v2_panel' / 'rfd_micro_central_extended_try6_s016_fixedcontacts_s016_mutant.yaml'
OLD_LEDGER = ROOT / 'audit' / 'rfd_micro_central_extended_try6_s016_fixedcontacts_all32_metrics.csv'
OUT_DIR = ROOT / 'inputs' / f'{RUN_ID}_resample02_mutant'

old = {r['sequence'] for r in csv.DictReader(OLD_LEDGER.open())}
lines = FASTA.read_text().splitlines()
records = []
for i, header in enumerate(lines):
    if not header.startswith('>') or 'sample=' not in header:
        continue
    seq = lines[i + 1].strip()
    if len(seq) != 65:
        raise ValueError(f'Expected 65 aa sequence, got {len(seq)} for {header}')
    match = re.search(r'(?<!global_)score=([0-9.]+)', header)
    if not match:
        raise ValueError(f'No ProteinMPNN score: {header}')
    records.append((float(match.group(1)), seq, header))

# Retain the best-scoring occurrence for each unique new sequence.
best = {}
for score, seq, header in records:
    if seq not in old and (seq not in best or score < best[seq][0]):
        best[seq] = (score, header)
chosen = sorted(((score, seq, header) for seq, (score, header) in best.items()), key=lambda x: (x[0], x[1]))[:32]
if len(chosen) < 16:
    raise RuntimeError(f'Only {len(chosen)} unique new sequences available')

OUT_DIR.mkdir(exist_ok=True)
template = yaml.safe_load(SOURCE_YAML.read_text())
rows = []
for rank, (score, seq, header) in enumerate(chosen, 1):
    cid = f'{RUN_ID}_resample02_s{rank:03d}'
    payload = json.loads(json.dumps(template))
    d = next(e['protein'] for e in payload['sequences'] if e['protein']['id'] == 'D')
    d['sequence'] = seq
    path = OUT_DIR / f'{cid}.yaml'
    path.write_text(yaml.safe_dump(payload, sort_keys=False))
    rows.append({
        'candidate_id': cid,
        'sequence': seq,
        'length': len(seq),
        'sequence_source': 'ProteinMPNN_fixed_contact_resampling_on_boltz2_mutant_pose',
        'source_backbone_pdb': str(FASTA),
        'mpnn_score': score,
        'mpnn_header': header,
        'sequence_sha256': hashlib.sha256(seq.encode()).hexdigest(),
        'input_yaml': str(path),
        'input_sha256': sha(path),
        'status': 'prepared_mutant_screen',
    })
dump_csv(ROOT / 'audit' / f'{RUN_ID}_resample02_selected32.csv', rows)
(ROOT / 'audit' / f'{RUN_ID}_resample02_sampling_manifest.json').write_text(json.dumps({
    'run_id': RUN_ID,
    'batch': BATCH,
    'input_pose': str(FASTA),
    'input_pose_sha256': sha(FASTA),
    'input_fixed_positions': [12, 16, 19, 20, 23, 27, 52, 56],
    'generated_samples_including_temps': len(records),
    'new_unique_sequences': len(best),
    'excluded_prior_32_sequences': True,
    'selection': 'lowest ProteinMPNN score, exact-sequence deduplication',
    'selected': len(rows),
    'selected_ids': [r['candidate_id'] for r in rows],
}, indent=2))
print(json.dumps({'generated': len(records), 'new_unique': len(best), 'selected': len(rows)}, indent=2))

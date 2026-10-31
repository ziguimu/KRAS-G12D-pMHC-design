import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

from audit_baseline import ROOT, dump_csv, sha

p = argparse.ArgumentParser()
p.add_argument('--input-pdb', required=True)
p.add_argument('--output-id', required=True)
p.add_argument('--sequence-count', type=int, default=64)
p.add_argument('--seed', type=int, default=7301)
p.add_argument('--fixed-positions', nargs='+', type=int, default=[12, 16, 19, 20, 23, 27, 52, 56])
a = p.parse_args()
pdb = Path(a.input_pdb)
if not pdb.is_absolute():
    pdb = ROOT / pdb
out = ROOT / 'generation' / a.output_id
out.mkdir(parents=True, exist_ok=True)
fixed = out / 'fixed_positions.jsonl'
fixed.write_text(json.dumps({pdb.stem: {'A': [], 'B': [], 'C': [], 'D': a.fixed_positions}}) + '\n')
cmd = [
    '/home/<USER>/miniconda3/envs/proteinmpnn/bin/python',
    '/home/<USER>/ProteinMPNN/protein_mpnn_run.py',
    '--pdb_path', str(pdb), '--pdb_path_chains', 'D',
    '--fixed_positions_jsonl', str(fixed), '--out_folder', str(out),
    '--num_seq_per_target', str(a.sequence_count), '--sampling_temp', '0.1 0.2 0.3',
    '--seed', str(a.seed), '--batch_size', '1', '--omit_AAs', 'CX', '--save_score', '1',
]
manifest = {'route': 'ProteinMPNN inverse-folding on Boltz2 mutant pose with peptide-contact positions fixed', 'input_pdb': str(pdb), 'input_sha256': sha(pdb), 'fixed_positions_chain_D_1based': a.fixed_positions, 'fixed_positions_jsonl': str(fixed), 'fixed_positions_sha256': sha(fixed), 'sequence_count_per_temperature': a.sequence_count, 'seed': a.seed, 'command': cmd, 'status': 'running', 'start_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
(out / 'run_manifest.json').write_text(json.dumps(manifest, indent=2))
env = os.environ.copy()
env['TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD'] = '1'
with (out / 'run.log').open('w') as log:
    proc = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, env=env)
manifest.update(status='complete' if proc.returncode == 0 else 'failed', exit_code=proc.returncode, end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
(out / 'run_manifest.json').write_text(json.dumps(manifest, indent=2))
if proc.returncode:
    raise SystemExit(f'ProteinMPNN failed; inspect {out / "run.log"}')
fa = next((out / 'seqs').glob('*.fa'))
lines = fa.read_text().splitlines()
rows, sample = [], 0
for i, h in enumerate(lines):
    if not h.startswith('>') or 'sample=' not in h:
        continue
    sample += 1
    seq = lines[i + 1].strip()
    if len(seq) != 65:
        raise ValueError(f'Expected D-chain length 65; got {len(seq)} at {h}')
    m = re.search(r'(?<!global_)score=([0-9.]+)', h)
    rows.append({'candidate_id': f'{a.output_id}_s{sample:03d}', 'sequence': seq, 'length': len(seq), 'mpnn_score': m.group(1) if m else '', 'mpnn_header': h[1:], 'source_pdb': str(pdb), 'source_pdb_sha256': sha(pdb), 'sequence_sha256': hashlib.sha256(seq.encode()).hexdigest(), 'source_fasta': str(fa)})
dump_csv(ROOT / 'audit' / f'{a.output_id}_sequences.csv', rows)
print(json.dumps({'generated': len(rows), 'unique_sequences': len({r['sequence'] for r in rows}), 'source_pdb': str(pdb)}, indent=2))

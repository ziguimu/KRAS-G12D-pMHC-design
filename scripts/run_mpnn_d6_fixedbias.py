import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

import numpy as np
from Bio.PDB import PDBParser

from audit_baseline import ROOT, atoms, dump_csv, residues, sha

ALPHABET = 'ACDEFGHIKLMNPQRSTVWYX'
p = argparse.ArgumentParser()
p.add_argument('--input-pdb', required=True)
p.add_argument('--output-id', required=True)
p.add_argument('--count', type=int, default=64)
p.add_argument('--seed', type=int, default=8421)
p.add_argument('--fixed-positions', nargs='+', type=int, default=[12, 16, 19, 20, 23, 27, 52, 56])
a = p.parse_args()
pdb = Path(a.input_pdb)
if not pdb.is_absolute():
    pdb = ROOT / pdb
model = PDBParser(QUIET=True).get_structure('pose', pdb)[0]
peptide = atoms(model['C'])
asp6 = [x for x in model['C'][6] if x.element not in ('H', 'D') and x.name in ('OD1', 'OD2')]
chain = residues(model['D'])
bias = np.zeros((len(chain), len(ALPHABET)), dtype=float)
iface, d6 = [], []
for i, res in enumerate(chain):
    heavy = [x for x in res if x.element not in ('H', 'D')]
    if not heavy:
        continue
    dpep = min(float(np.linalg.norm(x.coord - y.coord)) for x in heavy for y in peptide)
    dasp = min(float(np.linalg.norm(x.coord - y.coord)) for x in heavy for y in asp6)
    if dpep <= 9.0:
        iface.append(i + 1)
        for aa, value in {'F': 1.2, 'Y': 1.2, 'W': 1.2, 'R': 0.7, 'K': 0.7, 'N': 0.4, 'Q': 0.4, 'S': 0.2, 'T': 0.2, 'A': -0.4}.items():
            bias[i, ALPHABET.index(aa)] = value
    if dasp <= 9.0:
        d6.append(i + 1)
        for aa, value in {'R': 3.0, 'K': 2.5, 'H': 1.2, 'Y': 0.8, 'W': 0.5, 'D': -1.5, 'E': -1.5, 'A': -2.0}.items():
            bias[i, ALPHABET.index(aa)] = value

out = ROOT / 'generation' / a.output_id
out.mkdir(parents=True, exist_ok=True)
fixed = out / 'fixed_positions.jsonl'
fixed.write_text(json.dumps({pdb.stem: {'A': [], 'B': [], 'C': [], 'D': a.fixed_positions}}) + '\n')
bias_file = out / 'bias_by_res.jsonl'
bias_by_chain = {ch: np.zeros((len(residues(model[ch])), len(ALPHABET)), dtype=float).tolist() for ch in ('A', 'B', 'C')}
bias_by_chain['D'] = bias.tolist()
bias_file.write_text(json.dumps({pdb.stem: bias_by_chain}) + '\n')
cmd = ['/home/<USER>/miniconda3/envs/proteinmpnn/bin/python', '/home/<USER>/ProteinMPNN/protein_mpnn_run.py', '--pdb_path', str(pdb), '--pdb_path_chains', 'D', '--fixed_positions_jsonl', str(fixed), '--bias_by_res_jsonl', str(bias_file), '--out_folder', str(out), '--num_seq_per_target', str(a.count), '--sampling_temp', '0.1 0.2', '--seed', str(a.seed), '--batch_size', '1', '--omit_AAs', 'CX', '--save_score', '1']
manifest = {'route': 'D6-focused charge-biased ProteinMPNN on a Boltz2 mutant pose; eight peptide-contact positions fixed', 'input_pdb': str(pdb), 'input_sha256': sha(pdb), 'fixed_positions_chain_D_1based': a.fixed_positions, 'peptide_interface_positions_biased': iface, 'D6_proximal_positions_biased': d6, 'fixed_positions_jsonl': str(fixed), 'fixed_positions_sha256': sha(fixed), 'bias_by_res_jsonl': str(bias_file), 'bias_by_res_sha256': sha(bias_file), 'seed': a.seed, 'num_seq_per_target': a.count, 'command': cmd, 'status': 'running', 'start_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
(out / 'run_manifest.json').write_text(json.dumps(manifest, indent=2))
env = os.environ.copy(); env['TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD'] = '1'
with (out / 'run.log').open('w') as log:
    proc = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, env=env)
manifest.update(status='complete' if proc.returncode == 0 else 'failed', exit_code=proc.returncode, end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
(out / 'run_manifest.json').write_text(json.dumps(manifest, indent=2))
if proc.returncode:
    raise SystemExit(f'MPNN failed; inspect {out / "run.log"}')
fa = next((out / 'seqs').glob('*.fa'))
lines = fa.read_text().splitlines(); rows = []; sample = 0
for i, header in enumerate(lines):
    if not header.startswith('>') or 'sample=' not in header:
        continue
    sample += 1; seq = lines[i + 1].strip(); match = re.search(r'(?<!global_)score=([0-9.]+)', header)
    if len(seq) != len(chain):
        raise ValueError(f'Unexpected sequence length {len(seq)} != {len(chain)}')
    rows.append({'candidate_id': f'{a.output_id}_s{sample:03d}', 'sequence': seq, 'length': len(seq), 'mpnn_score': match.group(1) if match else '', 'mpnn_header': header[1:], 'source_pdb': str(pdb), 'source_pdb_sha256': sha(pdb), 'sequence_sha256': hashlib.sha256(seq.encode()).hexdigest(), 'source_fasta': str(fa)})
dump_csv(ROOT / 'audit' / f'{a.output_id}_sequences.csv', rows)
print(json.dumps({'generated': len(rows), 'unique_sequences': len({r['sequence'] for r in rows}), 'biased_interface_positions': iface, 'biased_D6_positions': d6}, indent=2))

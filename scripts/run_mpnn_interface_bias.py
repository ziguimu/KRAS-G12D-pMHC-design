import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
from Bio.PDB import PDBParser

from audit_baseline import ROOT, atoms, dump_csv, residues, sha


ALPHABET = 'ACDEFGHIKLMNPQRSTVWYX'
PYTHON = '/home/<USER>/miniconda3/envs/proteinmpnn/bin/python'
MPNN = '/home/<USER>/ProteinMPNN/protein_mpnn_run.py'


def main():
    parser = argparse.ArgumentParser(description='Sample ProteinMPNN sequences with peptide-interface residue biases.')
    parser.add_argument('--backbone-id', default='design_4101')
    parser.add_argument('--run-id', default='rfd_micro_try1')
    parser.add_argument('--output-id')
    parser.add_argument('--input-pdb')
    parser.add_argument('--sequence-count', type=int, default=32)
    parser.add_argument('--seed', type=int, default=5501)
    parser.add_argument('--bias-profile', choices=('standard', 'charge-focused'), default='standard')
    args = parser.parse_args()

    pdb_path = Path(args.input_pdb) if args.input_pdb else ROOT / 'generation' / args.run_id / 'restored' / f'{args.backbone_id}_restored.pdb'
    if not pdb_path.is_absolute():
        pdb_path = ROOT / pdb_path
    output_id = args.output_id or f'{args.run_id}_{args.backbone_id}_interfacebias'
    out = ROOT / 'generation' / args.run_id / f'mpnn_{output_id}'
    out.mkdir(parents=True, exist_ok=True)
    bias_path = out / 'bias_by_res.jsonl'
    log_path = out / 'run.log'
    manifest_path = out / 'run_manifest.json'
    if manifest_path.exists():
        raise FileExistsError(manifest_path)

    model = PDBParser(QUIET=True).get_structure('complex', pdb_path)[0]
    peptide_atoms = atoms(model['C'])
    asp6 = [a for a in model['C'][6] if a.element not in ('H', 'D') and a.name in ('OD1', 'OD2')]
    binder_residues = residues(model['D'])
    bias_by_chain = {}
    interface_ids = []
    d6_ids = []
    for chain_id in ('A', 'B', 'C', 'D'):
        chain_res = residues(model[chain_id])
        chain_bias = np.zeros((len(chain_res), len(ALPHABET)), dtype=float)
        if chain_id == 'D':
            for i, residue in enumerate(chain_res):
                heavy = [a for a in residue if a.element not in ('H', 'D')]
                if not heavy or not peptide_atoms:
                    continue
                d_pep = min(float(np.linalg.norm(a.coord - b.coord)) for a in heavy for b in peptide_atoms)
                d_d6 = min(float(np.linalg.norm(a.coord - b.coord)) for a in heavy for b in asp6)
                if d_pep <= 9.0:
                    interface_ids.append(i + 1)
                    interface_bias = (
                        {'F': 2.0, 'Y': 2.0, 'W': 2.0, 'R': 1.2, 'K': 1.2,
                         'N': 0.8, 'Q': 0.8, 'S': 0.4, 'T': 0.4, 'A': -2.0}
                        if args.bias_profile == 'charge-focused'
                        else {'F': 1.2, 'Y': 1.2, 'W': 1.2, 'R': 0.7, 'K': 0.7,
                              'N': 0.4, 'Q': 0.4, 'S': 0.2, 'T': 0.2, 'A': -0.4}
                    )
                    for aa, value in interface_bias.items():
                        chain_bias[i, ALPHABET.index(aa)] = value
                if d_d6 <= 9.0:
                    d6_ids.append(i + 1)
                    d6_bias = (
                        {'R': 3.0, 'K': 2.5, 'H': 1.2, 'Y': 0.8, 'W': 0.5,
                         'D': -1.5, 'E': -1.5, 'A': -2.0}
                        if args.bias_profile == 'charge-focused'
                        else {'R': 1.5, 'K': 1.2, 'H': 0.8, 'Y': 0.7, 'W': 0.5}
                    )
                    for aa, value in d6_bias.items():
                        chain_bias[i, ALPHABET.index(aa)] = value
        bias_by_chain[chain_id] = chain_bias.tolist()

    parsed_name = pdb_path.stem
    bias_payload = {parsed_name: bias_by_chain}
    bias_path.write_text(json.dumps(bias_payload) + '\n')
    cmd = [
        PYTHON, MPNN,
        '--pdb_path', str(pdb_path), '--pdb_path_chains', 'D',
        '--out_folder', str(out), '--num_seq_per_target', str(args.sequence_count),
        '--sampling_temp', '0.1 0.2', '--seed', str(args.seed), '--batch_size', '1',
        '--omit_AAs', 'CX', '--save_score', '1', '--bias_by_res_jsonl', str(bias_path),
    ]
    manifest = {
        'route': 'interface-biased-inverse-folding',
        'bias_profile': args.bias_profile,
        'backbone_id': args.backbone_id,
        'output_id': output_id,
        'input_pdb': str(pdb_path),
        'input_sha256': sha(pdb_path),
        'bias_file': str(bias_path),
        'bias_file_sha256': sha(bias_path),
        'biased_binder_positions_1based': interface_ids,
        'D6_proximal_binder_positions_1based': d6_ids,
        'position_bias': ('strong aromatic/polar/basic enrichment on peptide-facing residues; stronger Arg/Lys enrichment and Asp/Glu/Ala penalty near mutant Asp6; strong Ala penalty on peptide-facing positions' if args.bias_profile == 'charge-focused' else 'aromatic/polar/basic enrichment on peptide-facing residues; additional Arg/Lys/His enrichment near mutant Asp6; mild Ala penalty on peptide-facing positions'),
        'known_binder_used_as_start': False,
        'seed': args.seed,
        'command': cmd,
        'start_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status': 'running',
    }
    manifest_path.write_text(json.dumps(manifest, indent=2))
    env = os.environ.copy()
    env['TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD'] = '1'
    with log_path.open('w') as log:
        proc = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, env=env)
    manifest.update(
        exit_code=proc.returncode,
        status='complete' if proc.returncode == 0 else 'failed',
        end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    )
    manifest_path.write_text(json.dumps(manifest, indent=2))
    if proc.returncode:
        raise RuntimeError(f'ProteinMPNN failed; see {log_path}')

    fasta_files = list((out / 'seqs').glob('*.fa'))
    if len(fasta_files) != 1:
        raise RuntimeError(f'Expected one FASTA, found {len(fasta_files)}')
    lines = fasta_files[0].read_text().splitlines()
    rows = []
    sample = 0
    import re
    for i, line in enumerate(lines):
        if line.startswith('>') and 'sample=' in line:
            sample += 1
            seq = lines[i + 1]
            score = re.search(r'(?<!global_)score=([\d.]+)', line)
            rows.append({
                'candidate_id': f'{args.run_id}_{args.backbone_id}_interfacebias_s{sample:03d}',
                'source_backbone': args.backbone_id,
                'sequence': seq,
                'length': len(seq),
                'mpnn_score': score.group(1) if score else '',
                'status': 'generated_unpredicted',
                'mpnn_header': line[1:],
                'sequence_sha256': hashlib.sha256(seq.encode()).hexdigest(),
                'source_fasta': str(fasta_files[0]),
                'source_backbone_pdb': str(pdb_path),
            })
    dump_csv(ROOT / 'audit' / f'{output_id}_sequences.csv', rows)
    print(json.dumps({
        'generated': len(rows),
        'unique_sequences': len({r['sequence'] for r in rows}),
        'peptide_interface_positions_biased': interface_ids,
        'D6_proximal_positions_biased': d6_ids,
    }, indent=2))
    sys.exit(proc.returncode)


if __name__ == '__main__':
    main()

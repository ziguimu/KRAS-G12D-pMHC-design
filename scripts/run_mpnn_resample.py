import argparse, csv, datetime, hashlib, json, os, re, subprocess
from pathlib import Path
from audit_baseline import ROOT, dump_csv, sha

p = argparse.ArgumentParser()
p.add_argument('backbone_run')
p.add_argument('--batch-tag', required=True)
p.add_argument('--sequences-per-temperature', type=int, default=16)
p.add_argument('--seed-start', type=int, default=3200)
p.add_argument('--backbones', nargs='*', default=None)
a = p.parse_args()
rows = list(csv.DictReader((ROOT / 'audit' / f'{a.backbone_run}_backbones.csv').open()))
ledger = []
for i, r in enumerate(rows):
    if r['status'] != 'eligible_for_mpnn':
        continue
    bid = r['backbone_id']
    if a.backbones and bid not in a.backbones:
        continue
    inp = Path(r['pdb'])
    out = ROOT / 'generation' / a.backbone_run / f'mpnn_{a.batch_tag}' / bid
    out.mkdir(parents=True, exist_ok=True)
    seed = a.seed_start + i
    cmd = [
        '/home/<USER>/miniconda3/envs/proteinmpnn/bin/python',
        '/home/<USER>/ProteinMPNN/protein_mpnn_run.py',
        '--pdb_path', str(inp), '--pdb_path_chains', 'D', '--out_folder', str(out),
        '--num_seq_per_target', str(a.sequences_per_temperature), '--sampling_temp', '0.1 0.2',
        '--seed', str(seed), '--batch_size', '1', '--omit_AAs', 'CX', '--save_score', '1',
    ]
    manifest = {
        'command': cmd, 'input_sha256': sha(inp),
        'start_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status': 'running', 'seed': seed, 'fixed_chains': ['A', 'B', 'C'],
        'designed_chains': ['D'], 'no_residue_bias': True,
        'resampling_of_existing_backbone': True,
    }
    mp = out / 'run_manifest.json'
    mp.write_text(json.dumps(manifest, indent=2))
    env = os.environ.copy(); env['TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD'] = '1'
    with (out / 'run.log').open('w') as log:
        proc = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, env=env)
    manifest.update(exit_code=proc.returncode, status='complete' if proc.returncode == 0 else 'failed', end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    mp.write_text(json.dumps(manifest, indent=2))
    if proc.returncode:
        raise RuntimeError(f'MPNN failed {bid}; see {out}/run.log')
    fas = list((out / 'seqs').glob('*.fa'))
    assert len(fas) == 1
    lines = fas[0].read_text().splitlines(); sample = 0
    for j, line in enumerate(lines):
        if line.startswith('>') and 'sample=' in line:
            sample += 1; sequence = lines[j + 1]
            assert len(sequence) == int(r['binder_length']) and '/' not in sequence
            match = re.search(r'(?<!global_)score=([\d.]+)', line)
            ledger.append({
                'candidate_id': f'{a.backbone_run}_{a.batch_tag}_{bid}_s{sample:03d}',
                'source_backbone': bid, 'sequence': sequence, 'length': len(sequence),
                'mpnn_score': match.group(1) if match else '',
                'status': 'generated_unpredicted', 'mpnn_header': line[1:],
                'sequence_sha256': hashlib.sha256(sequence.encode()).hexdigest(),
                'source_fasta': str(fas[0]), 'source_backbone_pdb': str(inp),
                'batch_tag': a.batch_tag, 'mpnn_seed': seed,
            })
dump_csv(ROOT / 'audit' / f'{a.backbone_run}_{a.batch_tag}_mpnn_sequences.csv', ledger)
print(json.dumps({
    'generated': len(ledger), 'unique_sequences': len({r['sequence'] for r in ledger}),
    'backbones': len({r['source_backbone'] for r in ledger}), 'batch_tag': a.batch_tag,
}, indent=2))

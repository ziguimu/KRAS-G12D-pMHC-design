import argparse
import datetime
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RFD_REPO = Path('/home/<USER>/RFdiffusion/env/RFdiffusion-main')
PYTHON = '/home/<USER>/miniconda3/envs/rfdiff/bin/python'


def main():
    parser = argparse.ArgumentParser(description='Generate de novo compact pMHC binders with RFdiffusion.')
    parser.add_argument('--count', type=int, default=4)
    parser.add_argument('--start', type=int, default=4100)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--binder-length', default='40-55')
    parser.add_argument('--hotspots', default='C5,C6,C7')
    args = parser.parse_args()

    out = ROOT / 'generation' / args.run_id
    out.mkdir(parents=True, exist_ok=True)
    manifest_path = ROOT / 'logs' / f'{args.run_id}.json'
    if manifest_path.exists():
        raise FileExistsError(manifest_path)

    cmd = [
        PYTHON, str(RFD_REPO / 'scripts/run_inference.py'),
        f'inference.input_pdb={ROOT}/inputs/target_7OW6_native_observed.pdb',
        f'inference.output_prefix={out}/design',
        f'inference.num_designs={args.count}',
        f'inference.design_startnum={args.start}',
        'inference.deterministic=True',
        'inference.write_trajectory=False',
        f'contigmap.contigs=[A1-275/0 B1-99/0 C1-10/0 {args.binder_length}]',
        f'ppi.hotspot_res=[{args.hotspots}]',
        'denoiser.noise_scale_ca=0.5',
        'denoiser.noise_scale_frame=0.5',
    ]
    record = {
        'route': 'de_novo_compact_binder_backbones',
        'binder_length': args.binder_length,
        'hotspots': args.hotspots.split(','),
        'known_binder_used_as_start': False,
        'command': cmd,
        'cwd': str(RFD_REPO),
        'start_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status': 'running',
        'seeds': list(range(args.start, args.start + args.count)),
    }
    manifest_path.write_text(json.dumps(record, indent=2))
    env = os.environ.copy()
    env['TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD'] = '1'
    log_path = ROOT / 'logs' / f'{args.run_id}.log'
    with log_path.open('w') as log:
        result = subprocess.run(cmd, cwd=RFD_REPO, stdout=log, stderr=subprocess.STDOUT, env=env)
    record.update(
        exit_code=result.returncode,
        end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        status='process_complete' if result.returncode == 0 else 'failed',
        outputs=[str(p) for p in out.glob('*.pdb')],
    )
    manifest_path.write_text(json.dumps(record, indent=2))
    print(json.dumps(record, indent=2))
    sys.exit(result.returncode)


if __name__ == '__main__':
    main()

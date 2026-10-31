from pathlib import Path
import argparse,json,subprocess,datetime,sys,yaml
from audit_baseline import ROOT,sha
p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('--run-id',required=True);p.add_argument('--seed',type=int,default=15);p.add_argument('--msa',type=int,default=64);a=p.parse_args()
inp=Path(a.input); out=ROOT/'predictions'/a.run_id; logs=ROOT/'logs';logs.mkdir(exist_ok=True)
cmd=['/home/<USER>/miniconda3/envs/boltz/bin/boltz','predict',str(inp),'--out_dir',str(out),'--model','boltz2','--recycling_steps','3','--sampling_steps','200','--diffusion_samples','1','--max_parallel_samples','1','--seed',str(a.seed),'--num_workers','0','--max_msa_seqs',str(a.msa),'--num_subsampled_msa',str(a.msa),'--output_format','pdb']
files=[inp] if inp.is_file() else sorted(inp.glob('*.yaml'))
dependencies={}
for f in files:
    dependencies[str(f)]=sha(f)
    for ent in yaml.safe_load(f.read_text())['sequences']:
        msa=ent['protein'].get('msa')
        if msa and msa!='empty' and msa not in dependencies:dependencies[msa]=sha(msa)
record={'command':cmd,'input_sha256':sha(inp) if inp.is_file() else None,'input_dependencies_sha256':dependencies,'start_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'running','actual_gpu':'NVIDIA GeForce RTX 5070 Laptop GPU; driver nvidia-smi; printed A6000 is kernel fallback metadata'}
manifest=logs/f'{a.run_id}.json'
if manifest.exists():raise FileExistsError(manifest)
manifest.write_text(json.dumps(record,indent=2))
with (logs/f'{a.run_id}.log').open('w') as log:r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
record.update(status='process_complete' if r.returncode==0 else 'process_failed',exit_code=r.returncode,end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),outputs=[str(p) for p in out.rglob('confidence_*.json')])
manifest.write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2));sys.exit(r.returncode)

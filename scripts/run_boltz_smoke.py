from pathlib import Path
import json,subprocess,datetime,sys,time
from audit_baseline import ROOT,sha
logs=ROOT/'logs';logs.mkdir(exist_ok=True)
inp=ROOT/'inputs/baseline_03_mutant.yaml'
cmd=['/home/<USER>/miniconda3/envs/boltz/bin/boltz','predict',str(inp),'--out_dir',str(ROOT/'smoke/boltz_baseline03'),'--model','boltz2','--recycling_steps','3','--sampling_steps','200','--diffusion_samples','1','--max_parallel_samples','1','--seed','15','--num_workers','0','--max_msa_seqs','64','--num_subsampled_msa','64','--output_format','pdb']
record={'purpose':'full assay construct GPU feasibility; not final ranking','command':cmd,'input_sha256':sha(inp),'start_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'running'}
manifest=logs/'boltz_smoke_manifest.json';manifest.write_text(json.dumps(record,indent=2))
with (logs/'boltz_smoke.log').open('w') as log:
    r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
record.update(status='process_complete' if r.returncode==0 else 'process_failed',exit_code=r.returncode,end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),outputs=[str(p) for p in (ROOT/'smoke').rglob('confidence_*.json')])
manifest.write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2));sys.exit(r.returncode)

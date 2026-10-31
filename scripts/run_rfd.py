import argparse,json,subprocess,datetime,os,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--count',type=int,default=1);p.add_argument('--start',type=int,default=1000);p.add_argument('--run-id',required=True);p.add_argument('--hotspots',default='C4,C5,C7,C8');a=p.parse_args()
ROOT=Path(__file__).resolve().parents[1]
repo=Path('/home/<USER>/RFdiffusion/env/RFdiffusion-main')
out=ROOT/'generation'/a.run_id;out.mkdir(parents=True,exist_ok=True)
cmd=['/home/<USER>/miniconda3/envs/rfdiff/bin/python',str(repo/'scripts/run_inference.py'),f'inference.input_pdb={ROOT}/inputs/target_7OW6_native_observed.pdb',f'inference.output_prefix={out}/design',f'inference.num_designs={a.count}',f'inference.design_startnum={a.start}','inference.deterministic=True','inference.write_trajectory=False','contigmap.contigs=[A1-275/0 B1-99/0 C1-10/0 80-100]',f'ppi.hotspot_res=[{a.hotspots}]','denoiser.noise_scale_ca=0.5','denoiser.noise_scale_frame=0.5']
env=os.environ.copy();env['TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD']='1'
record={'command':cmd,'cwd':str(repo),'start_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'running','seeds':list(range(a.start,a.start+a.count)),'known_binder_used_as_start':False}
manifest=ROOT/'logs'/f'{a.run_id}.json'
if manifest.exists():raise FileExistsError(manifest)
manifest.write_text(json.dumps(record,indent=2))
with (ROOT/'logs'/f'{a.run_id}.log').open('w') as log:r=subprocess.run(cmd,cwd=repo,stdout=log,stderr=subprocess.STDOUT,env=env)
record.update(exit_code=r.returncode,end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='process_complete' if r.returncode==0 else 'failed',outputs=[str(x) for x in out.glob('*.pdb')])
manifest.write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2));sys.exit(r.returncode)

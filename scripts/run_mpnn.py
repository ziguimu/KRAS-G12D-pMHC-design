import argparse,json,subprocess,datetime,os,sys,csv,re,hashlib
from pathlib import Path
from audit_baseline import ROOT,dump_csv,sha
p=argparse.ArgumentParser();p.add_argument('backbone_run');p.add_argument('--sequences',type=int,default=8);a=p.parse_args()
rows=list(csv.DictReader((ROOT/'audit'/f'{a.backbone_run}_backbones.csv').open()))
ledger=[]
for i,r in enumerate(rows):
    if r['status']!='eligible_for_mpnn':continue
    bid=r['backbone_id'];inp=Path(r['pdb']);out=ROOT/'generation'/a.backbone_run/'mpnn'/bid;out.mkdir(parents=True,exist_ok=True)
    cmd=['/home/<USER>/miniconda3/envs/proteinmpnn/bin/python','/home/<USER>/ProteinMPNN/protein_mpnn_run.py','--pdb_path',str(inp),'--pdb_path_chains','D','--out_folder',str(out),'--num_seq_per_target',str(a.sequences),'--sampling_temp','0.1 0.2','--seed',str(2100+i),'--batch_size','1','--omit_AAs','CX','--save_score','1']
    manifest={'command':cmd,'input_sha256':sha(inp),'start_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'running','fixed_chains':['A','B','C'],'designed_chains':['D'],'no_residue_bias':True}
    mp=out/'run_manifest.json';mp.write_text(json.dumps(manifest,indent=2))
    env=os.environ.copy();env['TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD']='1'
    with (out/'run.log').open('w') as log:proc=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,env=env)
    manifest.update(exit_code=proc.returncode,status='complete' if proc.returncode==0 else 'failed',end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());mp.write_text(json.dumps(manifest,indent=2))
    if proc.returncode:raise RuntimeError(f'MPNN failed {bid}; see {out}/run.log')
    fas=list((out/'seqs').glob('*.fa'));assert len(fas)==1
    lines=fas[0].read_text().splitlines();sample=0
    for j,line in enumerate(lines):
        if line.startswith('>') and 'sample=' in line:
            sample+=1;s=lines[j+1]
            assert len(s)==int(r['binder_length']) and '/' not in s
            match=re.search(r'(?<!global_)score=([\d.]+)',line)
            ledger.append({'candidate_id':f'{a.backbone_run}_{bid}_s{sample:02d}','source_backbone':bid,'sequence':s,'length':len(s),'mpnn_score':match.group(1) if match else '', 'status':'generated_unpredicted','mpnn_header':line[1:],'sequence_sha256':hashlib.sha256(s.encode()).hexdigest(),'source_fasta':str(fas[0]),'source_backbone_pdb':str(inp)})
dump_csv(ROOT/'audit'/f'{a.backbone_run}_mpnn_sequences.csv',ledger)
print(json.dumps({'generated':len(ledger),'unique_sequences':len({r['sequence'] for r in ledger}),'backbones':len({r['source_backbone'] for r in ledger})},indent=2))

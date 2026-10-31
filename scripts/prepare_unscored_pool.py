"""Recover unused original de novo sequences without changing any sequence."""
import csv,json,yaml,hashlib,math
from pathlib import Path
from collections import Counter
from audit_baseline import ROOT,OLD,HLA,B2M,dump_csv,sha
src=OLD/'proteinmpnn_round1/pooled_candidates/all_100_sequences.csv'
allrows=list(csv.DictReader(src.open()))
baseline={r['sequence'] for r in csv.DictReader((ROOT/'audit/legacy_sequences.csv').open())}
prior_scored={}
f=OLD/'proteinmpnn_round1/pooled_candidates/structure_prediction_shortlist_v1.fasta'
lines=f.read_text().splitlines()
for i,line in enumerate(lines):
    if line.startswith('>'):prior_scored[lines[i+1]]=line[1:].split()[0]
out=ROOT/'inputs/recovered_de_novo_pool';out.mkdir(exist_ok=True)
ledger=[]
for i,r in enumerate(allrows,1):
    s=r['sequence']; counts=Counter(s)
    cid=f'recovered_{i:03d}'
    row={'candidate_id':cid,'legacy_source_id':r['candidate_id'],'source_backbone':r['source_backbone'],'source_sample':r['sample'],'sequence':s,'length':len(s),'mpnn_score':r['score'],'sequence_sha256':hashlib.sha256(s.encode()).hexdigest(),'old_boltz_id':prior_scored.get(s,''),'is_baseline':s in baseline,'status':'legacy_baseline' if s in baseline else 'awaiting_control_calibration','entropy_bits':-sum(n/len(s)*math.log2(n/len(s)) for n in counts.values()),'A_fraction':s.count('A')/len(s),'input_source':str(src),'source_sha256':sha(src)}
    ledger.append(row)
    if s in baseline:continue
    entries=[]
    for ch,seq in {'A':HLA,'B':B2M,'C':'VVVGADGVGK','D':s}.items():
        entries.append({'protein':{'id':ch,'sequence':seq,'msa':str(ROOT/'inputs/msa'/f'{ch}.csv') if ch in ['A','B'] else 'empty'}})
    (out/f'{cid}_mutant.yaml').write_text(yaml.safe_dump({'version':1,'sequences':entries},sort_keys=False))
dump_csv(ROOT/'audit/recovered_pool_ledger.csv',ledger)
print(json.dumps({'total':len(ledger),'unique_sequences':len({x['sequence'] for x in ledger}),'source_backbones':len({x['source_backbone'] for x in ledger}),'baselines':len(baseline),'nonbaseline_sequences':len(ledger)-len(baseline),'never_Boltz_scored':sum(not x['old_boltz_id'] for x in ledger)},indent=2))

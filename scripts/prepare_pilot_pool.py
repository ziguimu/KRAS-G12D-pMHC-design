import csv,json,shutil
from audit_baseline import ROOT,dump_csv
rows=list(csv.DictReader((ROOT/'audit/recovered_pool_ledger.csv').open()))
# A fixed, inexpensive pilot prioritization only. No claim that MPNN is affinity.
unscored=[r for r in rows if not r['old_boltz_id']]
selected=sorted(unscored,key=lambda r:(float(r['mpnn_score']),r['candidate_id']))[:16]
out=ROOT/'inputs/pilot_recovered';out.mkdir(exist_ok=True)
for r in selected:
    f=ROOT/'inputs/recovered_de_novo_pool'/f"{r['candidate_id']}_mutant.yaml"
    shutil.copyfile(f,out/f.name)
    r['pilot_reason']='16 lowest original ProteinMPNN scores in pooled 85 unscored sequences; no backbone quotas; not an affinity ranking'
dump_csv(ROOT/'audit/pilot_recovered_selection.csv',selected)
print(json.dumps({'pilot_sequences':len(selected),'source_backbones':sorted({r['source_backbone'] for r in selected})}))

from pathlib import Path
import csv,json,yaml
from audit_baseline import ROOT,OLD,HLA,B2M,sha

msa=ROOT/'inputs/msa'; msa.mkdir(exist_ok=True)
base=OLD/'boltz_batch15/outputs/PMHC_candidate_03/boltz_results_PMHC_candidate_03/msa'
manifest=[]
for chain,idx in [('A',0),('B',1)]:
    src=base/f'PMHC_candidate_03_{idx}.csv'
    rows=list(csv.DictReader(src.open()))
    if chain=='A':
        for r in rows:
            s=r['sequence']
            # CSV MSA contains aligned residues with optional lowercase insertions.
            aligned=[x for x in s if not x.islower()]
            assert len(aligned)==276,(len(aligned),s)
            # 7OW6 _struct_ref_seq_dif identifies P276 as an expression tag.
            # Drop that non-native column; append the six native missing positions.
            last=len(s)-1
            while s[last].islower(): last-=1
            r['sequence']=s[:last]+'------'
        rows[0]['sequence']=HLA
    else:
        assert rows[0]['sequence']==B2M
    dst=msa/f'{chain}.csv'
    with dst.open('w',newline='') as f:
        w=csv.DictWriter(f,['key','sequence']);w.writeheader();w.writerows(rows)
    manifest.append({'source':str(src),'source_sha256':sha(src),'output':str(dst),'sha256':sha(dst),'rows':len(rows),'transformation':'A residues 1:275 unchanged; expression-tag P276 column removed; official LSSQPT appended to query and six gaps appended to homologs' if chain=='A' else 'unchanged'})
for p in (ROOT/'inputs').glob('baseline_*.yaml'):
    y=yaml.safe_load(p.read_text())
    for entry in y['sequences']:
        protein=entry['protein']
        if protein['id'] in ['A','B']:protein['msa']=str(msa/f"{protein['id']}.csv")
    p.write_text(yaml.safe_dump(y,sort_keys=False))
(msa/'manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2))

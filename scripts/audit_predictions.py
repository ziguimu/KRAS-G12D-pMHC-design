import argparse,json,yaml
from pathlib import Path
from Bio.PDB import MMCIFParser
from audit_baseline import ROOT,metrics,seq,ca,fit,rms,dump_csv

p=argparse.ArgumentParser();p.add_argument('--run-id',required=True);p.add_argument('--inputs',required=True);p.add_argument('--prefix',default='');a=p.parse_args()
inputs=Path(a.inputs); run=ROOT/'predictions'/a.run_id
refpaths={'mutant':ROOT/'inputs/source_7ow6.cif','WT':ROOT/'inputs/source_7ow5.cif'}
refs={k:MMCIFParser(QUIET=True).get_structure(k,v)[0] for k,v in refpaths.items()}
rows=[];errors=[]
for yp in sorted(inputs.glob(a.prefix+'*.yaml')):
    inp=yaml.safe_load(yp.read_text());expected={e['protein']['id']:e['protein']['sequence'] for e in inp['sequences']}
    name=yp.stem
    # Infer assay condition from the input sequence, not the final token of the
    # filename: one-condition screening files such as recovered_034.yaml end
    # in an index, while panel files end in _mutant/_WT/_apo.
    peptide=expected.get('C','')
    if peptide=='VVVGADGVGK': condition='mutant'
    elif peptide=='VVVGAGGVGK': condition='WT'
    elif peptide=='': condition='apo'
    else: condition='unknown'
    candidate_id=name
    for suffix in ('_mutant','_WT','_apo'):
        if name.endswith(suffix):
            candidate_id=name[:-len(suffix)]
            break
    pdbs=list(run.rglob(f'{name}_model_0.pdb'));confs=list(run.rglob(f'confidence_{name}_model_0.json'))
    row={'candidate_id':candidate_id,'condition':condition,'prediction_id':name,'status':'prediction_failed_or_missing','sequence':expected['D'],'length':len(expected['D']),'run_id':a.run_id}
    if len(pdbs)!=1 or len(confs)!=1:
        rows.append(row);continue
    try:
        m,s=metrics(pdbs[0],confs[0],expected)
        row.update(m,status='output_audited',pdb=str(pdbs[0]),confidence=str(confs[0]))
        if condition in refs:
            ref=refs[condition];rot,trans=fit(ca(s['A'])[:180],ca(ref['A'])[:180])
            row['target_HLA_groove_CA_RMSD_to_crystal_A']=rms(ca(s['A'])[:180]@rot+trans,ca(ref['A'])[:180])
            row['target_peptide_CA_RMSD_to_crystal_after_HLA_fit_A']=rms(ca(s['C'])@rot+trans,ca(ref['C']))
    except Exception as e:
        row.update(status='audit_failed',error=str(e));errors.append(row)
    rows.append(row)
dump_csv(ROOT/'audit'/f'{a.run_id}_metrics.csv',rows)
print(json.dumps({'rows':len(rows),'audited':sum(x['status']=='output_audited' for x in rows),'failures':sum(x['status']!='output_audited' for x in rows),'errors':errors,'summary':[{k:r.get(k) for k in ['candidate_id','condition','iptm','binder_peptide_iptm_min','binder_HLA_iptm_min','peptide_atom_pairs_lt4A','all_target_pairs_lt2A']} for r in rows]},indent=2))

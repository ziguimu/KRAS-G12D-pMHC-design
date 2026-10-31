import csv,json,yaml,hashlib
from pathlib import Path
from audit_baseline import ROOT,B2M,HLA,PEPTIDES,dump_csv,sha

seqrows=list(csv.DictReader((ROOT/'audit/rfd_smoke_mpnn_sequences.csv').open()))
recovered=list(csv.DictReader((ROOT/'audit/pilot_recovered_selection.csv').open()))
rows=[]
for r in seqrows:
    rows.append({'candidate_id':r['candidate_id'],'sequence':r['sequence'],'length':r['length'],'sequence_source':'new_RFdiffusion_ProteinMPNN','source_backbone':r['source_backbone'],'mpnn_score':r['mpnn_score'],'source_file':r['source_fasta'],'sequence_sha256':r['sequence_sha256']})
for r in recovered:
    rows.append({'candidate_id':r['candidate_id'],'sequence':r['sequence'],'length':r['length'],'sequence_source':'previously_unscored_original_de_novo_pool','source_backbone':r['source_backbone'],'mpnn_score':r['mpnn_score'],'source_file':str(ROOT/'inputs/recovered_de_novo_pool'/f"{r['candidate_id']}_mutant.yaml"),'sequence_sha256':r['sequence_sha256']})
assert len({r['sequence'] for r in rows})==len(rows)
out=ROOT/'inputs/new_candidate_panel';out.mkdir(exist_ok=True)
for r in rows:
    for condition,peptide in PEPTIDES.items():
        entries=[]
        for chain,seq in {'A':HLA,'B':B2M,'C':peptide,'D':r['sequence']}.items():
            entries.append({'protein':{'id':chain,'sequence':seq,'msa':str(ROOT/'inputs/msa'/f'{chain}.csv') if chain in ('A','B') else 'empty'}})
        dst=out/f"{r['candidate_id']}_{condition}.yaml"
        dst.write_text(yaml.safe_dump({'version':1,'sequences':entries},sort_keys=False))
        r[f'{condition}_input']=str(dst);r[f'{condition}_input_sha256']=sha(dst)
dump_csv(ROOT/'audit/new_candidate_panel_ledger.csv',rows)
print(json.dumps({'sequences':len(rows),'new_backbone_design_sequences':len(seqrows),'recovered_previous_pool_sequences':len(recovered),'all3_conditions_prepared':len(rows)*3,'unique_sequences':len({r['sequence'] for r in rows})},indent=2))

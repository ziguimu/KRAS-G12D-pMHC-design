"""Recompute legacy structural descriptors; never infer experimental binding."""
from pathlib import Path
import csv, json, hashlib
import numpy as np
import yaml
from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1
from Bio.Align import PairwiseAligner

ROOT = Path(__file__).resolve().parents[1]
OLD = Path('<LEGACY_PMHC_ROOT>/rfdiffusion_G12D')
HLA = 'GSHSMRYFYTSVSRPGRGEPRFIAVGYVDDTQFVRFDSDAASQRMEPRAPWIEQEGPEYWDQETRNVKAQSQTDRVDLGTLRGYYNQSEDGSHTIQIMYGCDVGPDGRFLRGYRQDAYDGKDYIALNEDLRSWTAADMAAQITKRKWEAAHAAEQQRAYLEGRCVEWLRRYLENGKETLQRTDPPKTHMTHHPISDHEATLRCWALGFYPAEITLTWQRDGEDQTQDTELVETRPAGDGTFQKWAAVVVPSGEEQRYTCHVQHEGLPKPLTLRWELSSQPT'
B2M = 'IQRTPKIQVYSRHPAENGKSNFLNCYVSGFHPSDIEVDLLKNGERIEKVEHSDLSFSKDWSFYLLYYTEFTPTEKDEYACRVNHVTLSQPKIVKWDRDM'
PEPTIDES = {'mutant':'VVVGADGVGK', 'WT':'VVVGAGGVGK'}
AA = set('ACDEFGHIKLMNPQRSTVWY')

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def dump_csv(path, rows):
    if not rows:
        return
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with Path(path).open('w',newline='') as f:
        w=csv.DictWriter(f,fields); w.writeheader(); w.writerows(rows)

def residues(ch):
    return [r for r in ch if r.id[0]==' ']

def seq(ch):
    return ''.join(seq1(r.resname) for r in residues(ch))

def atoms(ch):
    return [a for r in residues(ch) for a in r if a.element not in ('H','D') and a.altloc in (' ','A')]

def dist(a,b):
    return np.linalg.norm(np.array([x.coord for x in a])[:,None,:]-np.array([x.coord for x in b])[None,:,:],axis=2)

def metrics(pdb, confidence, expected):
    s=PDBParser(QUIET=True).get_structure('x',pdb)[0]
    observed={c.id:seq(c) for c in s}
    if observed!=expected:
        raise ValueError(f'Chain sequence mismatch: {pdb}: {observed}')
    conf=json.loads(Path(confidence).read_text())
    row={k:conf[k] for k in ['confidence_score','iptm','ptm','complex_plddt','complex_iplddt','complex_pde','complex_ipde']}
    chain_idx={ch:str(i) for i,ch in enumerate(expected)}
    binder_idx=chain_idx['D']
    row['binder_ptm']=conf['chains_ptm'][binder_idx]
    for target,ch in [('HLA','A'),('b2m','B'),('peptide','C')]:
        if ch not in expected:continue
        idx=chain_idx[ch]
        forward=conf['pair_chains_iptm'][binder_idx][idx]
        reverse=conf['pair_chains_iptm'][idx][binder_idx]
        row[f'binder_{target}_iptm_min']=min(forward,reverse)
        row[f'binder_{target}_iptm_mean']=(forward+reverse)/2
    da=atoms(s['D'])
    for chain,label in [('A','HLA'),('B','b2m'),('C','peptide')]:
        if chain not in s:continue
        ta=atoms(s[chain]); ds=dist(da,ta); ii,jj=np.where(ds<4.)
        row[f'{label}_atom_pairs_lt4A']=len(ii)
        row[f'{label}_residue_pairs_lt4A']=len({(da[i].parent.id,ta[j].parent.id) for i,j in zip(ii,jj)})
        row[f'{label}_positions_lt4A']=len({ta[j].parent.id for j in jj})
        row[f'{label}_min_A']=float(ds.min())
        row[f'{label}_pairs_lt2A']=int((ds<2.).sum())
    target_atoms=atoms(s['A'])+atoms(s['B'])+(atoms(s['C']) if 'C' in s else [])
    row['all_target_pairs_lt2A']=int((dist(da,target_atoms)<2.).sum())
    site=residues(s['C'])[5] if 'C' in s else []
    row['site_resname']=site.resname if site else ''
    sc=[a for a in site if a.name not in ('N','CA','C','O','OXT') and a.element!='H']
    od=[a for a in site if a.name in ('OD1','OD2')]
    row['site_sidechain_min_A']=float(dist(da,sc).min()) if sc else ''
    row['Asp6_OD_min_A']=float(dist(da,od).min()) if od else ''
    polar=[a for a in da if a.element in ('N','O') and a.name not in ('N','CA','C','O','OXT')]
    row['Asp6_OD_binder_polar_sidechain_min_A']=float(dist(polar,od).min()) if od and polar else ''
    row['binder_mean_pdb_bfactor']=float(np.mean([a.bfactor for a in s['D'].get_atoms()]))
    return row,s

def fit(moving,fixed):
    cm=moving.mean(0); cf=fixed.mean(0)
    u,_,vt=np.linalg.svd((moving-cm).T@(fixed-cf))
    d=np.eye(3); d[-1,-1]=np.linalg.det(u@vt)
    rot=u@d@vt
    return rot,cf-cm@rot

def ca(ch):
    return np.array([r['CA'].coord for r in residues(ch)])

def rms(a,b):
    return float(np.sqrt(np.mean(np.sum((a-b)**2,axis=1))))

def main():
    out=ROOT/'audit'; out.mkdir(parents=True,exist_ok=True)
    inputs=ROOT/'inputs'; inputs.mkdir(exist_ok=True)
    rows=[]; manifests=[]; aligned=[]; sequences=[]; structs={}
    for cid in ['03','05','12','14']:
        y=OLD/'boltz_batch15/inputs'/f'PMHC_candidate_{cid}.yaml'
        inp=yaml.safe_load(y.read_text())
        expected={e['protein']['id']:e['protein']['sequence'] for e in inp['sequences']}
        assert expected['B']==B2M and expected['C']==PEPTIDES['mutant']
        assert set(expected['D'])<=AA
        sequences.append({'candidate':cid,'sequence':expected['D'],'length':len(expected['D']),'input_yaml':str(y),'sha256':sha(y)})
        for condition in ['mutant','WT']:
            name=f'PMHC_candidate_{cid}'+('_WT' if condition=='WT' else '')
            base=(OLD/'boltz_batch15/outputs'/name if condition=='mutant' else OLD/'boltz_wt_batch4'/f'candidate_{cid}')/f'boltz_results_{name}'/'predictions'/name
            pdb=base/f'{name}_model_0.pdb'; conf=base/f'confidence_{name}_model_0.json'
            expected['C']=PEPTIDES[condition]
            row,s=metrics(pdb,conf,expected)
            row={'candidate':cid,'condition':condition,**row,'pdb':str(pdb),'confidence':str(conf)}
            rows.append(row); structs[(cid,condition)]=s
            for path in [y,pdb,conf]:
                manifests.append({'path':str(path),'size':path.stat().st_size,'sha256':sha(path)})
        mutant=structs[(cid,'mutant')]; wt=structs[(cid,'WT')]
        rot,trans=fit(ca(wt['A'])[:180],ca(mutant['A'])[:180])
        aligned.append({'candidate':cid,'HLA_groove_CA_RMSD_A':rms(ca(wt['A'])[:180]@rot+trans,ca(mutant['A'])[:180]),'peptide_CA_RMSD_after_HLA_fit_A':rms(ca(wt['C'])@rot+trans,ca(mutant['C'])),'binder_CA_RMSD_after_HLA_fit_A':rms(ca(wt['D'])@rot+trans,ca(mutant['D']))})
        for condition in ['mutant','WT','apo']:
            entries=[]
            for ch,sequence in {'A':HLA,'B':B2M,'C':PEPTIDES.get(condition),'D':expected['D']}.items():
                if sequence is not None:
                    entries.append({'protein':{'id':ch,'sequence':sequence,'msa':'empty'}})
            (inputs/f'baseline_{cid}_{condition}.yaml').write_text(yaml.safe_dump({'version':1,'sequences':entries},sort_keys=False))
    assert len(HLA)==281 and len(B2M)==99
    dump_csv(out/'legacy_metrics_recomputed.csv',rows)
    dump_csv(out/'legacy_mutant_WT_pose_comparison.csv',aligned)
    dump_csv(out/'legacy_sequences.csv',sequences)
    dump_csv(out/'legacy_input_hashes.csv',list({r['path']:r for r in manifests}.values()))
    old_hla=expected['A']; a=PairwiseAligner(); a.mode='global'; a.match_score=2; a.mismatch_score=-2; a.open_gap_score=-5; a.extend_gap_score=-.5
    alignment=str(a.align(HLA,old_hla)[0])
    (out/'construct_alignment.txt').write_text(f'Official HLA length: {len(HLA)}\nLegacy HLA length: {len(old_hla)}\n{alignment}')
    archived=list(csv.DictReader((OLD/'mutant_wt_interface_audit/mutant_wt_metrics_v1.csv').open()))
    for r in rows:
        prior=next(x for x in archived if x['candidate']==r['candidate'] and x['condition']==r['condition'])
        for k,pk in [('peptide_atom_pairs_lt4A','D_C_atom_pairs_lt4A'),('HLA_atom_pairs_lt4A','D_A_atom_pairs_lt4A')]:
            assert r[k]==int(prior[pk]),(r['candidate'],k,r[k],prior[pk])
    print(json.dumps({'recomputed_rows':len(rows),'legacy_contact_counts_match':True,'construct_alignment':alignment,'summary':[{k:r[k] for k in ['candidate','condition','iptm','binder_peptide_iptm_min','binder_HLA_iptm_min','peptide_atom_pairs_lt4A','Asp6_OD_min_A','all_target_pairs_lt2A']} for r in rows],'pose_comparison':aligned},indent=2))

if __name__=='__main__':
    main()

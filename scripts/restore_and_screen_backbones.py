import argparse,pickle,json,copy
from pathlib import Path
import numpy as np
from Bio.PDB import PDBParser,PDBIO
from Bio.PDB.Chain import Chain
from audit_baseline import ROOT,residues,atoms,fit,dist,dump_csv,sha
p=argparse.ArgumentParser();p.add_argument('run_id');p.add_argument('--min-length',type=int,default=80);p.add_argument('--max-length',type=int,default=100);a=p.parse_args()
native=PDBParser(QUIET=True).get_structure('native',ROOT/'inputs/target_7OW6_native_observed.pdb')[0]
out=ROOT/'generation'/a.run_id/'restored';out.mkdir(exist_ok=True)
rows=[]
for fp in sorted((ROOT/'generation'/a.run_id).glob('design_*.pdb')):
    trb=fp.with_suffix('.trb');meta=pickle.load(trb.open('rb'))
    pred=PDBParser(QUIET=True).get_structure('rfd',fp)[0]
    refs=[(str(c),int(n)) for c,n in meta['complex_con_ref_pdb_idx']]
    hals=[(str(c),int(n)) for c,n in meta['complex_con_hal_pdb_idx']]
    assert len(refs)==384 and len(set(refs))==384
    fixed_idx=[i for i,(c,n) in enumerate(refs) if c!='_']
    reference=np.array([native[refs[i][0]][refs[i][1]]['CA'].coord for i in fixed_idx])
    # RFdiffusion writes the concatenated receptor to B with a one-based
    # sequential index; its binder is also emitted as chain D. The trb map
    # records concatenated hal indices and marks generated residues by ref '_'.
    moving=[]
    for (rc,rn),(hc,hn) in zip(refs,hals):
        if rc=='_': moving.append(pred['D'][rn]['CA'].coord)
        else: moving.append(pred[rc][rn]['CA'].coord)
    moving=np.array(moving)
    rot,trans=fit(moving[fixed_idx],reference)
    maxdev=float(np.linalg.norm(moving[fixed_idx]@rot+trans-reference,axis=1).max())
    new=residues(pred['D'])
    assert a.min_length<=len(new)<=a.max_length and maxdev<.4
    model=copy.deepcopy(native);ch=Chain('D')
    for i,r in enumerate(new,1):
        nr=copy.deepcopy(r);nr.detach_parent();nr.id=(' ',i,' ')
        for at in nr:at.coord=(at.coord@rot+trans).astype(np.float32)
        ch.add(nr)
    model.add(ch)
    ds=dist(atoms(ch),atoms(model['C']))
    target=atoms(model['A'])+atoms(model['B'])+atoms(model['C'])
    target_ca=[at for at in target if at.name=='CA'];binder_ca=[at for at in atoms(ch) if at.name=='CA']
    close_peptide_res=len({atoms(model['C'])[i].parent.id for i in np.where((ds<8).any(0))[0]})
    min_ca=float(dist(binder_ca,target_ca).min())
    status='eligible_for_mpnn' if close_peptide_res>=3 and min_ca>=3 else 'excluded_backbone_geometry'
    dst=out/(fp.stem+'_restored.pdb');io=PDBIO();io.set_structure(model);io.save(str(dst))
    rows.append({'backbone_id':fp.stem,'status':status,'binder_length':len(new),'target_fixed_CA_max_deviation_A':maxdev,'peptide_residues_within8A':close_peptide_res,'binder_target_CA_min_A':min_ca,'binder_backbone_target_heavy_pairs_lt2A':int((dist(atoms(ch),target)<2).sum()),'rfd_mean_last_plddt':float(np.asarray(meta['plddt'])[-1].mean()),'pdb':str(dst),'rfd_pdb':str(fp),'rfd_pdb_sha256':sha(fp),'trb_sha256':sha(trb),'source_target_sha256':sha(ROOT/'inputs/target_7OW6_native_observed.pdb')})
dump_csv(ROOT/'audit'/f'{a.run_id}_backbones.csv',rows)
print(json.dumps(rows,indent=2))

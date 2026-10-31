from pathlib import Path
import json,csv,argparse
import numpy as np
from Bio.PDB import PDBParser,MMCIFParser
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
from audit_baseline import ROOT,fit,rms,ca,residues,seq,dump_csv

p=argparse.ArgumentParser();p.add_argument('--run-id',default='control_full_v2_seed15');p.add_argument('--variable',action='store_true');a=p.parse_args()
root=ROOT/'predictions'/a.run_id
files=list(root.rglob('*_model_0.pdb'))
if len(files)!=1:raise RuntimeError(f'Expected 1 control PDB, found {len(files)}')
pred=PDBParser(QUIET=True).get_structure('pred',files[0])[0]
ref=MMCIFParser(QUIET=True).get_structure('ref',ROOT/'inputs/source_7ow6.cif')[0]
mm=MMCIF2Dict(ROOT/'inputs/source_7ow6.cif')
refcoords={}
for ch,label,res,atom,element,x,y,z,alt in zip(*[mm[f'_atom_site.{k}'] for k in ['auth_asym_id','label_seq_id','auth_seq_id','auth_atom_id','type_symbol','Cartn_x','Cartn_y','Cartn_z','label_alt_id']]):
    if label=='.' or alt not in ('.','A') or element in ('H','D'):continue
    n=int(label)
    if ch=='B':n-=1
    if ch=='A' and n>275:continue
    if ch not in 'ABCDE' or n<1:continue
    if a.variable and ((ch=='D' and n>117) or (ch=='E' and n>116)):continue
    refcoords[(ch,n,atom)]=np.array([x,y,z],float)
predcoords={(ch.id,r.id[1],a.name):a.coord for ch in pred for r in residues(ch) for a in r if a.element not in ('H','D')}
unmatched=[key for key in refcoords if key not in predcoords]
if any(k[2]!='OXT' for k in unmatched):raise ValueError(f'Missing matched nonterminal control atoms {unmatched}')
# Some model PDB writers omit terminal OXT; use identical common atom sets.
refcoords={k:v for k,v in refcoords.items() if k in predcoords}
keys=[('A',i,'CA') for i in range(1,181)]
rot,trans=fit(np.array([predcoords[k] for k in keys]),np.array([refcoords[k] for k in keys]))
predcoords={k:v@rot+trans for k,v in predcoords.items()}
def contacts(coords,cut=5.):
    ta=[k for k in coords if k[0] in 'ABC'];bi=[k for k in coords if k[0] in 'DE']
    ds=np.linalg.norm(np.array([coords[k] for k in ta])[:,None,:]-np.array([coords[k] for k in bi])[None,:,:],axis=2)
    ii,jj=np.where(ds<cut)
    return {(ta[i][:2],bi[j][:2]) for i,j in zip(ii,jj)}
nc=contacts(refcoords); pc=contacts({k:predcoords[k] for k in refcoords})
native_interface_binder=sorted({(k[0],k[1],'CA') for a,k in nc})
metrics={'native_contact_residue_pairs_5A':len(nc),'predicted_contact_residue_pairs_5A':len(pc),'recovered_native_pairs':len(nc&pc),'native_contact_recovery_fraction':len(nc&pc)/len(nc),'native_interface_binder_CA_RMSD_after_HLA_fit_A':rms(np.array([predcoords[k] for k in native_interface_binder]),np.array([refcoords[k] for k in native_interface_binder])),'HLA_groove_CA_RMSD_A':rms(np.array([predcoords[k] for k in keys]),np.array([refcoords[k] for k in keys])),'source':str(files[0]),'scope':'full deposited TCR sequences; crystal has unresolved residues, only matched observed atoms compared; coordinates unavailable for native HLA tail'}
metrics['scope']='TCR variable domains D1-117 and E1-116, full official pMHC; all native pMHC-contacting TCR residues retained' if a.variable else metrics['scope']
metrics['unmatched_terminal_atoms_excluded_from_both_contact_sets']=unmatched
(ROOT/'audit'/f'{a.run_id}_pose_recovery.json').write_text(json.dumps(metrics,indent=2));print(json.dumps(metrics,indent=2))

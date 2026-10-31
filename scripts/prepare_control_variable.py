import json,yaml,numpy as np
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
from audit_baseline import ROOT
mm=MMCIF2Dict(ROOT/'inputs/source_7ow6.cif')
target=[];binder=[]
limits={'D':117,'E':116}
for ch,label,x,y,z,el in zip(*[mm[f'_atom_site.{k}'] for k in ['auth_asym_id','label_seq_id','Cartn_x','Cartn_y','Cartn_z','type_symbol']]):
    if label=='.' or el in ('H','D'):continue
    if ch in 'ABC':target.append([float(x),float(y),float(z)])
    if ch in 'DE':binder.append((ch,int(label),np.array([x,y,z],float)))
contact_keys=set();omitted_min=float('inf')
for ch,n,coord in binder:
    d=np.linalg.norm(np.array(target)-coord,axis=1).min()
    if d<5:contact_keys.add((ch,n))
    if n>limits[ch]:omitted_min=min(omitted_min,float(d))
assert all(n<=limits[ch] for ch,n in contact_keys)
full=yaml.safe_load((ROOT/'inputs/control_native_TCR_full_v2.yaml').read_text())
for e in full['sequences']:
    p=e['protein']
    if p['id'] in limits:p['sequence']=p['sequence'][:limits[p['id']]]
(ROOT/'inputs/control_TCR_variable.yaml').write_text(yaml.safe_dump(full,sort_keys=False))
record={'purpose':'TCR variable-domain pose recovery control; retains full official pMHC and all native TCR residues contacting pMHC within 5A','D_polymer_residues':[1,117],'E_polymer_residues':[1,116],'native_contacting_binder_residues':sorted(contact_keys),'minimum_distance_of_omitted_TCR_atoms_to_pMHC_A':omitted_min,'total_tokens':sum(len(e['protein']['sequence']) for e in full['sequences']),'caveat':'domain-truncated geometric control; not a new experimentally measured binder, not a design starting sequence'}
(ROOT/'audit/control_variable_construct.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))

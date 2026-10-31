import sys,json
from pathlib import Path
sys.path.insert(0,'/home/<USER>/RFdiffusion/env/RFdiffusion-main')
from rfdiffusion.inference.utils import process_target,get_idx0_hotspots
from rfdiffusion.contigs import ContigMap
from omegaconf import OmegaConf
ROOT=Path(__file__).resolve().parents[1]
pdb=ROOT/'inputs/target_7OW6_native_observed.pdb'
target=process_target(str(pdb),parse_hetatom=False,center=False)
contig='A1-275/0 B1-99/0 C1-10/0 80-100'
m=ContigMap(target,contigs=[contig])
mapping=m.get_mappings()
hotspots=['C4','C5','C7','C8']
mapped=get_idx0_hotspots(mapping,OmegaConf.create({'hotspot_res':hotspots}),binderlen=len(m.inpaint))
assert len(m.inpaint)>=80 and len(m.inpaint)<=100
assert len(m.receptor)==384
assert len(mapping['complex_con_ref_pdb_idx'])==384
assert len(mapped)==4
assert all(x==('_','_') for x in m.inpaint)
assert set(mapping['complex_con_ref_pdb_idx'])==set(target['pdb_idx'])
r={'contig':contig,'binder_length_example':len(m.inpaint),'fixed_target_count':len(m.receptor),'hotspots':hotspots,'hotspot_indices':list(map(int,mapped)),'all_target_residues_fixed':True,'all_generated_residues_binder_only':True}
(ROOT/'audit/rfd_preflight.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))

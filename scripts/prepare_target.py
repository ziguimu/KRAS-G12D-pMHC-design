from pathlib import Path
import csv,json,shutil,yaml
from Bio.PDB import MMCIFParser,PDBIO,Select
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
from audit_baseline import ROOT,HLA,B2M,seq,residues,sha

out=ROOT/'inputs'; out.mkdir(exist_ok=True)
src=Path('<LEGACY_PMHC_ROOT>/7ow6.cif')
s=MMCIFParser(QUIET=True).get_structure('7OW6',src)[0]
chains={c.id:{'n':len(residues(c)),'sequence':seq(c),'first':residues(c)[0].id,'last':residues(c)[-1].id} for c in s}
print(json.dumps(chains,indent=2))
assert seq(s['A'])==HLA[:275]+'P'
assert seq(s['B'])==B2M
assert seq(s['C'])=='VVVGADGVGK'
class Target(Select):
    def accept_chain(self,c): return c.id in ['A','B','C']
    def accept_residue(self,r): return r.id[0]==' ' and not(r.parent.id=='A' and r.id[1]==276)
io=PDBIO();io.set_structure(s);io.save(str(out/'target_7OW6_native_observed.pdb'),Target())
shutil.copyfile(src,out/'source_7ow6.cif')
meta={'source':str(src),'sha256':sha(src),'chains':chains,'design_structure':'A1-275, B1-99, C1-10; no expression tag; no TCR','prediction_construct':'full official A1-281; B1-99; C1-10','unresolved_native_HLA_residues':'276-281 LSSQPT; no coordinates fabricated','P276':'7OW6 _struct_ref_seq_dif explicitly says expression tag','reference_url':'https://www.rcsb.org/structure/7OW6'}
(out/'target_audit.json').write_text(json.dumps(meta,indent=2))
# Full deposited polymer sequences, including unresolved residues; never a design template.
mm=MMCIF2Dict(src)
entity_seqs={ch:''.join(sequence.split()) for ch,sequence in zip(mm['_entity_poly.pdbx_strand_id'],mm['_entity_poly.pdbx_seq_one_letter_code_can'])}
entries=[]
for c,sequence in {'A':HLA,'B':B2M,'C':'VVVGADGVGK','D':entity_seqs['D'],'E':entity_seqs['E']}.items():
    msa=str(out/'msa'/f'{c}.csv') if c in ['A','B'] else 'empty'
    entries.append({'protein':{'id':c,'sequence':sequence,'msa':msa}})
(out/'control_native_TCR_full_v2.yaml').write_text(yaml.safe_dump({'version':1,'sequences':entries},sort_keys=False))
print('Target prepared. Full control tokens:',sum(len(e['protein']['sequence']) for e in entries))

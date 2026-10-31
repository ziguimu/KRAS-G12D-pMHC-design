from pathlib import Path
import csv, json, re, hashlib
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
root=Path('.')
old={}
for p in (root/'audit').glob('*.csv'):
    try:
        with p.open(newline='',encoding='utf-8-sig') as f:
            reader=csv.DictReader(f)
            for row in reader:
                seq=(row.get('sequence') or row.get('binder_sequence') or '').strip().upper()
                if 30 <= len(seq) <= 250 and re.fullmatch(r'[ACDEFGHIKLMNPQRSTVWY]+',seq): old.setdefault(seq,[]).append(str(p))
    except Exception: pass
rows=[]
for p in sorted((root/'results/boltzgen_smoke_v1/intermediate_designs_inverse_folded').glob('*.cif')):
    d=MMCIF2Dict(str(p))
    asym=d['_struct_asym.id']; ent=d['_struct_asym.entity_id']
    eids=d['_entity_poly.entity_id']; seqs=d['_entity_poly.pdbx_seq_one_letter_code']
    emap={str(i):re.sub(r'\s+','',str(s)).replace('X','X') for i,s in zip(eids,seqs)}
    chains={str(c):emap[str(e)] for c,e in zip(asym,ent)}
    bind=chains['A']
    rows.append({'candidate_id':p.stem,'binder_chain':'A','sequence':bind,'length':len(bind),'sha256':hashlib.sha256(bind.encode()).hexdigest(),'duplicate_old':bind in old,'old_sources':old.get(bind,[])})
out=root/'audit/boltzgen_smoke_v1_sequences.csv'
with out.open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['candidate_id','binder_chain','sequence','length','sha256','duplicate_old','old_sources']);w.writeheader();w.writerows(rows)
print(json.dumps({'count':len(rows),'sequences':rows,'unique':len({r['sequence'] for r in rows}),'historical_sequence_union':len(old),'output':str(out)},indent=2))

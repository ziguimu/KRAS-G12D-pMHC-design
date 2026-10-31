import csv, hashlib, json
from pathlib import Path
from audit_baseline import ROOT, dump_csv

OUT = ROOT / 'results'
OUT.mkdir(exist_ok=True)
sources = {
    'recovered_003': (ROOT/'audit/recovered_pool_ledger.csv', ROOT/'audit/expanded_mutant_seed15_metrics.csv', ROOT/'audit/expanded_mutant_gate_v1.csv', 'legacy_unscored_pool'),
    'rfd_batch2_design_1001_s14': (ROOT/'audit/rfd_batch2_mpnn_sequences.csv', ROOT/'audit/expanded_mutant_seed15_metrics.csv', ROOT/'audit/expanded_mutant_gate_v1.csv', 'RFdiffusion_hotspots_C4_C5_C7_C8'),
    'rfd_peptidewide_batch_design_3003_s04': (ROOT/'audit/rfd_peptidewide_batch_mpnn_sequences.csv', ROOT/'audit/peptidewide_mutant_seed15_metrics.csv', ROOT/'audit/peptidewide_mutant_gate_v1.csv', 'RFdiffusion_hotspots_C1_C10'),
    'rfd_peptidewide_batch_design_3003_s05': (ROOT/'audit/rfd_peptidewide_batch_mpnn_sequences.csv', ROOT/'audit/peptidewide_mutant_seed15_metrics.csv', ROOT/'audit/peptidewide_mutant_gate_v1.csv', 'RFdiffusion_hotspots_C1_C10'),
}
rows = []
for cid, (seqfile, metricsfile, gatefile, origin) in sources.items():
    seqrows = list(csv.DictReader(seqfile.open()))
    if cid == 'recovered_003':
        seq = next(r for r in seqrows if r['candidate_id'] == cid)
    else:
        seq = next(r for r in seqrows if r['candidate_id'] == cid)
    metric = next(r for r in csv.DictReader(metricsfile.open()) if r['candidate_id'] == cid and r['condition'] == 'mutant')
    gate = next(r for r in csv.DictReader(gatefile.open()) if r['candidate_id'] == cid)
    sequence = seq['sequence']
    rows.append({
        'candidate_id': cid, 'sequence': sequence, 'length': len(sequence),
        'sequence_sha256': hashlib.sha256(sequence.encode()).hexdigest(),
        'origin': origin, 'source_backbone': seq.get('source_backbone',''),
        'mpnn_score': seq.get('mpnn_score',''), 'seed15_mutant_gate': gate['status'],
        'seed15_failed_metrics': gate.get('failed_metrics',''),
        'peptide_atom_pairs_lt4A': metric.get('peptide_atom_pairs_lt4A',''),
        'peptide_residue_pairs_lt4A': metric.get('peptide_residue_pairs_lt4A',''),
        'peptide_positions_lt4A': metric.get('peptide_positions_lt4A',''),
        'iptm': metric.get('iptm',''), 'binder_HLA_iptm_min': metric.get('binder_HLA_iptm_min',''),
        'binder_peptide_iptm_min': metric.get('binder_peptide_iptm_min',''),
        'all_target_pairs_lt2A': metric.get('all_target_pairs_lt2A',''),
        'full_confirmation': 'failed WT/apo and/or seed16/17' if cid == 'recovered_003' else 'not run: mutant seed15 gate failed',
        'overall_qualified': '0',
    })
assert len({r['sequence'] for r in rows}) == len(rows)
dump_csv(OUT/'near_miss_shortlist_v1.csv', rows)
with (OUT/'near_miss_sequences_v1.fasta').open('w') as f:
    for r in rows:
        f.write(f">{r['candidate_id']} | NOT_QUALIFIED | {r['seed15_failed_metrics'] or r['full_confirmation']}\n{r['sequence']}\n")
print(json.dumps({'near_misses':len(rows),'all_qualified':False,'csv':str(OUT/'near_miss_shortlist_v1.csv'),'fasta':str(OUT/'near_miss_sequences_v1.fasta')},indent=2))

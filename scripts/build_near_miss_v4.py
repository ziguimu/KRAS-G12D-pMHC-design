import csv
import hashlib
from pathlib import Path

from audit_baseline import ROOT, dump_csv

candidates = [
    {
        'candidate_id': 'rfd_micro_central_extended_try6_s016_fixedcontacts_resample02_s024',
        'initial_metrics': 'rfd_micro_central_extended_try6_s016_fixedcontacts_resample02_seed15_mutant_metrics.csv',
        'initial_gate': 'rfd_micro_central_extended_try6_s016_fixedcontacts_resample02_seed15_gate.csv',
        'status': 'NOT_QUALIFIED',
        'exclusion_reason': 'Initial mutant seed15 screen passed; an independent same-seed mutant prediction had only 32 peptide atom pairs (<37 required). WT/apo seed15 were predicted, but no repeat-seed panel was run after the mutant contact failure.',
        'confirmation_metrics': 'rfd_micro_central_extended_try6_s016_fixedcontacts_resample02_s024_seed15_metrics.csv',
        'confirmation_gate': '',
    },
    {
        'candidate_id': 'rfd_micro_central_extended_try6_s016_fixedcontacts_resample05_d6_bias_partialfix_s016',
        'initial_metrics': 'rfd_micro_central_extended_try6_s016_fixedcontacts_resample05_d6_bias_partialfix_seed15_mutant_metrics.csv',
        'initial_gate': 'rfd_micro_central_extended_try6_s016_fixedcontacts_resample05_d6_bias_partialfix_seed15_gate.csv',
        'status': 'NOT_QUALIFIED',
        'exclusion_reason': 'Initial mutant seed15 screen passed; full mutant/WT/apo seed15 rerun failed absolute clash and all three mutant-minus-control contrast thresholds. No seed16/17 predictions were run after the seed15 failure.',
        'confirmation_metrics': 'rfd_micro_central_extended_try6_s016_fixedcontacts_resample05_d6_bias_partialfix_s016_seed15_metrics.csv',
        'confirmation_gate': 'rfd_micro_central_extended_try6_s016_fixedcontacts_resample05_d6_bias_partialfix_s016_seed15_comparison.csv',
    },
]
rows = []
fasta = []
for item in candidates:
    initial = next(r for r in csv.DictReader((ROOT / 'audit' / item['initial_metrics']).open()) if r['candidate_id'] == item['candidate_id'])
    gate = next(r for r in csv.DictReader((ROOT / 'audit' / item['initial_gate']).open()) if r['candidate_id'] == item['candidate_id'])
    repeat = {}
    if item['confirmation_metrics']:
        repeat_rows = list(csv.DictReader((ROOT / 'audit' / item['confirmation_metrics']).open()))
        repeat = next((r for r in repeat_rows if r['condition'] == 'mutant'), {})
    comparison = {}
    if item['confirmation_gate']:
        comparison = next(r for r in csv.DictReader((ROOT / 'audit' / item['confirmation_gate']).open()))
    seq = initial['sequence']
    fasta.append(f">{item['candidate_id']}|{item['status']}|initial_seed15_mutant_gate=PASS|{item['exclusion_reason']}\n{seq}")
    rows.append({
        'candidate_id': item['candidate_id'], 'status': item['status'], 'sequence': seq,
        'length': len(seq), 'sequence_sha256': hashlib.sha256(seq.encode()).hexdigest(),
        'initial_seed15_failed_metrics': gate['failed_metrics'],
        'initial_confidence_score': initial['confidence_score'], 'initial_iptm': initial['iptm'],
        'initial_binder_ptm': initial['binder_ptm'], 'initial_binder_HLA_iptm_min': initial['binder_HLA_iptm_min'],
        'initial_binder_peptide_iptm_min': initial['binder_peptide_iptm_min'],
        'initial_peptide_atom_pairs_lt4A': initial['peptide_atom_pairs_lt4A'],
        'initial_peptide_residue_pairs_lt4A': initial['peptide_residue_pairs_lt4A'],
        'initial_peptide_positions_lt4A': initial['peptide_positions_lt4A'],
        'initial_complex_pde': initial['complex_pde'], 'initial_complex_ipde': initial['complex_ipde'],
        'initial_all_target_pairs_lt2A': initial['all_target_pairs_lt2A'],
        'repeat_mutant_seed15_peptide_atom_pairs_lt4A': repeat.get('peptide_atom_pairs_lt4A', ''),
        'repeat_mutant_seed15_all_target_pairs_lt2A': repeat.get('all_target_pairs_lt2A', ''),
        'confirmation_failed_metrics': comparison.get('failed_metrics', ''),
        'exclusion_reason': item['exclusion_reason'],
    })
(ROOT / 'results' / 'near_miss_sequences_v4.fasta').write_text('\n'.join(fasta) + '\n')
dump_csv(ROOT / 'results' / 'near_miss_shortlist_v4.csv', rows)
print(f'Wrote {len(rows)} explicitly nonqualified sequence records.')

import csv, json, math
from audit_baseline import ROOT

criteria = json.loads((ROOT / 'criteria_v1.json').read_text())
def read(path):
    return list(csv.DictReader((ROOT / path).open()))

candidate_files = {
    15: (read('audit/expanded_mutant_seed15_metrics.csv'), read('audit/recovered_003_confirm_seed15_metrics.csv')),
    16: (read('audit/recovered_003_confirm_seed16_metrics.csv'), read('audit/recovered_003_confirm_seed16_metrics.csv')),
    17: (read('audit/recovered_003_confirm_seed17_metrics.csv'), read('audit/recovered_003_confirm_seed17_metrics.csv')),
}
baseline_files = {
    15: read('audit/baseline_seed15_v2_metrics.csv'),
    16: read('audit/baseline_seed16_metrics.csv'),
    17: read('audit/baseline_seed17_metrics.csv'),
}
rows = []
for seed in (15, 16, 17):
    mutant_rows, control_rows = candidate_files[seed]
    if seed == 15:
        cand_m = next(r for r in mutant_rows if r['candidate_id'] == 'recovered_003' and r['condition'] == 'mutant')
        control_id = 'recovered_003_seed15'
    else:
        control_id = f'recovered_003_seed{seed}'
        cand_m = next(r for r in mutant_rows if r['candidate_id'] == control_id and r['condition'] == 'mutant')
    controls = {r['condition']: r for r in control_rows if r['candidate_id'] == control_id}
    base = {r['candidate_id']: r for r in baseline_files[seed] if r['condition'] == 'mutant'}
    assert len(base) == 4 and all(r['status'] == 'output_audited' for r in base.values())
    failed, missing = [], []
    for key in criteria['higher_is_better_mutant']:
        threshold = max(float(r[key]) for r in base.values())
        value = float(cand_m[key])
        if value < threshold - 1e-8:
            failed.append(key)
    for key in criteria['lower_is_better_mutant']:
        threshold = min(float(r[key]) for r in base.values())
        value = float(cand_m[key])
        if value > threshold + 1e-8:
            failed.append(key)
    if cand_m['status'] != 'output_audited':
        missing.append('mutant_output_audited')
    for cond in ('WT', 'apo'):
        if cond not in controls or controls[cond]['status'] != 'output_audited':
            missing.append(f'{cond}_output_audited')
    for condition in ('mutant', 'WT', 'apo'):
        r = cand_m if condition == 'mutant' else controls.get(condition)
        if r and float(r.get('all_target_pairs_lt2A') or 0) > 0:
            failed.append(f'{condition}_absolute_clash_gate')
    base_all = baseline_files[seed]
    by_id = {}
    for r in base_all:
        by_id.setdefault(r['candidate_id'], {})[r['condition']] = r
    contrast_defs = [
        ('mutant_minus_WT_binder_HLA_iptm_min', 'binder_HLA_iptm_min', 'WT'),
        ('mutant_minus_apo_binder_HLA_iptm_min', 'binder_HLA_iptm_min', 'apo'),
        ('mutant_minus_WT_binder_peptide_iptm_min', 'binder_peptide_iptm_min', 'WT'),
    ]
    contrasts = {}
    for label, metric, negative in contrast_defs:
        try:
            cand_delta = float(cand_m[metric]) - float(controls[negative][metric])
            base_deltas = [float(x['mutant'][metric]) - float(x[negative][metric]) for x in by_id.values()]
            best = max(base_deltas)
            contrasts[label] = {'candidate_delta': cand_delta, 'best_baseline_delta': best, 'pass': cand_delta >= best - 1e-8}
            if cand_delta < best - 1e-8:
                failed.append(label)
        except (KeyError, ValueError, TypeError):
            missing.append(label)
    rows.append({
        'seed': seed,
        'status': 'pass_seed' if not failed and not missing else ('missing_data' if missing else 'failed_seed'),
        'candidate_id': 'recovered_003',
        'mutant_iptm': cand_m.get('iptm'),
        'mutant_binder_HLA_iptm_min': cand_m.get('binder_HLA_iptm_min'),
        'mutant_binder_peptide_iptm_min': cand_m.get('binder_peptide_iptm_min'),
        'mutant_peptide_atom_pairs_lt4A': cand_m.get('peptide_atom_pairs_lt4A'),
        'mutant_target_HLA_groove_CA_RMSD_to_crystal_A': cand_m.get('target_HLA_groove_CA_RMSD_to_crystal_A'),
        'mutant_target_peptide_CA_RMSD_to_crystal_after_HLA_fit_A': cand_m.get('target_peptide_CA_RMSD_to_crystal_after_HLA_fit_A'),
        'WT_binder_HLA_iptm_min': controls.get('WT', {}).get('binder_HLA_iptm_min'),
        'apo_binder_HLA_iptm_min': controls.get('apo', {}).get('binder_HLA_iptm_min'),
        'failed_metrics': ';'.join(failed),
        'missing_metrics': ';'.join(missing),
        'controls': json.dumps(contrasts, sort_keys=True),
    })

out = ROOT / 'audit/recovered_003_confirmation_v1.csv'
with out.open('w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader(); w.writerows(rows)
print(json.dumps({'candidate':'recovered_003','all_seeds_pass':all(r['status']=='pass_seed' for r in rows),'results':rows,'output':str(out)},indent=2))

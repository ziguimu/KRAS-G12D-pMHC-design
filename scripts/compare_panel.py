"""Strict componentwise baseline comparison. Model descriptors are not KD."""
import argparse,csv,json,math
from pathlib import Path
from audit_baseline import ROOT,dump_csv
p=argparse.ArgumentParser();p.add_argument('baseline_csv');p.add_argument('candidate_csv');p.add_argument('--output',required=True);a=p.parse_args()
criteria=json.loads((ROOT/'criteria_v1.json').read_text())
baselines=list(csv.DictReader(Path(a.baseline_csv).open()))
candidates=list(csv.DictReader(Path(a.candidate_csv).open()))
def number(r,k):
    x=float(r[k]);assert math.isfinite(x),(r.get('candidate_id'),k);return x
def group(rows):
    d={}
    for r in rows:
        key=r['candidate_id'];condition=r['condition']
        assert condition not in d.setdefault(key,{}),(key,condition)
        d[key][condition]=r
    return d
bg=group(baselines);cg=group(candidates)
assert len(bg)==4
for cid,g in bg.items():
    assert set(g)=={'mutant','WT','apo'},(cid,'missing baseline condition')
    assert all(r['status']=='output_audited' for r in g.values())
thresholds={}
for key in criteria['higher_is_better_mutant']:
    thresholds[key]={'direction':'>=','value':max(number(g['mutant'],key) for g in bg.values())}
for key in criteria['lower_is_better_mutant']:
    thresholds[key]={'direction':'<=','value':min(number(g['mutant'],key) for g in bg.values())}
contrasts=[('WT','binder_HLA_iptm_min'),('apo','binder_HLA_iptm_min'),('WT','binder_peptide_iptm_min')]
for condition,key in contrasts:
    thresholds[f'mutant_minus_{condition}_{key}']={'direction':'>=','value':max(number(g['mutant'],key)-number(g[condition],key) for g in bg.values())}
results=[]
for cid,g in cg.items():
    failures=[];missing=[];metrics={}
    for condition in ['mutant','WT','apo']:
        if condition not in g or g[condition]['status']!='output_audited':missing.append(condition)
    if 'mutant' in g and g['mutant']['status']=='output_audited':
        for key in criteria['higher_is_better_mutant']+criteria['lower_is_better_mutant']:
            try:metrics[key]=number(g['mutant'],key)
            except (KeyError,ValueError,AssertionError):missing.append(key)
        if number(g['mutant'],'all_target_pairs_lt2A')>0:failures.append('absolute_clash_gate')
        for condition,key in contrasts:
            if condition in g and g[condition]['status']=='output_audited':
                metrics[f'mutant_minus_{condition}_{key}']=number(g['mutant'],key)-number(g[condition],key)
    for key,val in metrics.items():
        rule=thresholds[key]
        if rule['direction']=='>=' and val<rule['value']-1e-8:failures.append(key)
        if rule['direction']=='<=' and val>rule['value']+1e-8:failures.append(key)
    # Passing this table remains preliminary: repeats, pose intent, and eligibility are separate gates.
    state='missing_required_data' if missing else ('failed_numeric_gate' if failures else 'passed_numeric_gate_pending_pose_repeats')
    results.append({'candidate_id':cid,'status':state,'failed_count':len(failures),'missing_count':len(missing),'failed_metrics':';'.join(failures),'missing_metrics':';'.join(missing),'experimental_binding_claim':False,**metrics})
dump_csv(ROOT/'audit'/f'{a.output}.csv',results)
(ROOT/'audit'/f'{a.output}_thresholds.json').write_text(json.dumps(thresholds,indent=2))
print(json.dumps({'evaluated_sequences':len(results),'passed_numeric_gate':sum(x['status']=='passed_numeric_gate_pending_pose_repeats' for x in results),'failed_numeric_gate':sum(x['status']=='failed_numeric_gate' for x in results),'missing_required_data':sum(x['status']=='missing_required_data' for x in results),'final_qualified_count':'requires independent pose/repeat gates; not determined by this script'},indent=2))

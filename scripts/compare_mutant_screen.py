import csv,json,math
from pathlib import Path
from audit_baseline import ROOT,dump_csv
base=list(csv.DictReader((ROOT/'audit/baseline_seed15_v2_metrics.csv').open()))
cand=list(csv.DictReader((ROOT/'audit/new_mutant_seed15_metrics.csv').open()))
criteria=json.loads((ROOT/'criteria_v1.json').read_text())
bm={r['candidate_id']:r for r in base if r['condition']=='mutant'}
assert len(bm)==4 and all(r['status']=='output_audited' for r in bm.values())
thresholds={}
for k in criteria['higher_is_better_mutant']:
    thresholds[k]=max(float(r[k]) for r in bm.values())
for k in criteria['lower_is_better_mutant']:
    thresholds[k]=min(float(r[k]) for r in bm.values())
out=[]
for r in cand:
    fails=[];missing=[]
    if r['status']!='output_audited':missing.append('audited_mutant_prediction')
    else:
        for k,cut in thresholds.items():
            try:
                v=float(r[k]);
                if not math.isfinite(v):raise ValueError(k)
                if k in criteria['higher_is_better_mutant'] and v<cut-1e-8:fails.append(k)
                if k in criteria['lower_is_better_mutant'] and v>cut+1e-8:fails.append(k)
            except (ValueError,KeyError):missing.append(k)
    if float(r.get('all_target_pairs_lt2A',0) or 0)>0:fails.append('absolute_clash_gate')
    out.append({'candidate_id':r['candidate_id'],'status':'missing_data' if missing else ('pass_mutant_screen_pending_controls' if not fails else 'failed_mutant_gate'),'failed_metrics':';'.join(fails),'missing_metrics':';'.join(missing),**{k:r.get(k,'') for k in thresholds}})
dump_csv(ROOT/'audit/mutant_screen_gate_v1.csv',out)
(ROOT/'audit/mutant_screen_thresholds_v1.json').write_text(json.dumps(thresholds,indent=2))
print(json.dumps({'screened':len(out),'mutant_gate_pass':sum(r['status']=='pass_mutant_screen_pending_controls' for r in out),'failed':sum(r['status']=='failed_mutant_gate' for r in out),'missing':sum(r['status']=='missing_data' for r in out)},indent=2))

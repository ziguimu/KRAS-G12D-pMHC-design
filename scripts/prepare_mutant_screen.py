import csv,shutil,json
from pathlib import Path
from audit_baseline import ROOT,sha
rows=list(csv.DictReader((ROOT/'audit/new_candidate_panel_ledger.csv').open()))
out=ROOT/'inputs/mutant_screen';out.mkdir(exist_ok=True)
for r in rows:shutil.copyfile(r['mutant_input'],out/f"{r['candidate_id']}.yaml")
(ROOT/'audit/mutant_screen_input_manifest.json').write_text(json.dumps([{'candidate_id':r['candidate_id'],'input':str(out/f"{r['candidate_id']}.yaml"),'sha256':sha(out/f"{r['candidate_id']}.yaml")} for r in rows],indent=2))
print(f'Prepared {len(rows)} unique mutant-condition screening jobs.')

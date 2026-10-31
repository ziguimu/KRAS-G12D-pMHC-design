from pathlib import Path
import shutil,json
from audit_baseline import ROOT,sha
out=ROOT/'inputs/baseline_panel';out.mkdir(exist_ok=True)
for p in (ROOT/'inputs').glob('baseline_*.yaml'):shutil.copyfile(p,out/p.name)
(out/'manifest.json').write_text(json.dumps([{'file':p.name,'sha256':sha(p)} for p in sorted(out.glob('*.yaml'))],indent=2))
assert len(list(out.glob('*.yaml')))==12
print('Prepared 12 baseline jobs: 4 sequences x mutant/WT/apo.')

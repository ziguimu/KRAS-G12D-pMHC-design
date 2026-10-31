import argparse
import csv
from pathlib import Path

import yaml

from audit_baseline import ROOT, HLA, B2M, PEPTIDES, dump_csv, sha


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate-ids', nargs='+', required=True)
    parser.add_argument('--panel-id', default='boltzgen_site_v1')
    args = parser.parse_args()
    ledger_path = ROOT / 'audit' / f'{args.panel_id}_panel_ledger.csv'
    records = {row['candidate_id']: row for row in csv.DictReader(ledger_path.open())}
    out = ROOT / 'inputs' / f'{args.panel_id}_confirmation'
    out.mkdir(parents=True, exist_ok=True)
    prepared = []
    for candidate_id in args.candidate_ids:
        if candidate_id not in records:
            raise KeyError(f'Unknown candidate id: {candidate_id}')
        source = records[candidate_id]
        sequence = source['sequence']
        for condition, peptide in {**PEPTIDES, 'apo': None}.items():
            chains = {'A': HLA, 'B': B2M, 'D': sequence}
            if peptide is not None:
                chains['C'] = peptide
            entries = []
            for chain, seq in chains.items():
                msa = str(ROOT / 'inputs' / 'msa' / f'{chain}.csv') if chain in ('A', 'B') else 'empty'
                entries.append({'protein': {'id': chain, 'sequence': seq, 'msa': msa}})
            path = out / f'{candidate_id}_{condition}.yaml'
            path.write_text(yaml.safe_dump({'version': 1, 'sequences': entries}, sort_keys=False))
            prepared.append({
                'candidate_id': candidate_id,
                'condition': condition,
                'sequence': sequence,
                'length': len(sequence),
                'input_yaml': str(path),
                'input_sha256': sha(path),
            })
    dump_csv(ROOT / 'audit' / f'{args.panel_id}_confirmation_inputs.csv', prepared)
    print({'candidate_count': len(args.candidate_ids), 'input_count': len(prepared), 'conditions': ['mutant', 'WT', 'apo']})


if __name__ == '__main__':
    main()

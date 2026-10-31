import argparse
import csv
import hashlib
import re
from pathlib import Path

import yaml
from Bio.PDB.MMCIF2Dict import MMCIF2Dict

from audit_baseline import ROOT, HLA, B2M, PEPTIDES, dump_csv, sha


def cif_sequences(path):
    d = MMCIF2Dict(str(path))
    entity_ids = d['_entity_poly.entity_id']
    entity_seqs = d['_entity_poly.pdbx_seq_one_letter_code']
    seq_by_entity = {
        str(e): re.sub(r'\s+', '', str(s)).upper()
        for e, s in zip(entity_ids, entity_seqs)
    }
    chains = {
        str(chain): seq_by_entity[str(entity)]
        for chain, entity in zip(d['_struct_asym.id'], d['_struct_asym.entity_id'])
    }
    return chains


def historical_sequences():
    seen = set()
    for path in (ROOT / 'audit').glob('*.csv'):
        if path.name.startswith('boltzgen_'):
            continue
        try:
            with path.open(newline='', encoding='utf-8-sig') as handle:
                for row in csv.DictReader(handle):
                    sequence = (row.get('sequence') or row.get('binder_sequence') or '').strip().upper()
                    if 30 <= len(sequence) <= 250 and re.fullmatch(r'[ACDEFGHIKLMNPQRSTVWY]+', sequence):
                        seen.add(sequence)
        except (OSError, UnicodeError, csv.Error):
            continue
    return seen


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', action='append', required=True, help='BoltzGen output directory; repeatable')
    parser.add_argument('--output-id', default='boltzgen_v1')
    args = parser.parse_args()

    old = historical_sequences()
    seen = set()
    records = []
    for source in args.source:
        source_dir = Path(source)
        if not source_dir.is_absolute():
            source_dir = ROOT / source_dir
        inverse_dir = source_dir / 'intermediate_designs_inverse_folded'
        for cif in sorted(inverse_dir.glob('*.cif')):
            chains = cif_sequences(cif)
            sequence = chains.get('A', '')
            if not re.fullmatch(r'[ACDEFGHIKLMNPQRSTVWY]+', sequence):
                raise ValueError(f'Invalid inverse-folded binder chain in {cif}: {sequence!r}')
            if not 55 <= len(sequence) <= 75:
                raise ValueError(f'Binder length outside requested 55-75 aa range: {cif} ({len(sequence)})')
            if sequence in seen:
                continue
            seen.add(sequence)
            source_label = source_dir.name
            candidate_id = f"{args.output_id}_{source_label}_{cif.stem.rsplit('_', 1)[-1]}"
            record = {
                'candidate_id': candidate_id,
                'sequence': sequence,
                'length': len(sequence),
                'source_run': source_label,
                'source_cif': str(cif),
                'source_cif_sha256': sha(cif),
                'sequence_sha256': hashlib.sha256(sequence.encode()).hexdigest(),
                'duplicate_historical_sequence': sequence in old,
            }
            if sequence in old:
                record['status'] = 'duplicate_excluded'
                records.append(record)
                continue
            record['status'] = 'prepared_mutant_screen'
            entries = []
            for chain, seq in {'A': HLA, 'B': B2M, 'C': PEPTIDES['mutant'], 'D': sequence}.items():
                msa = str(ROOT / 'inputs' / 'msa' / f'{chain}.csv') if chain in ('A', 'B') else 'empty'
                entries.append({'protein': {'id': chain, 'sequence': seq, 'msa': msa}})
            input_path = ROOT / 'inputs' / 'boltzgen_mutant_screen' / f'{candidate_id}_mutant.yaml'
            input_path.parent.mkdir(parents=True, exist_ok=True)
            input_path.write_text(yaml.safe_dump({'version': 1, 'sequences': entries}, sort_keys=False))
            record['mutant_input'] = str(input_path)
            record['mutant_input_sha256'] = sha(input_path)
            records.append(record)

    ledger = ROOT / 'audit' / f'{args.output_id}_panel_ledger.csv'
    dump_csv(ledger, records)
    print({
        'candidate_rows': len(records),
        'unique_new_sequences': sum(r['status'] == 'prepared_mutant_screen' for r in records),
        'historical_duplicates': sum(r['status'] == 'duplicate_excluded' for r in records),
        'yaml_inputs': sum(bool(r.get('mutant_input')) for r in records),
        'ledger': str(ledger),
    })


if __name__ == '__main__':
    main()

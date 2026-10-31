import argparse
import csv
import json
import yaml
from pathlib import Path

from audit_baseline import ROOT, B2M, HLA, PEPTIDES, dump_csv, sha


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--run-id', default='rfd_micro_try1')
    p.add_argument('--source-csv')
    p.add_argument('--output-id')
    p.add_argument('--candidate-id')
    p.add_argument('--sequences-per-backbone', type=int, default=8)
    args = p.parse_args()
    source = Path(args.source_csv) if args.source_csv else ROOT / 'audit' / f'{args.run_id}_mpnn_sequences.csv'
    if not source.is_absolute():
        source = ROOT / source
    output_id = args.output_id or args.run_id
    raw = list(csv.DictReader(source.open()))
    if args.candidate_id:
        raw = [row for row in raw if row['candidate_id'] == args.candidate_id]
        if not raw:
            raise ValueError(f'Candidate not found in source CSV: {args.candidate_id}')
    # Keep a bounded, spread sample: the lowest ProteinMPNN sequence score
    # (best log-likelihood) per backbone and then its remaining unique variants.
    raw.sort(key=lambda r: (r['source_backbone'], float(r['mpnn_score'] or 1e9), r['sequence_sha256']))
    chosen = []
    seen = set()
    count_by_backbone = {}
    for row in raw:
        seq = row['sequence']
        bid = row['source_backbone']
        if seq in seen or count_by_backbone.get(bid, 0) >= args.sequences_per_backbone:
            continue
        seen.add(seq)
        count_by_backbone[bid] = count_by_backbone.get(bid, 0) + 1
        chosen.append(row)

    out = ROOT / 'inputs' / f'{output_id}_panel'
    out.mkdir(parents=True, exist_ok=True)
    ledger = []
    for row in chosen:
        rec = {
            'candidate_id': row['candidate_id'],
            'sequence': row['sequence'],
            'length': int(row['length']),
            'sequence_source': 'de_novo_RFdiffusion_compact_backbone_ProteinMPNN',
            'source_backbone': row['source_backbone'],
            'mpnn_score': row['mpnn_score'],
            'sequence_sha256': row['sequence_sha256'],
            'source_file': row['source_fasta'],
            'backbone_pdb': row['source_backbone_pdb'],
        }
        conditions = {**PEPTIDES, 'apo': None}
        for condition, peptide in conditions.items():
            entries = []
            chain_sequences = {'A': HLA, 'B': B2M, 'D': rec['sequence']}
            if peptide is not None:
                chain_sequences['C'] = peptide
            for chain, seq in chain_sequences.items():
                msa = str(ROOT / 'inputs' / 'msa' / f'{chain}.csv') if chain in ('A', 'B') else 'empty'
                entries.append({'protein': {'id': chain, 'sequence': seq, 'msa': msa}})
            dst = out / f"{rec['candidate_id']}_{condition}.yaml"
            dst.write_text(yaml.safe_dump({'version': 1, 'sequences': entries}, sort_keys=False))
            rec[f'{condition}_input'] = str(dst)
            rec[f'{condition}_input_sha256'] = sha(dst)
        ledger.append(rec)
    dump_csv(ROOT / 'audit' / f'{output_id}_panel_ledger.csv', ledger)
    print(json.dumps({
        'candidate_count': len(ledger),
        'unique_sequences': len({r['sequence'] for r in ledger}),
        'scaffold_backbones': len({r['source_backbone'] for r in ledger}),
        'conditions_per_sequence': 3,
        'prepared_yaml_count': 3 * len(ledger),
        'selected_per_backbone': count_by_backbone,
    }, indent=2))


if __name__ == '__main__':
    main()

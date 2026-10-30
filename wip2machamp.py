#!/usr/bin/env python3
"""Convert WIP CSV files to MaChAmp-compatible 3-column TSV format.

Output columns: form \t lemma \t upos
Sentences delimited by blank lines.
Train/dev/test split is 80/10/10 by file (random seed 42).
"""

import csv
import random
from pathlib import Path


def process_file(filepath):
    sentences = []
    current_unit = None
    current_sentence = []

    with open(filepath, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        has_unit = 'unit' in fieldnames
        has_id = 'id' in fieldnames

        for row in reader:
            # Use 'unit' if available, else fall back to 'tu_id' for sentence grouping
            unit = row['unit'] if has_unit else row['tu_id']
            form = row['form']
            lemma = row['lemma']
            upos = row['upos']

            # Sentence boundary on unit change
            if current_unit is not None and unit != current_unit:
                if current_sentence:
                    sentences.append(current_sentence)
                current_sentence = []
            current_unit = unit

            # Skip multiword parent rows (id is a range like "8-9" and upos is unset)
            if has_id:
                id_field = row['id']
                if '-' in id_field and upos == '_':
                    continue

            # Skip unannotated tokens
            if upos == '_' or lemma == '_':
                continue

            current_sentence.append((form, lemma, upos))

    if current_sentence:
        sentences.append(current_sentence)

    return sentences


def write_split(sentences, path):
    with open(path, 'w', encoding='utf-8') as f:
        for sent in sentences:
            for form, lemma, upos in sent:
                f.write(f"{form}\t{lemma}\t{upos}\n")
            f.write("\n")


def main():
    base = Path(__file__).parent / "wip"
    output_dir = Path(__file__).parent / "machamp_data"
    output_dir.mkdir(exist_ok=True)

    csv_files = sorted(base.rglob("*.csv"))
    if not csv_files:
        print("No CSV files found under", base)
        return

    all_data = {}
    total_sents = 0
    total_tokens = 0
    for filepath in csv_files:
        sents = process_file(filepath)
        all_data[str(filepath)] = sents
        n_tok = sum(len(s) for s in sents)
        total_sents += len(sents)
        total_tokens += n_tok
        print(f"  {filepath.parent.name}/{filepath.name}: {len(sents)} sentences, {n_tok} tokens")

    print(f"\nTotal: {len(csv_files)} files, {total_sents} sentences, {total_tokens} tokens")

    random.seed(42)
    files = sorted(all_data.keys())
    random.shuffle(files)

    n = len(files)
    n_test = max(1, round(n * 0.1))
    n_dev = max(1, round(n * 0.1))

    test_files = files[:n_test]
    dev_files = files[n_test:n_test + n_dev]
    train_files = files[n_test + n_dev:]

    train_sents = [s for f in train_files for s in all_data[f]]
    dev_sents = [s for f in dev_files for s in all_data[f]]
    test_sents = [s for f in test_files for s in all_data[f]]

    write_split(train_sents, output_dir / "train.tsv")
    write_split(dev_sents, output_dir / "dev.tsv")
    write_split(test_sents, output_dir / "test.tsv")

    print(f"\nSplit (by file, seed=42):")
    print(f"  Train: {len(train_sents):>5} sentences  ({len(train_files)} files)")
    print(f"  Dev:   {len(dev_sents):>5} sentences  ({len(dev_files)} files)")
    print(f"  Test:  {len(test_sents):>5} sentences  ({len(test_files)} files)")
    print(f"\nWritten to {output_dir}/")

    print("\nTest files:")
    for f in sorted(test_files):
        print(f"  {Path(f).parent.name}/{Path(f).name}")
    print("Dev files:")
    for f in sorted(dev_files):
        print(f"  {Path(f).parent.name}/{Path(f).name}")


if __name__ == "__main__":
    main()

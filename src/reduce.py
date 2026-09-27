#!/usr/bin/env python3
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--input_paths", nargs="+", required=True)
parser.add_argument("--output_path", required=True)
args = parser.parse_args()

total = defaultdict(Counter)
for input_path in args.input_paths:
    with open(input_path, encoding="utf-8") as handle:
        daily_counts = json.load(handle)
    for hashtag, grouped_counts in daily_counts.items():
        total[hashtag].update({str(g): int(c) for g, c in grouped_counts.items()})

output_path = Path(args.output_path)
output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, "w", encoding="utf-8") as handle:
    json.dump({k: dict(v) for k, v in total.items()}, handle,
              ensure_ascii=False, sort_keys=True)
print(f"combined {len(args.input_paths)} files into {output_path}")

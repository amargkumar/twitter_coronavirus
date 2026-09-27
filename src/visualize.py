#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("--input_path", required=True)
parser.add_argument("--key", required=True)
parser.add_argument("--output_path")
parser.add_argument("--percent", action="store_true")
args = parser.parse_args()

# Lambda may not have a Korean font, so use an English title for that hashtag.
display_names = {"#코로나바이러스": "Korean #coronavirus"}
display_key = display_names.get(args.key, args.key)

with open(args.input_path, encoding="utf-8") as handle:
    counts = json.load(handle)
if args.key not in counts:
    raise KeyError(f"{args.key!r} is not present in {args.input_path}")

values = {}
for group, raw_count in counts[args.key].items():
    value = float(raw_count)
    if args.percent:
        denominator = float(counts.get("_all", {}).get(group, 0))
        value = value / denominator if denominator else 0.0
    values[group] = value

# Top 10 keys, displayed from low to high.
items = sorted(values.items(), key=lambda item: (item[1], item[0]))[-10:]
labels = [k for k, _ in items]
heights = [v for _, v in items]
for k, v in items:
    print(k, ":", v)

if args.output_path:
    output_path = Path(args.output_path)
else:
    safe_key = re.sub(r"\W+", "_", args.key).strip("_") or "hashtag"
    output_path = Path("img") / f"{Path(args.input_path).stem}-{safe_key}.png"
output_path.parent.mkdir(parents=True, exist_ok=True)

kind = "language" if "lang" in Path(args.input_path).name else "country"
plural = "languages" if kind == "language" else "countries"
figure, axis = plt.subplots(figsize=(10, 6))
axis.bar(labels, heights, color="#2F75B5")
axis.set_title(f"Top 10 {plural} for {display_key} tweets (2020)")
axis.set_xlabel("Language code" if kind == "language" else "Country code")
axis.set_ylabel("Share of tweets" if args.percent else "Number of tweets")
axis.tick_params(axis="x", labelrotation=45)
axis.grid(axis="y", alpha=0.25)
figure.tight_layout()
figure.savefig(output_path, dpi=150)
plt.close(figure)
print(f"saved {output_path}")

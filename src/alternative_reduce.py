#!/usr/bin/env python3
import argparse
import datetime
import glob
import json
import re
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("--hashtags", nargs="+", required=True)
parser.add_argument("--input_folder", default="outputs")
parser.add_argument("--output_path", default="img/hashtag-timeseries.png")
args = parser.parse_args()

display_names = {"#코로나바이러스": "Korean #coronavirus"}
pattern = re.compile(r"geoTwitter(\d{2}-\d{2}-\d{2})\.zip\.lang$")

# Step 1: scan all mapper outputs and build the dataset.
counts = defaultdict(dict)   # hashtag -> {day_of_year: count}
for path in sorted(glob.glob(f"{args.input_folder}/geoTwitter20-*.zip.lang")):
    match = pattern.search(Path(path).name)
    if not match:
        continue
    day = datetime.datetime.strptime(match.group(1), "%y-%m-%d").timetuple().tm_yday
    with open(path, encoding="utf-8") as handle:
        daily = json.load(handle)
    for hashtag in args.hashtags:
        counts[hashtag][day] = sum(int(v) for v in daily.get(hashtag, {}).values())

# Step 2: plot one line per hashtag.
days = list(range(1, 367))
figure, axis = plt.subplots(figsize=(12, 6))
for hashtag in args.hashtags:
    axis.plot(days, [counts[hashtag].get(d, 0) for d in days], linewidth=1.5,
              label=display_names.get(hashtag, hashtag))
axis.set_title("Daily tweets using each hashtag in 2020")

# Month boundaries as grid lines, month names centered in each month.
month_starts = [datetime.date(2020, m, 1).timetuple().tm_yday for m in range(1, 13)] + [367]
month_names = [datetime.date(2020, m, 1).strftime("%b") for m in range(1, 13)]
month_middles = [(a + b) / 2 for a, b in zip(month_starts[:-1], month_starts[1:])]
axis.set_xticks(month_starts, minor=True)
axis.set_xticks(month_middles)
axis.set_xticklabels(month_names)
axis.tick_params(axis="x", which="major", length=0)
axis.tick_params(axis="x", which="minor", length=6)
axis.grid(axis="x", which="minor", alpha=0.35)
axis.grid(axis="x", which="major", visible=False)

axis.set_xlabel("Month (2020)")
axis.set_ylabel("Number of tweets")
axis.set_xlim(1, 367)
axis.grid(axis="y", alpha=0.25)
axis.legend()
figure.tight_layout()
output_path = Path(args.output_path)
output_path.parent.mkdir(parents=True, exist_ok=True)
figure.savefig(output_path, dpi=150)
plt.close(figure)
print(f"saved {output_path}")

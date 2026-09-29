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

# Label the x-axis with dates: Jan 1, Feb 1, ... Dec 1, and Dec 31 at the end.
tick_dates = [datetime.date(2020, m, 1) for m in range(1, 13)] + [datetime.date(2020, 12, 31)]
axis.set_xticks([d.timetuple().tm_yday for d in tick_dates])
axis.set_xticklabels([f"{d:%b} {d.day}" for d in tick_dates], rotation=45, ha="right")
axis.grid(axis="x", alpha=0.35)

axis.set_xlabel("Date (2020)")
axis.set_ylabel("Number of tweets")
axis.set_xlim(1, 366)
axis.grid(axis="y", alpha=0.25)
axis.legend()
figure.tight_layout()
output_path = Path(args.output_path)
output_path.parent.mkdir(parents=True, exist_ok=True)
figure.savefig(output_path, dpi=150)
plt.close(figure)
print(f"saved {output_path}")

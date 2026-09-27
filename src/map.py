#!/usr/bin/env python3
import argparse
import datetime
import json
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--input_path", required=True)
parser.add_argument("--output_folder", default="outputs")
parser.add_argument("--hashtags_path", default="hashtags")
args = parser.parse_args()

with open(args.hashtags_path, encoding="utf-8") as handle:
    hashtags = [line.strip().casefold() for line in handle if line.strip()]

counter_lang = defaultdict(Counter)
counter_country = defaultdict(Counter)
invalid_lines = 0

with zipfile.ZipFile(args.input_path) as archive:
    for member in archive.infolist():
        if member.is_dir():
            continue
        print(datetime.datetime.now().isoformat(timespec="seconds"),
              args.input_path, member.filename, flush=True)
        with archive.open(member) as handle:
            for raw_line in handle:
                try:
                    tweet = json.loads(raw_line)
                except (json.JSONDecodeError, UnicodeDecodeError) as error:
                    invalid_lines += 1
                    continue

                text = str(tweet.get("text") or "").casefold()
                lang = str(tweet.get("lang") or "_unknown")

                # Some tweets have no place / country_code (e.g. international waters).
                place = tweet.get("place")
                country = "_unknown"
                if isinstance(place, dict):
                    country = str(place.get("country_code") or "_unknown")

                # Count every tweet once (the denominator).
                counter_lang["_all"][lang] += 1
                counter_country["_all"][country] += 1

                # search hashtags
                for hashtag in hashtags:
                    if hashtag in text:
                        counter_lang[hashtag][lang] += 1
                        counter_country[hashtag][country] += 1

output_folder = Path(args.output_folder)
output_folder.mkdir(parents=True, exist_ok=True)
output_base = output_folder / Path(args.input_path).name

for suffix, counts in ((".lang", counter_lang), (".country", counter_country)):
    output_path = Path(str(output_base) + suffix)
    print("saving", output_path, flush=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump({k: dict(v) for k, v in counts.items()}, handle,
                  ensure_ascii=False, sort_keys=True)

if invalid_lines:
    print(f"WARNING: skipped {invalid_lines} invalid JSON lines", file=sys.stderr)

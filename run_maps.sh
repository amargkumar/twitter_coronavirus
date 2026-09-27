#!/bin/bash
# Launch map.py on every 2020 file in parallel (nohup + &).
DATA_DIR="${DATA_DIR:-/data/Twitter dataset}"
OUTPUT_DIR="${OUTPUT_DIR:-outputs}"
LOG_DIR="${LOG_DIR:-logs}"
MAX_JOBS="${MAX_JOBS:-0}"          # 0 = launch everything at once
PYTHON="${PYTHON:-python3}"
mkdir -p "$OUTPUT_DIR" "$LOG_DIR"

for file in "$DATA_DIR"/geoTwitter20-*.zip; do
    base="$(basename "$file")"
    if [[ -s "$OUTPUT_DIR/$base.lang" && -s "$OUTPUT_DIR/$base.country" ]]; then
        echo "skipping completed $base"
        continue
    fi
    echo "starting $base"
    nohup "$PYTHON" src/map.py --input_path "$file" --output_folder "$OUTPUT_DIR" \
        > "$LOG_DIR/$base.log" 2>&1 &
    if (( MAX_JOBS > 0 )); then
        while (( $(jobs -pr | wc -l) >= MAX_JOBS )); do wait -n; done
    fi
done
wait
echo "all mapper processes have finished"

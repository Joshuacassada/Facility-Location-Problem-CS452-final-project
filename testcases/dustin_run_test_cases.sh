#!/bin/bash

# === CONFIGURATION (edit these four lines only) ========================
SOLVER="../dustin_approx_sol/facility_location_approx.py"
OUTPUT_DIR="../dustin_approx_sol/test_outputs"
TIME_LIMIT=1.0
SEED=123
# =======================================================================

mkdir -p "$OUTPUT_DIR"

echo "Running approximation solver on ALL test cases in this folder..."
echo

# Loop through every .txt file directly in the testcases folder
for f in *.txt; do
    if [ -f "$f" ]; then
        base=$(basename "$f" .txt)
        echo "Running $f ..."
        python3 $SOLVER -t $TIME_LIMIT "$f" --seed $SEED \
            > "$OUTPUT_DIR/${base}_out.txt"
    fi
done

echo
echo "All test cases finished!"
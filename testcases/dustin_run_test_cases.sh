#!/bin/bash

# === CONFIGURATION (edit these four lines only) ========================
SOLVER="../dustin_approx_sol/facility_location_approx.py"
OUTPUT_DIR="../dustin_approx_sol/test_outputs"
TIME_LIMIT=0.5
# =======================================================================

mkdir -p "$OUTPUT_DIR"

echo "Running approximation solver on ALL test cases in this folder..."
echo

# Loop through every .txt file directly in the testcases folder
for f in *.txt; do
    if [ -f "$f" ]; then
        base=$(basename "$f" .txt)
        echo "Running $f ..."
        python3 $SOLVER -t $TIME_LIMIT "$f" \
            > "$OUTPUT_DIR/${base}_out.txt"
    fi
done

# test_case_41.txt is intentionally larger so that the exact solver exceeds 5 minutes

echo
echo "All test cases finished!"
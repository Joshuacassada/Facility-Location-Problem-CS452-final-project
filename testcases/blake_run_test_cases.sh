#!/bin/bash

# === CONFIGURATION (edit these lines if needed) =========================
SOLVER="../blake_approx_solution/facility_location_approx_blake.py"
OUTPUT_DIR="../blake_approx_solution/test"
TIME_LIMIT=1.0
SEED=142
# =======================================================================

mkdir -p "$OUTPUT_DIR"

echo "Running Blake's approximation solver on all test cases..."
echo

# Loop through every .txt file directly in this testcases directory
for f in *.txt; do
    if [ -f "$f" ]; then
        base=$(basename "$f" .txt)
        echo "Running $f ..."
        python3 "$SOLVER" -t "$TIME_LIMIT" "$f" --seed "$SEED" \
            > "$OUTPUT_DIR/${base}_out.txt"
    fi
done

echo
echo "All test cases completed!"

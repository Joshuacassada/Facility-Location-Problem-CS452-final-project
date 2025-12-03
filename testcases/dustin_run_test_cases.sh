#!/bin/bash

# === CONFIGURATION (edit these four lines only) ========================
SOLVER="../dustin_approx_sol/facility_location_approx.py"
OUTPUT_DIR="../dustin_approx_sol/test_outputs"
TIME_LIMIT=1.0
SEED=123
# =======================================================================

mkdir -p "$OUTPUT_DIR/small"
mkdir -p "$OUTPUT_DIR/large"
mkdir -p "$OUTPUT_DIR/extreme"

echo "Running approximation solver on all test cases..."
echo

# ------------------------------
# SMALL cases
# ------------------------------
echo "===== SMALL CASES ====="
for f in small/*.txt; do
    base=$(basename "$f" .txt)
    echo "Running $f ..."
    python3 $SOLVER -t $TIME_LIMIT $f --seed $SEED \
        > "$OUTPUT_DIR/small/${base}_out.txt"
done

# ------------------------------
# LARGE cases
# ------------------------------
echo
echo "===== LARGE CASES ====="
for f in large/*.txt; do
    base=$(basename "$f" .txt)
    echo "Running $f ..."
    python3 $SOLVER -t $TIME_LIMIT $f --seed $SEED \
        > "$OUTPUT_DIR/large/${base}_out.txt"
done

# ------------------------------
# EXTREME case
# ------------------------------
echo
echo "===== EXTREME CASE ====="
echo "# NOTE: The EXACT solver would take ~5 minutes on this test."
for f in extreme/*.txt; do
    base=$(basename "$f" .txt)
    python3 $SOLVER -t 2.0 $f --seed $SEED \
        > "$OUTPUT_DIR/extreme/${base}_out.txt"
done

echo
echo "All test cases finished!"
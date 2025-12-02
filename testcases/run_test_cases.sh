#!/usr/bin/env bash
# run_test_cases.sh
#
# Runs the approximation solver on all test cases.
# Prints results directly to the terminal (NO .out files created)

set -euo pipefail

APPROX="../facility_location_approx.py"
TIME_LIMIT=1   # seconds per test; adjust as needed

echo "Running SMALL test cases..."
for f in test_small_*.txt; do
    echo
    echo "----------------------------------------"
    echo "  Running $f"
    echo "----------------------------------------"
    python "$APPROX" -t "$TIME_LIMIT" "$f"
done

echo
echo "Running LARGE test cases..."
for f in test_large_*.txt; do
    echo
    echo "----------------------------------------"
    echo "  Running $f"
    echo "----------------------------------------"
    python "$APPROX" -t "$TIME_LIMIT" "$f"
done

echo
echo "# NOTE: This case would take more than 60 minutes for the exact solver:"
echo "#   test_extreme_60min_optimal_only.txt"
echo "# Uncomment below to run the approximation on it."

# python "$APPROX" -t "$TIME_LIMIT" test_extreme_60min_optimal_only.txt
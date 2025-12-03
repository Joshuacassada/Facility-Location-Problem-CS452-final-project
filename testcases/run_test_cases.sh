#!/bin/bash

echo "Running approximation solver on all test cases..."
echo

SOLVER="../facility_location_approx.py"

# ------------------------------
# Run SMALL cases
# ------------------------------
echo "===== SMALL TEST CASES (should be fast) ====="
for f in small/*.txt; do
    echo "Running $f ..."
    python3 $SOLVER -t 1.0 $f --seed 123
done

# ------------------------------
# Run LARGE cases
# ------------------------------
echo
echo "===== LARGE TEST CASES (optimal solver would struggle) ====="
for f in large/*.txt; do
    echo "Running $f ..."
    python3 $SOLVER -t 1.0 $f --seed 123
done

# ------------------------------
# EXTREME case — mark for professor
# ------------------------------
echo
echo "===== EXTREME HARD TEST CASE ====="
echo "# This test case is designed so the EXACT SOLVER would take ~5 minutes"
echo "# DO NOT attempt full optimal search — approximation runs fine"
python3 $SOLVER -t 2.0 extreme/extreme_hard.txt --seed 123

echo
echo "All tests completed."
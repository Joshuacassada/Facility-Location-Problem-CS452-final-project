#!/bin/bash

# Run all test cases with facility_location.py

echo "Running all Facility Location test cases..."

# Path to main program (edit if needed)
PROGRAM="../facility_location_exact.py"

for file in *.txt; do
    echo "=== Running $file ==="
    python3 $PROGRAM "$file"
    echo ""
done

echo "Done."

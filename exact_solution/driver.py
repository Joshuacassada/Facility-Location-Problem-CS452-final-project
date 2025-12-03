import time
import csv
import os
from facility_location_exact import read_input, solve_flp

INPUT_DIR = "flp_test_inputs"   
OUTPUT_CSV = "results.csv"

def main():
    input_files = sorted(
        [f for f in os.listdir(INPUT_DIR) if f.endswith(".txt")]
    )

    results = []

    print(f"Found {len(input_files)} input files. Starting tests...\n")

    for fname in input_files:
        full_path = os.path.join(INPUT_DIR, fname)
        print(f"Running {fname}...")

        # Read input
        facilities, customers = read_input(full_path)

        # Time solver
        start = time.time()
        best_cost, best_set = solve_flp(facilities, customers)
        end = time.time()

        elapsed = end - start

        print(f"  Finished {fname}: {elapsed:.3f} seconds")

        results.append([
            fname,
            len(facilities),
            len(customers),
            best_cost,
            len(best_set),
            elapsed
        ])

    # Write CSV
    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "filename",
            "facility_count",
            "customer_count",
            "best_cost",
            "open_facilities",
            "runtime_seconds"
        ])
        writer.writerows(results)

    print("\nAll tests complete!")
    print(f"Results saved to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()

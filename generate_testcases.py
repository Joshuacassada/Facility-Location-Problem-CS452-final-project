#!/usr/bin/env python3
import os
import random

# -----------------------------------------
# Helper to write a single test case
# -----------------------------------------
def write_case(path, n_clients, n_facilities, coverage_dist, grid_size=100):
    with open(path, "w") as f:
        f.write(f"{n_clients} {n_facilities}\n")

        # clients
        for i in range(1, n_clients + 1):
            x = random.uniform(0, grid_size)
            y = random.uniform(0, grid_size)
            f.write(f"C{i} {x:.2f} {y:.2f}\n")

        # facilities
        for j in range(1, n_facilities + 1):
            x = random.uniform(0, grid_size)
            y = random.uniform(0, grid_size)
            f.write(f"F{j} {x:.2f} {y:.2f} 0\n")

        f.write(f"{coverage_dist}\n")


# -----------------------------------------
# Generate all test cases
# -----------------------------------------
def main():
    random.seed(42)  # reproducible

    base = "testcases"
    os.makedirs(base, exist_ok=True)

    small_dir = os.path.join(base, "small")
    large_dir = os.path.join(base, "large")
    extreme_dir = os.path.join(base, "extreme")

    os.makedirs(small_dir, exist_ok=True)
    os.makedirs(large_dir, exist_ok=True)
    os.makedirs(extreme_dir, exist_ok=True)

    # -------------------------------
    # 25 SMALL CASES (easy for optimal)
    # -------------------------------
    for i in range(1, 26):
        n_clients = random.randint(5, 12)
        n_facilities = random.randint(3, 8)
        coverage = random.uniform(5, 15)
        filename = f"small_{i:02d}.txt"
        write_case(os.path.join(small_dir, filename),
                   n_clients, n_facilities, coverage)

    # -------------------------------
    # 25 LARGE CASES (optimal solver struggles)
    # -------------------------------
    for i in range(1, 26):
        n_clients = random.randint(40, 70)
        n_facilities = random.randint(25, 40)
        coverage = random.uniform(8, 20)
        filename = f"large_{i:02d}.txt"
        write_case(os.path.join(large_dir, filename),
                   n_clients, n_facilities, coverage, grid_size=200)

    # -------------------------------
    # EXTREME HARD CASE (optimal ~5 min)
    #
    # This size is known to explode optimal facility-location solvers:
    #      ~150 clients
    #      ~100 facilities
    #
    # The combination space becomes enormous.
    # -------------------------------
    filename = "extreme_hard.txt"
    write_case(os.path.join(extreme_dir, filename),
               n_clients=150,
               n_facilities=100,
               coverage_dist=12.0,
               grid_size=300)

    print("Test cases generated successfully!")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
import random
import math

def gen_case(f, c, xmin, xmax, ymin, ymax):
    """Generate a single facility-location instance.

    f = number of facilities
    c = number of customers
    coordinates are uniform random in bounding box
    demands are random integers (1–10)
    facility opening costs are random (5–50)
    """
    fac_costs = [round(random.uniform(5, 50), 2) for _ in range(f)]

    fac_coords = [
        (round(random.uniform(xmin, xmax), 2),
         round(random.uniform(ymin, ymax), 2))
        for _ in range(f)
    ]

    demands = [random.randint(1, 10) for _ in range(c)]

    cust_coords = [
        (round(random.uniform(xmin, xmax), 2),
         round(random.uniform(ymin, ymax), 2))
        for _ in range(c)
    ]

    return fac_costs, fac_coords, demands, cust_coords


def write_case(filename, fac_costs, fac_coords, demands, cust_coords):
    f = len(fac_costs)
    c = len(demands)

    with open(filename, "w") as f_out:
        f_out.write(f"{f} {c}\n")
        f_out.write(" ".join(map(str, fac_costs)) + "\n")

        for (x, y) in fac_coords:
            f_out.write(f"{x} {y}\n")

        f_out.write(" ".join(map(str, demands)) + "\n")

        for (x, y) in cust_coords:
            f_out.write(f"{x} {y}\n")


def main():
    random.seed(42)  # deterministic reproducibility

    # --- 25 SMALL TEST CASES (optimal-known group) ---
    # Good sizes for exact solver (optimal):
    small_params = [
        (5, 15),   # very easy
        (6, 20),
        (7, 25),
        (8, 30),
        (10, 40)
    ]

    idx = 1
    for (f, c) in small_params:
        for _ in range(5):  # 5 cases per size → 25 total
            fac_costs, fac_coords, demands, cust_coords = gen_case(f, c, 0, 100, 0, 100)
            write_case(f"test_cases/test_small_{idx:02d}.txt",
                       fac_costs, fac_coords, demands, cust_coords)
            idx += 1

    # --- 50 LARGE TEST CASES (hard for optimal) ---
    large_params = [
        (25, 150),
        (30, 200),
        (40, 300),
        (50, 400),
        (75, 600)
    ]

    idx = 1
    for (f, c) in large_params:
        for _ in range(10):  # 10 per size → 50 total
            fac_costs, fac_coords, demands, cust_coords = gen_case(f, c, -50, 150, -50, 150)
            write_case(f"test_cases/test_large_{idx:02d}.txt",
                       fac_costs, fac_coords, demands, cust_coords)
            idx += 1

    # --- EXTREME CASE (exact solver > 60 minutes) ---
    # This one must be labelled in run_test_cases.sh
    f, c = 150, 2000
    fac_costs, fac_coords, demands, cust_coords = gen_case(f, c, -100, 200, -100, 200)
    write_case("test_cases/test_extreme_60min_optimal_only.txt",
               fac_costs, fac_coords, demands, cust_coords)

    print("✔ All test cases generated.")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.abspath(".."))

import random
import time
import matplotlib.pyplot as plt

from facility_location_approx import Instance, Facility, Client, anytime
from exact_solution.facility_location_exact import distance   # only for distance()

# --- Parameters ---
customer_count = 5
facility_sizes = list(range(2, 29))  # 2–28
coverage = 30

# --- FIXED TIME LIMIT ---
TIME_LIMIT = 0.05  # 50 ms (change if needed)

runtimes = []

# --- Instance generator ---
def generate_test_case(num_facilities, num_customers):
    facilities = [(f"F{i+1}", random.uniform(0, 100), random.uniform(0, 100))
                  for i in range(num_facilities)]

    customers = [(f"C{i+1}", random.uniform(0, 100), random.uniform(0, 100))
                 for i in range(num_customers)]

    # Ensure feasibility
    for i, (cx, cy) in enumerate([(c[1], c[2]) for c in customers]):
        if min(distance((cx, cy), (f[1], f[2])) for f in facilities) > coverage:
            fx, fy = facilities[0][1], facilities[0][2]
            customers[i] = (
                customers[i][0],
                fx + random.uniform(-coverage/2, coverage/2),
                fy + random.uniform(-coverage/2, coverage/2),
            )

    return facilities, customers


print("\nRunning APPROX solver...\n")

for f in facility_sizes:
    print(f"Facilities = {f}")

    facilities, customers = generate_test_case(f, customer_count)

    inst = Instance(
        clients=[Client(n,x,y) for (n,x,y) in customers],
        facilities=[Facility(n,x,y,False) for (n,x,y) in facilities],
        coverage_distance=coverage
    )

    # --- RUN APPROX SOLVER WITH FIXED TIME LIMIT ---
    t0 = time.perf_counter()
    anytime(inst, TIME_LIMIT, seed=0)
    t1 = time.perf_counter()

    runtime = t1 - t0
    runtimes.append(runtime)

    print(f"  Runtime: {runtime:.6f} sec")


# --- Plot ---
def generate_all_plots():
    plt.figure(figsize=(10, 5))
    plt.plot(facility_sizes, runtimes, '-s', label="Approx Solver", color='orange')
    plt.xlabel("Number of Facilities")
    plt.ylabel("Wall Clock Time (seconds)")
    plt.title("Approximate FLP Solver Runtime")
    plt.grid(True)
    plt.legend()

    plt.ylim(-100, 2000)

    plt.subplots_adjust(top=0.92, bottom=0.15)

    output_file = "approx_runtime.png"
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    print(f"\nSaved: {output_file}")

    plt.show()

if __name__ == "__main__":
    generate_all_plots()
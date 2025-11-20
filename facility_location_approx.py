#!/usr/bin/env python3
"""
Anytime stochastic greedy approximation solver
for the 2D Facility Location Problem.

Input format (from README):

f c
<facility opening costs>
<f lines of facility coords>
<customer demands>
<c lines of customer coords>

Distances = Euclidean.

Output format:

<total_cost>
facility_index: c1 c2 c3 ...
"""

import sys
import time
import math
import random
import argparse
from typing import List, Tuple


# ----------------------------------------------------------
# Problem Representation
# ----------------------------------------------------------

class FacilityLocationInstance:
    def __init__(
        self,
        facility_costs: List[float],
        facility_coords: List[Tuple[float, float]],
        customer_demands: List[float],
        customer_coords: List[Tuple[float, float]],
    ):
        self.f = len(facility_costs)
        self.c = len(customer_coords)
        self.facility_costs = facility_costs
        self.facility_coords = facility_coords
        self.customer_demands = customer_demands
        self.customer_coords = customer_coords

        # Precompute distance * demand cost matrix
        self.service_cost = [
            [
                customer_demands[i] *
                math.dist(customer_coords[i], facility_coords[j])
                for j in range(self.f)
            ]
            for i in range(self.c)
        ]


# ----------------------------------------------------------
# Input / Output
# ----------------------------------------------------------

def read_instance(stream) -> FacilityLocationInstance:
    """
    Reads the 2D coordinate FLP format.

    f c
    <facility opening costs>
    <f lines of facility coords>
    <customer demands>
    <c lines of customer coords>
    """
    # Read first line: f c
    header = stream.readline().strip()
    while header == "" or header.startswith("#"):
        header = stream.readline().strip()

    f, c = map(int, header.split())

    # Facility opening costs
    facility_costs = list(map(float, stream.readline().split()))
    if len(facility_costs) != f:
        raise ValueError("Incorrect number of facility opening costs.")

    # Facility coordinates
    facility_coords = []
    for _ in range(f):
        x, y = map(float, stream.readline().split())
        facility_coords.append((x, y))

    # Customer demands
    customer_demands = list(map(float, stream.readline().split()))
    if len(customer_demands) != c:
        raise ValueError("Incorrect number of customer demands.")

    # Customer coordinates
    customer_coords = []
    for _ in range(c):
        x, y = map(float, stream.readline().split())
        customer_coords.append((x, y))

    return FacilityLocationInstance(
        facility_costs, facility_coords,
        customer_demands, customer_coords
    )


def write_solution(out, cost, open_facilities, assignment):
    """
    Output format:

    <total_cost>
    facility_index: customer_1 customer_2 ...
    """
    print(f"{cost:.2f}", file=out)

    f = len(open_facilities)
    groups = {j: [] for j in range(f) if open_facilities[j]}

    for i, j in enumerate(assignment):
        groups[j].append(i)

    for j in groups:
        custs = " ".join(str(i) for i in groups[j])
        print(f"{j}: {custs}", file=out)


# ----------------------------------------------------------
# Greedy Anytime Approximation
# ----------------------------------------------------------

def evaluate(inst: FacilityLocationInstance,
             open_fac,
             assignment) -> float:
    """Compute true total cost (without noise)."""
    total = 0.0
    # opening costs
    for j in range(inst.f):
        if open_fac[j]:
            total += inst.facility_costs[j]
    # assignment costs
    for i in range(inst.c):
        total += inst.service_cost[i][assignment[i]]
    return total


def greedy_build(inst: FacilityLocationInstance,
                 deadline: float):
    """
    One greedy construction with randomization:

    - Random initial facility
    - Tiny random noise on service costs to induce variation
    - Greedy additions with random tie-breaking
    """
    f, c = inst.f, inst.c

    # Tiny noise to induce randomness in choices
    noise_scale = 1e-4
    noise = [
        [random.uniform(-noise_scale, noise_scale) for _ in range(f)]
        for _ in range(c)
    ]

    # ------------------------------------------------------
    # Step 1: choose a random initial facility (stochastic)
    # ------------------------------------------------------
    start_fac = random.randrange(f)

    open_fac = [False] * f
    open_fac[start_fac] = True
    assignment = [start_fac] * c
    current_cost = evaluate(inst, open_fac, assignment)

    # ------------------------------------------------------
    # Step 2: greedy additions (with noisy comparisons)
    # ------------------------------------------------------
    while time.time() < deadline:
        best_delta = 0.0
        best_js = []

        for j in range(f):
            if open_fac[j]:
                continue
            if time.time() >= deadline:
                break

            delta_assign = 0.0
            for i in range(c):
                old = assignment[i]
                new_cost = inst.service_cost[i][j] + noise[i][j]
                old_cost = inst.service_cost[i][old] + noise[i][old]
                if new_cost < old_cost:
                    delta_assign += (new_cost - old_cost)

            delta_total = inst.facility_costs[j] + delta_assign

            if delta_total < best_delta - 1e-12:
                best_delta = delta_total
                best_js = [j]
            elif abs(delta_total - best_delta) < 1e-12:
                best_js.append(j)

        # No improving facility found -> stop
        if best_delta >= -1e-12 or not best_js:
            break

        # Random tie-breaking among best facilities
        chosen = random.choice(best_js)
        open_fac[chosen] = True

        # Reassign customers using same noisy costs
        for i in range(c):
            old = assignment[i]
            new_cost = inst.service_cost[i][chosen] + noise[i][chosen]
            old_cost = inst.service_cost[i][old] + noise[i][old]
            if new_cost < old_cost:
                assignment[i] = chosen

        # Update approximate cost (for internal consistency)
        current_cost += best_delta

    # Return the *true* cost using the actual cost function
    true_cost = evaluate(inst, open_fac, assignment)
    return true_cost, open_fac, assignment


def anytime(inst: FacilityLocationInstance,
            t: float,
            seed=None):
    """
    Anytime wrapper:
    - Keeps running greedy_build while time remains.
    - Keeps the best solution found so far.
    """
    if seed is not None:
        random.seed(seed)

    start = time.time()
    deadline = start + t

    best_cost, best_open, best_assign = greedy_build(inst, deadline)

    while time.time() < deadline:
        cost, open_f, assign = greedy_build(inst, deadline)
        if cost < best_cost:
            best_cost, best_open, best_assign = cost, open_f, assign

    return best_cost, best_open, best_assign


# ----------------------------------------------------------
# Main
# ----------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Anytime stochastic greedy approximation for facility location."
    )
    parser.add_argument(
        "-t",
        type=float,
        required=True,
        help="Time limit in seconds",
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        default="-",
        help="Input file (or - / omitted for stdin)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed (optional, for reproducibility)",
    )
    args = parser.parse_args()

    if args.input_file == "-" or args.input_file is None:
        inst = read_instance(sys.stdin)
    else:
        with open(args.input_file) as f:
            inst = read_instance(f)

    cost, open_fac, assignment = anytime(inst, args.t, seed=args.seed)
    write_solution(sys.stdout, cost, open_fac, assignment)


if __name__ == "__main__":
    main()
"""
Anytime stochastic greedy approximation for the Facility Location Problem.

Requirements satisfied:
- Polynomial time per run (greedy incremental facility opening).
- Anytime behavior via -t time limit: runs multiple greedy restarts,
  keeps best solution seen so far, and exits before the deadline.
- Stochastic component: random tie-breaking and randomized initial choice.
- Greedy: repeatedly adds the facility that most reduces total cost.

NOTE: You MUST adapt `read_instance` and `write_solution` to match
the exact input/output format specified on Canvas (the same used by
your exact/optimal solution architect code.
"""

import sys
import time
import math
import random
import argparse
from typing import List, Tuple, Optional


# ----------------------------------------------------------------------
# Problem representation
# ----------------------------------------------------------------------

class FacilityLocationInstance:
    """
    Generic facility location instance with:
      - m facilities
      - n customers
      - open_cost[j] : fixed cost to open facility j
      - service_cost[i][j] : cost to serve customer i from facility j
    """

    def __init__(
        self,
        open_cost: List[float],
        service_cost: List[List[float]],
    ):
        self.m = len(open_cost)
        self.n = len(service_cost)
        self.open_cost = open_cost
        self.service_cost = service_cost
        if self.n == 0 or self.m == 0:
            raise ValueError("Instance must have at least one facility and one customer.")


# ----------------------------------------------------------------------
# I/O – ADAPT TO YOUR CANVAS FORMAT
# ----------------------------------------------------------------------

def read_instance(in_stream) -> FacilityLocationInstance:
    """
    TODO: Replace this with the *exact* input format from Canvas.

    Example format (you may NOT be using this in your class):
        Line 1: m n
        Line 2: m space-separated opening costs
        Next n lines: m space-separated service costs for each customer

    Example:
        3 4
        10 12 8
        5 7 4
        6 2 9
        3 3 3
        9 1 5

    This means:
      - 3 facilities, 4 customers
      - open_cost = [10, 12, 8]
      - service_cost[0] = [5, 7, 4], etc.
    """
    data = []
    for line in in_stream:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        data.append(line)

    if not data:
        raise ValueError("Empty input.")

    # Parse the example format
    it = iter(data)
    m_str, n_str = next(it).split()
    m, n = int(m_str), int(n_str)

    open_cost = list(map(float, next(it).split()))
    if len(open_cost) != m:
        raise ValueError("Expected {} opening costs, got {}".format(m, len(open_cost)))

    service_cost: List[List[float]] = []
    for _ in range(n):
        row = list(map(float, next(it).split()))
        if len(row) != m:
            raise ValueError("Expected {} service costs per customer.".format(m))
        service_cost.append(row)

    return FacilityLocationInstance(open_cost, service_cost)


def write_solution(
    out_stream,
    total_cost: float,
    open_facilities: List[bool],
    assignment: List[int],
):
    """
    TODO: Replace this with the *exact* output format from Canvas.

    Example simple format:

      Line 1: total_cost
      Line 2: indices of open facilities (0-based) separated by spaces
      Next n lines: facility index serving customer i

    Adjust to whatever your optimal solver uses.
    """
    m = len(open_facilities)
    n = len(assignment)

    open_indices = [str(j) for j in range(m) if open_facilities[j]]

    print(f"{total_cost:.6f}", file=out_stream)
    print(" ".join(open_indices), file=out_stream)
    for i in range(n):
        print(assignment[i], file=out_stream)


# ----------------------------------------------------------------------
# Greedy anytime approximation
# ----------------------------------------------------------------------

def evaluate_solution(
    inst: FacilityLocationInstance,
    open_facilities: List[bool],
    assignment: List[int]
) -> float:
    """Compute total cost for a complete solution."""
    m, n = inst.m, inst.n
    assert len(open_facilities) == m
    assert len(assignment) == n

    total = 0.0
    # Opening costs
    for j in range(m):
        if open_facilities[j]:
            total += inst.open_cost[j]
    # Assignment costs
    for i in range(n):
        j = assignment[i]
        total += inst.service_cost[i][j]
    return total


def greedy_construct(
    inst: FacilityLocationInstance,
    deadline: float,
) -> Tuple[float, List[bool], List[int]]:
    """
    Single greedy run:
    1. Choose an initial facility to open (randomized among near-best choices).
    2. Assign all customers to that facility.
    3. Repeatedly add the facility that yields the largest cost reduction.
       Stop when no facility improves the cost or when near the deadline.

    Time complexity per run is polynomial: O(m^2 * n).
    """

    m, n = inst.m, inst.n

    # ---------------------------
    # Step 1: choose initial facility
    # ---------------------------
    # For each facility j, compute cost if only j is open
    #   cost_j = open_cost[j] + sum_i service_cost[i][j]
    # Then pick randomly among facilities whose cost_j is within
    # some epsilon of the best.
    base_costs = []
    for j in range(m):
        if time.time() >= deadline:
            break
        cost_j = inst.open_cost[j]
        for i in range(n):
            cost_j += inst.service_cost[i][j]
        base_costs.append((cost_j, j))

    base_costs.sort(key=lambda x: x[0])
    if not base_costs:
        # fallback (shouldn't happen with valid instance)
        j0 = 0
    else:
        best_cost = base_costs[0][0]
        # allow some slack (e.g., up to 5% worse than best) for randomness
        candidates = [j for (c, j) in base_costs
                      if c <= best_cost * 1.05 + 1e-9]
        j0 = random.choice(candidates)

    # Open initial facility
    open_fac = [False] * m
    open_fac[j0] = True

    # Assign all customers to j0
    assignment = [j0] * n
    current_total = evaluate_solution(inst, open_fac, assignment)

    # ---------------------------
    # Step 2: greedy additions
    # ---------------------------
    while time.time() < deadline:
        best_delta = 0.0
        best_js: List[int] = []  # all facilities achieving best_delta (for random tie-break)

        # For each unopened facility, check cost if we open it
        for j in range(m):
            if open_fac[j]:
                continue
            if time.time() >= deadline:
                break

            # Compute cost if we open facility j and reassign customers greedily
            # to min(current service cost, service_cost to j).
            # We don't commit yet; just compute delta.
            delta_assign = 0.0
            for i in range(n):
                # current cost serving i
                current_c_ij = inst.service_cost[i][assignment[i]]
                new_c_ij = inst.service_cost[i][j]
                if new_c_ij < current_c_ij:
                    delta_assign += (new_c_ij - current_c_ij)
                # else no change

            # Opening cost is added
            delta_total = inst.open_cost[j] + delta_assign  # delta relative to current_total

            if delta_total < best_delta - 1e-9:
                # Strictly better
                best_delta = delta_total
                best_js = [j]
            elif abs(delta_total - best_delta) <= 1e-9:
                # Tie: add for random tie-breaking
                best_js.append(j)

        # If no improving facility, we are done
        if best_delta >= -1e-9 or not best_js:
            break

        # Choose facility randomly among the best (stochastic tie-breaking)
        chosen_j = random.choice(best_js)

        # Actually open chosen_j and reassign customers
        open_fac[chosen_j] = True
        for i in range(n):
            old_fac = assignment[i]
            if inst.service_cost[i][chosen_j] < inst.service_cost[i][old_fac]:
                assignment[i] = chosen_j

        current_total += best_delta

    # End greedy run
    return current_total, open_fac, assignment


def anytime_stochastic_greedy(
    inst: FacilityLocationInstance,
    time_limit: float,
    seed: Optional[int] = None,
) -> Tuple[float, List[bool], List[int]]:
    """
    Anytime wrapper:
      - Runs greedy_construct repeatedly with different randomness
      - Keeps best solution seen so far
      - Stops before the time_limit is exceeded
    """

    if seed is not None:
        random.seed(seed)

    start = time.time()
    deadline = start + max(0.01, time_limit)  # tiny minimum

    # Initial run
    best_cost, best_open, best_assign = greedy_construct(inst, deadline)

    # Additional random restarts if time allows
    runs = 1
    while time.time() < deadline:
        runs += 1
        cost, open_fac, assign = greedy_construct(inst, deadline)
        if cost < best_cost:
            best_cost = cost
            best_open = open_fac
            best_assign = assign

    # You can print to stderr if you want debug info (not required)
    # sys.stderr.write(f"Anytime runs: {runs}, best_cost: {best_cost:.4f}\n")

    return best_cost, best_open, best_assign


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Anytime stochastic greedy approximation for facility location."
    )
    parser.add_argument(
        "-t",
        type=float,
        required=True,
        help="Time limit in seconds (anytime requirement).",
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        default=None,
        help="Optional input file (otherwise read from stdin).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility (optional).",
    )
    return parser.parse_args(argv)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    args = parse_args(argv)

    # Read instance
    if args.input_file is None or args.input_file == "-":
        inst = read_instance(sys.stdin)
    else:
        with open(args.input_file, "r") as f:
            inst = read_instance(f)

    # Run anytime approximation
    best_cost, best_open, best_assign = anytime_stochastic_greedy(
        inst,
        time_limit=args.t,
        seed=args.seed,
    )

    # Output solution in required format
    write_solution(sys.stdout, best_cost, best_open, best_assign)


if __name__ == "__main__":
    main()


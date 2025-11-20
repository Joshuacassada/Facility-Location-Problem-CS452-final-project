#!/usr/bin/env python3
"""
Anytime local-search approximation for the Facility Location Problem.

Different idea from the provided "stochastic greedy add" template:
- Starts from a simple solution (all facilities open).
- Uses local search with OPEN / CLOSE moves.
- Greedily applies the best improving move, with random tie-breaking.
- Runs multiple random restarts until a -t time limit is hit (anytime).
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
    Facility location instance:
      - m facilities
      - n customers
      - open_cost[j] : fixed cost to open facility j
      - service_cost[i][j] : cost to serve customer i from facility j
    """

    def __init__(self, open_cost: List[float], service_cost: List[List[float]]):
        self.m = len(open_cost)
        self.n = len(service_cost)
        self.open_cost = open_cost
        self.service_cost = service_cost
        if self.m == 0 or self.n == 0:
            raise ValueError("Instance must have at least one facility and one customer.")


# ----------------------------------------------------------------------
# I/O – ADAPT THESE TO YOUR CANVAS FORMAT
# ----------------------------------------------------------------------

def read_instance(in_stream) -> FacilityLocationInstance:

    data = []
    for line in in_stream:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        data.append(line)

    if not data:
        raise ValueError("Empty input.")

    it = iter(data)
    m_str, n_str = next(it).split()
    m, n = int(m_str), int(n_str)

    open_cost = list(map(float, next(it).split()))
    if len(open_cost) != m:
        raise ValueError(f"Expected {m} opening costs, got {len(open_cost)}")

    service_cost: List[List[float]] = []
    for _ in range(n):
        row = list(map(float, next(it).split()))
        if len(row) != m:
            raise ValueError(f"Expected {m} service costs per customer.")
        service_cost.append(row)

    return FacilityLocationInstance(open_cost, service_cost)


def write_solution(
    out_stream,
    total_cost: float,
    open_facilities: List[bool],
    assignment: List[int],
):
    m = len(open_facilities)
    n = len(assignment)
    open_indices = [str(j) for j in range(m) if open_facilities[j]]

    print(f"{total_cost:.6f}", file=out_stream)
    print(" ".join(open_indices), file=out_stream)
    for i in range(n):
        print(assignment[i], file=out_stream)


# ----------------------------------------------------------------------
# Cost and assignment helpers
# ----------------------------------------------------------------------

def evaluate_solution(
    inst: FacilityLocationInstance,
    open_facilities: List[bool],
    assignment: List[int],
) -> float:
    """Compute total cost for a complete solution."""
    m, n = inst.m, inst.n
    assert len(open_facilities) == m
    assert len(assignment) == n

    total = 0.0
    for j in range(m):
        if open_facilities[j]:
            total += inst.open_cost[j]
    for i in range(n):
        j = assignment[i]
        total += inst.service_cost[i][j]
    return total


def greedy_assign_all(
    inst: FacilityLocationInstance,
    open_facilities: List[bool],
) -> List[int]:
    """Assign each customer to the cheapest open facility."""
    m, n = inst.m, inst.n
    assignment = [-1] * n
    open_indices = [j for j in range(m) if open_facilities[j]]
    if not open_indices:
        raise ValueError("No open facilities to assign customers to.")

    for i in range(n):
        best_j = open_indices[0]
        best_cost = inst.service_cost[i][best_j]
        for j in open_indices[1:]:
            c = inst.service_cost[i][j]
            if c < best_cost:
                best_cost = c
                best_j = j
        assignment[i] = best_j
    return assignment


# ----------------------------------------------------------------------
# Initial / randomized solutions
# ----------------------------------------------------------------------

def initial_solution_all_open(inst: FacilityLocationInstance):
    """Start with all facilities open and customers assigned to nearest."""
    m = inst.m
    open_fac = [True] * m
    assignment = greedy_assign_all(inst, open_fac)
    cost = evaluate_solution(inst, open_fac, assignment)
    return open_fac, assignment, cost


def random_initial_solution(inst: FacilityLocationInstance, p_open: float = 0.5):
    """
    Random initial solution: each facility independently open with probability p_open.
    Ensure at least one facility is open; then assign customers greedily.
    """
    m = inst.m
    open_fac = [random.random() < p_open for _ in range(m)]
    if not any(open_fac):
        # Force at least one facility open
        j = random.randrange(m)
        open_fac[j] = True
    assignment = greedy_assign_all(inst, open_fac)
    cost = evaluate_solution(inst, open_fac, assignment)
    return open_fac, assignment, cost


# ----------------------------------------------------------------------
# Local search: OPEN / CLOSE moves
# ----------------------------------------------------------------------

def best_improving_move(
    inst: FacilityLocationInstance,
    open_fac: List[bool],
    assignment: List[int],
    current_cost: float,
) -> Tuple[Optional[Tuple[str, int]], float]:
    """
    Find the best improving OPEN or CLOSE move.
    Returns (move, new_cost):
      - move is ('open', j) or ('close', j) or None if no improvement.
      - new_cost is the cost after applying that move.
    """
    m, n = inst.m, inst.n
    best_delta = 0.0
    best_moves: List[Tuple[str, int]] = []

    # Precompute customers served by each facility (for closing)
    customers_by_fac = [[] for _ in range(m)]
    for i in range(n):
        j = assignment[i]
        customers_by_fac[j].append(i)

    eps = 1e-9

    # Try CLOSING open facilities
    for j in range(m):
        if not open_fac[j]:
            continue

        # If we close j, customers served by j must be reassigned
        delta_open = -inst.open_cost[j]
        delta_assign = 0.0

        # If j is the only open facility, we can't close it
        if sum(open_fac) == 1:
            continue

        open_indices = [k for k in range(m) if open_fac[k] and k != j]

        for i in customers_by_fac[j]:
            old_cost = inst.service_cost[i][j]
            # find best alternative open facility
            best_alt = inst.service_cost[i][open_indices[0]]
            for k in open_indices[1:]:
                c = inst.service_cost[i][k]
                if c < best_alt:
                    best_alt = c
            delta_assign += (best_alt - old_cost)

        delta_total = delta_open + delta_assign
        if delta_total < best_delta - eps:
            best_delta = delta_total
            best_moves = [("close", j)]
        elif abs(delta_total - best_delta) <= eps:
            best_moves.append(("close", j))

    # Try OPENING closed facilities
    for j in range(m):
        if open_fac[j]:
            continue

        delta_open = inst.open_cost[j]
        delta_assign = 0.0

        for i in range(n):
            old_fac = assignment[i]
            old_cost = inst.service_cost[i][old_fac]
            new_cost = inst.service_cost[i][j]
            if new_cost < old_cost:
                delta_assign += (new_cost - old_cost)

        delta_total = delta_open + delta_assign
        if delta_total < best_delta - eps:
            best_delta = delta_total
            best_moves = [("open", j)]
        elif abs(delta_total - best_delta) <= eps:
            best_moves.append(("open", j))

    if not best_moves or best_delta >= -eps:
        return None, current_cost

    # Stochastic tie-breaking among equally good moves
    move = random.choice(best_moves)
    new_cost = current_cost + best_delta
    return move, new_cost


def apply_move(
    inst: FacilityLocationInstance,
    open_fac: List[bool],
    assignment: List[int],
    move: Tuple[str, int],
):
    """Apply 'open' or 'close' move and update assignment greedily."""
    m, n = inst.m, inst.n
    move_type, j = move

    if move_type == "close":
        open_fac[j] = False
    elif move_type == "open":
        open_fac[j] = True
    else:
        raise ValueError("Unknown move type")

    # Reassign customers greedily given new open set
    new_assignment = greedy_assign_all(inst, open_fac)
    # in-place update
    for i in range(n):
        assignment[i] = new_assignment[i]


def local_search(
    inst: FacilityLocationInstance,
    open_fac: List[bool],
    assignment: List[int],
    current_cost: float,
    deadline: float,
) -> Tuple[List[bool], List[int], float]:
    """Run local search until no improving move or time runs out."""
    while time.time() < deadline:
        move, new_cost = best_improving_move(inst, open_fac, assignment, current_cost)
        if move is None or new_cost >= current_cost - 1e-9:
            break
        apply_move(inst, open_fac, assignment, move)
        current_cost = new_cost

    return open_fac, assignment, current_cost


# ----------------------------------------------------------------------
# Anytime wrapper with random restarts
# ----------------------------------------------------------------------

def anytime_local_search(
    inst: FacilityLocationInstance,
    time_limit: float,
    seed: Optional[int] = None,
) -> Tuple[float, List[bool], List[int]]:
    """
    Anytime algorithm:
      - While time remains:
          * build randomized initial solution
          * run local search from it
      - Return best solution seen.
    """
    if seed is not None:
        random.seed(seed)

    start = time.time()
    deadline = start + max(0.01, time_limit)

    # First run: start from "all open" solution
    open_fac, assignment, cost = initial_solution_all_open(inst)
    open_fac, assignment, cost = local_search(inst, open_fac, assignment, cost, deadline)

    best_cost = cost
    best_open = open_fac[:]
    best_assign = assignment[:]

    runs = 1
    while time.time() < deadline:
        runs += 1
        open_fac, assignment, cost = random_initial_solution(inst, p_open=0.5)
        open_fac, assignment, cost = local_search(inst, open_fac, assignment, cost, deadline)
        if cost < best_cost:
            best_cost = cost
            best_open = open_fac[:]
            best_assign = assignment[:]

    # Debug to stderr if you want
    # print(f"Runs: {runs}, best_cost = {best_cost:.4f}", file=sys.stderr)

    return best_cost, best_open, best_assign


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------

def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Anytime local-search approximation for facility location."
    )
    parser.add_argument(
        "-t", type=float, required=True,
        help="Time limit in seconds (anytime requirement).",
    )
    parser.add_argument(
        "input_file", nargs="?", default=None,
        help="Optional input file (otherwise read from stdin).",
    )
    parser.add_argument(
        "--seed", type=int, default=None,
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

    # Run anytime local search
    best_cost, best_open, best_assign = anytime_local_search(
        inst, time_limit=args.t, seed=args.seed
    )

    # Output solution
    write_solution(sys.stdout, best_cost, best_open, best_assign)


if __name__ == "__main__":
    main()

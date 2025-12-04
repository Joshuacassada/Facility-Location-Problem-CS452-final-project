#!/usr/bin/env python3
"""
Anytime stochastic local-search approximation for the distance-based
facility location / coverage problem.

Input format (matches the current test cases):

    n_clients n_facilities
    <n_clients lines>:
        client_name  x  y
    <n_facilities lines>:
        facility_name  x  y  open_flag
    coverage_distance

Example:

    6 8
    C1 61.59 0.60
    C2 15.74 80.04
    ...
    F1 43.76 88.30 1
    ...
    30.21

Semantics:
- Every client must be assigned to some open facility WITHIN coverage_distance.
  Any solution that fails to cover even a single client is considered infeasible
  and is never accepted.
- A client is covered by facility j if dist(client, j) <= coverage_distance.
- Among all feasible solutions, we compare first by:
      (1) # of open facilities (fewer is better),
      (2) total Euclidean assignment distance (smaller is better).
- Unlike greedy methods, this solver uses OPEN, CLOSE, and SWAP moves to explore
  a neighborhood of candidate solutions, and employs simulated annealing to accept
  both improving and occasional non-improving moves (but ONLY among feasible
  solutions), enabling escape from local minima.

Anytime behaviour:
- For a given time limit (-t), the solver repeatedly performs stochastic
  local-search runs starting from an initial feasible solution (all facilities open).
- Each run applies simulated annealing to refine the current solution while
  enforcing full coverage at all times.
- The best feasible solution found across all runs is returned at the deadline.

Method summary:
- Start with all facilities open (which should cover every client if the instance
  is feasible).
- Iteratively apply OPEN / CLOSE / SWAP modifications to explore the solution space.
- After every modification, reassign every client to its nearest open facility
  that is within coverage_distance.
- If any client cannot be covered by the new open set, the move is discarded.
- Among feasible neighbors, accept moves based on a simulated annealing rule.
- Track and output the best feasible solution encountered before the time limit.
"""

import argparse
import math
import random
import sys
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Client:
    name: str
    x: float
    y: float


@dataclass
class Facility:
    name: str
    x: float
    y: float
    initially_open: bool


@dataclass
class Instance:
    clients: List[Client]
    facilities: List[Facility]
    coverage_distance: float


# ---------------------------------------------------------------------------
# Basic distance + input parsing (similar to exact solver style)
# ---------------------------------------------------------------------------

def euclidean(x1: float, y1: float, x2: float, y2: float) -> float:
    """Euclidean distance between two points."""
    return math.hypot(x1 - x2, y1 - y2)


def _next_data_line(stream) -> str:
    """Return next non-empty NON-comment line."""
    while True:
        line = stream.readline()
        if not line:
            return ""
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        return s


def read_instance(stream) -> Instance:
    """
    Input format:

        n_clients n_facilities
        <client_name> <x> <y>
        ...
        <facility_name> <x> <y> <open_flag>
        ...
        <coverage_distance>
    """
    header = _next_data_line(stream)
    if not header:
        raise ValueError("Expected: n_clients n_facilities")

    parts = header.split()
    if len(parts) != 2:
        raise ValueError("Header must be: n_clients n_facilities")
    nC = int(parts[0])
    nF = int(parts[1])

    clients: List[Client] = []
    for _ in range(nC):
        line = _next_data_line(stream)
        nm, xs, ys = line.split()
        clients.append(Client(nm, float(xs), float(ys)))

    facilities: List[Facility] = []
    for _ in range(nF):
        line = _next_data_line(stream)
        nm, xs, ys, fl = line.split()
        facilities.append(Facility(nm, float(xs), float(ys), bool(int(fl))))

    cov_line = _next_data_line(stream)
    if not cov_line:
        raise ValueError("Missing coverage distance line.")
    coverage = float(cov_line)

    return Instance(clients, facilities, coverage)


def parse_input(path: str) -> Instance:
    """
    File-based input wrapper mirroring the style of the exact solver:
    takes a filename, returns an Instance.
    """
    if path == "-" or path is None:
        return read_instance(sys.stdin)
    with open(path, "r", encoding="utf-8") as f:
        return read_instance(f)


# ---------------------------------------------------------------------------
# Precomputed distances
# ---------------------------------------------------------------------------

def precompute_distances(inst: Instance) -> List[List[float]]:
    """
    dist[c][f] = distance from client c to facility f.
    """
    dist: List[List[float]] = []
    for c in inst.clients:
        row = []
        for f in inst.facilities:
            row.append(euclidean(c.x, c.y, f.x, f.y))
        dist.append(row)
    return dist


# ---------------------------------------------------------------------------
# Assignment + objective (core problem semantics)
# ---------------------------------------------------------------------------

def assign_clients_with_hard_coverage(
    open_set: Set[int],
    dist: List[List[float]],
    coverage: float,
) -> Tuple[Optional[Dict[int, int]], bool, float]:
    """
    Assign each client to the nearest open facility WITHIN coverage.

    Returns:
      (assignment, feasible, total_dist)

    - If any client has no open facility within coverage distance, feasible=False
      and assignment is None.
    - Otherwise feasible=True, assignment maps each client -> facility, and
      total_dist is the sum of distances for all assignments.
    """
    if not open_set:
        return None, False, float("inf")

    C = len(dist)
    assignment: Dict[int, int] = {}
    total_dist = 0.0

    open_list = sorted(open_set)

    for c in range(C):
        best_f = None
        best_d = float("inf")

        for f in open_list:
            d = dist[c][f]
            if d <= coverage and d < best_d:
                best_d = d
                best_f = f

        if best_f is None:
            # No facility within coverage for this client: infeasible solution
            return None, False, float("inf")

        assignment[c] = best_f
        total_dist += best_d

    return assignment, True, total_dist


def objective(num_open: int, total_dist: float) -> float:
    """
    Scalar objective for feasible solutions:
      primary: minimize num_open
      secondary: minimize total_dist
    """
    OPEN_WEIGHT = 1_000.0
    return num_open * OPEN_WEIGHT + total_dist


def initial_solution(inst: Instance) -> Set[int]:
    """
    Start from a guaranteed-feasible solution:
      - Open ALL facilities.

    We rely on the instance being such that with all facilities open, every
    client has at least one facility within coverage_distance. If even that
    fails, the instance is infeasible for this coverage radius.
    """
    return set(range(len(inst.facilities)))


# ---------------------------------------------------------------------------
# Local search + simulated annealing (OPEN / CLOSE / SWAP moves)
# ---------------------------------------------------------------------------

def local_search(
    inst: Instance,
    dist: List[List[float]],
    time_deadline: float,
    rng: random.Random,
) -> Tuple[Set[int], Dict[int, int]]:
    coverage = inst.coverage_distance
    F = len(inst.facilities)

    # Start from all facilities open
    current_open = initial_solution(inst)
    curr_assign, feasible, curr_dist = assign_clients_with_hard_coverage(
        current_open, dist, coverage
    )
    if not feasible:
        # If even all facilities can't cover all clients, there is no feasible solution.
        # In that case, just bail out with all facilities open and no assignments.
        # (Your instance set should not do this.)
        raise ValueError(
            "Instance appears infeasible: even all facilities open cannot cover all clients."
        )

    curr_cost = objective(len(current_open), curr_dist)

    best_open = set(current_open)
    best_assign = dict(curr_assign)
    best_cost = curr_cost

    # Annealing parameters
    T = 1.0
    MIN_T = 1e-4
    COOLING = 0.995

    # Optional iteration cap to keep complexity clean
    max_iters = 10 * F * F if F > 0 else 0
    iters = 0

    while time.time() < time_deadline and T > MIN_T and iters < max_iters:
        iters += 1

        move_type = rng.choice(["open", "close", "swap"])
        neighbor_open = set(current_open)

        if move_type == "open":
            closed = [j for j in range(F) if j not in neighbor_open]
            if not closed:
                continue
            j = rng.choice(closed)
            neighbor_open.add(j)

        elif move_type == "close":
            if len(neighbor_open) <= 1:
                continue
            j = rng.choice(list(neighbor_open))
            neighbor_open.remove(j)

        else:  # "swap"
            if len(neighbor_open) == 0:
                continue
            closed = [j for j in range(F) if j not in neighbor_open]
            if not closed:
                continue
            j_close = rng.choice(list(neighbor_open))
            j_open = rng.choice(closed)
            neighbor_open.remove(j_close)
            neighbor_open.add(j_open)

        # Check feasibility of the neighbor (hard coverage constraint)
        n_assign, feasible, n_dist = assign_clients_with_hard_coverage(
            neighbor_open, dist, coverage
        )
        if not feasible:
            # Discard infeasible neighbor
            continue

        n_cost = objective(len(neighbor_open), n_dist)
        delta = n_cost - curr_cost

        # Simulated annealing acceptance (only among feasible moves)
        if delta <= 0:
            accept = True
        else:
            accept_prob = math.exp(-delta / max(T, 1e-9))
            accept = rng.random() < accept_prob

        if accept:
            current_open = neighbor_open
            curr_assign = n_assign
            curr_dist = n_dist
            curr_cost = n_cost

            if n_cost < best_cost:
                best_cost = n_cost
                best_open = set(neighbor_open)
                best_assign = dict(n_assign)

        T *= COOLING

    return best_open, best_assign


# ---------------------------------------------------------------------------
# Anytime wrapper (analogous to solve_exact, but time-bounded)
# ---------------------------------------------------------------------------

def anytime(
    inst: Instance,
    time_limit: float,
    seed: Optional[int] = None,
) -> Tuple[Set[int], Dict[int, int]]:
    """
    Anytime driver: repeatedly runs local_search with shrinking time budgets
    until the global deadline is reached, keeping the best feasible solution.
    """
    rng = random.Random(seed)
    start = time.time()
    deadline = start + time_limit

    dist = precompute_distances(inst)

    # First local-search run
    first_deadline = start + time_limit * 0.25
    if first_deadline > deadline:
        first_deadline = deadline

    best_open, best_assign = local_search(inst, dist, first_deadline, rng)
    _, _, best_dist = assign_clients_with_hard_coverage(
        best_open, dist, inst.coverage_distance
    )
    best_cost = objective(len(best_open), best_dist)

    # Additional restarts while time remains
    while time.time() < deadline:
        remaining = deadline - time.time()
        if remaining <= 0:
            break

        run_deadline = time.time() + remaining * 0.25
        if run_deadline > deadline:
            run_deadline = deadline

        try:
            cand_open, cand_assign = local_search(inst, dist, run_deadline, rng)
        except ValueError:
            # Instance infeasible; stop trying.
            break

        _, feasible, cand_dist = assign_clients_with_hard_coverage(
            cand_open, dist, inst.coverage_distance
        )
        if not feasible:
            continue

        cand_cost = objective(len(cand_open), cand_dist)
        if cand_cost < best_cost:
            best_cost = cand_cost
            best_open = cand_open
            best_assign = cand_assign

    return best_open, best_assign


# ---------------------------------------------------------------------------
# Output formatting (similar role to exact solver's final print)
# ---------------------------------------------------------------------------

def write_solution(
    inst: Instance,
    open_facilities: Set[int],
    assignment: Dict[int, int],
    out=sys.stdout,
) -> None:
    """
    Print solution in the agreed format:
    
        Total distance: <value>

        Open facilities:
        F1 F3 F7

        Coverage:
        F1 covers: C1 C4
        F3 covers: C2
        F7 covers: C3 C5
    """
    facs = inst.facilities
    clts = inst.clients
    
    # ---- compute total distance of this solution ----
    total_dist = 0.0
    for ci, fj in assignment.items():
        c = clts[ci]
        f = facs[fj]
        total_dist += euclidean(c.x, c.y, f.x, f.y)

    # print total distance first (for humans)
    print(f"Total distance: {total_dist:.4f}", file=out)
    print("", file=out)

    print("Open facilities:", file=out)
    names = [facs[j].name for j in sorted(open_facilities)]
    print(" ".join(names), file=out)
    print("", file=out)

    print("Coverage:", file=out)
    cover_map: Dict[int, List[str]] = {j: [] for j in open_facilities}
    for ci, fj in assignment.items():
        if fj in cover_map:
            cover_map[fj].append(clts[ci].name)

    for j in sorted(open_facilities):
        fname = facs[j].name
        served = cover_map.get(j, [])
        if served:
            print(f"{fname} covers: " + " ".join(served), file=out)
        else:
            print(f"{fname} covers: (none)", file=out)


# ---------------------------------------------------------------------------
# Main (now visually similar to the exact solver's main)
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Anytime stochastic local-search approximation for facility coverage "
            "with a hard coverage constraint (every client must be covered)."
        )
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
        default="-",
        help="Input file (or '-' for stdin).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional explicit random seed (for reproducible experiments).",
    )
    args = parser.parse_args()

    # Read instance (parse_input mirrors the exact solver style)
    inst = parse_input(args.input_file)

    # Run anytime approximation
    open_facilities, assignment = anytime(inst, args.t, seed=args.seed)

    # Print solution
    write_solution(inst, open_facilities, assignment, out=sys.stdout)


if __name__ == "__main__":
    main()

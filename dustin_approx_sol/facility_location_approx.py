#!/usr/bin/env python3
"""
Anytime stochastic greedy approximation for the distance-based facility
location / coverage problem.

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
    F1 43.76 88.30 0
    ...
    30.21

Semantics:
- Every client must be assigned to some open facility.
- A client is covered by facility j if dist(client, j) <= coverage_distance.
- The greedy algorithm tries to open as few facilities as possible while covering
  all clients; remaining uncovered clients are attached to their nearest facility.
- Cost = total Euclidean distance from each client to its assigned facility.

Anytime behaviour:
- For a given time limit -t, we repeatedly build solutions with a *randomized*
  greedy heuristic.
- We keep the best solution seen so far (primary: fewest open facilities,
  secondary: smallest total distance).
"""

import argparse
import math
import random
import sys
import time
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple


# ---------------------------------------------------------------------------
# Data structures
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
# Parsing and printing
# ---------------------------------------------------------------------------

def _next_data_line(stream) -> str:
    """Return the next non-empty, non-comment line, stripped."""
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
    Read an instance in the simple coverage format:

        n_clients n_facilities
        <clients>
        <facilities>
        coverage_distance
    """
    header = _next_data_line(stream)
    if not header:
        raise ValueError("Empty input: expected 'n_clients n_facilities'.")

    parts = header.split()
    if len(parts) != 2:
        raise ValueError("Header must be: n_clients n_facilities")
    n_clients = int(parts[0])
    n_facilities = int(parts[1])

    clients: List[Client] = []
    for _ in range(n_clients):
        line = _next_data_line(stream)
        parts = line.split()
        if len(parts) != 3:
            raise ValueError("Client line must be: name x y")
        nm, xs, ys = parts
        clients.append(Client(nm, float(xs), float(ys)))

    facilities: List[Facility] = []
    for _ in range(n_facilities):
        line = _next_data_line(stream)
        parts = line.split()
        if len(parts) != 4:
            raise ValueError("Facility line must be: name x y open_flag")
        nm, xs, ys, flag = parts
        facilities.append(Facility(nm, float(xs), float(ys), bool(int(flag))))

    cov_line = _next_data_line(stream)
    if not cov_line:
        raise ValueError("Missing coverage distance line.")
    coverage = float(cov_line)

    return Instance(clients=clients, facilities=facilities,
                    coverage_distance=coverage)


def write_solution(
    inst: Instance,
    open_facilities: Set[int],
    assignment: Dict[int, int],
    out=sys.stdout,
) -> None:
    """
    Print solution in the exact same style as the OPTIMAL solver,
    but with the header changed to '=== APPROXIMATION SOLUTION FOUND ==='.
    """

    facs = inst.facilities
    clts = inst.clients

    print("")

    # === HEADER ===
    print("=== APPROXIMATION SOLUTION FOUND ===", file=out)

    # Coverage distance (your instance stores it)
    print(f"Coverage distance: {inst.coverage_distance:.2f}", file=out)

    # Number of facilities chosen
    print(f"Facilities chosen ({len(open_facilities)}):", file=out)

    # Each facility with coordinates
    for j in sorted(open_facilities):
        f = facs[j]
        print(f"  {f.name} at ({f.x:.2f}, {f.y:.2f})", file=out)

    print("", file=out)
    print("Coverage mapping:", file=out)

    # Build mapping facility → list of client names
    cover_map: Dict[int, List[str]] = {j: [] for j in open_facilities}
    for ci, fj in assignment.items():
        if fj in cover_map:
            cover_map[fj].append(clts[ci].name)

    # Print coverage lists
    for j in sorted(open_facilities):
        clients = sorted(cover_map[j])
        if clients:
            client_str = ", ".join(clients)
        else:
            client_str = "(none)"
        print(f"{facs[j].name} covers: {client_str}", file=out)



# ---------------------------------------------------------------------------
# Distance helpers
# ---------------------------------------------------------------------------

def euclidean(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.hypot(x1 - x2, y1 - y2)


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
# Randomized greedy construction
# ---------------------------------------------------------------------------

def greedy_randomized(
    inst: Instance,
    rng: random.Random,
) -> Tuple[Set[int], Dict[int, int], float, int]:
    """
    SINGLE randomized greedy construction.

    At each step, for each unopened facility j:
      gain_j = # of currently uncovered clients it can cover (within R)

    Instead of always taking argmax_j gain_j (deterministic), we use a
    softmax-style choice:

        P(pick j) ∝ exp(beta * gain_j)

    so higher gain is more likely but not guaranteed. This introduces true
    randomness between runs, letting the anytime wrapper improve with time.

    Remaining uncovered clients are attached to their nearest facility
    (opening that facility if needed).
    """
    C = len(inst.clients)
    F = len(inst.facilities)
    R = inst.coverage_distance

    dist = precompute_distances(inst)

    # Precompute cover sets
    cover_sets: List[Set[int]] = []
    for j in range(F):
        can_cover = {i for i in range(C) if dist[i][j] <= R}
        cover_sets.append(can_cover)

    uncovered: Set[int] = set(range(C))
    open_facilities: Set[int] = set()
    assignment: Dict[int, int] = {}

    beta = 0.15  # softness; larger = more greedy, smaller = more random

    # Greedy loop
    while True:
        unopened = [j for j in range(F) if j not in open_facilities]
        if not unopened:
            break

        gains: List[int] = []
        best_gain = 0
        for j in unopened:
            g = len(uncovered & cover_sets[j])
            gains.append(g)
            if g > best_gain:
                best_gain = g

        if best_gain == 0:
            # no facility can cover any *new* client within R
            break

        # Softmax over gains
        weights = [math.exp(beta * g) for g in gains]
        total_w = sum(weights)
        r = rng.random() * total_w
        acc = 0.0
        chosen = unopened[-1]  # fallback
        for j, w in zip(unopened, weights):
            acc += w
            if r <= acc:
                chosen = j
                break

        open_facilities.add(chosen)
        newly = uncovered & cover_sets[chosen]
        for c in newly:
            assignment[c] = chosen
        uncovered -= newly

    # Fallback: any leftover clients go to their nearest facility
    for c in uncovered:
        best_j = min(range(F), key=lambda j: dist[c][j])
        open_facilities.add(best_j)
        assignment[c] = best_j

    # Safety: ensure all clients assigned
    for c in range(C):
        if c not in assignment:
            best_j = min(range(F), key=lambda j: dist[c][j])
            open_facilities.add(best_j)
            assignment[c] = best_j

    # Compute total distance
    total_dist = 0.0
    for c, j in assignment.items():
        total_dist += dist[c][j]

    num_open = len(open_facilities)
    return open_facilities, assignment, total_dist, num_open


# ---------------------------------------------------------------------------
# Anytime wrapper
# ---------------------------------------------------------------------------

def anytime(
    inst: Instance,
    time_limit: float,
    seed: int | None = None,
) -> Tuple[Set[int], Dict[int, int]]:
    """
    Anytime loop:

    - Initialize RNG.
    - Run randomized greedy at least once.
    - Re-run as many times as the time limit allows.
    - Keep the best solution seen so far.

    "Best" is lexicographic:
        1. fewer open facilities
        2. if tied, smaller total distance
    """
    rng = random.Random(seed)
    start = time.time()
    deadline = start + time_limit

    # First construction
    best_open, best_assign, best_dist, best_num = greedy_randomized(inst, rng)
    runs = 1

    while time.time() < deadline:
        o, a, d, k = greedy_randomized(inst, rng)
        runs += 1
        if (k < best_num) or (k == best_num and d < best_dist):
            best_open, best_assign, best_dist, best_num = o, a, d, k

    # Debug if you want:
    # print(f"[ANYTIME] runs = {runs}", file=sys.stderr)

    return best_open, best_assign


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Anytime stochastic greedy approximation for facility coverage."
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

    # Read instance
    if args.input_file == "-" or args.input_file is None:
        inst = read_instance(sys.stdin)
    else:
        with open(args.input_file, "r", encoding="utf-8") as f:
            inst = read_instance(f)

    # Run anytime approximation
    open_facilities, assignment = anytime(inst, args.t, seed=args.seed)

    # Print solution
    write_solution(inst, open_facilities, assignment, out=sys.stdout)


if __name__ == "__main__":
    main()
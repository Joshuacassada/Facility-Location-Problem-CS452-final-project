#!/usr/bin/env python3
"""
Anytime greedy approximation for a simple Facility Location / Coverage problem.

Input format (from Canvas / README, numeric version):

Line 1:
    n_clients n_facilities

Next n_clients lines:
    client_name x y

Next n_facilities lines:
    facility_name x y open_flag
    (open_flag is 0 or 1; typically 0, you may treat 1 as initially open)

Final line:
    coverage_distance   (float)

Example:

4 3
C1 2 3
C2 5 4
C3 1 7
C4 6 8
F1 2 4 0
F2 5 5 0
F3 1 6 0
2.5

Output format:

Open facilities:
F1 F3

Coverage:
F1 covers: C1 C2
F3 covers: C3 C4

Approximation approach (high level):

- Precompute distances between every client and facility.
- A client can be *covered* by a facility if distance <= coverage_distance.
- Greedy algorithm to approximate a minimum number of facilities that cover all clients:
    * While there are still uncovered clients and some facility can cover new ones:
        - For each unopened facility, count how many *currently uncovered* clients
          it would newly cover.
        - Select the facility that covers the most new clients.
        - Break ties randomly (satisfies the "greedy tie-breaking is random" spec).
        - Open it and assign those clients to this facility.
    * If any clients remain uncovered (no facility within coverage distance),
      assign them to their nearest facility (even if distance > coverage_distance),
      opening that facility if necessary.

Anytime requirement:

- The program accepts a command-line argument -t (time limit in seconds).
- It repeatedly runs this randomized greedy construction until the time limit expires.
- It keeps the *best* solution seen so far, where "best" is:
    1) fewer open facilities,
    2) if tied, smaller total distance from clients to their assigned facilities.

Runtime per construction:

- Let:
    C = number of clients
    F = number of facilities
- Precompute distances: O(C * F).
- Each greedy step:
    - For each unopened facility, scan all clients ⇒ O(F * C)
    - At most F steps ⇒ O(F^2 * C) per construction.
- Anytime wrapper simply repeats this construction as many times as time allows,
  so total runtime is polynomial in C and F for any fixed time limit.

This file is intentionally simpler than a full optimal solver and is meant
to be used as an approximation solution architect with an anytime greedy algorithm.
"""

import argparse
import math
import random
import sys
import time
from dataclasses import dataclass
from typing import List, Tuple, Dict, Set


# ----------------------------------------------------------
# Data Structures
# ----------------------------------------------------------

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


# ----------------------------------------------------------
# Input / Output
# ----------------------------------------------------------

def read_instance(stream) -> Instance:
    """
    Parse the instance from the given text stream according to the
    simple numeric format described in the module docstring.
    """
    # Read first non-empty, non-comment line as "n_clients n_facilities"
    def next_data_line() -> str:
        while True:
            line = stream.readline()
            if not line:
                return ""  # EOF
            line = line.strip()
            if line == "" or line.startswith("#"):
                continue
            return line

    header = next_data_line()
    if not header:
        raise ValueError("Empty input: expected 'n_clients n_facilities' line.")
    n_clients, n_facilities = map(int, header.split())

    clients: List[Client] = []
    for _ in range(n_clients):
        line = next_data_line()
        if not line:
            raise ValueError("Unexpected EOF while reading clients.")
        parts = line.split()
        if len(parts) != 3:
            raise ValueError(f"Client line must have 3 fields: {line}")
        name, xs, ys = parts
        clients.append(Client(name=name, x=float(xs), y=float(ys)))

    facilities: List[Facility] = []
    for _ in range(n_facilities):
        line = next_data_line()
        if not line:
            raise ValueError("Unexpected EOF while reading facilities.")
        parts = line.split()
        if len(parts) != 4:
            raise ValueError(f"Facility line must have 4 fields: {line}")
        name, xs, ys, fs = parts
        initially_open = (int(fs) != 0)
        facilities.append(Facility(name=name, x=float(xs), y=float(ys),
                                   initially_open=initially_open))

    # Final line: coverage distance
    line = next_data_line()
    if not line:
        raise ValueError("Expected coverage distance.")
    coverage_distance = float(line)

    return Instance(clients=clients,
                    facilities=facilities,
                    coverage_distance=coverage_distance)


def write_solution(
    instance: Instance,
    open_facilities: Set[int],
    assignment: Dict[int, int],
    out=sys.stdout
) -> None:
    """
    Print solution in the required human-readable format:

    Open facilities:
    F1 F3

    Coverage:
    F1 covers: C1 C2
    F3 covers: C3 C4
    """
    facilities = instance.facilities
    clients = instance.clients

    # First line: open facilities by name
    open_names = [facilities[j].name for j in sorted(open_facilities)]
    print("Open facilities:", file=out)
    if open_names:
        print(" ".join(open_names), file=out)
    else:
        print("(none)", file=out)

    print("", file=out)  # blank line

    # Coverage mapping
    print("Coverage:", file=out)
    # Build mapping facility index -> list of client names
    coverage_map: Dict[int, List[str]] = {j: [] for j in open_facilities}
    for ci, fj in assignment.items():
        if fj in coverage_map:
            coverage_map[fj].append(clients[ci].name)

    for j in sorted(open_facilities):
        fac_name = facilities[j].name
        client_list = coverage_map.get(j, [])
        if client_list:
            print(f"{fac_name} covers: " + " ".join(client_list), file=out)
        else:
            # Facility opened but covers no clients (unlikely, but possible)
            print(f"{fac_name} covers: (none)", file=out)


# ----------------------------------------------------------
# Distance Helpers
# ----------------------------------------------------------

def euclidean_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.hypot(x1 - x2, y1 - y2)


def precompute_distances(inst: Instance) -> List[List[float]]:
    """
    dist[c][f] = Euclidean distance between client c and facility f.
    """
    dist: List[List[float]] = []
    for c in inst.clients:
        row = []
        for f in inst.facilities:
            d = euclidean_distance(c.x, c.y, f.x, f.y)
            row.append(d)
        dist.append(row)
    return dist


# ----------------------------------------------------------
# Greedy Approximation (Single Construction)
# ----------------------------------------------------------

def greedy_cover(
    inst: Instance,
    rng: random.Random
) -> Tuple[Set[int], Dict[int, int], float, int]:
    """
    One greedy construction with random tie-breaking.

    Objective (approximate): minimize the number of open facilities while
    covering all clients within the coverage distance. If some clients cannot be
    covered by any facility within the coverage distance, assign them to the
    nearest facility regardless (opening that facility if needed).

    Returns:
        open_facilities: set of facility indices
        assignment: dict {client_index -> facility_index}
        total_distance: sum of distances client -> assigned facility
        num_open: number of open facilities
    """
    clients = inst.clients
    facilities = inst.facilities
    n_clients = len(clients)
    n_facilities = len(facilities)
    R = inst.coverage_distance

    dist = precompute_distances(inst)

    # For each facility, precompute which clients it can cover (within distance R)
    cover_sets: List[Set[int]] = []
    for j in range(n_facilities):
        can_cover = {i for i in range(n_clients) if dist[i][j] <= R}
        cover_sets.append(can_cover)

    uncovered: Set[int] = set(range(n_clients))
    open_facilities: Set[int] = set()
    assignment: Dict[int, int] = {}

    # Optionally mark initially-open facilities as open (if you want that behavior)
    # Here we completely ignore them for simplicity (everything starts closed).
    # If you want to honor them, uncomment the next block:
    #
    # for j, fac in enumerate(facilities):
    #     if fac.initially_open:
    #         open_facilities.add(j)
    #         newly_covered = uncovered & cover_sets[j]
    #         for c in newly_covered:
    #             assignment[c] = j
    #         uncovered -= newly_covered

    # Greedy loop: repeatedly pick the facility that covers the largest number
    # of currently uncovered clients, breaking ties randomly.
    while True:
        best_gain = 0
        best_candidates: List[int] = []

        for j in range(n_facilities):
            if j in open_facilities:
                continue
            newly_covered = uncovered & cover_sets[j]
            gain = len(newly_covered)
            if gain > best_gain:
                best_gain = gain
                best_candidates = [j]
            elif gain == best_gain and gain > 0:
                # tie: record for random tie-breaking
                best_candidates.append(j)

        if best_gain == 0 or not best_candidates:
            # No unopened facility can cover any new client within R
            break

        # Random tie-breaking among best facilities
        chosen = rng.choice(best_candidates)
        open_facilities.add(chosen)
        newly_covered = uncovered & cover_sets[chosen]
        for c in newly_covered:
            assignment[c] = chosen
        uncovered -= newly_covered

    # If any client remains uncovered, assign it to its nearest facility
    # (opening that facility if needed).
    for c in uncovered:
        # Find nearest facility by distance
        best_j = min(range(n_facilities), key=lambda j: dist[c][j])
        open_facilities.add(best_j)
        assignment[c] = best_j

    # Ensure all clients are assigned (sanity check)
    for c_idx in range(n_clients):
        if c_idx not in assignment:
            # This should not happen, but just to be safe, assign to nearest facility
            best_j = min(range(n_facilities), key=lambda j: dist[c_idx][j])
            open_facilities.add(best_j)
            assignment[c_idx] = best_j

    # Compute total distance for this solution
    total_distance = 0.0
    for c_idx, f_idx in assignment.items():
        total_distance += dist[c_idx][f_idx]

    num_open = len(open_facilities)
    return open_facilities, assignment, total_distance, num_open


# ----------------------------------------------------------
# Anytime Wrapper
# ----------------------------------------------------------

def anytime(
    inst: Instance,
    time_limit: float,
    seed: int | None = None
) -> Tuple[Set[int], Dict[int, int]]:
    """
    Anytime wrapper:
    - Initialize RNG.
    - Perform at least one greedy construction.
    - While time remains, repeat the greedy construction with random tie-breaking.
    - Keep the best solution seen so far:
        1) fewer open facilities, then
        2) smaller total distance.
    """
    rng = random.Random(seed)
    start = time.time()
    deadline = start + time_limit

    # At least one run
    best_open, best_assign, best_dist, best_num_open = greedy_cover(inst, rng)
    runs = 1

    # Keep rerunning as long as we have time
    while time.time() < deadline:
        open_f, assign, dist_val, num_open = greedy_cover(inst, rng)
        runs += 1

        # Compare (num_open, total_distance)
        if (num_open < best_num_open) or (
            num_open == best_num_open and dist_val < best_dist
        ):
            best_open, best_assign = open_f, assign
            best_dist, best_num_open = dist_val, num_open

    # You could print number of runs to stderr for debugging:
    # print(f"Anytime runs: {runs}", file=sys.stderr)

    return best_open, best_assign


# ----------------------------------------------------------
# Main
# ----------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Anytime greedy approximation for a simple facility coverage problem."
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
        help="Input file (or '-' / omitted for stdin).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed (optional, for reproducible runs).",
    )

    args = parser.parse_args()

    # Read instance from file or stdin
    if args.input_file == "-" or args.input_file is None:
        inst = read_instance(sys.stdin)
    else:
        with open(args.input_file, "r", encoding="utf-8") as f:
            inst = read_instance(f)

    # Run anytime greedy approximation
    open_facilities, assignment = anytime(inst, args.t, seed=args.seed)

    # Output solution
    write_solution(inst, open_facilities, assignment, out=sys.stdout)


if __name__ == "__main__":
    main()

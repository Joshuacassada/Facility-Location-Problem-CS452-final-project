#!/usr/bin/env python3
"""
reduction.py

Reduce a 2D coverage-based Facility Location instance to a Max-3SAT instance.

New input format (from stdin or file):

    c f
    <c lines: client_name cx cy>
    <f lines: facility_name fx fy open_flag>
    <coverage_distance>

Where:
    - c is the number of clients
    - f is the number of facilities
    - (cx, cy) and (fx, fy) are 2D coordinates
    - open_flag is an initial open/closed indicator (ignored by the reduction)
    - coverage_distance is the maximum allowed distance between a client
      and a facility for service.

For the purposes of the reduction, we create a simplified UFLP-style instance:
    - Each facility has uniform opening cost 1.0
    - Each client has uniform demand 1.0
    - A client j may only be assigned to facility i if
          dist(i, j) <= coverage_distance

We construct Boolean variables:
    Y_i   : facility i is open
    X_ij  : client j assigned to facility i
plus helper variables to encode costs and OR-chains in 3-CNF.

Output (to stdout) in the Max-3SAT group's format:
    n m
    l11 l12 l13
    l21 l22 l23
    ...

where each clause is exactly 3 literals, positive or negative integers,
variables are numbered 1..n.
"""

import sys
import math
import argparse
from typing import List, Tuple, TextIO


# ---------------------------------------------------------------------
# CNF representation
# ---------------------------------------------------------------------

class CNF:
    def __init__(self):
        self.var_to_id = {}   # name -> int
        self.vars: List[str] = []   # index-1 -> name
        self.clauses: List[List[int]] = []  # list of [a,b,c]

    def new_var(self, name: str) -> int:
        """Get or create a variable index for a symbolic name."""
        if name not in self.var_to_id:
            idx = len(self.vars) + 1  # DIMACS-style: start at 1
            self.var_to_id[name] = idx
            self.vars.append(name)
        return self.var_to_id[name]

    def lit(self, name: str, neg: bool = False) -> int:
        """Return literal integer for variable name (negated if needed)."""
        v = self.new_var(name)
        return -v if neg else v

    def add_clause(self, lits: List[int]) -> None:
        """Add a clause; pad to 3 literals by repeating last literal."""
        if not lits:
            raise ValueError("Empty clause not allowed")
        while len(lits) < 3:
            lits.append(lits[-1])
        if len(lits) != 3:
            raise ValueError("Clause must be <= 3 literals before padding.")
        self.clauses.append(lits)


# ---------------------------------------------------------------------
# Read coverage-based FLP instance (2D coordinates format)
# ---------------------------------------------------------------------

def _next_data_line(stream: TextIO) -> str:
    """Read next non-empty, non-comment line or raise on EOF."""
    line = stream.readline()
    while line and (line.strip() == "" or line.lstrip().startswith("#")):
        line = stream.readline()
    if not line:
        raise ValueError("Unexpected EOF while reading input")
    return line.strip()


def read_flp_instance(stream: TextIO):
    """
    Read the coverage-based FLP format:

        c f
        <c lines: client_name cx cy>
        <f lines: facility_name fx fy open_flag>
        <coverage_distance>

    Returns:
        f, c, open_costs, fac_coords, cust_demands, cust_coords, coverage
    where:
        - open_costs is a length-f list of uniform facility opening costs (1.0)
        - cust_demands is a length-c list of uniform client demands (1.0)
    """

    header = _next_data_line(stream)
    parts = header.split()
    if len(parts) != 2:
        raise ValueError(f"Expected header 'c f', got: {header!r}")
    c_str, f_str = parts
    c = int(c_str)
    f = int(f_str)

    # Client coordinates
    cust_coords: List[Tuple[float, float]] = []
    for _ in range(c):
        line = _next_data_line(stream)
        tokens = line.split()
        if len(tokens) < 3:
            raise ValueError(
                f"Client line must have at least 3 tokens (name x y), got: {line!r}"
            )
        # name = tokens[0]
        x_str, y_str = tokens[1], tokens[2]
        cust_coords.append((float(x_str), float(y_str)))

    # Facility coordinates
    fac_coords: List[Tuple[float, float]] = []
    for _ in range(f):
        line = _next_data_line(stream)
        tokens = line.split()
        if len(tokens) < 4:
            raise ValueError(
                "Facility line must have at least 4 tokens "
                "(name x y open_flag), got: {line!r}"
            )
        # name = tokens[0]
        x_str, y_str = tokens[1], tokens[2]
        # open_flag = tokens[3]  # ignored for reduction
        fac_coords.append((float(x_str), float(y_str)))

    # Coverage distance
    coverage_line = _next_data_line(stream)
    try:
        coverage = float(coverage_line)
    except ValueError as e:
        raise ValueError(f"Invalid coverage distance {coverage_line!r}") from e

    # Uniform costs / demands for reduction
    open_costs = [1.0] * f
    cust_demands = [1.0] * c

    return f, c, open_costs, fac_coords, cust_demands, cust_coords, coverage


def build_service_costs(
    f: int,
    c: int,
    open_costs: List[float],
    fac_coords: List[Tuple[float, float]],
    cust_demands: List[float],
    cust_coords: List[Tuple[float, float]],
    coverage: float,
) -> List[List[float]]:
    """
    service_cost[j][i] = demand_j * dist(customer j, facility i)

    If dist > coverage, the assignment is forbidden and we encode that by
    storing a negative sentinel value service_cost[j][i] = -1.0.
    """
    service_cost = [[0.0 for _ in range(f)] for _ in range(c)]
    for j in range(c):
        cx, cy = cust_coords[j]
        dj = cust_demands[j]
        for i in range(f):
            fx, fy = fac_coords[i]
            dist = math.dist((cx, cy), (fx, fy))
            if dist > coverage:
                # Forbidden edge: handled specially in the reduction.
                service_cost[j][i] = -1.0
            else:
                service_cost[j][i] = dj * dist
    return service_cost


# ---------------------------------------------------------------------
# Reduction FLP -> Max-3SAT
# ---------------------------------------------------------------------

def reduce_flp_to_max3sat(
    f: int,
    c: int,
    open_costs: List[float],
    service_cost: List[List[float]],
    facility_scale: float = 1.0,
    edge_scale: float = 10.0,
) -> CNF:
    """
    Build a CNF instance encoding the FLP as Max-3SAT.

    facility_scale and edge_scale control how many copies of each
    cost-related "bonus" clause we add so counts stay reasonable.

    For pairs (i, j) where service_cost[j][i] < 0, the assignment X_ij
    is forbidden (dist > coverage) and we force X_ij = FALSE.
    """
    cnf = CNF()

    # --- Variables: Y_i, X_ij ---
    for i in range(f):
        cnf.new_var(f"Y_{i}")
    for i in range(f):
        for j in range(c):
            cnf.new_var(f"X_{i}_{j}")

    # -------------------------------------------------------------
    # Feasibility clauses
    # -------------------------------------------------------------

    # (A) Each client j must be assigned to at least one facility.
    # Big OR over X_{i,j}, converted to 3-CNF via chain.
    for j in range(c):
        xs = [cnf.lit(f"X_{i}_{j}") for i in range(f)]
        # If some X_{i,j} are later forced false, that's fine;
        # the SAT solver will handle the implications.
        if len(xs) <= 3:
            cnf.add_clause(xs)
        else:
            # Tseitin-style chain:
            prev_z = f"Z_{j}_0"
            cnf.new_var(prev_z)
            cnf.add_clause([xs[0], xs[1], cnf.lit(prev_z)])
            idx = 2
            z_idx = 1
            # middle clauses
            while idx < len(xs) - 2:
                new_z = f"Z_{j}_{z_idx}"
                cnf.new_var(new_z)
                cnf.add_clause(
                    [cnf.lit(prev_z, True), xs[idx], cnf.lit(new_z)]
                )
                prev_z = new_z
                idx += 1
                z_idx += 1
            # last clause
            cnf.add_clause([cnf.lit(prev_z, True), xs[-2], xs[-1]])

    # (B) Each client j assigned to at most one facility:
    # For all i < k, (~X_ij OR ~X_kj).
    for j in range(c):
        for i in range(f):
            for k in range(i + 1, f):
                cnf.add_clause([
                    cnf.lit(f"X_{i}_{j}", True),
                    cnf.lit(f"X_{k}_{j}", True)
                ])

    # (C) Assignment implies facility open: X_ij -> Y_i
    for i in range(f):
        for j in range(c):
            cnf.add_clause([
                cnf.lit(f"X_{i}_{j}", True),
                cnf.lit(f"Y_{i}")
            ])

    # -------------------------------------------------------------
    # Cost encoding: bonus clauses for cheap configurations
    # -------------------------------------------------------------

    # Facilities: bonus if facility is CLOSED.
    for i in range(f):
        Ki = f"K_{i}"
        Ti = f"T_k_{i}"

        # Force K_i = FALSE: (~K_i OR T_i OR ~T_i)
        cnf.add_clause([
            cnf.lit(Ki, True),
            cnf.lit(Ti),
            cnf.lit(Ti, True)
        ])

        # Scale facility opening cost down if needed.
        scaled = max(1, int(round(open_costs[i] / facility_scale)))

        # Add scaled copies of (~Y_i OR K_i OR K_i)
        for _ in range(scaled):
            cnf.add_clause([
                cnf.lit(f"Y_{i}", True),
                cnf.lit(Ki),
                cnf.lit(Ki)
            ])

    # Edges (assignments): bonus if NOT used.
    for i in range(f):
        for j in range(c):
            cij = service_cost[j][i]

            if cij < 0:
                # Forbidden edge (dist > coverage): force X_ij = FALSE.
                cnf.add_clause([cnf.lit(f"X_{i}_{j}", True)])
                continue

            # Scale to keep clause count reasonable.
            scaled = max(1, int(round(cij / edge_scale)))
            if scaled <= 0:
                scaled = 1

            Lij = f"L_{i}_{j}"
            Tij = f"T_l_{i}_{j}"

            # Force L_ij = FALSE: (~L_ij OR T_ij OR ~T_ij)
            cnf.add_clause([
                cnf.lit(Lij, True),
                cnf.lit(Tij),
                cnf.lit(Tij, True)
            ])

            # Add scaled copies of (~X_ij OR L_ij OR L_ij)
            for _ in range(scaled):
                cnf.add_clause([
                    cnf.lit(f"X_{i}_{j}", True),
                    cnf.lit(Lij),
                    cnf.lit(Lij)
                ])

    return cnf


# ---------------------------------------------------------------------
# Output in Max-3SAT group format
# ---------------------------------------------------------------------

def write_max3sat(cnf: CNF, out: TextIO) -> None:
    n = len(cnf.vars)
    m = len(cnf.clauses)
    print(f"{n} {m}", file=out)
    for a, b, c in cnf.clauses:
        print(f"{a} {b} {c}", file=out)


# ---------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------

def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Reduce 2D coverage-based Facility Location instance to Max-3SAT."
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        default="-",
        help="Input FLP file (or - / omitted for stdin).",
    )
    parser.add_argument(
        "--facility-scale",
        type=float,
        default=1.0,
        help="Scaling factor for facility opening costs (default 1.0).",
    )
    parser.add_argument(
        "--edge-scale",
        type=float,
        default=10.0,
        help="Scaling factor for assignment costs (default 10.0).",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    if args.input_file == "-" or args.input_file is None:
        stream = sys.stdin
    else:
        stream = open(args.input_file, "r")

    f, c, open_costs, fac_coords, cust_demands, cust_coords, coverage = read_flp_instance(stream)

    if stream is not sys.stdin:
        stream.close()

    service_cost = build_service_costs(
        f, c, open_costs, fac_coords, cust_demands, cust_coords, coverage
    )

    cnf = reduce_flp_to_max3sat(
        f, c, open_costs, service_cost,
        facility_scale=args.facility_scale,
        edge_scale=args.edge_scale,
    )

    write_max3sat(cnf, sys.stdout)


if __name__ == "__main__":
    main()

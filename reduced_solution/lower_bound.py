import sys
import math


def next_data_line(stream):
    """Read next non-empty, non-comment line or raise on EOF."""
    line = stream.readline()
    while line and (line.strip() == "" or line.lstrip().startswith("#")):
        line = stream.readline()
    if not line:
        raise ValueError("Unexpected EOF while reading input")
    return line.strip()


def read_instance(stream):
    """
    New input format:

        c f
        <c lines: client_name cx cy>
        <f lines: facility_name fx fy open_flag>
        <coverage_distance>

    Returns:
        f, c, fac_xy, cust_xy, coverage
    """

    header = next_data_line(stream)
    parts = header.split()
    if len(parts) != 2:
        raise ValueError(f"Expected header 'c f', got: {header!r}")
    c_str, f_str = parts
    c = int(c_str)
    f = int(f_str)

    # Clients
    cust_xy = []
    for _ in range(c):
        line = next_data_line(stream)
        tokens = line.split()
        if len(tokens) < 3:
            raise ValueError(
                f"Client line must have at least 3 tokens (name x y), got: {line!r}"
            )
        # name = tokens[0]
        x_str, y_str = tokens[1], tokens[2]
        cust_xy.append((float(x_str), float(y_str)))

    # Facilities
    fac_xy = []
    for _ in range(f):
        line = next_data_line(stream)
        tokens = line.split()
        if len(tokens) < 4:
            raise ValueError(
                "Facility line must have at least 4 tokens "
                "(name x y open_flag), got: {line!r}"
            )
        # name = tokens[0]
        x_str, y_str = tokens[1], tokens[2]
        # open_flag = tokens[3]  # ignored here
        fac_xy.append((float(x_str), float(y_str)))

    # Coverage distance
    coverage_line = next_data_line(stream)
    try:
        coverage = float(coverage_line)
    except ValueError as e:
        raise ValueError(f"Invalid coverage distance {coverage_line!r}") from e

    return f, c, fac_xy, cust_xy, coverage


def compute_lower_bound(f, c, fac_xy, cust_xy, coverage):
    """
    Compute a lower bound on the minimum number of facilities that must open
    to cover all clients under the coverage constraint.

    Lower bound approach:
    1) If any client has zero feasible facilities → infeasible → inf
    2) Force-open any facility that is the *only* option for a client
    3) Remove covered clients and repeat until stable
    4) Then greedily pick the facility covering the most remaining clients
       to estimate a lower bound (set cover style)

    Returns:
        LB (integer number of facilities), or inf if infeasible
    """

    # Build list of feasible coverage options:
    # covers[i] = list of client indices covered by facility i
    covers = [[] for _ in range(f)]
    for i in range(f):
        fx, fy = fac_xy[i]
        for j in range(c):
            cx, cy = cust_xy[j]
            if math.dist((fx, fy), (cx, cy)) <= coverage:
                covers[i].append(j)

    # For each client, track the facilities that can cover them
    can_cover = [[] for _ in range(c)]
    for i in range(f):
        for j in covers[i]:
            can_cover[j].append(i)

    # If any client has no coverage option → infeasible
    for j in range(c):
        if not can_cover[j]:
            return float('inf')

    required_facilities = set()
    remaining_clients = set(range(c))

    # Step 2: Force facilities that uniquely cover a client
    changed = True
    while changed:
        changed = False
        for j in list(remaining_clients):
            if len(can_cover[j]) == 1:
                only_fac = can_cover[j][0]
                if only_fac not in required_facilities:
                    required_facilities.add(only_fac)
                    changed = True

                # Remove all clients that this facility covers
                for k in covers[only_fac]:
                    if k in remaining_clients:
                        remaining_clients.remove(k)

    # Step 3: Greedy set-cover lower bound for remaining clients
    lb = len(required_facilities)

    while remaining_clients:
        # pick facility covering the most of the remaining uncovered clients
        best_fac = None
        best_cover = 0
        for i in range(f):
            count = sum(1 for j in covers[i] if j in remaining_clients)
            if count > best_cover:
                best_cover = count
                best_fac = i

        if best_fac is None:
            return float('inf')

        # open this facility
        lb += 1
        for j in covers[best_fac]:
            remaining_clients.discard(j)

    return lb



def main():
    if len(sys.argv) != 2:
        print("Usage: lower_bound.py <input_file>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], "r") as f:
        f_, c_, fac_xy, cust_xy, coverage = read_instance(f)

    lb = compute_lower_bound(f_, c_, fac_xy, cust_xy, coverage)

    if math.isinf(lb):
        print("inf")
    else:
        print(lb)


if __name__ == "__main__":
    main()

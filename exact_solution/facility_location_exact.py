import itertools
import math
import sys


def distance(a, b):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)


def parse_input(filename):
    with open(filename, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    # first line: number of clients, number of facilities
    n_clients, n_facilities = map(int, lines[0].split())

    clients = []
    facilities = []

    idx = 1

    # read clients
    for _ in range(n_clients):
        name, x, y = lines[idx].split()
        clients.append((name, float(x), float(y)))
        idx += 1

    # read facilities
    for _ in range(n_facilities):
        name, x, y, flag = lines[idx].split()
        facilities.append((name, float(x), float(y)))
        idx += 1

    # coverage distance
    coverage_dist = float(lines[idx])

    return clients, facilities, coverage_dist


def all_clients_covered(facilities_subset, clients, coverage_dist):
    """Check if all clients are within coverage_dist of at least one selected facility."""
    for cname, cx, cy in clients:
        covered = False
        for fname, fx, fy in facilities_subset:
            if distance((cx, cy), (fx, fy)) <= coverage_dist:
                covered = True
                break
        if not covered:
            return False
    return True


def solve_exact(clients, facilities, coverage_dist):
    best_solution = None
    best_count = float("inf")

    # Check all subsets of facilities
    for r in range(1, len(facilities) + 1):
        for subset in itertools.combinations(facilities, r):
            if all_clients_covered(subset, clients, coverage_dist):
                if r < best_count:
                    best_count = r
                    best_solution = subset

    return best_solution


def main():
    if len(sys.argv) != 2:
        print("Usage: python exact_solver.py <inputfile>")
        return

    clients, facilities, coverage_dist = parse_input(sys.argv[1])

    best = solve_exact(clients, facilities, coverage_dist)

    if best is None:
        print("No feasible solution exists.")
        return

    print("\n=== OPTIMAL SOLUTION FOUND ===")
    print(f"Coverage distance: {coverage_dist}")
    print(f"Facilities chosen ({len(best)}):")
    for fac in best:
        print(f"  {fac[0]} at ({fac[1]}, {fac[2]})")

    print("\nCoverage mapping:")
    for fac in best:
        covered_clients = []
        for cname, cx, cy in clients:
            if distance((cx, cy), (fac[1], fac[2])) <= coverage_dist:
                covered_clients.append(cname)
        print(f"{fac[0]} covers: {', '.join(covered_clients)}")


if __name__ == "__main__":
    main()

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


def assign_clients_to_facilities(clients, selected, coverage_dist):
    """
    Assign each client to EXACTLY ONE facility (the closest one in range).
    Returns (assignment_dict, total_distance)
    """
    assignment = {fac[0]: [] for fac in selected}
    total_dist = 0.0

    for cname, cx, cy in clients:
        best_fac = None
        best_dist = float("inf")

        for fname, fx, fy in selected:
            d = distance((cx, cy), (fx, fy))
            if d <= coverage_dist and d < best_dist:
                best_dist = d
                best_fac = fname

        if best_fac is None:
            raise ValueError(f"Client {cname} cannot be assigned to any chosen facility.")

        assignment[best_fac].append(cname)
        total_dist += best_dist

    return assignment, total_dist


def solve_exact(clients, facilities, coverage_dist):
    """
    Find the MINIMUM NUMBER of facilities needed to cover all clients
    within the coverage distance constraint.
    (Set Cover variant)
    """
    best_solution = None
    best_count = float("inf")
    best_assignments = None
    best_distance = None

    # Check all subsets of facilities, starting from smallest
    for r in range(1, len(facilities) + 1):
        for subset in itertools.combinations(facilities, r):
            if all_clients_covered(subset, clients, coverage_dist):
                # Found a valid solution with r facilities
                if r < best_count:
                    best_count = r
                    best_solution = subset
                    
                    # Calculate assignments and distance for reporting
                    try:
                        assignments, total_dist = assign_clients_to_facilities(
                            clients, subset, coverage_dist
                        )
                        best_assignments = assignments
                        best_distance = total_dist
                    except ValueError:
                        continue
        
        # Once we find a solution with r facilities, no need to check larger r
        if best_solution is not None:
            break

    return best_solution, best_assignments, best_distance, best_count


def main():
    if len(sys.argv) != 2:
        print("Usage: python exact_solver.py <inputfile>")
        return

    clients, facilities, coverage_dist = parse_input(sys.argv[1])

    best, assignments, total_dist, num_facs = solve_exact(clients, facilities, coverage_dist)

    if best is None:
        print("No feasible solution exists.")
        return

    print("\n=== OPTIMAL SOLUTION FOUND ===")
    print(f"Objective: Minimize number of facilities")
    print(f"Facilities opened: {num_facs} (OPTIMAL - minimum needed)")
    print(f"Total assignment distance: {total_dist:.2f} (for this solution)")
    print(f"Coverage distance constraint: {coverage_dist}")
    print(f"\nFacilities chosen ({len(best)}):")
    for fac in best:
        print(f"  {fac[0]} at ({fac[1]}, {fac[2]})")

    print("\nUnique Client Assignment:")
    for fac in best:
        fname = fac[0]
        clients_here = assignments[fname]
        print(f"{fname} covers: {', '.join(clients_here) if clients_here else 'None'}")


if __name__ == "__main__":
    main()
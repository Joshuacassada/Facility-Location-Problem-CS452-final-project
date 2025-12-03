import random
import time
import matplotlib.pyplot as plt
from facility_location_exact import solve_exact, distance

# --- Parameters ---
num_facilities_list = [5, 7, 10, 12, 15]   # number of facilities
num_clients_list    = [5, 7, 10, 12, 15]   # number of clients
coverage = 50  # adjust so multiple facilities are needed

runtimes = []

for f, c in zip(num_facilities_list, num_clients_list):
    # Generate random clients
    clients = [(f"C{i+1}", random.uniform(0, 100), random.uniform(0, 100)) for i in range(c)]
    
    # Generate facilities clustered near clients to ensure feasibility
    facilities = []
    for i in range(f):
        cx, cy = random.choice(clients)[1:3]
        fx = cx + random.uniform(-coverage, coverage)
        fy = cy + random.uniform(-coverage, coverage)
        facilities.append((f"F{i+1}", fx, fy))
    
    # --- Run exact solver and measure runtime ---
    start_time = time.time()
    best = solve_exact(clients, facilities, coverage)
    end_time = time.time()
    
    runtime = end_time - start_time
    runtimes.append(runtime)
    
    print(f"\n=== FLP for {f} facilities and {c} clients ===")
    if best is None:
        print("No feasible solution exists (unexpected!)")
        continue
    print(f"Facilities chosen ({len(best)}): {[fac[0] for fac in best]}")
    print(f"Time elapsed: {runtime:.2f} seconds")
    
    # --- Visualization ---
    plt.figure(figsize=(8,8))
    
    # Plot all facilities
    for fac in facilities:
        if fac in best:
            plt.scatter(fac[1], fac[2], c='red', s=150, marker='s', label='Open Facility' if fac==best[0] else "")
        else:
            plt.scatter(fac[1], fac[2], c='gray', s=80, marker='x', label='Closed Facility' if fac==facilities[0] else "")
    
    # Assign clients to nearest open facility that actually covers them
    assignments = {fac: [] for fac in best}
    for cname, cx, cy in clients:
        closest_fac = None
        for fac in best:
            if distance((cx, cy), (fac[1], fac[2])) <= coverage:
                closest_fac = fac
                break
        if closest_fac:
            assignments[closest_fac].append((cx, cy))
        else:
            print(f"Client {cname} not covered!")
    
    # Plot clients and edges
    colors = plt.cm.get_cmap("tab10", len(best))
    for idx, fac in enumerate(best):
        xs = [x for x, y in assignments[fac]]
        ys = [y for x, y in assignments[fac]]
        plt.scatter(xs, ys, s=30, c=[colors(idx)]*len(xs), label=f"Clients of {fac[0]}" if idx==0 else "")
        # Draw edges
        for x, y in assignments[fac]:
            plt.plot([fac[1], x], [fac[2], y], c=colors(idx), linewidth=0.8, alpha=0.6)
    
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.title(f"FLP Solution: {f} Facilities, {c} Clients")
    plt.legend(fontsize=8)
    plt.grid(True)
    plt.show()

# --- Plot runtime vs problem size ---
plt.figure(figsize=(8,5))
plt.plot([f+c for f,c in zip(num_facilities_list,num_clients_list)], runtimes, marker='o')
plt.xlabel("Number of facilities + clients")
plt.ylabel("Runtime (seconds)")
plt.title("Exact FLP Solver Runtime vs Problem Size")
plt.grid(True)
plt.show()

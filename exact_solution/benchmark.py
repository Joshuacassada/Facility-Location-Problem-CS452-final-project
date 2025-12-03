import random
import time
import matplotlib.pyplot as plt
from facility_location_exact import solve_exact, distance

# --- Parameters ---
customer_count = 5  # fixed number of customers
facility_sizes = list(range(2, 29))  # from 2 to 28 facilities
coverage = 30  # coverage distance (adjust so solution exists)
repeats = 1  # keep 1 repeat for large sizes to avoid extremely long runs

runtimes = []

def generate_test_case(num_facilities, num_customers):
    # Generate random facilities: (name, x, y)
    facilities = [(f"F{i+1}", random.uniform(0, 100), random.uniform(0, 100)) for i in range(num_facilities)]
    
    # Generate random customers: (name, x, y)
    customers = [(f"C{i+1}", random.uniform(0, 100), random.uniform(0, 100)) for i in range(num_customers)]
    
    # Ensure feasibility: every customer within coverage of at least one facility
    for i, (cx, cy) in enumerate([(c[1], c[2]) for c in customers]):
        if min([distance((cx, cy), (f[1], f[2])) for f in facilities]) > coverage:
            # Move customer closer to first facility
            fx, fy = facilities[0][1], facilities[0][2]
            customers[i] = (customers[i][0], fx + random.uniform(-coverage/2, coverage/2),
                            fy + random.uniform(-coverage/2, coverage/2))
    return facilities, customers

# --- Benchmark ---
for f in facility_sizes:
    print(f"Running solver for {f} facilities...")
    facilities, customers = generate_test_case(f, customer_count)
    start_time = time.time()
    solve_exact(customers, facilities, coverage)
    end_time = time.time()
    runtime = end_time - start_time
    runtimes.append(runtime)
    print(f"Facilities: {f}, Runtime: {runtime:.4f} seconds")

# --- Plot results ---
plt.figure(figsize=(10,5))
plt.plot(facility_sizes, runtimes, marker='o')
plt.xlabel("Number of Facilities")
plt.ylabel("Wall Clock Time (seconds)")
plt.title("Exact FLP Solver Runtime vs Number of Facilities")
plt.grid(True)
plt.show()

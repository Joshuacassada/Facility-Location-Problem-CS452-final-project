from facility_location_exact import solve_exact
import random
import time

# Parameters
f = 12      # number of potential facility locations
c = 200     # number of customers

# Generate random facilities: (opening_cost, (x, y))
facilities = [(random.randint(50, 150), (random.uniform(0, 100), random.uniform(0, 100))) for _ in range(f)]

# Generate random customers: (x, y)
customers = [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(c)]

# Show summary of generated data
print(f"Generated {f} facilities and {c} customers.")
print("Facility opening costs and coordinates:")
for i, (cost, coord) in enumerate(facilities):
    print(f"Facility {i}: cost={cost}, location={coord}")

start_time = time.time()
best_cost, best_set = solve_exact(facilities, customers)
end_time = time.time()

print("\n=== Solution ===")
print("Best total cost:", best_cost)
print("Facilities to open:", best_set)
print("Time elapsed:", end_time - start_time, "seconds")

# Optional: Show which customers go to which facility
assignments = {}
for cust in customers:
    closest_fac = min(best_set, key=lambda i: ((facilities[i][1][0] - cust[0])**2 + (facilities[i][1][1] - cust[1])**2))
    if closest_fac not in assignments:
        assignments[closest_fac] = []
    assignments[closest_fac].append(cust)

print("\nCustomer assignments to open facilities:")
for fac in best_set:
    print(f"Facility {fac} serves {len(assignments[fac])} customers")

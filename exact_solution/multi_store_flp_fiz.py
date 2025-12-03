from facility_location_exact import solve_flp
import random
import time
import matplotlib.pyplot as plt

# Parameters
f = 12      # number of potential facility locations
c = 200     # number of customers

# Generate random facilities: (opening_cost, (x, y))
facilities = [(random.randint(50, 150), (random.uniform(0, 100), random.uniform(0, 100))) for _ in range(f)]

# Generate random customers: (x, y)
customers = [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(c)]

# Solve FLP
start_time = time.time()
best_cost, best_set = solve_flp(facilities, customers)
end_time = time.time()

print(f"Generated {f} facilities and {c} customers.")
print("\n=== Solution ===")
print("Best total cost:", best_cost)
print("Facilities to open:", best_set)
print("Time elapsed:", end_time - start_time, "seconds")

# Assign customers to nearest open facility
assignments = {}
for cust in customers:
    closest_fac = min(best_set, key=lambda i: ((facilities[i][1][0] - cust[0])**2 + (facilities[i][1][1] - cust[1])**2))
    if closest_fac not in assignments:
        assignments[closest_fac] = []
    assignments[closest_fac].append(cust)

for fac in best_set:
    print(f"Facility {fac} serves {len(assignments[fac])} customers")

# --- Visualization ---
colors = plt.cm.get_cmap("tab10", len(best_set))

plt.figure(figsize=(10, 10))

# Plot all facilities
for i, (cost, coord) in enumerate(facilities):
    if i in best_set:
        plt.scatter(coord[0], coord[1], s=200, c='red', marker='s', label=f"Open Facility {i}" if i==best_set[0] else "")
    else:
        plt.scatter(coord[0], coord[1], s=80, c='gray', marker='x', label="Closed Facility" if i==0 else "")

# Plot customers
for idx, fac in enumerate(best_set):
    cust_coords = assignments[fac]
    xs = [x for x, y in cust_coords]
    ys = [y for x, y in cust_coords]
    plt.scatter(xs, ys, s=30, c=[colors(idx)]*len(xs), label=f"Customers of Facility {fac}" if idx==0 else "")

# Optional: draw lines from customers to their facility
for fac in best_set:
    fx, fy = facilities[fac][1]
    for x, y in assignments[fac]:
        plt.plot([fx, x], [fy, y], c='lightgray', linewidth=0.5)

plt.xlabel("X Coordinate")
plt.ylabel("Y Coordinate")
plt.title("Facility Location and Customer Assignments")
plt.legend(loc="upper right", fontsize=8)
plt.grid(True)
plt.show()

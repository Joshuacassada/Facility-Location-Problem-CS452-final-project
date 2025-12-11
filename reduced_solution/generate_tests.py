import random
import os
import math

# Output folder
os.makedirs("test_cases", exist_ok=True)


def euclid(x1, y1, x2, y2):
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)


def generate_test_case(filename, n_customers, n_facilities, coverage):
    customers = []
    facilities = []

    # Random customer coordinates
    for i in range(1, n_customers + 1):
        x = round(random.uniform(0, 100), 2)
        y = round(random.uniform(0, 100), 2)
        customers.append((f"C{i}", x, y))

    # Random facility coordinates
    for i in range(1, n_facilities + 1):
        x = round(random.uniform(0, 100), 2)
        y = round(random.uniform(0, 100), 2)
        facilities.append((f"F{i}", x, y, 0))  # last 0 like your sample

    # Ensure feasibility: each customer must be within coverage of at least one facility
    max_min_dist = 0
    for cx, cy in [(c[1], c[2]) for c in customers]:
        min_dist = min(euclid(cx, cy, f[1], f[2]) for f in facilities)
        if min_dist > max_min_dist:
            max_min_dist = min_dist

    # Increase coverage if needed (guarantees feasible instance)
    if coverage < max_min_dist:
        coverage = round(max_min_dist + 1.0, 2)

    # Write file
    with open(filename, "w") as f:
        f.write(f"{n_customers} {n_facilities}\n")

        for c in customers:
            f.write(f"{c[0]} {c[1]} {c[2]}\n")

        for fac in facilities:
            f.write(f"{fac[0]} {fac[1]} {fac[2]} {fac[3]}\n")

        f.write(str(coverage) + "\n")


# Generate 50 test cases with mixed difficulty
for i in range(1, 51):
    if i <= 20:
        # Small, easy
        n_customers = random.randint(5, 10)
        n_facilities = random.randint(5, 10)
        coverage = random.uniform(20, 40)
    elif i <= 40:
        # Medium complexity
        n_customers = random.randint(10, 15)
        n_facilities = random.randint(12, 18)
        coverage = random.uniform(10, 20)
    else:
        # Larger (slower), used for showing runtime scaling
        n_customers = random.randint(15, 20)
        n_facilities = random.randint(20, 25)
        coverage = random.uniform(5, 15)

    filename = f"test_cases/test_case_{i}.txt"
    generate_test_case(filename, n_customers, n_facilities, coverage)

print("50 test cases generated in 'test_cases/'")

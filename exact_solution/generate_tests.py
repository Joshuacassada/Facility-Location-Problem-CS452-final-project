import random
import os

os.makedirs("realistic_test_cases", exist_ok=True)

def generate_test_case(filename, n_clients, n_facilities, coverage):
    clients = []
    for i in range(1, n_clients+1):
        x = round(random.uniform(0, 100),2)
        y = round(random.uniform(0, 100),2)
        clients.append((f"C{i}", x, y))

    facilities = []
    for i in range(1, n_facilities+1):
        x = round(random.uniform(0, 100),2)
        y = round(random.uniform(0, 100),2)
        facilities.append((f"F{i}", x, y, 0))

    # Ensure feasibility: each client must be within coverage of at least one facility
    # Simple way: increase coverage if needed (guaranteed feasible)
    max_dist = 0
    for cx, cy in [(c[1], c[2]) for c in clients]:
        min_d = min([((cx-f[1])**2 + (cy-f[2])**2)**0.5 for f in facilities])
        if min_d > max_dist:
            max_dist = min_d
    if coverage < max_dist:
        coverage = round(max_dist + 1.0, 2)

    with open(filename, "w") as f:
        f.write(f"{n_clients} {n_facilities}\n")
        for c in clients:
            f.write(f"{c[0]} {c[1]} {c[2]}\n")
        for fac in facilities:
            f.write(f"{fac[0]} {fac[1]} {fac[2]} {fac[3]}\n")
        f.write(str(coverage) + "\n")


# Generate 50 test cases
for i in range(1, 51):
    if i <= 20:
        # Fast: small
        n_clients = random.randint(5,10)
        n_facilities = random.randint(5,10)
        coverage = random.uniform(15, 30)
    elif i <= 40:
        # Medium: ~1 min
        n_clients = random.randint(10,15)
        n_facilities = random.randint(12,18)
        coverage = random.uniform(5, 15)
    else:
        # Slow: minutes
        n_clients = random.randint(15,20)
        n_facilities = random.randint(20,25)
        coverage = random.uniform(5, 10)

    filename = f"realistic_test_cases/test_case_{i}.txt"
    generate_test_case(filename, n_clients, n_facilities, coverage)

print("50 test cases generated in 'realistic_test_cases/'")

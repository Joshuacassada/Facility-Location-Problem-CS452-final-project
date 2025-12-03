import random
import time
import matplotlib.pyplot as plt
from facility_location_exact import solve_flp

def generate_test_case(f, c):
    facilities = [(random.randint(10,100), (random.uniform(0,100), random.uniform(0,100))) for _ in range(f)]
    customers = [(random.uniform(0,100), random.uniform(0,100)) for _ in range(c)]
    return facilities, customers

# Benchmark: vary number of facilities
times = []
sizes = [2, 3, 4, 5, 6]  # small for exact solver
customers_count = 5

for f in sizes:
    facilities, customers = generate_test_case(f, customers_count)
    start = time.time()
    solve_flp(facilities, customers)
    end = time.time()
    times.append(end-start)

plt.plot(sizes, times, marker='o')
plt.xlabel("Number of facilities")
plt.ylabel("Wall clock time (seconds)")
plt.title("Exact FLP runtime vs number of facilities")
plt.grid(True)
plt.show()

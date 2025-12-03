import itertools
import math
import time

def euclidean_distance(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def total_cost(facilities, customers, open_facilities):
    cost = 0
    # Add opening costs
    for i in open_facilities:
        cost += facilities[i][0]  # facility opening cost

    # Assign each customer to nearest open facility
    for cust_coord in customers:
        min_dist = float('inf')
        for i in open_facilities:
            dist = euclidean_distance(facilities[i][1], cust_coord)
            if dist < min_dist:
                min_dist = dist
        cost += min_dist
    return cost

def solve_flp(facilities, customers):
    f = len(facilities)
    best_cost = float('inf')
    best_set = None

    # Enumerate all subsets of facilities
    for r in range(1, f+1):
        for subset in itertools.combinations(range(f), r):
            cost = total_cost(facilities, customers, subset)
            if cost < best_cost:
                best_cost = cost
                best_set = subset

    return best_cost, best_set

def read_input(filename):
    with open(filename) as f:
        lines = f.readlines()
    f_count, c_count = map(int, lines[0].split())
    
    # Facility opening costs and coordinates
    facilities = []
    for i in range(f_count):
        parts = list(map(float, lines[1+i].split()))
        opening_cost, x, y = parts[0], parts[1], parts[2]
        facilities.append((opening_cost, (x, y)))

    # Customer coordinates
    customers = []
    for i in range(c_count):
        x, y = map(float, lines[1+f_count+i].split())
        customers.append((x, y))

    return facilities, customers

if __name__ == "__main__":
    filename = "input.txt"
    facilities, customers = read_input(filename)
    
    start_time = time.time()
    best_cost, best_set = solve_flp(facilities, customers)
    end_time = time.time()

    print("Best cost:", best_cost)
    print("Facilities to open:", best_set)
    print("Time elapsed:", end_time - start_time, "seconds")

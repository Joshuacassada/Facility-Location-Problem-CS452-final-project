import sys
import math

def compute_lower_bound(f, c, fac_cost, fac_xy, cust_dem, cust_xy):
    lb = 0.0

    for j in range(c):
        cx, cy = cust_xy[j]
        dj = cust_dem[j]

        best_cost = float('inf')
        for i in range(f):
            fx, fy = fac_xy[i]
            dist = math.sqrt((fx - cx)**2 + (fy - cy)**2)
            cost = dj * dist
            if cost < best_cost:
                best_cost = cost

        lb += best_cost

    return lb


def main():
    data = sys.stdin.read().strip().split()
    ptr = 0

    # read counts
    f = int(data[ptr]); ptr += 1
    c = int(data[ptr]); ptr += 1

    # read facility opening costs (but NOT used in LB)
    fac_cost = list(map(float, data[ptr:ptr+f])); ptr += f

    # facility coordinates
    fac_xy = []
    for _ in range(f):
        x = float(data[ptr]); y = float(data[ptr+1])
        ptr += 2
        fac_xy.append((x, y))

    # read customer demands
    cust_dem = list(map(float, data[ptr:ptr+c])); ptr += c

    # customer coordinates
    cust_xy = []
    for _ in range(c):
        x = float(data[ptr]); y = float(data[ptr+1])
        ptr += 2
        cust_xy.append((x, y))

    lb = compute_lower_bound(f, c, fac_cost, fac_xy, cust_dem, cust_xy)
    print(lb)


if __name__ == "__main__":
    main()

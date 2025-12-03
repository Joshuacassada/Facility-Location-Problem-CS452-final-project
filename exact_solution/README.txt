Facility Location Problem – Exact Solver
========================================

Program Description:
-------------------
This program computes the exact optimal solution for the Facility Location Problem (FLP) using a brute-force approach. 
Given a set of potential facilities (each with an opening cost and coordinates) and a set of customers (with coordinates), 
the program determines which subset of facilities to open to minimize the total cost, where the total cost is defined as:

    Total cost = Sum of opening costs of opened facilities + Sum of Euclidean distances from each customer to their nearest open facility.

The program can handle small to moderate numbers of facilities efficiently. The runtime grows exponentially with the number of facilities, but linearly with the number of customers.

----------------------------------------
Running Time Complexity (O-notation):
----------------------------------------
Let:
    f = number of potential facilities
    c = number of customers

- The program enumerates all non-empty subsets of facilities: there are 2^f - 1 subsets.
- For each subset, it computes the assignment cost for each customer to their nearest open facility (O(c * |subset|) ≤ O(c*f)).

Therefore, the total runtime is:

    O(2^f * c * f)

Notes:
- Exponential growth in f makes this approach feasible only for small numbers of facilities (e.g., f ≤ 15).
- The number of customers (c) increases runtime linearly, so hundreds of customers are manageable.

----------------------------------------
Sample Input File Format:
----------------------------------------
The input file should be a plain text file with the following format:

    f c
    <f lines: opening_cost x y>
    <c lines: x y>

Example (`input.txt`):
10 5
10 0 0
15 10 0
20 5 5
12 7 2
18 3 8
25 8 8
14 2 3
22 6 6
16 1 9
19 4 4
1 1
2 2
8 1
7 7
5 5

----------------------------------------
Example Command Line:
----------------------------------------
To run the exact solver using the sample input file:

Windows PowerShell / Command Prompt:

    python facility_location_exact.py

Output:
    Best cost: <calculated total cost>
    Facilities to open: <indices of facilities in optimal subset>
    Time elapsed: <seconds>

Alternatively, to run a randomized multi-store scenario with hundreds of customers:

    python multi_store_flp.py

Output:
    Generates random facilities and customers.
    Prints best total cost, facilities to open, and customer assignments.
    Optional visualization can be run using `multi_store_flp_viz.py` to plot facility locations and customer clusters.

----------------------------------------
Dependencies:
----------------------------------------
- Python 3.x
- matplotlib (for visualization)
    Install via: pip install matplotlib

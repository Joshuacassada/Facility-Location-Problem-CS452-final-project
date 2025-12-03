Running Time Analysis

This project computes the Exact Solution to the Facility Location / Set Cover–style covering problem using exhaustive search.
Given:

F = number of facilities

C = number of clients

A fixed coverage radius R

The program must determine the minimum number of facilities whose coverage collectively reaches all clients.

Algorithmic Running Time

The solver tries every subset of facilities until it finds the smallest feasible one.
Thus:

Worst-Case Running Time:

O(2^F ⋅ F ⋅ C)

Explanation:

There are 
2^𝐹 subsets of facilities.

For each subset, the program checks coverage for all clients.

Coverage check costs O(F⋅C) in the naive implementation.

Notes:

Runtime grows exponentially in the number of facilities, not clients.

For large input (F > ~25), runtime becomes multiple minutes.

This is expected: the decision version of the problem is NP-Complete, via reduction from Set Cover.



How to Run the Program

Your program is executed using:

python facility_location_exact.py sample_input.txt


Where:

facility_location_exact.py is your script

inputfile.txt contains facilities, clients, and coverage radius

A sample input file might look like:

10 5
C1 69.69 90.47
C2 45.03 61.68
C3 26.71 57.00
C4 77.94 68.52
C5 43.43 61.07
F1 6.20 33.75 0
F2 8.26 9.32 0
F3 44.19 98.25 0
F4 62.91 66.37 0
F5 94.27 1.72 0
33.14

Example Command Line
python flp_exact_solver.py test_case_4.txt

Example Output
=== OPTIMAL SOLUTION FOUND ===
Coverage distance: 33.14
Facilities chosen (3):
  F1 at (6.20, 33.75)
  F4 at (62.91, 66.37)
  F3 at (44.19, 98.25)

Coverage mapping:
F1 covers: C2
F3 covers: C1, C4
F4 covers: C5, C2
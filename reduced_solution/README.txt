------------------
Reduction Overview
------------------

reduction.py converts a 2D uncapacitated Facility Location Problem instance
into an equivalent Max-3SAT instance in order to help prove NP Completeness

Using our inputs:
    <number of clients: c> <number of facilities: f>
    C1 XY
    C2 XY
    ...
    f1 XY
    f2 XY
    ...
    Max Coverage Distance

It produces a Max-3SAT input file:
    n m
    l11 l12 l13
    l21 l22 l23
    ...


---------------------
Running Time Analysis
---------------------

Reduction.py:

    Reading input = O(c + f)
        Reading facilities, customers, costs, and coordinates runs in

    Computing service costs = O(cf)
        For each pair (facility i, customer j) we compute a Euclidean distance:

    Creating variables = O(cf)
        f variables Y_i
        f×c variables X_i_j
        Additional helper variables Z, K, T, and L for chains and cost scaling

    Worst Case = O(cf^2)

lower_bound.py:
    Reading input = O(c + f)
    Computing distance from each customer to each facility = O(f * c)
    Checking coverage of each client and computing a 
        lower bound on the number of facilities = O(f * c)

    Worst case = O(cf)


--------------------------
Example Command Line Usage
--------------------------

Example Input:
10 7
C1 96.71 50.44
C2 85.44 29.26
C3 17.51 87.18
C4 84.88 32.83
C5 89.2 4.17
C6 38.6 13.58
C7 90.91 57.27
C8 29.06 47.2
C9 80.36 72.45
C10 60.32 28.06
F1 8.36 75.83 0
F2 98.5 10.78 0
F3 64.17 86.18 0
F4 29.53 37.02 0
F5 22.88 87.4 0
F6 44.2 41.31 0
F7 4.29 39.5 0
40.7


---------------------------------------
How to run the reduction and test cases
---------------------------------------

from inside the reduced_solution directory:
$ python3 reduction.py {Example uflp input} > {output file}

using the test case script from inside the test_cases directory:
$ ./run_test_cases.sh

The test case script runs all 50 tests through the lower bound, 
approximate solution, and exact solution, and produces a csv file of their outputs
which are the min facilities needed for the input

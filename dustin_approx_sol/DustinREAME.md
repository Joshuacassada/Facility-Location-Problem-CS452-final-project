Approximation Solution (Dustin Smith)

Facility Location Problem – Anytime Greedy Approximation Solver

This folder contains my approximation-based solution for the Facility Location Problem (FLP), developed for the Approximation Solution Architect component of the CS452 Final Project. The goal of this module is to produce a high-quality, polynomial-time approximation algorithm that can run under a specified time budget, support randomized greedy behavior, and generate results that are comparable to the exact and reduction solutions implemented by other members of the group.

1. Overview of the Approach

My approximation algorithm is based on a randomized greedy construction combined with an anytime improvement loop. Each greedy run incrementally selects facilities that cover the largest number of uncovered clients within the coverage distance, breaking ties randomly as required by the project specification. The solver always produces a feasible solution, even when some clients are beyond the given coverage distance, by assigning those clients to their nearest facility.

An anytime wrapper repeatedly invokes this greedy procedure until the time limit provided with the -t argument expires. Across iterations, randomness produces variations in solutions, and the solver keeps whichever solution is best according to two criteria: (1) minimizing the number of facilities opened, and (2) minimizing total client-to-facility assignment distance when the first measure is tied. This ensures the solution quality improves with more available runtime, demonstrating the anytime property described in the requirements.

2. Input Format

The solver uses the simplified input format adopted across the project so that exact, reduction, and approximation solutions can be directly compared. The input consists of:

A first line specifying the number of clients and facilities.

The list of clients, each given as:

client_name x y


The list of facilities, each given as:

facility_name x y initially_open_flag


A final line containing the coverage distance.

An example of a valid input file is shown below:

4 3
C1 2 3
C2 5 4
C3 1 7
C4 6 8
F1 2 4 0
F2 5 5 0
F3 1 6 0
2.5


This format is the same one used by the team’s exact solver and reduction solver, ensuring compatibility across all solutions.

3. Output Format

The solver outputs the set of facilities it opens, followed by a coverage mapping showing which clients were assigned to each opened facility. The structure is straightforward and human-readable:

Open facilities:
F1 F2 F3

Coverage:
F1 covers: C1
F2 covers: C2 C4
F3 covers: C3


The exact formatting mirrors the example format distributed in Canvas and used by the exact solution architect.

4. Algorithm Details and Runtime Analysis

The algorithm proceeds in two stages: a single greedy construction and an anytime loop that repeats this construction as long as time remains.

Greedy Construction

During one greedy construction:

For each unopened facility, the solver computes how many currently uncovered clients it can serve within the coverage distance.

It selects the facility that covers the largest number of these clients.

When multiple facilities achieve the same coverage gain, the solver uses random tie-breaking, ensuring variability between runs.

Once no unopened facility can cover additional clients within range, the remaining uncovered clients—if any—are assigned to their nearest facility (opening it if needed).

Runtime Complexity

Let:

C = number of clients

F = number of facilities

The algorithm precomputes all pairwise client–facility distances in:

O(C × F)

During the greedy phase, each iteration evaluates all unopened facilities, and each evaluation scans through all clients. In the worst case, up to F facilities may be opened. Therefore, a single greedy construction takes:

O(F² × C)

Since the solver invokes this greedy procedure repeatedly inside an anytime loop, the number of constructions depends on the time limit, but each iteration remains polynomial in the size of the input as required by the project.

5. Anytime Behavior

The solver accepts a mandatory command-line argument -t <seconds>, specifying how long the algorithm is allowed to run. Within this window, the solver repeats randomized greedy constructions, stores the best solution encountered, and returns that result when the time expires. This behavior satisfies the project’s requirement for an anytime procedure that improves solution quality the longer it is allowed to run.

6. Example Usage

The following command runs the solver for two seconds on the example input file:

python3 facility_location_approx.py -t 2.0 example_input.txt --seed 42


Here:

-t 2.0 provides a 2-second time limit

example_input.txt is the input file included in this folder

--seed 42 is optional and ensures reproducible randomized behavior

7. Test Cases and Folder Structure

This project uses a centralized /testcases directory shared across all solvers produced by the group. The directory contains:

25 small cases originating from the optimal solution architect

25 additional small and medium cases

25 larger cases designed to stress the exact solver

One extreme case that pushes the exact solver to multi-minute runtimes

My outputs generated from these tests are stored in:

dustin_approx_sol/test_outputs/


Each teammate maintains their own test outputs in their own solver folder while sharing the same test cases.

A shell script derived from the shared template is used to run all test cases automatically and direct output to the correct location.

8. Included Files

This folder contains:

facility_location_approx.py — my approximation solver

README.txt — this documentation file

example_input.txt — sample input file

test_outputs/ — results from running shared test cases

A teammate-customizable shell script for running all shared test cases

9. Summary

This approximation solution satisfies all requirements laid out in the project description, including polynomial runtime, randomized greedy behavior, anytime termination, compatibility with the shared input format, and the ability to run consistently across a suite of shared test cases. It produces high-quality approximations within the prescribed time window and supports direct comparison against the exact and reduction approaches developed by the other members of the team.
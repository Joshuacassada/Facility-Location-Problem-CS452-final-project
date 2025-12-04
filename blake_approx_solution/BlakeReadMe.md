Facility Location – Approximation Solution (Blake Buchert)

CS452 Final Project

This directory contains the approximation-based solution for the Facility Location Problem developed for the CS452 final project. The purpose of this component is to compute high-quality feasible solutions in polynomial time for instances where the exact solver becomes too slow to finish.

Unlike greedy constructions, this solver is based on stochastic local search with simulated annealing, enabling it to explore a wider space of feasible configurations. Because the method is anytime, it always produces a complete solution before the time limit and continues refining that solution as long as time remains.

In this project, the Facility Location Problem requires selecting which facilities to open so that every client is assigned to an open facility within a fixed coverage radius. Assignment costs are based on Euclidean distance. Since the exact solver grows exponentially with the number of facilities, approximation is essential for medium and large inputs. This implementation is designed to remain efficient under time constraints while staying fully compatible with the exact solver’s input and output formats.

Approximation Method Summary

This solver does not use a greedy construction. Instead, it begins with a fully feasible configuration in which all facilities are open. Because every client must be covered by some open facility within the specified radius, starting from the maximal open set guarantees feasibility even on difficult instances.

From this starting point, the solver performs stochastic local search using three neighborhood operations:

OPEN: add a closed facility to the solution

CLOSE: remove an open facility

SWAP: exchange an open facility with a closed one

Each proposed modification creates a new candidate solution. After every move, clients are reassigned to their nearest open facility. If any client cannot be assigned within the coverage radius, the candidate move is discarded as infeasible — ensuring that the algorithm always operates within the space of valid solutions.

To avoid local minima, the solver uses simulated annealing:

Improving moves are always accepted.

Worse moves may be accepted early on with a probability controlled by a temperature parameter that decreases over time.

This process continues until the time limit is reached. Because the modifications are random, different runs explore different regions of the solution space, and the solver may discover progressively better feasible solutions. This satisfies both the anytime and stochastic requirements of the project.

Runtime Analysis

Let n = number of clients, m = number of candidate facilities.

The dominant operation in each local-search iteration is reassigning all clients to their nearest open facility. This requires:

𝑂 ( 𝑛 ⋅ 𝑚 )

since each client may need to check every open facility in the worst case.

A single local-search run performs at most O(m²) neighborhood moves (a standard polynomial cap for local-search heuristics). Each move requires a full reassignment evaluation, giving:

𝑂(2𝑚 ⋅ 𝑛𝑚) = 𝑂(2𝑚𝑛 ⋅ 2𝑚^2)


All operations inside this loop run in polynomial time with respect to the input size.

The anytime wrapper simply repeats these polynomial-time search phases until the user-supplied time limit expires. Thus the runtime is determined by the deadline rather than problem size and satisfies the project requirement that approximation methods run in polynomial time.

Test Cases Included

This directory contains 50 test cases covering small, medium, and large instances. These files include a range of facility distributions, densities, and coverage radii. A very large instance is also provided to demonstrate that the exact solver fails to finish within a reasonable time, while the approximation solver continues to refine solutions efficiently.

Plots and Analysis

Graphs are generated using make_plots.py. These include:

Anytime improvement plots, showing how solution quality improves as more time is allowed.

Distance plots, showing total assignment distance across all test cases.

Open facility counts, demonstrating how aggressively the algorithm prunes facilities under the coverage constraint.

When exact solver outputs are added, the script will also generate:

Approximation vs. Exact total distance comparison

Approximation vs. Exact facility count comparison

These plots support the final project presentation and help illustrate approximation quality.

Input Format

The solver accepts files formatted according to the exact solver’s specification:

<grid_width> <grid_height>
<number_of_facilities>
<number_of_clients>
<facility_x> <facility_y>
<client_x> <client_y>


All coordinate-based inputs are fully compatible with the exact solver.

Output Format

The solver outputs:

<total_cost>
<f_id> <client_id_1> <client_id_2> ...
<f_id> <client_id_1> <client_id_2> ...


Each line after the cost lists an open facility followed by the clients assigned to it. Only feasible assignments (clients within coverage radius) appear in the output.

Folder Contents

This directory contains:

facility_location_approx_blake.py, the complete approximation solver

make_plots.py, used to generate visualizations

run_tests_blake.sh, a script to run all test cases

testcases/, containing all 50 instance files including a large benchmark instance

test_outputs/, where solver outputs are stored

README.txt, this document

presentation.pdf (added prior to submission)

Summary

This approximation framework uses stochastic local search, OPEN/CLOSE/SWAP neighborhood exploration, and simulated annealing, all under a hard coverage constraint that ensures every client is always reached by some open facility.

The solver satisfies the anytime requirement, improves solution quality over time, runs each iteration in polynomial time, and remains fully compatible with the exact solver’s input and output formats. These components collectively fulfill the responsibilities of the Approximation Solution Architect as defined in the project specification.
Facility Location – Approximation Solution (Dustin Smith)

CS452 Final Project

This directory contains the approximation-based solution for the Facility Location Problem developed for the CS452 final project. The goal of this component is to compute high-quality, near-optimal solutions in polynomial time for instances where the exact solver becomes too slow to finish. The approximation method implemented here combines a randomized greedy construction with an anytime stochastic refinement loop. Because of this structure, the solver always returns a complete feasible solution before the time limit and continues improving that solution as long as time is available.

In this project, the Facility Location Problem requires determining which facilities to open and how to assign each client to an open facility so that the overall assignment cost is minimized. Costs are based on Euclidean distance between clients and facilities. Since the exact solver grows exponentially with the number of facilities, approximation is essential for achieving good performance on medium and large instances. This implementation is designed specifically to be efficient under time constraints while remaining compatible with the exact solver’s input and output formats.

Approximation Method Summary

The solver begins with a randomized greedy construction. Facilities are randomly shuffled, and each candidate facility is evaluated to determine whether adding it decreases total cost. A facility is included only if it improves the solution. After this forward pass, a pruning step removes any facilities that do not significantly contribute to reducing the assignment cost. This produces a valid and reasonably effective starting solution.

After this initialization, the solver enters an anytime improvement loop. In this loop, small random modifications are applied to the current best solution, such as adding or removing facilities. Each modified solution is evaluated independently, and improvements replace the current best result. This loop continues only until the user-specified time limit is reached. Because the modifications are random, different runs may produce different solutions, and because the loop continues as long as time remains, the method satisfies the stochastic and anytime requirements of the project.

Runtime Analysis

Let n denote the number of clients and m the number of candidate facilities.

The dominant operation in the approximation method is the computation of total cost for a candidate solution. This involves assigning each client to its nearest open facility, which takes:

𝑂(𝑛 ⋅ 𝑚)

in the worst case when many facilities are open.

The greedy initialization phase evaluates O(m) potential facility additions, and each evaluation computes a full assignment cost, giving:

𝑂(𝑚 ⋅ 𝑛 ⋅ 𝑚) = 𝑂 (𝑛𝑚^2)

The anytime improvement loop evaluates one candidate per iteration, each requiring an     O(nm) cost computation. Since this loop continues only until the time limit is reached, the overall runtime is determined by the user-supplied deadline rather than by the problem size. Each iteration is polynomial in n and m, satisfying the project requirement that the approximation method must run in polynomial time.

Test Cases Included

This directory contains exactly 50 test cases that span small, medium and large instance sizes. The cases include a variety of spatial distributions and ratios of clients to facilities. A single extremely large test case is additionally included to demonstrate that the exact solver cannot finish within a practical time window, while the approximation solver continues to run efficiently.

Plots and Analysis

Graphs are generated using make_plots.py. These include:

• Anytime Improvement Plot, showing how the approximation improves as more time is allowed.
• Approximation-only distance plot, showing the total assignment distance across all 50 test cases.
• Facilities open plot, showing how many facilities the approximation algorithm selects per test case.

When exact solver outputs become available, the same script will also produce:

• Approximation versus Exact total cost comparison.
• Approximation versus Exact facility count comparison.

These plots are essential for the final project presentation and for demonstrating approximation quality.

Input Format

The solver accepts files formatted according to the exact solver’s specification:

<grid_width> <grid_height>
<number_of_facilities>
<number_of_clients>
<facility_x> <facility_y>     (m lines)
<client_x> <client_y>         (n lines)


This ensures that the approximation system is fully compatible with the exact solver’s input format.

Output Format

The solver outputs:

<total_cost>
<f_id> <client_id_1> <client_id_2> ...
<f_id> <client_id_1> <client_id_2> ...


Each line after the cost lists one open facility and the client identifiers assigned to that facility. This output format is consistent with the exact solver and supports direct comparison.

Folder Contents

This directory contains:

• facility_location_approx.py, the complete approximation solver.
• make_plots.py, the script used to generate all required graphs.
• dustin_run_test_cases.sh, an automated script that runs the solver across all test cases.
• testcases, a folder containing all 50 test cases and the extremely large instance.
• test_outputs, the directory where solver outputs are collected.
• README.txt, this document.
• presentation.pdf, which will be added prior to final submission.

Summary

This approximation framework uses a randomized greedy construction phase and incorporates randomness throughout the refinement stage. It satisfies the anytime requirement by improving solutions until the time limit is reached. Each iteration runs in polynomial time. The solver is consistent with the exact solver’s input and output requirements, includes all required test cases and automation scripts, and provides the visual analysis necessary for evaluating solution quality. These components collectively meet the expectations for the Approximation Solution Architect role in the project specification.
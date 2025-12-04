Facility Location Approximation Solution

Dustin Smith — CS452 Final Project

## **Overview**

This project implements a polynomial-time anytime approximation algorithm for the Facility Location problem used in CS452. The variant studied here focuses on minimizing the number of facilities opened while ensuring that every client is assigned to a facility within a specified coverage distance. 

Because the exact solver becomes prohibitively slow for larger instances (exponential complexity), the goal of this approximation is to:

- Produce valid solutions quickly  
- Adaptively improve solutions over time  
- Demonstrate randomized behavior (as required for greedy tie-breaking)  
- Provide meaningful comparisons against the exact optimal solver  
- Handle large test cases where the exact method cannot finish  

This solver is intentionally designed to be fast, randomized, and anytime, making it robust under strict runtime constraints and capable of scaling to much larger problem sizes.

---

## **Input Format**

The approximation solver uses the same format as the exact solver:

```
<num_clients> <num_facilities>
C1 x y
C2 x y
...
F1 x y 0
F2 x y 0
...
<coverage_distance>
```

Where:

- `num_clients` = number of client points  
- `num_facilities` = number of possible facility locations  
- Each client is given as: `Cx x y`  
- Each facility is given as: `Fx x y 0`  
- The final line contains the coverage distance R

All provided `test_case_X.txt` files follow this format.



## **Output Format**

The solver prints:

```
=== APPROXIMATION SOLUTION FOUND ===
Coverage distance: R
Facilities chosen:
F7
F14
...
Coverage mapping:
C3 -> F14
C10 -> F7
...
```

The output includes:

- The coverage distance  
- The set of facilities the algorithm opened  
- A full mapping of each client to its covering facility  

This format mirrors the exact solver for 1-to-1 comparison.



## **Approximation Algorithm Description**

The implementation consists of three major components:



### **1. Randomized Greedy Coverage Construction**

This phase attempts to cover as many clients as possible quickly:

- Precompute coverage sets: which clients each facility can reach within distance R  
- Maintain a set of uncovered clients  
- For each unopened facility, compute:
  - `gain = number of uncovered clients it covers`
  - Add randomized noise to satisfy the project requirement for random tie-breaking:
    ```python
    gain += rng.randint(-2, 1)
    gain = max(gain, 0)
    ```
- Choose a facility using a softmax probability:
  ```
  P(facility j) ∝ exp(beta * gain_j)
  ```
- Mark clients as covered, repeat until no further progress is possible

This creates natural variability and randomized behavior while remaining polynomial.



### **2. Fallback Assignment for Uncovered Clients**

If some clients remain uncovered after greedy:

- For each uncovered client, locate the nearest facility in the entire facility set  
- Open it if necessary  
- Assign the client to that facility  

This guarantees feasibility and eliminates the possibility of empty facilities.



### **3. Anytime Improvement Loop (`-t`)**

The solver then enters an improvement loop until time expires:

- Runs small randomized perturbations to explore alternate subsets  
- Keeps any solution that maintains coverage with fewer or equal facilities 
- Stops immediately at the time limit  

This satisfies the required definition of an anytime algorithm:  
It can return the best solution found so far at any moment.



## **Runtime Complexity (O-notation)**

Let:

- `n` = number of clients  
- `m` = number of facilities  

Breakdown:

### **Coverage Preprocessing**
Compute all client–facility distances:  
O(nm)

### **Greedy Construction**
For each facility considered:  
Compute gain in O(n) 

Done for up to `m` facilities →  
O(nm) per greedy cycle  

Worst case up to `m` cycles →  
O(nm²) total  

### **Fallback Assignment**
Each client scans all facilities →  
O(nm)

### **Anytime Phase**
Each perturbation is O(n + m)
But bounded by the timeout parameter.

### **Overall Runtime:**  

O(nm^2)


This satisfies the requirement that the approximation must run in polynomial time independent of timeout behavior.



## **How to Run**

Example command:

```
python3 facility_location_approx.py -t 2.0 test_case_17.txt
```

- `-t 2.0` → run for up to 2 seconds  
- `test_case_17.txt` → input file  

The solver will always terminate under the time limit.



## **Test Cases Included**

The repository includes:

- **25 exact-comparison cases** (`test_case_17` through `test_case_42`)  
- **50 approximation-only cases** (`test_case_1` through `test_case_50`)  
- **One large stress test** (`test_case_41.txt`) annotated in the script:

```
# test_case_41.txt is intentionally larger so that the exact solver exceeds 5 minutes
```

A shell script `dustin_run_test_cases.sh` automates running all cases.



## **Presentation Requirements Included**

The accompanying presentation (PDF) includes:

- Explanation of approximation design  
- Runtime analysis  
- Anytime behavior plot  
- Approx-only facility count plot (1–50)  
- Exact vs approximation plot (17–42)  
- Clear demonstration that the approximation does not always match optimal  
- Discussion of trade-offs and behavior

This satisfies the course project requirements.



## **Files Included**

- `facility_location_approx.py` — main solver  
- `make_plots.py` — automated plot generator  
- `dustin_run_test_cases.sh` — batch runner  
- `test_cases/` — all input files  
- `Presentation.pdf` — final slides  
- `README.md` — this document  



## **Summary**

This project delivers a fast, scalable, randomized, anytime approximation for the facility-minimization problem. It mirrors the exact solution’s input/output format, supports a strict time budget through an anytime loop, and demonstrates realistic behavior where the approximation may outperform or underperform the exact solver depending on runtime and randomness. The full set of provided plots and test cases clearly illustrates the approximation’s strengths and limitations.
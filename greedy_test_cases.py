import subprocess
import matplotlib.pyplot as plt

# ----------------------------
# Configuration
# ----------------------------
EXACT_SOLVER = "exact_solution/facility_location_exact.py"
APPROX_SOLVER = "blake_approx_solution/facility_location_approx_blake.py"
APPROX_T = 1
SEED = 42
MAX_TESTS = 10

# ----------------------------
# Test Cases (just names for plotting)
# ----------------------------
test_case_names = [
    "trap_01_two_clusters",
    "trap_02_overlap_clusters",
    "trap_03_linear_chain",
    "trap_04_star",
    "trap_05_tictactoe_dense",
    "trap_06_asymmetric",
    "trap_07_overlap_central",
    "trap_08_sparse_chain",
    "trap_09_two_small_clusters",
    "trap_10_large_square",
]

# ----------------------------
# Run solver helper
# ----------------------------
def run_solver(solver_path, test_file, approx=False):
    cmd = ["python", solver_path]
    if approx:
        cmd += ["-t", str(APPROX_T), "--seed", str(SEED)]
    cmd.append(test_file)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = result.stdout.splitlines()

        fac_count = None
        i = 0
        while i < len(output):
            line = output[i].strip()

            # Exact solver
            if line.startswith("Facilities opened:") or line.startswith("Facilities chosen"):
                fac_count = sum(1 for w in line.split() if w.isdigit())
                break

            # Approx solver
            if line.startswith("Open facilities:"):
                i += 1
                if i < len(output):
                    fac_line = output[i].strip()
                    if fac_line:
                        fac_count = len(fac_line.split())
                break
            i += 1

        return fac_count

    except Exception as e:
        print(f"  Error running solver: {e}")
        return None

# ----------------------------
# Main: run all tests
# ----------------------------
exact_results = []
approx_results = []

for i, name in enumerate(test_case_names, 1):
    test_file = f"test_{name}.txt"  # assuming these test files already exist
    print(f"[{i}/{len(test_case_names)}] Testing {name}...")

    exact = run_solver(EXACT_SOLVER, test_file)
    approx = run_solver(APPROX_SOLVER, test_file, approx=True)

    exact_results.append(exact)
    approx_results.append(approx)

    print(f"  Exact solver... {'✓ ' + str(exact) + ' facilities' if exact else '✗ failed'}")
    print(f"  Approx solver... {'✓ ' + str(approx) + ' facilities' if approx else '✗ failed'}")

# ----------------------------
# Plotting
# ----------------------------
plt.figure(figsize=(12, 6))
x = range(len(test_case_names))

plt.plot(x, exact_results, marker='o', label='Exact Solver', color='green')
plt.plot(x, approx_results, marker='x', label='Approx Solver', color='red')

plt.xticks(x, test_case_names, rotation=45, ha='right')
plt.ylabel("Number of Facilities")
plt.title("Exact vs Approximate Facility Location Results")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

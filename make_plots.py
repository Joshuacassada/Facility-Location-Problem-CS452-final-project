import matplotlib.pyplot as plt
import re
import os

# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def read_cost_from_output(filename):
    """
    Reads the FIRST line of an approximation output (the cost).
    Assumes file format:
       <cost>
       facility: customers...
    """
    try:
        with open(filename, "r") as f:
            first = f.readline().strip()
            return float(first)
    except:
        return None


def read_optimal_cost(filename):
    """
    Reads the FIRST line from the *optimal solver output*.
    You must export these from your teammate.
    """
    with open(filename, "r") as f:
        return float(f.readline().strip())


# ---------------------------------------------------------
# 1. Approx vs Optimal Plot
# ---------------------------------------------------------

def plot_approx_vs_optimal():
    approx_costs = []
    optimal_costs = []
    case_numbers = []

    # Assumes:
    #   test_small_XX.txt       (input)
    #   test_small_XX.opt       (optimal solver output)
    #   test_small_XX.out       (our approx output)
    #
    # You ONLY need to provide the .opt files yourself.

    for i in range(1, 26):    # 1–25
        idx = f"{i:02d}"
        approx_file = f"test_cases/test_small_{idx}.out"
        optimal_file = f"test_cases/test_small_{idx}.opt"

        if not os.path.exists(approx_file):
            print(f"Missing: {approx_file}")
            continue
        if not os.path.exists(optimal_file):
            print(f"Missing optimal file: {optimal_file}")
            continue

        approx_c = read_cost_from_output(approx_file)
        opt_c = read_optimal_cost(optimal_file)

        approx_costs.append(approx_c)
        optimal_costs.append(opt_c)
        case_numbers.append(i)

    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(case_numbers, optimal_costs, 'o-', label="Optimal")
    plt.plot(case_numbers, approx_costs, 's-', label="Approximation")

    plt.xlabel("Test Case (1–25)")
    plt.ylabel("Total Cost")
    plt.title("Approximation vs Optimal (Small Cases)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("plot_approx_vs_optimal.png")
    plt.show()


# ---------------------------------------------------------
# 2. Anytime Behavior Plot
# ---------------------------------------------------------

def run_and_collect_anytime(case_file, times):
    """
    Runs:
       python facility_location_approx.py -t T case_file
    for T in [list of times], extracts costs.
    """
    costs = []
    for t in times:
        cmd = f"python facility_location_approx.py -t {t} {case_file}"
        print(f"Running: {cmd}")
        stream = os.popen(cmd).read()
        try:
            cost = float(stream.splitlines()[0].strip())
        except:
            cost = None
        costs.append(cost)
    return costs


def plot_anytime_behavior():
    case_file = "test_cases/test_large_03.txt"   # pick any medium case
    times = [0.1, 0.2, 0.5, 1, 2, 5]             # seconds

    costs = run_and_collect_anytime(case_file, times)

    plt.figure(figsize=(10,6))
    plt.plot(times, costs, marker='o')
    plt.xlabel("Time Limit (seconds)")
    plt.ylabel("Best Cost Found")
    plt.title("Anytime Behavior: Cost vs Time Limit")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("plot_anytime_behavior.png")
    plt.show()


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":
    print("Generating Plot 1: Approximation vs Optimal...")
    plot_approx_vs_optimal()
    print("Saved: plot_approx_vs_optimal.png")

    print("\nGenerating Plot 2: Anytime Behavior...")
    plot_anytime_behavior()
    print("Saved: plot_anytime_behavior.png")
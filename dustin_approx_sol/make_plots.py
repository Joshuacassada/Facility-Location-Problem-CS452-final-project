import os
import math
import subprocess
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TESTCASE_DIR = os.path.join(BASE_DIR, "..", "testcases")
APPROX_OUT_DIR = os.path.join(BASE_DIR, "test_outputs")
EXACT_OUT_DIR = os.path.join(BASE_DIR, "..", "exact_solution", "outputs")   # auto-detect


# -------------------------------------------------------------
# Input Parsing
# -------------------------------------------------------------
def parse_input(path):
    with open(path) as f:
        data = f.read().strip().split()

    it = iter(data)
    nC = int(next(it))
    nF = int(next(it))

    clients = {}
    for _ in range(nC):
        name = next(it)
        x = float(next(it))
        y = float(next(it))
        clients[name] = (x, y)

    facs = {}
    for _ in range(nF):
        name = next(it)
        x = float(next(it))
        y = float(next(it))
        _flag = next(it)
        facs[name] = (x, y)

    cov = float(next(it))
    return clients, facs, cov


# -------------------------------------------------------------
# Output Parsing
# -------------------------------------------------------------
def parse_output(path):
    if not os.path.exists(path):
        return None, None

    with open(path) as f:
        lines = f.read().splitlines()

    mode = None
    open_facs = []
    coverage = {}

    for line in lines:
        s = line.strip()
        if not s:
            continue
        if s.startswith("Open"):
            mode = "open"
            continue
        if s.startswith("Coverage"):
            mode = "cov"
            continue
        if mode == "open":
            open_facs = s.split()
        if mode == "cov" and "covers:" in s:
            fac, rest = s.split("covers:")
            fac = fac.strip()
            coverage[fac] = rest.strip().split()

    return open_facs, coverage


# -------------------------------------------------------------
# Distance Computation
# -------------------------------------------------------------
def compute_total_distance(clients, facs, coverage):
    total = 0.0
    for fac, client_list in coverage.items():
        fx, fy = facs[fac]
        for c in client_list:
            cx, cy = clients[c]
            total += math.dist((fx, fy), (cx, cy))
    return total


# -------------------------------------------------------------
# Anytime Improvement
# -------------------------------------------------------------
def run_anytime(case_file, time_values):
    """Runs the approx solver repeatedly for increasing times."""

    costs = []
    for t in time_values:
        cmd = [
            "python3",
            os.path.join(BASE_DIR, "facility_location_approx.py"),
            "-t", str(t),
            case_file
        ]

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()

        # parse temporary output directly from stdout
        out = out.decode()
        lines = out.splitlines()

        # find coverage block
        open_facs = []
        coverage = {}
        mode = None

        for line in lines:
            s = line.strip()
            if not s:
                continue
            if s.startswith("Open"):
                mode = "open"
                continue
            if s.startswith("Coverage"):
                mode = "cov"
                continue
            if mode == "open":
                open_facs = s.split()
            if mode == "cov" and "covers:" in s:
                fac, rest = s.split("covers:")
                fac = fac.strip()
                coverage[fac] = rest.strip().split()

        # compute cost
        clients, facs, cov = parse_input(case_file)
        c = compute_total_distance(clients, facs, coverage)
        costs.append(c)

    return costs


# -------------------------------------------------------------
# MAIN: Generate All Plots
# -------------------------------------------------------------
def generate_all_plots():

    # ------------------------
    # 1. Approx-Only Stats
    # ------------------------

    case_ids = []
    approx_facilities = []
    approx_costs = []

    exact_facilities = []
    exact_costs = []

    for fname in sorted(os.listdir(TESTCASE_DIR)):
        if not fname.startswith("test_case_") or not fname.endswith(".txt"):
            continue

        case_id = int(fname.split("_")[2].split(".")[0])
        input_path = os.path.join(TESTCASE_DIR, fname)
        approx_out = os.path.join(APPROX_OUT_DIR, fname.replace(".txt", "_out.txt"))
        exact_out = os.path.join(EXACT_OUT_DIR, fname.replace(".txt", "_out.txt"))

        clients, facs, cov = parse_input(input_path)
        approx_open, approx_cov = parse_output(approx_out)

        if approx_open is None:
            continue

        a_cost = compute_total_distance(clients, facs, approx_cov)
        a_fac = len(approx_open)

        case_ids.append(case_id)
        approx_facilities.append(a_fac)
        approx_costs.append(a_cost)

        # exact only if available
        if os.path.exists(exact_out):
            ex_open, ex_cov = parse_output(exact_out)
            e_cost = compute_total_distance(clients, facs, ex_cov)
            e_fac = len(ex_open)
        else:
            e_cost = None
            e_fac = None

        exact_facilities.append(e_fac)
        exact_costs.append(e_cost)

    # sort by case id
    zipped = sorted(zip(case_ids, approx_facilities, approx_costs, exact_facilities, exact_costs))
    case_ids, approx_facilities, approx_costs, exact_facilities, exact_costs = zip(*zipped)

    # ------------------------------------------
    # PLOT: Approx vs Exact — Facilities Opened
    # ------------------------------------------
    plt.figure(figsize=(10,6))
    plt.plot(case_ids, approx_facilities, '-o', label="Approx")

    # exact values only if exist
    if any(e is not None for e in exact_facilities):
        plt.plot(case_ids, [e if e is not None else None for e in exact_facilities],
                 '-s', label="Exact")

    plt.title("Facilities Opened: Approx vs Exact")
    plt.xlabel("Test Case")
    plt.ylabel("# Facilities")
    plt.grid(True)
    plt.legend()
    plt.savefig(os.path.join(BASE_DIR, "plot_facilities_comparison.png"))
    plt.show()

    # ------------------------------------------
    # PLOT: Approx vs Exact — Total Distance
    # ------------------------------------------
    plt.figure(figsize=(10,6))
    plt.plot(case_ids, approx_costs, '-o', color="orange", label="Approx")

    if any(e is not None for e in exact_costs):
        plt.plot(case_ids, [e if e is not None else None for e in exact_costs],
                 '-s', color="green", label="Exact")

    plt.title("Total Assignment Distance: Approx vs Exact")
    plt.xlabel("Test Case")
    plt.ylabel("Total Distance")
    plt.grid(True)
    plt.legend()
    plt.savefig(os.path.join(BASE_DIR, "plot_total_distance_comparison.png"))
    plt.show()

    # ------------------------------------------
    # ANYTIME IMPROVEMENT PLOT (choose a test)
    # ------------------------------------------
    test_for_anytime = os.path.join(TESTCASE_DIR, "test_case_50.txt")
    times = [0.1, 0.2, 0.4, 0.8, 1.6, 3.2, 5.0 ]

    anytime_costs = run_anytime(test_for_anytime, times)

    plt.figure(figsize=(10,6))
    plt.plot(times, anytime_costs, '-o')
    plt.title("Anytime Improvement (Approximation Improves Over Time)")
    plt.xlabel("Allowed Time (seconds)")
    plt.ylabel("Best Cost Found")
    plt.grid(True)
    plt.savefig(os.path.join(BASE_DIR, "plot_anytime.png"))
    plt.show()

    print("All plots generated successfully!")


if __name__ == "__main__":
    generate_all_plots()
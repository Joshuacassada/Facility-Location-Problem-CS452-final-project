import os
import math
import subprocess
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TESTCASE_DIR = os.path.join(BASE_DIR, "..", "testcases")
APPROX_OUT_DIR = os.path.join(BASE_DIR, "test_outputs")
EXACT_OUT_DIR = os.path.join(BASE_DIR, "..", "exact_solution", "realistic_test_cases", "outputs")


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
# Output Parsing (NEW + OLD format)
# -------------------------------------------------------------
def parse_output(path):
    if not os.path.exists(path):
        return None, None

    with open(path) as f:
        lines = [ln.strip() for ln in f if ln.strip()]

    # ---------- NEW FORMAT ----------
    if any("Facilities chosen" in ln for ln in lines):
        open_facs = []
        coverage = {}
        in_facility_section = False
        in_coverage_section = False

        for s in lines:
            if "Facilities chosen" in s:
                in_facility_section = True
                in_coverage_section = False
                continue

            if s.startswith("Coverage mapping"):
                in_facility_section = False
                in_coverage_section = True
                continue

            # Facility list
            if in_facility_section and s.startswith("F") and " at " in s:
                fac = s.split()[0]
                open_facs.append(fac)

            # Coverage list
            if in_coverage_section and "covers:" in s:
                fac, rest = s.split("covers:")
                fac = fac.strip()
                rest = rest.strip()
                if rest == "(none)":
                    coverage[fac] = []
                else:
                    coverage[fac] = [c.strip() for c in rest.split(",")]

        return open_facs, coverage

    # ---------- OLD FORMAT ----------
    open_facs = []
    coverage = {}
    mode = None

    for s in lines:
        if s.startswith("Open"):
            mode = "open"
            continue
        if s.startswith("Coverage"):
            mode = "cov"
            continue
        if mode == "open":
            open_facs = s.split()
        elif mode == "cov" and "covers:" in s:
            fac, rest = s.split("covers:")
            fac = fac.strip()
            rest = rest.strip()
            if rest == "(none)":
                coverage[fac] = []
            else:
                coverage[fac] = rest.split()

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
        out, _ = proc.communicate()
        out = out.decode()

        temp_path = "_tmp_any_time_parse.txt"
        with open(temp_path, "w") as f:
            f.write(out)

        open_facs, coverage = parse_output(temp_path)
        os.remove(temp_path)

        clients, facs, _ = parse_input(case_file)
        cost = compute_total_distance(clients, facs, coverage)
        costs.append(cost)

    return costs


# -------------------------------------------------------------
# MAIN: Generate All Plots (FIXED)
# -------------------------------------------------------------
def generate_all_plots():

    case_ids = []
    approx_facilities = []
    approx_costs = []
    exact_facilities = []
    exact_costs = []

    # ------------------------
    # Load data for all cases
    # ------------------------
    for fname in sorted(os.listdir(TESTCASE_DIR)):
        if not fname.startswith("test_case_") or not fname.endswith(".txt"):
            continue

        case_id = int(fname.split("_")[2].split(".")[0])
        input_path = os.path.join(TESTCASE_DIR, fname)
        approx_out = os.path.join(APPROX_OUT_DIR, fname.replace(".txt", "_out.txt"))
        exact_out = os.path.join(EXACT_OUT_DIR, f"test_case_{case_id}.out")

        clients, facs, _ = parse_input(input_path)
        approx_open, approx_cov = parse_output(approx_out)

        if approx_open is None:
            continue

        # FIX → USE TOTAL DISTANCE (not radius)
        approx_cost = compute_total_distance(clients, facs, approx_cov)
        approx_num = len(approx_open)

        case_ids.append(case_id)
        approx_facilities.append(approx_num)
        approx_costs.append(approx_cost)

        if os.path.exists(exact_out):
            ex_open, ex_cov = parse_output(exact_out)
            # FIX → USE TOTAL DISTANCE
            exact_cost = compute_total_distance(clients, facs, ex_cov)
            exact_num = len(ex_open)
        else:
            exact_cost = None
            exact_num = None

        exact_facilities.append(exact_num)
        exact_costs.append(exact_cost)

    # Sort
    zipped = sorted(
        zip(case_ids, approx_facilities, approx_costs, exact_facilities, exact_costs)
    )
    case_ids, approx_facilities, approx_costs, exact_facilities, exact_costs = zip(*zipped)

    # ------------------------------------------------------------
    # APPROX vs EXACT — ONLY CASES 17 THROUGH 42 (FIXED)
    # ------------------------------------------------------------
    selected_indices = [i for i, cid in enumerate(case_ids) if 17 <= cid <= 42]

    case_ids_sel = [case_ids[i] for i in selected_indices]
    approx_fac_sel = [approx_facilities[i] for i in selected_indices]
    exact_fac_sel = [exact_facilities[i] for i in selected_indices]

    approx_cost_sel = [approx_costs[i] for i in selected_indices]
    exact_cost_sel = [exact_costs[i] for i in selected_indices]

    # -------- Facility Count Comparison --------
    plt.figure(figsize=(10, 6))
    plt.plot(case_ids_sel, approx_fac_sel, '-o', label="Approximation")
    plt.plot(case_ids_sel, exact_fac_sel, '-s', label="Exact")
    plt.title("Facilities Opened (Cases 17–42): Approx vs Exact")
    plt.xlabel("Test Case")
    plt.ylabel("# Facilities")
    plt.grid(True)
    plt.legend()
    plt.savefig(os.path.join(BASE_DIR, "plot_facilities_comparison_17_42.png"))
    plt.show()

    # -------- TOTAL DISTANCE Comparison --------
    plt.figure(figsize=(10, 6))
    plt.plot(case_ids_sel, approx_cost_sel, '-o', color="orange", label="Approximation")
    plt.plot(case_ids_sel, exact_cost_sel, '-s', color="green", label="Exact")
    plt.title("Total Distance (Cases 17–42): Approx vs Exact")
    plt.xlabel("Test Case")
    plt.ylabel("Total Assignment Distance")
    plt.grid(True)
    plt.legend()
    plt.savefig(os.path.join(BASE_DIR, "plot_total_distance_comparison_17_42.png"))
    plt.show()

    # ------------------------------------------
    # FULL 50 — APPROX ONLY
    # ------------------------------------------
    plt.figure(figsize=(10, 6))
    plt.plot(case_ids, approx_facilities, '-o')
    plt.title("Number of Facilities Opened (Approx Only)")
    plt.xlabel("Test Cases 1-50")
    plt.ylabel("# Facilities Opened")
    plt.grid(True)
    plt.savefig(os.path.join(BASE_DIR, "plot_facilities_opened.png"))
    plt.show()

    plt.figure(figsize=(10, 6))
    plt.plot(case_ids, approx_costs, '-o', color="orange")
    plt.title("Total Assignment Distance (Approx Only)")
    plt.xlabel("Test Case 1-50")
    plt.ylabel("Sum of Distances")
    plt.grid(True)
    plt.savefig(os.path.join(BASE_DIR, "plot_total_distance.png"))
    plt.show()

    # ------------------------------------------
    # ANYTIME IMPROVEMENT PLOT (UNCHANGED)
    # ------------------------------------------
    test_for_anytime = os.path.join(TESTCASE_DIR, "test_case_50.txt")
    times = [0.1, 0.2, 0.4, 0.8, 1.6, 3.2, 5.0]
    anytime_costs = run_anytime(test_for_anytime, times)

    plt.figure(figsize=(10, 6))
    plt.plot(times, anytime_costs, '-o')
    plt.title("Anytime Improvement (Approximation Improves Over Time)")
    plt.xlabel("Allowed Time (seconds)")
    plt.ylabel("Best Cost Found")
    plt.grid(True)
    plt.savefig(os.path.join(BASE_DIR, "plot_anytime.png"))
    plt.show()

    print("All plots generated successfully using CORRECT distance metric!")


if __name__ == "__main__":
    generate_all_plots()
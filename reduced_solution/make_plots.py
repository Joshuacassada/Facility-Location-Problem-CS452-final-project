#!/usr/bin/env python3
"""
make_reduction_plots.py

Reads results.csv and generates plots required by the Reduction Solution Architect
guidelines:

1. Plot showing the optimal solution (exact) vs your bound (lower_bound)
   for varying problem sizes.

2. Plot showing the approximation cost and how it compares to your bound
   (and to the exact cost when available).

3. Plot of approximation ratio (approx / exact) on instances where exact
   did not timeout.

Expected CSV format (results.csv):

    test_case,lower_bound,approx1,exact
    1,231.73,239.53,285.87
    2,180.46,198.03,334.34
    ...
    41,170.78,201.01,TIMEOUT
    ...

Strings like "TIMEOUT" or "ERR" are handled gracefully.

Run with:

    python3 make_reduction_plots.py [path_to_results_csv]

If no argument is given, defaults to "../results.csv".
"""

import csv
import math
import os
import sys

import matplotlib.pyplot as plt


# ----------------------------------------------------------------------
# Helpers to read CSV and coerce numeric values
# ----------------------------------------------------------------------

def safe_float(val):
    """
    Convert a string to float if possible, otherwise return None.
    Handles 'TIMEOUT', 'ERR', empty strings, etc.
    """
    if val is None:
        return None
    s = str(val).strip()
    if not s:
        return None
    if s.upper() in ("TIMEOUT", "ERR"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def read_results_csv(path):
    """
    Reads results.csv and returns lists of:
      test_cases, lower_bounds, approx_costs, exact_costs

    Any non-numeric approx/exact (TIMEOUT/ERR) is stored as None.
    """
    test_cases = []
    lower_bounds = []
    approx_costs = []
    exact_costs = []

    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                tc = int(row["test_case"])
            except (KeyError, ValueError):
                # Skip malformed rows
                continue

            lb = safe_float(row.get("lower_bound"))
            a1 = safe_float(row.get("approx1"))
            ex = safe_float(row.get("exact"))

            test_cases.append(tc)
            lower_bounds.append(lb)
            approx_costs.append(a1)
            exact_costs.append(ex)

    return test_cases, lower_bounds, approx_costs, exact_costs


# ----------------------------------------------------------------------
# Plotting Functions
# ----------------------------------------------------------------------

def plot_lb_vs_exact(test_cases, lower_bounds, exact_costs, out_dir="."):
    """
    Plot: lower bound vs exact (optimal) on instances where exact is available.
    This corresponds to:
      "Plots that show the optimal solution test cases that show the optimal
       value and your bound for varying size problems."
    """
    xs = []
    lbs = []
    exs = []

    for tc, lb, ex in zip(test_cases, lower_bounds, exact_costs):
        if lb is None or ex is None:
            continue
        xs.append(tc)
        lbs.append(lb)
        exs.append(ex)

    if not xs:
        print("[WARN] No instances with finite exact and lower bound; skipping lb_vs_exact plot.")
        return

    plt.figure(figsize=(10, 6))
    plt.plot(xs, lbs, marker="o", linestyle="-", label="Lower Bound")
    plt.plot(xs, exs, marker="s", linestyle="-", label="Exact (Optimal)")

    plt.title("Lower Bound vs Exact Cost (Instances with Exact Solution)")
    plt.xlabel("Test Case #")
    plt.ylabel("# of Facilities")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()

    out_path = os.path.join(out_dir, "plot_lb_vs_exact.png")
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    print(f"[INFO] Saved {out_path}")


def plot_lb_approx_exact(test_cases, lower_bounds, approx_costs, exact_costs, out_dir="."):
    """
    Plot: lower bound, approximation, and exact cost (when available)
    on a single figure.

    This corresponds to:
      "Plots that show the approximation found and how that compares to your
       bounds." + extra credit single-plot triple comparison.
    """
    xs = []
    lbs = []
    a1s = []
    exs = []

    for tc, lb, a1, ex in zip(test_cases, lower_bounds, approx_costs, exact_costs):
        # We allow approx or exact to be missing, but require LB and approx
        if lb is None or a1 is None:
            continue
        xs.append(tc)
        lbs.append(lb)
        a1s.append(a1)
        exs.append(ex)  # may be None for TIMEOUT

    if not xs:
        print("[WARN] No instances with both lower bound and approx; skipping lb_approx_exact plot.")
        return

    plt.figure(figsize=(10, 6))
    plt.plot(xs, lbs, marker="o", linestyle="-", label="Lower Bound")
    plt.plot(xs, a1s, marker="^", linestyle="-", label="Approximation")

    # Exact only where it exists
    ex_xs = [tc for tc, ex in zip(xs, exs) if ex is not None]
    ex_vals = [ex for ex in exs if ex is not None]
    if ex_xs:
        plt.plot(ex_xs, ex_vals, marker="s", linestyle="-", label="Exact (Optimal)")

    plt.title("Lower Bound vs Approximation vs Exact Cost")
    plt.xlabel("Test Case #")
    plt.ylabel("# of Facilities")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()

    out_path = os.path.join(out_dir, "plot_lb_approx_exact.png")
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    print(f"[INFO] Saved {out_path}")


def plot_approx_ratio(test_cases, approx_costs, exact_costs, out_dir="."):
    """
    Plot approximation ratio: approx / exact, only where exact is available.
    This is very useful in the writeup to show how good the approximation is.
    """
    xs = []
    ratios = []

    for tc, a1, ex in zip(test_cases, approx_costs, exact_costs):
        if a1 is None or ex is None:
            continue
        if ex == 0:
            continue
        xs.append(tc)
        ratios.append(a1 / ex)

    if not xs:
        print("[WARN] No instances with finite approx and exact; skipping approx_ratio plot.")
        return

    plt.figure(figsize=(10, 6))
    plt.plot(xs, ratios, marker="o", linestyle="-")
    plt.axhline(1.0, color="gray", linestyle="--", label="ratio = 1.0")

    plt.title("Approximation Ratio (approx / exact)")
    plt.xlabel("Test Case #")
    plt.ylabel("Approximation Ratio")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()

    out_path = os.path.join(out_dir, "plot_approx_ratio.png")
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    print(f"[INFO] Saved {out_path}")


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

def main():
    # Default path: ../results.csv (since script likely lives in reduced_solution/)
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    else:
        csv_path = os.path.join("..", "results.csv")

    if not os.path.exists(csv_path):
        print(f"[ERROR] Could not find CSV at: {csv_path}")
        print("Usage: python3 make_reduction_plots.py path/to/results.csv")
        sys.exit(1)

    print(f"[INFO] Reading results from {csv_path}")
    test_cases, lower_bounds, approx_costs, exact_costs = read_results_csv(csv_path)

    out_dir = os.path.dirname(os.path.abspath(csv_path))

    # Generate plots required by the guidelines
    plot_lb_vs_exact(test_cases, lower_bounds, exact_costs, out_dir=out_dir)
    plot_lb_approx_exact(test_cases, lower_bounds, approx_costs, exact_costs, out_dir=out_dir)
    plot_approx_ratio(test_cases, approx_costs, exact_costs, out_dir=out_dir)

    print("[INFO] All plots generated.")


if __name__ == "__main__":
    main()

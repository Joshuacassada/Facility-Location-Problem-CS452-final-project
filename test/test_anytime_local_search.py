"""
Tests for approx.py (anytime local-search facility location solver).

Assumes the solver file is named `approx.py` and lives in the project root.
If your file has a different name, change:

    import approx as fl

accordingly.
"""

import io
import math
import pathlib
import sys

# Make project root importable
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import facility_location_approx_blake as fl  # <-- change this module name if needed

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def tiny_instance():
    """
    Simple 2-facility, 2-customer instance we can reason about by hand.

    m = 2, n = 2
    open_cost = [1, 1]
    service_cost:
      c0: [1, 1000]
      c1: [1000, 1]

    Globally optimal solution: open both facilities, assign each
    customer to its "own" facility, total cost 4.
    """
    open_cost = [1.0, 1.0]
    service_cost = [
        [1.0, 1000.0],
        [1000.0, 1.0],
    ]
    return fl.FacilityLocationInstance(open_cost, service_cost)


def three_fac_instance():
    """
    Slightly larger instance for testing moves/local search.
    """
    open_cost = [10.0, 1.0, 1.0]
    service_cost = [
        [1.0, 5.0, 5.0],   # customer 0
        [5.0, 1.0, 10.0],  # customer 1
        [5.0, 10.0, 1.0],  # customer 2
    ]
    return fl.FacilityLocationInstance(open_cost, service_cost)


# ----------------------------------------------------------------------
# read_instance / write_solution
# ----------------------------------------------------------------------


def test_read_instance_parses_basic_format():
    text = """\
2 3
1.0 2.0
# customer rows
5.0 6.0
7.0 8.0
9.0 10.0
"""
    inst = fl.read_instance(io.StringIO(text))
    assert inst.m == 2
    assert inst.n == 3
    assert inst.open_cost == [1.0, 2.0]
    assert inst.service_cost[0] == [5.0, 6.0]
    assert inst.service_cost[2] == [9.0, 10.0]


def test_write_solution_roundtrip():
    inst = tiny_instance()
    open_fac = [True, True]
    assignment = [0, 1]
    total_cost = fl.evaluate_solution(inst, open_fac, assignment)

    buf = io.StringIO()
    fl.write_solution(buf, total_cost, open_fac, assignment)
    out = buf.getvalue().strip().splitlines()

    # first line: total cost
    assert math.isclose(float(out[0]), total_cost, rel_tol=1e-6)

    # second line: indices of open facilities
    assert out[1].split() == ["0", "1"]

    # remaining lines: assignments
    assert [int(x) for x in out[2:]] == assignment


# ----------------------------------------------------------------------
# Cost / assignment helpers
# ----------------------------------------------------------------------


def test_greedy_assign_all_all_open():
    inst = tiny_instance()
    open_fac = [True, True]
    assignment = fl.greedy_assign_all(inst, open_fac)

    # Customer 0 should go to facility 0, customer 1 to facility 1
    assert assignment == [0, 1]

    total = fl.evaluate_solution(inst, open_fac, assignment)
    # open cost: 1 + 1, service: 1 + 1 -> 4
    assert math.isclose(total, 4.0, rel_tol=1e-6)


def test_greedy_assign_all_raises_if_no_open_facilities():
    inst = tiny_instance()
    open_fac = [False, False]
    try:
        fl.greedy_assign_all(inst, open_fac)
    except ValueError as e:
        assert "No open facilities" in str(e)
    else:
        assert False, "Expected ValueError when no facilities are open"


def test_initial_solution_all_open():
    inst = tiny_instance()
    open_fac, assignment, cost = fl.initial_solution_all_open(inst)

    assert all(open_fac)
    assert assignment == [0, 1]  # nearest
    assert math.isclose(cost, 4.0, rel_tol=1e-6)


def test_random_initial_solution_respects_at_least_one_open():
    inst = tiny_instance()
    for _ in range(10):
        open_fac, assignment, cost = fl.random_initial_solution(inst, p_open=0.0)
        assert any(open_fac)  # at least one open
        # assignment length matches number of customers
        assert len(assignment) == inst.n
        # cost is finite
        assert cost > 0.0


# ----------------------------------------------------------------------
# Local neighborhood (best_improving_move) tests
# ----------------------------------------------------------------------


def test_best_improving_move_close_facility():
    """
    Make closing an expensive facility obviously beneficial.
    """
    open_cost = [100.0, 1.0]
    service_cost = [
        [1.0, 5.0],
        [1.0, 5.0],
    ]
    inst = fl.FacilityLocationInstance(open_cost, service_cost)

    open_fac = [True, True]
    assignment = fl.greedy_assign_all(inst, open_fac)
    current_cost = fl.evaluate_solution(inst, open_fac, assignment)

    move, new_cost = fl.best_improving_move(inst, open_fac, assignment, current_cost)
    assert move == ("close", 0)
    # if we close fac 0, both customers go to fac 1
    assert math.isclose(new_cost, 1.0 + 5.0 + 5.0, rel_tol=1e-6)


def test_best_improving_move_open_facility():
    """
    Make opening a cheap, beneficial facility clearly helpful.
    """
    open_cost = [1.0, 1.0]
    service_cost = [
        [10.0, 1.0],
    ]
    inst = fl.FacilityLocationInstance(open_cost, service_cost)

    open_fac = [True, False]
    assignment = [0]  # forced to use facility 0
    current_cost = fl.evaluate_solution(inst, open_fac, assignment)

    move, new_cost = fl.best_improving_move(inst, open_fac, assignment, current_cost)
    assert move == ("open", 1)
    # after opening, best is to serve from facility 1
    assert math.isclose(new_cost, 1.0 + 1.0 + 1.0, rel_tol=1e-6)


# ----------------------------------------------------------------------
# Local search & anytime wrapper
# ----------------------------------------------------------------------


def test_local_search_reaches_local_optimum():
    inst = three_fac_instance()
    open_fac, assignment, current_cost = fl.initial_solution_all_open(inst)

    # Large deadline in the future
    import time as _time
    deadline = _time.time() + 10.0

    open_fac, assignment, final_cost = fl.local_search(
        inst, open_fac, assignment, current_cost, deadline
    )

    # After local_search, no further improving move should exist
    move, new_cost = fl.best_improving_move(inst, open_fac, assignment, final_cost)
    assert move is None
    assert math.isclose(new_cost, final_cost, rel_tol=1e-9)


def test_anytime_local_search_finds_known_optimum():
    """
    On the tiny 2x2 instance, we know the optimal cost is 4.0.
    For this instance, 'all facilities open' is globally optimal, so
    anytime_local_search should always return that cost.
    """
    inst = tiny_instance()
    best_cost, best_open, best_assign = fl.anytime_local_search(
        inst, time_limit=0.05, seed=123
    )

    assert math.isclose(best_cost, 4.0, rel_tol=1e-6)
    # both facilities should be open
    assert best_open == [True, True]
    # and each customer assigned to its cheapest facility
    assert best_assign == [0, 1]


def test_anytime_never_gets_worse_with_more_time():
    """
    Running with a longer time limit can only keep or improve the best cost.
    """
    inst = three_fac_instance()

    c_short, _, _ = fl.anytime_local_search(inst, time_limit=0.01, seed=42)
    c_long, _, _ = fl.anytime_local_search(inst, time_limit=0.2, seed=42)

    assert c_long <= c_short + 1e-9

"""Pre-solve validation of 288 weighted representative month-hours."""
import calendar
import sys
import types

import pandas as pd
import pytest

from energy_transition.eia930_west import build_and_solve


def _representatives(year=2024):
    snapshots = pd.DatetimeIndex([
        pd.Timestamp(year=year, month=month, day=15, hour=hour)
        for month in range(1, 13) for hour in range(24)
    ])
    return pd.DataFrame({
        "snapshot": snapshots,
        "weight_h": [float(calendar.monthrange(year, month)[1])
                     for month in range(1, 13) for _ in range(24)],
        "value": 100.0,
    })


@pytest.mark.parametrize("corruption, message", [
    ("shift_month_weights", "calendar days"),
    ("missing_timestamp", "missing snapshot timestamps"),
    ("infinite_weight", "finite"),
    ("zero_weight", "calendar days"),
    ("missing_weight", "finite"),
    ("duplicate_month_hour", "288 unique month-hour snapshots"),
])
def test_representative_input_rejected_before_solver(monkeypatch, tmp_path, corruption, message):
    class Network:
        def add(self, *args, **kwargs):
            pass
    monkeypatch.setitem(sys.modules, "pypsa", types.SimpleNamespace(Network=Network))
    reps = _representatives()
    if corruption == "shift_month_weights":
        # Annual total is unchanged; month-level integrity must still fail.
        reps.loc[0, "weight_h"] += 1
        reps.loc[24, "weight_h"] -= 1
    elif corruption == "missing_timestamp":
        reps.loc[0, "snapshot"] = pd.NaT
    elif corruption == "infinite_weight":
        reps.loc[0, "weight_h"] = float("inf")
    elif corruption == "zero_weight":
        reps.loc[0, "weight_h"] = 0
    elif corruption == "missing_weight":
        reps.loc[0, "weight_h"] = float("nan")
    else:
        reps.loc[0, "snapshot"] = reps.loc[1, "snapshot"]
    with pytest.raises(ValueError, match=message):
        build_and_solve(reps, tmp_path)


@pytest.mark.parametrize("year, expected_hours", [(2023, 8760), (2024, 8784)])
def test_valid_calendar_weight_inputs_reach_network_setup(monkeypatch, tmp_path, year, expected_hours):
    """Positive control: the time guards accept both regular and leap years."""
    class ReachedSolverSetup(Exception):
        pass

    class Network:
        def add(self, *args, **kwargs):
            pass
        def set_snapshots(self, *args, **kwargs):
            raise ReachedSolverSetup

    monkeypatch.setitem(sys.modules, "pypsa", types.SimpleNamespace(Network=Network))
    reps = _representatives(year)
    assert reps.weight_h.sum() == expected_hours
    with pytest.raises(ReachedSolverSetup):
        build_and_solve(reps, tmp_path)

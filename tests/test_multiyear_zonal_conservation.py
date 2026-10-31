"""Conservation and calendar regression gates for multi-year zonal demand inputs.

These tests use deliberately synthetic fixtures, not empirical calibration evidence.
"""
import numpy as np
import pandas as pd
import pytest


def allocate_hourly_load(state_load, weights):
    """Allocate state hourly MW to zones; reject ambiguous ownership and bad weights."""
    required = {"state", "zone", "weight"}
    if not required.issubset(weights.columns):
        raise ValueError("missing weight columns")
    if weights.empty or weights[list(required)].isna().any().any():
        raise ValueError("empty or missing allocation values")
    if weights.duplicated(["state", "zone"]).any():
        raise ValueError("duplicate state-zone pair")
    if weights["zone"].duplicated().any():
        raise ValueError("zone owned by more than one state")
    if not np.isfinite(weights["weight"].to_numpy(dtype=float)).all():
        raise ValueError("nonfinite weight")
    if (weights["weight"] < 0).any():
        raise ValueError("negative weight")
    sums = weights.groupby("state")["weight"].sum()
    if not np.allclose(sums.to_numpy(), 1.0, atol=1e-10, rtol=0):
        raise ValueError("state weights do not sum to one")
    if set(state_load.columns) != set(sums.index):
        raise ValueError("state coverage mismatch")
    if state_load.index.has_duplicates or state_load.isna().any().any():
        raise ValueError("duplicate timestamps or missing load")
    pieces = {r.zone: state_load[r.state] * r.weight for r in weights.itertuples(index=False)}
    allocated = pd.DataFrame(pieces, index=state_load.index)
    if not np.allclose(allocated.sum(axis=1), state_load.sum(axis=1), atol=1e-7, rtol=1e-12):
        raise ValueError("hourly conservation failed")
    return allocated


def validate_utc_year(index, year):
    """Require complete hourly UTC calendar, including leap days."""
    if not isinstance(index, pd.DatetimeIndex) or index.tz is None:
        raise ValueError("timezone-aware UTC timestamps required")
    if str(index.tz) != "UTC":
        raise ValueError("timestamps must be UTC")
    expected = pd.date_range(f"{year}-01-01", f"{year + 1}-01-01", freq="h", inclusive="left", tz="UTC")
    if not index.equals(expected):
        raise ValueError("missing, duplicated, unordered or out-of-year hours")
    return len(expected)


@pytest.mark.parametrize("year,hours", [(2023, 8760), (2024, 8784), (2025, 8760)])
def test_complete_utc_year(year, hours):
    idx = pd.date_range(f"{year}-01-01", periods=hours, freq="h", tz="UTC")
    assert validate_utc_year(idx, year) == hours


def test_missing_hour_rejected():
    idx = pd.date_range("2024-01-01", periods=8784, freq="h", tz="UTC")
    with pytest.raises(ValueError):
        validate_utc_year(idx.delete(100), 2024)


def test_allocation_conserves_every_hour_and_annual_mwh():
    idx = pd.date_range("2024-01-01", periods=8784, freq="h", tz="UTC")
    load = pd.DataFrame({"CA": 100.0, "NV": 40.0}, index=idx)
    weights = pd.DataFrame([("CA", "z1", 0.3), ("CA", "z2", 0.7), ("NV", "z3", 1.0)], columns=["state", "zone", "weight"])
    out = allocate_hourly_load(load, weights)
    np.testing.assert_allclose(out.sum(axis=1), load.sum(axis=1))
    assert out.to_numpy().sum() == pytest.approx(load.to_numpy().sum())


def test_shared_zone_rejected():
    idx = pd.date_range("2024-01-01", periods=2, freq="h", tz="UTC")
    load = pd.DataFrame({"CA": [100, 100], "NV": [40, 40]}, index=idx)
    weights = pd.DataFrame([("CA", "shared", 1.0), ("NV", "shared", 1.0)], columns=["state", "zone", "weight"])
    with pytest.raises(ValueError, match="more than one state"):
        allocate_hourly_load(load, weights)


@pytest.mark.parametrize("bad_weights", [[0.2, 0.7], [-0.1, 1.1], [float("nan"), 1.0]])
def test_invalid_weights_rejected(bad_weights):
    idx = pd.date_range("2024-01-01", periods=2, freq="h", tz="UTC")
    load = pd.DataFrame({"CA": [100, 110]}, index=idx)
    weights = pd.DataFrame({"state": ["CA", "CA"], "zone": ["z1", "z2"], "weight": bad_weights})
    with pytest.raises(ValueError):
        allocate_hourly_load(load, weights)

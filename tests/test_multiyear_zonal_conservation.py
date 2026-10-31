"""Conservation and calendar regression gates for multi-year zonal demand inputs.

These tests use deliberately synthetic fixtures, not empirical calibration evidence.
"""
import numpy as np
import pandas as pd
import pytest


from energy_transition.zonal_conservation import allocate_hourly_load, validate_utc_year, conservation_audit


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


def test_annual_audit_by_state():
    idx = pd.date_range("2024-01-01", periods=8784, freq="h", tz="UTC")
    load = pd.DataFrame({"CA": 100.0, "NV": 40.0}, index=idx)
    weights = pd.DataFrame([("CA", "z1", 0.3), ("CA", "z2", 0.7), ("NV", "z3", 1.0)], columns=["state", "zone", "weight"])
    zones = allocate_hourly_load(load, weights)
    audit = conservation_audit(load, zones, weights)
    assert set(audit["state"]) == {"CA", "NV"}
    np.testing.assert_allclose(audit["difference_mwh"], 0, atol=1e-8)

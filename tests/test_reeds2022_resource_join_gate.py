"""Synthetic unit tests only: official-source admission is a separate CI job."""
import numpy as np
import pandas as pd
import pytest

from energy_transition.reeds2022_resource_join_gate import (
    FIXED_CST, HOURS, audit_native_clocks, audit_county_zone_cross_state,
    capacity_weighted_cf, require_empirical_join, validate_native_cf,
)


def test_explicit_demand_and_naive_publisher_weather_calendar():
    native = pd.date_range("2012-01-01", periods=HOURS, freq="h", tz=FIXED_CST)
    audit = audit_native_clocks(native, native.tz_localize(None))
    assert audit.count == HOURS
    assert audit.physical_hour_interval_admitted is False
    assert audit.first_utc == "2012-01-01T06:00:00+00:00"


def test_wrong_timezone_or_missing_leap_hour_is_rejected():
    native = pd.date_range("2012-01-01", periods=HOURS, freq="h", tz=FIXED_CST)
    with pytest.raises(ValueError, match="calendar"):
        audit_native_clocks(native, native.delete(1416).tz_localize(None))
    with pytest.raises(ValueError, match="calendar"):
        audit_native_clocks(native, native.tz_convert("UTC").tz_localize(None))


def test_native_integer_cf_cannot_be_guessed_and_pv_ac_normalization():
    with pytest.raises(ValueError, match="authenticated"):
        validate_native_cf(np.array([[5000]], dtype=np.int16), technology="pv")
    p = validate_native_cf(np.array([[5000, 7000]], dtype=np.int16),
                           technology="pv", encoded_scale=10000)
    np.testing.assert_allclose(p, [[0.67, 0.938]])
    w = validate_native_cf(np.array([[0.2, 0.4]]), technology="wind")
    np.testing.assert_allclose(w, [[0.2, 0.4]])
    with pytest.raises(ValueError, match="above 1"):
        validate_native_cf(np.array([[0.9]]), technology="pv")


def test_capacity_weights_do_not_imply_state_allocation():
    result = capacity_weighted_cf([[0.1, 0.8], [0.3, 0.2]], [3, 1])
    np.testing.assert_allclose(result, [0.275, 0.275])
    with pytest.raises(ValueError, match="match"):
        capacity_weighted_cf([[0.1, 0.8]], [3])


def test_border_zone_diagnostic_is_not_spatial_certification():
    zones = audit_county_zone_cross_state(
        ["04001", "04003", "08001"], ["p1", "p1", "p1"])
    assert bool(zones.loc[0, "crosses_state_border"])
    assert not bool(zones.loc[0, "capacity_state_fraction_certified"])
    with pytest.raises(ValueError, match="duplicated"):
        audit_county_zone_cross_state(["04001", "04001"], ["p1", "p2"])


def test_fail_closed_empirical_join():
    with pytest.raises(ValueError, match="BLOCK_PHYSICAL_JOIN"):
        require_empirical_join(hour_energy_contract=False,
                               state_capacity_allocation_certified=False,
                               full_cf_scale_certified=True)
    assert require_empirical_join(hour_energy_contract=True,
                                  state_capacity_allocation_certified=True,
                                  full_cf_scale_certified=True)

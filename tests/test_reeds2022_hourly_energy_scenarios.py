import numpy as np
import pytest

from energy_transition.reeds2022_hourly_energy_scenarios import (
    scenario_installed_capacity_mw,
    instantaneous_cf_hour_ending_sensitivities,
    assumed_state_hourly_energy_mwh,
)


def test_resource_potential_must_not_silently_become_installed_capacity():
    assert scenario_installed_capacity_mw(1000,installed_capacity_mw=50)==50
    assert scenario_installed_capacity_mw(1000,fraction_of_potential=.1)==100
    with pytest.raises(ValueError,match="Exactly one"):
        scenario_installed_capacity_mw(1000)
    with pytest.raises(ValueError,match="Exactly one"):
        scenario_installed_capacity_mw(1000,installed_capacity_mw=5,
                                       fraction_of_potential=.2)
    with pytest.raises(ValueError,match="within developable"):
        scenario_installed_capacity_mw(1000,installed_capacity_mw=1100)


def test_first_hour_requires_prior_cf_for_trapezoid_no_cyclic_wrap():
    x=np.full(8760,.5)
    x[0]=.1
    x[-1]=.9
    y=instantaneous_cf_hour_ending_sensitivities(x)
    assert np.isnan(y["trapezoidal_mwh_per_mw_assumed"].iloc[0])
    assert y["trapezoidal_mwh_per_mw_assumed"].iloc[1]==.3
    assert y["endpoint_hold_mwh_per_mw_assumed"].iloc[0]==.1
    assert not y["first_hour_preceding_sample_certified"].any()
    with_prior=instantaneous_cf_hour_ending_sensitivities(x,prior_hour_cf=.7)
    assert with_prior["trapezoidal_mwh_per_mw_assumed"].iloc[0]==pytest.approx(.4)


def test_assumed_energy_uses_declared_installed_mw_not_total_potential():
    x=np.full(8760,.25)
    out=assumed_state_hourly_energy_mwh(
        x,scenario_installed_mw=100,reference_potential_mw=10000,
        assumption="endpoint_hold")
    assert out.shape==(8760,)
    np.testing.assert_allclose(out,25)
    trap=assumed_state_hourly_energy_mwh(
        x,scenario_installed_mw=100,reference_potential_mw=10000,
        assumption="trapezoid")
    assert np.isnan(trap[0])
    np.testing.assert_allclose(trap[1:],25)

import numpy as np
import pytest

from energy_transition.reeds2022_county_full_state_lp import (
    HOURS, modeled_hourly_cf, MODES, YEARS, STATES, DURATIONS,
    RENEWABLE_PEAK_RATIO, WIND_FRACTION,
)


def test_experiment_matrix_and_illustrative_capacity_assumptions():
    assert len(STATES)*len(YEARS)*len(MODES)*len(DURATIONS)==48
    assert RENEWABLE_PEAK_RATIO==.9
    assert WIND_FRACTION==.5


def test_trapezoid_uses_real_previous_hour_not_cyclic_wrap():
    x=np.full(HOURS,.4)
    x[0]=.1
    x[1]=.7
    x[-1]=.95
    endpoint=modeled_hourly_cf(x,"end_instant_hold")
    trap=modeled_hourly_cf(x,"trapezoid_with_first_endpoint")
    assert endpoint[0]==pytest.approx(.1)
    assert trap[0]==pytest.approx(.1) # openly declared first-hour assumption
    assert trap[1]==pytest.approx(.4)
    assert trap[-1]==pytest.approx((x[-2]+x[-1])/2)
    assert trap[0]!=pytest.approx((x[-1]+x[0])/2)


def test_reject_unverified_shape_or_invalid_cf():
    with pytest.raises(ValueError,match="Invalid"):
        modeled_hourly_cf(np.ones(8759),MODES[0])
    x=np.full(HOURS,.2)
    x[40]=1.5
    with pytest.raises(ValueError,match="Invalid"):
        modeled_hourly_cf(x,MODES[1])
    with pytest.raises(ValueError,match="Unknown"):
        modeled_hourly_cf(np.full(HOURS,.2),"unjustified_clock_shift")

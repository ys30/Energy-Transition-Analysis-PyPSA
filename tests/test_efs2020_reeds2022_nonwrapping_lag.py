import numpy as np
import pytest
from energy_transition.efs2020_reeds2022_nonwrapping_lag import lag_overlap,assess

def reference():
    h=np.arange(8760,dtype=float)
    return 1000.+0.1*h+350.*np.sin(2*np.pi*h/24.)+75.*np.cos(2*np.pi*h/168.)

def test_exact_nonwrap_minus2_lag():
    b=reference()
    a=np.roll(b,-2)
    result=assess(a,b)
    assert result["best_nonwrap_offset"]==-2
    assert result["best_nonwrap_compared_hours"]==8758
    assert result["best_nonwrap_excluded_boundary_hours"]==2
    assert result["best_nonwrap_mae_mw"]==pytest.approx(0)
    assert result["runnerup_mae_margin_mw"]>1.

def test_annual_mwh_same_but_unshifted_hour_wrong():
    b=reference()
    a=np.roll(b,-3)
    result=assess(a,b)
    assert a.sum()==pytest.approx(b.sum())
    assert result["best_nonwrap_offset"]==-3
    assert result["zero_offset_mae_mw"]>result["best_nonwrap_mae_mw"]

def test_nonwrap_boundary_does_not_invent_edge_match():
    b=reference()
    a=np.roll(b,-2)
    a[-2:]+=5000.
    r=assess(a,b)
    assert r["best_nonwrap_offset"]==-2
    assert r["best_nonwrap_mae_mw"]==pytest.approx(0)
    assert r["best_nonwrap_excluded_boundary_hours"]==2

def test_idaho_like_mixed_shifts_remain_unresolved():
    b=reference()
    a=.83*np.roll(b,-2)+.17*np.roll(b,-3)
    result=assess(a,b)
    assert result["best_nonwrap_offset"]==-2
    assert result["best_nonwrap_hours_over_1mw"]>0
    assert not result["best_offset_has_below_1mw_all_overlapping_hours"]
    assert not result["source_2020_clock_authoritatively_verified"]

def test_bad_length_and_nonfinite_fail():
    with pytest.raises(ValueError,match="8760"):
        lag_overlap([1.,2.],reference(),-2)
    b=reference()
    b[10]=float("nan")
    with pytest.raises(ValueError,match="Nonfinite"):
        lag_overlap(reference(),b,-2)

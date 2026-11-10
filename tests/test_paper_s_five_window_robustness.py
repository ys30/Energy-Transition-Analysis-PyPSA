import pytest
from energy_transition.paper_s_five_window_robustness import validate_windows,WINDOWS
def test_five_predeclared_nonoverlapping_equal_length_windows():
    assert validate_windows()
    assert len(WINDOWS)==5
    assert all(b-a+1==168 for a,b in WINDOWS.values())
def test_overlapping_windows_fail_closed():
    w=dict(WINDOWS);w["ordinal_8001"]=(4001,4168)
    with pytest.raises(ValueError,match="Overlapping"):validate_windows(w)
def test_incomplete_reference_fails_closed():
    w=dict(WINDOWS);w.pop("ordinal_4001_reference")
    with pytest.raises(ValueError,match="all five"):validate_windows(w)
